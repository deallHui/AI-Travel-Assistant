#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版向量数据库去重工具
兼容不同版本的 ChromaDB，安全清理重复数据
"""

import os
import sys
import shutil
from pathlib import Path
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🧹 简化版向量数据库去重工具                           ║
    ║                                                              ║
    ║        安全清理重复数据，自动备份                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def backup_vectorstore():
    """备份向量数据库"""
    vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
    
    if not os.path.exists(vectorstore_path):
        print(f"❌ 向量数据库路径不存在: {vectorstore_path}")
        return False
    
    # 创建备份目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{vectorstore_path}_backup_{timestamp}"
    
    try:
        print(f"💾 创建备份: {backup_path}")
        shutil.copytree(vectorstore_path, backup_path)
        print(f"✅ 备份创建成功: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False

def rebuild_from_source():
    """从原始数据重建向量数据库"""
    print("\n🔄 从原始数据重建向量数据库...")
    print("这将删除现有数据库并从旅游攻略文件重新构建")
    
    confirm = input("确认重建? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 重建已取消")
        return False
    
    try:
        # 删除现有向量数据库
        vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
        if os.path.exists(vectorstore_path):
            print(f"🗑️ 删除现有数据库: {vectorstore_path}")
            shutil.rmtree(vectorstore_path)
        
        # 重建数据库
        print("🔄 开始重建...")
        import subprocess
        result = subprocess.run([sys.executable, "build_travel_vectordb.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 向量数据库重建成功")
            print("📊 重建后的数据库应该不包含重复数据")
            return True
        else:
            print(f"❌ 重建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 重建失败: {e}")
        return False

def smart_clean():
    """智能清理重复数据"""
    print("\n🧠 智能清理模式")
    print("这将保留每组重复数据的第一个，删除其余副本")
    
    try:
        from langchain_chroma import Chroma
        
        vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
        embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
        
        print(f"📂 向量数据库路径: {vectorstore_path}")
        
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
            return False
        
        # 加载向量数据库
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embeddings
        )
        
        print("✅ 向量数据库加载成功")
        
        # 获取所有文档
        collection = vectorstore._collection
        all_data = collection.get()
        
        documents = all_data.get('documents', [])
        ids = all_data.get('ids', [])
        
        if not documents:
            print("❌ 无法获取文档数据")
            return False
        
        print(f"📊 当前文档数: {len(documents)}")
        
        # 分析重复内容
        content_to_first_id = {}
        duplicate_ids = []
        
        for i, (doc, doc_id) in enumerate(zip(documents, ids)):
            # 标准化内容
            normalized_content = ' '.join(doc.split())
            
            if normalized_content not in content_to_first_id:
                # 第一次遇到这个内容，保留
                content_to_first_id[normalized_content] = doc_id
            else:
                # 重复内容，标记删除
                duplicate_ids.append(doc_id)
        
        unique_count = len(content_to_first_id)
        duplicate_count = len(duplicate_ids)
        
        print(f"📈 分析结果:")
        print(f"唯一内容数: {unique_count}")
        print(f"重复文档数: {duplicate_count}")
        
        if duplicate_count == 0:
            print("✅ 未发现重复数据")
            return True
        
        print(f"\n🧹 准备删除 {duplicate_count} 个重复文档...")
        
        # 删除重复文档
        if duplicate_ids:
            collection.delete(ids=duplicate_ids)
            print(f"✅ 成功删除 {duplicate_count} 个重复文档")
            
            # 验证结果
            remaining_data = collection.get()
            remaining_count = len(remaining_data.get('documents', []))
            
            print(f"📊 清理结果:")
            print(f"清理前: {len(documents)} 文档")
            print(f"清理后: {remaining_count} 文档")
            print(f"清理数量: {len(documents) - remaining_count}")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ 智能清理失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    print("⚠️ 重要提醒: 此操作将修改向量数据库")
    print("建议先备份数据库以防意外")
    
    # 询问是否继续
    continue_choice = input("\n是否继续进行清理操作? (y/N): ").strip().lower()
    if continue_choice != 'y':
        print("👋 操作已取消")
        return
    
    # 备份数据库
    backup_path = backup_vectorstore()
    if not backup_path:
        print("❌ 备份失败，为安全起见，停止操作")
        return
    
    print(f"\n💡 清理方案:")
    print("1. 智能去重 (推荐) - 快速删除重复数据")
    print("2. 重建数据库 - 从原始数据重新构建")
    print("3. 取消操作")
    
    choice = input("\n请选择清理方案 (1-3): ").strip()
    
    if choice == "1":
        # 智能去重
        print("\n🧹 开始智能去重...")
        if smart_clean():
            print("\n🎉 去重完成！")
            print(f"💾 备份位置: {backup_path}")
            print("🔄 建议重启后端服务以应用更改:")
            print("   python start_backend.py")
        else:
            print("❌ 去重失败")
    
    elif choice == "2":
        # 重建数据库
        if rebuild_from_source():
            print("\n🎉 数据库重建完成！")
            print(f"💾 备份位置: {backup_path}")
            print("🔄 建议重启后端服务:")
            print("   python start_backend.py")
        else:
            print("❌ 重建失败")
    
    else:
        print("👋 操作已取消")
        print(f"💾 备份位置: {backup_path}")

if __name__ == "__main__":
    main()
