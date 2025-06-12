from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# 添加config目录到Python路径
config_dir = Path(__file__).parent.parent / "config"
if config_dir.exists():
    sys.path.insert(0, str(config_dir))
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.llms.base import LLM
from langchain.chains import RetrievalQA
from typing import List
import requests
import json

# 导入嵌入模型配置
try:
    from backend.embedding_models import create_embedding_instance, get_current_model_status
    EMBEDDING_CONFIG_AVAILABLE = True
except ImportError:
    try:
        from embedding_models import create_embedding_instance, get_current_model_status
        EMBEDDING_CONFIG_AVAILABLE = True
    except ImportError:
        EMBEDDING_CONFIG_AVAILABLE = False

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Knowledge Base API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: Optional[float] = None

# 微信小程序专用请求模型
class WechatQueryRequest(BaseModel):
    question: str
    openid: Optional[str] = None  # 微信用户唯一标识
    location: Optional[dict] = None  # 用户位置信息 {"latitude": float, "longitude": float, "city": str}
    top_k: Optional[int] = 3

class WechatQueryResponse(BaseModel):
    success: bool
    message: str = ""
    data: dict = {}
    timestamp: str

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class DeepSeekLLM(LLM):
    """自定义DeepSeek LLM类"""

    api_key: str

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 添加旅游助手的系统提示
        system_prompt = """你是一个专业的旅游攻略助手，专门为用户提供旅游相关的建议和信息。请遵循以下原则：

1. 🎯 专注旅游：只回答与旅游、景点、美食、住宿、交通、行程规划相关的问题
2. 📍 具体实用：提供具体的地点、价格、时间等实用信息
3. 🌟 个性化：根据用户的预算、时间、偏好给出个性化建议
4. 💡 贴心提示：提供实用的旅游小贴士和注意事项
5. 📚 基于知识库：优先使用提供的攻略知识库内容回答

请用友好、专业的语气回答，并适当使用emoji让回答更生动。"""

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return f"抱歉，AI服务暂时不可用。错误信息: {str(e)}"
    
    def search_and_answer(self, question: str) -> str:
        """使用DeepSeek的知识进行网络搜索和回答"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构建网络搜索提示
        search_prompt = f"""你是一个专业的旅游顾问AI助手。用户询问了一个旅游相关的问题，但在本地知识库中没有找到相关信息。

请你利用你的知识和推理能力，为用户提供准确、实用的旅游建议。

用户问题：{question}

请提供：
1. 直接回答用户的问题
2. 相关的实用建议和推荐
3. 注意事项（如果适用）
4. 推荐的时间、地点或其他相关信息
5. 如果涉及具体价格、时间等信息，请提醒用户这些信息可能会变化

请确保回答准确、详细且实用，使用友好的语气并适当使用emoji。"""

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": search_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"]

            # 添加来源说明
            enhanced_answer = f"""🤖 **AI智能回答**（基于DeepSeek知识推理）

{answer}

---
💡 *此回答基于AI知识推理生成，建议出行前查询最新信息确认。*"""

            return enhanced_answer

        except Exception as e:
            logger.error(f"DeepSeek 网络搜索失败: {e}")
            return "抱歉，无法获取相关信息，请稍后重试。"

    @property
    def _llm_type(self) -> str:
        return "deepseek"

# 全局变量
vectorstore = None
qa_chain = None

def initialize_rag_system():
    """初始化RAG系统"""
    global vectorstore, qa_chain

    try:
        # 向量数据库路径 - 从环境变量读取
        vectorstore_path = os.getenv("VECTORSTORE_PATH", "../vectorstores")
        if not os.path.isabs(vectorstore_path):
            vectorstore_path = os.path.join(os.path.dirname(__file__), vectorstore_path)
        
        # 初始化嵌入模型 - 支持配置系统
        logger.info("初始化嵌入模型...")

        try:
            if EMBEDDING_CONFIG_AVAILABLE:
                # 使用配置系统
                embeddings = create_embedding_instance()
                status = get_current_model_status()
                logger.info(f"✅ 使用配置系统初始化嵌入模型: {status['model_info']['name']}")
            else:
                # 使用环境变量配置
                embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
                embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")

                logger.info(f"使用环境变量配置: {embedding_model} (提供商: {embedding_provider})")

                if embedding_provider.lower() == "ollama":
                    # 添加重试机制和更好的错误处理
                    import time
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            embeddings = OllamaEmbeddings(
                                model=embedding_model,
                                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                            )
                            # 测试嵌入功能
                            test_embedding = embeddings.embed_query("测试")
                            logger.info(f"✅ Ollama嵌入模型测试成功，维度: {len(test_embedding)}")
                            break
                        except Exception as e:
                            logger.warning(f"Ollama嵌入模型尝试 {attempt + 1}/{max_retries} 失败: {e}")
                            if attempt < max_retries - 1:
                                logger.info("等待5秒后重试...")
                                time.sleep(5)
                            else:
                                raise e

                elif embedding_provider.lower() == "siliconflow":
                    # 使用 SiliconFlow API
                    try:
                        from backend.embedding_models import create_siliconflow_embeddings
                    except ImportError:
                        from embedding_models import create_siliconflow_embeddings
                    embeddings = create_siliconflow_embeddings(embedding_model)

                elif embedding_provider.lower() == "huggingface":
                    from langchain_huggingface import HuggingFaceEmbeddings
                    embeddings = HuggingFaceEmbeddings(
                        model_name=embedding_model,
                        model_kwargs={'device': 'cpu'}
                    )
                else:
                    logger.warning(f"不支持的嵌入模型提供商: {embedding_provider}，使用默认Ollama")
                    embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

                logger.info(f"✅ 嵌入模型初始化成功: {embedding_model}")

        except Exception as e:
            logger.error(f"嵌入模型初始化失败: {e}")
            # 回退到默认配置
            logger.info("回退到默认嵌入模型配置")
            embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

        if embeddings is None:
            raise Exception("嵌入模型初始化失败")
        
        # 加载向量数据库
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embeddings
        )
        
        # 初始化LLM
        llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
        
        # 创建检索QA链
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        
        logger.info("RAG系统初始化成功")
        
    except Exception as e:
        logger.error(f"RAG系统初始化失败: {e}")
        raise e

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化RAG系统"""
    initialize_rag_system()

@app.get("/")
async def root():
    """健康检查接口"""
    return {"message": "RAG Knowledge Base API is running"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "vectorstore_initialized": vectorstore is not None,
        "qa_chain_initialized": qa_chain is not None
    }

def is_answer_insufficient(answer: str, sources: List[str]) -> bool:
    """判断知识库回答是否不充分"""
    # 检查回答质量的指标
    insufficient_indicators = [
        "抱歉，我无法",
        "没有找到相关信息",
        "不在我的知识库中",
        "无法提供",
        "不清楚",
        "不知道",
        "没有相关内容",
        "无法回答"
    ]

    # 检查回答长度
    if len(answer.strip()) < 50:
        return True

    # 检查是否包含不充分的指标
    for indicator in insufficient_indicators:
        if indicator in answer:
            return True

    # 检查是否有有效的源文档
    if not sources or len(sources) == 0:
        return True

    return False

@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """增强的查询知识库接口 - 支持知识库+网络搜索"""
    if not qa_chain:
        raise HTTPException(status_code=500, detail="RAG系统未初始化")

    try:
        # 1. 首先尝试知识库查询
        logger.info(f"查询知识库: {request.question}")
        result = qa_chain({"query": request.question})

        # 提取源文档
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                    sources.append(doc.metadata['source'])
                else:
                    sources.append("旅游攻略知识库")

        answer = result["result"]

        # 2. 判断知识库回答是否充分
        if is_answer_insufficient(answer, sources):
            logger.info("知识库回答不充分，启用网络搜索")

            # 使用DeepSeek进行网络搜索
            llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
            network_answer = llm.search_and_answer(request.question)

            # 合并回答
            combined_answer = f"""📚 **知识库搜索结果**：
{answer}

{network_answer}"""

            return QueryResponse(
                answer=combined_answer,
                sources=sources + ["DeepSeek AI 网络搜索"],
                confidence=0.7  # 混合回答的置信度稍低
            )
        else:
            # 知识库回答充分，直接返回
            return QueryResponse(
                answer=answer,
                sources=sources,
                confidence=0.9  # 知识库回答的置信度较高
            )

    except Exception as e:
        logger.error(f"查询失败: {e}")

        # 如果知识库查询完全失败，尝试纯网络搜索
        try:
            logger.info("知识库查询失败，尝试纯网络搜索")
            llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
            network_answer = llm.search_and_answer(request.question)

            return QueryResponse(
                answer=network_answer,
                sources=["DeepSeek AI 网络搜索"],
                confidence=0.6  # 纯网络搜索的置信度
            )
        except Exception as network_error:
            logger.error(f"网络搜索也失败: {network_error}")
            raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.post("/search", response_model=QueryResponse)
async def network_search(request: QueryRequest):
    """纯网络搜索接口 - 直接使用DeepSeek进行搜索"""
    try:
        logger.info(f"执行网络搜索: {request.question}")

        llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
        answer = llm.search_and_answer(request.question)

        return QueryResponse(
            answer=answer,
            sources=["DeepSeek AI 网络搜索"],
            confidence=0.7
        )

    except Exception as e:
        logger.error(f"网络搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"网络搜索失败: {str(e)}")

@app.get("/vectorstore/info")
async def get_vectorstore_info():
    """获取向量数据库信息"""
    if not vectorstore:
        raise HTTPException(status_code=500, detail="向量数据库未初始化")

    try:
        # 获取文档数量
        collection = vectorstore._collection
        doc_count = collection.count()

        # 获取当前嵌入模型配置
        embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")

        # 根据提供商确定显示名称
        if embedding_provider == "siliconflow":
            embedding_display = "SiliconFlow Embedding"
        elif embedding_provider == "modelscope":
            embedding_display = f"ModelScope: {embedding_model}"
        elif embedding_provider == "huggingface_mirror":
            embedding_display = f"HF Mirror: {embedding_model}"
        else:
            embedding_display = embedding_model

        return {
            "document_count": doc_count,
            "status": "active",
            "embedding_model": embedding_display,
            "llm_model": "deepseek-chat"
        }
    except Exception as e:
        logger.error(f"获取向量数据库信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取信息失败: {str(e)}")

@app.post("/vectorstore/search")
async def search_vectorstore(request: QueryRequest):
    """直接搜索向量数据库（不使用LLM）"""
    if not vectorstore:
        raise HTTPException(status_code=500, detail="向量数据库未初始化")

    try:
        # 直接进行相似性搜索
        docs = vectorstore.similarity_search(
            request.question,
            k=request.top_k if hasattr(request, 'top_k') else 5
        )

        results = []
        for i, doc in enumerate(docs):
            results.append({
                "rank": i + 1,
                "content": doc.page_content,
                "metadata": doc.metadata if hasattr(doc, 'metadata') else {},
                "similarity_score": 0.8 - (i * 0.1)  # 模拟相似度分数
            })

        return {
            "query": request.question,
            "results": results,
            "total_found": len(results)
        }

    except Exception as e:
        logger.error(f"向量搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.get("/models/info")
async def get_models_info():
    """获取模型信息"""
    # 获取当前配置
    embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")

    # 根据模型名称和提供商推断显示名称
    embedding_name_map = {
        "nomic-embed-text:latest": "Nomic Embed Text",
        "all-minilm:l6-v2": "All MiniLM L6 v2",
        "BAAI/bge-large-zh-v1.5": "BGE Large Chinese v1.5",
        "BAAI/bge-small-zh-v1.5": "BGE Small Chinese v1.5",
        "AI-ModelScope/bge-small-zh": "BGE Small Chinese (ModelScope)",
        "sentence-transformers/all-MiniLM-L6-v2": "Sentence Transformers",
        "damo/nlp_corom_sentence-embedding_chinese-base": "Text2Vec Base Chinese"
    }

    # 根据提供商确定显示名称
    if embedding_provider == "siliconflow":
        embedding_name = "SiliconFlow Embedding"
        provider_display = "SiliconFlow"
    elif embedding_provider == "modelscope":
        embedding_name = embedding_name_map.get(embedding_model, f"ModelScope: {embedding_model}")
        provider_display = "ModelScope"
    elif embedding_provider == "huggingface_mirror":
        embedding_name = embedding_name_map.get(embedding_model, f"HF Mirror: {embedding_model}")
        provider_display = "HuggingFace Mirror"
    else:
        embedding_name = embedding_name_map.get(embedding_model, embedding_model)
        provider_display = embedding_provider.title()

    return {
        "llm": {
            "name": "DeepSeek Chat",
            "provider": "DeepSeek",
            "model_id": "deepseek-chat",
            "status": "active"
        },
        "embedding": {
            "name": embedding_name,
            "provider": provider_display,
            "model_id": embedding_model,
            "status": "active"
        },
        "vectorstore": {
            "name": "ChromaDB",
            "type": "local",
            "status": "active"
        }
    }

# ==================== 微信小程序专用API ====================

@app.post("/wechat/query", response_model=WechatQueryResponse)
async def wechat_query(request: WechatQueryRequest):
    """微信小程序专用查询接口"""
    try:
        # 记录用户查询（可用于分析和优化）
        logger.info(f"微信用户查询 - OpenID: {request.openid}, 问题: {request.question}")

        # 如果有位置信息，可以结合位置提供更精准的建议
        enhanced_question = request.question
        if request.location and request.location.get('city'):
            enhanced_question = f"在{request.location['city']}，{request.question}"
            logger.info(f"结合位置信息: {request.location}")

        # 调用现有的查询逻辑
        if not qa_chain:
            return WechatQueryResponse(
                success=False,
                message="服务暂时不可用，请稍后重试",
                timestamp=datetime.now().isoformat()
            )

        # 执行查询
        result = qa_chain({"query": enhanced_question})

        # 提取源文档
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                    sources.append(doc.metadata['source'])
                else:
                    sources.append("旅游攻略知识库")

        answer = result["result"]

        # 判断是否需要网络搜索增强
        if is_answer_insufficient(answer, sources):
            logger.info("启用AI网络搜索增强")
            llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
            network_answer = llm.search_and_answer(enhanced_question)

            # 为小程序优化回答格式
            combined_answer = f"📚 知识库搜索：\n{answer}\n\n🤖 AI智能补充：\n{network_answer}"
            sources.append("DeepSeek AI 网络搜索")
            confidence = 0.7
        else:
            combined_answer = answer
            confidence = 0.9

        return WechatQueryResponse(
            success=True,
            message="查询成功",
            data={
                "answer": combined_answer,
                "sources": sources,
                "confidence": confidence,
                "has_location": bool(request.location),
                "enhanced_with_ai": is_answer_insufficient(result["result"], sources)
            },
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"微信小程序查询失败: {e}")

        # 尝试纯AI搜索作为备选
        try:
            llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
            fallback_answer = llm.search_and_answer(enhanced_question)

            return WechatQueryResponse(
                success=True,
                message="使用AI智能搜索回答",
                data={
                    "answer": fallback_answer,
                    "sources": ["DeepSeek AI 智能搜索"],
                    "confidence": 0.6,
                    "has_location": bool(request.location),
                    "enhanced_with_ai": True,
                    "fallback_mode": True
                },
                timestamp=datetime.now().isoformat()
            )
        except Exception as fallback_error:
            logger.error(f"备选AI搜索也失败: {fallback_error}")
            return WechatQueryResponse(
                success=False,
                message="服务暂时不可用，请稍后重试",
                timestamp=datetime.now().isoformat()
            )

@app.get("/wechat/health")
async def wechat_health_check():
    """微信小程序健康检查接口"""
    try:
        # 检查系统状态
        vectorstore_status = vectorstore is not None
        qa_chain_status = qa_chain is not None

        # 获取文档数量
        doc_count = 0
        if vectorstore:
            try:
                collection = vectorstore._collection
                doc_count = collection.count()
            except:
                pass

        return WechatQueryResponse(
            success=True,
            message="系统运行正常",
            data={
                "status": "healthy",
                "vectorstore_ready": vectorstore_status,
                "qa_chain_ready": qa_chain_status,
                "document_count": doc_count,
                "features": {
                    "knowledge_base": True,
                    "ai_search": True,
                    "location_aware": True,
                    "voice_support": True
                }
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return WechatQueryResponse(
            success=False,
            message="系统检查失败",
            timestamp=datetime.now().isoformat()
        )

if __name__ == "__main__":
    import uvicorn

    # 从环境变量读取服务器配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
