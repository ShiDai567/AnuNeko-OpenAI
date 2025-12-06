from flask import jsonify
from datetime import datetime

def check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })