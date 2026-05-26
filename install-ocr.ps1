# Fix for "No meaningful text extracted from file" error
# This script installs missing OCR dependencies

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Installing Missing OCR Dependencies" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "IMPORTANT: Please stop the backend server first!" -ForegroundColor Yellow
Write-Host "Press Ctrl+C in the backend terminal, then run this script." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to continue or Ctrl+C to cancel..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Step 1: Installing PaddleOCR..." -ForegroundColor Green
py -m pip install paddleocr --upgrade

Write-Host ""
Write-Host "Step 2: Installing PaddlePaddle..." -ForegroundColor Green
py -m pip install paddlepaddle --upgrade

Write-Host ""
Write-Host "Step 3: Verifying installation..." -ForegroundColor Green
py -c "from paddleocr import PaddleOCR; print('✅ PaddleOCR installed successfully!')"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "✅ Installation Complete!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now you can:" -ForegroundColor Cyan
    Write-Host "1. Restart the backend server" -ForegroundColor White
    Write-Host "2. Try uploading a file again" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Red
    Write-Host "❌ Installation Failed" -ForegroundColor Red
    Write-Host "==================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try these steps:" -ForegroundColor Yellow
    Write-Host "1. Close ALL Python/backend processes" -ForegroundColor White
    Write-Host "2. Restart your computer" -ForegroundColor White
    Write-Host "3. Run this script again" -ForegroundColor White
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
