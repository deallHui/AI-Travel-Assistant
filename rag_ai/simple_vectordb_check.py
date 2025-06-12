#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版向量数据库检查工具
兼容不同版本的 ChromaDB
"""

import os
import sys
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🔍 向量数据库简化检查工具                             ║
    ║                                                              ║
    ║        快速检查数据库状态和重复情况                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def load_vectorstore():
    """加载向量数据库"""
    try:
        from langchain_chroma import Chroma
        
        vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
        embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
        
        print(f"📂 向量数据库路径: {vectorstore_path}")
        print(f"🤖 嵌入模型: {embedding_model} ({embedding_provider})")
        
        if not os.path.exists(vectorstore_path):
            print(f"❌ 向量数据库路径不存在: {vectorstore_path}")
            return None
        
        # 初始化嵌入模型
        if embedding_provider == "siliconflow":
            sys.path.append("backend")
            from embedding_models import create_siliconflow_embeddings
            embeddings = create_siliconflow_embeddings(embedding_model)
        elif embedding_provider == "ollama":
            from langchain_ollama import OllamaEmbeddings
            embeddings = OllamaEmbeddings(model=embedding_model)
        else:
            print(f"❌ 不支持的嵌入模型提供商: {embedding_provider}")
            return None
        
        # 加载向量数据库
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embeddings
        )
        
        print("✅ 向量数据库加载成功")
        return vectorstore
        
    except Exception as e:
        print(f"❌ 加载向量数据库失败: {e}")
        return None

def check_database_simple(vectorstore):
    """简单检查数据库"""
    try:
        collection = vectorstore._collection
        
        # 尝试多种方法获取数据
        documents = []
        total_count = 0
        
        try:
            # 方法1: 直接获取文档数量
            total_count = collection.count()
            print(f"📊 数据库文档总数: {total_count}")
        except Exception as e:
            print(f"无法获取文档数量: {e}")
        
        try:
            # 方法2: 获取所有文档内容
            all_data = collection.get()
            documents = all_data.get('documents', [])
            metadatas = all_data.get('metadatas', [])
            
            print(f"📄 成功获取文档内容: {len(documents)} 个")
            
            if len(documents) > 0:
                # 分析重复内容
                content_counter = Counter(documents)
                unique_count = len(content_counter)
                duplicate_groups = sum(1 for count in content_counter.values() if count > 1)
                total_duplicates = sum(count - 1 for count in content_counter.values() if count > 1)
                
                print(f"\n📈 重复分析:")
                print(f"总文档数: {len(documents)}")
                print(f"唯一内容数: {unique_count}")
                print(f"重复组数: {duplicate_groups}")
                print(f"重复文档数: {total_duplicates}")
                
                if total_duplicates > 0:
                    print(f"\n⚠️ 发现重复数据!")
                    print(f"可以清理 {total_duplicates} 个重复文档")
                    print(f"清理后将剩余 {unique_count} 个唯一文档")
                    
                    # 显示重复内容示例
                    print(f"\n🔍 重复内容示例:")
                    shown = 0
                    for content, count in content_counter.items():
                        if count > 1 and shown < 3:
                            preview = content[:100] + "..." if len(content) > 100 else content
                            print(f"  重复{count}次: {preview}")
                            shown += 1
                    
                    return {
                        'has_duplicates': True,
                        'total_docs': len(documents),
                        'unique_docs': unique_count,
                        'duplicate_count': total_duplicates,
                        'documents': documents
                    }
                else:
                    print(f"\n✅ 未发现重复数据，数据库状态良好")
                    return {
                        'has_duplicates': False,
                        'total_docs': len(documents),
                        'unique_docs': unique_count,
                        'duplicate_count': 0,
                        'documents': documents
                    }
            else:
                print("❌ 数据库为空或无法获取文档内容")
                return None
                
        except Exception as e:
            print(f"❌ 获取文档内容失败: {e}")
            return None
            
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return None

def show_sample_documents(documents, num_samples=3):
    """显示样本文档"""
    if not documents:
        return
    
    print(f"\n📄 样本文档 (前{min(num_samples, len(documents))}个):")
    print("=" * 60)
    
    for i in range(min(num_samples, len(documents))):
        content = documents[i]
        preview = content[:200] + "..." if len(content) > 200 else content
        print(f"\n{i+1}. 文档内容:")
        print(f"   {preview}")
        print("-" * 40)

def main():
    """主函数"""
    print_banner()
    
    print("🔍 开始检查向量数据库...")
    
    # 加载向量数据库
    vectorstore = load_vectorstore()
    if not vectorstore:
        return
    
    # 检查数据库
    result = check_database_simple(vectorstore)
    if not result:
        return
    
    # 显示样本文档
    if result.get('documents'):
        show_sample_documents(result['documents'])
    
    # 给出建议
    if result['has_duplicates']:
        print(f"\n💡 建议操作:")
        print(f"1. 运行去重脚本: python simple_vectordb_clean.py")
        print(f"2. 或重建数据库: python build_travel_vectordb.py")
        
        clean_choice = input("\n是否现在运行去重脚本? (y/N): ").strip().lower()
        if clean_choice == 'y':
            print("🔄 准备运行去重脚本...")
            try:
                import subprocess
                result = subprocess.run([sys.executable, "simple_vectordb_clean.py"])
                if result.returncode == 0:
                    print("✅ 去重完成")
                else:
                    print("❌ 去重失败")
            except Exception as e:
                print(f"❌ 运行去重脚本失败: {e}")
    else:
        print(f"\n✅ 数据库状态良好，无需清理")

if __name__ == "__main__":
    main()
