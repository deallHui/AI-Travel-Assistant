@echo off
echo WeChat MiniProgram RAG AI Integration Deploy
echo ============================================

echo.
echo Configuration:
echo - RAG API: https://47c24b5e.r38.cpolar.top
echo - Project: WCDS
echo - Cloud Function: getQASystem
echo.

echo Step 1: Test RAG API Connection...
curl -s https://47c24b5e.r38.cpolar.top/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] RAG API is accessible
) else (
    echo [WARNING] RAG API connection failed
    echo Please check:
    echo 1. Docker container status
    echo 2. cpolar tunnel status
    echo 3. Network connection
    echo.
    echo Continue anyway? Press any key...
    pause >nul
)

echo.
echo Step 2: Install Cloud Function Dependencies...
if exist "cloudfunctions\getQASystem" (
    cd cloudfunctions\getQASystem
    echo Installing npm packages...
    call npm install --silent
    if %errorlevel% equ 0 (
        echo [OK] Dependencies installed
    ) else (
        echo [ERROR] npm install failed
        cd ..\..
        pause
        exit /b 1
    )
    cd ..\..
) else (
    echo [ERROR] Cloud function directory not found
    pause
    exit /b 1
)

echo.
echo Step 3: Test API Integration...
echo Testing WeChat API endpoint...
curl -X POST "https://47c24b5e.r38.cpolar.top/wechat/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"openid\":\"test_user\",\"question\":\"Hello\",\"location\":null}" ^
  --connect-timeout 10 --max-time 30 >test_result.json 2>nul

if %errorlevel% equ 0 (
    echo [OK] API test successful
    echo Test result saved to test_result.json
) else (
    echo [WARNING] API test failed - may be due to network delay
)

echo.
echo Step 4: WeChat Developer Tools Instructions
echo ============================================
echo.
echo Please follow these steps in WeChat Developer Tools:
echo.
echo 1. Open Project:
echo    - File ^> Open ^> Select WCDS folder
echo.
echo 2. Configure Domain Whitelist:
echo    - Details ^> Local Settings
echo    - Check "Do not verify legal domains..."
echo    - OR configure in MP backend: 47c24b5e.r38.cpolar.top
echo.
echo 3. Deploy Cloud Function:
echo    - Right-click cloudfunctions/getQASystem
echo    - Select "Upload and Deploy: Install dependencies"
echo    - Wait for deployment completion
echo.
echo 4. Test Integration:
echo    - Go to "AI Assistant" page
echo    - Send test message: "Recommend Beijing attractions"
echo    - Check if response is normal
echo.
echo 5. Preview/Publish:
echo    - Click "Preview" to generate QR code
echo    - Scan with WeChat to test
echo    - Click "Upload" to publish when ready
echo.

echo Deployment preparation completed!
echo.
echo Quick test commands:
echo   curl https://47c24b5e.r38.cpolar.top/health
echo   curl https://47c24b5e.r38.cpolar.top/docs
echo.

pause
