# LLM Wiki 작업 이력

이 문서는 위키 작업 기록을 남긴다.

## 작업 이력

- 2026-05-30: 로컬 MVP UI와 처리 상태 문서 반영
  - 변경: `README.md`, `docs/product-spec.md`, `docs/database-design.md`, `.wiki/index.md`, `.wiki/insights.md`
  - 기준: 서버 실행 후 `/ui/upload`에서 MVP 업로드, 목록, 상세, 처리 상태, 저장 데이터를 확인한다.
  - 기준: 처리 상태는 실제 API 호출과 내부 처리 단계를 구분한다.
  - 기준: AI 해석 토큰 사용량은 `record_ai_interpretations.raw_response_ref.token_usage`에 저장한다.
- 2026-05-27: 자체 서버 운영 기준으로 인프라 문서 정리
  - 변경: `docs/development-infra.md`, `docs/database-design.md`, `.project/core_workflow.md`, `README.md`
  - 기준: API 서버는 자체 서버의 컨테이너 또는 systemd 서비스로 운영한다.
  - 기준: PostgreSQL 18 + pgvector, Redis 8.6, 비공개 Object Storage 또는 사설 파일 저장소를 우선한다.
  - 반영: `.wiki/index.md`, `.wiki/insights.md`
- 2026-05-24: `docs/` 문서 체계 정리
  - 삭제: `docs/technical-spec.md`
  - 기준: 제품, DB, 인프라, 개인정보, 로컬 실행 문서만 유지한다.
  - 반영: `README.md`, `.wiki/index.md`, `.project/core_project.md`, `docs/product-spec.md`, `docs/development-infra.md`, `docs/database-design.md`
- 2026-05-23: 환경별 ENV 파일과 실행 스크립트 분리
  - 추가: `.env.dev`, `.env.prd`, `scripts/local.sh`, `scripts/prd.sh`, `scripts/local.ps1`, `scripts/prd.ps1`
  - 변경: `app/settings.py`, `scripts/dev.sh`, `scripts/dev.ps1`
  - 기준: Git에는 `.env.local`, `.env.dev`, `.env.prd`를 포함하고 dev/prd 값은 서버에서 채운다.
- 2026-05-23: 로컬 인프라와 실행 스크립트 기준 재정리
  - 변경: `docker-compose.yml`, `infra/postgres/Dockerfile`, `infra/postgres/initdb/001_extensions.sql`
  - 기준: PostgreSQL 18.4 + pgvector, Redis 8.6, UUID v7
  - 반영: `docs/database-design.md`, `docs/development-infra.md`, `docs/fastapi-quickstart.md`, `.project/core_project.md`, `.project/core_workflow.md`, `.wiki/index.md`
- 2026-05-22: MVP DB 설계 문서 작성
  - 생성: `docs/database-design.md`
  - 반영: `.wiki/index.md`
- 2026-05-22: `docs/` 문서 위키화와 공식 문서 검증
  - 대상: `docs/product-spec.md`, `docs/development-infra.md`, `docs/privacy-compliance.md`, `docs/fastapi-quickstart.md`
  - 반영: `.wiki/index.md`, `.wiki/insights.md`
  - 확인: OpenAI, Gemini, Supabase, Google Cloud, Cloudflare R2, Upstash, 개인정보보호위원회 공식 문서
- 2026-05-22: LLM Wiki를 최소 구조로 재시작
  - 유지: `.wiki/raw/`, `.wiki/index.md`, `.wiki/log.md`, `.wiki/insights.md`
  - 제거: 프로젝트 파일 스냅샷과 세분화된 위키 하위 디렉터리

## 이력관리

- 2026-05-30: 로컬 MVP UI와 처리 상태 문서 반영 이력 추가
- 2026-05-27: 자체 서버 운영 기준 문서 변경 이력 추가
- 2026-05-24: `docs/` 문서 체계 정리 이력 추가
- 2026-05-23: 환경별 ENV 파일과 실행 스크립트 분리 이력 추가
- 2026-05-23: 로컬 인프라와 실행 스크립트 재정리 이력 추가
- 2026-05-22: MVP DB 설계 작업 이력 추가
- 2026-05-22: `docs/` 위키화와 공식 검증 작업 이력 추가
- 2026-05-22: 빈 작업 이력으로 재시작
