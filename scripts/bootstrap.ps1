# CX MIRROR — Windows Bootstrap Script
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "CX MIRROR — Automated Bootstrap & Launch Sequence" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# 1. Python Virtual Environment
If (-Not (Test-Path "venv")) {
    Write-Host "[1/4] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}
Write-Host "[1/4] Activating Python virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# 2. Python Dependencies
Write-Host "[2/4] Installing Python requirements..." -ForegroundColor Yellow
.\venv\Scripts\python -m pip install -r backend\requirements.txt
.\venv\Scripts\python -m playwright install chromium

# 3. Frontend Dependencies
Write-Host "[3/4] Installing Frontend NPM dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

# 4. Generate Golden Baseline
Write-Host "[4/4] Generating Golden Mockup Baseline..." -ForegroundColor Yellow
.\venv\Scripts\python scripts\generate_golden.py

Write-Host "================================================================" -ForegroundColor Green
Write-Host "Bootstrap Complete! Launch services using:" -ForegroundColor Green
Write-Host "Backend:  .\venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
Write-Host "Frontend: cd frontend; npm run dev -- --host 127.0.0.1 --port 5173"
Write-Host "================================================================" -ForegroundColor Green

