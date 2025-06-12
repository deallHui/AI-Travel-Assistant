#!/usr/bin/env python3
"""
RAG应用后端启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查Python依赖"""
    try:
        import fastapi
        import uvicorn
        import langchain
        import chromadb
        print("✓ 所有Python依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_vectorstore():
    """检查向量数据库"""
    vectorstore_path = Path("vectorstores")
    if vectorstore_path.exists() and vectorstore_path.is_dir():
        files = list(vectorstore_path.glob("*"))
        if files:
            print(f"✓ 向量数据库已存在，包含 {len(files)} 个文件")
            return True
    
    print("✗ 向量数据库不存在或为空")
    print("请确保向量数据库位于 ./vectorstores 目录下")
    return False

def check_env():
    """检查环境变量"""
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("⚠ 未找到 .env 文件，将使用默认配置")
        print("建议复制 backend/.env.example 为 backend/.env 并配置DeepSeek API密钥")
        return False
    else:
        print("✓ 找到环境配置文件")

        # 检查关键配置项
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            import os

            deepseek_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_key or deepseek_key == "your-deepseek-api-key":
                print("⚠ DeepSeek API密钥未配置或使用默认值")
                print("请在 .env 文件中设置正确的 DEEPSEEK_API_KEY")
            else:
                print("✓ DeepSeek API密钥已配置")

            vectorstore_path = os.getenv("VECTORSTORE_PATH", "../vectorstores")
            print(f"✓ 向量数据库路径: {vectorstore_path}")

        except Exception as e:
            print(f"⚠ 读取环境配置时出错: {e}")

    return True

def main():
    """主函数"""
    print("=== RAG应用后端启动检查 ===")
    
    # 切换到项目目录
    os.chdir(Path(__file__).parent)
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查向量数据库
    if not check_vectorstore():
        print("警告: 向量数据库检查失败，但仍将尝试启动服务")
    
    # 检查环境配置
    check_env()
    
    print("\n=== 启动后端服务 ===")
    
    try:
        # 加载环境变量
        from dotenv import load_dotenv
        load_dotenv("backend/.env")

        # 从环境变量读取配置
        host = os.getenv("HOST", "0.0.0.0")
        port = os.getenv("PORT", "8000")

        print(f"启动服务器: http://{host}:{port}")

        # 启动FastAPI服务
        os.chdir("backend")
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", host,
            "--port", port,
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
