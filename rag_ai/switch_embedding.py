#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌入模型切换工具
支持快速切换不同的嵌入模型提供商
"""

import os
import sys
import argparse
import time
from pathlib import Path

def print_banner():
    """打印工具横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        ⚡ 嵌入模型切换工具                                   ║
    ║                                                              ║
    ║        快速切换嵌入模型，提升系统性能                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def get_available_models():
    """获取可用的嵌入模型"""
    models = {
        # 推荐模型（速度优化）
        "bge-small-zh": {
            "name": "BGE Small Chinese (推荐)",
            "provider": "modelscope",
            "speed": "⚡ 很快",
            "quality": "🌟 高",
            "description": "智源BGE中文模型，使用ModelScope镜像，速度快",
            "requirements": "pip install sentence-transformers"
        },
        "siliconflow-embedding": {
            "name": "SiliconFlow Embedding (推荐)",
            "provider": "siliconflow", 
            "speed": "⚡ 极快",
            "quality": "🌟 很高",
            "description": "SiliconFlow云端API，速度极快，质量很高",
            "requirements": "需要SiliconFlow API密钥"
        },
        "hf-bge-small": {
            "name": "BGE Small (HF Mirror)",
            "provider": "huggingface_mirror",
            "speed": "⚡ 快",
            "quality": "🌟 高", 
            "description": "使用HuggingFace镜像的BGE模型",
            "requirements": "pip install sentence-transformers"
        },
        
        # 其他模型
        "bge-base-zh": {
            "name": "BGE Base Chinese",
            "provider": "modelscope",
            "speed": "🔄 中等",
            "quality": "🌟 很高",
            "description": "智源BGE中文基础模型，质量更高",
            "requirements": "pip install sentence-transformers"
        },
        "text2vec-base": {
            "name": "Text2Vec Base Chinese",
            "provider": "modelscope",
            "speed": "⚡ 快",
            "quality": "🌟 高",
            "description": "达摩院中文句子嵌入模型",
            "requirements": "pip install sentence-transformers"
        },
        "nomic-embed-text": {
            "name": "Nomic Embed Text (本地)",
            "provider": "ollama",
            "speed": "🔄 中等",
            "quality": "🌟 高",
            "description": "Ollama本地模型，支持中英文",
            "requirements": "需要安装Ollama"
        },
        "all-minilm-l6-v2": {
            "name": "All MiniLM L6 v2 (轻量)",
            "provider": "ollama",
            "speed": "⚡ 快",
            "quality": "🌟 中等",
            "description": "轻量级模型，速度快",
            "requirements": "需要安装Ollama"
        },

    }
    return models

def list_models():
    """列出所有可用模型"""
    models = get_available_models()
    
    print("📋 可用的嵌入模型:")
    print("=" * 80)
    
    # 按类别分组显示
    categories = {
        "🚀 推荐模型（速度优化）": [],
        "🔧 本地模型": [],
        "☁️ 云端API": [],
        "🌐 其他选择": []
    }
    
    for key, model in models.items():
        if "推荐" in model["name"]:
            categories["🚀 推荐模型（速度优化）"].append((key, model))
        elif model["provider"] in ["ollama"]:
            categories["🔧 本地模型"].append((key, model))
        elif model["provider"] in ["siliconflow"]:
            categories["☁️ 云端API"].append((key, model))
        else:
            categories["🌐 其他选择"].append((key, model))
    
    for category, model_list in categories.items():
        if model_list:
            print(f"\n{category}")
            print("-" * 60)
            for key, model in model_list:
                print(f"🔹 {key}")
                print(f"   名称: {model['name']}")
                print(f"   速度: {model['speed']} | 质量: {model['quality']}")
                print(f"   描述: {model['description']}")
                print(f"   要求: {model['requirements']}")
                print()

def get_current_config():
    """获取当前配置"""
    env_file = Path("backend/.env")
    if not env_file.exists():
        env_file = Path(".env")
    
    if not env_file.exists():
        return None, None
    
    current_model = None
    current_provider = None
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('EMBEDDING_MODEL='):
                    current_model = line.split('=', 1)[1]
                elif line.startswith('EMBEDDING_PROVIDER='):
                    current_provider = line.split('=', 1)[1]
    except Exception as e:
        print(f"⚠️ 读取配置文件失败: {e}")
    
    return current_model, current_provider

def show_current():
    """显示当前配置"""
    print("📊 当前嵌入模型配置:")
    print("=" * 50)
    
    current_model, current_provider = get_current_config()
    
    if current_model:
        print(f"✅ 当前模型: {current_model}")
        print(f"✅ 提供商: {current_provider or '未指定'}")
        
        # 显示性能信息
        models = get_available_models()
        for key, model_info in models.items():
            if key in current_model or model_info.get("model_id", "") == current_model:
                print(f"📈 性能: 速度 {model_info['speed']} | 质量 {model_info['quality']}")
                break
    else:
        print("⚠️ 未找到嵌入模型配置")
        print("   使用默认模型: nomic-embed-text:latest")

def switch_model(model_key: str):
    """切换嵌入模型"""
    models = get_available_models()
    
    if model_key not in models:
        print(f"❌ 未知的模型: {model_key}")
        print("请使用 'list' 命令查看可用模型")
        return False
    
    model_info = models[model_key]
    
    # 模型配置映射
    model_configs = {
        "bge-small-zh": {
            "model": "AI-ModelScope/bge-small-zh",
            "provider": "modelscope"
        },
        "bge-base-zh": {
            "model": "AI-ModelScope/bge-base-zh", 
            "provider": "modelscope"
        },
        "text2vec-base": {
            "model": "damo/nlp_corom_sentence-embedding_chinese-base",
            "provider": "modelscope"
        },
        "siliconflow-embedding": {
            "model": "BAAI/bge-large-zh-v1.5",
            "provider": "siliconflow"
        },
        "hf-bge-small": {
            "model": "BAAI/bge-small-zh-v1.5",
            "provider": "huggingface_mirror"
        },
        "nomic-embed-text": {
            "model": "nomic-embed-text:latest",
            "provider": "ollama"
        },
        "all-minilm-l6-v2": {
            "model": "all-minilm:l6-v2",
            "provider": "ollama"
        },

    }
    
    if model_key not in model_configs:
        print(f"❌ 模型配置未找到: {model_key}")
        return False
    
    config = model_configs[model_key]
    
    # 更新环境变量文件
    env_file = Path("backend/.env")
    if not env_file.exists():
        env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ 未找到环境变量文件")
        return False
    
    try:
        # 读取现有配置
        lines = []
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新或添加配置
        embedding_model_found = False
        embedding_provider_found = False
        
        for i, line in enumerate(lines):
            if line.startswith('EMBEDDING_MODEL='):
                lines[i] = f"EMBEDDING_MODEL={config['model']}\n"
                embedding_model_found = True
            elif line.startswith('EMBEDDING_PROVIDER='):
                lines[i] = f"EMBEDDING_PROVIDER={config['provider']}\n"
                embedding_provider_found = True
        
        # 如果没有找到，添加新的配置
        if not embedding_model_found:
            lines.append(f"EMBEDDING_MODEL={config['model']}\n")
        if not embedding_provider_found:
            lines.append(f"EMBEDDING_PROVIDER={config['provider']}\n")
        
        # 写回文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ 嵌入模型已切换为: {model_info['name']}")
        print(f"   模型ID: {config['model']}")
        print(f"   提供商: {config['provider']}")
        print(f"   性能: 速度 {model_info['speed']} | 质量 {model_info['quality']}")
        print(f"   配置文件: {env_file}")
        
        # 显示额外要求
        if model_info.get("requirements"):
            print(f"\n💡 要求: {model_info['requirements']}")
        
        # 给出重启提示
        print("\n🔄 请重启后端服务以应用新配置:")
        print("   python start_backend.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 切换配置失败: {e}")
        return False

def quick_setup():
    """快速设置推荐模型"""
    print("🚀 快速设置推荐的高速嵌入模型")
    print("=" * 50)
    
    recommendations = [
        ("bge-small-zh", "智源BGE中文模型 (ModelScope镜像)"),
        ("siliconflow-embedding", "SiliconFlow云端API (需要API密钥)"),
        ("hf-bge-small", "BGE模型 (HuggingFace镜像)")
    ]
    
    print("推荐选择:")
    for i, (key, desc) in enumerate(recommendations, 1):
        print(f"{i}. {desc}")
    
    try:
        choice = input("\n请选择 (1-3): ").strip()
        if choice in ['1', '2', '3']:
            model_key = recommendations[int(choice) - 1][0]
            return switch_model(model_key)
        else:
            print("❌ 无效选择")
            return False
    except KeyboardInterrupt:
        print("\n操作已取消")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="嵌入模型切换工具")
    parser.add_argument("command", nargs='?', choices=["list", "current", "switch", "quick"], 
                       help="操作命令")
    parser.add_argument("--model", help="模型名称（用于switch命令）")
    
    args = parser.parse_args()
    
    print_banner()
    
    if not args.command:
        print("🎯 使用说明:")
        print("  python switch_embedding.py list     # 查看所有可用模型")
        print("  python switch_embedding.py current  # 查看当前配置")
        print("  python switch_embedding.py quick    # 快速设置推荐模型")
        print("  python switch_embedding.py switch --model <model_name>  # 切换模型")
        return
    
    if args.command == "list":
        list_models()
    
    elif args.command == "current":
        show_current()
    
    elif args.command == "quick":
        quick_setup()
    
    elif args.command == "switch":
        if not args.model:
            print("❌ 请指定模型名称")
            print("使用: python switch_embedding.py switch --model <model_name>")
            sys.exit(1)
        switch_model(args.model)

if __name__ == "__main__":
    main()
