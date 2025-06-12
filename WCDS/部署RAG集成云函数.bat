@echo off
chcp 65001 >nul
title 部署RAG集成云函数
echo.
echo ========================================
echo 🚀 部署微信小程序RAG AI集成云函数
echo ========================================
echo.

:: 设置颜色
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

echo %BLUE%📋 开始部署流程...%RESET%
echo.

:: 1. 检查RAG AI后端服务
echo %YELLOW%1. 检查RAG AI后端服务状态...%RESET%
curl -s http://localhost:8000/wechat/health >nul 2>&1
if errorlevel 1 (
    echo %RED%   ❌ RAG AI后端服务未运行%RESET%
    echo %YELLOW%   请先启动RAG AI后端服务：%RESET%
    echo %YELLOW%   cd rag_ai%RESET%
    echo %YELLOW%   python start_backend.py%RESET%
    echo.
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ RAG AI后端服务正常运行%RESET%
)

:: 2. 检查云函数目录
echo %YELLOW%2. 检查云函数目录...%RESET%
if not exist "cloudfunctions\getQASystem" (
    echo %RED%   ❌ 云函数目录不存在%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ 云函数目录存在%RESET%
)

:: 3. 检查package.json
echo %YELLOW%3. 检查package.json配置...%RESET%
findstr /C:"axios" "cloudfunctions\getQASystem\package.json" >nul 2>&1
if errorlevel 1 (
    echo %RED%   ❌ package.json缺少axios依赖%RESET%
    echo %YELLOW%   请确认package.json已更新%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ package.json配置正确%RESET%
)

:: 4. 安装依赖
echo %YELLOW%4. 安装云函数依赖...%RESET%
cd cloudfunctions\getQASystem
if exist "node_modules" (
    echo %YELLOW%   清理旧的依赖...%RESET%
    rmdir /s /q node_modules 2>nul
)

echo %YELLOW%   正在安装依赖...%RESET%
npm install
if errorlevel 1 (
    echo %RED%   ❌ 依赖安装失败%RESET%
    cd ..\..
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ 依赖安装成功%RESET%
)

cd ..\..

:: 5. 验证安装
echo %YELLOW%5. 验证安装结果...%RESET%
if exist "cloudfunctions\getQASystem\node_modules\axios" (
    echo %GREEN%   ✅ axios依赖安装成功%RESET%
) else (
    echo %RED%   ❌ axios依赖安装失败%RESET%
    pause
    exit /b 1
)

:: 6. 测试云函数代码
echo %YELLOW%6. 检查云函数代码...%RESET%
findstr /C:"RAG AI集成版本" "cloudfunctions\getQASystem\index.js" >nul 2>&1
if errorlevel 1 (
    echo %RED%   ❌ 云函数代码未更新%RESET%
    echo %YELLOW%   请确认index.js已更新为RAG集成版本%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ 云函数代码已更新%RESET%
)

echo.
echo %GREEN%========================================%RESET%
echo %GREEN%🎉 云函数准备完成！%RESET%
echo %GREEN%========================================%RESET%
echo.
echo %BLUE%📋 接下来的步骤：%RESET%
echo.
echo %YELLOW%1. 在微信开发者工具中：%RESET%
echo    - 右键点击 getQASystem 云函数
echo    - 选择"上传并部署：云端安装依赖"
echo    - 等待部署完成
echo.
echo %YELLOW%2. 测试功能：%RESET%
echo    - 打开小程序AI对话页面
echo    - 输入问题测试智能回答
echo    - 例如："推荐一些北京的必去景点"
echo.
echo %YELLOW%3. 查看部署指南：%RESET%
echo    - 阅读 "云函数RAG集成部署指南.md"
echo    - 了解详细配置和故障排除
echo.
echo %GREEN%✨ 部署完成后，您的AI助手将提供真正的智能回答！%RESET%
echo.
pause
