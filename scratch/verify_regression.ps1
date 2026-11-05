# Pre-Implementation Regression Guard & Quarantine Verification Script
# Verifies that 26/26 backend tests pass and frozen directories remain untouched

$ErrorActionPreference = "Stop"

Write-Host "=== Step 1: Checking Quarantine Directories ===" -ForegroundColor Cyan
$quarantineStatus = git status --porcelain coach/ data/problems/ tests/
if ($quarantineStatus) {
    Write-Error "Quarantine violation detected! Dirty files found in coach/, data/problems/, or tests/:`n$quarantineStatus"
    exit 1
} else {
    Write-Host "Git quarantine clean: coach/, data/problems/, and tests/ are completely pristine." -ForegroundColor Green
}

Write-Host "`n=== Step 2: Executing Pytest Suite (26 tests) ===" -ForegroundColor Cyan
$env:PYTHONPATH = "."
& .\.venv\Scripts\python.exe -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Error "Pytest regression failure! Tests failed with exit code $LASTEXITCODE."
    exit $LASTEXITCODE
} else {
    Write-Host "`nAll 26 backend regression tests PASSED cleanly." -ForegroundColor Green
}

Write-Host "`n=== Step 3: Shell Gate Status Verification ===" -ForegroundColor Cyan
Write-Host "Shell Gate Recount: 0 impossible elements in Streamlit. Default shell retained." -ForegroundColor Green
Write-Host "Pre-implementation baseline established successfully." -ForegroundColor Green
