#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双模式智能切换器
在 SiliconFlow (在线) 和 nomic-embed-text (离线) 之间智能切换
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🔄 双模式智能切换器                                   ║
    ║                                                              ║
    ║        SiliconFlow (在线) ⟷ nomic-embed-text (离线)        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def test_siliconflow_connectivity():
    """测试 SiliconFlow 连接"""
    print("🌐 测试 SiliconFlow 连接...")
    
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("❌ 未配置 SiliconFlow API Key")
        return False
    
    try:
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.siliconflow.cn/v1/embeddings",
            headers=headers,
            json={
                "model": "BAAI/bge-large-zh-v1.5",
                "input": ["测试连接"]
            },
            timeout=5
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            speed = end_time - start_time
            print(f"✅ SiliconFlow: 连接成功 ({speed:.2f}秒)")
            return True
        else:
            print(f"❌ SiliconFlow: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ SiliconFlow: 连接超时")
        return False
    except Exception as e:
        print(f"❌ SiliconFlow: {str(e)[:50]}...")
        return False

def test_ollama_availability():
    """测试 Ollama 可用性"""
    print("🖥️ 测试 Ollama 本地模型...")
    
    try:
        # 检查 Ollama 服务
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("❌ Ollama: 服务不可用")
            return False
        
        # 检查 nomic-embed-text 模型
        if 'nomic-embed-text' not in result.stdout:
            print("❌ Ollama: 缺少 nomic-embed-text 模型")
            print("   请运行: ollama pull nomic-embed-text")
            return False
        
        print("✅ Ollama: nomic-embed-text 模型可用")
        return True
        
    except FileNotFoundError:
        print("❌ Ollama: 未安装")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama: 响应超时")
        return False

def get_current_mode():
    """获取当前模式"""
    embedding_model = os.getenv("EMBEDDING_MODEL", "")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "")
    
    if embedding_provider == "siliconflow":
        return "online"
    elif embedding_provider == "ollama" and "nomic-embed-text" in embedding_model:
        return "offline"
    else:
        return "unknown"

def switch_to_online():
    """切换到在线模式 (SiliconFlow)"""
    print("\n🌐 切换到在线模式...")
    
    if not test_siliconflow_connectivity():
        print("❌ SiliconFlow 不可用，无法切换到在线模式")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "switch_embedding.py", "switch", "--model", "siliconflow-embedding"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 已切换到在线模式: SiliconFlow Embedding")
            print("   优势: 速度极快 (0.2秒)，质量最高")
            return True
        else:
            print(f"❌ 切换失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 切换失败: {e}")
        return False

def switch_to_offline():
    """切换到离线模式 (nomic-embed-text)"""
    print("\n🖥️ 切换到离线模式...")
    
    if not test_ollama_availability():
        print("❌ Ollama 或 nomic-embed-text 不可用，无法切换到离线模式")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "switch_embedding.py", "switch", "--model", "nomic-embed-text"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 已切换到离线模式: nomic-embed-text")
            print("   优势: 完全离线，无需网络，数据隐私")
            return True
        else:
            print(f"❌ 切换失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 切换失败: {e}")
        return False

def auto_switch():
    """智能自动切换"""
    print("\n🧠 智能检测最佳模式...")
    
    current_mode = get_current_mode()
    print(f"当前模式: {current_mode}")
    
    # 测试网络和服务可用性
    siliconflow_ok = test_siliconflow_connectivity()
    ollama_ok = test_ollama_availability()
    
    print(f"\n📊 可用性检测:")
    print(f"  SiliconFlow (在线): {'✅' if siliconflow_ok else '❌'}")
    print(f"  Ollama (离线): {'✅' if ollama_ok else '❌'}")
    
    # 智能推荐
    if siliconflow_ok and ollama_ok:
        if current_mode == "offline":
            print("\n💡 推荐: 切换到在线模式以获得更快速度")
            choice = input("是否切换到在线模式? (Y/n): ").strip().lower()
            if choice != 'n':
                return switch_to_online()
        else:
            print("\n✅ 当前在线模式运行良好，无需切换")
            return True
    
    elif siliconflow_ok and not ollama_ok:
        print("\n💡 推荐: 使用在线模式 (Ollama不可用)")
        if current_mode != "online":
            return switch_to_online()
        return True
    
    elif not siliconflow_ok and ollama_ok:
        print("\n💡 推荐: 切换到离线模式 (网络不可用)")
        if current_mode != "offline":
            return switch_to_offline()
        return True
    
    else:
        print("\n❌ 两种模式都不可用")
        print("请检查:")
        print("1. SiliconFlow API Key 配置")
        print("2. Ollama 服务和 nomic-embed-text 模型")
        return False

def show_status():
    """显示当前状态"""
    print("\n📊 当前系统状态:")
    print("=" * 50)
    
    current_mode = get_current_mode()
    embedding_model = os.getenv("EMBEDDING_MODEL", "未知")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "未知")
    
    print(f"当前模式: {current_mode}")
    print(f"嵌入模型: {embedding_model}")
    print(f"提供商: {embedding_provider}")
    
    if current_mode == "online":
        print("🌐 在线模式特点:")
        print("  • 速度极快 (0.2秒)")
        print("  • 质量最高")
        print("  • 需要网络连接")
        print("  • 按使用量付费")
    elif current_mode == "offline":
        print("🖥️ 离线模式特点:")
        print("  • 完全本地运行")
        print("  • 无需网络连接")
        print("  • 完全免费")
        print("  • 数据隐私保护")
    
    # 测试当前模式可用性
    print(f"\n🔍 测试当前模式可用性...")
    if current_mode == "online":
        test_siliconflow_connectivity()
    elif current_mode == "offline":
        test_ollama_availability()

def main():
    """主函数"""
    print_banner()
    
    print("🎯 选择操作:")
    print("1. 切换到在线模式 (SiliconFlow - 速度最快)")
    print("2. 切换到离线模式 (nomic-embed-text - 完全本地)")
    print("3. 智能自动切换 (推荐)")
    print("4. 查看当前状态")
    print("5. 退出")
    
    try:
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == "1":
            if switch_to_online():
                print("\n🔄 请重启后端服务:")
                print("  python start_backend.py")
        
        elif choice == "2":
            if switch_to_offline():
                print("\n🔄 请重启后端服务:")
                print("  python start_backend.py")
        
        elif choice == "3":
            if auto_switch():
                print("\n🔄 请重启后端服务:")
                print("  python start_backend.py")
        
        elif choice == "4":
            show_status()
        
        elif choice == "5":
            print("👋 再见！")
        
        else:
            print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 操作已取消")

if __name__ == "__main__":
    main()
