$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

$env:ENV_FILE = ".env.local"
$WorkerProcess = $null
$RequiredEnvKeys = @(
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "REDIS_HOST",
    "REDIS_PORT",
    "LOCAL_STORAGE_ROOT",
    "LOCAL_STORAGE_BUCKET",
    "LOCAL_FILE_MAX_BYTES"
)

function Test-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Stop-LocalProcesses {
    if ($null -ne $WorkerProcess -and -not $WorkerProcess.HasExited) {
        Write-Host ""
        Write-Host "worker를 종료합니다."
        Stop-Process -Id $WorkerProcess.Id -Force -ErrorAction SilentlyContinue
        $WorkerProcess.WaitForExit()
    }
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

Get-ChildItem "scripts/postgres/initdb" -Filter "*.sql" | Sort-Object Name | ForEach-Object {
    Get-Content $_.FullName -Raw | docker compose --env-file $env:ENV_FILE exec -T postgres `
        sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
}

Write-Host "local 환경으로 API 서버를 실행합니다: http://127.0.0.1:8000"
Write-Host "local 환경으로 worker를 실행합니다: python -m app.workers.jobs"
Write-Host "종료하려면 Ctrl+C를 누르세요."

$PythonPath = Join-Path $RootDir ".venv\Scripts\python.exe"
$WorkerProcess = Start-Process `
    -FilePath $PythonPath `
    -ArgumentList "-m", "app.workers.jobs" `
    -WorkingDirectory $RootDir `
    -NoNewWindow `
    -PassThru

try {
    fastapi dev app/main.py
}
finally {
    Stop-LocalProcesses
}
