"""
RAG旅游助手 Python SDK
简化API调用的客户端库
"""

import requests
import json
import time
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QueryResult:
    """查询结果数据类"""
    success: bool
    answer: str
    confidence: float
    sources: List[str]
    enhanced_with_ai: bool
    timestamp: str
    usage: Dict
    error_message: Optional[str] = None

class RAGTravelClient:
    """RAG旅游助手客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://your-domain.com"):
        """
        初始化客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'RAG-Travel-Python-SDK/1.0.0'
        })
    
    def health_check(self) -> Dict:
        """
        检查API服务健康状态
        
        Returns:
            服务状态信息
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def query(
        self,
        question: str,
        location: Optional[Dict] = None,
        user_id: Optional[str] = None,
        top_k: int = 3,
        include_sources: bool = True,
        enable_ai_search: bool = True,
        timeout: int = 30
    ) -> QueryResult:
        """
        发送查询请求
        
        Args:
            question: 用户问题
            location: 位置信息，格式: {"city": "北京", "latitude": 39.9, "longitude": 116.4}
            user_id: 用户标识
            top_k: 检索结果数量
            include_sources: 是否包含信息来源
            enable_ai_search: 是否启用AI搜索增强
            timeout: 请求超时时间（秒）
            
        Returns:
            QueryResult对象
        """
        url = f"{self.base_url}/api/v1/query"
        
        data = {
            "question": question,
            "location": location,
            "user_id": user_id,
            "top_k": top_k,
            "include_sources": include_sources,
            "enable_ai_search": enable_ai_search
        }
        
        try:
            response = self.session.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            
            if result["success"]:
                return QueryResult(
                    success=True,
                    answer=result["data"]["answer"],
                    confidence=result["data"].get("confidence", 0.0),
                    sources=result["data"].get("sources", []),
                    enhanced_with_ai=result["data"].get("enhanced_with_ai", False),
                    timestamp=result["timestamp"],
                    usage=result.get("usage", {})
                )
            else:
                return QueryResult(
                    success=False,
                    answer="",
                    confidence=0.0,
                    sources=[],
                    enhanced_with_ai=False,
                    timestamp=result.get("timestamp", ""),
                    usage={},
                    error_message=result.get("message", "未知错误")
                )
                
        except requests.RequestException as e:
            return QueryResult(
                success=False,
                answer="",
                confidence=0.0,
                sources=[],
                enhanced_with_ai=False,
                timestamp=datetime.now().isoformat(),
                usage={},
                error_message=f"请求失败: {str(e)}"
            )
    
    def get_api_info(self) -> Dict:
        """
        获取API信息
        
        Returns:
            API信息字典
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/info")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def batch_query(
        self,
        questions: List[str],
        location: Optional[Dict] = None,
        delay: float = 1.0,
        **kwargs
    ) -> List[QueryResult]:
        """
        批量查询
        
        Args:
            questions: 问题列表
            location: 位置信息
            delay: 请求间隔（秒）
            **kwargs: 其他查询参数
            
        Returns:
            查询结果列表
        """
        results = []
        
        for i, question in enumerate(questions):
            if i > 0:
                time.sleep(delay)
            
            result = self.query(question, location=location, **kwargs)
            results.append(result)
        
        return results
    
    def query_with_retry(
        self,
        question: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ) -> QueryResult:
        """
        带重试的查询
        
        Args:
            question: 用户问题
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
            **kwargs: 其他查询参数
            
        Returns:
            QueryResult对象
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            result = self.query(question, **kwargs)
            
            if result.success:
                return result
            
            last_error = result.error_message
            
            if attempt < max_retries:
                time.sleep(retry_delay * (2 ** attempt))  # 指数退避
        
        return QueryResult(
            success=False,
            answer="",
            confidence=0.0,
            sources=[],
            enhanced_with_ai=False,
            timestamp=datetime.now().isoformat(),
            usage={},
            error_message=f"重试{max_retries}次后仍失败: {last_error}"
        )

# 便捷函数
def create_client(api_key: str, base_url: str = "https://your-domain.com") -> RAGTravelClient:
    """创建客户端实例"""
    return RAGTravelClient(api_key, base_url)

def quick_query(api_key: str, question: str, **kwargs) -> str:
    """快速查询，直接返回答案文本"""
    client = create_client(api_key)
    result = client.query(question, **kwargs)
    
    if result.success:
        return result.answer
    else:
        return f"查询失败: {result.error_message}"

# 使用示例
if __name__ == "__main__":
    # 基础使用
    client = RAGTravelClient("your_api_key_here")
    
    # 健康检查
    health = client.health_check()
    print("服务状态:", health)
    
    # 简单查询
    result = client.query("北京有什么好玩的景点？")
    if result.success:
        print("回答:", result.answer)
        print("来源:", result.sources)
        print("置信度:", result.confidence)
    else:
        print("查询失败:", result.error_message)
    
    # 带位置的查询
    location = {"city": "上海", "latitude": 31.2304, "longitude": 121.4737}
    result = client.query("推荐一些特色美食", location=location)
    print("上海美食推荐:", result.answer)
    
    # 批量查询
    questions = [
        "杭州西湖有什么好玩的？",
        "三亚有什么特色美食？",
        "从北京到上海怎么去最方便？"
    ]
    
    results = client.batch_query(questions, delay=0.5)
    for i, result in enumerate(results):
        print(f"问题{i+1}: {questions[i]}")
        print(f"回答: {result.answer[:100]}...")
        print("---")
    
    # 带重试的查询
    result = client.query_with_retry("成都有什么必去的景点？", max_retries=2)
    print("成都景点:", result.answer)
    
    # 快速查询
    answer = quick_query("your_api_key_here", "西安有什么历史古迹？")
    print("西安古迹:", answer)
