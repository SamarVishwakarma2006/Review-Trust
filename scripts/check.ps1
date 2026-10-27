$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $repoRoot 'api')
try {
    & ./.venv/Scripts/python.exe -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Backend dependency check failed.' }
    & ./.venv/Scripts/python.exe -m pytest
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
    & ./.venv/Scripts/python.exe -m ruff check .
    if ($LASTEXITCODE -ne 0) { throw 'Backend lint failed.' }
    & ./.venv/Scripts/python.exe -m ruff format --check .
    if ($LASTEXITCODE -ne 0) { throw 'Backend format check failed.' }
} finally {
    Pop-Location
}
Push-Location (Join-Path $repoRoot 'web')
try {
    foreach ($check in @('test', 'lint', 'typecheck', 'build')) {
        & npm.cmd run $check
        if ($LASTEXITCODE -ne 0) { throw "Frontend $check failed." }
    }
} finally {
    Pop-Location
}
