from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import time
from collections import defaultdict

# 导入原有的RAG系统
from main import (
    initialize_rag_system,
    DeepSeekLLM, is_answer_insufficient, DEEPSEEK_API_KEY
)
import main  # 导入模块以便访问全局变量

# 加载部署配置
sys.path.append(str(Path(__file__).parent.parent))
from deploy_config import config, API_KEYS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Travel Assistant Public API",
    description="智能旅游助手公开API接口",
    version="1.0.0",
    docs_url="/docs" if config.DEBUG else None,  # 生产环境可关闭文档
    redoc_url="/redoc" if config.DEBUG else None
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# API密钥验证
security = HTTPBearer(auto_error=False)  # 开发模式下不自动报错

# 请求频率限制
request_counts = defaultdict(list)

def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """验证API密钥"""
    if not config.REQUIRE_API_KEY:
        return {"name": "开发用户", "permissions": ["query", "health"]}

    if not credentials:
        raise HTTPException(status_code=401, detail="需要API密钥")

    api_key = credentials.credentials
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="无效的API密钥")

    return API_KEYS[api_key]

def check_rate_limit(api_key: str, user_info: dict):
    """检查请求频率限制"""
    now = time.time()
    hour_ago = now - 3600
    
    # 清理过期记录
    request_counts[api_key] = [req_time for req_time in request_counts[api_key] if req_time > hour_ago]
    
    # 检查频率限制
    rate_limit = user_info.get("rate_limit", "100/hour")
    max_requests = int(rate_limit.split("/")[0])
    
    if len(request_counts[api_key]) >= max_requests:
        raise HTTPException(status_code=429, detail="请求频率超限，请稍后重试")
    
    # 记录当前请求
    request_counts[api_key].append(now)

# 请求模型
class PublicQueryRequest(BaseModel):
    question: str
    location: Optional[Dict] = None
    user_id: Optional[str] = None
    top_k: Optional[int] = 3
    include_sources: Optional[bool] = True
    enable_ai_search: Optional[bool] = True

class PublicQueryResponse(BaseModel):
    success: bool
    message: str
    data: Dict
    usage: Dict
    timestamp: str

# API接口

@app.get("/")
async def root():
    """API根路径"""
    return {
        "service": "RAG Travel Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if config.DEBUG else "请联系管理员获取文档",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "vectorstore_ready": main.vectorstore is not None,
        "qa_chain_ready": main.qa_chain is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/query", response_model=PublicQueryResponse)
async def public_query(
    request: PublicQueryRequest,
    user_info: dict = Depends(verify_api_key)
):
    """公开查询接口"""
    
    # 检查权限
    if "query" not in user_info.get("permissions", []):
        raise HTTPException(status_code=403, detail="无查询权限")
    
    # 检查频率限制
    api_key = request.user_id or "anonymous"
    check_rate_limit(api_key, user_info)
    
    try:
        # 参数验证
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        if len(request.question) > 500:
            raise HTTPException(status_code=400, detail="问题长度不能超过500字符")
        
        logger.info(f"公开API查询 - 用户: {user_info['name']}, 问题: {request.question}")
        
        # 构建查询
        enhanced_question = request.question.strip()
        if request.location and request.location.get('city'):
            enhanced_question = f"在{request.location['city']}，{enhanced_question}"
        
        # 执行查询
        if not main.qa_chain:
            raise HTTPException(status_code=500, detail="RAG系统未初始化")

        result = main.qa_chain({"query": enhanced_question})
        
        # 提取源文档
        sources = []
        if request.include_sources and "source_documents" in result:
            for doc in result["source_documents"]:
                if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                    sources.append(doc.metadata['source'])
                else:
                    sources.append("旅游攻略知识库")
        
        answer = result["result"]
        confidence = 0.9
        enhanced_with_ai = False
        
        # AI搜索增强
        if request.enable_ai_search and is_answer_insufficient(answer, sources):
            logger.info("启用AI搜索增强")
            llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
            network_answer = llm.search_and_answer(enhanced_question)
            
            answer = f"📚 **知识库回答**：\n{answer}\n\n🤖 **AI智能补充**：\n{network_answer}"
            sources.append("DeepSeek AI 网络搜索")
            confidence = 0.7
            enhanced_with_ai = True
        
        # 构建响应
        response_data = {
            "answer": answer,
            "confidence": confidence,
            "enhanced_with_ai": enhanced_with_ai
        }
        
        if request.include_sources:
            response_data["sources"] = sources
        
        if request.location:
            response_data["location_used"] = True
        
        # 使用统计
        usage_stats = {
            "question_length": len(request.question),
            "answer_length": len(answer),
            "sources_count": len(sources),
            "processing_time": "< 1s"
        }
        
        return PublicQueryResponse(
            success=True,
            message="查询成功",
            data=response_data,
            usage=usage_stats,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"公开API查询失败: {e}")
        
        # 尝试AI搜索作为备选
        if request.enable_ai_search:
            try:
                llm = DeepSeekLLM(api_key=DEEPSEEK_API_KEY)
                fallback_answer = llm.search_and_answer(request.question)
                
                return PublicQueryResponse(
                    success=True,
                    message="使用AI搜索回答",
                    data={
                        "answer": fallback_answer,
                        "sources": ["DeepSeek AI 搜索"],
                        "confidence": 0.6,
                        "enhanced_with_ai": True,
                        "fallback_mode": True
                    },
                    usage={"fallback": True},
                    timestamp=datetime.now().isoformat()
                )
            except Exception as fallback_error:
                logger.error(f"AI搜索备选也失败: {fallback_error}")
        
        raise HTTPException(status_code=500, detail="服务暂时不可用")

@app.get("/api/v1/info")
async def api_info(user_info: dict = Depends(verify_api_key)):
    """获取API信息"""
    return {
        "user": user_info["name"],
        "permissions": user_info.get("permissions", []),
        "rate_limit": user_info.get("rate_limit", "100/hour"),
        "endpoints": {
            "query": "/api/v1/query",
            "health": "/health",
            "info": "/api/v1/info"
        },
        "timestamp": datetime.now().isoformat()
    }

# 启动时初始化
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化RAG系统"""
    logger.info("初始化公开API服务...")
    initialize_rag_system()

    # 确保全局变量已正确设置
    if main.vectorstore is None or main.qa_chain is None:
        logger.warning("全局变量未正确设置，重新初始化...")
        initialize_rag_system()

    logger.info(f"向量数据库状态: {main.vectorstore is not None}")
    logger.info(f"QA链状态: {main.qa_chain is not None}")
    logger.info("公开API服务启动完成")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config.HOST, 
        port=config.PORT,
        log_level="info"
    )
