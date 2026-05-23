# FastAPI 빠른 시작

## 문서 목적

이 문서는 로컬 개발환경에서 `scene-story-agent` API 서버와 의존 서비스를 실행하는 절차를 정리한다.

FastAPI, Python 가상 환경, Docker의 개념 설명은 공식 문서를 따른다.

## 준비 항목

로컬 PC에 다음 도구를 설치한다.

| 도구 | 용도 |
|---|---|
| Python | API 서버 실행 |
| Visual Studio Code | 코드 편집 |
| Python Extension for VS Code | Python 개발 지원 |
| Docker Desktop | PostgreSQL, Redis 실행 |

PowerShell에서 설치 상태를 확인한다.

```powershell
python --version
docker --version
docker compose version
```

macOS 터미널에서는 다음 명령으로 확인한다.

```bash
python3 --version
docker --version
docker compose version
```

Docker Desktop을 Chocolatey로 설치한 직후 `docker` 명령을 찾지 못하면 새 PowerShell 터미널을 연 뒤 다시 확인한다.

macOS에서 `docker` 명령을 찾지 못하면 Docker Desktop을 실행한 뒤 새 터미널을 열고 다시 확인한다.

## Python 환경 설정

Windows PowerShell에서는 `local` 스크립트로 로컬 환경 준비와 서버 실행을 한 번에 처리할 수 있다.

```powershell
.\scripts\local.ps1
```

실행 정책 때문에 스크립트가 막히면 다음 명령을 사용한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1
```

macOS에서는 `local` 스크립트로 로컬 환경 준비와 서버 실행을 한 번에 처리할 수 있다.

```bash
chmod +x scripts/local.sh
./scripts/local.sh
```

`local` 스크립트는 다음 작업을 순서대로 실행한다.

- `.env.local`이 없으면 기본 로컬 값으로 생성한다.
- `.venv`가 없으면 Python 가상 환경을 생성한다.
- `requirements.txt` 의존성을 설치한다.
- Docker Compose로 PostgreSQL 18.4 + pgvector와 Redis 8.6을 실행한다.
- PostgreSQL에 `vector` 확장이 없으면 생성한다.
- `fastapi dev app/main.py`로 API 서버를 실행한다.
- `Ctrl+C`를 누르면 FastAPI 개발 서버 프로세스를 종료한다.

서버 환경에서는 환경별 스크립트를 사용한다.

```bash
./scripts/dev.sh
./scripts/prd.sh
```

```powershell
.\scripts\dev.ps1
.\scripts\prd.ps1
```

- `dev` 스크립트는 `.env.dev`를 읽는다.
- `prd` 스크립트는 `.env.prd`를 읽는다.
- `.env.dev`, `.env.prd`는 Git에 포함하지만 값은 비워둔다.
- 서버에서는 `.env.local`을 참고해 필요한 값을 채운다.

Windows PowerShell에서는 프로젝트 루트에서 다음 명령을 실행한다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS 터미널에서는 프로젝트 루트에서 다음 명령을 실행한다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

VS Code에서는 `.venv` 인터프리터를 선택한다.

```text
Python: Select Interpreter
```

## API 파일

API 시작 파일은 `app/main.py`를 사용한다.

```python
from fastapi import FastAPI

app = FastAPI(title="scene-story-agent")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "scene-story-agent API"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

PostgreSQL과 Redis 연결 확인은 `/health/ready`에서 처리한다.

## PostgreSQL과 Redis 실행

로컬 환경 파일을 만든다.

Windows PowerShell:

```powershell
New-Item -ItemType File .env.local
```

macOS:

```bash
touch .env.local
```

`.env.local`에 다음 값을 입력한다.

```text
POSTGRES_DB=scene_story_agent
POSTGRES_USER=scene_story_agent
POSTGRES_PASSWORD=scene_story_agent
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

프로젝트 루트에서 다음 명령을 실행한다.

```powershell
docker compose --env-file .env.local up --build -d postgres redis
```

실행 상태를 확인한다.

```powershell
docker compose --env-file .env.local ps
```

로그를 확인한다.

```powershell
docker compose --env-file .env.local logs -f postgres redis
```

로그 확인을 끝낼 때는 `Ctrl+C`를 누른다. 컨테이너는 계속 실행된다.

로컬 접속 정보는 다음 값을 사용한다.

| 항목 | 값 |
|---|---|
| PostgreSQL Host | `.env.local`의 `POSTGRES_HOST` |
| PostgreSQL Port | `.env.local`의 `POSTGRES_PORT` |
| PostgreSQL Database | `.env.local`의 `POSTGRES_DB` |
| PostgreSQL User | `.env.local`의 `POSTGRES_USER` |
| PostgreSQL Password | `.env.local`의 `POSTGRES_PASSWORD` |
| Redis Host | `.env.local`의 `REDIS_HOST` |
| Redis Port | `.env.local`의 `REDIS_PORT` |

## API 서버 실행

Windows PowerShell에서는 프로젝트 루트에서 가상 환경을 활성화한 뒤 서버를 실행한다.

```powershell
.\.venv\Scripts\Activate.ps1
fastapi dev app/main.py
```

macOS 터미널에서는 다음 명령을 실행한다.

```bash
source .venv/bin/activate
fastapi dev app/main.py
```

서버가 실행되면 다음 주소를 사용한다.

```text
http://127.0.0.1:8000
```

## API 확인

브라우저에서 다음 주소를 연다.

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/ready
http://127.0.0.1:8000/docs
```

`/health` 응답은 다음과 같다.

```json
{
  "status": "ok"
}
```

`/health/ready` 응답은 다음과 같다.

```json
{
  "status": "ok",
  "dependencies": {
    "postgres": "ok",
    "redis": "ok"
  }
}
```

## API 서버 종료

API 서버를 실행한 터미널에서 다음 키를 누른다.

```text
Ctrl+C
```

## API 서버 재시작

코드를 바꾼 뒤 `/docs`나 응답이 바뀌지 않으면 서버를 종료하고 다시 실행한다.

Windows PowerShell:

```powershell
fastapi dev app/main.py
```

macOS:

```bash
fastapi dev app/main.py
```

그래도 8000번 포트가 이전 서버를 보고 있으면 남은 프로세스를 확인한다.

Windows PowerShell:

```powershell
netstat -ano | Select-String ':8000'
```

`LISTENING` 상태의 PID를 종료한다.

```powershell
taskkill /PID <PID> /F
```

macOS:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

`PID`를 확인한 뒤 종료한다.

```bash
kill -9 <PID>
```

종료 후 서버를 다시 실행한다.

```powershell
fastapi dev app/main.py
```

## PostgreSQL과 Redis 종료

컨테이너를 종료한다.

```bash
docker compose --env-file .env.local down
```

저장된 데이터까지 삭제할 때만 다음 명령을 사용한다.

```bash
docker compose --env-file .env.local down -v
```

`-v` 옵션은 PostgreSQL 데이터 볼륨도 함께 삭제한다.

## 참고 자료

- Python, [venv 공식 문서](https://docs.python.org/3/library/venv.html)
- FastAPI, [공식 문서](https://fastapi.tiangolo.com/)
- FastAPI, [First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- Docker, [Compose 공식 문서](https://docs.docker.com/compose/)

## 이력관리

- 2026-05-23: 환경별 실행 스크립트와 `.env.dev`, `.env.prd` 사용 기준 추가
- 2026-05-23: 로컬 의존 서비스 실행 기준을 PostgreSQL 18.4 + pgvector, Redis 8.6으로 갱신
- 2026-05-22: Windows PowerShell용 개발 실행 스크립트 안내 추가
- 2026-05-22: 개발 실행 스크립트의 `Ctrl+C` 종료 처리 설명 추가
- 2026-05-22: macOS용 개발 실행 스크립트 안내 추가
- 2026-05-22: macOS 기준 설치 확인, 가상 환경, 환경 파일 생성, 서버 실행, 포트 정리 절차 추가
- 2026-04-27: API 서버 재시작과 포트 점유 프로세스 정리 절차 추가
- 2026-04-27: `requirements.txt` 설치와 `/health/ready` 확인 절차 추가
- 2026-04-27: Docker 접속 정보를 `.env.local` 기준으로 변경
- 2026-04-27: 로컬 PostgreSQL과 Redis 기본 접속 정보 추가
- 2026-04-27: 빠른 개발환경 설정 중심으로 문서 재정리
- 2026-04-27: Docker 기반 PostgreSQL과 Redis 실행 절차 추가
- 2026-04-27: 프로젝트 구조 기준 서버 실행과 종료 방법 추가
- 2026-04-27: 가상 환경 역할과 패키지 설치 범위 설명 추가
- 2026-04-27: FastAPI 설치와 Hello World 문서 작성
