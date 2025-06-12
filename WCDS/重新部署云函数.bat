@echo off
chcp 65001 >nul
title 重新部署微信小程序云函数
echo.
echo ========================================
echo 🔄 重新部署微信小程序云函数
echo ========================================
echo.

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

echo %BLUE%📋 部署步骤说明：%RESET%
echo.
echo %YELLOW%1. 打开微信开发者工具%RESET%
echo %YELLOW%2. 确保项目已导入（WCDS目录）%RESET%
echo %YELLOW%3. 找到 cloudfunctions/getQASystem 文件夹%RESET%
echo %YELLOW%4. 右键点击该文件夹%RESET%
echo %YELLOW%5. 选择"删除云端文件"（如果存在）%RESET%
echo %YELLOW%6. 再次右键点击该文件夹%RESET%
echo %YELLOW%7. 选择"上传并部署：云端安装依赖"%RESET%
echo %YELLOW%8. 等待部署完成（约1-2分钟）%RESET%
echo.

echo %BLUE%🔧 优化内容：%RESET%
echo %GREEN%✅ 减少超时时间到15秒%RESET%
echo %GREEN%✅ 添加智能降级机制%RESET%
echo %GREEN%✅ 优化错误处理%RESET%
echo %GREEN%✅ 云函数超时设置为20秒%RESET%
echo.

echo %BLUE%🌐 测试地址：%RESET%
echo %YELLOW%- cpolar地址: http://6dc100db.r38.cpolar.top%RESET%
echo %YELLOW%- 健康检查: http://6dc100db.r38.cpolar.top/wechat/health%RESET%
echo.

echo %BLUE%📱 测试问题建议：%RESET%
echo %YELLOW%- "推荐北京景点"%RESET%
echo %YELLOW%- "三亚美食攻略"%RESET%
echo %YELLOW%- "上海到杭州交通"%RESET%
echo.

echo %GREEN%🎯 如果仍然超时，系统会自动使用本地智能回答！%RESET%
echo.
pause
