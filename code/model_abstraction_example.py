from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
import json

# 配置模型后端的地址
MODEL_BACKENDS = {
    "deepseek": "http://deepseek-adapter-service:8000",
    "gpt": "http://gpt-adapter-service:8000",
}

app = FastAPI()

# 统一模型抽象层的客户端
# 在生产环境中，推荐使用带有连接池的异步HTTP客户端
client = httpx.AsyncClient()

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    这个端点作为统一的入口，接收类似OpenAI的请求，
    然后根据请求中指定的 `model` 字段，将请求路由到相应的后端适配器服务。
    它处理了普通响应和流式响应两种模式。
    """
    try:
        # 1. 解析请求体
        body = await request.json()
        model_name = body.get("model")
        is_stream = body.get("stream", False)

        if not model_name:
            raise HTTPException(status_code=400, detail="'model' field is required")

        # 2. 根据模型名称，动态选择后端服务
        # 在实际应用中，这里会有更复杂的路由和负载均衡逻辑
        backend_service_key = model_name.split('-')[0].lower() # 简单的路由逻辑
        backend_url = MODEL_BACKENDS.get(backend_service_key)

        if not backend_url:
            raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found or supported.")

        # 3. 构建到后端服务的请求
        backend_request_url = f"{backend_url}/invoke"
        headers = {"Content-Type": "application/json"}
        
        # 4. 根据是否流式，决定如何请求和响应
        if is_stream:
            # 对于流式请求，也以流式的方式请求后端
            async def stream_generator():
                async with client.stream("POST", backend_request_url, json=body, headers=headers, timeout=60) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
            
            return StreamingResponse(stream_generator(), media_type="text/event-stream")
        else:
            # 对于非流式请求，直接请求并返回JSON
            response = await client.post(backend_request_url, json=body, headers=headers, timeout=60)
            response.raise_for_status() # 如果后端返回错误，这里会抛出异常
            return JSONResponse(content=response.json())

    except httpx.HTTPStatusError as e:
        # 捕获后端服务返回的HTTP错误
        return JSONResponse(status_code=e.response.status_code, content=e.response.json())
    except Exception as e:
        # 捕获其他所有异常
        return JSONResponse(status_code=500, detail=str(e))

# 这是一个模型适配器的示例，所有模型适配器都实现这个接口
# /invoke
# 这样路由层就不需要关心具体模型的实现细节

# 下面是 gpt-adapter-service:8000 和 deepseek-adapter-service:8000
# 两个服务的伪代码

# gpt-adapter-service.py
# from fastapi import FastAPI
# import openai
# app = FastAPI()
# @app.post("/invoke")
# async def invoke_gpt(request: Request):
#     body = await request.json()
#     # 调用 OpenAI 的 SDK
#     response = openai.ChatCompletion.create(**body)
#     return response
