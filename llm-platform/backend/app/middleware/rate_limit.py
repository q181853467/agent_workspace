from typing import Dict, Optional
from fastapi import HTTPException, Request, status
import time
import asyncio
from collections import defaultdict, deque
from app.core.config import settings

class InMemoryRateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def is_allowed(
        self, 
        key: str, 
        limit: int = None, 
        window: int = 60
    ) -> bool:
        """Check if request is allowed based on rate limit"""
        if limit is None:
            limit = settings.RATE_LIMIT_PER_MINUTE
            
        current_time = time.time()
        window_start = current_time - window
        
        async with self.lock:
            # Clean old requests
            request_times = self.requests[key]
            while request_times and request_times[0] < window_start:
                request_times.popleft()
            
            # Check if limit exceeded
            if len(request_times) >= limit:
                return False
            
            # Add current request
            request_times.append(current_time)
            return True
    
    async def get_remaining(
        self, 
        key: str, 
        limit: int = None, 
        window: int = 60
    ) -> int:
        """Get remaining requests in current window"""
        if limit is None:
            limit = settings.RATE_LIMIT_PER_MINUTE
            
        current_time = time.time()
        window_start = current_time - window
        
        async with self.lock:
            request_times = self.requests[key]
            # Count requests in current window
            current_requests = sum(1 for t in request_times if t >= window_start)
            return max(0, limit - current_requests)

# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()

async def check_rate_limit(
    request: Request,
    user_id: Optional[int] = None,
    api_key_id: Optional[int] = None
):
    """Middleware to check rate limits"""
    # Create a unique key for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    if api_key_id:
        key = f"api_key_{api_key_id}"
    elif user_id:
        key = f"user_{user_id}"
    else:
        key = f"ip_{client_ip}"
    
    if not await rate_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + 60)
            }
        )
    
    # Add rate limit headers
    remaining = await rate_limiter.get_remaining(key)
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(time.time()) + 60)
    }