# LLM Wiki 작업 이력

이 문서는 위키 작업 기록을 남긴다.

## 작업 이력

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
  - 대상: `docs/product-spec.md`, `docs/technical-spec.md`, `docs/development-infra.md`, `docs/privacy-compliance.md`, `docs/fastapi-quickstart.md`
  - 반영: `.wiki/index.md`, `.wiki/insights.md`
  - 확인: OpenAI, Gemini, Supabase, Google Cloud, Cloudflare R2, Upstash, 개인정보보호위원회 공식 문서
- 2026-05-22: LLM Wiki를 최소 구조로 재시작
  - 유지: `.wiki/raw/`, `.wiki/index.md`, `.wiki/log.md`, `.wiki/insights.md`
  - 제거: 프로젝트 파일 스냅샷과 세분화된 위키 하위 디렉터리

## 이력관리

- 2026-05-23: 환경별 ENV 파일과 실행 스크립트 분리 이력 추가
- 2026-05-23: 로컬 인프라와 실행 스크립트 재정리 이력 추가
- 2026-05-22: MVP DB 설계 작업 이력 추가
- 2026-05-22: `docs/` 위키화와 공식 검증 작업 이력 추가
- 2026-05-22: 빈 작업 이력으로 재시작
