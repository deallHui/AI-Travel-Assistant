@echo off
chcp 65001 >nul
title 验证微信小程序配置
echo.
echo ========================================
echo 🔍 验证微信小程序配置
echo ========================================
echo.

:: 设置颜色
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

echo %BLUE%📋 检查配置文件...%RESET%
echo.

:: 1. 检查app.json配置
echo %YELLOW%1. 检查app.json配置%RESET%
if exist "app.json" (
    echo %GREEN%   ✅ app.json文件存在%RESET%
    
    :: 检查是否包含chatBot页面
    findstr /C:"pages/chatBot/chatBot" app.json >nul
    if errorlevel 1 (
        echo %RED%   ❌ app.json中缺少chatBot页面配置%RESET%
    ) else (
        echo %GREEN%   ✅ chatBot页面已配置%RESET%
    )
    
    :: 检查tabBar配置
    findstr /C:"AI助手" app.json >nul
    if errorlevel 1 (
        echo %RED%   ❌ tabBar中缺少AI助手配置%RESET%
    ) else (
        echo %GREEN%   ✅ AI助手已添加到tabBar%RESET%
    )
) else (
    echo %RED%   ❌ app.json文件不存在%RESET%
)

:: 2. 检查chatBot页面文件
echo %YELLOW%2. 检查chatBot页面文件%RESET%
set "missing_files="

if not exist "pages\chatBot\chatBot.js" (
    echo %RED%   ❌ 缺少 chatBot.js%RESET%
    set "missing_files=1"
) else (
    echo %GREEN%   ✅ chatBot.js 存在%RESET%
)

if not exist "pages\chatBot\chatBot.wxml" (
    echo %RED%   ❌ 缺少 chatBot.wxml%RESET%
    set "missing_files=1"
) else (
    echo %GREEN%   ✅ chatBot.wxml 存在%RESET%
)

if not exist "pages\chatBot\chatBot.wxss" (
    echo %RED%   ❌ 缺少 chatBot.wxss%RESET%
    set "missing_files=1"
) else (
    echo %GREEN%   ✅ chatBot.wxss 存在%RESET%
)

if not exist "pages\chatBot\chatBot.json" (
    echo %RED%   ❌ 缺少 chatBot.json%RESET%
    set "missing_files=1"
) else (
    echo %GREEN%   ✅ chatBot.json 存在%RESET%
)

:: 3. 检查云函数配置
echo %YELLOW%3. 检查云函数配置%RESET%
if exist "cloudfunctions\getQASystem\index.js" (
    echo %GREEN%   ✅ 云函数代码存在%RESET%
    
    :: 检查是否包含axios依赖
    findstr /C:"axios" cloudfunctions\getQASystem\package.json >nul
    if errorlevel 1 (
        echo %RED%   ❌ package.json中缺少axios依赖%RESET%
    ) else (
        echo %GREEN%   ✅ axios依赖已配置%RESET%
    )
) else (
    echo %RED%   ❌ 云函数代码不存在%RESET%
)

:: 4. 检查首页AI助手入口
echo %YELLOW%4. 检查首页AI助手入口%RESET%
if exist "pages\index\index.wxml" (
    findstr /C:"goToAIAssistant" pages\index\index.wxml >nul
    if errorlevel 1 (
        echo %YELLOW%   ⚠️ 首页缺少AI助手入口按钮%RESET%
    ) else (
        echo %GREEN%   ✅ 首页AI助手入口已添加%RESET%
    )
) else (
    echo %RED%   ❌ 首页文件不存在%RESET%
)

:: 5. 检查配置文件
echo %YELLOW%5. 检查配置文件%RESET%
if exist "config\api.js" (
    echo %GREEN%   ✅ API配置文件存在%RESET%
) else (
    echo %YELLOW%   ⚠️ API配置文件不存在（可选）%RESET%
)

echo.
echo %BLUE%📊 配置验证结果:%RESET%
echo ================================

if "%missing_files%"=="" (
    echo %GREEN%✅ 所有必需文件都存在%RESET%
) else (
    echo %RED%❌ 部分文件缺失，请检查上述错误%RESET%
)

echo.
echo %BLUE%📱 下一步操作:%RESET%
echo 1. 在微信开发者工具中打开项目
echo 2. 检查底部导航栏是否显示"AI助手"
echo 3. 点击"AI助手"测试页面是否正常
echo 4. 部署云函数: 右键getQASystem → 上传并部署
echo 5. 测试AI对话功能
echo.

echo %YELLOW%💡 如果底部导航栏没有显示AI助手，请尝试：%RESET%
echo - 在微信开发者工具中重新编译项目
echo - 检查app.json文件格式是否正确
echo - 确保tabBar配置没有语法错误
echo.

pause
