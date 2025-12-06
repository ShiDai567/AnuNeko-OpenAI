# -*- coding: utf-8 -*-
"""
AnuNeko API Python 封装
基于 send.py 中的 API 调用实现，支持异步操作
"""

import json
import os
import httpx
from typing import Dict, List, Optional, Union, AsyncGenerator


class AnuNekoAPI:
    """AnuNeko API 封装类"""
    
    # API 地址
    CHAT_API_URL = "https://anuneko.com/api/v1/chat"
    STREAM_API_URL = "https://anuneko.com/api/v1/msg/{uuid}/stream"
    MODEL_VIEW_URL = "https://anuneko.com/api/v1/user/view"
    SELECT_CHOICE_URL = "https://anuneko.com/api/v1/msg/select-choice"
    SELECT_MODEL_URL = "https://anuneko.com/api/v1/user/select_model"
    
    def __init__(self, token: str = None, cookie: str = None):
        """
        初始化 AnuNeko API 客户端
        
        Args:
            token: 账号 Token，如果为 None 则从环境变量 ANUNEKO_TOKEN 获取
            cookie: 可选的 Cookie 值，如果为 None 则从环境变量 ANUNEKO_COOKIE 获取
        """
        self.token = token or os.environ.get("ANUNEKO_TOKEN")
        self.cookie = cookie or os.environ.get("ANUNEKO_COOKIE")
        
        if not self.token:
            raise ValueError("Token 未提供，请设置 ANUNEKO_TOKEN 环境变量或直接传入 token 参数")
    
    def build_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """
        构建请求头
        
        Args:
            content_type: 内容类型，默认为 application/json
            
        Returns:
            请求头字典
        """
        headers = {
            "accept": "*/*",
            "content-type": content_type,
            "origin": "https://anuneko.com",
            "referer": "https://anuneko.com/",
            "user-agent": "Mozilla/5.0",
            "x-app_id": "com.anuttacon.neko",
            "x-client_type": "4",
            "x-device_id": "7b75a432-6b24-48ad-b9d3-3dc57648e3e3",
            "x-token": self.token,
        }
        
        if self.cookie:
            headers["Cookie"] = self.cookie
            
        return headers
    
    async def model_view(self) -> Dict[str, Union[str, List[str]]]:
    
        """
        获取模型列表
        
        Returns:
            模型列表，包含模型名称
        """
        headers = self.build_headers()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(self.MODEL_VIEW_URL, headers=headers)
                resp_json = resp.json()
                return resp_json
        except Exception:
            pass
            
        return None
    async def create_session(self, model: str = "Orange Cat") -> Optional[str]:
        """
        创建新会话
        
        Args:
            model: 模型名称，默认为 "Orange Cat"
            
        Returns:
            会话 ID，如果创建失败则返回 None
        """
        headers = self.build_headers()
        data = json.dumps({"model": model})
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(self.CHAT_API_URL, headers=headers, content=data)
                resp_json = resp.json()
                
                chat_id = resp_json.get("chat_id") or resp_json.get("id")
                if chat_id:
                    # 切换模型以确保一致性
                    await self.switch_model(chat_id, model)
                    return chat_id
        except Exception:
            pass
            
        return None
    
    async def switch_model(self, chat_id: str, model_name: str) -> bool:
        """
        切换模型
        
        Args:
            chat_id: 会话 ID
            model_name: 模型名称 ("Orange Cat" 或 "Exotic Shorthair")
            
        Returns:
            是否切换成功
        """
        headers = self.build_headers()
        data = json.dumps({"chat_id": chat_id, "model": model_name})
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(self.SELECT_MODEL_URL, headers=headers, content=data)
                return resp.status_code == 200
        except:
            pass
            
        return False
    
    async def send_choice(self, msg_id: str, choice_idx: int = 0) -> bool:
        """
        发送选择回复
        
        Args:
            msg_id: 消息 ID
            choice_idx: 选择的回复索引，默认为 0
            
        Returns:
            是否发送成功
        """
        headers = self.build_headers()
        data = json.dumps({"msg_id": msg_id, "choice_idx": choice_idx})
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(self.SELECT_CHOICE_URL, headers=headers, content=data)
                return resp.status_code == 200
        except:
            pass
            
        return False
    
    async def stream_reply(self, session_uuid: str, text: str) -> str:
        """
        流式发送消息并获取回复
        
        Args:
            session_uuid: 会话 UUID
            text: 要发送的文本
            
        Returns:
            AI 的回复文本
        """
        headers = self.build_headers("text/plain")
        
        url = self.STREAM_API_URL.format(uuid=session_uuid)
        data = json.dumps({"contents": [text]}, ensure_ascii=False)
        
        result = ""
        current_msg_id = None
        
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, headers=headers, content=data) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        
                        # 处理错误响应
                        if not line.startswith("data: "):
                            try:
                                error_json = json.loads(line)
                                if error_json.get("code") == "chat_choice_shown":
                                    return "⚠️ 检测到对话分支未选择，请重试或新建会话。"
                            except:
                                pass
                            continue
                        
                        # 处理 data: {}
                        try:
                            raw_json = line[6:]
                            if not raw_json.strip():
                                continue
                                
                            j = json.loads(raw_json)
                            
                            # 只要出现 msg_id 就更新，流最后一条通常是 assistmsg，也就是我们要的 ID
                            if "msg_id" in j:
                                current_msg_id = j["msg_id"]
                            
                            # 如果有 'c' 字段，说明是多分支内容
                            # 格式如: {"c":[{"v":"..."},{"v":"...","c":1}]}
                            if "c" in j and isinstance(j["c"], list):
                                for choice in j["c"]:
                                    # 默认选项 idx=0，可能显式 c=0 或隐式(无 c 字段)
                                    idx = choice.get("c", 0)
                                    if idx == 0:
                                        if "v" in choice:
                                            result += choice["v"]
                            
                            # 常规内容 (兼容旧格式或无分支情况)
                            elif "v" in j and isinstance(j["v"], str):
                                result += j["v"]
                                
                        except:
                            continue
            
            # 流结束后，如果有 msg_id，自动确认选择第一项，确保下次对话正常
            if current_msg_id:
                await self.send_choice(current_msg_id)
                
        except Exception:
            return "请求失败，请稍后再试。"
            
        return result
    
    async def stream_reply_generator(self, session_uuid: str, text: str) -> AsyncGenerator[str, None]:
        """
        流式发送消息并生成器方式获取回复
        
        Args:
            session_uuid: 会话 UUID
            text: 要发送的文本
            
        Yields:
            AI 的回复文本片段
        """
        headers = self.build_headers("text/plain")
        
        url = self.STREAM_API_URL.format(uuid=session_uuid)
        data = json.dumps({"contents": [text]}, ensure_ascii=False)
        
        current_msg_id = None
        
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, headers=headers, content=data) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        
                        # 处理错误响应
                        if not line.startswith("data: "):
                            try:
                                error_json = json.loads(line)
                                if error_json.get("code") == "chat_choice_shown":
                                    yield "⚠️ 检测到对话分支未选择，请重试或新建会话。"
                                    return
                            except:
                                pass
                            continue
                        
                        # 处理 data: {}
                        try:
                            raw_json = line[6:]
                            if not raw_json.strip():
                                continue
                                
                            j = json.loads(raw_json)
                            
                            # 只要出现 msg_id 就更新，流最后一条通常是 assistmsg，也就是我们要的 ID
                            if "msg_id" in j:
                                current_msg_id = j["msg_id"]
                            
                            # 如果有 'c' 字段，说明是多分支内容
                            # 格式如: {"c":[{"v":"..."},{"v":"...","c":1}]}
                            if "c" in j and isinstance(j["c"], list):
                                for choice in j["c"]:
                                    # 默认选项 idx=0，可能显式 c=0 或隐式(无 c 字段)
                                    idx = choice.get("c", 0)
                                    if idx == 0:
                                        if "v" in choice:
                                            yield choice["v"]
                            
                            # 常规内容 (兼容旧格式或无分支情况)
                            elif "v" in j and isinstance(j["v"], str):
                                yield j["v"]
                                
                        except:
                            continue
            
            # 流结束后，如果有 msg_id，自动确认选择第一项，确保下次对话正常
            if current_msg_id:
                await self.send_choice(current_msg_id)
                
        except Exception:
            yield "请求失败，请稍后再试。"