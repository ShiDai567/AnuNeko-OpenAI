# AnuNeko API Python 封装

这是一个基于 AnuNeko AI 的 Python API 封装，将 curl.txt 和 send.py 中的 API 调用转换为易于使用的异步 Python 函数。此外，还提供了一个 OpenAI API 兼容服务器，可以将 AnuNeko AI 作为 OpenAI API 的替代品使用。

## 功能特性

### AnuNeko API 封装
- 异步发送消息到 AnuNeko AI
- 异步选择回复选项
- 异步切换 AI 模型（橘猫/黑猫）
- 创建新会话
- 流式回复支持（完整回复和生成器模式）
- 支持类实例和便捷函数两种调用方式
- 完整的错误处理
- 交互式使用示例
- 批量处理支持

### OpenAI API 兼容服务器
- 完全兼容 OpenAI API v1 格式
- 支持聊天完成端点 (`/v1/chat/completions`)
- 支持模型列表端点 (`/v1/models`)
- 支持流式和非流式响应
- 支持会话管理
- 可使用 OpenAI 官方客户端库

## 文件说明

### 核心文件
- `anuneko_api.py`: 主要的异步 API 封装类和函数
- `openai_api_server.py`: OpenAI API 兼容服务器
- `example_usage.py`: AnuNeko API 使用示例和交互式界面
- `openai_example.py`: OpenAI API 使用示例
- `test_anuneko_api.py`: AnuNeko API 异步测试脚本
- `test_openai_api.py`: OpenAI API 兼容服务器测试脚本
- `README.md`: 本说明文档
- `requirements.txt`: 项目依赖

## 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install httpx
```

## 快速开始

### 方法一：使用类实例

```python
import asyncio
from anuneko_api import AnuNekoAPI

async def main():
    # 创建 API 实例
    api = AnuNekoAPI(token="你的Token", cookie="你的Cookie")
    
    # 创建会话
    chat_id = await api.create_session("Orange Cat")
    print(f"会话 ID: {chat_id}")
    
    # 发送消息
    response = await api.stream_reply(chat_id, "你好，AnuNeko！")
    print(f"AI 回复: {response}")
    
    # 切换模型
    success = await api.switch_model(chat_id, "Exotic Shorthair")
    print(f"切换成功: {success}")

# 运行异步函数
asyncio.run(main())
```

### 方法二：使用便捷函数

```python
import asyncio
from anuneko_api import create_session, send_message, switch_model, select_choice

async def main():
    # 创建会话
    chat_id = await create_session("你的Token", "你的Cookie", "Orange Cat")
    print(f"会话 ID: {chat_id}")
    
    # 发送消息
    response = await send_message("你的Token", chat_id, ["你好，AnuNeko！"], "你的Cookie")
    print(f"AI 回复: {response}")
    
    # 切换模型
    success = await switch_model("你的Token", chat_id, "Orange Cat", "你的Cookie")
    print(f"切换成功: {success}")

# 运行异步函数
asyncio.run(main())
```

### 方法三：使用生成器模式获取流式回复

```python
import asyncio
from anuneko_api import AnuNekoAPI

async def main():
    api = AnuNekoAPI(token="你的Token", cookie="你的Cookie")
    
    # 创建会话
    chat_id = await api.create_session("Orange Cat")
    
    # 使用生成器模式获取流式回复
    print("AI: ", end="", flush=True)
    async for chunk in api.stream_reply_generator(chat_id, "介绍一下你自己"):
        print(chunk, end="", flush=True)
    print()

# 运行异步函数
asyncio.run(main())
```

## 环境变量配置

你可以通过环境变量设置 Token 和 Cookie：

```bash
export ANUNEKO_TOKEN="你的Token"
export ANUNEKO_COOKIE="你的Cookie"
```

然后可以直接使用：

```python
api = AnuNekoAPI()  # 自动从环境变量读取
```

## API 参考

### AnuNekoAPI 类

#### `__init__(token=None, cookie=None)`

初始化 API 客户端。

**参数:**
- `token` (str, 可选): 账号 Token，如果为 None 则从环境变量 ANUNEKO_TOKEN 获取
- `cookie` (str, 可选): Cookie 值，如果为 None 则从环境变量 ANUNEKO_COOKIE 获取

#### `build_headers(content_type="application/json")`

构建请求头。

**参数:**
- `content_type` (str): 内容类型，默认为 "application/json"

**返回:** 请求头字典

#### `create_session(model="Orange Cat")`

创建新会话。

**参数:**
- `model` (str): 模型名称，默认为 "Orange Cat"

**返回:** 会话 ID (str)，如果创建失败则返回 None

#### `stream_reply(session_uuid, text)`

流式发送消息并获取完整回复。

**参数:**
- `session_uuid` (str): 会话 UUID
- `text` (str): 要发送的文本

**返回:** AI 的完整回复文本 (str)

#### `stream_reply_generator(session_uuid, text)`

流式发送消息并生成器方式获取回复。

**参数:**
- `session_uuid` (str): 会话 UUID
- `text` (str): 要发送的文本

**返回:** 异步生成器，产出 AI 的回复文本片段

#### `switch_model(chat_id, model_name)`

切换模型。

**参数:**
- `chat_id` (str): 会话 ID
- `model_name` (str): 模型名称 ("Orange Cat" 或 "Exotic Shorthair")

**返回:** 是否切换成功 (bool)

#### `send_choice(msg_id, choice_idx=0)`

发送选择回复。

**参数:**
- `msg_id` (str): 消息 ID
- `choice_idx` (int): 选择的回复索引，默认为 0

**返回:** 是否发送成功 (bool)

### 便捷函数

#### `create_session(token=None, cookie=None, model="Orange Cat")`

创建新会话的便捷函数。

#### `send_message(token, session_uuid, contents, cookie=None)`

发送消息到 AnuNeko 的便捷函数。

#### `switch_model(token, chat_id, model, cookie=None)`

切换会话的 AI 模型的便捷函数。

#### `select_choice(token, msg_id, choice_idx=0, cookie=None)`

选择回复选项的便捷函数。

## 运行示例

### 运行示例模式

```bash
python example_usage.py
# 然后选择 1
```

### 运行交互模式

```bash
python example_usage.py
# 然后选择 2
```

### 运行批量处理模式

```bash
python example_usage.py
# 然后选择 3
```

### 运行测试

```bash
python test_anuneko_api.py
```

## 注意事项

1. 需要有效的 AnuNeko 账号 Token
2. Cookie 是可选的，但某些情况下可能需要
3. 选择回复功能需要有效的消息 ID
4. 模型名称必须是 "Exotic Shorthair" 或 "Orange Cat"
5. 所有 API 调用都是异步的，需要使用 asyncio 运行

## 错误处理

所有 API 调用都可能抛出异常，建议使用 try-except 块来捕获：

```python
import asyncio
from anuneko_api import AnuNekoAPI

async def main():
    try:
        api = AnuNekoAPI("你的Token", "你的Cookie")
        chat_id = await api.create_session("Orange Cat")
        response = await api.stream_reply(chat_id, "你好")
        print(response)
    except Exception as e:
        print(f"操作失败: {e}")

asyncio.run(main())
```

## 从 curl 命令转换

这个 Python 封装基于以下 curl 命令和 send.py 中的实现：

### 创建会话

```python
# 对应 send.py 中的 create_new_session 函数
chat_id = await api.create_session("Orange Cat")
```

### 发送消息

```bash
curl --location 'https://anuneko.com/api/v1/msg/会话id/stream' \
--header 'x-token: 账号Token' \
--header 'Content-Type: text/plain' \
--header 'Cookie: 自动拿取' \
--data '{"contents":["test"]}'
```

对应的 Python 代码：

```python
response = await api.stream_reply("会话id", "test")
```

### 选择回复

```bash
curl --location 'https://anuneko.com/api/v1/msg/select-choice' \
--header 'x-token: 你的Token' \
--header 'Content-Type: text/plain' \
--header 'Cookie: 自动拿取' \
--data '{"msg_id":"会话id","choice_idx":0或1}'
```

对应的 Python 代码：

```python
success = await api.send_choice("消息id", 0)  # 或 1
```

### 切换模型

```bash
curl --location 'https://anuneko.com/api/v1/user/select_model' \
--header 'x-token: 你的Token' \
--header 'Content-Type: text/plain' \
--header 'Cookie: 自动拿取' \
--data '{"chat_id":"会话id","model":"Exotic Shorthair或Orange Cat"}'
```

对应的 Python 代码：

```python
success = await api.switch_model("会话id", "Orange Cat")  # 或 "Exotic Shorthair"
```

## OpenAI API 兼容服务器使用

### 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 设置环境变量：
```bash
export ANUNEKO_TOKEN="你的Token"
export ANUNEKO_COOKIE="你的Cookie"  # 可选
```

3. 启动服务器：
```bash
python openai_api_server.py
```

服务器将在 `http://localhost:8080` 启动。

### 使用 OpenAI 客户端库

安装 OpenAI 客户端库：
```bash
pip install openai
```

使用示例：
```python
from openai import OpenAI

# 创建客户端
client = OpenAI(
    api_key="dummy-key",  # 不需要真实的 key
    base_url="http://localhost:8080/v1"
)

# 聊天完成
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # 对应 AnuNeko 的橘猫
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
)

print(response.choices[0].message.content)
```

### 模型映射

| OpenAI 模型名 | AnuNeko 模型 | 描述 |
|---------------|---------------|------|
| gpt-3.5-turbo | Orange Cat | 橘猫模型 |
| gpt-4 | Exotic Shorthair | 黑猫模型 |

### API 端点

- `GET /v1/models` - 列出可用模型
- `POST /v1/chat/completions` - 聊天完成
- `GET /health` - 健康检查
- `GET /sessions` - 列出会话
- `DELETE /sessions/<session_id>` - 删除会话

### 测试服务器

运行测试脚本：
```bash
python test_openai_api.py
```

运行示例：
```bash
python openai_example.py
```

### 环境变量配置

| 变量名 | 描述 | 必需 |
|--------|------|------|
| ANUNEKO_TOKEN | AnuNeko 账号 Token | 是 |
| ANUNEKO_COOKIE | AnuNeko Cookie | 可选 |
| FLASK_HOST | 服务器主机地址 | 否 (默认: 0.0.0.0) |
| FLASK_PORT | 服务器端口 | 否 (默认: 8080) |
| FLASK_DEBUG | 调试模式 | 否 (默认: False) |

## 许可证

本项目仅供学习和研究使用。