#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制重建向量数据库
彻底清理并重建向量数据库，解决维度不匹配问题
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🔥 强制重建向量数据库                                 ║
    ║                                                              ║
    ║        彻底清理并重建，解决维度匹配问题                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def force_clean():
    """强制清理向量数据库"""
    vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
    
    print(f"🗑️ 强制清理向量数据库: {vectorstore_path}")
    
    if os.path.exists(vectorstore_path):
        # 创建备份
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{vectorstore_path}_backup_{timestamp}"
        
        try:
            print(f"💾 创建备份: {backup_path}")
            shutil.copytree(vectorstore_path, backup_path)
            print("✅ 备份创建成功")
        except Exception as e:
            print(f"⚠️ 备份失败: {e}")
        
        # 删除原数据库
        try:
            print(f"🗑️ 删除旧数据库...")
            shutil.rmtree(vectorstore_path)
            print("✅ 旧数据库删除成功")
            return True
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False
    else:
        print("ℹ️ 向量数据库目录不存在")
        return True

def rebuild_database():
    """重建数据库"""
    print("\n🔄 开始重建向量数据库...")
    
    try:
        import subprocess
        
        # 运行构建脚本
        result = subprocess.run(
            [sys.executable, "build_travel_vectordb.py"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("✅ 向量数据库重建成功")
            print(result.stdout)
            return True
        else:
            print("❌ 重建失败")
            print(f"错误输出: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 重建过程出错: {e}")
        return False

def verify_rebuild():
    """验证重建结果"""
    print("\n🔍 验证重建结果...")
    
    vectorstore_path = os.getenv("VECTORSTORE_PATH", "vectorstores")
    
    if not os.path.exists(vectorstore_path):
        print("❌ 向量数据库目录不存在")
        return False
    
    # 检查目录内容
    try:
        files = list(Path(vectorstore_path).rglob("*"))
        if files:
            print(f"✅ 向量数据库目录存在，包含 {len(files)} 个文件")
            return True
        else:
            print("❌ 向量数据库目录为空")
            return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    print("⚠️ 警告: 此操作将完全删除现有向量数据库并重建")
    print("建议在执行前确保:")
    print("1. 后端服务已停止")
    print("2. 没有其他程序在使用向量数据库")
    
    confirm = input("\n确认执行强制重建? (输入 'YES' 确认): ").strip()
    
    if confirm != 'YES':
        print("❌ 操作已取消")
        return
    
    print("\n🚀 开始强制重建流程...")
    
    # 1. 强制清理
    if not force_clean():
        print("❌ 清理失败，停止操作")
        return
    
    # 2. 重建数据库
    if not rebuild_database():
        print("❌ 重建失败")
        return
    
    # 3. 验证结果
    if verify_rebuild():
        print("\n🎉 强制重建完成!")
        print("\n📋 下一步操作:")
        print("1. 重启后端服务: python start_backend.py")
        print("2. 测试前端问答功能")
        print("3. 如果还有问题，请检查后端日志")
    else:
        print("❌ 验证失败，可能需要手动检查")

if __name__ == "__main__":
    main()
