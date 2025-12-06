from flask import Blueprint

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("", methods=["GET"])
def chat():
    """模型列表端点"""
    return "test"