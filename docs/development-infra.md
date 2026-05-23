# 개발 인프라

## 1. 문서 목적

이 문서는 `scene-story-agent`의 개발, MVP 배포, 초기 운영에 필요한 인프라 구성을 정의한다.

중점은 다음이다.

- 어떤 서비스에서 어떤 제품을 쓸지 정한다.
- 각 제품이 어떤 역할을 맡는지 정한다.
- 제품 간 연결 구조를 인프라 관점에서 정리한다.
- API 기반 AI 처리 비용을 산정한다.

가격과 무료 제공 범위는 수시로 바뀐다. 실제 도입 전 각 서비스의 공식 가격표를 다시 확인한다.

## 2. MVP 권장 인프라 구성

MVP는 비용, 구현 속도, 운영 난이도를 기준으로 다음 조합을 우선 적용한다.

| 영역 | 서비스 | 제품 | 역할 |
|---|---|---|---|
| API 서버 | Google Cloud | Cloud Run | FastAPI 컨테이너 실행 |
| 백그라운드 작업 | Google Cloud | Cloud Run Jobs 또는 Cloud Tasks | 이미지 분석, 임베딩 생성, 결과 생성 비동기 처리 |
| 관계형 DB | Supabase | Supabase Postgres | 원본 기록 메타데이터, AI 해석 정보, 연결 결과 저장 |
| 벡터 검색 | Supabase | Supabase Postgres + pgvector | 기록 임베딩 저장과 유사 기록 검색 |
| 원본 파일 저장 | Cloudflare | R2 | 원본 사진·영상 비공개 저장 |
| 캐시/큐 | Upstash | Redis | AI 분석 작업 큐, 작업 상태, 재시도, 중복 처리 방지 |
| 비밀값 | Google Cloud | Secret Manager | API 키, DB 접속 정보, 스토리지 키 관리 |
| 컨테이너 이미지 | Google Cloud | Artifact Registry | API 서버 이미지 저장 |
| 로그 | Google Cloud | Cloud Logging | API 서버와 작업 로그 수집 |
| CI/CD | GitHub | GitHub Actions | 테스트, 이미지 빌드, Cloud Run 배포 |
| AI API | OpenAI / Google | OpenAI API, Gemini API | 사진 정보 추출, 결과 생성, 임베딩 생성 |

이 구성은 Google Cloud를 실행 환경 중심으로 쓰고, 데이터 저장과 비용 최적화는 Supabase, Cloudflare R2, Upstash를 조합하는 방식이다.

## 3. 서비스별 책임

### Google Cloud

Google Cloud는 애플리케이션 실행과 운영 관측을 맡는다.

- Cloud Run에서 FastAPI API 서버를 실행한다.
- Cloud Run Jobs 또는 Cloud Tasks로 백그라운드 작업을 실행한다.
- Artifact Registry에 컨테이너 이미지를 저장한다.
- Secret Manager에서 외부 서비스 접속 정보를 관리한다.
- Cloud Logging으로 API와 작업 로그를 확인한다.

### Supabase

Supabase는 기록 데이터와 벡터 검색을 맡는다.

- Postgres에 사용자 기록과 AI 해석 결과를 저장한다.
- Postgres의 pgvector 확장으로 임베딩 벡터를 저장한다.
- SQL 조건 검색과 벡터 유사도 검색을 함께 처리한다.
- MVP에서는 별도 Vector DB를 두지 않고 Supabase Postgres + pgvector가 벡터 검색 역할을 맡는다.

### Cloudflare

Cloudflare는 원본 파일 저장을 맡는다.

- R2에 원본 사진과 영상을 비공개 저장한다.
- API 서버는 R2 객체 키만 DB에 저장한다.
- 사용자 조회 시 API 서버가 접근 권한을 확인한 뒤 서명 URL을 발급한다.

### Upstash

Upstash는 Redis 기반 작업 큐와 임시 상태 관리를 맡는다.

- AI 분석 작업 대기열을 관리한다.
- 이미지 처리 작업 상태를 저장한다.
- 실패한 작업의 재시도 정보를 관리한다.
- 같은 기록에 대한 중복 작업 실행을 막는다.
- 짧은 TTL이 필요한 임시 데이터를 저장한다.

### OpenAI / Gemini

AI API는 사진 정보 추출, 결과 생성, 임베딩 생성을 맡는다.

- 개발·검증 단계는 Gemini Free Tier를 우선 사용한다.
- MVP 운영은 OpenAI `gpt-5.4-mini`와 Gemini Flash 계열을 비교한다.
- 고품질 결과 생성이 필요한 경우 OpenAI `gpt-5.4`를 검토한다.
- Provider 인터페이스를 분리해 OpenAI와 Gemini를 교체 가능하게 만든다.

## 4. 인프라 연결 구조

기본 연결 구조는 다음이다.

```text
Client
  ↓
Cloud Run API 서버
  ↓
Cloudflare R2
  ↓
Cloud Run Worker
  ↓
AI API
  ↓
Supabase Postgres
  ↓
Supabase Postgres + pgvector
  ↓
AI API
  ↓
Supabase Postgres
  ↓
Client
```

## 5. 요청 처리 흐름

사진 기록 1건은 다음 순서로 처리한다.

1. 사용자가 클라이언트에서 사진을 업로드한다.
2. Cloud Run API 서버가 인증과 파일 검증을 처리한다.
3. API 서버가 원본 사진을 Cloudflare R2에 저장한다.
4. API 서버가 Supabase Postgres에 원본 기록 메타데이터를 저장한다.
5. API 서버가 Upstash Redis에 처리 작업을 등록한다.
6. Cloud Run Worker가 작업을 가져온다.
7. Worker가 R2에서 원본 이미지를 읽고 AI 처리용 리사이즈 이미지를 만든다.
8. Worker가 AI API로 사진 정보를 추출한다.
9. Worker가 추출 결과를 Supabase Postgres에 저장한다.
10. Worker가 추출 결과 일부로 임베딩을 생성한다.
11. Worker가 임베딩을 Supabase Postgres의 pgvector 컬럼에 저장한다.
12. Worker가 Supabase Postgres + pgvector로 연관 기록 후보를 조회한다.
13. Worker가 AI API에 현재 기록과 연관 기록 후보를 전달한다.
14. AI API가 연결 후보, 재방문 판단, 타임라인 반영 결과를 생성한다.
15. Worker가 최종 결과를 Supabase Postgres에 저장한다.
16. 클라이언트가 API 서버를 통해 처리 결과를 조회한다.

## 6. 데이터 연결 구조

데이터는 다음 기준으로 연결한다.

| 데이터 | 저장 위치 | 연결 키 |
|---|---|---|
| 사용자 | Supabase Postgres | `user_id` |
| 원본 기록 | Supabase Postgres | `record_id`, `user_id` |
| 원본 파일 | Cloudflare R2 | `object_key` |
| AI 해석 정보 | Supabase Postgres | `record_id` |
| 임베딩 벡터 | Supabase Postgres의 pgvector 컬럼 | `record_id` |
| 연관 후보 | Supabase Postgres | `source_record_id`, `target_record_id` |
| 작업 상태 | Upstash Redis | `job_id`, `record_id` |

`record_id`를 기준으로 원본 기록, AI 해석 정보, 임베딩 벡터, 연결 결과를 묶는다.

## 7. 환경 구성

환경은 다음 3개로 나눈다.

| 환경 | 목적 | 구성 |
|---|---|---|
| local | 개발자 로컬 개발 | Docker Compose, PostgreSQL 18.4 + pgvector, Redis 8.6, 로컬 파일 저장 |
| dev | 통합 개발 검증 | Cloud Run dev, Supabase dev, R2 dev bucket, Upstash dev |
| prod | 실제 사용자 운영 | Cloud Run prod, Supabase prod, R2 prod bucket, Upstash prod |

운영 데이터와 개발 데이터는 절대 공유하지 않는다.

## 8. 클라우드별 대체 구성

운영 요구가 바뀌면 다음 구성을 검토한다.

| 영역 | 추천 구성 | 대체 구성 |
|---|---|---|
| API 서버 | Google Cloud Run | AWS App Runner, AWS ECS Fargate, Azure Container Apps |
| 워커 | Cloud Run Jobs | AWS Lambda, ECS Fargate, Azure Container Apps Jobs |
| DB/Vector | Supabase Postgres + pgvector | Cloud SQL PostgreSQL + pgvector, RDS PostgreSQL + pgvector, Azure PostgreSQL + pgvector |
| 파일 저장 | Cloudflare R2 | S3, Cloud Storage, Azure Blob Storage |
| Redis/Queue | Upstash Redis | Memorystore, ElastiCache, Azure Cache for Redis |
| 비밀값 | Google Secret Manager | AWS Secrets Manager, Azure Key Vault |
| 로그 | Cloud Logging | CloudWatch, Azure Monitor |

## 9. AWS 단일 구성

AWS로 단일 구성할 때는 다음 제품을 사용한다.

| 영역 | 제품 |
|---|---|
| API 서버 | ECS Fargate 또는 App Runner |
| 워커 | ECS Fargate 또는 Lambda |
| DB/Vector | RDS for PostgreSQL + pgvector |
| 파일 저장 | S3 |
| 큐 | SQS |
| Redis | ElastiCache Redis |
| 비밀값 | Secrets Manager |
| 로그 | CloudWatch |
| 컨테이너 이미지 | ECR |

AWS 구성은 장기 운영과 보안 확장성은 좋지만 MVP 단계에서는 설정 부담이 크다.

## 10. Google Cloud 단일 구성

Google Cloud로 단일 구성할 때는 다음 제품을 사용한다.

| 영역 | 제품 |
|---|---|
| API 서버 | Cloud Run |
| 워커 | Cloud Run Jobs 또는 Cloud Tasks |
| DB/Vector | Cloud SQL PostgreSQL + pgvector |
| 파일 저장 | Cloud Storage |
| 큐 | Pub/Sub 또는 Cloud Tasks |
| Redis | Memorystore |
| 비밀값 | Secret Manager |
| 로그 | Cloud Logging |
| 컨테이너 이미지 | Artifact Registry |

Google Cloud 단일 구성은 권한과 운영 책임을 한 곳에서 관리하기 좋다. Supabase와 R2를 쓰는 조합보다 초기 비용은 높을 수 있다.

## 11. Azure 단일 구성

Azure로 단일 구성할 때는 다음 제품을 사용한다.

| 영역 | 제품 |
|---|---|
| API 서버 | Container Apps |
| 워커 | Container Apps Jobs |
| DB/Vector | Azure Database for PostgreSQL + pgvector |
| 파일 저장 | Blob Storage |
| 큐 | Service Bus |
| Redis | Azure Cache for Redis |
| 비밀값 | Key Vault |
| 로그 | Azure Monitor |
| 컨테이너 이미지 | Azure Container Registry |

Azure 구성은 Microsoft 조직 계정, 기업 보안, 내부 시스템 연동이 중요한 경우에 적합하다.

## 12. AI 처리 파이프라인

MVP에서는 LLM을 직접 운영하지 않고 API 기반으로 처리한다.

기본 파이프라인은 다음이다.

1. 사진 정보 추출
2. 임베딩 생성
3. Supabase Postgres의 pgvector 컬럼에 벡터 저장
4. 연관 데이터 조회
5. 결과 생성

### 리사이즈 기준

AI 처리용 이미지는 다음 기준을 적용한다.

- 긴 변 최대 1024px
- JPEG 또는 WebP 변환
- 품질 70~80
- EXIF 제거
- OCR이 필요한 메뉴판·영수증은 `detail: high`
- 단순 음식·공간·분위기 사진은 `detail: low` 또는 `detail: auto`

## 13. AI 비용 시뮬레이션

이 문서의 시뮬레이션은 다음 가정을 둔다.

- 환율: $1 = 1,500원
- 기록 1건당 이미지 1장
- 리사이즈 후 AI 처리
- 연관 기록 조회는 상위 5개 후보 기준
- 임베딩 비용은 전체 비용에서 비중이 작으므로 별도 항목으로 분리하지 않는다.

기록 1건당 토큰 가정은 다음이다.

| 처리 | 입력 토큰 | 출력 토큰 | 설명 |
|---|---:|---:|---|
| 사진 정보 추출 | 1,700 | 700 | 이미지에서 장소, OCR, 태그, 요약 추출 |
| 임베딩 생성 | 600 | 0 | 요약, 태그, OCR 일부로 벡터 생성 |
| 연관 데이터 조회 | 0 | 0 | Postgres/pgvector 조회라 LLM 토큰 비용 없음 |
| 결과 생성 | 2,500 | 700 | 현재 기록과 상위 5개 후보를 분석 |
| 합계 | 4,200 | 1,400 | 임베딩 입력 토큰은 별도 모델 비용 |

### OpenAI 비용

OpenAI 기준 단가는 다음이다.

- `gpt-5.4-mini`: 입력 $0.75/1M tokens, 출력 $4.50/1M tokens
- `gpt-5.4`: 입력 $2.50/1M tokens, 출력 $15.00/1M tokens

| 월 기록 수 | 기본 파이프라인 | 고품질 결과 생성 |
|---:|---:|---:|
| 1,000건 | 약 $9.5 / 14,250원 | 약 $21 / 31,500원 |
| 10,000건 | 약 $95 / 142,500원 | 약 $210 / 315,000원 |
| 100,000건 | 약 $950 / 1,425,000원 | 약 $2,100 / 3,150,000원 |

고품질 결과 생성은 사진 정보 추출은 `gpt-5.4-mini`, 결과 생성은 `gpt-5.4`를 사용하는 기준이다.

### Gemini 비용

Gemini Flash-Lite 계열 기준 단가는 입력 $0.10/1M tokens, 출력 $0.40/1M tokens 수준으로 계산한다.

| 월 기록 수 | 기본 파이프라인 |
|---:|---:|
| 1,000건 | 약 $1 / 1,500원 |
| 10,000건 | 약 $10 / 15,000원 |
| 100,000건 | 약 $100 / 150,000원 |

Gemini Free Tier 안에서 처리되면 API 비용은 0원이다. 운영 서비스에서는 무료 티어를 고정 비용 절감 수단으로 보지 않고 개발·검증용으로 본다.

## 14. OpenAI와 Gemini 운영 기준

| 항목 | OpenAI | Gemini |
|---|---|---|
| 초기 비용 | 사용량 과금 중심 | Free Tier가 있어 개발·검증 비용이 낮다. |
| 저비용 모델 | `gpt-5.4-mini`, `gpt-5.4-nano` | Flash, Flash-Lite 계열 |
| 이미지 입력 | 이미지 토큰 계산 규칙이 명확하다. | Flash 계열에서 이미지·텍스트 입력 단가가 낮다. |
| 임베딩 | `text-embedding-3-small` 후보 | `gemini-embedding-001` 후보 |
| 개인정보 | API 데이터 정책 확인 필요 | Free Tier와 Paid Tier의 데이터 사용 정책 차이를 확인해야 한다. |
| 권장 사용 | MVP 품질 기준 모델 | 개발·저비용 처리 후보 |

Provider 인터페이스를 분리해 OpenAI와 Gemini를 교체 가능하게 만든다.

권장 기본값은 다음이다.

- 개발·검증: Gemini Flash 계열
- MVP 기본 운영: OpenAI `gpt-5.4-mini`와 Gemini Flash 계열 A/B 테스트
- 고품질 결과 생성: OpenAI `gpt-5.4`
- 임베딩: OpenAI Embeddings와 Gemini Embedding 비교 후 결정

## 15. 필수 운영 설정

초기부터 다음 설정을 적용한다.

- 클라우드 비용 예산 알림
- API 서버 로그 수집
- 워커 실패 로그 수집
- DB 자동 백업
- 스토리지 수명주기 정책
- 환경 변수와 비밀값 분리
- 장애 대응 연락 채널
- 공급자별 AI API 월 예산 한도

## 16. 피해야 할 선택

MVP에서는 다음 선택을 피한다.

- Kubernetes 직접 운영
- 자체 Vector DB 운영
- 자체 Redis 운영
- 원본 이미지 로컬 디스크 저장
- 운영 DB와 개발 DB 공유
- 비용 알림 없이 클라우드 리소스 생성

## 17. 전환 기준

다음 조건이 생기면 인프라를 재검토한다.

- 월간 활성 사용자가 빠르게 증가한다.
- 원본 사진·영상 저장량이 커진다.
- 벡터 검색 응답 시간이 느려진다.
- 개인정보 처리위탁 관리가 복잡해진다.
- 기업 고객 또는 기관 고객 요구가 생긴다.
- 단일 장애 지점 제거가 필요하다.
- 특정 클라우드 크레딧이나 계약 조건이 생긴다.

## 18. 참고 자료

- OpenAI, [API Pricing](https://openai.com/api/pricing/)
- OpenAI, [Pricing in API docs](https://developers.openai.com/api/docs/pricing)
- OpenAI, [Images and vision](https://developers.openai.com/api/docs/guides/images-vision)
- Google AI for Developers, [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Google AI for Developers, [Gemini API billing](https://ai.google.dev/gemini-api/docs/billing/)
- Google AI for Developers, [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- AWS, [Amazon RDS Free Tier](https://aws.amazon.com/rds/free/)
- AWS, [Amazon S3 Pricing](https://aws.amazon.com/s3/pricing/)
- AWS, [AWS Fargate Pricing](https://aws.amazon.com/fargate/pricing/)
- AWS, [RDS for PostgreSQL pgvector support](https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-rds-for-postgresql-pgvector-080/)
- Google Cloud, [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- Google Cloud, [Cloud SQL Pricing](https://cloud.google.com/sql/pricing/)
- Google Cloud, [Cloud Storage Pricing](https://cloud.google.com/storage/pricing)
- Google Cloud, [Cloud SQL PostgreSQL extensions](https://cloud.google.com/sql/docs/postgres/extensions)
- Azure, [Container Apps Pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/)
- Azure, [Azure Database for PostgreSQL](https://azure.microsoft.com/en-us/products/postgresql/)
- Azure, [pgvector on Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/azure/postgresql/extensions/how-to-use-pgvector)
- Azure, [Blob Storage Pricing](https://azure.microsoft.com/en-us/pricing/details/storage/)
- Supabase, [pgvector: Embeddings and vector similarity](https://supabase.com/docs/guides/database/extensions/pgvector)
- Supabase, [Storage pricing](https://supabase.com/docs/guides/storage/management/pricing)
- Cloudflare, [R2 Pricing](https://developers.cloudflare.com/r2/pricing/)
- Railway, [Pricing plans](https://docs.railway.com/pricing/plans)
- Upstash, [Redis Pricing and Limits](https://upstash.com/docs/redis/overall/pricing)

## 19. 이력관리

- 2026-05-23: 로컬 인프라 기준을 PostgreSQL 18.4 + pgvector, Redis 8.6으로 갱신
- 2026-04-24: 개발 인프라 초안 작성
