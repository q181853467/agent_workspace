from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, models, api_keys, chat, admin

api_router = APIRouter()

# Public endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# API endpoints (require authentication)
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Admin endpoints
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])