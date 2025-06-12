# 🐳 Docker快速部署指南

## 🎯 5分钟快速部署

### 前置要求
- ✅ 安装Docker Desktop
- ✅ 确保RAG AI系统本地运行正常
- ✅ 有DeepSeek API密钥（可选）

### 🚀 一键部署

#### 1. 进入Docker目录
```bash
cd rag_ai/docker
```

#### 2. 运行部署脚本
```bash
# Windows用户
deploy.bat

# 或者手动执行
docker compose up -d rag-api
```

#### 3. 检查服务状态
```bash
# 查看服务状态
docker compose ps

# 健康检查
curl http://localhost:8000/health
```

#### 4. 启动内网穿透
```bash
# 使用ngrok（推荐）
ngrok http 8000

# 或使用cpolar
cpolar http 8000
```

## 💰 成本对比方案

### 方案A：完全免费（推荐新手）
- **成本**: ¥0/月
- **配置**: Docker + ngrok免费版
- **限制**: 随机域名，重启后变化
- **适合**: 个人测试、学习使用

### 方案B：低成本稳定（推荐小团队）
- **成本**: ¥19/月
- **配置**: Docker + cpolar认证版
- **优势**: 固定域名，国内访问快
- **适合**: 小规模商用

### 方案C：专业版（推荐商用）
- **成本**: ¥35/月
- **配置**: Docker + ngrok付费版
- **优势**: 全球稳定，专业支持
- **适合**: 正式商用项目

## 📋 详细部署步骤

### 1. 准备Docker环境

#### 安装Docker Desktop
1. 下载：https://www.docker.com/products/docker-desktop
2. 安装并启动Docker Desktop
3. 验证安装：`docker --version`

#### 配置Docker（可选优化）
```bash
# 配置镜像加速（国内用户）
# 在Docker Desktop设置中添加镜像源：
# https://registry.docker-cn.com
# https://docker.mirrors.ustc.edu.cn
```

### 2. 构建和启动服务

#### 方式1：使用docker-compose（推荐）
```bash
cd rag_ai/docker

# 设置环境变量（可选）
echo DEEPSEEK_API_KEY=your_api_key > .env

# 启动服务
docker compose up -d rag-api

# 查看日志
docker compose logs -f rag-api
```

#### 方式2：直接使用Docker
```bash
cd rag_ai

# 构建镜像
docker build -f docker/Dockerfile -t rag-travel-api .

# 运行容器
docker run -d \
  --name rag-api \
  -p 8000:8000 \
  -v $(pwd)/vectorstores:/app/vectorstores:ro \
  -e DEEPSEEK_API_KEY=your_api_key \
  rag-travel-api
```

### 3. 配置内网穿透

#### 选项1：ngrok（全球推荐）
```bash
# 1. 注册ngrok账号: https://ngrok.com/
# 2. 下载并安装ngrok
# 3. 设置认证token
ngrok config add-authtoken YOUR_TOKEN

# 4. 启动隧道
ngrok http 8000

# 输出示例：
# Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

#### 选项2：cpolar（国内推荐）
```bash
# 1. 注册cpolar账号: https://www.cpolar.com/
# 2. 下载并安装cpolar
# 3. 启动隧道
cpolar http 8000

# 输出示例：
# https://abc123.cpolar.cn -> http://localhost:8000
```

### 4. 测试API服务

#### 健康检查
```bash
curl https://your-tunnel-url.ngrok.io/health
```

#### API测试
```bash
curl -X POST "https://your-tunnel-url.ngrok.io/api/v1/query" \
  -H "Authorization: Bearer demo_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "北京有什么好玩的景点？",
    "include_sources": true
  }'
```

## 🔧 常用管理命令

### Docker服务管理
```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart rag-api

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f rag-api

# 进入容器
docker compose exec rag-api bash
```

### 服务监控
```bash
# 查看资源使用
docker stats rag-travel-api

# 查看容器信息
docker inspect rag-travel-api

# 查看端口映射
docker port rag-travel-api
```

## 🛠️ 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看详细日志
docker compose logs rag-api

# 常见原因：
# - 端口被占用：修改docker-compose.yml中的端口
# - 向量数据库路径错误：检查vectorstores目录
# - 依赖安装失败：重新构建镜像
```

#### 2. API无法访问
```bash
# 检查容器状态
docker compose ps

# 检查端口映射
netstat -an | findstr 8000

# 检查防火墙设置
# Windows: 允许Docker Desktop通过防火墙
```

#### 3. 内网穿透连接失败
```bash
# ngrok问题：
# - 检查认证token是否正确
# - 确认账号是否激活
# - 尝试重新启动ngrok

# cpolar问题：
# - 检查客户端是否登录
# - 确认隧道配置是否正确
```

### 性能优化

#### 1. 调整Docker资源
```yaml
# 在docker-compose.yml中添加资源限制
services:
  rag-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

#### 2. 优化Gunicorn配置
```bash
# 根据CPU核心数调整worker数量
# 在start.sh中修改：
--workers 4  # 建议为CPU核心数
```

## 📊 监控和维护

### 1. 自动重启脚本
```batch
@echo off
:monitor
timeout /t 60
curl -s http://localhost:8000/health >nul || (
    echo Service down, restarting...
    docker compose restart rag-api
    timeout /t 30
)
goto monitor
```

### 2. 日志轮转
```bash
# 定期清理日志
docker system prune -f
docker compose logs --tail=1000 rag-api > latest.log
```

### 3. 备份脚本
```bash
# 备份向量数据库
tar -czf vectorstore_backup_$(date +%Y%m%d).tar.gz vectorstores/

# 备份配置文件
cp docker-compose.yml docker-compose.yml.bak
```

## 🎯 生产环境建议

### 1. 安全配置
- 使用强密码的API密钥
- 配置IP白名单
- 启用HTTPS（通过内网穿透自动提供）
- 定期更新Docker镜像

### 2. 监控告警
- 设置服务健康检查
- 配置资源使用监控
- 设置异常告警通知

### 3. 备份策略
- 定期备份向量数据库
- 备份配置文件
- 记录API使用统计

---

## 🎉 部署完成！

现在您的RAG AI服务已经通过Docker部署并可以通过公网访问了！

### 📍 访问信息
- **本地API**: http://localhost:8000
- **公网API**: https://your-tunnel-url
- **API文档**: https://your-tunnel-url/docs
- **健康检查**: https://your-tunnel-url/health

### 📞 分享给用户
将公网URL和API密钥分享给需要使用的开发者，他们就可以集成您的智能旅游助手API了！

**总成本：¥0-35/月，比云服务器便宜90%以上！** 💰✨
