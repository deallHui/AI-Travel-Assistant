#!/bin/bash

# RAG AI Docker启动脚本

echo "🚀 启动RAG旅游助手API服务..."

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  警告: DEEPSEEK_API_KEY 未设置，AI搜索功能将不可用"
fi

# 检查向量数据库
if [ ! -d "/app/vectorstores" ] || [ -z "$(ls -A /app/vectorstores)" ]; then
    echo "⚠️  警告: 向量数据库目录为空，请确保已初始化知识库"
fi

# 设置默认环境
export DEPLOY_ENV=${DEPLOY_ENV:-production}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}

echo "📋 配置信息:"
echo "   - 环境: $DEPLOY_ENV"
echo "   - 主机: $HOST"
echo "   - 端口: $PORT"
echo "   - 工作目录: $(pwd)"

# 启动服务
if [ "$DEPLOY_ENV" = "development" ]; then
    echo "🔧 开发模式启动（包含微信API）..."
    cd backend && python -m uvicorn main:app --host $HOST --port $PORT --reload
else
    echo "🏭 生产模式启动（包含微信API）..."
    # 使用Gunicorn启动，支持多进程
    exec gunicorn backend.main:app \
        --bind $HOST:$PORT \
        --workers 2 \
        --worker-class uvicorn.workers.UvicornWorker \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 60 \
        --access-logfile /app/logs/access.log \
        --error-logfile /app/logs/error.log \
        --log-level info
fi
