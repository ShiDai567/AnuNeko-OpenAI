#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 服务器，模仿 OpenAI API 接口
使用 AnuNeko API 作为后端
"""

import json
import os
import time
import uuid
import asyncio
from typing import Dict, List, Optional, Any, Generator
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from anuneko_api import AnuNekoAPI

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 全局变量存储会话信息
sessions: Dict[str, Dict[str, Any]] = {}

# 默认配置
DEFAULT_MODEL = "gpt-3.5-turbo"  # 对应 AnuNeko 的 "Orange Cat"
MODEL_MAPPING = {
    "gpt-3.5-turbo": "Orange Cat",  # 橘猫
    "gpt-4": "Exotic Shorthair"     # 黑猫
}

def get_anuneko_client() -> AnuNekoAPI:
    """获取 AnuNeko API 客户端"""
    token = os.environ.get("ANUNEKO_TOKEN")
    cookie = os.environ.get("ANUNEKO_COOKIE")
    
    if not token:
        raise ValueError("未设置 ANUNEKO_TOKEN 环境变量")
    
    return AnuNekoAPI(token, cookie)

def map_openai_to_anuneko_model(model: str) -> str:
    """将 OpenAI 模型名映射到 AnuNeko 模型名"""
    return MODEL_MAPPING.get(model, "Orange Cat")

def format_openai_response(anuneko_response: str, model: str, created: int, 
                          finish_reason: str = "stop") -> Dict[str, Any]:
    """将 AnuNeko 响应格式化为 OpenAI 格式"""
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": anuneko_response
                },
                "finish_reason": finish_reason
            }
        ],
        "usage": {
            "prompt_tokens": 0,  # AnuNeko 不提供 token 计数
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

def format_openai_chunk(anuneko_chunk: str, model: str, created: int, 
                       finish_reason: Optional[str] = None) -> str:
    """将 AnuNeko 响应块格式化为 OpenAI 流式格式"""
    chunk_data = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {
                    "content": anuneko_chunk
                },
                "finish_reason": finish_reason
            }
        ]
    }
    
    return f"data: {json.dumps(chunk_data)}\n\n"

@app.route("/v1/models", methods=["GET"])
def list_models():
    """列出可用模型，模仿 OpenAI API"""
    try:
        models = [
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "anuneko-orange-cat"
            },
            {
                "id": "gpt-4",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "anuneko-exotic-shorthair"
            }
        ]
        
        return jsonify({
            "object": "list",
            "data": models
        })
    except Exception as e:
        return jsonify({"error": {"message": str(e), "type": "internal_error"}}), 500

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """聊天完成端点，模仿 OpenAI API"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": {"message": "Missing request body", "type": "invalid_request_error"}}), 400
        
        # 提取参数
        messages = data.get("messages", [])
        model = data.get("model", DEFAULT_MODEL)
        stream = data.get("stream", False)
        temperature = data.get("temperature", 1.0)
        max_tokens = data.get("max_tokens", None)
        
        if not messages:
            return jsonify({"error": {"message": "Missing messages", "type": "invalid_request_error"}}), 400
        
        # 提取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            return jsonify({"error": {"message": "No user message found", "type": "invalid_request_error"}}), 400
        
        # 创建或获取会话
        session_id = request.headers.get("X-Session-ID")
        if not session_id or session_id not in sessions:
            # 创建新会话
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                "created_at": time.time(),
                "model": model,
                "anuneko_chat_id": None
            }
        
        session = sessions[session_id]
        created = int(time.time())
        
        # 获取 AnuNeko 客户端
        api = get_anuneko_client()
        
        # 如果需要切换模型
        if session["model"] != model:
            session["model"] = model
        
        # 异步处理 AnuNeko API 调用
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 创建或获取 AnuNeko 会话
            if not session.get("anuneko_chat_id"):
                anuneko_model = map_openai_to_anuneko_model(model)
                anuneko_chat_id = loop.run_until_complete(api.create_session(anuneko_model))
                if not anuneko_chat_id:
                    return jsonify({"error": {"message": "Failed to create AnuNeko session", "type": "api_error"}}), 500
                session["anuneko_chat_id"] = anuneko_chat_id
            else:
                # 切换模型（如果需要）
                anuneko_model = map_openai_to_anuneko_model(model)
                loop.run_until_complete(api.switch_model(session["anuneko_chat_id"], anuneko_model))
            
            # 处理流式响应
            if stream:
                def generate():
                    try:
                        response_text = ""
                        async for chunk in api.stream_reply_generator(session["anuneko_chat_id"], user_message):
                            response_text += chunk
                            yield format_openai_chunk(chunk, model, created)
                        
                        # 发送结束标记
                        yield format_openai_chunk("", model, created, finish_reason="stop")
                        yield "data: [DONE]\n\n"
                    except Exception as e:
                        error_chunk = {
                            "error": {
                                "message": str(e),
                                "type": "api_error"
                            }
                        }
                        yield f"data: {json.dumps(error_chunk)}\n\n"
                
                return Response(stream_with_context(generate()), 
                              mimetype="text/event-stream",
                              headers={
                                  "Cache-Control": "no-cache",
                                  "Connection": "keep-alive",
                                  "X-Session-ID": session_id
                              })
            else:
                # 非流式响应
                response_text = loop.run_until_complete(api.stream_reply(session["anuneko_chat_id"], user_message))
                openai_response = format_openai_response(response_text, model, created)
                
                return jsonify(openai_response)
        
        finally:
            loop.close()
    
    except Exception as e:
        return jsonify({"error": {"message": str(e), "type": "internal_error"}}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy", "timestamp": int(time.time())})

@app.route("/sessions", methods=["GET"])
def list_sessions():
    """列出当前会话"""
    session_list = []
    for session_id, session_data in sessions.items():
        session_list.append({
            "id": session_id,
            "created_at": session_data["created_at"],
            "model": session_data["model"],
            "has_anuneko_chat": bool(session_data.get("anuneko_chat_id"))
        })
    
    return jsonify({"sessions": session_list})

@app.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """删除指定会话"""
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({"message": "Session deleted successfully"})
    else:
        return jsonify({"error": {"message": "Session not found", "type": "not_found"}}), 404

@app.errorhandler(404)
def not_found(error):
    """处理 404 错误"""
    return jsonify({"error": {"message": "Not found", "type": "not_found"}}), 404

@app.errorhandler(500)
def internal_error(error):
    """处理 500 错误"""
    return jsonify({"error": {"message": "Internal server error", "type": "internal_error"}}), 500

if __name__ == "__main__":
    # 检查环境变量
    if not os.environ.get("ANUNEKO_TOKEN"):
        print("错误：请设置 ANUNEKO_TOKEN 环境变量")
        exit(1)
    
    # 启动服务器
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    print(f"启动 OpenAI 兼容 API 服务器...")
    print(f"地址: http://{host}:{port}")
    print(f"健康检查: http://{host}:{port}/health")
    print(f"模型列表: http://{host}:{port}/v1/models")
    print(f"聊天完成: http://{host}:{port}/v1/chat/completions")
    
    app.run(host=host, port=port, debug=debug)