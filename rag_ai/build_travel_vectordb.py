#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旅游攻略向量数据库构建脚本
解决 Windows 系统兼容性问题
"""

import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from langchain_chroma import Chroma
    from langchain_community.document_loaders import TextLoader
    from langchain_ollama import OllamaEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("✅ 所有依赖包导入成功")
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请运行: pip install langchain-chroma langchain-community langchain-ollama langchain-text-splitters")
    sys.exit(1)

def build_travel_vectordb():
    """构建旅游攻略向量数据库"""
    
    # 文件路径配置
    travel_file = "travel_guides_database.txt"
    vdb_path = r"D:\AICD\rag_ai\vectorstores"
    
    # 检查文件是否存在
    if not os.path.exists(travel_file):
        print(f"❌ 文件不存在: {travel_file}")
        return False
    
    print(f"📖 正在加载文档: {travel_file}")
    
    try:
        # 加载旅游攻略文档
        loader = TextLoader(travel_file, encoding="utf-8")
        documents = loader.load()
        print(f"✅ 文档加载成功，共 {len(documents)} 个文档")
        
        # 针对旅游攻略优化的分块参数
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,      # 增加到800字符，保证攻略信息完整性
            chunk_overlap=100,   # 增加重叠，确保相关信息不被分割
            separators=[         # 优化分割符，按旅游攻略结构分割
                "\n## ",         # 按大标题分割
                "\n### ",        # 按小标题分割  
                "\n**",          # 按粗体标题分割
                "\n- ",          # 按列表项分割
                "\n",            # 按段落分割
                "。",            # 按句号分割
                "，",            # 按逗号分割
                " ",             # 按空格分割
                ""               # 字符级分割
            ]
        )
        
        split_documents = text_splitter.split_documents(documents)
        print(f"📄 文档被分割为 {len(split_documents)} 个块")
        
        # 显示分块示例
        if split_documents:
            print(f"📋 分块示例 (前3个块):")
            for i, doc in enumerate(split_documents[:3]):
                print(f"  块 {i+1}: {len(doc.page_content)} 字符")
                preview = doc.page_content[:100].replace('\n', ' ')
                print(f"  内容: {preview}...")
                print()
        
        # 初始化嵌入模型
        print("🤖 正在初始化嵌入模型...")
        try:
            embed_model = OllamaEmbeddings(
                model="nomic-embed-text:latest",
            )
            print("✅ 嵌入模型初始化成功")
        except Exception as e:
            print(f"❌ 嵌入模型初始化失败: {e}")
            print("请确保 Ollama 服务正在运行，并已下载 nomic-embed-text 模型")
            print("运行命令: ollama pull nomic-embed-text")
            return False
        
        # 创建向量数据库目录
        os.makedirs(vdb_path, exist_ok=True)
        print(f"📁 向量数据库路径: {vdb_path}")
        
        # 初始化向量数据库
        print("🗄️ 正在初始化向量数据库...")
        try:
            vectorstore = Chroma(
                persist_directory=vdb_path, 
                embedding_function=embed_model
            )
            print("✅ 向量数据库初始化成功")
        except Exception as e:
            print(f"❌ 向量数据库初始化失败: {e}")
            return False
        
        # 批处理写入 - 200个块一批，平衡效率和稳定性
        batch_size = 200
        total_batches = (len(split_documents) + batch_size - 1) // batch_size
        
        print(f"🚀 开始批量写入向量数据库...")
        print(f"📊 总计 {len(split_documents)} 个文档块，分 {total_batches} 批处理")
        
        for i in range(0, len(split_documents), batch_size):
            batch_num = i // batch_size + 1
            batch = split_documents[i:i+batch_size]
            
            try:
                vectorstore.add_documents(batch)
                processed = min(i + batch_size, len(split_documents))
                print(f"✅ 批次 {batch_num}/{total_batches}: 已处理 {processed}/{len(split_documents)} 个文档块")
            except Exception as e:
                print(f"❌ 批次 {batch_num} 处理失败: {e}")
                return False
        
        print("🎉 旅游攻略向量数据库构建完成！")
        print(f"📈 统计信息:")
        print(f"  - 原始文档: {len(documents)} 个")
        print(f"  - 分割块数: {len(split_documents)} 个")
        print(f"  - 平均块大小: {sum(len(doc.page_content) for doc in split_documents) // len(split_documents)} 字符")
        print(f"  - 存储路径: {vdb_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vectordb():
    """测试向量数据库"""
    vdb_path = r"D:\AICD\rag_ai\vectorstores"
    
    try:
        embed_model = OllamaEmbeddings(model="nomic-embed-text:latest")
        vectorstore = Chroma(persist_directory=vdb_path, embedding_function=embed_model)
        
        # 测试查询
        test_query = "北京旅游景点推荐"
        results = vectorstore.similarity_search(test_query, k=3)
        
        print(f"🔍 测试查询: '{test_query}'")
        print(f"📋 返回结果: {len(results)} 个相关文档")
        
        for i, doc in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(f"内容: {doc.page_content[:200]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始构建旅游攻略向量数据库")
    print("=" * 50)
    
    # 构建向量数据库
    success = build_travel_vectordb()
    
    if success:
        print("\n" + "=" * 50)
        print("🧪 正在测试向量数据库...")
        test_vectordb()
    else:
        print("❌ 构建失败，请检查错误信息")
        sys.exit(1)
