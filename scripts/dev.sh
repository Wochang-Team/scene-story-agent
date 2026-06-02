#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE=".env.dev"
export ENV_FILE
REQUIRED_ENV_KEYS=(
  POSTGRES_DB
  POSTGRES_USER
  POSTGRES_PASSWORD
  POSTGRES_HOST
  POSTGRES_PORT
  REDIS_HOST
  REDIS_PORT
)

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 명령을 찾을 수 없습니다."
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "$ENV_FILE 파일이 없습니다. .env.local을 참고해 생성하세요."
  exit 1
fi

missing_keys=()
for key in "${REQUIRED_ENV_KEYS[@]}"; do
  if ! grep -Eq "^${key}=.+" "$ENV_FILE"; then
    missing_keys+=("$key")
  fi
done

if [ "${#missing_keys[@]}" -gt 0 ]; then
  echo "$ENV_FILE 파일에 값이 비어 있는 항목이 있습니다: ${missing_keys[*]}"
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo ".venv 가상 환경을 생성했습니다."
fi

source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "dev 환경으로 API 서버를 실행합니다: http://0.0.0.0:8000"
echo "dev 환경으로 worker를 실행합니다: python -m app.workers.jobs"
echo "종료하려면 Ctrl+C를 누르세요."

python -m app.workers.jobs &
WORKER_PID="$!"

stop_processes() {
  if [ -n "$WORKER_PID" ] && kill -0 "$WORKER_PID" >/dev/null 2>&1; then
    echo
    echo "worker를 종료합니다."
    kill "$WORKER_PID" >/dev/null 2>&1 || true
    wait "$WORKER_PID" >/dev/null 2>&1 || true
  fi
}

trap stop_processes INT TERM EXIT

fastapi run app/main.py --host 0.0.0.0 --port 8000
