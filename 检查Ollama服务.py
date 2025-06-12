#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama 服务检查和模型管理脚本
检查 Ollama 服务状态，确保 nomic-embed-text 模型可用
"""

import requests
import subprocess
import sys
import time
import os
from pathlib import Path

def check_ollama_service(base_url="http://localhost:11434"):
    """检查 Ollama 服务是否运行"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def get_ollama_models(base_url="http://localhost:11434"):
    """获取已安装的 Ollama 模型列表"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except Exception:
        return []

def check_model_exists(model_name, base_url="http://localhost:11434"):
    """检查指定模型是否存在"""
    models = get_ollama_models(base_url)
    return any(model_name in model for model in models)

def pull_model(model_name, base_url="http://localhost:11434"):
    """拉取指定模型"""
    try:
        print(f"🔄 正在下载模型: {model_name}")
        print("这可能需要几分钟时间，请耐心等待...")
        
        # 使用 ollama pull 命令
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            print(f"✅ 模型 {model_name} 下载成功")
            return True
        else:
            print(f"❌ 模型下载失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 模型下载超时")
        return False
    except FileNotFoundError:
        print("❌ 未找到 ollama 命令，请确保 Ollama 已正确安装")
        return False
    except Exception as e:
        print(f"❌ 模型下载失败: {e}")
        return False

def test_embedding(model_name="nomic-embed-text:latest", base_url="http://localhost:11434"):
    """测试嵌入模型"""
    try:
        from langchain_ollama import OllamaEmbeddings
        
        embeddings = OllamaEmbeddings(
            model=model_name,
            base_url=base_url
        )
        
        # 测试嵌入
        test_text = "这是一个测试文本"
        embedding = embeddings.embed_query(test_text)
        
        print(f"✅ 嵌入测试成功")
        print(f"   文本: {test_text}")
        print(f"   嵌入维度: {len(embedding)}")
        print(f"   前5个值: {embedding[:5]}")
        return True
        
    except Exception as e:
        print(f"❌ 嵌入测试失败: {e}")
        return False

def start_ollama_service():
    """尝试启动 Ollama 服务"""
    try:
        print("🚀 尝试启动 Ollama 服务...")
        
        # 在 Windows 上尝试启动 Ollama
        if sys.platform == "win32":
            # 尝试通过命令行启动
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/Mac
            subprocess.Popen(["ollama", "serve"])
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        for i in range(10):
            time.sleep(2)
            if check_ollama_service():
                print("✅ Ollama 服务启动成功")
                return True
            print(f"   等待中... ({i+1}/10)")
        
        print("❌ Ollama 服务启动超时")
        return False
        
    except FileNotFoundError:
        print("❌ 未找到 ollama 命令")
        print("请从 https://ollama.ai 下载并安装 Ollama")
        return False
    except Exception as e:
        print(f"❌ 启动 Ollama 服务失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 Ollama 服务检查工具")
    print("=" * 50)
    
    base_url = "http://localhost:11434"
    target_model = "nomic-embed-text:latest"
    
    # 1. 检查 Ollama 服务
    print("1️⃣ 检查 Ollama 服务状态")
    if check_ollama_service(base_url):
        print("✅ Ollama 服务正在运行")
    else:
        print("❌ Ollama 服务未运行")
        print("🚀 尝试启动服务...")
        if not start_ollama_service():
            print("\n💡 手动启动建议:")
            print("1. 打开新的命令行窗口")
            print("2. 运行命令: ollama serve")
            print("3. 保持该窗口开启")
            return False
    
    # 2. 检查模型
    print(f"\n2️⃣ 检查模型: {target_model}")
    if check_model_exists(target_model, base_url):
        print(f"✅ 模型 {target_model} 已安装")
    else:
        print(f"❌ 模型 {target_model} 未安装")
        print("🔄 开始下载模型...")
        if not pull_model(target_model, base_url):
            print("\n💡 手动下载建议:")
            print(f"运行命令: ollama pull {target_model}")
            return False
    
    # 3. 列出所有模型
    print("\n3️⃣ 已安装的模型列表")
    models = get_ollama_models(base_url)
    if models:
        for model in models:
            print(f"   📦 {model}")
    else:
        print("   ❌ 未找到已安装的模型")
    
    # 4. 测试嵌入功能
    print(f"\n4️⃣ 测试嵌入功能")
    if test_embedding(target_model, base_url):
        print("🎉 Ollama 嵌入模型配置完成！")
        print("\n📋 下一步:")
        print("1. 启动 RAG AI 后端服务")
        print("2. 系统将自动使用本地 Ollama 嵌入模型")
        print("3. 无需网络连接即可正常工作")
        return True
    else:
        print("❌ 嵌入功能测试失败")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️  配置未完成，请检查上述错误信息")
        sys.exit(1)
