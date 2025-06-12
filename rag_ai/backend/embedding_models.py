#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌入模型配置
简化的嵌入模型配置和管理
"""

import os
from typing import Dict, Any, Optional

# 支持的嵌入模型配置
EMBEDDING_MODELS = {
    # Ollama 本地模型
    "nomic-embed-text": {
        "name": "Nomic Embed Text",
        "provider": "ollama",
        "model_id": "nomic-embed-text:latest",
        "dimension": 768,
        "description": "高质量的文本嵌入模型，适合中文和英文",
        "speed": "中等",
        "quality": "高"
    },
    "all-minilm-l6-v2": {
        "name": "All MiniLM L6 v2",
        "provider": "ollama",
        "model_id": "all-minilm:l6-v2",
        "dimension": 384,
        "description": "轻量级嵌入模型，速度快",
        "speed": "快",
        "quality": "中等"
    },

    # ModelScope 模型（国内镜像，速度快）
    "bge-small-zh": {
        "name": "BGE Small Chinese",
        "provider": "modelscope",
        "model_id": "AI-ModelScope/bge-small-zh",
        "dimension": 512,
        "description": "智源开源的中文嵌入模型，速度快，适合中文",
        "speed": "快",
        "quality": "高"
    },
    "bge-base-zh": {
        "name": "BGE Base Chinese",
        "provider": "modelscope",
        "model_id": "AI-ModelScope/bge-base-zh",
        "dimension": 768,
        "description": "智源开源的中文嵌入模型，质量高",
        "speed": "中等",
        "quality": "很高"
    },
    "text2vec-base": {
        "name": "Text2Vec Base Chinese",
        "provider": "modelscope",
        "model_id": "damo/nlp_corom_sentence-embedding_chinese-base",
        "dimension": 768,
        "description": "达摩院中文句子嵌入模型",
        "speed": "快",
        "quality": "高"
    },

    # SiliconFlow API 模型（云端API，速度很快）
    "siliconflow-embedding": {
        "name": "SiliconFlow Embedding",
        "provider": "siliconflow",
        "model_id": "BAAI/bge-large-zh-v1.5",
        "dimension": 1024,
        "description": "SiliconFlow提供的高质量中文嵌入模型",
        "speed": "很快",
        "quality": "很高"
    },

    # HuggingFace 镜像模型
    "hf-bge-small": {
        "name": "BGE Small (HF Mirror)",
        "provider": "huggingface_mirror",
        "model_id": "BAAI/bge-small-zh-v1.5",
        "dimension": 512,
        "description": "使用HuggingFace镜像的BGE模型",
        "speed": "快",
        "quality": "高"
    },



    # 本地 Sentence Transformers
    "sentence-transformers": {
        "name": "Sentence Transformers",
        "provider": "sentence_transformers",
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "dimension": 384,
        "description": "开源的句子嵌入模型",
        "speed": "中等",
        "quality": "中等"
    }
}

def get_embedding_model_info(model_key: str = None) -> Dict[str, Any]:
    """
    获取嵌入模型信息
    
    Args:
        model_key: 模型键名，如果为None则使用环境变量
    
    Returns:
        Dict[str, Any]: 模型信息
    """
    if model_key is None:
        # 从环境变量获取
        embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
        # 尝试匹配模型键
        for key, config in EMBEDDING_MODELS.items():
            if config["model_id"] == embedding_model or key in embedding_model:
                model_key = key
                break
        
        if model_key is None:
            model_key = "nomic-embed-text"  # 默认值
    
    return EMBEDDING_MODELS.get(model_key, EMBEDDING_MODELS["nomic-embed-text"])

def create_embedding_instance(model_key: str = None):
    """
    创建嵌入模型实例

    Args:
        model_key: 模型键名

    Returns:
        嵌入模型实例
    """
    model_info = get_embedding_model_info(model_key)
    provider = model_info["provider"]
    model_id = model_info["model_id"]

    try:
        if provider == "ollama":
            from langchain_ollama import OllamaEmbeddings
            return OllamaEmbeddings(
                model=model_id,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )



        elif provider == "modelscope":
            # 使用 ModelScope 的嵌入模型
            return create_modelscope_embeddings(model_id)

        elif provider == "siliconflow":
            # 使用 SiliconFlow API
            return create_siliconflow_embeddings(model_id)

        elif provider == "huggingface_mirror":
            # 使用 HuggingFace 镜像
            return create_huggingface_mirror_embeddings(model_id)

        elif provider == "sentence_transformers":
            # 使用本地 Sentence Transformers
            return create_sentence_transformers_embeddings(model_id)

        elif provider == "huggingface":
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name=model_id,
                model_kwargs={'device': 'cpu'}
            )

        else:
            raise ValueError(f"不支持的提供商: {provider}")

    except ImportError as e:
        raise ImportError(f"缺少依赖包: {e}")
    except Exception as e:
        raise Exception(f"创建嵌入模型失败: {e}")

def create_modelscope_embeddings(model_id: str):
    """创建 ModelScope 嵌入模型"""
    try:
        from sentence_transformers import SentenceTransformer
        from langchain.embeddings.base import Embeddings
        from typing import List

        class ModelScopeEmbeddings(Embeddings):
            def __init__(self, model_name: str):
                # 设置 ModelScope 镜像
                os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
                self.model = SentenceTransformer(model_name, trust_remote_code=True)

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                embeddings = self.model.encode(texts)
                return embeddings.tolist()

            def embed_query(self, text: str) -> List[float]:
                embedding = self.model.encode([text])
                return embedding[0].tolist()

        return ModelScopeEmbeddings(model_id)

    except ImportError:
        raise ImportError("请安装 sentence-transformers: pip install sentence-transformers")

def create_siliconflow_embeddings(model_id: str):
    """创建 SiliconFlow 嵌入模型"""
    try:
        from langchain.embeddings.base import Embeddings
        import requests
        from typing import List

        class SiliconFlowEmbeddings(Embeddings):
            def __init__(self, model_name: str):
                self.model_name = model_name
                self.api_key = os.getenv("SILICONFLOW_API_KEY")
                if not self.api_key:
                    raise ValueError("请设置 SILICONFLOW_API_KEY 环境变量")
                self.base_url = "https://api.siliconflow.cn/v1/embeddings"

                # 测试连接
                self._test_connection()

            def _test_connection(self):
                """测试 API 连接"""
                try:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }

                    # 测试一个简单的嵌入请求
                    test_data = {
                        "model": self.model_name,
                        "input": ["测试"]
                    }

                    response = requests.post(
                        self.base_url,
                        headers=headers,
                        json=test_data,
                        timeout=10
                    )

                    if response.status_code != 200:
                        raise ValueError(f"SiliconFlow API 测试失败: {response.status_code} - {response.text}")

                except requests.exceptions.RequestException as e:
                    raise ValueError(f"SiliconFlow API 连接失败: {e}")

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                # 分批处理大量文本
                batch_size = 100
                all_embeddings = []

                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i+batch_size]

                    data = {
                        "model": self.model_name,
                        "input": batch
                    }

                    try:
                        response = requests.post(
                            self.base_url,
                            headers=headers,
                            json=data,
                            timeout=30
                        )
                        response.raise_for_status()

                        result = response.json()
                        batch_embeddings = [item["embedding"] for item in result["data"]]
                        all_embeddings.extend(batch_embeddings)

                    except requests.exceptions.RequestException as e:
                        raise ValueError(f"SiliconFlow API 请求失败: {e}")

                return all_embeddings

            def embed_query(self, text: str) -> List[float]:
                return self.embed_documents([text])[0]

        return SiliconFlowEmbeddings(model_id)

    except ImportError:
        raise ImportError("请安装 requests: pip install requests")

def create_huggingface_mirror_embeddings(model_id: str):
    """创建 HuggingFace 镜像嵌入模型"""
    try:
        from sentence_transformers import SentenceTransformer
        from langchain.embeddings.base import Embeddings
        from typing import List

        # 设置 HuggingFace 镜像
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

        class HuggingFaceMirrorEmbeddings(Embeddings):
            def __init__(self, model_name: str):
                self.model = SentenceTransformer(model_name, trust_remote_code=True)

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                embeddings = self.model.encode(texts)
                return embeddings.tolist()

            def embed_query(self, text: str) -> List[float]:
                embedding = self.model.encode([text])
                return embedding[0].tolist()

        return HuggingFaceMirrorEmbeddings(model_id)

    except ImportError:
        raise ImportError("请安装 sentence-transformers: pip install sentence-transformers")

def create_sentence_transformers_embeddings(model_id: str):
    """创建本地 Sentence Transformers 嵌入模型"""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name=model_id,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    except ImportError:
        raise ImportError("请安装 langchain-huggingface: pip install langchain-huggingface")

def list_available_models() -> Dict[str, Dict[str, Any]]:
    """
    列出所有可用的嵌入模型
    
    Returns:
        Dict[str, Dict[str, Any]]: 可用模型字典
    """
    return EMBEDDING_MODELS

def validate_model_config(model_key: str) -> tuple[bool, str]:
    """
    验证模型配置
    
    Args:
        model_key: 模型键名
    
    Returns:
        tuple[bool, str]: (是否有效, 错误信息)
    """
    if model_key not in EMBEDDING_MODELS:
        return False, f"未知的模型: {model_key}"
    
    model_info = EMBEDDING_MODELS[model_key]
    provider = model_info["provider"]
    
    # 检查特定提供商的要求
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            return False, "OpenAI API密钥未配置"
    
    return True, ""

def get_current_model_status() -> Dict[str, Any]:
    """
    获取当前模型状态
    
    Returns:
        Dict[str, Any]: 当前模型状态
    """
    embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
    
    # 查找匹配的模型配置
    model_info = None
    model_key = None
    for key, config in EMBEDDING_MODELS.items():
        if config["model_id"] == embedding_model or key in embedding_model:
            model_info = config
            model_key = key
            break
    
    if model_info is None:
        model_info = {
            "name": "自定义模型",
            "provider": embedding_provider,
            "model_id": embedding_model,
            "dimension": "未知",
            "description": "自定义配置的嵌入模型"
        }
        model_key = "custom"
    
    # 检查配置有效性
    is_valid, error_msg = validate_model_config(model_key) if model_key != "custom" else (True, "")
    
    return {
        "model_key": model_key,
        "model_info": model_info,
        "is_valid": is_valid,
        "error_message": error_msg,
        "env_model": embedding_model,
        "env_provider": embedding_provider
    }
