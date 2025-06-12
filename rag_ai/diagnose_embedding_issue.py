#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌入模型维度诊断工具
检查嵌入模型和向量数据库的维度匹配问题
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🔍 嵌入模型维度诊断工具                               ║
    ║                                                              ║
    ║        检查维度匹配问题并提供解决方案                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_current_config():
    """检查当前配置"""
    print("📋 当前嵌入模型配置:")
    print("=" * 50)
    
    embedding_model = os.getenv("EMBEDDING_MODEL", "未配置")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "未配置")
    
    print(f"模型: {embedding_model}")
    print(f"提供商: {embedding_provider}")
    
    return embedding_model, embedding_provider

def test_embedding_dimension():
    """测试当前嵌入模型的维度"""
    print("\n🧪 测试嵌入模型维度...")
    
    embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
    
    try:
        if embedding_provider == "siliconflow":
            sys.path.append("backend")
            from embedding_models import create_siliconflow_embeddings
            embeddings = create_siliconflow_embeddings(embedding_model)
        elif embedding_provider == "ollama":
            from langchain_ollama import OllamaEmbeddings
            embeddings = OllamaEmbeddings(model=embedding_model)
        else:
            print(f"❌ 不支持的提供商: {embedding_provider}")
            return None
        
        # 测试嵌入
        test_text = "测试文本"
        embedding = embeddings.embed_query(test_text)
        dimension = len(embedding)
        
        print(f"✅ 嵌入模型测试成功")
        print(f"📊 嵌入维度: {dimension}")
        
        return dimension
        
    except Exception as e:
        print(f"❌ 嵌入模型测试失败: {e}")
        return None

def check_vectorstore_dimension():
    """检查向量数据库维度"""
    print("\n🗄️ 检查向量数据库维度...")
    
    vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
    
    if not os.path.exists(vectorstore_path):
        print(f"❌ 向量数据库不存在: {vectorstore_path}")
        return None
    
    try:
        from langchain_chroma import Chroma
        
        # 使用临时嵌入模型加载数据库（只是为了检查维度）
        from langchain_ollama import OllamaEmbeddings
        temp_embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
        
        try:
            vectorstore = Chroma(
                persist_directory=vectorstore_path,
                embedding_function=temp_embeddings
            )
            
            # 获取集合信息
            collection = vectorstore._collection
            
            # 尝试获取一个向量来检查维度
            data = collection.get(limit=1, include=['embeddings'])
            
            if data['embeddings'] and len(data['embeddings']) > 0:
                dimension = len(data['embeddings'][0])
                print(f"✅ 向量数据库检查成功")
                print(f"📊 数据库维度: {dimension}")
                return dimension
            else:
                print("⚠️ 向量数据库为空")
                return None
                
        except Exception as e:
            print(f"❌ 无法加载向量数据库: {e}")
            return None
            
    except Exception as e:
        print(f"❌ 检查向量数据库失败: {e}")
        return None

def provide_solution(embedding_dim, vectorstore_dim):
    """提供解决方案"""
    print("\n💡 解决方案:")
    print("=" * 50)
    
    if embedding_dim is None:
        print("❌ 嵌入模型有问题，请检查配置")
        return
    
    if vectorstore_dim is None:
        print("🔄 向量数据库不存在或为空，需要构建")
        print("解决方案: python build_travel_vectordb.py")
        return
    
    if embedding_dim == vectorstore_dim:
        print("✅ 维度匹配，应该没有问题")
        print("可能是其他原因导致的错误")
    else:
        print(f"❌ 维度不匹配!")
        print(f"   嵌入模型维度: {embedding_dim}")
        print(f"   数据库维度: {vectorstore_dim}")
        print("\n🔧 解决方案:")
        print("1. 重建向量数据库 (推荐):")
        print("   python build_travel_vectordb.py")
        print("\n2. 或者切换到匹配的嵌入模型:")
        if vectorstore_dim == 768:
            print("   python switch_embedding.py switch --model nomic-embed-text")
        elif vectorstore_dim == 1024:
            print("   python switch_embedding.py switch --model siliconflow-embedding")

def force_clean_and_rebuild():
    """强制清理并重建"""
    print("\n🧹 强制清理并重建向量数据库...")
    
    vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
    
    if os.path.exists(vectorstore_path):
        import shutil
        from datetime import datetime
        
        # 备份
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{vectorstore_path}_backup_{timestamp}"
        
        try:
            print(f"💾 创建备份: {backup_path}")
            shutil.copytree(vectorstore_path, backup_path)
            
            print(f"🗑️ 删除旧数据库: {vectorstore_path}")
            shutil.rmtree(vectorstore_path)
            
            print("✅ 清理完成")
            
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            return False
    
    # 重建
    print("🔄 开始重建...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "build_travel_vectordb.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 重建成功")
            return True
        else:
            print(f"❌ 重建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 重建失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查配置
    embedding_model, embedding_provider = check_current_config()
    
    # 测试嵌入模型维度
    embedding_dim = test_embedding_dimension()
    
    # 检查向量数据库维度
    vectorstore_dim = check_vectorstore_dimension()
    
    # 提供解决方案
    provide_solution(embedding_dim, vectorstore_dim)
    
    # 询问是否强制重建
    if embedding_dim and vectorstore_dim and embedding_dim != vectorstore_dim:
        print(f"\n⚠️ 检测到维度不匹配: {embedding_dim} vs {vectorstore_dim}")
        choice = input("是否强制清理并重建向量数据库? (y/N): ").strip().lower()
        
        if choice == 'y':
            if force_clean_and_rebuild():
                print("\n🎉 问题已解决！请重启后端服务:")
                print("   python start_backend.py")
            else:
                print("❌ 重建失败，请手动操作")

if __name__ == "__main__":
    main()
