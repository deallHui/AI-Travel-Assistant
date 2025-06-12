#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能旅游攻略问答系统启动脚本
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🧭 智能旅游攻略问答系统 v1.0                          ║
    ║                                                              ║
    ║        🌟 您的专属旅游助手                                   ║
    ║        📍 景点推荐 | 🏨 住宿建议 | 🍜 美食攻略              ║
    ║        🚗 交通指南 | 💰 预算规划 | 📅 行程安排              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_travel_data():
    """检查旅游攻略数据"""
    print("🗺️ 检查旅游攻略数据...")
    
    # 检查旅游攻略文件
    travel_file = Path("travel_guides_database.txt")
    if travel_file.exists():
        print("✅ 旅游攻略数据文件存在")
        
        # 显示文件信息
        file_size = travel_file.stat().st_size
        print(f"   📄 文件大小: {file_size / 1024:.1f} KB")
        
        # 简单统计内容
        try:
            with open(travel_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.split('\n'))
                chars = len(content)
                print(f"   📊 内容统计: {lines} 行, {chars} 字符")
        except Exception as e:
            print(f"   ⚠️ 读取文件时出错: {e}")
        
        return True
    else:
        print("❌ 旅游攻略数据文件不存在")
        print("   请确保 travel_guides_database.txt 文件存在")
        return False

def check_vectorstore():
    """检查向量数据库"""
    print("🗄️ 检查向量数据库...")
    
    vectorstore_path = Path("vectorstores")
    if vectorstore_path.exists() and any(vectorstore_path.iterdir()):
        print("✅ 向量数据库已存在")
        
        # 统计文件数量
        files = list(vectorstore_path.rglob("*"))
        print(f"   📁 数据库文件: {len(files)} 个")
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

def check_dependencies():
    """检查系统依赖"""
    print("🔍 检查系统依赖...")
    
    # 检查Python依赖
    required_packages = [
        'fastapi', 'uvicorn', 'langchain_chroma', 
        'langchain_ollama', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少Python包: {', '.join(missing_packages)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    else:
        print("✅ Python依赖检查通过")
    
    # 检查Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js未安装")
            return False
    except FileNotFoundError:
        print("❌ Node.js未安装")
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
    print("🤖 检查Ollama嵌入模型服务...")
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            if 'nomic-embed-text' in result.stdout:
                print("✅ Ollama服务正常，嵌入模型已就绪")
                return True
            else:
                print("⚠️ 嵌入模型未安装，正在下载...")
                subprocess.run(['ollama', 'pull', 'nomic-embed-text'], check=True)
                print("✅ 嵌入模型下载完成")
                return True
        else:
            print("❌ Ollama服务未运行")
            return False
    except FileNotFoundError:
        print("❌ Ollama未安装")
        print("   请访问 https://ollama.ai 安装Ollama")
        return False
    except subprocess.CalledProcessError:
        print("❌ Ollama服务检查失败")
        return False

def start_services():
    """启动服务"""
    print("\n🚀 启动智能旅游攻略问答系统...")
    print("=" * 60)
    
    # 启动后端
    print("🔧 启动后端服务...")
    try:
        os.chdir("backend")
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        os.chdir("..")
        print("✅ 后端服务启动中...")
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None, None
    
    # 等待后端启动
    print("⏳ 等待后端服务就绪...")
    time.sleep(5)
    
    # 启动前端
    print("🎨 启动前端服务...")
    try:
        frontend_process = subprocess.Popen([
            'npm', 'run', 'dev'
        ], cwd="frontend")
        print("✅ 前端服务启动中...")
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        backend_process.terminate()
        return None, None
    
    return backend_process, frontend_process

def open_browser():
    """打开浏览器"""
    import webbrowser
    print("🌐 正在打开浏览器...")
    webbrowser.open('http://localhost:5173')

def signal_handler(sig, frame):
    """信号处理器"""
    print("\n🛑 正在关闭智能旅游攻略系统...")
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    # 打印启动横幅
    print_banner()
    
    print("🔍 系统检查中...")
    print("=" * 60)
    
    # 系统检查
    checks = [
        ("旅游攻略数据", check_travel_data),
        ("系统依赖", check_dependencies),
        ("Ollama服务", check_ollama),
        ("向量数据库", check_vectorstore)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ {check_name}检查失败，请解决问题后重试")
            sys.exit(1)
        print()
    
    # 启动服务
    backend_process, frontend_process = start_services()
    if not backend_process or not frontend_process:
        print("❌ 服务启动失败")
        sys.exit(1)
    
    # 等待服务完全启动
    time.sleep(3)
    
    print("\n" + "=" * 60)
    print("🎉 智能旅游攻略问答系统启动成功！")
    print("=" * 60)
    print("🌐 前端地址: http://localhost:5173")
    print("🔧 后端地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("=" * 60)
    print("💡 功能特色:")
    print("   📍 景点推荐 - 发现最佳旅游目的地")
    print("   🏨 住宿建议 - 找到性价比最高的住宿")
    print("   🍜 美食攻略 - 品尝地道特色美食")
    print("   🚗 交通指南 - 规划最优出行路线")
    print("   💰 预算规划 - 制定合理旅游预算")
    print("   📅 行程安排 - 定制个性化行程")
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
        
        print("✅ 智能旅游攻略系统已关闭")
        print("🌟 感谢使用，祝您旅途愉快！")

if __name__ == "__main__":
    main()
