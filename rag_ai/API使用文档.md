# 🌐 RAG旅游助手 - 公开API使用文档

## 📋 概述

RAG旅游助手提供RESTful API接口，支持第三方应用集成智能旅游问答功能。

### 🔗 API基础信息

- **基础URL**: `https://your-domain.com/api/v1`
- **认证方式**: Bearer Token (API Key)
- **数据格式**: JSON
- **字符编码**: UTF-8

## 🔑 API密钥申请

### 获取API密钥
1. 联系管理员申请API密钥
2. 提供应用名称和预期使用量
3. 获得API密钥和使用权限

### 密钥类型
- **演示版** (demo_key_123): 50次/小时，基础功能
- **标准版**: 200次/小时，完整功能
- **高级版**: 1000次/小时，优先支持

## 📡 API接口

### 1. 健康检查
```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "vectorstore_ready": true,
  "qa_chain_ready": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 智能问答
```http
POST /api/v1/query
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**请求参数**:
```json
{
  "question": "北京有什么好玩的景点？",
  "location": {
    "city": "北京",
    "latitude": 39.9042,
    "longitude": 116.4074
  },
  "user_id": "user_123",
  "top_k": 3,
  "include_sources": true,
  "enable_ai_search": true
}
```

**参数说明**:
- `question` (必填): 用户问题，最大500字符
- `location` (可选): 用户位置信息
- `user_id` (可选): 用户标识，用于统计
- `top_k` (可选): 检索结果数量，默认3
- `include_sources` (可选): 是否包含信息来源，默认true
- `enable_ai_search` (可选): 是否启用AI搜索增强，默认true

**响应示例**:
```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "answer": "🏛️ **北京必去景点推荐**\n\n**历史文化类：**\n• 故宫博物院 - 明清皇宫，世界文化遗产\n• 天坛公园 - 明清皇帝祭天的场所\n• 颐和园 - 中国古典园林艺术的杰作",
    "confidence": 0.9,
    "enhanced_with_ai": false,
    "sources": ["旅游攻略知识库", "北京景点指南"],
    "location_used": true
  },
  "usage": {
    "question_length": 12,
    "answer_length": 156,
    "sources_count": 2,
    "processing_time": "< 1s"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3. API信息查询
```http
GET /api/v1/info
Authorization: Bearer YOUR_API_KEY
```

**响应示例**:
```json
{
  "user": "演示用户",
  "permissions": ["query", "health"],
  "rate_limit": "50/hour",
  "endpoints": {
    "query": "/api/v1/query",
    "health": "/health",
    "info": "/api/v1/info"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 💻 代码示例

### Python示例
```python
import requests
import json

# API配置
API_BASE_URL = "https://your-domain.com"
API_KEY = "your_api_key_here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 发送查询请求
def query_travel_assistant(question, location=None):
    url = f"{API_BASE_URL}/api/v1/query"
    
    data = {
        "question": question,
        "location": location,
        "include_sources": True,
        "enable_ai_search": True
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            return result["data"]["answer"]
        else:
            return f"查询失败: {result['message']}"
    else:
        return f"请求失败: {response.status_code}"

# 使用示例
answer = query_travel_assistant(
    question="推荐一些上海的特色美食",
    location={"city": "上海"}
)
print(answer)
```

### JavaScript示例
```javascript
// API配置
const API_BASE_URL = 'https://your-domain.com';
const API_KEY = 'your_api_key_here';

// 查询函数
async function queryTravelAssistant(question, location = null) {
    const url = `${API_BASE_URL}/api/v1/query`;
    
    const data = {
        question: question,
        location: location,
        include_sources: true,
        enable_ai_search: true
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            return result.data.answer;
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('查询失败:', error);
        return '查询失败，请稍后重试';
    }
}

// 使用示例
queryTravelAssistant('杭州西湖有什么好玩的？', {city: '杭州'})
    .then(answer => console.log(answer))
    .catch(error => console.error(error));
```

### cURL示例
```bash
# 健康检查
curl -X GET "https://your-domain.com/health"

# 智能问答
curl -X POST "https://your-domain.com/api/v1/query" \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "三亚有什么特色美食？",
    "location": {"city": "三亚"},
    "include_sources": true,
    "enable_ai_search": true
  }'
```

## ⚠️ 错误处理

### 常见错误码
- `400`: 请求参数错误
- `401`: API密钥无效
- `403`: 权限不足
- `429`: 请求频率超限
- `500`: 服务器内部错误

### 错误响应格式
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📊 使用限制

### 频率限制
- **演示版**: 50次/小时
- **标准版**: 200次/小时  
- **高级版**: 1000次/小时

### 内容限制
- 问题长度: 最大500字符
- 响应时间: 通常 < 5秒
- 并发请求: 最大10个/用户

## 🔧 最佳实践

### 1. 错误重试
```python
import time
import random

def query_with_retry(question, max_retries=3):
    for attempt in range(max_retries):
        try:
            return query_travel_assistant(question)
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise e
```

### 2. 缓存结果
```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(question):
    return query_travel_assistant(question)
```

### 3. 批量处理
```python
def batch_query(questions, delay=1):
    results = []
    for question in questions:
        result = query_travel_assistant(question)
        results.append(result)
        time.sleep(delay)  # 避免频率限制
    return results
```

## 📞 技术支持

- **文档**: https://your-domain.com/docs
- **邮箱**: api-support@your-domain.com
- **QQ群**: 123456789
- **工作时间**: 周一至周五 9:00-18:00

## 📝 更新日志

### v1.0.0 (2024-01-01)
- 🎉 首次发布
- ✅ 支持智能问答
- ✅ 支持位置感知
- ✅ 支持AI搜索增强
- ✅ 支持API密钥认证

---

**开始使用RAG旅游助手API，为您的应用添加智能旅游问答功能！** 🚀
