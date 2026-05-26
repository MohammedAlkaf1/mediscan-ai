# Smart Medical Report Interpreter - Web Application Startup
# This runs the application as a web service

Write-Host "Starting Smart Medical Report Interpreter Web Application..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
$dockerRunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerRunning) {
    Write-Host "ERROR: Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Navigate to project directory
Set-Location "c:\xampp\htdocs\medical"

Write-Host "Step 1: Checking PostgreSQL..." -ForegroundColor Cyan
$pgService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq "Running") {
    Write-Host "  ✓ PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "  ⚠ PostgreSQL is not running. Starting Docker services..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Starting Docker services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "Step 3: Waiting for services to initialize (30 seconds)..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Step 4: Checking service status..." -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  WEB APPLICATION IS READY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the web application at:" -ForegroundColor White
Write-Host ""
Write-Host "  Frontend (Main App): " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Yellow
Write-Host "  Backend API:         " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Yellow
Write-Host "  API Documentation:   " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host "  1. Open your web browser" -ForegroundColor White
Write-Host "  2. Go to http://localhost:3000" -ForegroundColor White
Write-Host "  3. Click 'Try Demo Report' for instant results" -ForegroundColor White
Write-Host "  4. Or upload your lab report (JPG/PNG/PDF)" -ForegroundColor White
Write-Host ""
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Gray
Write-Host "To stop: docker-compose down" -ForegroundColor Gray
Write-Host ""

# Open browser automatically
Write-Host "Opening web browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Press Ctrl+C to view logs or close this window to keep services running in background" -ForegroundColor Yellow
Write-Host ""

# Follow logs
docker-compose logs -f
