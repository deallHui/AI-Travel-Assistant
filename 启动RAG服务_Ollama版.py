#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG AI 服务启动脚本 - Ollama 本地嵌入模型版本
专门处理 Ollama 嵌入模型的启动和配置
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path

def check_ollama_service():
    """检查 Ollama 服务状态"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_ollama_model(model_name="nomic-embed-text:latest"):
    """检查 Ollama 模型是否存在"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return any(model_name in model for model in models)
        return False
    except:
        return False

def test_ollama_embedding():
    """测试 Ollama 嵌入功能"""
    try:
        test_data = {
            "model": "nomic-embed-text:latest",
            "prompt": "测试"
        }
        
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            embedding = data.get('embedding', [])
            return len(embedding) > 0
        return False
    except:
        return False

def wait_for_ollama_ready(max_wait=60):
    """等待 Ollama 服务完全就绪"""
    print("⏳ 等待 Ollama 服务就绪...")
    
    for i in range(max_wait):
        if check_ollama_service():
            print("✅ Ollama 服务已启动")
            
            # 检查模型
            if check_ollama_model():
                print("✅ nomic-embed-text 模型已加载")
                
                # 测试嵌入功能
                if test_ollama_embedding():
                    print("✅ 嵌入功能测试成功")
                    return True
                else:
                    print("⏳ 等待嵌入功能就绪...")
            else:
                print("⏳ 等待模型加载...")
        else:
            print("⏳ 等待 Ollama 服务启动...")
        
        time.sleep(1)
    
    return False

def start_rag_backend():
    """启动 RAG 后端服务"""
    print("\n🚀 启动 RAG AI 后端服务")
    print("=" * 50)
    
    # 切换到项目目录
    os.chdir(Path(__file__).parent)
    
    # 设置环境变量
    env = os.environ.copy()
    env["HOST"] = "172.18.2.53"
    env["PORT"] = "8000"
    
    try:
        # 启动后端服务
        cmd = [
            sys.executable, "-m", "uvicorn",
            "rag_ai.backend.main:app",
            "--host", "172.18.2.53",
            "--port", "8000",
            "--reload"
        ]
        
        print(f"启动命令: {' '.join(cmd)}")
        print(f"服务地址: http://172.18.2.53:8000")
        print("按 Ctrl+C 停止服务")
        print("-" * 50)
        
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n✅ 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🤖 RAG AI 服务启动器 - Ollama 版本")
    print("IP地址: 172.18.2.53:8000")
    print("=" * 50)
    
    # 1. 检查 Ollama 服务
    print("1️⃣ 检查 Ollama 服务")
    if not check_ollama_service():
        print("❌ Ollama 服务未运行")
        print("\n💡 请先启动 Ollama 服务:")
        print("1. 打开新的命令行窗口")
        print("2. 运行: ollama serve")
        print("3. 保持该窗口开启")
        print("4. 重新运行此脚本")
        return False
    
    # 2. 检查模型
    print("2️⃣ 检查嵌入模型")
    if not check_ollama_model():
        print("❌ nomic-embed-text 模型未安装")
        print("\n💡 请安装模型:")
        print("运行: ollama pull nomic-embed-text")
        return False
    
    # 3. 等待服务就绪
    print("3️⃣ 等待服务完全就绪")
    if not wait_for_ollama_ready():
        print("❌ Ollama 服务未能完全就绪")
        print("\n💡 建议:")
        print("1. 重启 Ollama 服务")
        print("2. 等待几分钟让模型完全加载")
        print("3. 重新运行此脚本")
        return False
    
    # 4. 启动 RAG 服务
    print("4️⃣ 启动 RAG AI 服务")
    return start_rag_backend()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 启动失败")
        input("按回车键退出...")
        sys.exit(1)
