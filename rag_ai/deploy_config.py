# 部署配置文件
import os
from pathlib import Path

class DeployConfig:
    """部署配置类"""
    
    def __init__(self, environment='production'):
        self.environment = environment
        self.setup_config()
    
    def setup_config(self):
        """设置配置"""
        if self.environment == 'production':
            self.setup_production()
        elif self.environment == 'development':
            self.setup_development()
    
    def setup_production(self):
        """生产环境配置"""
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8002"))
        self.DEBUG = False
        self.CORS_ORIGINS = [
            "https://your-domain.com",
            "https://api.your-domain.com",
            "*"  # 开发阶段可以使用，生产环境建议限制具体域名
        ]
        self.API_RATE_LIMIT = "100/hour"  # API调用频率限制
        self.REQUIRE_API_KEY = True  # 是否需要API密钥

    def setup_development(self):
        """开发环境配置"""
        self.HOST = os.getenv("HOST", "172.18.2.53")
        self.PORT = int(os.getenv("PORT", "8002"))
        self.DEBUG = True
        self.CORS_ORIGINS = ["*"]
        self.API_RATE_LIMIT = "1000/hour"
        self.REQUIRE_API_KEY = False

# 环境变量配置
DEPLOY_ENV = os.getenv("DEPLOY_ENV", "development")
config = DeployConfig(DEPLOY_ENV)

# API密钥管理
API_KEYS = {
    "demo_key_123": {
        "name": "演示用户",
        "rate_limit": "50/hour",
        "permissions": ["query", "health"]
    },
    "premium_key_456": {
        "name": "高级用户", 
        "rate_limit": "500/hour",
        "permissions": ["query", "health", "vectorstore"]
    }
}

# 服务器推荐配置
SERVER_REQUIREMENTS = {
    "minimum": {
        "cpu": "2核",
        "memory": "4GB",
        "storage": "20GB SSD",
        "bandwidth": "5Mbps"
    },
    "recommended": {
        "cpu": "4核",
        "memory": "8GB", 
        "storage": "50GB SSD",
        "bandwidth": "10Mbps"
    }
}

# 云服务商推荐
CLOUD_PROVIDERS = {
    "阿里云": {
        "url": "https://ecs.aliyun.com",
        "特点": "国内访问速度快，文档丰富",
        "推荐配置": "ECS通用型g6.large"
    },
    "腾讯云": {
        "url": "https://cloud.tencent.com",
        "特点": "与微信生态集成好",
        "推荐配置": "CVM标准型S5.MEDIUM4"
    },
    "华为云": {
        "url": "https://huaweicloud.com", 
        "特点": "AI服务丰富",
        "推荐配置": "ECS通用计算型c6.large.2"
    }
}
