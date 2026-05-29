# 개발 인프라

## 1. 문서 목적

이 문서는 `scene-story-agent`의 개발, MVP 배포, 초기 운영에 필요한 인프라 구성을 정의한다.

중점은 다음이다.

- 어떤 서비스에서 어떤 제품을 쓸지 정한다.
- 각 제품이 어떤 역할을 맡는지 정한다.
- 제품 간 연결 구조를 인프라 관점에서 정리한다.
- API 기반 AI 처리 비용을 산정한다.

운영 서버 사양, AI API 단가, 저장소 비용은 실제 도입 전 다시 확인한다.

## 2. MVP 권장 인프라 구성

MVP는 PostgreSQL에서 해결 가능한 것은 PostgreSQL로 처리한다.

| 영역 | 권장 구성 | 역할 |
|---|---|---|
| API 서버 | 자체 서버의 컨테이너 또는 systemd 서비스 | FastAPI API 실행 |
| 데이터 저장 | PostgreSQL 18 + pgvector | 원본 기록 메타데이터, AI 해석 정보, 벡터 검색, 작업 상태 저장 |
| 작업 처리 | PostgreSQL `processing_jobs` 테이블 | AI 분석, 임베딩 생성, 후보 생성 작업 등록과 상태 추적 |
| Redis | Redis 8.6 | 작업 상태 캐시, 중복 실행 완화, 로그인 세션 캐시, 인증 조회 캐시 |
| 원본 파일 저장 | 자체 S3 호환 Object Storage 또는 사설 파일 저장소 | 원본 사진·영상 비공개 저장 |
| AI API | OpenAI API 또는 Gemini API | 사진 정보 추출, 결과 생성, 임베딩 생성 |
| 비밀값 | 서버 환경 변수 또는 secret 파일 | API 키, DB 접속 정보, 스토리지 키 관리 |
| 로그 | 서버 로그 수집 | API 오류와 작업 처리 오류 확인 |
| 배포 | 수동 배포 또는 GitHub Actions | 테스트, 이미지 빌드, 서버 반영 |

MVP 필수 구성에서 별도 작업 프로세스와 전용 Vector DB는 제외한다.

- API 서버가 `processing_jobs`에 작업을 등록한다.
- API 서버가 초기 MVP 작업 처리도 함께 담당한다.
- PostgreSQL의 `available_at`, `attempt_count`, `status`로 재시도와 실패 상태를 관리한다.
- Redis는 작업과 로그인 흐름의 보조 최적화에만 사용한다.
- 작업량이 늘거나 API 응답 지연이 커질 때 별도 작업 프로세스 도입을 검토한다.

## 3. 기술 선택 기준

기술은 MVP 구현 속도와 운영 단순성을 우선해 고른다.

- 판단 기준:
  - Python 기반 AI 처리 코드와 잘 맞는다.
  - 구조화 데이터와 벡터 검색을 같은 기준으로 관리할 수 있다.
  - 로컬, dev, prod 환경의 차이를 줄일 수 있다.
  - Provider 교체가 가능하도록 경계를 분리할 수 있다.
  - 팀이 유지보수하기 쉬운 구조를 우선한다.
- 애플리케이션 기준:
  - API 서버는 FastAPI와 Pydantic 조합을 우선한다.
  - 정형 데이터는 PostgreSQL을 우선한다.
  - 벡터 검색은 pgvector를 우선한다.
  - 원본 파일은 S3 호환 Object Storage에 저장한다.
  - AI Provider와 Embedding Provider는 OpenAI와 Gemini를 비교 가능한 경계로 분리한다.
  - 작업 상태와 재시도는 PostgreSQL 작업 테이블을 우선 사용한다.
  - Redis는 영구 저장소가 아니라 작업 실행, 로그인, 인증 조회의 보조 캐시로 사용한다.

## 4. 서비스별 책임

### API 실행 환경

API 실행 환경은 자체 서버에서 FastAPI 서버 실행과 운영 관측을 맡는다.

- FastAPI API 서버를 실행한다.
- API 서버 안에서 MVP 작업 처리를 시작한다.
- 컨테이너 또는 systemd 서비스로 배포한다.
- 환경 변수와 비밀값을 주입한다.
- API 로그와 작업 처리 오류를 확인한다.

### PostgreSQL

PostgreSQL은 MVP의 중심 저장소다.

- 사용자 기록과 AI 해석 결과를 저장한다.
- pgvector 확장으로 임베딩 벡터를 저장한다.
- SQL 조건 검색과 벡터 유사도 검색을 함께 처리한다.
- `processing_jobs`로 작업 등록, 실행 상태, 재시도, 실패 원인을 관리한다.
- MVP에서는 별도 Vector DB를 두지 않는다.

### Object Storage

Object Storage는 원본 파일 저장을 맡는다.

- 원본 사진과 영상을 비공개 저장한다.
- API 서버는 저장소 객체 키만 DB에 저장한다.
- 사용자 조회 시 API 서버가 접근 권한을 확인한 뒤 서명 URL을 발급한다.

### Redis

Redis는 PostgreSQL 정본을 보조한다.

- 적용 범위:
  - 작업 실행 lock
  - 작업 상태 조회 캐시
  - 같은 기록의 같은 작업 중복 등록 완화
  - 로그인 세션 캐시
  - 인증 주체 기준 사용자 조회 캐시
  - 인증 요청 rate limit
- 정본 기준:
  - 작업 생성, 상태, 재시도, 실패 사유는 PostgreSQL `processing_jobs`에 남긴다.
  - 사용자 계정 정보는 PostgreSQL `app_users`에 남긴다.
  - 외부 인증 Provider가 있으면 인증 결과의 최종 판단은 해당 Provider와 서버 검증을 따른다.
- 복구 기준:
  - Redis 값이 없어도 PostgreSQL 기준으로 다시 조회하거나 재생성할 수 있어야 한다.
  - Redis TTL 만료는 장애가 아니라 cache miss로 처리한다.
- 민감정보 기준:
  - Redis에는 API key, 원본 파일 URL, OCR 원문, Provider 응답 원문을 저장하지 않는다.

#### 작업 처리 Redis key

작업 처리 key는 아래만 사용한다.

| key | 용도 | TTL | 정본 |
|---|---|---:|---|
| `job:lock:{job_id}` | 같은 작업의 동시 실행 완화 | 5분 | PostgreSQL `processing_jobs` |
| `job:state:{job_id}` | 작업 상태 조회 캐시 | 30~60초 | PostgreSQL `processing_jobs` |
| `record:job:dedupe:{record_id}:{job_type}` | 같은 기록의 같은 작업 중복 등록 완화 | 5분 | PostgreSQL `processing_jobs` |

- `job:lock:{job_id}`:
  - 값은 실행 token으로 둔다.
  - 생성은 `SET NX EX`로 처리한다.
  - 삭제는 token이 일치할 때만 처리한다.
- `job:state:{job_id}`:
  - 상태 변경 시 갱신한다.
  - cache miss 시 PostgreSQL에서 조회한 뒤 다시 저장한다.
- `record:job:dedupe:{record_id}:{job_type}`:
  - hit 시 기존 `job_id`를 우선 반환한다.
  - miss 시 PostgreSQL에서 진행 중 작업을 확인한 뒤 새 작업을 만든다.

#### 로그인 Redis key

로그인 보조 key는 아래만 사용한다.

| key | 용도 | TTL | 정본 |
|---|---|---:|---|
| `session:{session_id}` | 로그인 세션 캐시 | 7일 | 서버 세션 검증 기준, 운영 확장 시 PostgreSQL 세션 테이블 |
| `user:auth:{auth_provider}:{auth_subject}` | 인증 주체에서 내부 `user_id` 조회 | 10분~1시간 | PostgreSQL `app_users` |
| `user:profile:{user_id}` | 사용자 기본 정보 조회 캐시 | 10분 | PostgreSQL `app_users` |
| `auth:rate:{key}` | 로그인과 인증 요청 제한 | 1분 | Redis 카운터 |

- `session:{session_id}`:
  - 값은 `user_id`, `auth_provider`, `auth_subject`, `issued_at`만 둔다.
  - 로그아웃 시 삭제한다.
  - Redis 값이 없으면 재로그인 또는 서버 세션 재검증으로 복구한다.
  - 강제 로그아웃이나 기기별 세션 관리가 필요하면 PostgreSQL `user_sessions`를 정본으로 추가한다.
- `user:auth:{auth_provider}:{auth_subject}`:
  - 값은 `user_id`만 둔다.
  - cache miss 시 PostgreSQL `app_users`를 조회하거나 생성한 뒤 다시 저장한다.
- `user:profile:{user_id}`:
  - 값은 표시 이름과 이메일 같은 기본 정보만 둔다.
  - 프로필 수정 시 삭제하거나 재설정한다.
- `auth:rate:{key}`:
  - `INCR`와 `EXPIRE`로 처리한다.
  - 기준 초과 시 API는 429로 응답한다.

### OpenAI / Gemini

AI API는 사진 정보 추출, 결과 생성, 임베딩 생성을 맡는다.

- 개발·검증 단계는 Gemini Free Tier를 우선 사용한다.
- MVP 운영은 OpenAI `gpt-5.4-mini`와 Gemini Flash 계열을 비교한다.
- 고품질 결과 생성이 필요한 경우 OpenAI `gpt-5.4`를 검토한다.
- AI Provider 인터페이스는 OpenAI, Gemini, Mock을 지원한다.
- Embedding Provider 인터페이스는 Gemini와 Mock을 지원한다.
- Gemini 임베딩은 `embedContent` API와 `output_dimensionality` 설정을 사용한다.

## 5. 인프라 연결 구조

기본 연결 구조는 다음이다.

```text
Client
  ↓
API 서버
  ↓
Object Storage
  ↓
PostgreSQL processing_jobs
  ↓
Redis
  ↓
AI API
  ↓
PostgreSQL + pgvector
  ↓
Client
```

## 6. 요청 처리 흐름

사진 기록 1건은 다음 순서로 처리한다.

1. 사용자가 클라이언트에서 사진을 업로드한다.
2. API 서버가 인증과 파일 검증을 처리한다.
3. API 서버가 원본 사진을 Object Storage에 저장한다.
4. API 서버가 PostgreSQL에 원본 기록 메타데이터를 저장한다.
5. API 서버가 `processing_jobs`에 AI 처리 작업을 등록한다.
6. API 서버가 Redis에 작업 중복 등록 완화 key와 짧은 TTL 상태 캐시를 기록한다.
7. API 서버가 실행 가능한 작업을 가져와 처리한다.
8. API 서버가 원본 이미지를 읽고 AI 처리용 리사이즈 이미지를 만든다.
9. API 서버가 AI API로 사진 정보를 추출한다.
10. API 서버가 추출 결과를 PostgreSQL에 저장한다.
11. API 서버가 추출 결과 일부로 임베딩을 생성한다.
12. API 서버가 임베딩을 PostgreSQL의 pgvector 컬럼에 저장한다.
13. API 서버가 pgvector로 연관 기록 후보를 조회한다.
14. API 서버가 AI API에 현재 기록과 연관 기록 후보를 전달한다.
15. AI API가 연결 후보, 재방문 판단, 타임라인 반영 결과를 생성한다.
16. API 서버가 최종 결과와 작업 상태를 PostgreSQL에 저장한다.
17. 클라이언트가 API 서버를 통해 처리 결과를 조회한다.

## 7. 데이터 연결 구조

데이터는 다음 기준으로 연결한다.

| 데이터 | 저장 위치 | 연결 키 |
|---|---|---|
| 사용자 | PostgreSQL | `user_id` |
| 원본 기록 | PostgreSQL | `record_id`, `user_id` |
| 원본 파일 | Object Storage | `object_key` |
| AI 해석 정보 | PostgreSQL | `record_id` |
| 임베딩 벡터 | PostgreSQL pgvector 컬럼 | `record_id` |
| 연관 후보 | PostgreSQL | `source_record_id`, `target_record_id` |
| 작업 상태 | PostgreSQL `processing_jobs` | `job_id`, `record_id` |
| 작업 보조 캐시 | Redis | `job_id`, `record_id`, `job_type` |
| 로그인 세션 캐시 | Redis | `session_id` |
| 인증 조회 캐시 | Redis | `auth_provider`, `auth_subject`, `user_id` |

`record_id`를 기준으로 원본 기록, AI 해석 정보, 임베딩 벡터, 연결 결과를 묶는다.

## 8. 환경 구성

환경은 다음 3개로 나눈다.

| 환경 | 목적 | 구성 |
|---|---|---|
| local | 개발자 로컬 개발 | Docker Compose, PostgreSQL 18.4 + pgvector, Redis 8.6, 로컬 파일 저장 |
| dev | 통합 개발 검증 | API dev, PostgreSQL dev, Redis dev, Object Storage dev bucket |
| prod | 실제 사용자 운영 | API prod, PostgreSQL prod, Redis prod, Object Storage prod bucket |

운영 데이터와 개발 데이터는 절대 공유하지 않는다.

## 9. AI 처리 파이프라인

MVP에서는 LLM을 직접 운영하지 않고 API 기반으로 처리한다.

기본 파이프라인은 다음이다.

1. 사용자가 사진과 메모를 등록한다.
2. API 서버가 원본 파일을 Object Storage에 저장한다.
3. API 서버가 원본 기록 메타데이터를 PostgreSQL에 저장한다.
4. 작업 실행 환경이 AI 처리용 이미지를 만든다.
5. AI API가 사진 정보와 텍스트 후보를 추출한다.
6. Embedding API가 검색용 벡터를 생성한다.
7. PostgreSQL의 pgvector 컬럼에 벡터를 저장한다.
8. pgvector 조회로 연관 기록 후보를 찾는다.
9. AI API가 현재 기록과 후보 기록을 함께 보고 결과를 생성한다.
10. API 서버가 사용자에게 원본 기록, AI 해석 정보, 연결 후보를 함께 보여준다.

### 리사이즈 기준

AI 처리용 이미지는 다음 기준을 적용한다.

- 긴 변 최대 1024px
- JPEG 또는 WebP 변환
- 품질 70~80
- EXIF 제거
- OCR이 필요한 메뉴판·영수증은 `detail: high`
- 단순 음식·공간·분위기 사진은 `detail: low` 또는 `detail: auto`

## 10. AI 비용 시뮬레이션

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

## 11. OpenAI와 Gemini 운영 기준

| 항목 | OpenAI | Gemini |
|---|---|---|
| 초기 비용 | 사용량 과금 중심 | Free Tier가 있어 개발·검증 비용이 낮다. |
| 저비용 모델 | `gpt-5.4-mini`, `gpt-5.4-nano` | Flash, Flash-Lite 계열 |
| 이미지 입력 | 이미지 토큰 계산 규칙이 명확하다. | Flash 계열에서 이미지·텍스트 입력 단가가 낮다. |
| 임베딩 | `text-embedding-3-small` 후보 | `gemini-embedding-2`, `gemini-embedding-001` 후보 |
| 개인정보 | API 데이터 정책 확인 필요 | Free Tier와 Paid Tier의 데이터 사용 정책 차이를 확인해야 한다. |
| 권장 사용 | MVP 품질 기준 모델 | 개발·저비용 처리 후보 |

Provider 인터페이스를 분리해 OpenAI와 Gemini를 교체 가능하게 만든다.

권장 기본값은 다음이다.

- 개발·검증: Gemini Flash 계열
- MVP 기본 운영: OpenAI `gpt-5.4-mini`와 Gemini Flash 계열 A/B 테스트
- 고품질 결과 생성: OpenAI `gpt-5.4`
- 로컬 MVP 임베딩: Gemini Embedding과 `768` 차원
- 운영 임베딩: OpenAI Embeddings와 Gemini Embedding 비교 후 결정

## 12. 필수 운영 설정

초기부터 다음 설정을 적용한다.

- 서버 리소스와 AI API 비용 알림
- API 서버 로그 수집
- 작업 처리 실패 로그 수집
- DB 자동 백업
- 스토리지 수명주기 정책
- 환경 변수와 비밀값 분리
- 장애 대응 연락 채널
- 공급자별 AI API 월 예산 한도

## 13. 피해야 할 선택

MVP에서는 다음 선택을 피한다.

- Kubernetes 직접 운영
- 자체 Vector DB 운영
- Redis를 영구 작업 상태 저장소로 사용
- 원본 이미지 로컬 디스크 저장
- 운영 DB와 개발 DB 공유
- 비용 알림 없이 AI API 사용량 증가

## 14. 전환 기준

다음 조건이 생기면 인프라를 재검토한다.

- 월간 활성 사용자가 빠르게 증가한다.
- 원본 사진·영상 저장량이 커진다.
- 벡터 검색 응답 시간이 느려진다.
- API 서버의 작업 처리 때문에 응답 지연이 커진다.
- 개인정보 처리위탁 관리가 복잡해진다.
- 기업 고객 또는 기관 고객 요구가 생긴다.
- 단일 장애 지점 제거가 필요하다.
- 자체 서버 운영 비용이나 운영 부담이 외부 서비스 사용보다 커진다.

## 15. 참고 자료

- OpenAI, [API Pricing](https://openai.com/api/pricing/)
- OpenAI, [Pricing in API docs](https://developers.openai.com/api/docs/pricing)
- OpenAI, [Images and vision](https://developers.openai.com/api/docs/guides/images-vision)
- Google AI for Developers, [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Google AI for Developers, [Gemini API billing](https://ai.google.dev/gemini-api/docs/billing/)
- Google AI for Developers, [Gemini Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Google AI for Developers, [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- PostgreSQL, [공식 문서](https://www.postgresql.org/docs/)
- pgvector, [공식 저장소](https://github.com/pgvector/pgvector)
- Redis, [공식 문서](https://redis.io/docs/latest/)

## 16. 이력관리

- 2026-05-28: Gemini Embedding Provider 구현 기준과 로컬 MVP 임베딩 기본값 반영
- 2026-05-27: 클라우드 대체 구성 제거, 자체 서버 운영 기준과 Redis 보조 최적화 기준 정리
- 2026-05-24: MVP 인프라를 API, PostgreSQL 작업 테이블, Redis 기준으로 정리
- 2026-05-23: 로컬 인프라 기준을 PostgreSQL 18.4 + pgvector, Redis 8.6으로 갱신
- 2026-04-24: 개발 인프라 초안 작성
