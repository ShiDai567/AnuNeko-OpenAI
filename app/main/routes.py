from flask import Blueprint
# 导入处理函数
from . import health

# 创建蓝图
health_bp = Blueprint("health", __name__)



# 定义路由
@health_bp.route("", methods=["GET"])
@health_bp.route("/", methods=["GET"])
def health_check():
    return health.check()

