$ErrorActionPreference = 'Stop'
$apiRoot = Join-Path $PSScriptRoot '../api'
$pythonPath = Join-Path $apiRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) {
    throw 'Create api/.venv and install requirements-dev.txt first; see README.md.'
}
& $pythonPath -m uvicorn app.main:app --app-dir $apiRoot --host 127.0.0.1 --port 8000 --reload --reload-dir (Join-Path $apiRoot 'app') --no-access-log --no-proxy-headers
exit $LASTEXITCODE
