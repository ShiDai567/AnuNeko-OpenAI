#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnuNeko API 测试脚本
用于测试 anuneko_api.py 中的异步函数
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import asyncio
from anuneko_api import AnuNekoAPI, create_session, send_message, switch_model, select_choice


class TestAnuNekoAPI(unittest.TestCase):
    """AnuNekoAPI 测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.token = "test_token"
        self.cookie = "test_cookie"
        self.chat_id = "test_chat_id"
        self.msg_id = "test_msg_id"
        self.api = AnuNekoAPI(self.token, self.cookie)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.api.token, self.token)
        self.assertEqual(self.api.cookie, self.cookie)
        self.assertEqual(self.api.CHAT_API_URL, "https://anuneko.com/api/v1/chat")
        self.assertEqual(self.api.STREAM_API_URL, "https://anuneko.com/api/v1/msg/{uuid}/stream")
        self.assertEqual(self.api.SELECT_CHOICE_URL, "https://anuneko.com/api/v1/msg/select-choice")
        self.assertEqual(self.api.SELECT_MODEL_URL, "https://anuneko.com/api/v1/user/select_model")
    
    def test_init_without_token(self):
        """测试不带 token 的初始化"""
        with self.assertRaises(ValueError):
            AnuNekoAPI()
    
    def test_build_headers(self):
        """测试构建请求头"""
        headers = self.api.build_headers()
        
        self.assertEqual(headers["x-token"], self.token)
        self.assertEqual(headers["Cookie"], self.cookie)
        self.assertEqual(headers["content-type"], "application/json")
        self.assertIn("x-app_id", headers)
        self.assertIn("x-client_type", headers)
        self.assertIn("x-device_id", headers)
        
        # 测试不同的 content_type
        headers_json = self.api.build_headers("application/json")
        self.assertEqual(headers_json["content-type"], "application/json")
        
        headers_text = self.api.build_headers("text/plain")
        self.assertEqual(headers_text["content-type"], "text/plain")
    
    @patch('anuneko_api.httpx.AsyncClient')
    async def test_create_session(self, mock_client_class):
        """测试创建会话"""
        # 模拟响应
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"chat_id": "new_chat_id"}
        mock_client.post.return_value = mock_response
        
        # 调用函数
        result = await self.api.create_session("Orange Cat")
        
        # 验证调用
        expected_url = self.api.CHAT_API_URL
        expected_data = json.dumps({"model": "Orange Cat"})
        mock_client.post.assert_called_once_with(expected_url, headers=self.api.build_headers(), content=expected_data)
        
        # 验证返回值
        self.assertEqual(result, "new_chat_id")
    
    @patch('anuneko_api.httpx.AsyncClient')
    async def test_switch_model(self, mock_client_class):
        """测试切换模型"""
        # 模拟响应
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        
        # 调用函数
        result = await self.api.switch_model(self.chat_id, "Orange Cat")
        
        # 验证调用
        expected_url = self.api.SELECT_MODEL_URL
        expected_data = json.dumps({"chat_id": self.chat_id, "model": "Orange Cat"})
        mock_client.post.assert_called_once_with(expected_url, headers=self.api.build_headers(), content=expected_data)
        
        # 验证返回值
        self.assertTrue(result)
    
    @patch('anuneko_api.httpx.AsyncClient')
    async def test_send_choice(self, mock_client_class):
        """测试发送选择回复"""
        # 模拟响应
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        
        # 调用函数
        result = await self.api.send_choice(self.msg_id, 1)
        
        # 验证调用
        expected_url = self.api.SELECT_CHOICE_URL
        expected_data = json.dumps({"msg_id": self.msg_id, "choice_idx": 1})
        mock_client.post.assert_called_once_with(expected_url, headers=self.api.build_headers(), content=expected_data)
        
        # 验证返回值
        self.assertTrue(result)
    
    @patch('anuneko_api.httpx.AsyncClient')
    async def test_stream_reply(self, mock_client_class):
        """测试流式回复"""
        # 模拟响应
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # 模拟流式响应
        mock_stream = AsyncMock()
        mock_client.stream.return_value.__aenter__.return_value = mock_stream
        
        # 模拟流数据
        mock_stream.aiter_lines.return_value = [
            'data: {"v": "Hello"}',
            'data: {"v": " world"}',
            'data: {"msg_id": "test_msg_id"}',
            ''
        ]
        
        # 调用函数
        result = await self.api.stream_reply(self.chat_id, "Hi")
        
        # 验证调用
        expected_url = self.api.STREAM_API_URL.format(uuid=self.chat_id)
        expected_data = json.dumps({"contents": ["Hi"]}, ensure_ascii=False)
        mock_client.stream.assert_called_once_with(
            "POST", expected_url, headers=self.api.build_headers("text/plain"), content=expected_data
        )
        
        # 验证返回值
        self.assertEqual(result, "Hello world")
    
    @patch('anuneko_api.httpx.AsyncClient')
    async def test_stream_reply_with_choices(self, mock_client_class):
        """测试带选择的流式回复"""
        # 模拟响应
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # 模拟流式响应
        mock_stream = AsyncMock()
        mock_client.stream.return_value.__aenter__.return_value = mock_stream
        
        # 模拟带选择的流数据
        mock_stream.aiter_lines.return_value = [
            'data: {"c":[{"v":"Choice 1"},{"v":"Choice 2","c":1}]}',
            'data: {"msg_id": "test_msg_id"}',
            ''
        ]
        
        # 调用函数
        result = await self.api.stream_reply(self.chat_id, "Hi")
        
        # 验证返回值
        self.assertEqual(result, "Choice 1")
    
    @patch('anuneko_api.httpx.AsyncClient')
    async def test_stream_reply_error(self, mock_client_class):
        """测试流式回复错误处理"""
        # 模拟响应
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # 模拟流式响应
        mock_stream = AsyncMock()
        mock_client.stream.return_value.__aenter__.return_value = mock_stream
        
        # 模拟错误流数据
        mock_stream.aiter_lines.return_value = [
            '{"code":"chat_choice_shown"}',
            ''
        ]
        
        # 调用函数
        result = await self.api.stream_reply(self.chat_id, "Hi")
        
        # 验证返回值
        self.assertEqual(result, "⚠️ 检测到对话分支未选择，请重试或新建会话。")


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试类"""
    
    @patch('anuneko_api.AnuNekoAPI')
    async def test_create_session(self, mock_api_class):
        """测试创建会话便捷函数"""
        mock_api = AsyncMock()
        mock_api_class.return_value = mock_api
        mock_api.create_session.return_value = "new_chat_id"
        
        result = await create_session("token", "cookie", "Orange Cat")
        
        mock_api_class.assert_called_once_with("token", "cookie")
        mock_api.create_session.assert_called_once_with("Orange Cat")
        self.assertEqual(result, "new_chat_id")
    
    @patch('anuneko_api.AnuNekoAPI')
    async def test_send_message(self, mock_api_class):
        """测试发送消息便捷函数"""
        mock_api = AsyncMock()
        mock_api_class.return_value = mock_api
        mock_api.stream_reply.return_value = "AI response"
        
        result = await send_message("token", "chat_id", ["message"], "cookie")
        
        mock_api_class.assert_called_once_with("token", "cookie")
        mock_api.stream_reply.assert_called_once_with("chat_id", "message")
        self.assertEqual(result, "AI response")
    
    @patch('anuneko_api.AnuNekoAPI')
    async def test_switch_model(self, mock_api_class):
        """测试切换模型便捷函数"""
        mock_api = AsyncMock()
        mock_api_class.return_value = mock_api
        mock_api.switch_model.return_value = True
        
        result = await switch_model("token", "chat_id", "Orange Cat", "cookie")
        
        mock_api_class.assert_called_once_with("token", "cookie")
        mock_api.switch_model.assert_called_once_with("chat_id", "Orange Cat")
        self.assertTrue(result)
    
    @patch('anuneko_api.AnuNekoAPI')
    async def test_select_choice(self, mock_api_class):
        """测试选择回复便捷函数"""
        mock_api = AsyncMock()
        mock_api_class.return_value = mock_api
        mock_api.send_choice.return_value = True
        
        result = await select_choice("token", "msg_id", 1, "cookie")
        
        mock_api_class.assert_called_once_with("token", "cookie")
        mock_api.send_choice.assert_called_once_with("msg_id", 1)
        self.assertTrue(result)


# 异步测试运行器
def run_async_test(test_func):
    """运行异步测试函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(test_func())
    finally:
        loop.close()


# 为异步测试创建包装器
def async_test(test_func):
    """异步测试装饰器"""
    def wrapper(self):
        return run_async_test(lambda: test_func(self))
    return wrapper


# 应用装饰器到异步测试方法
TestAnuNekoAPI.test_create_session = async_test(TestAnuNekoAPI.test_create_session)
TestAnuNekoAPI.test_switch_model = async_test(TestAnuNekoAPI.test_switch_model)
TestAnuNekoAPI.test_send_choice = async_test(TestAnuNekoAPI.test_send_choice)
TestAnuNekoAPI.test_stream_reply = async_test(TestAnuNekoAPI.test_stream_reply)
TestAnuNekoAPI.test_stream_reply_with_choices = async_test(TestAnuNekoAPI.test_stream_reply_with_choices)
TestAnuNekoAPI.test_stream_reply_error = async_test(TestAnuNekoAPI.test_stream_reply_error)

TestConvenienceFunctions.test_create_session = async_test(TestConvenienceFunctions.test_create_session)
TestConvenienceFunctions.test_send_message = async_test(TestConvenienceFunctions.test_send_message)
TestConvenienceFunctions.test_switch_model = async_test(TestConvenienceFunctions.test_switch_model)
TestConvenienceFunctions.test_select_choice = async_test(TestConvenienceFunctions.test_select_choice)


if __name__ == '__main__':
    print("运行 AnuNeko API 异步测试...")
    unittest.main(verbosity=2)