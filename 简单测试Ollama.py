#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的 Ollama 嵌入模型测试
"""

import requests
import time

def test_ollama_simple():
    """简单测试 Ollama 嵌入"""
    base_url = "http://localhost:11434"
    model = "nomic-embed-text:latest"
    
    print("🔍 测试 Ollama 嵌入模型")
    print(f"服务地址: {base_url}")
    print(f"模型: {model}")
    print("-" * 40)
    
    # 测试数据
    test_data = {
        "model": model,
        "prompt": "这是一个测试文本"
    }
    
    try:
        print("📡 发送嵌入请求...")
        response = requests.post(
            f"{base_url}/api/embeddings",
            json=test_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            embedding = data.get('embedding', [])
            print(f"✅ 嵌入成功!")
            print(f"嵌入维度: {len(embedding)}")
            print(f"前5个值: {embedding[:5] if embedding else '无数据'}")
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，模型可能正在加载中...")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_with_langchain():
    """使用 LangChain 测试"""
    try:
        print("\n🔧 使用 LangChain 测试...")
        from langchain_ollama import OllamaEmbeddings
        
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text:latest",
            base_url="http://localhost:11434"
        )
        
        # 简单测试
        test_text = "测试"
        print(f"测试文本: {test_text}")
        
        embedding = embeddings.embed_query(test_text)
        print(f"✅ LangChain 嵌入成功!")
        print(f"嵌入维度: {len(embedding)}")
        return True
        
    except Exception as e:
        print(f"❌ LangChain 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    
    # 先测试原始 API
    success1 = test_ollama_simple()
    
    # 再测试 LangChain
    success2 = test_with_langchain()
    
    print("\n" + "=" * 50)
    if success1 or success2:
        print("🎉 至少一种方式测试成功!")
        print("可以尝试启动 RAG AI 服务")
    else:
        print("❌ 所有测试都失败了")
        print("建议:")
        print("1. 重启 Ollama 服务: ollama serve")
        print("2. 等待几分钟让模型完全加载")
        print("3. 重新运行测试")
