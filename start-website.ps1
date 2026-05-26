# Smart Medical Report Interpreter - Website Launcher
# Runs website WITHOUT Docker

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Medical Report Interpreter - WEBSITE STARTUP" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "c:\xampp\htdocs\medical"

# Check PostgreSQL
Write-Host "[1/5] Checking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq "Running") {
    Write-Host "  OK PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "  ERROR PostgreSQL is not running!" -ForegroundColor Red
    Write-Host "  Please start PostgreSQL service first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python
Write-Host ""
Write-Host "[2/5] Checking Python..." -ForegroundColor Yellow
$pythonVersion = py --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
Write-Host ""
Write-Host "[3/5] Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Node.js found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR Node.js not found!" -ForegroundColor Red
    Write-Host "  Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install Backend Dependencies
Write-Host ""
Write-Host "[4/5] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location "backend"
if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    py -m venv venv
}
Write-Host "  Installing packages (this may take a few minutes)..." -ForegroundColor Cyan
.\venv\Scripts\pip install --quiet fastapi uvicorn[standard] sqlalchemy psycopg2-binary pydantic pydantic-settings python-multipart pillow opencv-python-headless
Write-Host "  OK Backend dependencies installed" -ForegroundColor Green
Set-Location ".."

# Install Frontend Dependencies
Write-Host ""
Write-Host "[5/5] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing packages (this may take a few minutes)..." -ForegroundColor Cyan
    npm install --silent 2>&1 | Out-Null
}
Write-Host "  OK Frontend dependencies installed" -ForegroundColor Green
Set-Location ".."

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Starting Website Services..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend in new window
Write-Host "Starting Backend API Server (http://localhost:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\xampp\htdocs\medical\backend'; .\venv\Scripts\python.exe main.py"

Start-Sleep -Seconds 5

# Start Frontend in new window
Write-Host "Starting Frontend Website (http://localhost:3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\xampp\htdocs\medical\frontend'; npm run dev"

Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  WEBSITE IS LIVE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your website is accessible at:" -ForegroundColor White
Write-Host ""
Write-Host "  >> http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend API running at:" -ForegroundColor Gray
Write-Host "  http://localhost:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "Opening website in browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Two PowerShell windows have opened:" -ForegroundColor White
Write-Host "  1. Backend Server (port 8000)" -ForegroundColor White
Write-Host "  2. Frontend Website (port 3000)" -ForegroundColor White
Write-Host ""
Write-Host "To stop the website: Close both PowerShell windows" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to close this window (website will keep running)"
