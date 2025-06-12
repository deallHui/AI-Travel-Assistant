@echo off
echo RAG AI Simple Deploy Script
echo =============================

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker not found
    echo Please install Docker Desktop
    pause
    exit /b 1
)

echo Docker found, starting deployment...

:: Create directories
if not exist "..\vectorstores" mkdir "..\vectorstores"
if not exist "logs" mkdir "logs"

:: Start the service
echo Starting RAG API service...
docker compose up -d rag-api

:: Wait for startup
echo Waiting for service to start...
timeout /t 15 >nul

:: Check status
echo Checking service status...
docker compose ps

:: Health check
echo Testing API health...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: API is running at http://localhost:8000
    echo API Documentation: http://localhost:8000/docs
    echo.
    echo Next steps:
    echo 1. Install ngrok: https://ngrok.com/download
    echo 2. Run: ngrok http 8000
    echo 3. Share the ngrok URL with users
) else (
    echo ERROR: API health check failed
    echo Check logs with: docker compose logs rag-api
)

echo.
echo Press any key to exit...
pause >nul
