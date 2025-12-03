#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 OpenAI 兼容 API 的示例
"""

import os
from openai import OpenAI

# 配置 API
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8080")
API_KEY = "dummy-key"  # 不需要真实的 key

# 创建客户端
client = OpenAI(
    api_key=API_KEY,
    base_url=f"{API_BASE_URL}/v1"
)

def simple_chat_example():
    """简单聊天示例"""
    print("=== 简单聊天示例 ===")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 对应 AnuNeko 的橘猫
        messages=[
            {"role": "system", "content": "你是一个有用的助手。"},
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    print(f"模型: {response.model}")
    print(f"回复: {response.choices[0].message.content}")
    print()

def gpt4_example():
    """使用 GPT-4 模型示例"""
    print("=== GPT-4 模型示例 ===")
    
    response = client.chat.completions.create(
        model="gpt-4",  # 对应 AnuNeko 的黑猫
        messages=[
            {"role": "user", "content": "现在你是黑猫模型吗？请用黑猫的语气回复"}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    print(f"模型: {response.model}")
    print(f"回复: {response.choices[0].message.content}")
    print()

def streaming_example():
    """流式回复示例"""
    print("=== 流式回复示例 ===")
    
    print("AI: ", end="", flush=True)
    
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "请用流式回复写一首关于猫的诗"}
        ],
        stream=True,
        temperature=0.8
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
    
    print("\n")

def conversation_example():
    """多轮对话示例"""
    print("=== 多轮对话示例 ===")
    
    conversation = [
        {"role": "system", "content": "你是一个有趣的对话伙伴。"},
        {"role": "user", "content": "你喜欢什么颜色？"}
    ]
    
    # 第一轮对话
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        temperature=0.7
    )
    
    assistant_reply = response.choices[0].message.content
    print(f"用户: {conversation[-1]['content']}")
    print(f"助手: {assistant_reply}")
    print()
    
    # 添加助手回复到对话历史
    conversation.append({"role": "assistant", "content": assistant_reply})
    
    # 第二轮对话
    conversation.append({"role": "user", "content": "为什么喜欢这个颜色？"})
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        temperature=0.7
    )
    
    assistant_reply = response.choices[0].message.content
    print(f"用户: {conversation[-1]['content']}")
    print(f"助手: {assistant_reply}")
    print()

def list_models_example():
    """列出可用模型示例"""
    print("=== 可用模型列表 ===")
    
    models = client.models.list()
    
    for model in models.data:
        print(f"- {model.id} (owned by: {model.owned_by})")
    print()

def interactive_chat():
    """交互式聊天"""
    print("=== 交互式聊天 ===")
    print("输入 'quit' 退出，输入 'switch gpt-4' 切换到 GPT-4 模型")
    print()
    
    current_model = "gpt-3.5-turbo"
    conversation = []
    
    while True:
        user_input = input("你: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if user_input.lower() == 'switch gpt-4':
            current_model = "gpt-4"
            print(f"已切换到 {current_model} 模型")
            continue
        
        if user_input.lower() == 'switch gpt-3.5-turbo':
            current_model = "gpt-3.5-turbo"
            print(f"已切换到 {current_model} 模型")
            continue
        
        if not user_input:
            continue
        
        # 添加用户消息
        conversation.append({"role": "user", "content": user_input})
        
        try:
            # 获取回复
            response = client.chat.completions.create(
                model=current_model,
                messages=conversation,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_reply = response.choices[0].message.content
            print(f"助手 ({current_model}): {assistant_reply}")
            print()
            
            # 添加助手回复
            conversation.append({"role": "assistant", "content": assistant_reply})
            
        except Exception as e:
            print(f"错误: {str(e)}")
            print()

def main():
    """主函数"""
    print("OpenAI 兼容 API 使用示例\n")
    
    try:
        # 运行各种示例
        list_models_example()
        simple_chat_example()
        gpt4_example()
        streaming_example()
        conversation_example()
        
        # 交互式聊天
        choice = input("是否要尝试交互式聊天？(y/n): ").strip().lower()
        if choice == 'y':
            interactive_chat()
        
    except Exception as e:
        print(f"运行示例时出错: {str(e)}")
        print("\n请确保:")
        print("1. 已安装 openai 库: pip install openai")
        print("2. API 服务器正在运行: python openai_api_server.py")
        print("3. 已设置 ANUNEKO_TOKEN 环境变量")

if __name__ == "__main__":
    main()