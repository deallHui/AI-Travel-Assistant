#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP配置验证脚本
验证所有配置文件中的IP地址是否已正确更新为 172.18.2.53
"""

import os
import re
from pathlib import Path

def check_file_content(file_path, expected_ip="172.18.2.53"):
    """检查文件中的IP配置"""
    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找IP地址模式
        ip_patterns = [
            r'localhost',
            r'127\.0\.0\.1',
            r'0\.0\.0\.0',
            r'192\.168\.\d+\.\d+',
            r'10\.0\.0\.\d+',
            expected_ip
        ]
        
        found_ips = []
        for pattern in ip_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found_ips.extend(matches)
        
        has_expected_ip = expected_ip in content
        return has_expected_ip, found_ips
        
    except Exception as e:
        return False, f"读取文件失败: {e}"

def main():
    """主函数"""
    print("🔍 IP配置验证工具")
    print("=" * 50)
    
    expected_ip = "172.18.2.53"
    
    # 需要检查的文件列表
    files_to_check = [
        {
            "path": "rag_ai/backend/.env",
            "description": "后端环境配置",
            "key_config": "HOST"
        },
        {
            "path": "WCDS/cloudfunctions/getQASystem/index.js",
            "description": "微信云函数配置",
            "key_config": "ragApiBaseUrl"
        },
        {
            "path": "WCDS/config/api.js",
            "description": "微信小程序API配置",
            "key_config": "ragApiBaseUrl"
        },
        {
            "path": "rag_ai/frontend/vite.config.js",
            "description": "前端代理配置",
            "key_config": "proxy target"
        },
        {
            "path": "rag_ai/deploy_config.py",
            "description": "部署配置",
            "key_config": "HOST"
        }
    ]
    
    all_correct = True
    
    for file_info in files_to_check:
        file_path = file_info["path"]
        description = file_info["description"]
        
        print(f"\n📁 检查 {description}")
        print(f"   文件: {file_path}")
        
        has_expected, found_ips = check_file_content(file_path, expected_ip)
        
        if has_expected:
            print(f"   ✅ 已配置目标IP: {expected_ip}")
        else:
            print(f"   ❌ 未找到目标IP: {expected_ip}")
            all_correct = False
        
        if found_ips:
            print(f"   🔍 发现的IP地址: {list(set(found_ips))}")
    
    print("\n" + "=" * 50)
    
    if all_correct:
        print("🎉 所有配置文件都已正确更新！")
        print(f"✅ 目标IP地址: {expected_ip}")
        print("\n📋 下一步操作:")
        print("1. 启动后端服务: python rag_ai/start_backend.py")
        print("2. 测试服务连接: curl http://172.18.2.53:8000/health")
        print("3. 重新部署微信小程序云函数")
        print("4. 测试微信小程序功能")
    else:
        print("⚠️  部分配置文件需要手动检查和修正")
        print("请检查上述标记为❌的文件")
    
    print("\n🌐 网络连接测试:")
    print("可以使用以下命令测试网络连接:")
    print(f"ping {expected_ip}")
    print(f"curl http://{expected_ip}:8000/health")

if __name__ == "__main__":
    main()
