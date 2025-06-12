@echo off
chcp 65001 >nul
title 系统状态检查
echo.
echo ========================================
echo 🔍 微信小程序 + RAG AI 系统状态检查
echo ========================================
echo.

:: 设置颜色
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

echo %BLUE%📊 正在检查系统状态...%RESET%
echo.

:: 1. 检查RAG AI后端服务
echo %YELLOW%1. 检查RAG AI后端服务 (http://localhost:8000)%RESET%
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo %RED%   ❌ RAG AI后端服务未运行%RESET%
    echo %YELLOW%   请先启动RAG AI后端服务%RESET%
    set "backend_status=offline"
) else (
    echo %GREEN%   ✅ RAG AI后端服务正常运行%RESET%
    set "backend_status=online"
)

:: 2. 检查微信专用接口
echo %YELLOW%2. 检查微信专用接口 (http://localhost:8000/wechat/health)%RESET%
curl -s http://localhost:8000/wechat/health >nul 2>&1
if errorlevel 1 (
    echo %RED%   ❌ 微信专用接口不可用%RESET%
    set "wechat_api_status=offline"
) else (
    echo %GREEN%   ✅ 微信专用接口正常%RESET%
    set "wechat_api_status=online"
)

:: 3. 检查云函数配置
echo %YELLOW%3. 检查云函数配置%RESET%
if exist "cloudfunctions\getQASystem\index.js" (
    echo %GREEN%   ✅ 云函数代码存在%RESET%
) else (
    echo %RED%   ❌ 云函数代码缺失%RESET%
)

if exist "cloudfunctions\getQASystem\node_modules" (
    echo %GREEN%   ✅ 云函数依赖已安装%RESET%
) else (
    echo %YELLOW%   ⚠️ 云函数依赖未安装%RESET%
    echo %YELLOW%   请运行: cd cloudfunctions\getQASystem && npm install%RESET%
)

:: 4. 检查小程序页面文件
echo %YELLOW%4. 检查小程序页面文件%RESET%
set "missing_files="

if not exist "pages\chatBot\chatBot.js" (
    set "missing_files=%missing_files% chatBot.js"
)
if not exist "pages\chatBot\chatBot.wxml" (
    set "missing_files=%missing_files% chatBot.wxml"
)
if not exist "pages\chatBot\chatBot.wxss" (
    set "missing_files=%missing_files% chatBot.wxss"
)
if not exist "pages\chatBot\chatBot.json" (
    set "missing_files=%missing_files% chatBot.json"
)

if "%missing_files%"=="" (
    echo %GREEN%   ✅ 所有页面文件完整%RESET%
) else (
    echo %RED%   ❌ 缺少文件:%missing_files%%RESET%
)

:: 5. 检查配置文件
echo %YELLOW%5. 检查配置文件%RESET%
if exist "app.json" (
    findstr /C:"chatBot" app.json >nul
    if errorlevel 1 (
        echo %YELLOW%   ⚠️ app.json中可能缺少chatBot页面配置%RESET%
    ) else (
        echo %GREEN%   ✅ app.json配置正常%RESET%
    )
) else (
    echo %RED%   ❌ app.json文件缺失%RESET%
)

:: 6. 运行连接测试
echo %YELLOW%6. 运行连接测试%RESET%
if exist "test_rag_connection.js" (
    if "%backend_status%"=="online" (
        echo %YELLOW%   正在运行连接测试...%RESET%
        node test_rag_connection.js >nul 2>&1
        if errorlevel 1 (
            echo %RED%   ❌ 连接测试失败%RESET%
        ) else (
            echo %GREEN%   ✅ 连接测试通过%RESET%
        )
    ) else (
        echo %YELLOW%   ⚠️ 后端服务未运行，跳过连接测试%RESET%
    )
) else (
    echo %YELLOW%   ⚠️ 连接测试脚本不存在%RESET%
)

echo.
echo %BLUE%📋 系统状态汇总:%RESET%
echo ================================

if "%backend_status%"=="online" (
    echo %GREEN%✅ RAG AI后端: 运行中%RESET%
) else (
    echo %RED%❌ RAG AI后端: 离线%RESET%
)

if "%wechat_api_status%"=="online" (
    echo %GREEN%✅ 微信API: 正常%RESET%
) else (
    echo %RED%❌ 微信API: 不可用%RESET%
)

if exist "cloudfunctions\getQASystem\node_modules" (
    echo %GREEN%✅ 云函数依赖: 已安装%RESET%
) else (
    echo %YELLOW%⚠️ 云函数依赖: 未安装%RESET%
)

if "%missing_files%"=="" (
    echo %GREEN%✅ 页面文件: 完整%RESET%
) else (
    echo %RED%❌ 页面文件: 不完整%RESET%
)

echo.
if "%backend_status%"=="online" and "%wechat_api_status%"=="online" and "%missing_files%"=="" (
    echo %GREEN%🎉 系统状态良好，可以正常使用！%RESET%
) else (
    echo %YELLOW%⚠️ 系统存在问题，请根据上述检查结果进行修复。%RESET%
)

echo.
echo %BLUE%🔗 快速链接:%RESET%
echo - RAG AI后端: http://localhost:8000
echo - 健康检查: http://localhost:8000/health
echo - 微信健康检查: http://localhost:8000/wechat/health
echo.

set /p "open_health=是否打开健康检查页面？(y/n): "
if /i "%open_health%"=="y" (
    start http://localhost:8000/health
)

echo.
pause
