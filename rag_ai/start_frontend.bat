@echo off
echo === RAG应用前端启动脚本 ===

cd /d "%~dp0"

echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo 检查npm环境...
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到npm，请检查Node.js安装
    pause
    exit /b 1
)

echo 进入前端目录...
cd frontend

echo 检查依赖是否已安装...
if not exist "node_modules" (
    echo 安装前端依赖...
    npm install
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo 启动前端开发服务器...
echo 前端地址: http://localhost:3000
echo 后端API: http://localhost:8000
echo.
echo 请确保后端服务已启动！
echo.

npm run dev

pause
