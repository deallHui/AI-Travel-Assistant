@echo off
echo RAG AI Docker Deploy Script

:: Check Docker installation
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker not installed
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: Check Docker Compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose not available
    pause
    exit /b 1
)

echo SUCCESS: Docker environment check passed

:: Set environment variables
set /p DEEPSEEK_API_KEY="Enter DeepSeek API Key (optional, press Enter to skip): "
if not "%DEEPSEEK_API_KEY%"=="" (
    echo DEEPSEEK_API_KEY=%DEEPSEEK_API_KEY% > .env
    echo SUCCESS: API key configured
) else (
    echo WARNING: No API key set, AI search will be disabled
)

:: Check vectorstore directory
if not exist "..\vectorstores" (
    echo WARNING: Vectorstore directory not found, creating...
    mkdir "..\vectorstores"
)

:: Create logs directory
if not exist "logs" mkdir logs

echo.
echo Deploy Options:
echo 1. Start API service only (port 8000)
echo 2. Start API + Nginx (port 80)
echo 3. Rebuild and start
echo 4. Stop services
echo 5. View logs
echo 6. Check status

set /p choice="Please choose (1-6): "

if "%choice%"=="1" goto start_api
if "%choice%"=="2" goto start_all
if "%choice%"=="3" goto rebuild
if "%choice%"=="4" goto stop
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto status
goto invalid

:start_api
echo Starting API service...
docker compose up -d rag-api
goto check_status

:start_all
echo Starting full services...
docker compose up -d
goto check_status

:rebuild
echo Rebuilding and starting...
docker compose down
docker compose build --no-cache
docker compose up -d
goto check_status

:stop
echo Stopping services...
docker compose down
echo SUCCESS: Services stopped
goto end

:logs
echo Viewing logs...
docker compose logs -f rag-api
goto end

:status
echo Service Status:
docker compose ps
echo.
echo Health Check:
timeout /t 3 >nul
curl -s http://localhost:8000/health 2>nul || echo ERROR: API service unavailable
goto end

:check_status
echo.
echo Waiting for service to start...
timeout /t 10 >nul

echo Service Status:
docker compose ps

echo.
echo Health Check:
curl -s http://localhost:8000/health 2>nul && (
    echo SUCCESS: API service is running
    echo API URL: http://localhost:8000
    echo API Docs: http://localhost:8000/docs
) || (
    echo ERROR: API service failed to start, check logs
    echo View logs: docker compose logs rag-api
)

echo.
echo Tunnel Options:
echo 1. Use ngrok: ngrok http 8000
echo 2. Use frp: Configure frp client
echo 3. Use cpolar: cpolar http 8000
goto end

:invalid
echo ERROR: Invalid choice
goto end

:end
echo.
echo Common Commands:
echo   Start: docker compose up -d
echo   Stop: docker compose down
echo   Logs: docker compose logs -f rag-api
echo   Restart: docker compose restart rag-api
echo   Status: docker compose ps
echo.
pause
