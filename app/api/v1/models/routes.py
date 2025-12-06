from flask import Blueprint

models_bp = Blueprint("models", __name__)

@models_bp.route("", methods=["GET"])
def models():
    """模型列表端点"""
    return "test"