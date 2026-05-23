$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

$env:ENV_FILE = ".env.prd"
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

if (-not (Test-Path $env:ENV_FILE)) {
    Write-Error "$env:ENV_FILE 파일이 없습니다. .env.local을 참고해 생성하세요."
    exit 1
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

Write-Host "prd 환경으로 API 서버를 실행합니다: http://0.0.0.0:8000"
Write-Host "종료하려면 Ctrl+C를 누르세요."

fastapi run app/main.py --host 0.0.0.0 --port 8000
