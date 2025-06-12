@echo off
chcp 65001 >nul
title 设置微信小程序云函数超时时间
echo.
echo ========================================
echo 🔧 设置微信小程序云函数超时时间
echo ========================================
echo.

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

echo %RED%⚠️  当前问题：云函数3秒超时导致工作链不完整%RESET%
echo %GREEN%✅ 解决方案：将超时时间设置为20-30秒%RESET%
echo.

echo %BLUE%📋 手动设置步骤（推荐）：%RESET%
echo %YELLOW%1. 打开微信开发者工具%RESET%
echo %YELLOW%2. 点击顶部"云开发"按钮%RESET%
echo %YELLOW%3. 进入"云函数"页面%RESET%
echo %YELLOW%4. 点击"getQASystem"函数名%RESET%
echo %YELLOW%5. 点击"配置"选项卡%RESET%
echo %YELLOW%6. 将"超时时间"改为 30秒%RESET%
echo %YELLOW%7. 点击"保存"按钮%RESET%
echo %YELLOW%8. 重新上传部署云函数%RESET%
echo.

echo %BLUE%🔄 工作链流程：%RESET%
echo %GREEN%1. RAG知识库查询 (5-8秒)%RESET%
echo %GREEN%2. 判断回答是否充分 (1秒)%RESET%
echo %GREEN%3. 如果不充分 → DeepSeek网络搜索 (10-15秒)%RESET%
echo %GREEN%4. 合并回答并返回 (1-2秒)%RESET%
echo %YELLOW%总计需要：15-25秒%RESET%
echo.

echo %BLUE%📊 超时设置建议：%RESET%
echo %GREEN%• 开发环境：30秒 (留有余量)%RESET%
echo %GREEN%• 生产环境：45秒 (更稳定)%RESET%
echo %GREEN%• 小程序端：30秒 (已自动设置)%RESET%
echo.

echo %BLUE%🎯 优化后的效果：%RESET%
echo %GREEN%✅ 知识库有答案 → 直接返回 (快速)%RESET%
echo %GREEN%✅ 知识库无答案 → 自动网络搜索 (完整)%RESET%
echo %GREEN%✅ 网络搜索失败 → 降级模式 (稳定)%RESET%
echo.

echo %YELLOW%⚡ 已自动优化的配置：%RESET%
echo %GREEN%• 小程序网络超时：10秒 → 30秒%RESET%
echo %GREEN%• 云函数开发超时：15秒 → 25秒%RESET%
echo %GREEN%• 云函数生产超时：30秒 → 45秒%RESET%
echo %GREEN%• cpolar地址已更新为当前活跃地址%RESET%
echo.

echo %RED%🚨 重要提醒：%RESET%
echo %YELLOW%设置完成后，请重新部署云函数才能生效！%RESET%
echo.

echo %BLUE%📱 测试方法：%RESET%
echo %GREEN%1. 问一个知识库中没有的问题%RESET%
echo %GREEN%2. 观察是否会自动进行网络搜索%RESET%
echo %GREEN%3. 检查回答中是否包含"AI智能补充"部分%RESET%
echo.

pause
echo.
echo %GREEN%✅ 配置完成！请按照上述步骤在微信开发者工具中设置超时时间。%RESET%
echo.
pause
