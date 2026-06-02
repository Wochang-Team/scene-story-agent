#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.local}"
export ENV_FILE

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo ".venv 가상 환경을 생성했습니다."
fi

source .venv/bin/activate

echo "worker를 실행합니다: python -m app.workers.jobs"
python -m app.workers.jobs
