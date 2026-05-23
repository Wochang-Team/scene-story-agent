# scene-story-agent 개발 워크플로우

## 문서 메타
이 문서는 실행과 운영 절차의 기준이다.

- 생성일: 2026-05-21
- 목적: Python 프로젝트의 환경 구성, 실행, 검증, 배포 절차를 정리한다.
- 문서 성격: 실행/운영 절차 문서
- 책임 범위(정본): Python 버전, 환경 관리자, 의존성 설치, 테스트, lint/typecheck, 배포, 환경 변수의 최종 기준
- 포함 범위: 환경 생성, 설치, 실행, 테스트, 정적 점검, 환경 변수, 배포 산출물
- 제외 범위: 코드 구조 설명, 세부 구현 스타일
- 연계 문서: `.project/core_project.md`, `.project/core_code_style.md`
- 중복 방지 기준:
  - 구조와 영향 범위는 `.project/core_project.md`에만 기록한다.
  - 구현 스타일은 `.project/core_code_style.md`에만 기록한다.
  - 제품/기술 의사결정 배경은 `docs/` 문서에만 기록한다.

## 버전과 도구
파일 근거가 있는 항목만 확정한다.

- Python 버전: 확인 필요
- Python 버전 근거: `.python-version`, `pyproject.toml`, `runtime.txt`, Dockerfile, CI 설정 없음
- 환경/패키지 관리자: `pip`
- 관리자 판정 근거: `requirements.txt`
- build backend: 확인 필요
- 웹 프레임워크: `fastapi[standard]==0.136.1`
- PostgreSQL client: `psycopg[binary]==3.2.13`
- Redis client: `redis==7.1.0`
- 로컬 PostgreSQL: `scene-story-agent-postgres:18.4-pgvector`
- 로컬 Redis: `redis:8.6-alpine`

## 환경 생성/설치
로컬 Python 가상 환경을 만든 뒤 의존성을 설치한다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 환경별 실행 스크립트
환경별 스크립트가 ENV 파일을 지정한다.

```bash
./scripts/local.sh
./scripts/dev.sh
./scripts/prd.sh
```

- `local`: `.env.local`을 읽고 Docker Compose 의존 서비스를 함께 실행한다.
- `dev`: `.env.dev`를 읽고 API 서버를 실행한다.
- `prd`: `.env.prd`를 읽고 API 서버를 실행한다.
- `.env.dev`, `.env.prd`는 Git에 포함하지만 값은 비워둔다.

## 로컬 의존 서비스
PostgreSQL과 Redis는 Docker Compose로 실행한다.

```bash
docker compose --env-file .env.local up --build -d
docker compose --env-file .env.local ps
```

- 종료:

```bash
docker compose --env-file .env.local down
```

- 볼륨까지 삭제:

```bash
docker compose --env-file .env.local down -v
```

## 실행
FastAPI 개발 서버로 API를 실행한다.

```bash
fastapi dev app/main.py
```

- 프로세스 확인:

```bash
curl http://127.0.0.1:8000/health
```

- 의존성 확인:

```bash
curl http://127.0.0.1:8000/health/ready
```

## 테스트
테스트 실행 기준은 아직 확정되지 않았다.

```bash
# 확인 필요
```

- 현재 상태:
  - `tests/` 디렉터리 없음
  - `pytest` 의존성 없음
  - 테스트 설정 파일 없음
- 문서상 방향:
  - 테스트를 추가할 때 `pytest` 사용을 검토한다.
  - readiness 테스트는 공유 로컬 DB와 Redis에 직접 의존하지 않게 구성한다.

## 정적 점검
정적 점검 도구는 아직 확정되지 않았다.

```bash
# 확인 필요
```

- 확인 필요:
  - lint 도구
  - format 도구
  - typecheck 도구
  - CI 실행 여부

## 환경 변수
환경 변수는 `ENV_FILE`과 `app/settings.py`를 기준으로 관리한다.

- 기본값:
  - `ENV_FILE=.env.local`
- Git 포함:
  - `.env.local`
  - `.env.dev`
  - `.env.prd`
- 값 관리:
  - `.env.local`은 로컬 기본값을 둔다.
  - `.env.dev`, `.env.prd`는 키만 두고 값은 서버에서 채운다.

| 이름 | 용도 | 필수 여부 | 근거 |
|---|---|---|---|
| `POSTGRES_DB` | PostgreSQL database 이름 | 필수 | `app/settings.py`, `docker-compose.yml` |
| `POSTGRES_USER` | PostgreSQL 사용자 | 필수 | `app/settings.py`, `docker-compose.yml` |
| `POSTGRES_PASSWORD` | PostgreSQL 비밀번호 | 필수 | `app/settings.py`, `docker-compose.yml` |
| `POSTGRES_HOST` | PostgreSQL host | 선택, 기본값 있음 | `app/settings.py` |
| `POSTGRES_PORT` | PostgreSQL port | 선택, 기본값 있음 | `app/settings.py`, `docker-compose.yml` |
| `REDIS_HOST` | Redis host | 선택, 기본값 있음 | `app/settings.py` |
| `REDIS_PORT` | Redis port | 선택, 기본값 있음 | `app/settings.py`, `docker-compose.yml` |

- 기본값:
  - `POSTGRES_HOST`: `127.0.0.1`
  - `POSTGRES_PORT`: `5432`
  - `REDIS_HOST`: `127.0.0.1`
  - `REDIS_PORT`: `6379`
- 관리 기준:
  - 실제 비밀번호와 API 키는 커밋하지 않는다.
  - 운영 환경에서는 Secret Manager 또는 동등한 비밀값 관리 도구를 사용한다.

## 배포/산출물
배포 산출물은 아직 구현 파일로 확정되지 않았다.

- 산출물: 확인 필요
- 배포 대상: 확인 필요
- 현재 없는 파일:
  - API 서버 Dockerfile
  - GitHub Actions workflow
  - 배포 설정 파일
  - DB 마이그레이션 설정
- 문서상 권장 방향:
  - FastAPI 컨테이너를 Cloud Run 또는 동등한 실행 환경에 배포한다.
  - PostgreSQL은 Supabase Postgres 또는 pgvector 지원 PostgreSQL을 사용한다.
  - Redis는 Upstash Redis 또는 동등한 Redis 서비스를 사용한다.
- 배포 전 확인:
  - Python 버전 고정
  - 운영 환경 변수 목록 확정
  - DB 마이그레이션 도구 확정
  - 헬스체크 경로 확정
  - AI Provider 키 관리와 로그 마스킹 기준 확인

## 실패 대응 기준
장애는 API 프로세스, 의존 서비스, 외부 Provider 순서로 확인한다.

- API 프로세스:
  - `/health` 응답을 확인한다.
- PostgreSQL:
  - `/health/ready` 응답을 확인한다.
  - `.env.local`의 DB host, port, database, user 값을 확인한다.
  - Docker Compose `postgres` healthcheck 상태를 확인한다.
- Redis:
  - `/health/ready` 응답을 확인한다.
  - `.env.local`의 Redis host, port 값을 확인한다.
  - Docker Compose `redis` healthcheck 상태를 확인한다.
- AI Provider:
  - 현재 구현 없음
  - 도입 후 timeout, retry, rate limit, 응답 파싱 실패를 구분한다.
- 개인정보:
  - 원본 파일 URL, OCR 원문, 프롬프트 원문이 로그에 남지 않았는지 확인한다.
  - 유출 가능성이 있으면 `docs/privacy-compliance.md` 기준으로 대응한다.

## 확인 필요
아래 항목은 현재 파일 근거로 확정할 수 없다.

- Python 버전 고정 방식
- 개발 의존성 관리 방식
- 테스트 실행 명령
- lint, format, typecheck 표준 도구
- API 서버 Dockerfile과 운영 배포 절차
- CI/CD workflow
- DB 마이그레이션 명령

## 이력관리
- 2026-05-23: `local`, `dev`, `prd` 실행 스크립트와 ENV 파일 기준 추가
- 2026-05-23: 로컬 PostgreSQL 18.4 + pgvector, Redis 8.6 기준으로 갱신
- 2026-05-21: Python/FastAPI 기준 개발 워크플로우 문서 생성
