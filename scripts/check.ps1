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
Push-Location $repoRoot
try {
    $auditPython = Join-Path $repoRoot 'api/.venv/Scripts/python.exe'
    & $auditPython -m unittest discover -s ml/tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Offline audit tests failed.' }
    & $auditPython -m ruff check ml --config api/pyproject.toml
    if ($LASTEXITCODE -ne 0) { throw 'Offline audit lint failed.' }
    & $auditPython -m ruff format --check ml --config api/pyproject.toml
    if ($LASTEXITCODE -ne 0) { throw 'Offline audit format check failed.' }
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
