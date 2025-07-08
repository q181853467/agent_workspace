from typing import AsyncGenerator, Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
import json
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk
from app.models.model import Model
from app.core.config import settings

class BaseModelService(ABC):
    @abstractmethod
    async def chat_completion(
        self, 
        request: ChatCompletionRequest, 
        model: Model
    ) -> ChatCompletionResponse:
        pass
    
    @abstractmethod
    async def chat_completion_stream(
        self, 
        request: ChatCompletionRequest, 
        model: Model
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        pass

class ModelService(BaseModelService):
    """Real model service for actual API calls"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def chat_completion(
        self, 
        request: ChatCompletionRequest, 
        model: Model
    ) -> ChatCompletionResponse:
        """Call actual model API"""
        if model.provider.lower() == "openai":
            return await self._openai_completion(request, model)
        elif model.provider.lower() == "deepseek":
            return await self._deepseek_completion(request, model)
        else:
            raise ValueError(f"Unsupported model provider: {model.provider}")
    
    async def chat_completion_stream(
        self, 
        request: ChatCompletionRequest, 
        model: Model
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Stream response from actual model API"""
        if model.provider.lower() == "openai":
            async for chunk in self._openai_completion_stream(request, model):
                yield chunk
        elif model.provider.lower() == "deepseek":
            async for chunk in self._deepseek_completion_stream(request, model):
                yield chunk
        else:
            raise ValueError(f"Unsupported model provider: {model.provider}")
    
    async def _openai_completion(self, request: ChatCompletionRequest, model: Model) -> ChatCompletionResponse:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model.name,
            "messages": [msg.dict() for msg in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        return ChatCompletionResponse(**response.json())
    
    async def _openai_completion_stream(
        self, request: ChatCompletionRequest, model: Model
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model.name,
            "messages": [msg.dict() for msg in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True
        }
        
        async with self.client.stream(
            "POST",
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(data)
                        yield ChatCompletionChunk(**chunk_data)
                    except json.JSONDecodeError:
                        continue
    
    async def _deepseek_completion(self, request: ChatCompletionRequest, model: Model) -> ChatCompletionResponse:
        # Similar implementation for Deepseek API
        # This is a placeholder - implement based on Deepseek's actual API
        raise NotImplementedError("Deepseek API integration not implemented")
    
    async def _deepseek_completion_stream(
        self, request: ChatCompletionRequest, model: Model
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        # Similar implementation for Deepseek API streaming
        raise NotImplementedError("Deepseek API streaming not implemented")
        yield  # This is to make it a generator