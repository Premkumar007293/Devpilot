# Launch DevPilot FastAPI Backend
Write-Host "Starting DevPilot FastAPI backend on http://localhost:8000..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\..\backend"
& ".\.venv\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 8000 --reload
