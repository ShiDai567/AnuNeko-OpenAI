"""
共享状态模块
存储应用程序的全局状态变量
"""

from typing import Dict, Any

# 全局变量存储会话信息
sessions: Dict[str, Dict[str, Any]] = {}