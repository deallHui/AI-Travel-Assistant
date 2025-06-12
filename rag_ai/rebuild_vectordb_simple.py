#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用简单嵌入模型重建旅游攻略向量数据库
"""

import os
import sys
from pathlib import Path
import numpy as np
from typing import List

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from langchain_chroma import Chroma
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain.embeddings.base import Embeddings
    print("✅ 所有依赖包导入成功")
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)

# 简单的本地嵌入模型类
class SimpleEmbeddings(Embeddings):
    """简单的基于哈希的嵌入模型，用于离线环境"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """将文档列表转换为嵌入向量"""
        embeddings = []
        for text in texts:
            # 使用简单的哈希和归一化创建嵌入向量
            hash_value = hash(text)
            # 创建伪随机但确定性的向量
            np.random.seed(abs(hash_value) % (2**31))
            embedding = np.random.normal(0, 1, self.dimension)
            # 归一化
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding.tolist())
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """将查询文本转换为嵌入向量"""
        return self.embed_documents([text])[0]

def rebuild_travel_vectordb():
    """重建旅游攻略向量数据库"""
    
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
        print("🤖 正在初始化简单嵌入模型...")
        embeddings = SimpleEmbeddings(dimension=384)
        print("✅ 嵌入模型初始化成功")
        
        # 删除旧的向量数据库
        if os.path.exists(vdb_path):
            import shutil
            shutil.rmtree(vdb_path)
            print(f"🗑️ 已删除旧的向量数据库: {vdb_path}")
        
        # 创建向量数据库目录
        os.makedirs(vdb_path, exist_ok=True)
        print(f"📁 向量数据库路径: {vdb_path}")
        
        # 初始化向量数据库
        print("🗄️ 正在初始化向量数据库...")
        try:
            vectorstore = Chroma(
                persist_directory=vdb_path, 
                embedding_function=embeddings
            )
            print("✅ 向量数据库初始化成功")
        except Exception as e:
            print(f"❌ 向量数据库初始化失败: {e}")
            return False
        
        # 批处理写入 - 50个块一批，避免内存问题
        batch_size = 50
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
        
        print("🎉 旅游攻略向量数据库重建完成！")
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
        embeddings = SimpleEmbeddings(dimension=384)
        vectorstore = Chroma(persist_directory=vdb_path, embedding_function=embeddings)
        
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
    print("🚀 开始重建旅游攻略向量数据库")
    print("=" * 50)
    
    # 重建向量数据库
    success = rebuild_travel_vectordb()
    
    if success:
        print("\n" + "=" * 50)
        print("🧪 正在测试向量数据库...")
        test_vectordb()
    else:
        print("❌ 重建失败，请检查错误信息")
        sys.exit(1)
