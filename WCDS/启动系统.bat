@echo off
chcp 65001 >nul
title 微信小程序 + RAG AI 系统启动器
echo.
echo ========================================
echo 🚀 微信小程序 + RAG AI 系统启动器
echo ========================================
echo 📅 当前时间: %date% %time%
echo 💻 系统: Windows
echo.

:: 设置颜色
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

:: 检查是否在正确的目录
if not exist "cloudfunctions" (
    echo %RED%❌ 错误：请在WCDS目录下运行此脚本%RESET%
    pause
    exit /b 1
)

:: 检查RAG AI目录
if not exist "..\rag_ai" (
    echo %RED%❌ 错误：未找到rag_ai目录，请确保目录结构正确%RESET%
    pause
    exit /b 1
)

echo %BLUE%📋 系统启动检查清单%RESET%
echo.

:: 1. 检查Python环境
echo %YELLOW%1. 检查Python环境...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%   ❌ Python未安装或未添加到PATH%RESET%
    echo %YELLOW%   请安装Python 3.8+并添加到系统PATH%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ Python环境正常%RESET%
)

:: 2. 检查Node.js环境
echo %YELLOW%2. 检查Node.js环境...%RESET%
node --version >nul 2>&1
if errorlevel 1 (
    echo %RED%   ❌ Node.js未安装或未添加到PATH%RESET%
    echo %YELLOW%   请安装Node.js 16+并添加到系统PATH%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ Node.js环境正常%RESET%
)

:: 3. 检查RAG AI后端依赖
echo %YELLOW%3. 检查RAG AI后端依赖...%RESET%
if exist "..\rag_ai\requirements.txt" (
    echo %GREEN%   ✅ 找到requirements.txt%RESET%
) else (
    echo %RED%   ❌ 未找到requirements.txt%RESET%
    pause
    exit /b 1
)

:: 4. 检查云函数依赖
echo %YELLOW%4. 检查云函数依赖...%RESET%
if exist "cloudfunctions\getQASystem\package.json" (
    echo %GREEN%   ✅ 找到云函数配置%RESET%
) else (
    echo %RED%   ❌ 未找到云函数配置%RESET%
    pause
    exit /b 1
)

echo.
echo %BLUE%🔧 开始启动系统...%RESET%
echo.

:: 5. 启动RAG AI后端
echo %YELLOW%5. 启动RAG AI后端服务...%RESET%
cd ..\rag_ai
start "RAG AI Backend" cmd /k "echo 启动RAG AI后端服务... && python start_backend.py"
cd ..\WCDS

:: 等待后端启动
echo %YELLOW%   等待后端服务启动（10秒）...%RESET%
timeout /t 10 /nobreak >nul

:: 6. 测试后端连接
echo %YELLOW%6. 测试后端连接...%RESET%
if exist "test_rag_connection.js" (
    node test_rag_connection.js
    if errorlevel 1 (
        echo %RED%   ❌ 后端连接测试失败%RESET%
        echo %YELLOW%   请检查RAG AI后端是否正常启动%RESET%
    ) else (
        echo %GREEN%   ✅ 后端连接测试通过%RESET%
    )
) else (
    echo %YELLOW%   ⚠️ 未找到连接测试脚本，跳过测试%RESET%
)

:: 7. 安装云函数依赖
echo %YELLOW%7. 检查云函数依赖...%RESET%
cd cloudfunctions\getQASystem
if not exist "node_modules" (
    echo %YELLOW%   安装云函数依赖...%RESET%
    npm install
    if errorlevel 1 (
        echo %RED%   ❌ 云函数依赖安装失败%RESET%
    ) else (
        echo %GREEN%   ✅ 云函数依赖安装成功%RESET%
    )
) else (
    echo %GREEN%   ✅ 云函数依赖已存在%RESET%
)
cd ..\..

echo.
echo %GREEN%🎉 系统启动完成！%RESET%
echo.
echo %BLUE%📱 接下来的步骤：%RESET%
echo %YELLOW%1. 打开微信开发者工具%RESET%
echo %YELLOW%2. 导入当前项目目录（WCDS）%RESET%
echo %YELLOW%3. 右键点击 cloudfunctions/getQASystem%RESET%
echo %YELLOW%4. 选择"上传并部署：云端安装依赖"%RESET%
echo %YELLOW%5. 等待部署完成后测试AI助手功能%RESET%
echo.
echo %BLUE%🔗 有用的链接：%RESET%
echo %YELLOW%- RAG AI后端: http://localhost:8000%RESET%
echo %YELLOW%- 健康检查: http://localhost:8000/health%RESET%
echo %YELLOW%- 微信健康检查: http://localhost:8000/wechat/health%RESET%
echo.
echo %BLUE%📚 文档：%RESET%
echo %YELLOW%- 使用说明: 微信小程序接入RAG_AI使用说明.md%RESET%
echo %YELLOW%- 部署清单: 部署检查清单.md%RESET%
echo.

:: 询问是否打开浏览器测试
set /p "open_browser=是否打开浏览器测试后端服务？(y/n): "
if /i "%open_browser%"=="y" (
    start http://localhost:8000/health
)

echo.
echo %GREEN%✨ 祝您使用愉快！%RESET%
echo.
pause
