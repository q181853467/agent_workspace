from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.crud.user import user
from app.crud.model import model
from app.schemas.user import UserCreate
from app.schemas.model import ModelCreate
import logging

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize database with default data"""
    db = SessionLocal()
    
    try:
        # Create default admin user
        admin_user = user.get_by_username(db, username="admin")
        if not admin_user:
            admin_user_in = UserCreate(
                username="admin",
                email="admin@llm-platform.com",
                password="admin123",
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            admin_user = user.create(db, obj_in=admin_user_in)
            logger.info("Created default admin user")
        
        # Create default demo user
        demo_user = user.get_by_username(db, username="demo")
        if not demo_user:
            demo_user_in = UserCreate(
                username="demo",
                email="demo@llm-platform.com",
                password="demo123",
                full_name="Demo User",
                role="user",
                is_active=True
            )
            demo_user = user.create(db, obj_in=demo_user_in)
            logger.info("Created default demo user")
        
        # Create default models
        default_models = [
            {
                "name": "gpt-4",
                "display_name": "GPT-4",
                "provider": "OpenAI",
                "endpoint_url": "https://api.openai.com/v1/chat/completions",
                "description": "最先进的GPT-4模型，具备强大的推理和创作能力",
                "max_tokens": 8192,
                "priority": 100,
                "metadata": {
                    "context_length": 8192,
                    "training_data_cutoff": "2024-04",
                    "capabilities": ["chat", "reasoning", "coding", "analysis"]
                }
            },
            {
                "name": "gpt-3.5-turbo",
                "display_name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "endpoint_url": "https://api.openai.com/v1/chat/completions",
                "description": "快速高效的GPT-3.5模型，适合大部分对话任务",
                "max_tokens": 4096,
                "priority": 80,
                "metadata": {
                    "context_length": 4096,
                    "training_data_cutoff": "2024-01",
                    "capabilities": ["chat", "coding", "writing"]
                }
            },
            {
                "name": "deepseek-coder",
                "display_name": "DeepSeek Coder",
                "provider": "DeepSeek",
                "endpoint_url": "https://api.deepseek.com/v1/chat/completions",
                "description": "专门优化的编程AI模型，擅长代码生成和调试",
                "max_tokens": 4096,
                "priority": 90,
                "metadata": {
                    "context_length": 16384,
                    "specialization": "coding",
                    "capabilities": ["coding", "debugging", "code_review"]
                }
            },
            {
                "name": "deepseek-chat",
                "display_name": "DeepSeek Chat",
                "provider": "DeepSeek",
                "endpoint_url": "https://api.deepseek.com/v1/chat/completions",
                "description": "通用对话AI模型，支持中英文对话",
                "max_tokens": 4096,
                "priority": 70,
                "metadata": {
                    "context_length": 32768,
                    "languages": ["chinese", "english"],
                    "capabilities": ["chat", "reasoning", "writing"]
                }
            },
            {
                "name": "claude-3",
                "display_name": "Claude 3",
                "provider": "Anthropic",
                "endpoint_url": "https://api.anthropic.com/v1/messages",
                "description": "Anthropic的Claude 3模型，注重安全和有用性",
                "max_tokens": 4096,
                "priority": 85,
                "metadata": {
                    "context_length": 200000,
                    "safety_focus": True,
                    "capabilities": ["chat", "analysis", "writing", "reasoning"]
                }
            }
        ]
        
        for model_data in default_models:
            existing_model = model.get_by_name(db, name=model_data["name"])
            if not existing_model:
                model_in = ModelCreate(**model_data)
                model.create(db, obj_in=model_in)
                logger.info(f"Created default model: {model_data['name']}")
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()