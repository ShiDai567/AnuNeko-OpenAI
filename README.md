# AnuNeko OpenAI API 兼容服务器

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个将 AnuNeko AI 作为 OpenAI API 替代品的服务器，允许您使用标准的 OpenAI 客户端库与 AnuNeko AI 模型进行交互。

## 写在前面

1. 此项目基于 [AnuNeko](https://anuneko.com/) 提供的 AI 模型服务，并实现了 OpenAI API 兼容性。
2. 部分逆向接口参考了 [二叉树树](https://2x.nz/posts/anuneko/)博客的帮助。还请给他的[ AnuNeko_NoneBot2_Plugins](https://github.com/afoim/AnuNeko_NoneBot2_Plugins/blob/main/anuneko.py)一个Star！

## 功能特性

- 🔄 **完全兼容 OpenAI API**: 支持标准的 OpenAI API 格式和客户端库
- 🤖 **多模型支持**: 支持橘猫(Orange Cat)和黑猫(Exotic Shorthair)等模型
- 🌊 **流式响应**: 支持流式和非流式两种响应模式
- 🔄 **会话管理**: 自动管理和维护与 AnuNeko 的会话
- 📊 **动态模型映射**: 自动获取并映射可用的 AnuNeko 模型
- 🔧 **易于集成**: 只需更改 base_url 即可将现有 OpenAI 应用切换到 AnuNeko
- 📝 **日志记录**: 支持日志轮转和详细记录
- 🏗️ **模块化架构**: 采用 Flask 蓝图实现模块化设计

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 AnuNeko Token：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 你的 AnuNeko API Token
ANUNEKO_TOKEN=your_token_here

# 你的 AnuNeko Cookie (可选)
ANUNEKO_COOKIE=your_cookie_here

# 服务器配置 (可选)
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
FLASK_DEBUG=False

# 日志配置 (可选)
LOG_PATH=logs
LOG_NAME=anuneko-openai
```

### 启动服务器

```bash
python app.py
```

服务器将在 `http://localhost:8000` 启动。

## 使用方法

### 1. 使用 OpenAI 客户端库

```python
from openai import OpenAI

# 创建客户端
client = OpenAI(
    api_key="dummy-key",  # 不需要真实的 key
    base_url="http://localhost:8000/v1"
)

# 获取可用模型
models = client.models.list()
for model in models.data:
    print(model.id)

# 发送聊天请求
response = client.chat.completions.create(
    model="mihoyo-orange_cat",  # 橘猫模型
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
)

print(response.choices[0].message.content)
```

### 2. 使用标准 HTTP 请求

```python
import requests

# 获取模型列表
response = requests.get("http://localhost:8000/v1/models")
models = response.json()

# 发送聊天请求
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "mihoyo-orange_cat",
        "messages": [
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ]
    }
)

data = response.json()
print(data["choices"][0]["message"]["content"])
```

### 3. 流式响应

```python
from openai import OpenAI

client = OpenAI(
    api_key="dummy-key",
    base_url="http://localhost:8000/v1"
)

stream = client.chat.completions.create(
    model="mihoyo-orange_cat",
    messages=[
        {"role": "user", "content": "请写一首关于猫的诗"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## API 端点

### 聊天完成

`POST /v1/chat/completions`

标准 OpenAI 聊天完成端点，支持以下参数：

- `model`: 模型名称，如 `mihoyo-orange_cat` 或 `mihoyo-exotic_shorthair`
- `messages`: 消息列表
- `stream`: 是否使用流式响应 (默认: false)
- `temperature`: 温度参数 (0.0-2.0)
- `max_tokens`: 最大令牌数
- `session_id`: 指定要使用的会话ID (可选)

### 模型列表

`GET /v1/models`

返回所有可用的模型列表。

`GET /v1/models/<model_name>`

返回指定模型的详细信息。

### 会话管理

`GET /sessions`

列出所有活动会话。

`DELETE /sessions/<session_id>`

删除指定会话。

### 健康检查

`GET /health`

检查服务器状态。

## 模型映射

服务器自动将 AnuNeko 模型映射为 OpenAI 兼容的模型名称：

| AnuNeko 模型 | OpenAI 兼容名称 |
|-------------|----------------|
| Orange Cat | mihoyo-orange_cat |
| Exotic Shorthair | mihoyo-exotic_shorthair |
| 其他模型 | mihoyo-<模型名称小写并替换空格为下划线> |

## 测试

### 运行完整测试套件

```bash
python test_openai_api.py
```

### 使用示例代码

查看项目根目录中的 `test_openai_api.py` 文件，包含各种测试用例：
- 健康检查测试
- 模型列表测试
- 聊天完成测试（多种模型）
- 流式响应测试
- 会话管理测试
- OpenAI 客户端库测试

## 高级配置

### 环境变量

除了 `ANUNEKO_TOKEN` 和 `ANUNEKO_COOKIE`，还可以设置以下变量：

```env
# 服务器配置
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
FLASK_DEBUG=False

# API 配置
API_BASE_URL=http://localhost:8000

# 日志配置
LOG_PATH=logs
LOG_NAME=anuneko-openai
```

### 日志配置

服务器支持自动日志轮转，默认配置：
- 日志文件大小限制：10MB
- 备份文件数量：10个
- 日志格式：`[时间戳] [级别] 消息内容 [在 文件名:行号]`

日志文件保存在 `logs/` 目录下，文件名格式为 `anuneko-openai.log`。

### 自定义模型映射

服务器会自动从 AnuNeko API 获取可用模型列表并生成映射。如果需要自定义映射，可以修改 `app/services/session_service.py` 中的 `update_model_mapping` 方法。

## 故障排除

### 常见问题

1. **"Token 未提供" 错误**
   - 确保 `ANUNEKO_TOKEN` 环境变量已正确设置
   - 检查 `.env` 文件是否存在且格式正确

2. **"无法创建会话" 错误**
   - 检查 Token 是否有效
   - 确认网络连接正常
   - 尝试重新获取 Token

3. **"未找到模型映射" 警告**
   - 服务器将自动使用默认模型 (Orange Cat)
   - 检查 AnuNeko API 是否可访问

4. **日志文件无法创建**
   - 确保 `LOG_PATH` 目录存在且有写入权限
   - 检查磁盘空间是否充足

### 调试模式

启用调试模式以获取更详细的日志：

```bash
FLASK_DEBUG=True python app.py
```

## 开发

### 项目结构

```
anuneko-openai/
├── app.py                        # Flask 服务器主文件
├── requirements.txt              # 项目依赖
├── .env.example                 # 环境变量示例
├── test_openai_api.py           # OpenAI API 兼容性测试
├── app/                         # 应用主目录
│   ├── __init__.py
│   ├── api/                     # API 路由
│   │   └── v1/                  # API v1 版本
│   │       ├── routes.py        # API v1 路由入口
│   │       ├── chat/            # 聊天相关 API
│   │       │   └── routes.py
│   │       └── models/          # 模型相关 API
│   │           ├── routes.py
│   │           └── models.py
│   ├── main/                    # 主要功能路由
│   │   ├── routes.py
│   │   ├── health.py
│   │   └── sessions.py
│   └── services/                # 业务逻辑服务
│       ├── anuneko_service.py   # AnuNeko API 封装
│       ├── chat_service.py      # 聊天服务
│       └── session_service.py   # 会话管理服务
├── docs/                        # 文档目录
│   ├── gitlab-mirror-setup.md
│   └── openai-api-documentation.md
└── scripts/                     # 脚本目录
    └── validate-workflow.sh
```

### 架构设计

项目采用模块化架构，主要组件包括：

1. **Flask 应用主入口** (`app.py`)
   - 应用初始化和配置
   - 蓝图注册
   - 日志配置
   - 错误处理

2. **API 路由层** (`app/api/`)
   - 使用 Flask 蓝图组织路由
   - 按版本和功能模块划分
   - 处理 HTTP 请求和响应

3. **服务层** (`app/services/`)
   - 业务逻辑实现
   - 外部 API 调用封装
   - 会话管理
   - 数据处理和转换

4. **主功能路由** (`app/main/`)
   - 健康检查
   - 会话管理
   - 其他主要功能

### 未来计划
- [x] 重构模块化代码
- [ ] 添加更多模型映射
- [ ] 添加更多 API 端点
- [ ] 添加更多测试用例
- [ ] 打包 Docker 镜像
- [ ] 实现会话持久化
- [ ] 添加性能监控

### 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

- [AnuNeko](https://anuneko.com/) - 提供优秀的 AI 模型服务
- [OpenAI](https://openai.com/) - API 规范设计
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [二叉树树](https://2x.nz/posts/anuneko/) - 逆向工程参考