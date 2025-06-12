# RAG AI PowerShell 部署脚本
Write-Host "🐳 RAG旅游助手 Docker部署脚本" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# 检查Docker是否安装
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker未安装，请先安装Docker Desktop" -ForegroundColor Red
    Write-Host "下载地址: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查Docker Compose
try {
    $composeVersion = docker compose version
    Write-Host "✅ Docker Compose可用: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose不可用" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 设置API密钥
$apiKey = Read-Host "请输入DeepSeek API密钥 (可选，直接回车跳过)"
if ($apiKey) {
    "DEEPSEEK_API_KEY=$apiKey" | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ API密钥已设置" -ForegroundColor Green
} else {
    Write-Host "⚠️ 未设置API密钥，AI搜索功能将不可用" -ForegroundColor Yellow
}

# 创建必要目录
if (!(Test-Path "..\vectorstores")) {
    New-Item -ItemType Directory -Path "..\vectorstores" -Force
    Write-Host "📁 创建向量数据库目录" -ForegroundColor Blue
}

if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force
    Write-Host "📁 创建日志目录" -ForegroundColor Blue
}

# 显示部署选项
Write-Host ""
Write-Host "📋 部署选项:" -ForegroundColor Cyan
Write-Host "1. 仅启动API服务 (端口8000)" -ForegroundColor White
Write-Host "2. 启动API + Nginx (端口80)" -ForegroundColor White
Write-Host "3. 重新构建并启动" -ForegroundColor White
Write-Host "4. 停止服务" -ForegroundColor White
Write-Host "5. 查看日志" -ForegroundColor White
Write-Host "6. 查看服务状态" -ForegroundColor White

$choice = Read-Host "请选择 (1-6)"

switch ($choice) {
    "1" {
        Write-Host "🚀 启动API服务..." -ForegroundColor Green
        docker compose up -d rag-api
        $checkStatus = $true
    }
    "2" {
        Write-Host "🚀 启动完整服务..." -ForegroundColor Green
        docker compose up -d
        $checkStatus = $true
    }
    "3" {
        Write-Host "🔨 重新构建并启动..." -ForegroundColor Green
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        $checkStatus = $true
    }
    "4" {
        Write-Host "🛑 停止服务..." -ForegroundColor Red
        docker compose down
        Write-Host "✅ 服务已停止" -ForegroundColor Green
        $checkStatus = $false
    }
    "5" {
        Write-Host "📋 查看日志..." -ForegroundColor Blue
        docker compose logs -f rag-api
        $checkStatus = $false
    }
    "6" {
        Write-Host "📊 服务状态:" -ForegroundColor Blue
        docker compose ps
        Write-Host ""
        Write-Host "🔍 健康检查:" -ForegroundColor Blue
        try {
            $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
            Write-Host "✅ API服务正常运行" -ForegroundColor Green
        } catch {
            Write-Host "❌ API服务不可用" -ForegroundColor Red
        }
        $checkStatus = $false
    }
    default {
        Write-Host "❌ 无效选择" -ForegroundColor Red
        $checkStatus = $false
    }
}

# 检查服务状态
if ($checkStatus) {
    Write-Host ""
    Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10

    Write-Host "📊 服务状态:" -ForegroundColor Blue
    docker compose ps

    Write-Host ""
    Write-Host "🔍 健康检查:" -ForegroundColor Blue
    try {
        $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10
        Write-Host "✅ API服务正常运行" -ForegroundColor Green
        Write-Host "📍 API地址: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "📖 API文档: http://localhost:8000/docs" -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "🌐 内网穿透选项:" -ForegroundColor Magenta
        Write-Host "1. 使用ngrok: ngrok http 8000" -ForegroundColor White
        Write-Host "2. 使用cpolar: cpolar http 8000" -ForegroundColor White
        Write-Host "3. 使用frp: 配置frp客户端" -ForegroundColor White
    } catch {
        Write-Host "❌ API服务启动失败，请检查日志" -ForegroundColor Red
        Write-Host "查看日志命令: docker compose logs rag-api" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📚 常用命令:" -ForegroundColor Cyan
Write-Host "  启动服务: docker compose up -d" -ForegroundColor White
Write-Host "  停止服务: docker compose down" -ForegroundColor White
Write-Host "  查看日志: docker compose logs -f rag-api" -ForegroundColor White
Write-Host "  重启服务: docker compose restart rag-api" -ForegroundColor White
Write-Host "  查看状态: docker compose ps" -ForegroundColor White

Write-Host ""
Read-Host "按回车键退出"
