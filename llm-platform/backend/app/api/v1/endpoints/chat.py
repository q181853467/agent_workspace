import time
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.middleware.auth import get_current_api_key
from app.middleware.rate_limit import check_rate_limit
from app.crud.model import model as model_crud
from app.crud.access_log import access_log
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.mock_service import MockModelService
from app.services.model_service import ModelService
from app.core.config import settings
from app.models.api_key import APIKey
from app.models.user import User

router = APIRouter()

# Initialize model service based on demo mode
if settings.DEMO_MODE:
    model_service = MockModelService()
else:
    model_service = ModelService()

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: Request,
    chat_request: ChatCompletionRequest,
    response: Response,
    db: Session = Depends(get_db),
    auth_data: tuple[APIKey, User] = Depends(get_current_api_key)
):
    """Create a chat completion (OpenAI compatible)"""
    api_key_obj, user_obj = auth_data
    
    # Rate limiting
    await check_rate_limit(request, user_obj.id, api_key_obj.id)
    
    # Add rate limit headers to response
    if hasattr(request.state, 'rate_limit_headers'):
        for key, value in request.state.rate_limit_headers.items():
            response.headers[key] = value
    
    start_time = time.time()
    
    try:
        # Get model
        db_model = model_crud.get_by_name(db, name=chat_request.model)
        if not db_model or not db_model.is_active:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{chat_request.model}' not found or inactive"
            )
        
        # Handle streaming vs non-streaming
        if chat_request.stream:
            return StreamingResponse(
                _stream_chat_completion(chat_request, db_model, api_key_obj, user_obj, db, start_time),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # Disable nginx buffering
                }
            )
        else:
            # Non-streaming response
            completion_response = await model_service.chat_completion(chat_request, db_model)
            
            # Log the request
            latency_ms = int((time.time() - start_time) * 1000)
            access_log.create_log(
                db=db,
                user_id=user_obj.id,
                api_key_id=api_key_obj.id,
                model_id=db_model.id,
                request_type="chat",
                status_code=200,
                latency_ms=latency_ms,
                prompt_tokens=completion_response.usage.prompt_tokens,
                completion_tokens=completion_response.usage.completion_tokens,
                total_tokens=completion_response.usage.total_tokens,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent")
            )
            
            return completion_response
            
    except Exception as e:
        # Log error
        latency_ms = int((time.time() - start_time) * 1000)
        access_log.create_log(
            db=db,
            user_id=user_obj.id,
            api_key_id=api_key_obj.id,
            model_id=db_model.id if 'db_model' in locals() else 0,
            request_type="chat",
            status_code=500,
            latency_ms=latency_ms,
            error_message=str(e),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent")
        )
        raise HTTPException(status_code=500, detail=str(e))

async def _stream_chat_completion(
    chat_request: ChatCompletionRequest,
    db_model,
    api_key_obj: APIKey,
    user_obj: User,
    db: Session,
    start_time: float
) -> AsyncGenerator[str, None]:
    """Stream chat completion chunks"""
    try:
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        
        async for chunk in model_service.chat_completion_stream(chat_request, db_model):
            # Update token counts (simplified)
            if chunk.choices and chunk.choices[0].delta.content:
                completion_tokens += len(chunk.choices[0].delta.content.split())
            
            # Send chunk as SSE
            chunk_json = chunk.json(exclude_unset=True)
            yield f"data: {chunk_json}\n\n"
        
        # Send [DONE] signal
        yield "data: [DONE]\n\n"
        
        # Log the streaming request
        latency_ms = int((time.time() - start_time) * 1000)
        total_tokens = prompt_tokens + completion_tokens
        
        access_log.create_log(
            db=db,
            user_id=user_obj.id,
            api_key_id=api_key_obj.id,
            model_id=db_model.id,
            request_type="chat_stream",
            status_code=200,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )
        
    except Exception as e:
        # Log streaming error
        latency_ms = int((time.time() - start_time) * 1000)
        access_log.create_log(
            db=db,
            user_id=user_obj.id,
            api_key_id=api_key_obj.id,
            model_id=db_model.id,
            request_type="chat_stream",
            status_code=500,
            latency_ms=latency_ms,
            error_message=str(e)
        )
        
        error_chunk = {
            "error": {
                "message": str(e),
                "type": "server_error",
                "code": "internal_error"
            }
        }
        yield f"data: {error_chunk}\n\n"