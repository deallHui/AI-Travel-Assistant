#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG项目完整启动脚本
同时启动前端和后端服务
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def check_dependencies():
    """检查项目依赖"""
    print("🔍 检查项目依赖...")
    
    # 检查Python依赖
    try:
        import fastapi
        import uvicorn
        import langchain_chroma
        import langchain_ollama
        print("✅ Python后端依赖检查通过")
    except ImportError as e:
        print(f"❌ Python依赖缺失: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 检查Node.js和npm
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
        else:
            print("❌ Node.js未安装")
            return False
            
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm版本: {result.stdout.strip()}")
        else:
            print("❌ npm未安装")
            return False
            
    except FileNotFoundError:
        print("❌ Node.js或npm未安装")
        return False
    
    # 检查前端依赖
    frontend_dir = Path("frontend")
    if not (frontend_dir / "node_modules").exists():
        print("⚠️ 前端依赖未安装，正在安装...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            print("✅ 前端依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 前端依赖安装失败")
            return False
    else:
        print("✅ 前端依赖检查通过")
    
    return True

def check_ollama():
    """检查Ollama服务"""
    print("🔍 检查Ollama服务...")
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            if 'nomic-embed-text' in result.stdout:
                print("✅ Ollama服务正常，nomic-embed-text模型已安装")
                return True
            else:
                print("⚠️ nomic-embed-text模型未安装")
                print("正在下载模型...")
                subprocess.run(['ollama', 'pull', 'nomic-embed-text'], check=True)
                print("✅ 模型下载完成")
                return True
        else:
            print("❌ Ollama服务未运行")
            return False
    except FileNotFoundError:
        print("❌ Ollama未安装")
        return False
    except subprocess.CalledProcessError:
        print("❌ Ollama服务检查失败")
        return False

def check_vectorstore():
    """检查向量数据库"""
    vectorstore_path = Path("vectorstores")
    if vectorstore_path.exists() and any(vectorstore_path.iterdir()):
        print("✅ 向量数据库已存在")
        return True
    else:
        print("⚠️ 向量数据库不存在，正在构建...")
        try:
            subprocess.run([sys.executable, 'build_travel_vectordb.py'], check=True)
            print("✅ 向量数据库构建完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 向量数据库构建失败")
            return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    try:
        os.chdir("backend")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        os.chdir("..")
        return process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("🚀 启动前端服务...")
    try:
        process = subprocess.Popen([
            'npm', 'run', 'dev'
        ], cwd="frontend")
        return process
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None

def wait_for_service(url, service_name, timeout=30):
    """等待服务启动"""
    import requests
    print(f"⏳ 等待{service_name}服务启动...")
    
    for i in range(timeout):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print(f"✅ {service_name}服务已启动")
                return True
        except:
            pass
        time.sleep(1)
    
    print(f"❌ {service_name}服务启动超时")
    return False

def open_browser():
    """打开浏览器"""
    import webbrowser
    print("🌐 打开浏览器...")
    webbrowser.open('http://localhost:5173')

def signal_handler(sig, frame):
    """信号处理器"""
    print("\n🛑 正在关闭服务...")
    sys.exit(0)

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 RAG知识库问答系统启动器")
    print("=" * 60)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请解决依赖问题后重试")
        sys.exit(1)
    
    # 检查Ollama
    if not check_ollama():
        print("❌ Ollama检查失败，请安装并启动Ollama服务")
        sys.exit(1)
    
    # 检查向量数据库
    if not check_vectorstore():
        print("❌ 向量数据库检查失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎯 开始启动服务...")
    print("=" * 60)
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        print("❌ 后端启动失败")
        sys.exit(1)
    
    # 等待后端启动
    if not wait_for_service("http://localhost:8000/health", "后端"):
        backend_process.terminate()
        sys.exit(1)
    
    # 启动前端
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ 前端启动失败")
        backend_process.terminate()
        sys.exit(1)
    
    # 等待前端启动
    time.sleep(5)  # 给前端一些启动时间
    
    print("\n" + "=" * 60)
    print("🎉 服务启动成功！")
    print("=" * 60)
    print("📱 前端地址: http://localhost:5173")
    print("🔧 后端地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("=" * 60)
    print("按 Ctrl+C 停止所有服务")
    print("=" * 60)
    
    # 打开浏览器
    threading.Timer(2.0, open_browser).start()
    
    try:
        # 等待进程结束
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在关闭服务...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # 等待进程结束
        backend_process.wait()
        frontend_process.wait()
        
        print("✅ 所有服务已关闭")

if __name__ == "__main__":
    main()
