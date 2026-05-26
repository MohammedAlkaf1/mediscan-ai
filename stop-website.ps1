# Smart Medical Report Interpreter - Website Shutdown Script

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Medical Report Interpreter - STOPPING SYSTEM" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Stop Backend (Python/Uvicorn processes)
Write-Host "[1/3] Stopping Backend Server (port 8000)..." -ForegroundColor Yellow
$backendProcesses = Get-Process python,uvicorn -ErrorAction SilentlyContinue
if ($backendProcesses) {
    $backendProcesses | Stop-Process -Force
    Write-Host "  ✓ Backend server stopped" -ForegroundColor Green
} else {
    Write-Host "  - No backend processes found" -ForegroundColor Gray
}

# Stop Frontend (Node/Next.js processes)
Write-Host ""
Write-Host "[2/3] Stopping Frontend Website (port 3000)..." -ForegroundColor Yellow
$frontendProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($frontendProcesses) {
    $frontendProcesses | Stop-Process -Force
    Write-Host "  ✓ Frontend website stopped" -ForegroundColor Green
} else {
    Write-Host "  - No frontend processes found" -ForegroundColor Gray
}

# Verify ports are free
Write-Host ""
Write-Host "[3/3] Verifying ports are released..." -ForegroundColor Yellow

$port8000 = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue 2>$null
$port3000 = Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet -WarningAction SilentlyContinue 2>$null

if (-not $port8000) {
    Write-Host "  ✓ Port 8000 (Backend) is free" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Port 8000 still in use" -ForegroundColor Yellow
}

if (-not $port3000) {
    Write-Host "  ✓ Port 3000 (Frontend) is free" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Port 3000 still in use" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  SYSTEM STOPPED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start again, run: .\start-website.ps1" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close"
