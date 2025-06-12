#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库管理工具
用于管理和维护RAG系统的知识库
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from langchain_chroma import Chroma
    from langchain_community.document_loaders import TextLoader, DirectoryLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_ollama import OllamaEmbeddings
    from langchain.schema import Document
    print("✅ 所有依赖包导入成功")
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)

class KnowledgeManager:
    """知识库管理器"""
    
    def __init__(self, vectorstore_path: str = "vectorstores"):
        self.vectorstore_path = vectorstore_path
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n## ", "\n### ", "\n**", "\n- ", "\n", "。", "，", " ", ""]
        )
        
    def load_vectorstore(self) -> Chroma:
        """加载向量数据库"""
        if not os.path.exists(self.vectorstore_path):
            print(f"❌ 向量数据库不存在: {self.vectorstore_path}")
            return None
            
        try:
            vectorstore = Chroma(
                persist_directory=self.vectorstore_path,
                embedding_function=self.embeddings
            )
            print(f"✅ 向量数据库加载成功: {self.vectorstore_path}")
            return vectorstore
        except Exception as e:
            print(f"❌ 向量数据库加载失败: {e}")
            return None
    
    def add_document_from_file(self, file_path: str, metadata: Dict[str, Any] = None) -> bool:
        """从文件添加文档到知识库"""
        try:
            # 加载文档
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()
            
            # 添加元数据
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # 分割文档
            split_docs = self.text_splitter.split_documents(documents)
            
            # 加载向量数据库
            vectorstore = self.load_vectorstore()
            if not vectorstore:
                return False
            
            # 添加文档
            vectorstore.add_documents(split_docs)
            
            print(f"✅ 成功添加文档: {file_path}")
            print(f"   - 分割为 {len(split_docs)} 个块")
            return True
            
        except Exception as e:
            print(f"❌ 添加文档失败: {e}")
            return False
    
    def add_documents_from_directory(self, directory_path: str, file_pattern: str = "*.txt") -> bool:
        """从目录批量添加文档"""
        try:
            # 加载目录中的所有文档
            loader = DirectoryLoader(
                directory_path,
                glob=file_pattern,
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"}
            )
            documents = loader.load()
            
            if not documents:
                print(f"❌ 目录中没有找到匹配的文档: {directory_path}")
                return False
            
            # 分割文档
            split_docs = self.text_splitter.split_documents(documents)
            
            # 加载向量数据库
            vectorstore = self.load_vectorstore()
            if not vectorstore:
                return False
            
            # 批量添加文档
            batch_size = 50
            for i in range(0, len(split_docs), batch_size):
                batch = split_docs[i:i+batch_size]
                vectorstore.add_documents(batch)
                print(f"✅ 已处理 {min(i+batch_size, len(split_docs))}/{len(split_docs)} 个文档块")
            
            print(f"✅ 成功添加目录文档: {directory_path}")
            print(f"   - 总文档数: {len(documents)}")
            print(f"   - 分割块数: {len(split_docs)}")
            return True
            
        except Exception as e:
            print(f"❌ 批量添加文档失败: {e}")
            return False
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """搜索文档"""
        vectorstore = self.load_vectorstore()
        if not vectorstore:
            return []
        
        try:
            docs = vectorstore.similarity_search(query, k=k)
            results = []
            
            for i, doc in enumerate(docs):
                results.append({
                    "rank": i + 1,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        vectorstore = self.load_vectorstore()
        if not vectorstore:
            return {}
        
        try:
            collection = vectorstore._collection
            doc_count = collection.count()
            
            return {
                "document_count": doc_count,
                "vectorstore_path": self.vectorstore_path,
                "embedding_model": "nomic-embed-text:latest",
                "last_updated": datetime.now().isoformat(),
                "status": "active"
            }
            
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}
    
    def export_knowledge_base(self, output_file: str) -> bool:
        """导出知识库信息"""
        try:
            stats = self.get_database_stats()
            sample_docs = self.search_documents("", k=10)  # 获取一些示例文档
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "statistics": stats,
                "sample_documents": sample_docs
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 知识库信息已导出到: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False

def main():
    """主函数 - 命令行工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG知识库管理工具")
    parser.add_argument("--vectorstore", default="vectorstores", help="向量数据库路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 添加文档命令
    add_parser = subparsers.add_parser("add", help="添加文档到知识库")
    add_parser.add_argument("file_path", help="文档文件路径")
    add_parser.add_argument("--title", help="文档标题")
    add_parser.add_argument("--category", help="文档分类")
    
    # 批量添加命令
    batch_parser = subparsers.add_parser("batch-add", help="批量添加文档")
    batch_parser.add_argument("directory", help="文档目录路径")
    batch_parser.add_argument("--pattern", default="*.txt", help="文件匹配模式")
    
    # 搜索命令
    search_parser = subparsers.add_parser("search", help="搜索文档")
    search_parser.add_argument("query", help="搜索查询")
    search_parser.add_argument("--top-k", type=int, default=5, help="返回结果数量")
    
    # 统计命令
    subparsers.add_parser("stats", help="显示数据库统计信息")
    
    # 导出命令
    export_parser = subparsers.add_parser("export", help="导出知识库信息")
    export_parser.add_argument("output_file", help="输出文件路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建知识库管理器
    km = KnowledgeManager(args.vectorstore)
    
    if args.command == "add":
        metadata = {}
        if args.title:
            metadata["title"] = args.title
        if args.category:
            metadata["category"] = args.category
        
        success = km.add_document_from_file(args.file_path, metadata)
        sys.exit(0 if success else 1)
    
    elif args.command == "batch-add":
        success = km.add_documents_from_directory(args.directory, args.pattern)
        sys.exit(0 if success else 1)
    
    elif args.command == "search":
        results = km.search_documents(args.query, args.top_k)
        if results:
            print(f"🔍 搜索结果 (共 {len(results)} 条):")
            for result in results:
                print(f"\n{result['rank']}. {result['preview']}")
                if result['metadata']:
                    print(f"   元数据: {result['metadata']}")
        else:
            print("❌ 没有找到相关文档")
    
    elif args.command == "stats":
        stats = km.get_database_stats()
        if stats:
            print("📊 数据库统计信息:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        else:
            print("❌ 无法获取统计信息")
    
    elif args.command == "export":
        success = km.export_knowledge_base(args.output_file)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
