#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE=".env.local"
export ENV_FILE
REQUIRED_ENV_KEYS=(
  POSTGRES_DB
  POSTGRES_USER
  POSTGRES_PASSWORD
  POSTGRES_HOST
  POSTGRES_PORT
  REDIS_HOST
  REDIS_PORT
  LOCAL_STORAGE_ROOT
  LOCAL_STORAGE_BUCKET
  LOCAL_FILE_MAX_BYTES
)

SERVER_PID=""

stop_server() {
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    echo
    echo "API 서버를 종료합니다."
    pkill -P "$SERVER_PID" >/dev/null 2>&1 || true
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" >/dev/null 2>&1 || true
  fi
}

trap stop_server INT TERM EXIT

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 명령을 찾을 수 없습니다."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker 명령을 찾을 수 없습니다. Docker Desktop을 실행한 뒤 다시 시도하세요."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker daemon에 연결할 수 없습니다. Docker Desktop을 실행한 뒤 다시 시도하세요."
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  cat >"$ENV_FILE" <<'EOF'
POSTGRES_DB=scene_story_agent
POSTGRES_USER=scene_story_agent
POSTGRES_PASSWORD=scene_story_agent
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_HOST=127.0.0.1
REDIS_PORT=6379

LOCAL_STORAGE_ROOT=.local_storage
LOCAL_STORAGE_BUCKET=local
LOCAL_FILE_MAX_BYTES=52428800

AI_PROVIDER=mock
AI_MODEL=mock-scene-v1
AI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=2
AI_IMAGE_MAX_BYTES=5242880
EMBEDDING_PROVIDER=mock
EMBEDDING_MODEL=mock-embedding-v1
EMBEDDING_DIMENSION=8
OPENAI_API_KEY=
GEMINI_API_KEY=
SIMILAR_RECORDS_LIMIT=5
SIMILARITY_THRESHOLD=0.70
EOF
  echo "$ENV_FILE 파일을 기본 로컬 값으로 생성했습니다."
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

docker compose --env-file "$ENV_FILE" up --build -d postgres redis

for sql_file in scripts/postgres/initdb/*.sql; do
  docker compose --env-file "$ENV_FILE" exec -T postgres \
    sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' <"$sql_file"
done

echo "local 환경으로 API 서버를 실행합니다: http://127.0.0.1:8000"
echo "종료하려면 Ctrl+C를 누르세요."

fastapi dev app/main.py &
SERVER_PID="$!"
wait "$SERVER_PID"
