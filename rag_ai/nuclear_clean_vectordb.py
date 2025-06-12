#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核弹级向量数据库清理工具
彻底清理所有相关文件和缓存，解决顽固的维度不匹配问题
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        💥 核弹级向量数据库清理工具                           ║
    ║                                                              ║
    ║        彻底清理所有缓存和配置，解决顽固问题                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def find_all_vectorstore_dirs():
    """查找所有向量数据库相关目录"""
    base_dir = Path(".")
    vectorstore_dirs = []
    
    # 查找所有可能的向量数据库目录
    patterns = ["vectorstores*", "*vectorstore*", "chroma*"]
    
    for pattern in patterns:
        for path in base_dir.glob(pattern):
            if path.is_dir():
                vectorstore_dirs.append(path)
    
    return vectorstore_dirs

def find_chroma_cache():
    """查找 ChromaDB 缓存目录"""
    cache_dirs = []
    
    # 常见的缓存位置
    possible_cache_locations = [
        Path.home() / ".cache" / "chroma",
        Path.home() / ".chroma",
        Path(tempfile.gettempdir()) / "chroma",
        Path(".") / ".chroma",
        Path(".") / "__pycache__",
        Path("backend") / "__pycache__",
    ]
    
    for cache_dir in possible_cache_locations:
        if cache_dir.exists():
            cache_dirs.append(cache_dir)
    
    return cache_dirs

def nuclear_clean():
    """核弹级清理"""
    print("💥 开始核弹级清理...")
    
    cleaned_items = []
    
    # 1. 清理所有向量数据库目录
    print("\n🗑️ 清理向量数据库目录...")
    vectorstore_dirs = find_all_vectorstore_dirs()
    
    for vdir in vectorstore_dirs:
        try:
            print(f"   删除: {vdir}")
            if vdir.exists():
                shutil.rmtree(vdir)
                cleaned_items.append(str(vdir))
        except Exception as e:
            print(f"   ❌ 删除失败: {vdir} - {e}")
    
    # 2. 清理 ChromaDB 缓存
    print("\n🧹 清理 ChromaDB 缓存...")
    cache_dirs = find_chroma_cache()
    
    for cache_dir in cache_dirs:
        try:
            print(f"   删除缓存: {cache_dir}")
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                cleaned_items.append(str(cache_dir))
        except Exception as e:
            print(f"   ⚠️ 缓存删除失败: {cache_dir} - {e}")
    
    # 3. 清理 Python 缓存
    print("\n🐍 清理 Python 缓存...")
    pycache_dirs = list(Path(".").rglob("__pycache__"))
    
    for pycache in pycache_dirs:
        try:
            print(f"   删除: {pycache}")
            shutil.rmtree(pycache)
            cleaned_items.append(str(pycache))
        except Exception as e:
            print(f"   ⚠️ 删除失败: {pycache} - {e}")
    
    # 4. 清理可能的临时文件
    print("\n🗂️ 清理临时文件...")
    temp_patterns = ["*.tmp", "*.temp", "chroma*", ".chroma*"]
    
    for pattern in temp_patterns:
        for temp_file in Path(".").rglob(pattern):
            if temp_file.is_file():
                try:
                    print(f"   删除临时文件: {temp_file}")
                    temp_file.unlink()
                    cleaned_items.append(str(temp_file))
                except Exception as e:
                    print(f"   ⚠️ 删除失败: {temp_file} - {e}")
    
    return cleaned_items

def create_fresh_vectorstore():
    """创建全新的向量数据库"""
    print("\n🆕 创建全新向量数据库...")
    
    try:
        # 确保使用正确的嵌入模型
        embedding_model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "siliconflow")
        
        print(f"📋 使用嵌入模型: {embedding_model}")
        print(f"📋 提供商: {embedding_provider}")
        
        # 导入必要的库
        from langchain_community.document_loaders import TextLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_chroma import Chroma
        
        # 初始化嵌入模型
        if embedding_provider == "siliconflow":
            sys.path.append("backend")
            from embedding_models import create_siliconflow_embeddings
            embeddings = create_siliconflow_embeddings(embedding_model)
        elif embedding_provider == "ollama":
            from langchain_ollama import OllamaEmbeddings
            embeddings = OllamaEmbeddings(model=embedding_model)
        else:
            raise ValueError(f"不支持的提供商: {embedding_provider}")
        
        print("✅ 嵌入模型初始化成功")
        
        # 测试嵌入维度
        test_embedding = embeddings.embed_query("测试")
        print(f"📊 嵌入维度: {len(test_embedding)}")
        
        # 加载文档
        print("📖 加载旅游攻略文档...")
        loader = TextLoader("travel_guides_database.txt", encoding="utf-8")
        documents = loader.load()
        
        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
        texts = text_splitter.split_documents(documents)
        
        print(f"📄 文档分割为 {len(texts)} 个块")
        
        # 创建全新的向量数据库
        vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
        print(f"🗄️ 创建向量数据库: {vectorstore_path}")
        
        # 确保目录不存在
        if os.path.exists(vectorstore_path):
            shutil.rmtree(vectorstore_path)
        
        # 创建新的向量数据库
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=vectorstore_path
        )
        
        print("✅ 向量数据库创建成功")
        
        # 测试查询
        print("🧪 测试查询...")
        results = vectorstore.similarity_search("北京旅游", k=2)
        print(f"✅ 测试成功，返回 {len(results)} 个结果")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建向量数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_system():
    """验证系统状态"""
    print("\n🔍 验证系统状态...")
    
    # 检查向量数据库
    vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
    if os.path.exists(vectorstore_path):
        files = list(Path(vectorstore_path).rglob("*"))
        print(f"✅ 向量数据库存在，包含 {len(files)} 个文件")
    else:
        print("❌ 向量数据库不存在")
        return False
    
    # 检查嵌入模型
    try:
        embedding_model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "siliconflow")
        
        if embedding_provider == "siliconflow":
            sys.path.append("backend")
            from embedding_models import create_siliconflow_embeddings
            embeddings = create_siliconflow_embeddings(embedding_model)
        else:
            from langchain_ollama import OllamaEmbeddings
            embeddings = OllamaEmbeddings(model=embedding_model)
        
        test_embedding = embeddings.embed_query("测试")
        print(f"✅ 嵌入模型正常，维度: {len(test_embedding)}")
        
    except Exception as e:
        print(f"❌ 嵌入模型测试失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print_banner()
    
    print("⚠️ 警告: 这是核弹级清理，将删除所有相关文件和缓存")
    print("包括:")
    print("- 所有向量数据库目录")
    print("- ChromaDB 缓存")
    print("- Python 缓存文件")
    print("- 临时文件")
    
    confirm = input("\n确认执行核弹级清理? (输入 'NUCLEAR' 确认): ").strip()
    
    if confirm != 'NUCLEAR':
        print("❌ 操作已取消")
        return
    
    print("\n💥 开始核弹级清理流程...")
    
    # 1. 核弹级清理
    cleaned_items = nuclear_clean()
    
    if cleaned_items:
        print(f"\n✅ 清理完成，共清理 {len(cleaned_items)} 个项目")
    else:
        print("\nℹ️ 没有找到需要清理的项目")
    
    # 2. 创建全新向量数据库
    if create_fresh_vectorstore():
        print("\n🎉 全新向量数据库创建成功!")
    else:
        print("\n❌ 向量数据库创建失败")
        return
    
    # 3. 验证系统
    if verify_system():
        print("\n🎉 核弹级清理完成，系统验证通过!")
        print("\n📋 下一步:")
        print("1. 重启后端服务: python start_backend.py")
        print("2. 测试前端问答功能")
        print("3. 享受高速的 SiliconFlow 嵌入模型!")
    else:
        print("\n❌ 系统验证失败，可能需要手动检查")

if __name__ == "__main__":
    main()
