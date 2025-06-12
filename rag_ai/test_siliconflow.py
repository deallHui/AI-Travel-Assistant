#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SiliconFlow API 测试脚本
测试 SiliconFlow 嵌入模型 API 连接
"""

import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")
load_dotenv(".env")

def test_siliconflow_connection():
    """测试 SiliconFlow 连接"""
    print("🧪 测试 SiliconFlow API 连接...")
    
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("❌ 未找到 SILICONFLOW_API_KEY 环境变量")
        print("请在 .env 文件中添加:")
        print("SILICONFLOW_API_KEY=your-api-key")
        return False
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # 测试 API 连接
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 1. 测试模型列表接口
    print("\n🔍 测试模型列表接口...")
    try:
        response = requests.get(
            "https://api.siliconflow.cn/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 模型列表接口连接成功")
            models = response.json()
            
            # 查找嵌入模型
            embedding_models = []
            for model in models.get("data", []):
                if "embed" in model.get("id", "").lower() or "bge" in model.get("id", "").lower():
                    embedding_models.append(model["id"])
            
            if embedding_models:
                print(f"📋 可用的嵌入模型: {embedding_models}")
            else:
                print("⚠️ 未找到嵌入模型")
                
        else:
            print(f"❌ 模型列表接口失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 模型列表接口连接失败: {e}")
        return False
    
    # 2. 测试嵌入接口
    print("\n🧪 测试嵌入接口...")
    try:
        test_data = {
            "model": "BAAI/bge-large-zh-v1.5",
            "input": ["这是一个测试文本", "测试嵌入模型"]
        }
        
        response = requests.post(
            "https://api.siliconflow.cn/v1/embeddings",
            headers=headers,
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embeddings = result.get("data", [])
            
            if embeddings:
                print("✅ 嵌入接口测试成功")
                print(f"📊 嵌入维度: {len(embeddings[0]['embedding'])}")
                print(f"📝 处理文本数: {len(embeddings)}")
                return True
            else:
                print("❌ 嵌入接口返回空数据")
                return False
        else:
            print(f"❌ 嵌入接口失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 嵌入接口测试失败: {e}")
        return False

def get_siliconflow_models():
    """获取 SiliconFlow 可用模型"""
    print("📋 获取 SiliconFlow 可用模型...")
    
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("❌ 未配置 API Key")
        return []
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://api.siliconflow.cn/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            all_models = [model["id"] for model in models.get("data", [])]
            
            # 过滤嵌入模型
            embedding_models = [
                model for model in all_models 
                if any(keyword in model.lower() for keyword in ["embed", "bge", "text2vec"])
            ]
            
            print("🤖 所有可用模型:")
            for model in all_models[:10]:  # 显示前10个
                print(f"  - {model}")
            
            if len(all_models) > 10:
                print(f"  ... 还有 {len(all_models) - 10} 个模型")
            
            print(f"\n🎯 嵌入模型 ({len(embedding_models)} 个):")
            for model in embedding_models:
                print(f"  - {model}")
            
            return embedding_models
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return []

def test_embedding_performance():
    """测试嵌入性能"""
    print("\n⚡ 测试嵌入性能...")
    
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("❌ 未配置 API Key")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试不同大小的文本
    test_cases = [
        ("短文本", ["北京"]),
        ("中等文本", ["北京是中国的首都，有很多著名景点"]),
        ("长文本", ["北京是中华人民共和国的首都，也是全国的政治、文化中心。北京有着悠久的历史，拥有故宫、天安门、长城等众多世界闻名的旅游景点。"]),
        ("批量文本", ["北京景点", "上海美食", "广州购物", "深圳科技", "杭州西湖"])
    ]
    
    for test_name, texts in test_cases:
        print(f"\n🧪 测试 {test_name} ({len(texts)} 条)...")
        
        try:
            import time
            start_time = time.time()
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/embeddings",
                headers=headers,
                json={
                    "model": "BAAI/bge-large-zh-v1.5",
                    "input": texts
                },
                timeout=30
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                embeddings = result.get("data", [])
                print(f"✅ {test_name}: {duration:.2f}秒, {len(embeddings)} 个嵌入")
            else:
                print(f"❌ {test_name}: 失败 ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {test_name}: 错误 - {e}")

def setup_siliconflow():
    """设置 SiliconFlow API Key"""
    print("🔑 设置 SiliconFlow API Key")
    print("=" * 50)
    
    print("1. 访问 https://siliconflow.cn 注册账号")
    print("2. 在控制台创建 API Key")
    print("3. 将 API Key 添加到环境变量")
    
    api_key = input("\n请输入您的 SiliconFlow API Key (或按回车跳过): ").strip()
    
    if api_key:
        # 更新 .env 文件
        env_file = "backend/.env"
        if not os.path.exists(env_file):
            env_file = ".env"
        
        try:
            # 读取现有配置
            lines = []
            if os.path.exists(env_file):
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # 更新或添加 API Key
            key_found = False
            for i, line in enumerate(lines):
                if line.startswith('SILICONFLOW_API_KEY='):
                    lines[i] = f"SILICONFLOW_API_KEY={api_key}\n"
                    key_found = True
                    break
            
            if not key_found:
                lines.append(f"SILICONFLOW_API_KEY={api_key}\n")
            
            # 写回文件
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ API Key 已保存到 {env_file}")
            
            # 重新加载环境变量
            load_dotenv(env_file)
            
            # 测试连接
            if test_siliconflow_connection():
                print("🎉 SiliconFlow 配置成功！")
            else:
                print("❌ SiliconFlow 配置失败，请检查 API Key")
                
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    else:
        print("⏭️ 跳过 SiliconFlow 配置")

def main():
    """主函数"""
    print("🧪 SiliconFlow API 测试工具")
    print("=" * 50)
    
    # 检查 API Key
    api_key = os.getenv("SILICONFLOW_API_KEY")
    
    if not api_key:
        print("❌ 未找到 SiliconFlow API Key")
        setup_siliconflow()
    else:
        print(f"✅ 找到 API Key: {api_key[:10]}...{api_key[-4:]}")
        
        # 运行测试
        if test_siliconflow_connection():
            print("\n" + "=" * 50)
            get_siliconflow_models()
            test_embedding_performance()
        else:
            print("\n❌ 基础连接测试失败")
            print("💡 可能的原因:")
            print("  1. API Key 无效")
            print("  2. 网络连接问题")
            print("  3. API 服务暂时不可用")

if __name__ == "__main__":
    main()
