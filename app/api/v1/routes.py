from flask import Blueprint
from app.api.v1.chat.routes import chat_bp
from app.api.v1.models.routes import models_bp

# 声明 api-v1 蓝图
api_v1_bp = Blueprint("api_v1", __name__)

# 注册路由 chat
api_v1_bp.register_blueprint(
    blueprint=chat_bp,
    url_prefix="/chat"
)

# 注册路由 models
api_v1_bp.register_blueprint(
    blueprint=models_bp,
    url_prefix="/models"
)