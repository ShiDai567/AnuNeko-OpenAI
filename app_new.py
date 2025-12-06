import os

import logging
from logging.handlers import RotatingFileHandler

from flask import Flask,jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 导入路由
from app.main.routes import health_bp, sessions_dp
from app.api.routes import api_bp

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)

# 配置日志
# 设置日志文件路径
log_path = os.environ.get("LOG_PATH", "logs")
log_name = os.environ.get("LOG_NAME", "anuneko-openai")
if not os.path.exists(log_path):
    os.mkdir(log_path)

# 配置文件处理器
file_handler = RotatingFileHandler(
    f'{log_path}/{log_name}.log',
    maxBytes=10240000,  # 10MB
    backupCount=10
)

# 设置日志格式
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s [in %(pathname)s:%(lineno)d]'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# 添加处理器到应用日志器
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)



# 注册路由
app.register_blueprint(
    blueprint=health_bp,
    url_prefix="/health"
)

app.register_blueprint(
    blueprint=sessions_dp,
    url_prefix="/sessions"
)

app.register_blueprint(
    blueprint=api_bp,
    url_prefix="/api"
)

@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        "error": {
            "message": "端点不存在",
            "type": "invalid_request_error"
        }
    }), 404


if __name__ == "__main__":
    # 从环境变量获取配置
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "8000"))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    app.logger.info('启动 OpenAI API 兼容服务器...')
    app.logger.info(f"地址: http://{host}:{port}")
    app.logger.info(f"调试模式: {debug}")
    
    # 检查环境变量
    if not os.environ.get("ANUNEKO_TOKEN"):
        app.logger.error("⚠️ 警告: 未设置 ANUNEKO_TOKEN 环境变量")
        app.logger.error("   请设置 AnuNeko 账号 Token")
    
    # 启动服务器
    app.run(host=host, port=port, debug=debug)