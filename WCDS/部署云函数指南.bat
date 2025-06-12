@echo off
chcp 65001 >nul
title 微信小程序云函数部署指南
echo.
echo ========================================
echo 🚀 微信小程序云函数部署指南
echo ========================================
echo.

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

echo %GREEN%✅ cpolar地址已更新：http://47c24b5e.r38.cpolar.top%RESET%
echo %GREEN%✅ 超时配置已优化：开发环境25秒，生产环境45秒%RESET%
echo %GREEN%✅ 环境模式已切换：development（真正的RAG AI后端）%RESET%
echo.

echo %BLUE%📋 部署步骤：%RESET%
echo %YELLOW%1. 打开微信开发者工具%RESET%
echo %YELLOW%2. 打开WCDS项目%RESET%
echo %YELLOW%3. 点击"云开发"按钮%RESET%
echo %YELLOW%4. 进入"云函数"页面%RESET%
echo %YELLOW%5. 右键点击"getQASystem"文件夹%RESET%
echo %YELLOW%6. 选择"上传并部署：云端安装依赖"（推荐）%RESET%
echo %YELLOW%7. 等待部署完成（约1-2分钟）%RESET%
echo.

echo %BLUE%⚙️ 重要配置检查：%RESET%
echo %GREEN%• 云函数超时时间：30秒（在云开发控制台设置）%RESET%
echo %GREEN%• 内存配置：256MB或512MB（推荐512MB）%RESET%
echo %GREEN%• 环境变量：无需额外配置%RESET%
echo.

echo %BLUE%🔧 云函数超时设置：%RESET%
echo %YELLOW%1. 在云开发控制台中%RESET%
echo %YELLOW%2. 点击"getQASystem"函数名%RESET%
echo %YELLOW%3. 进入"配置"选项卡%RESET%
echo %YELLOW%4. 将"超时时间"设置为30秒%RESET%
echo %YELLOW%5. 将"内存"设置为512MB%RESET%
echo %YELLOW%6. 点击"保存"按钮%RESET%
echo.

echo %BLUE%🧪 测试方法：%RESET%
echo %GREEN%1. 在小程序中问："北京有什么好玩的景点？"%RESET%
echo %GREEN%2. 观察是否返回详细的景点信息%RESET%
echo %GREEN%3. 问一个知识库中没有的问题，如："2024年最新旅游政策"%RESET%
echo %GREEN%4. 检查是否会自动进行网络搜索并返回AI补充信息%RESET%
echo.

echo %BLUE%🔄 完整工作链测试：%RESET%
echo %GREEN%知识库有答案 → 直接返回（5-8秒）%RESET%
echo %GREEN%知识库无答案 → 自动网络搜索 → 返回AI补充（15-25秒）%RESET%
echo.

echo %BLUE%📊 预期结果：%RESET%
echo %GREEN%• 知识库回答：包含"📚 知识库搜索"部分%RESET%
echo %GREEN%• 网络搜索回答：包含"🤖 AI智能补充"部分%RESET%
echo %GREEN%• 回答格式：Markdown格式，结构化显示%RESET%
echo %GREEN%• 响应时间：知识库5-8秒，网络搜索15-25秒%RESET%
echo.

echo %RED%🚨 故障排除：%RESET%
echo %YELLOW%如果出现超时错误：%RESET%
echo %GREEN%• 检查cpolar地址是否正确%RESET%
echo %GREEN%• 确认云函数超时设置为30秒%RESET%
echo %GREEN%• 检查Docker服务是否正常运行%RESET%
echo %GREEN%• 查看云函数日志获取详细错误信息%RESET%
echo.

echo %YELLOW%如果返回测试模式回答：%RESET%
echo %GREEN%• 确认currentEnv设置为'development'%RESET%
echo %GREEN%• 重新部署云函数%RESET%
echo %GREEN%• 检查网络连接%RESET%
echo.

echo %BLUE%📱 小程序端配置：%RESET%
echo %GREEN%• 网络超时：30秒（已自动设置）%RESET%
echo %GREEN%• 请求域名：已配置cpolar域名白名单%RESET%
echo %GREEN%• 云函数调用：无需额外配置%RESET%
echo.

echo %GREEN%🎯 部署完成后，您的小程序将具备：%RESET%
echo %GREEN%✅ 智能旅游问答（基于24个攻略文档）%RESET%
echo %GREEN%✅ 自动网络搜索补充%RESET%
echo %GREEN%✅ 完整的工作链流程%RESET%
echo %GREEN%✅ 智能降级机制%RESET%
echo %GREEN%✅ 30秒超时保护%RESET%
echo.

pause
echo.
echo %GREEN%✅ 请按照上述步骤部署云函数，然后测试小程序功能！%RESET%
echo.
pause
