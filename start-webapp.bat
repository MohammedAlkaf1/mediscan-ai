@echo off
REM Smart Medical Report Interpreter - Web Application Startup (Windows Batch)

echo ================================================
echo  Smart Medical Report Interpreter
echo  Starting Web Application...
echo ================================================
echo.

cd /d c:\xampp\htdocs\medical

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Starting Docker services...
docker-compose up -d

echo.
echo Waiting for services to initialize (30 seconds)...
timeout /t 30 /nobreak >nul

echo.
echo ================================================
echo  WEB APPLICATION IS READY!
echo ================================================
echo.
echo Access the web application at:
echo.
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Opening browser...
start http://localhost:3000

echo.
echo To stop the web application, run: docker-compose down
echo.
pause
