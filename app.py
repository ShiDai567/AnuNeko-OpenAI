#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI API 兼容服务器
将 AnuNeko AI 作为 OpenAI API 的替代品使用
"""

import os
import json
import time
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Generator, Any

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from anuneko_api import AnuNekoAPI

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)

# 全局变量存储会话信息
sessions: Dict[str, Dict[str, Any]] = {}
anuneko_api: Optional[AnuNekoAPI] = None

# 动态模型映射表
MODEL_MAPPING: Dict[str, str] = {}

def update_model_mapping():
    """动态更新模型映射表"""
    global MODEL_MAPPING
    try:
        api = get_anuneko_api()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            anuneko_models = loop.run_until_complete(api.model_view())
        finally:
            loop.close()
        
        if anuneko_models and "models" in anuneko_models:
            # 清空现有映射
            MODEL_MAPPING.clear()
            
            # 为每个AnuNeko模型创建映射
            for anuneko_model in anuneko_models["models"]:
                # 生成模型ID
                openai_model = f"mihoyo-{anuneko_model.lower().replace(' ', '_')}"
                MODEL_MAPPING[openai_model] = anuneko_model
            
            print(f"已更新模型映射表，共{len(MODEL_MAPPING)}个模型")
        else:
            # 如果无法获取，设置默认映射
            MODEL_MAPPING.clear()
            MODEL_MAPPING["mihoyo-orange_cat"] = "Orange Cat"
            print("无法获取AnuNeko模型，使用默认映射")
            
    except Exception as e:
        print(f"更新模型映射失败: {str(e)}")
        # 设置默认映射作为后备
        MODEL_MAPPING.clear()
        MODEL_MAPPING["mihoyo-orange_cat"] = "Orange Cat"

def get_anuneko_api() -> AnuNekoAPI:
    """获取 AnuNeko API 实例"""
    global anuneko_api
    if anuneko_api is None:
        anuneko_api = AnuNekoAPI()
    return anuneko_api

def get_session_for_request(request_data: Dict[str, Any]) -> str:
    """根据请求获取或创建会话"""
    model = request_data.get("model", "mihoyo-orange_cat")
    
    # 确保模型映射是最新的
    if not MODEL_MAPPING:
        update_model_mapping()
    
    # 从动态映射表中获取AnuNeko模型名
    anuneko_model = MODEL_MAPPING.get(model)
    
    if not anuneko_model:
        # 如果映射中没有，默认使用Orange Cat
        print("未找到模型映射，使用默认模型：Orange Cat")
        anuneko_model = "Orange Cat"
    
    # 尝试从请求中获取会话ID（如果有的话）
    session_id = request_data.get("session_id")
    
    if session_id and session_id in sessions:
        session = sessions[session_id]
        # 检查模型是否匹配，如果不匹配则切换模型
        if session.get("model") != anuneko_model:
            api = get_anuneko_api()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(
                    api.switch_model(session["anuneko_chat_id"], anuneko_model)
                )
                if success:
                    session["model"] = anuneko_model
            finally:
                loop.close()
        return session_id
    
    # 创建新会话
    api = get_anuneko_api()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        anuneko_chat_id = loop.run_until_complete(api.create_session(anuneko_model))
        if anuneko_chat_id:
            new_session_id = str(uuid.uuid4())
            sessions[new_session_id] = {
                "id": new_session_id,
                "anuneko_chat_id": anuneko_chat_id,
                "model": anuneko_model,
                "openai_model": model,
                "created_at": datetime.now().isoformat(),
                "has_anuneko_chat": True
            }
            return new_session_id
    finally:
        loop.close()
    
    raise Exception("无法创建会话")

def format_openai_response(model: str, content: str, session_id: str = None) -> Dict[str, Any]:
    """格式化 OpenAI API 响应"""
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,  # AnuNeko 不提供 token 计数
            "completion_tokens": 0,
            "total_tokens": 0
        },
        "session_id": session_id
    }

def format_openai_chunk(model: str, content: str, session_id: str = None) -> str:
    """格式化 OpenAI API 流式响应块"""
    chunk = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {
                    "content": content
                },
                "finish_reason": None
            }
        ]
    }
    
    if session_id:
        chunk["session_id"] = session_id
    
    return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

@app.route("/health", methods=["GET"])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route("/v1/models", methods=["GET"])
def list_models():
    """列出可用模型"""
    try:
        # 尝试从AnuNeko API获取真实模型列表
        api = get_anuneko_api()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            anuneko_models = loop.run_until_complete(api.model_view())
        finally:
            loop.close()
        
        models = []
        
        # 如果成功获取到AnuNeko模型，使用真实数据
        if anuneko_models and "models" in anuneko_models:
            # 更新模型映射表
            MODEL_MAPPING.clear()
            
            # 为每个AnuNeko模型创建对应的OpenAI模型条目
            for anuneko_model in anuneko_models["models"]:
                # 生成模型ID
                openai_model = f"mihoyo-{anuneko_model.lower().replace(' ', '_')}"
                MODEL_MAPPING[openai_model] = anuneko_model
                
                models.append({
                    "id": openai_model,
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "anuneko",
                    "permission": [],
                    "root": openai_model,
                    "parent": None,
                    "anuneko_model": anuneko_model,
                    "anuneko_model_id": anuneko_models["models"].index(anuneko_model)
                })
            
            print(f"已更新模型映射表，共{len(MODEL_MAPPING)}个模型")
        else:
            # 如果无法获取真实模型，使用默认映射
            MODEL_MAPPING.clear()
            MODEL_MAPPING["mihoyo-orange_cat"] = "Orange Cat"
            
            models.append({
                "id": "mihoyo-orange_cat",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "anuneko",
                "permission": [],
                "root": "mihoyo-orange_cat",
                "parent": None,
                "anuneko_model": "Orange Cat",
                "note": "default_model"
            })
        return jsonify({
            "object": "list",
            "data": models,
            "anuneko_api_response": anuneko_models  # 调试信息，可选
        })
    
    except Exception as e:
        # 如果出错，设置默认映射作为后备
        MODEL_MAPPING.clear()
        MODEL_MAPPING["mihoyo-orange_cat"] = "Orange Cat"
        
        models = [{
            "id": "mihoyo-orange_cat",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "anuneko",
            "permission": [],
            "root": "mihoyo-orange_cat",
            "parent": None,
            "anuneko_model": "Orange Cat",
            "note": "fallback_default_model"
        }]
        
        return jsonify({
            "object": "list",
            "data": models,
            "error": f"无法获取AnuNeko模型列表，使用默认模型: {str(e)}"
        })

@app.route("/sessions", methods=["GET"])
def list_sessions():
    """列出会话"""
    session_list = []
    for session_id, session_data in sessions.items():
        session_list.append({
            "id": session_data["id"],
            "model": session_data["openai_model"],
            "created_at": session_data["created_at"],
            "has_anuneko_chat": session_data["has_anuneko_chat"]
        })
    
    return jsonify({
        "sessions": session_list,
        "total": len(session_list)
    })

@app.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id: str):
    """删除会话"""
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({"status": "success", "message": "会话已删除"})
    else:
        return jsonify({"status": "error", "message": "会话不存在"}), 404

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """聊天完成端点"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": {"message": "请求体不能为空", "type": "invalid_request_error"}}), 400
        
        messages = request_data.get("messages", [])
        if not messages:
            return jsonify({"error": {"message": "messages 不能为空", "type": "invalid_request_error"}}), 400
        
        # 获取最后一条用户消息
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            return jsonify({"error": {"message": "未找到用户消息", "type": "invalid_request_error"}}), 400
        
        model = request_data.get("model", "gpt-3.5-turbo")
        stream = request_data.get("stream", False)
        
        # 获取或创建会话
        session_id = get_session_for_request(request_data)
        session = sessions[session_id]
        
        if stream:
            # 流式响应
            def generate():
                api = get_anuneko_api()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    async def stream_generator():
                        async for chunk in api.stream_reply_generator(
                            session["anuneko_chat_id"], user_message
                        ):
                            yield format_openai_chunk(model, chunk, session_id)
                        
                        # 发送结束块
                        end_chunk = {
                            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {},
                                    "finish_reason": "stop"
                                }
                            ]
                        }
                        yield f"data: {json.dumps(end_chunk, ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"
                    
                    # 运行异步生成器
                    async_gen = stream_generator()
                    while True:
                        try:
                            chunk = loop.run_until_complete(async_gen.__anext__())
                            yield chunk
                        except StopAsyncIteration:
                            break
                finally:
                    loop.close()
            
            return Response(
                stream_with_context(generate()),
                mimetype="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        else:
            # 非流式响应
            api = get_anuneko_api()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                response = loop.run_until_complete(
                    api.stream_reply(session["anuneko_chat_id"], user_message)
                )
                return jsonify(format_openai_response(model, response, session_id))
            finally:
                loop.close()
    
    except Exception as e:
        return jsonify({
            "error": {
                "message": f"服务器内部错误: {str(e)}",
                "type": "server_error"
            }
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        "error": {
            "message": "端点不存在",
            "type": "invalid_request_error"
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        "error": {
            "message": "服务器内部错误",
            "type": "server_error"
        }
    }), 500

if __name__ == "__main__":
    # 从环境变量获取配置
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "8000"))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    print("启动 OpenAI API 兼容服务器...")
    print(f"地址: http://{host}:{port}")
    print(f"调试模式: {debug}")
    
    # 检查环境变量
    if not os.environ.get("ANUNEKO_TOKEN"):
        print("⚠️ 警告: 未设置 ANUNEKO_TOKEN 环境变量")
        print("   请设置 AnuNeko 账号 Token")
    
    # 启动服务器
    app.run(host=host, port=port, debug=debug)