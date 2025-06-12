#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强RAG系统测试脚本
测试知识库+网络搜索的混合工作链
"""

import requests
import json
import time

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🧪 增强RAG系统测试                                    ║
    ║                                                              ║
    ║        测试知识库+网络搜索混合工作链                         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def test_query(question, description):
    """测试查询"""
    print(f"\n🧪 测试: {description}")
    print(f"❓ 问题: {question}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/query",
            json={"question": question, "top_k": 3},
            timeout=30
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ 查询成功 (耗时: {duration:.2f}秒)")
            print(f"🎯 置信度: {result.get('confidence', 0) * 100:.0f}%")
            print(f"📚 来源数量: {len(result.get('sources', []))}")
            
            # 显示来源
            sources = result.get('sources', [])
            if sources:
                print(f"📋 信息来源:")
                for i, source in enumerate(sources, 1):
                    if 'DeepSeek' in source or '网络搜索' in source:
                        print(f"  {i}. 🤖 {source}")
                    else:
                        print(f"  {i}. 📚 {source}")
            
            # 显示回答（截取前200字符）
            answer = result.get('answer', '')
            if len(answer) > 200:
                preview = answer[:200] + "..."
            else:
                preview = answer
            
            print(f"💬 回答预览:")
            print(f"   {preview}")
            
            # 判断是否使用了网络搜索
            used_network = any('DeepSeek' in source or '网络搜索' in source for source in sources)
            if used_network:
                print("🌐 ✅ 已启用网络搜索增强")
            else:
                print("📚 ✅ 仅使用知识库回答")
            
            return True
            
        else:
            print(f"❌ 查询失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 查询超时")
        return False
    except Exception as e:
        print(f"❌ 查询异常: {e}")
        return False

def test_network_search(question, description):
    """测试纯网络搜索"""
    print(f"\n🌐 网络搜索测试: {description}")
    print(f"❓ 问题: {question}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/search",
            json={"question": question, "top_k": 3},
            timeout=30
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ 网络搜索成功 (耗时: {duration:.2f}秒)")
            print(f"🎯 置信度: {result.get('confidence', 0) * 100:.0f}%")
            
            # 显示回答（截取前200字符）
            answer = result.get('answer', '')
            if len(answer) > 200:
                preview = answer[:200] + "..."
            else:
                preview = answer
            
            print(f"💬 回答预览:")
            print(f"   {preview}")
            
            return True
            
        else:
            print(f"❌ 网络搜索失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 网络搜索异常: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查后端服务
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
        else:
            print("❌ 后端服务异常")
            return
    except:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        print("启动命令: python start_backend.py")
        return
    
    print("\n🚀 开始测试增强RAG系统...")
    
    # 测试用例
    test_cases = [
        # 知识库中有的问题（应该主要使用知识库）
        ("北京有哪些著名景点？", "知识库覆盖问题"),
        ("上海的美食推荐", "知识库覆盖问题"),
        ("三亚旅游攻略", "知识库覆盖问题"),
        
        # 知识库中可能没有的问题（应该启用网络搜索）
        ("2024年最新的日本签证政策", "需要网络搜索的时效性问题"),
        ("马尔代夫哪个岛屿最适合蜜月旅行", "知识库可能不足的问题"),
        ("欧洲火车通票怎么购买和使用", "专业性问题"),
        
        # 完全超出旅游范围的问题（测试系统边界）
        ("如何学习编程", "非旅游问题"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for question, description in test_cases:
        if test_query(question, description):
            success_count += 1
        time.sleep(1)  # 避免请求过于频繁
    
    # 测试纯网络搜索接口
    print(f"\n" + "=" * 60)
    print("🌐 测试纯网络搜索接口")
    
    network_test_cases = [
        ("最新的泰国入境政策", "时效性问题"),
        ("新加坡樟宜机场免税店购物攻略", "具体场所问题"),
    ]
    
    for question, description in network_test_cases:
        test_network_search(question, description)
        time.sleep(1)
    
    # 总结
    print(f"\n" + "=" * 60)
    print(f"📊 测试总结:")
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"📈 成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试通过！增强RAG系统工作正常")
    else:
        print("⚠️ 部分测试失败，请检查系统配置")
    
    print(f"\n💡 使用建议:")
    print(f"1. 知识库问题会优先使用本地数据")
    print(f"2. 不足时自动启用网络搜索增强")
    print(f"3. 查看回答来源了解信息类型")
    print(f"4. 置信度帮助判断答案可靠性")

if __name__ == "__main__":
    main()
