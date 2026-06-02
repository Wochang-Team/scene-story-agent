# 개발 인프라

## 1. 문서 목적

이 문서는 `scene-story-agent`의 MVP 개발, 배포, 초기 운영에 필요한 인프라 선택 기준을 정리한다.

- 포함 범위:
  - 인프라 구성 요소
  - 구성 요소별 책임
  - Redis와 PostgreSQL 역할 분리
  - AI Provider 운영 기준
  - 비용 판단 기준
  - 운영 전환 기준
- 제외 범위:
  - 로컬 실행 명령
  - API 요청 처리 절차
  - Worker polling 상세
  - 테이블, 컬럼, 제약 상세
  - 사용자 화면 흐름
- 참조:
  - 처리 흐름: `docs/processing-flow.md`
  - 로컬 실행: `docs/fastapi-quickstart.md`
  - 상태값과 SQL 정본: `docs/database-design.md`
  - 제품 기준: `docs/product-spec.md`

운영 서버 사양, AI API 단가, 저장소 비용은 실제 도입 전 다시 확인한다.

## 2. MVP 인프라 구성

MVP는 PostgreSQL에서 해결 가능한 것은 PostgreSQL로 처리한다.

| 영역 | 권장 구성 | 역할 |
|---|---|---|
| API 서버 | 자체 서버의 컨테이너 또는 systemd 서비스 | FastAPI API 실행, 기록 생성, 파일 업로드, 작업 등록, 상태 조회 |
| Worker | 자체 서버의 별도 프로세스 | AI 해석, 임베딩 생성, 연관 기록 후보 생성, 타임라인 후보 생성 |
| 데이터 저장 | PostgreSQL 18 + pgvector | 원본 기록 메타데이터, AI 해석 정보, 벡터 검색, 작업 상태 저장 |
| Redis | Redis 8.6 | 작업 lock, 상태 캐시, 중복 등록 완화, 로그인 보조 캐시 |
| 원본 파일 저장 | 자체 S3 호환 Object Storage 또는 사설 파일 저장소 | 원본 사진·영상과 썸네일 비공개 저장 |
| AI API | OpenAI API 또는 Gemini API | 사진 정보 추출, 결과 생성, 임베딩 생성 |
| 비밀값 | 서버 환경 변수 또는 secret 파일 | API key, DB 접속 정보, 스토리지 key 관리 |
| 로그 | 서버 로그 수집 | API 오류와 작업 처리 오류 확인 |
| 배포 | 수동 배포 또는 GitHub Actions | 테스트, 이미지 빌드, 서버 반영 |

### 선택 기준

초기 선택은 운영 단순성과 교체 가능성을 우선한다.

- API 서버는 FastAPI와 Pydantic 조합을 사용한다.
- 정형 데이터와 벡터 검색은 PostgreSQL + pgvector로 묶어 관리한다.
- 작업 상태와 재시도 정본은 PostgreSQL에 둔다.
- Redis는 영구 저장소가 아니라 실행 보조 캐시로 사용한다.
- 원본 파일은 DB가 아니라 Object Storage에 저장한다.
- AI Provider와 Embedding Provider는 교체 가능한 인터페이스로 분리한다.

## 3. 구성 요소별 책임

인프라 책임은 아래 기준으로 나눈다.

### API 서버

API 서버는 사용자 요청과 조회 응답을 맡는다.

- FastAPI API를 실행한다.
- 기록 생성과 파일 업로드를 처리한다.
- 작업을 등록한다.
- 상태와 결과 조회 API를 제공한다.
- 원본 파일 접근 권한을 확인하고 서명 URL을 발급한다.

### Worker

Worker는 오래 걸리는 파생 데이터 생성을 맡는다.

- AI 해석 작업을 처리한다.
- 임베딩을 생성한다.
- 연관 기록 후보를 생성한다.
- 타임라인 후보를 생성한다.
- 처리 실패와 재시도 상태를 작업 테이블에 남긴다.

### PostgreSQL

PostgreSQL은 MVP의 정본 저장소다.

- 사용자와 원본 기록을 저장한다.
- 파일 메타데이터를 저장한다.
- AI 해석 정보와 임베딩 벡터를 저장한다.
- 연관 기록 후보와 타임라인 후보를 저장한다.
- 작업 상태, 시도 횟수, 실패 원인을 저장한다.

### Redis

Redis는 PostgreSQL 정본을 보조한다.

- 허용 용도:
  - 작업 실행 lock
  - 작업 상태 조회 캐시
  - 같은 기록의 같은 작업 중복 등록 완화
  - 로그인 세션 캐시
  - 인증 주체 기준 사용자 조회 캐시
  - 인증 요청 rate limit
- 저장 제외:
  - API key
  - 원본 파일 URL
  - OCR 원문
  - Provider 응답 원문
  - 장기 보관이 필요한 작업 상태
- 복구 기준:
  - Redis 값이 없어도 PostgreSQL 기준으로 다시 조회하거나 재생성할 수 있어야 한다.
  - Redis TTL 만료는 장애가 아니라 cache miss로 처리한다.

### Object Storage

Object Storage는 원본 파일 저장을 맡는다.

- 원본 사진과 영상을 비공개 저장한다.
- 썸네일 파일을 저장한다.
- DB에는 저장소 객체 key만 남긴다.
- 사용자 조회 시 API 서버가 권한 확인 후 접근 URL을 발급한다.

## 4. Redis key 기준

Redis key는 정본 데이터가 아니라 보조 최적화 값이다.

### 작업 처리 key

작업 처리 key는 아래만 사용한다.

| key | 용도 | TTL | 정본 |
|---|---|---:|---|
| `job:lock:{job_id}` | 같은 작업의 동시 실행 완화 | 5분 | PostgreSQL `processing_jobs` |
| `job:state:{job_id}` | 작업 상태 조회 캐시 | 30~60초 | PostgreSQL `processing_jobs` |
| `record:job:dedupe:{record_id}:{job_type}` | 같은 기록의 같은 작업 중복 등록 완화 | 5분 | PostgreSQL `processing_jobs` |

### 로그인 보조 key

로그인 보조 key는 아래만 사용한다.

| key | 용도 | TTL | 정본 |
|---|---|---:|---|
| `session:{session_id}` | 로그인 세션 캐시 | 7일 | 서버 세션 검증 기준 |
| `user:auth:{auth_provider}:{auth_subject}` | 인증 주체에서 내부 `user_id` 조회 | 10분~1시간 | PostgreSQL `app_users` |
| `user:profile:{user_id}` | 사용자 기본 정보 조회 캐시 | 10분 | PostgreSQL `app_users` |
| `auth:rate:{key}` | 로그인과 인증 요청 제한 | 1분 | Redis 카운터 |

## 5. 인프라 연결 구조

기본 연결 구조는 다음이다.

```text
Client
  ↓
API 서버
  ├─ Object Storage
  ├─ PostgreSQL
  └─ Redis
       ↓
Worker
  ├─ Redis
  ├─ AI API
  └─ PostgreSQL
```

상세 처리 순서는 `docs/processing-flow.md`를 따른다.

## 6. 환경 구성 기준

환경은 다음 3개로 나눈다.

| 환경 | 목적 | 구성 |
|---|---|---|
| local | 개발자 로컬 개발 | Docker Compose, PostgreSQL 18.4 + pgvector, Redis 8.6, 로컬 파일 저장 |
| dev | 통합 개발 검증 | API dev, Worker dev, PostgreSQL dev, Redis dev, Object Storage dev bucket |
| prod | 실제 사용자 운영 | API prod, Worker prod, PostgreSQL prod, Redis prod, Object Storage prod bucket |

운영 데이터와 개발 데이터는 공유하지 않는다.

## 7. AI Provider 기준

MVP에서는 LLM을 직접 운영하지 않고 API 기반으로 처리한다.

- 개발·검증 단계는 Gemini Free Tier를 우선 사용한다.
- MVP 운영은 OpenAI와 Gemini Flash 계열을 비교한다.
- 고품질 결과 생성이 필요한 경우 상위 모델을 검토한다.
- AI Provider 인터페이스는 OpenAI, Gemini, Mock을 지원한다.
- Embedding Provider 인터페이스는 Gemini와 Mock을 지원한다.
- Gemini 임베딩은 `embedContent` API와 `output_dimensionality` 설정을 사용한다.

### OpenAI와 Gemini 운영 기준

| 항목 | OpenAI | Gemini |
|---|---|---|
| 초기 비용 | 사용량 과금 중심 | Free Tier가 있어 개발·검증 비용이 낮다. |
| 저비용 모델 | mini, nano 계열 후보 | Flash, Flash-Lite 계열 |
| 이미지 입력 | 이미지 토큰 계산 규칙이 명확하다. | Flash 계열에서 이미지·텍스트 입력 단가가 낮다. |
| 임베딩 | OpenAI Embeddings 후보 | Gemini Embedding 후보 |
| 개인정보 | API 데이터 정책 확인 필요 | Free Tier와 Paid Tier의 데이터 사용 정책 차이를 확인해야 한다. |
| 권장 사용 | MVP 품질 기준 모델 | 개발·저비용 처리 후보 |

Provider 인터페이스를 분리해 OpenAI와 Gemini를 교체 가능하게 만든다.

## 8. AI 비용 판단 기준

AI 비용은 기록 1건당 이미지 처리와 결과 생성 비용으로 판단한다.

- 가정:
  - 환율: $1 = 1,500원
  - 기록 1건당 이미지 1장
  - AI 처리 전 이미지 리사이즈
  - 연관 기록 조회는 PostgreSQL/pgvector로 처리
  - 임베딩 비용은 전체 비용에서 비중이 작으므로 별도 항목으로 분리하지 않는다.
- 비용 관리 기준:
  - 공급자별 월 예산 한도를 둔다.
  - 이미지 리사이즈와 EXIF 제거를 적용한다.
  - 비용 알림 없이 운영 사용량을 늘리지 않는다.
  - Free Tier는 개발·검증용으로만 본다.

## 9. 필수 운영 설정

초기부터 다음 설정을 적용한다.

- 서버 리소스와 AI API 비용 알림
- API 서버 로그 수집
- Worker 처리 실패 로그 수집
- DB 자동 백업
- 스토리지 수명주기 정책
- 환경 변수와 비밀값 분리
- 장애 대응 연락 채널
- 공급자별 AI API 월 예산 한도

## 10. 피해야 할 선택

MVP에서는 다음 선택을 피한다.

- Kubernetes 직접 운영
- 자체 Vector DB 운영
- Redis를 영구 작업 상태 저장소로 사용
- 원본 이미지 로컬 디스크 저장
- 운영 DB와 개발 DB 공유
- 비용 알림 없이 AI API 사용량 증가
- API 서버에서 오래 걸리는 AI 작업 직접 처리

## 11. 전환 기준

다음 조건이 생기면 인프라를 재검토한다.

- 월간 활성 사용자가 빠르게 증가한다.
- 원본 사진·영상 저장량이 커진다.
- 벡터 검색 응답 시간이 느려진다.
- Worker 처리 대기 시간이 길어진다.
- Worker 단일 프로세스로 처리 가능한 작업량을 넘는다.
- 개인정보 처리위탁 관리가 복잡해진다.
- 기업 고객 또는 기관 고객 요구가 생긴다.
- 단일 장애 지점 제거가 필요하다.
- 자체 서버 운영 비용이나 운영 부담이 외부 서비스 사용보다 커진다.

## 12. 참고 자료

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

## 13. 이력관리

- 2026-06-02: 처리 흐름과 실행 절차를 분리하고 인프라 선택, 책임, 운영 판단 중심으로 재정리
- 2026-05-28: Gemini Embedding Provider 구현 기준과 로컬 MVP 임베딩 기본값 반영
- 2026-05-27: 클라우드 대체 구성 제거, 자체 서버 운영 기준과 Redis 보조 최적화 기준 정리
- 2026-05-24: MVP 인프라를 API, PostgreSQL 작업 테이블, Redis 기준으로 정리
- 2026-05-23: 로컬 인프라 기준을 PostgreSQL 18.4 + pgvector, Redis 8.6으로 갱신
- 2026-04-24: 개발 인프라 초안 작성
