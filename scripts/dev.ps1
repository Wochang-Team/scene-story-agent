$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

function Test-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command "python")) {
    Write-Error "python 명령을 찾을 수 없습니다."
    exit 1
}

if (-not (Test-Command "docker")) {
    Write-Error "docker 명령을 찾을 수 없습니다. Docker Desktop을 실행한 뒤 다시 시도하세요."
    exit 1
}

if (-not (Test-Path ".env.local")) {
    @"
POSTGRES_DB=scene_story_agent
POSTGRES_USER=scene_story_agent
POSTGRES_PASSWORD=scene_story_agent
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
"@ | Set-Content -Path ".env.local" -Encoding UTF8

    Write-Host ".env.local 파일을 기본 로컬 값으로 생성했습니다."
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host ".venv 가상 환경을 생성했습니다."
}

& ".\.venv\Scripts\Activate.ps1"

python -m pip install --upgrade pip
pip install -r requirements.txt

docker compose --env-file .env.local up -d postgres redis

Write-Host "API 서버를 실행합니다: http://127.0.0.1:8000"
Write-Host "종료하려면 Ctrl+C를 누르세요."

fastapi dev app/main.py
