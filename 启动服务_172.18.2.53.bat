@echo off
chcp 65001 >nul
title RAG AI服务启动 - IP: 172.18.2.53

echo.
echo ========================================
echo 🚀 RAG AI服务启动脚本
echo 📍 IP地址: 172.18.2.53
echo ========================================
echo.

:: 设置颜色
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

:: 检查Python环境
echo %BLUE%1. 检查Python环境%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%   ❌ Python未安装或未添加到PATH%RESET%
    echo %YELLOW%   请安装Python 3.8+%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ Python环境正常%RESET%
)

:: 检查项目目录
echo %BLUE%2. 检查项目目录%RESET%
if not exist "rag_ai\backend\.env" (
    echo %RED%   ❌ 未找到后端配置文件%RESET%
    echo %YELLOW%   请确保在正确的项目目录下运行此脚本%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ 项目目录正确%RESET%
)

:: 验证IP配置
echo %BLUE%3. 验证IP配置%RESET%
findstr "172.18.2.53" rag_ai\backend\.env >nul
if errorlevel 1 (
    echo %RED%   ❌ IP配置未更新%RESET%
    echo %YELLOW%   请运行IP配置更新脚本%RESET%
    pause
    exit /b 1
) else (
    echo %GREEN%   ✅ IP配置已更新为 172.18.2.53%RESET%
)

:: 检查网络连接
echo %BLUE%4. 检查网络连接%RESET%
ping -n 1 172.18.2.53 >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%   ⚠️  无法ping通 172.18.2.53%RESET%
    echo %YELLOW%   这可能是正常的，继续启动服务...%RESET%
) else (
    echo %GREEN%   ✅ 网络连接正常%RESET%
)

echo.
echo %BLUE%5. 启动RAG AI后端服务%RESET%
echo %YELLOW%   服务地址: http://172.18.2.53:8000%RESET%
echo %YELLOW%   按 Ctrl+C 停止服务%RESET%
echo.

:: 切换到项目目录并启动服务
cd /d "%~dp0"
python rag_ai\start_backend.py

echo.
echo %YELLOW%服务已停止%RESET%
pause
