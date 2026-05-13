Param(
    [switch]$RunTests,
    [switch]$OpenChat,
    [string]$Prompt = "Hello! What can you help me with today?"
)

$ErrorActionPreference = "Stop"

Write-Host "`n🚀 Edge LLM Windows Quickstart" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Python venv not found at .venv. Create it first."
}

Write-Host "→ Checking core imports..." -ForegroundColor Yellow
& $pythonExe -c "import llm_edge_router, rich, click; print('Core imports OK')"

Write-Host "→ Current system status:" -ForegroundColor Yellow
& $pythonExe edge-llm-cli.py status

if ($RunTests) {
    Write-Host "→ Running tests (excluding benchmark/performance)..." -ForegroundColor Yellow
    & $pythonExe -m pytest test_edge_llm.py -q -k "not benchmark and not performance"
}

if ($OpenChat) {
    Write-Host "→ Starting offline chat..." -ForegroundColor Yellow
    & $pythonExe edge-llm-cli.py chat --offline
} else {
    Write-Host "→ Running one-shot offline prompt..." -ForegroundColor Yellow
    & $pythonExe edge-llm-cli.py chat $Prompt --offline
}

Write-Host "`n✅ Quickstart complete." -ForegroundColor Green
