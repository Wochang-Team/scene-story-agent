$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

$env:ENV_FILE = ".env.local"
$RequiredEnvKeys = @(
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "REDIS_HOST",
    "REDIS_PORT"
)

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

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker daemon에 연결할 수 없습니다. Docker Desktop을 실행한 뒤 다시 시도하세요."
    exit 1
}

if (-not (Test-Path $env:ENV_FILE)) {
    @"
POSTGRES_DB=scene_story_agent
POSTGRES_USER=scene_story_agent
POSTGRES_PASSWORD=scene_story_agent
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
"@ | Set-Content -Path $env:ENV_FILE -Encoding UTF8

    Write-Host "$env:ENV_FILE 파일을 기본 로컬 값으로 생성했습니다."
}

$EnvFileValues = @{}
Get-Content $env:ENV_FILE | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $EnvFileValues[$Matches[1].Trim()] = $Matches[2].Trim()
    }
}

$MissingKeys = $RequiredEnvKeys | Where-Object {
    -not $EnvFileValues.ContainsKey($_) -or [string]::IsNullOrWhiteSpace($EnvFileValues[$_])
}

if ($MissingKeys.Count -gt 0) {
    Write-Error "$env:ENV_FILE 파일에 값이 비어 있는 항목이 있습니다: $($MissingKeys -join ', ')"
    exit 1
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host ".venv 가상 환경을 생성했습니다."
}

& ".\.venv\Scripts\Activate.ps1"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

docker compose --env-file $env:ENV_FILE up --build -d postgres redis
docker compose --env-file $env:ENV_FILE exec -T postgres `
    sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "create extension if not exists vector;"'

Write-Host "local 환경으로 API 서버를 실행합니다: http://127.0.0.1:8000"
Write-Host "종료하려면 Ctrl+C를 누르세요."

fastapi dev app/main.py
