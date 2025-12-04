#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 OpenAI API 兼容服务器
"""

import json
import time
import requests
import os

# API 基础 URL
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def test_health_check():
    """测试健康检查端点"""
    print("测试健康检查端点...")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 健康检查成功: {data}")
        return True
    else:
        print(f"❌ 健康检查失败: {response.status_code} - {response.text}")
        return False

def test_models_list():
    """测试模型列表端点"""
    print("\n测试模型列表端点...")
    response = requests.get(f"{BASE_URL}/v1/models")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ 模型列表获取成功:")
        for model in data.get("data", []):
            print(f"  - {model['id']} (owned by: {model['owned_by']})")
        return True
    else:
        print(f"❌ 模型列表获取失败: {response.status_code} - {response.text}")
        return False

def test_chat_completion_with_orange_cat():
    """测试聊天完成端点"""
    print("\n测试 Orange Cat 模型聊天完成端点...")
    
    # 测试数据
    payload = {
        "model": "mihoyo-orange_cat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Orange Cat聊天完成成功:")
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"  模型: {data.get('model')}")
        print(f"  回复: {content[:100]}..." if len(content) > 100 else f"  回复: {content}")
        return True
    else:
        print(f"❌ Orange Cat聊天完成失败: {response.status_code} - {response.text}")
        return False

def test_chat_completion_with_exotic_shorthair():
    """测试使用 Exotic Shorthair 模型的聊天完成端点"""
    print("\n测试 Exotic Shorthair 模型聊天完成端点...")
    
    # 测试数据
    payload = {
        "model": "mihoyo-exotic_shorthair",
        "messages": [
            {"role": "user", "content": "现在你是黑猫模型吗？"}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Exotic Shorthair 聊天完成成功:")
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"  模型: {data.get('model')}")
        print(f"  回复: {content[:100]}..." if len(content) > 100 else f"  回复: {content}")
        return True
    else:
        print(f"❌ Exotic Shorthair 聊天完成失败: {response.status_code} - {response.text}")
        return False

def test_chat_completion_with_gpt4():
    """测试使用 非内部 模型的聊天完成端点"""
    print("\n测试 非内部 模型聊天完成端点...")
    
    # 测试数据
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "现在你是黑猫模型吗？"}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ GPT-4 聊天完成成功:")
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"  模型: {data.get('model')}")
        print(f"  回复: {content[:100]}..." if len(content) > 100 else f"  回复: {content}")
        return True
    else:
        print(f"❌ GPT-4 聊天完成失败: {response.status_code} - {response.text}")
        return False

def test_streaming_chat_completion():
    """测试流式聊天完成端点"""
    print("\n测试流式聊天完成端点...")
    
    # 测试数据
    payload = {
        "model": "mihoyo-orange_cat",
        "messages": [
            {"role": "user", "content": "请用流式回复介绍一下你自己"}
        ],
        "temperature": 0.7,
        "stream": True
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload,
        stream=True
    )
    
    if response.status_code == 200:
        print("✅ 流式聊天完成成功:")
        full_content = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                content = delta["content"]
                                full_content += content
                                print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        pass
        print(f"\n完整回复长度: {len(full_content)} 字符")
        return True
    else:
        print(f"❌ 流式聊天完成失败: {response.status_code} - {response.text}")
        return False

def test_sessions():
    """测试会话管理端点"""
    print("\n测试会话管理端点...")
    
    # 获取会话列表
    response = requests.get(f"{BASE_URL}/sessions")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ 会话列表获取成功:")
        for session in data.get("sessions", []):
            print(f"  - 会话 ID: {session['id']}")
            print(f"    模型: {session['model']}")
            print(f"    创建时间: {session['created_at']}")
            print(f"    有 AnuNeko 会话: {session['has_anuneko_chat']}")
        return True
    else:
        print(f"❌ 会话列表获取失败: {response.status_code} - {response.text}")
        return False

def test_openai_client():
    """使用 OpenAI 客户端库测试"""
    print("\n使用 OpenAI 客户端库测试...")
    
    try:
        from openai import OpenAI
        
        # 创建客户端
        client = OpenAI(
            api_key="dummy-key",  # 不需要真实的 key
            base_url=f"{BASE_URL}/v1"
        )
        
        # 测试聊天完成
        response = client.chat.completions.create(
            model="mihoyo-orange_cat",
            messages=[
                {"role": "user", "content": "你好，使用 OpenAI 客户端库测试"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        print("✅ OpenAI 客户端库测试成功:")
        print(f"  模型: {response.model}")
        print(f"  回复: {response.choices[0].message.content}")
        return True
    
    except ImportError:
        print("⚠️ 未安装 OpenAI 客户端库，跳过此测试")
        print("   安装命令: pip install openai")
        return True
    except Exception as e:
        print(f"❌ OpenAI 客户端库测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("开始测试 OpenAI API 兼容服务器...\n")
    
    tests = [
        test_health_check,
        test_models_list,
        test_chat_completion_with_orange_cat,
        test_chat_completion_with_exotic_shorthair,
        test_chat_completion_with_gpt4,
        test_streaming_chat_completion,
        test_sessions,
        test_openai_client
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
    
    print(f"\n测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查服务器状态")

if __name__ == "__main__":
    main()