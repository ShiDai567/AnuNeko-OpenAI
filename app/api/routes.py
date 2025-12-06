from flask import Blueprint
from app.api.v1.routes import api_v1_bp

api_bp = Blueprint("api", __name__)

# 注册 api-v1 版本路由
api_bp.register_blueprint(
    blueprint=api_v1_bp,
    url_prefix="/v1"
)