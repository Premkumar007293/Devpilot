# DevPilot Development Environment Setup Script
Write-Host "Setting up DevPilot development environment..." -ForegroundColor Cyan

# Check Python
Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "backend\.venv")) {
    python -m venv backend\.venv
}
& "backend\.venv\Scripts\pip.exe" install --upgrade pip
& "backend\.venv\Scripts\pip.exe" install -r backend\requirements.txt

# Check Frontend
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

Write-Host "DevPilot environment setup completed successfully!" -ForegroundColor Green
