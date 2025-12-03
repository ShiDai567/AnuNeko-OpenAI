#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnuNeko API 使用示例
演示如何使用 anuneko_api.py 中的异步函数
"""

import asyncio
import os
from anuneko_api import AnuNekoAPI, create_session, send_message, switch_model, select_choice


async def main():
    """主函数，演示 API 使用"""
    
    # 配置信息 - 可以从环境变量获取或直接设置
    TOKEN = os.environ.get("ANUNEKO_TOKEN", "你的Token")  # 替换为你的实际 Token
    COOKIE = os.environ.get("ANUNEKO_COOKIE", "你的Cookie")  # 替换为你的实际 Cookie
    # print(TOKEN,COOKIE)
    print("=== AnuNeko API 异步使用示例 ===\n")
    
    # 方法一：使用类实例
    print("方法一：使用类实例")
    api = AnuNekoAPI(TOKEN, COOKIE)
    
    try:
        # 创建会话
        print("1. 创建新会话...")
        chat_id = await api.create_session("Orange Cat")
        print(f"会话 ID: {chat_id}")
        
        if chat_id:
            # 发送消息
            print("\n2. 发送消息...")
            response = await api.stream_reply(chat_id, "你好，AnuNeko！")
            print(f"AI 回复: {response}")
            
            # 切换模型
            print("\n3. 切换到黑猫模型...")
            success = await api.switch_model(chat_id, "Exotic Shorthair")
            print(f"切换成功: {success}")
            
            # 再次发送消息
            print("\n4. 使用黑猫模型发送消息...")
            response = await api.stream_reply(chat_id, "现在你是黑猫了吗？")
            print(f"AI 回复: {response}")
            
            # 使用生成器方式获取流式回复
            print("\n5. 使用生成器方式获取流式回复:")
            print("AI: ", end="", flush=True)
            async for chunk in api.stream_reply_generator(chat_id, "介绍一下你自己"):
                print(chunk, end="", flush=True)
            print()
        
    except Exception as e:
        print(f"使用类实例时出错: {e}\n")
    
    # 方法二：使用便捷函数
    print("\n方法二：使用便捷函数")
    
    try:
        # 创建会话
        print("1. 创建新会话...")
        chat_id = await create_session(TOKEN, COOKIE, "Orange Cat")
        print(f"会话 ID: {chat_id}")
        
        if chat_id:
            # 发送消息
            print("\n2. 发送消息...")
            response = await send_message(TOKEN, chat_id, ["使用便捷函数发送消息"], COOKIE)
            print(f"AI 回复: {response}")
            
            # 切换模型
            print("\n3. 切换模型...")
            success = await switch_model(TOKEN, chat_id, "Orange Cat", COOKIE)
            print(f"切换成功: {success}")
        
    except Exception as e:
        print(f"使用便捷函数时出错: {e}\n")
    
    # 注意：选择回复功能需要实际的 msg_id，这里只展示语法
    print("\n选择回复功能示例（需要实际 msg_id）:")
    print("success = await select_choice(TOKEN, '实际的消息ID', 0, COOKIE)")
    print("print(f'选择成功: {success}')\n")
    
    print("=== 示例结束 ===")


async def interactive_mode():
    """交互模式，让用户输入参数并执行 API 调用"""
    
    print("=== AnuNeko API 交互模式 ===\n")
    
    # 获取用户输入
    token = input("请输入你的 Token (留空使用环境变量 ANUNEKO_TOKEN): ") or os.environ.get("ANUNEKO_TOKEN")
    cookie = input("请输入你的 Cookie (可选，留空使用环境变量 ANUNEKO_COOKIE): ") or os.environ.get("ANUNEKO_COOKIE")
    print(token)
    print(cookie)
    if not token:
        print("错误：Token 是必需的！")
        return
    
    # 创建 API 实例
    api = AnuNekoAPI(token, cookie)
    
    # 创建会话
    print("\n正在创建会话...")
    chat_id = await api.create_session("Orange Cat")
    if not chat_id:
        print("创建会话失败，请检查 Token 和 Cookie 是否正确")
        return
    
    print(f"会话创建成功，ID: {chat_id}")
    
    while True:
        print("\n请选择操作:")
        print("1. 发送消息")
        print("2. 切换模型")
        print("3. 选择回复")
        print("4. 流式回复（生成器模式）")
        print("5. 退出")
        
        choice = input("请输入选项 (1-5): ")
        
        if choice == "1":
            message = input("请输入要发送的消息: ")
            try:
                print("等待 AI 回复...")
                response = await api.stream_reply(chat_id, message)
                print(f"AI 回复: {response}")
            except Exception as e:
                print(f"发送消息失败: {e}")
        
        elif choice == "2":
            print("可用模型:")
            print("1. Orange Cat (橘猫)")
            print("2. Exotic Shorthair (黑猫)")
            model_choice = input("请选择模型 (1-2): ")
            
            model = "Orange Cat" if model_choice == "1" else "Exotic Shorthair"
            try:
                success = await api.switch_model(chat_id, model)
                print(f"切换模型成功: {success}")
            except Exception as e:
                print(f"切换模型失败: {e}")
        
        elif choice == "3":
            msg_id = input("请输入消息 ID: ")
            choice_idx = int(input("请输入选择索引 (0 或 1): "))
            try:
                success = await api.send_choice(msg_id, choice_idx)
                print(f"选择回复成功: {success}")
            except Exception as e:
                print(f"选择回复失败: {e}")
        
        elif choice == "4":
            message = input("请输入要发送的消息: ")
            try:
                print("AI: ", end="", flush=True)
                async for chunk in api.stream_reply_generator(chat_id, message):
                    print(chunk, end="", flush=True)
                print()
            except Exception as e:
                print(f"流式回复失败: {e}")
        
        elif choice == "5":
            print("退出交互模式")
            break
        
        else:
            print("无效选项，请重新输入")


async def batch_example():
    """批量处理示例"""
    
    print("=== AnuNeko API 批量处理示例 ===\n")
    
    # 配置信息
    TOKEN = os.environ.get("ANUNEKO_TOKEN", "你的Token")
    COOKIE = os.environ.get("ANUNEKO_COOKIE", "你的Cookie")
    
    if not TOKEN or TOKEN == "你的Token":
        print("请设置有效的 Token")
        return
    
    # 创建 API 实例
    api = AnuNekoAPI(TOKEN, COOKIE)
    
    # 创建会话
    chat_id = await api.create_session("Orange Cat")
    if not chat_id:
        print("创建会话失败")
        return
    
    print(f"会话 ID: {chat_id}")
    
    # 批量问题
    questions = [
        "你好，请介绍一下你自己",
        "你有什么特长？",
        "你能做什么？",
        "你喜欢什么？"
    ]
    
    print("\n开始批量提问...")
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        print("回答: ", end="", flush=True)
        
        try:
            # 使用生成器方式获取流式回复
            async for chunk in api.stream_reply_generator(chat_id, question):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"提问失败: {e}")
    
    print("\n批量提问完成")


if __name__ == "__main__":
    # 选择运行模式
    mode = input("选择运行模式:\n1. 示例模式\n2. 交互模式\n3. 批量处理模式\n请输入选项 (1-3): ")
    
    if mode == "1":
        asyncio.run(main())
    elif mode == "2":
        asyncio.run(interactive_mode())
    elif mode == "3":
        asyncio.run(batch_example())
    else:
        print("无效选项，运行示例模式")
        asyncio.run(main())