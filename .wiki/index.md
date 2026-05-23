# LLM Wiki 색인

이 문서는 `scene-story-agent` 개발 자료의 출발점이다.

## 프로젝트 문서

현재 프로젝트 문서는 `docs/`를 기준으로 읽는다.

- [프로덕트 스펙](../docs/product-spec.md): 원본 기록, AI 해석 정보, 벡터 연결, 타임라인, MVP 범위
- [기술 스펙](../docs/technical-spec.md): FastAPI, PostgreSQL, pgvector, AI Provider, 비동기 처리, 삭제 연계
- [DB 설계](../docs/database-design.md): 원본 기록, 파일, AI 해석, 임베딩, 연결 후보, 작업 상태 테이블 설계
- [개발 인프라](../docs/development-infra.md): Cloud Run, Supabase, Cloudflare R2, Upstash Redis, OpenAI/Gemini 운영 후보
- [개인정보 보호 조치](../docs/privacy-compliance.md): 개인정보 분류, 동의, AI 처리, 위치성 정보, 삭제, 출시 전 점검
- [FastAPI 빠른 시작](../docs/fastapi-quickstart.md): Windows PowerShell 기준 로컬 실행 절차

## 개발 기준 요약

제품과 구현은 원본 기록을 기준으로 설계한다.

- 원본 기록:
  - 사진, 영상, 메모, 감정, 만족도, 작성 시점을 기준 데이터로 둔다.
  - AI 해석 정보와 분리해 저장하고 보여준다.
- AI 해석 정보:
  - 장소 후보, OCR 후보, 태그, 요약, 연결 후보를 만든다.
  - 사용자가 확인하고 수정할 수 있어야 한다.
- 벡터 연결:
  - 임베딩 검색 결과는 최종 판단이 아니라 후보로 사용한다.
  - 재방문과 타임라인 반영은 후보 기록과 현재 기록을 함께 비교해 판단한다.
- 삭제:
  - 원본 기록 삭제 시 원본 파일, 사용자 입력, AI 해석 정보, 임베딩, 연결 후보, 타임라인 반영 결과를 함께 처리한다.
- 운영:
  - 개발 데이터와 운영 데이터는 공유하지 않는다.
  - AI Provider, 스토리지, DB, Redis는 교체 가능한 경계로 둔다.
- 환경 파일:
  - `local`은 `.env.local`을 읽는다.
  - `dev`는 `.env.dev`를 읽는다.
  - `prd`는 `.env.prd`를 읽는다.
  - `.env.dev`, `.env.prd`는 Git에 포함하지만 값은 서버에서 채운다.

## 공식 검증 결과

외부 기술 주장은 2026-05-22 기준 공식 문서로 확인했다.

- OpenAI:
  - `gpt-5.4`, `gpt-5.4 mini` 모델명과 `gpt-5.4` 입력 $2.50/1M, 출력 $15.00/1M, `gpt-5.4 mini` 입력 $0.75/1M, 출력 $4.50/1M 가격은 공식 가격표와 모델 문서 기준으로 일치한다.
  - 이미지 입력은 `low`, `high`, `original`, `auto` detail을 지원한다. 단, `original`은 `gpt-5.4`와 이후 모델 기준이고 `gpt-5.4-mini`는 `low`, `high`, `auto`만 확인된다.
  - API platform 입력과 출력은 기본적으로 모델 학습에 사용하지 않는다는 OpenAI 비즈니스 데이터 정책이 확인된다.
- Gemini:
  - `gemini-2.5-flash-lite` 유료 가격은 입력 $0.10/1M, 출력 $0.40/1M으로 확인된다.
  - Free Tier는 모델별 제한 안에서 무료지만, Google 문서는 Free Tier 데이터가 제품 개선에 사용될 수 있고 Paid Tier는 사용되지 않는다고 구분한다.
  - `gemini-embedding-001`은 Gemini API와 Vertex AI에서 일반 제공 중이며 가격은 입력 $0.15/1M tokens로 확인된다.
- Supabase와 pgvector:
  - Supabase는 Postgres와 pgvector 기반 AI/Vectors 툴킷을 제공한다.
  - Supabase client는 PostgREST를 거치므로 pgvector 유사도 연산은 Postgres 함수로 감싼 뒤 `rpc()`로 호출하는 방식이 공식 예시에 나온다.
- PostgreSQL:
  - PostgreSQL 18은 `uuidv7()`를 제공하므로 신규 PK 생성 기준은 UUID v7로 둔다.
  - 로컬 DB는 PostgreSQL 18.4 + pgvector 포함 이미지로 실행한다.
- Google Cloud:
  - Cloud Tasks는 Cloud Run 서비스로 비동기 작업을 밀어 넣는 용도에 맞다.
  - Cloud Tasks timeout을 넘는 작업은 Cloud Run Jobs 검토가 필요하다.
  - Cloud Run Jobs는 단일 작업 또는 최대 10,000개 독립 task 병렬 실행 구조를 지원한다.
- Cloudflare R2:
  - R2 presigned URL은 특정 객체와 작업에 대한 임시 접근을 제공한다.
  - URL 자체를 bearer token처럼 취급해야 하며, 민감 작업은 짧은 만료 시간을 사용한다.
- Upstash:
  - Upstash Redis는 serverless Redis 호환 서비스다.
  - Redis API 전체가 아니라 대부분을 지원하므로 사용할 명령은 호환성 문서를 확인해야 한다.
- 한국 개인정보:
  - 개인정보 처리방침 작성지침 2025.4. 공식 게시가 확인된다.
  - 사진, 메모, 위치성 정보, AI 해석 정보, 임베딩을 개인정보 또는 개인정보에 준하는 데이터로 취급하는 현재 문서 방향은 출시 전 법률 검토 전제와 맞다.

## 확인 필요

구현 전 다시 확인할 항목이다.

- `docs/development-infra.md`의 AI 비용 시뮬레이션은 공식 단가와 입력 토큰 산정 방식이 바뀔 수 있으므로 출시 전 재계산한다.
- OpenAI 이미지 detail 정책은 모델별 차이가 있으므로 `gpt-5.4`와 `gpt-5.4-mini`를 구분해 문서화한다.
- Gemini Free Tier는 개발·검증 전용으로만 사용하고, 개인정보 처리 검증이 필요한 환경은 Paid Tier 기준으로 본다.
- R2 presigned URL을 브라우저에서 쓰면 CORS 설정과 URL 노출 범위를 별도로 검토한다.
- Supabase pgvector 검색 API는 직접 SQL 호출이 아니라 Postgres 함수와 `rpc()` 경계를 기준으로 설계한다.
- 위치성 정보 기능이 구체화되면 위치정보법 적용 여부를 별도로 검토한다.

## 공식 출처

- OpenAI API Pricing, 확인일 2026-05-22: https://openai.com/api/pricing/
- OpenAI GPT-5.4 model docs, 확인일 2026-05-22: https://developers.openai.com/api/docs/models/gpt-5.4/
- OpenAI Images and vision, 확인일 2026-05-22: https://developers.openai.com/api/docs/guides/images-vision
- OpenAI Business data privacy, 확인일 2026-05-22: https://openai.com/business-data/
- PostgreSQL 18.4 release notes, 확인일 2026-05-23: https://www.postgresql.org/docs/release/
- PostgreSQL 18 UUID functions, 확인일 2026-05-23: https://www.postgresql.org/docs/18/functions-uuid.html
- PostgreSQL Docker official image, 확인일 2026-05-23: https://hub.docker.com/_/postgres
- Redis Docker official image, 확인일 2026-05-23: https://hub.docker.com/_/redis
- Gemini Developer API Pricing, 확인일 2026-05-22: https://ai.google.dev/gemini-api/docs/pricing
- Gemini API Billing, 확인일 2026-05-22: https://ai.google.dev/gemini-api/docs/billing
- Gemini API Rate limits, 확인일 2026-05-22: https://ai.google.dev/gemini-api/docs/rate-limits
- Gemini Embedding announcement, 확인일 2026-05-22: https://developers.googleblog.com/en/gemini-embedding-available-gemini-api/
- Supabase AI & Vectors, 확인일 2026-05-22: https://supabase.com/docs/guides/ai
- Supabase Vector columns, 확인일 2026-05-22: https://supabase.com/docs/guides/ai/vector-columns
- Google Cloud Run Cloud Tasks, 확인일 2026-05-22: https://docs.cloud.google.com/run/docs/triggering/using-tasks
- Google Cloud Run Jobs, 확인일 2026-05-22: https://docs.cloud.google.com/run/docs/create-jobs
- Cloudflare R2 Presigned URLs, 확인일 2026-05-22: https://developers.cloudflare.com/r2/api/s3/presigned-urls/
- Upstash Redis FAQ, 확인일 2026-05-22: https://upstash.com/docs/redis/help/faq
- 개인정보 처리방침 작성지침 2025.4., 확인일 2026-05-22: https://m.pipc.go.kr/np/cop/bbs/selectBoardArticle.do?bbsId=BS217&mCode=G010030020&nttId=11134

## 이력관리

- 2026-05-23: 환경별 ENV 파일과 실행 스크립트 기준 반영
- 2026-05-23: PostgreSQL 18, UUID v7, 로컬 pgvector 이미지 기준 반영
- 2026-05-22: DB 설계 문서 링크 추가
- 2026-05-22: `docs/` 문서 기반 위키 색인과 공식 검증 결과 작성
