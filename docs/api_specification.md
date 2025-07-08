# API接口规范：企业级大模型克隆平台

## 1. 设计原则

- **RESTful风格**: 遵循RESTful设计原则，使用标准的HTTP方法 (GET, POST, PUT, DELETE) 和状态码。
- **OpenAPI 3.0**: 规范遵循OpenAPI 3.0标准，便于生成客户端代码和交互式文档。
- **统一数据格式**: 所有请求和响应体均使用JSON格式。
- **安全性**: 所有需要认证的接口都应在HTTP Header中传递`Authorization: Bearer <JWT_or_API_Key>`。
- **版本管理**: API通过URL路径进行版本控制，例如 `/api/v1/...`。

## 2. 统一响应格式

为了便于客户端处理，所有API响应都遵循统一的结构。

**成功响应:**
```json
{
  "code": 0,
  "message": "Success",
  "data": { ... } // 具体业务数据
}
```

**失败响应:**
```json
{
  "code": 40001, // 业务错误码
  "message": "Invalid API Key",
  "data": null
}
```

## 3. 接口规范详情

### 3.1 模型调用接口 (核心)

#### 3.1.1 文本对话 (Chat Completions)

此接口兼容OpenAI的API格式，是平台的核心功能。

- **Endpoint**: `POST /api/v1/chat/completions`
- **描述**: 创建一个模型生成的对话响应。
- **认证**: JWT 或 API Key
- **请求体 (Request Body)**:
  ```json
  {
    "model": "gpt-4o", // 必选，指定要使用的模型ID
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ],
    "stream": false, // 可选，是否使用流式响应，默认为false
    "temperature": 0.7, // 可选
    "max_tokens": 1024 // 可选
  }
  ```
- **响应 (Response)**:
  - **`stream: false` (非流式)**:
    ```json
    {
      "code": 0,
      "message": "Success",
      "data": {
        "id": "chatcmpl-xxxxxxxx",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o",
        "choices": [
          {
            "index": 0,
            "message": {
              "role": "assistant",
              "content": "Hello there! How can I help you today?"
            },
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": 9,
          "completion_tokens": 12,
          "total_tokens": 21
        }
      }
    }
    ```
  - **`stream: true` (流式)**:
    - **协议**: Server-Sent Events (SSE)
    - **Content-Type**: `text/event-stream`
    - **响应流示例**:
      ```
      data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

      data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

      data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}
      
      data: [DONE]
      ```

#### 3.1.2 WebSocket接口

提供一个WebSocket端点以支持更低延迟、更具交互性的双向通信。

- **Endpoint**: `WS /api/v1/chat/stream`
- **描述**: 通过WebSocket进行实时的对话交互。
- **流程**:
  1. 客户端通过`Authorization`头或查询参数建立WebSocket连接。
  2. 连接建立后，客户端发送JSON格式的消息，结构同`POST /chat/completions`的请求体。
  3. 服务器接收到消息后，开始流式返回响应，每个响应是一个JSON对象，结构同SSE的`data`部分。
  4. 对话结束后，服务器发送一个特殊的`finish_reason`消息。

### 3.2 管理接口 (Admin APIs)

#### 3.2.1 用户管理
- `GET /api/v1/admin/users`: 获取用户列表
- `POST /api/v1/admin/users`: 创建新用户
- `GET /api/v1/admin/users/{userId}`: 获取特定用户信息
- `PUT /api/v1/admin/users/{userId}`: 更新用户信息

#### 3.2.2 API密钥管理
- `GET /api/v1/admin/keys`: 获取所有API密钥
- `POST /api/v1/admin/keys`: 为用户创建新的API密钥
- `PUT /api/v1/admin/keys/{keyId}`: 更新密钥状态 (启用/禁用)
- `DELETE /api/v1/admin/keys/{keyId}`: 删除密钥

#### 3.2.3 模型管理
- `GET /api/v1/admin/models`: 获取模型列表
- `POST /api/v1/admin/models`: 添加新模型配置
- `PUT /api/v1/admin/models/{modelId}`: 更新模型配置

### 3.3 认证接口

- `POST /api/v1/auth/login`: 用户名密码登录，成功返回JWT。
- `POST /api/v1/auth/refresh`: 使用Refresh Token刷新JWT。