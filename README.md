# scene-story-agent

`scene-story-agent`는 사용자가 남긴 사진, 영상, 메모를 원본 기록으로 보관하고, AI 해석과 벡터 검색으로 기록 사이의 연결을 보여주는 FastAPI 기반 MVP 프로젝트다.

## 핵심 이해

프로젝트는 원본 기록을 기준으로 동작한다.

- 사용자는 사진, 영상, 메모, 감정, 만족도를 원본 기록으로 남긴다.
- API 서버는 기록 생성, 파일 업로드, 썸네일 생성, 작업 등록, 상태 조회를 맡는다.
- Worker는 AI 해석, 임베딩 생성, 연관 기록 후보, 타임라인 후보 생성을 맡는다.
- PostgreSQL은 원본 기록, AI 파생 데이터, 작업 상태의 정본 저장소다.
- Redis는 작업 lock, 상태 캐시, 중복 등록 완화에만 사용한다.
- Object Storage는 원본 파일과 썸네일 파일을 저장한다.

## 처리 흐름

사진 기록 1건은 아래 순서로 처리한다.

1. API 서버가 원본 기록을 `processing` 상태로 저장한다.
2. API 서버가 파일을 저장하고 사진이면 썸네일을 생성한다.
3. API 서버가 `processing_jobs`에 `extract_ai_interpretation` 작업을 등록한다.
4. Worker가 AI 해석, 임베딩, 연관 기록, 타임라인 후보를 비동기로 처리한다.
5. 성공하면 기록은 `ready`, 작업은 `succeeded`가 된다.
6. 실패하면 10초 뒤 1회, 30초 뒤 2회 재시도하고, 3회 실패 시 기록은 `failed`가 된다.
7. 개발용 화면에서는 실패 기록을 `재시도 필요`로 표시하고 상세에서 다시 재시도할 수 있다.

상세 처리 흐름은 `docs/processing-flow.md`를 따른다.

## 상태 기준

사용자 화면과 작업 처리는 아래 상태를 기준으로 판단한다.

| 구분 | 상태 | 의미 |
|---|---|---|
| 기록 | `processing` | AI 해석과 파생 데이터 생성 대기 또는 진행 중 |
| 기록 | `ready` | 실사용자 화면에 노출 가능한 완료 상태 |
| 기록 | `failed` | 최대 재시도까지 실패한 상태 |
| 기록 | `deleted` | 삭제 처리된 상태 |
| 작업 | `queued` | 실행 대기 |
| 작업 | `running` | Worker 처리 중 |
| 작업 | `retrying` | 재시도 대기 |
| 작업 | `succeeded` | 처리 성공 |
| 작업 | `failed` | 처리 실패 확정 |

## 로컬 실행

빠른 로컬 확인은 `local` 스크립트를 사용한다.

macOS:

```bash
chmod +x scripts/local.sh
./scripts/local.sh
```

Windows PowerShell:

```powershell
.\scripts\local.ps1
```

`local` 스크립트는 API 서버와 Worker를 함께 실행한다.

Worker만 실행할 때는 다음 명령을 사용한다.

```powershell
.\.venv\Scripts\python -m app.workers.jobs
```

```bash
./scripts/worker.sh
```

로컬 MVP 화면은 아래 주소에서 확인한다.

```text
http://127.0.0.1:8000/ui/upload
```

## 문서 기준

상세 기준은 아래 문서를 따른다.

- 제품 기준: `docs/product-spec.md`
- 처리 흐름 기준: `docs/processing-flow.md`
- DB 기준: `docs/database-design.md`
- 인프라 기준: `docs/development-infra.md`
- 개인정보 기준: `docs/privacy-compliance.md`
- 빠른 실행 기준: `docs/fastapi-quickstart.md`
- 프로젝트 구조 기준: `.project/core_project.md`
- 코드 스타일 기준: `.project/core_code_style.md`
- 공통 실행과 테스트 기준: `.project/core_workflow.md`

테이블, 컬럼, 제약, 인덱스의 정본은 아래 SQL 파일을 따른다.

```text
scripts/postgres/initdb/002_schema.sql
```

## 문서 읽는 순서

처음 보는 사람은 아래 순서로 읽는다.

1. `README.md`: 프로젝트 핵심 구조와 실행 진입점
2. `docs/product-spec.md`: 제품 목표와 사용자 흐름
3. `docs/processing-flow.md`: 업로드, AI 비동기 처리, 재시도, UI polling 흐름
4. `docs/development-infra.md`: API, Worker, PostgreSQL, Redis 역할
5. `docs/database-design.md`: 상태값, 삭제, 조회, SQL 정본 기준
6. `docs/fastapi-quickstart.md`: 로컬 실행과 확인 절차
7. `.project/core_project.md`: 코드 구조와 변경 영향 범위

## 이력관리

- 2026-06-02: README를 프로젝트 이해 기준, 처리 흐름, 상태값, 문서 정본 기준 중심으로 재정리하고 `local` Worker 실행 설명과 처리 흐름 문서 참조 정정
- 2026-05-30: ENV 파일을 별도 관리 대상으로 정리
- 2026-05-30: 로컬 UI 확인 경로와 `/ui/upload` 화면 요약 추가
- 2026-05-24: 문서 체계를 제품, DB, 인프라, 개인정보, 로컬 실행 기준으로 정리
- 2026-04-24: README 초안 작성
