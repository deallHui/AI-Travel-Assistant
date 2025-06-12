@echo off
echo WeChat MiniProgram RAG AI Integration Deploy Script
echo ====================================================

echo.
echo Current Configuration:
echo    - RAG API URL: https://47c24b5e.r38.cpolar.top
echo    - WeChat MiniProgram: WCDS
echo    - Cloud Function: getQASystem
echo.

echo Step 1: Check RAG API Service Status...
curl -s https://47c24b5e.r38.cpolar.top/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] RAG API Service is running
) else (
    echo [ERROR] RAG API Service connection failed
    echo Please ensure:
    echo    1. Docker container is running
    echo    2. cpolar tunnel is active
    echo    3. URL address is correct
    pause
    exit /b 1
)

echo.
echo Step 2: Deploy Cloud Function...
echo Deploying getQASystem cloud function...

cd cloudfunctions\getQASystem
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] npm install failed
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully

echo.
echo 📱 步骤3: 微信开发者工具操作指南
echo =====================================
echo.
echo 请在微信开发者工具中执行以下操作:
echo.
echo 1️⃣ 打开项目: 选择WCDS文件夹
echo.
echo 2️⃣ 配置域名白名单:
echo    - 进入: 详情 → 本地设置
echo    - 勾选: "不校验合法域名、web-view、TLS版本..."
echo    - 或在小程序后台配置: 47c24b5e.r38.cpolar.top
echo.
echo 3️⃣ 部署云函数:
echo    - 右键点击 cloudfunctions/getQASystem
echo    - 选择 "上传并部署: 云端安装依赖"
echo    - 等待部署完成
echo.
echo 4️⃣ 测试功能:
echo    - 进入 "智能助手" 页面
echo    - 发送测试消息: "推荐一些北京的景点"
echo    - 检查是否正常回复
echo.
echo 5️⃣ 预览/发布:
echo    - 点击 "预览" 生成二维码
echo    - 用微信扫码测试
echo    - 确认无误后点击 "上传" 发布
echo.

echo 🎯 测试API连接...
echo 正在测试RAG API连接...

curl -X POST "https://47c24b5e.r38.cpolar.top/wechat/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"openid\":\"test_user\",\"question\":\"你好\",\"location\":null}" ^
  --connect-timeout 10 --max-time 30 >test_result.json 2>nul

if %errorlevel% equ 0 (
    echo ✅ API连接测试成功
    echo 📄 测试结果已保存到 test_result.json
) else (
    echo ⚠️  API连接测试失败，但不影响部署
    echo 可能原因: 网络延迟或服务正在启动
)

echo.
echo 🎉 部署准备完成！
echo =====================================
echo.
echo 📞 如遇问题，请检查:
echo    1. cpolar隧道是否正常运行
echo    2. Docker容器是否健康
echo    3. 微信开发者工具是否已登录
echo    4. 云函数是否部署成功
echo.
echo 💡 快速测试命令:
echo    curl https://47c24b5e.r38.cpolar.top/health
echo.

cd ..\..
pause
