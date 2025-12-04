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

### 模型列表

`GET /v1/models`

返回所有可用的模型列表。

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

### 运行 AnuNeko API 测试

```bash
python test/test_anuneko_api.py
```

### 使用示例代码

查看 `test/` 目录中的示例文件：

- `test/example_usage.py`: AnuNeko API 直接使用示例
- `test/openai_example.py`: OpenAI 兼容 API 使用示例

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
```

### 自定义模型映射

您可以通过修改 `app.py` 中的 `MODEL_MAPPING` 字典来自定义模型映射：

```python
MODEL_MAPPING = {
    "custom-model-name": "AnuNeko 模型名称"
}
```

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

### 调试模式

启用调试模式以获取更详细的日志：

```bash
FLASK_DEBUG=True python app.py
```

## 开发

### 项目结构

```
anuneko-openai/
├── app.py                 # Flask 服务器主文件
├── anuneko_api.py         # AnuNeko API 封装
├── requirements.txt       # 项目依赖
├── .env.example          # 环境变量示例
├── test_openai_api.py    # OpenAI API 兼容性测试
└── test/                 # 测试和示例文件
    ├── example_usage.py
    ├── openai_example.py
    └── test_anuneko_api.py
```

### 未来计划
- 添加更多模型映射
- 添加更多 API 端点
- 添加更多测试用例
- 打包 Docker 镜像

### 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

- [AnuNeko](https://anuneko.com/) - 提供优秀的 AI 模型服务
- [OpenAI](https://openai.com/) - API 规范设计
- [Flask](https://flask.palletsprojects.com/) - Web 框架