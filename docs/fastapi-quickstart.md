# FastAPI 빠른 시작

## 문서 목적

이 문서는 로컬 개발자가 API 서버를 빠르게 실행하고 상태를 확인하는 절차를 정리한다.

- 포함 범위:
  - 필수 도구 확인
  - `local` 스크립트 실행
  - API 상태 확인
  - 8000번 포트 충돌 대응
  - 로컬 의존 서비스 종료
- 제외 범위:
  - 환경 변수 전체 목록
  - Docker Compose 상세 기준
  - 앱 모듈 구조 설명
  - DB 설계와 초기 SQL 상세

상세 기준은 정본 문서를 따른다.

- 실행, 환경 변수, Docker Compose 기준: `.project/core_workflow.md`
- 앱 파일, 엔드포인트, 모듈 구조 기준: `.project/core_project.md`
- DB 설계와 초기 SQL 기준: `docs/database-design.md`
- 인프라 선택 배경: `docs/development-infra.md`

## 준비 항목

로컬 PC에 다음 도구를 설치한다.

| 도구 | 용도 |
|---|---|
| Python | API 서버 실행 |
| Visual Studio Code | 코드 편집 |
| Python Extension for VS Code | Python 개발 지원 |
| Docker Desktop | PostgreSQL, Redis 실행 |

설치 상태를 확인한다.

Windows PowerShell:

```powershell
python --version
docker --version
docker compose version
```

macOS:

```bash
python3 --version
docker --version
docker compose version
```

- Windows에서 `docker` 명령을 찾지 못하면 새 PowerShell 터미널을 연다.
- macOS에서 `docker` 명령을 찾지 못하면 Docker Desktop을 실행한 뒤 새 터미널을 연다.

## 로컬 실행

`local` 스크립트로 로컬 환경 준비와 서버 실행을 한 번에 처리한다.

Windows PowerShell:

```powershell
.\scripts\local.ps1
```

실행 정책 때문에 막히면 다음 명령을 사용한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\local.ps1
```

macOS:

```bash
chmod +x scripts/local.sh
./scripts/local.sh
```

`local` 스크립트의 실행 기준은 `.project/core_workflow.md`를 따른다.

- `.env.local`이 없으면 기본 로컬 값으로 생성한다.
- `.venv`가 없으면 Python 가상 환경을 생성한다.
- `requirements.txt` 의존성을 설치한다.
- Docker Compose로 PostgreSQL과 Redis를 실행한다.
- PostgreSQL `vector` 확장을 확인한다.
- `fastapi dev app/main.py`로 API 서버를 실행한다.

## API 확인

서버가 실행되면 다음 주소를 확인한다.

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/ready
http://127.0.0.1:8000/docs
```

터미널에서는 다음 명령으로 확인한다.

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/ready
```

정상 응답 기준은 다음이다.

- `/health`:

```json
{
  "status": "ok"
}
```

- `/health/ready`:

```json
{
  "status": "ok",
  "dependencies": {
    "postgres": "ok",
    "redis": "ok"
  }
}
```

## 포트 충돌 대응

이미 8000번 포트에서 서버가 실행 중이면 새 서버 실행은 실패한다.

- 기존 서버가 정상인지 먼저 확인한다.

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/ready
```

- 응답이 정상이면 기존 서버를 그대로 사용한다.
- 응답이 비정상이면 8000번 포트를 점유한 프로세스를 종료한다.

Windows PowerShell:

```powershell
netstat -ano | Select-String ':8000'
taskkill /PID <PID> /F
```

macOS:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
kill -9 <PID>
```

종료 후 `local` 스크립트를 다시 실행한다.

## 종료

API 서버는 실행 중인 터미널에서 종료한다.

```text
Ctrl+C
```

PostgreSQL과 Redis 컨테이너는 필요할 때만 종료한다.

```bash
docker compose --env-file .env.local down
```

저장된 데이터까지 삭제할 때만 볼륨을 함께 삭제한다.

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

- 2026-05-24: 중복 실행 기준을 정본 문서 참조로 대체하고 빠른 실행 절차 중심으로 정리
- 2026-05-23: 환경별 실행 스크립트와 로컬 의존 서비스 버전 기준 반영
- 2026-05-22: Windows, macOS 로컬 실행 절차와 서버 재시작 기준 정리
- 2026-04-27: FastAPI 설치와 Hello World 문서 작성
