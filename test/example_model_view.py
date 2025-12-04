#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：如何调用 AnuNeko API 的 model_view 方法
获取可用的模型列表
"""

import asyncio
import os
from dotenv import load_dotenv
from anuneko_api import AnuNekoAPI


async def main():
    """主函数：演示如何调用 model_view API"""
    
    # 加载 .env 文件中的环境变量
    # 首先复制 .env.example 为 .env 并填入你的实际值
    load_dotenv()
    
    # 从环境变量获取 token 和 cookie
    token = os.getenv("ANUNEKO_TOKEN")
    cookie = os.getenv("ANUNEKO_COOKIE")
    
    # 检查是否设置了必要的 token
    if not token:
        print("错误: 未找到 ANUNEKO_TOKEN")
        print("请按照以下步骤设置:")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 文件中填入你的实际 token 和 cookie")
        return
    
    try:
        # 初始化 API 客户端
        api = AnuNekoAPI(token=token, cookie=cookie)
        
        print("正在获取模型列表...")
        
        # 调用 model_view 方法获取模型列表
        models = await api.model_view()
        
        if models:
            print("获取模型列表成功！")
            print("=" * 50)
            print(models)
            # 打印模型列表
            if "models" in models:
                print("可用模型:")
                for i, model in enumerate(models["models"], 1):
                    print(f"  {i}. {model}")
            
            # 打印默认模型
            if "default_model" in models:
                print(f"\n默认模型: {models['default_model']}")
            
            # 打印完整响应（如果有其他字段）
            print("\n完整响应:")
            for key, value in models.items():
                if key not in ["models", "default_model"]:
                    print(f"  {key}: {value}")
        else:
            print("获取模型列表失败，请检查 token 和 cookie 是否正确")
    
    except ValueError as e:
        print(f"错误: {e}")
        print("请确保提供了有效的 token")
    except Exception as e:
        print(f"发生异常: {e}")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())