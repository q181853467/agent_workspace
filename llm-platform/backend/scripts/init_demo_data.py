#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示数据初始化脚本

创建初始用户、API密钥、模型配置和演示数据
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.database import Base
from app.models.user import User
from app.models.api_key import APIKey
from app.models.model import Model
from app.models.access_log import AccessLog
from app.core.security import get_password_hash, generate_api_key
from app.crud import user as user_crud, api_key as api_key_crud, model as model_crud
from app.schemas.user import UserCreate
from app.schemas.api_key import APIKeyCreate
from app.schemas.model import ModelCreate
from app.schemas.access_log import AccessLogCreate


def init_demo_data():
    """
    初始化演示数据
    """
    print("开始初始化演示数据...")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # 1. 创建管理员用户
        print("创建管理员用户...")
        admin_user = user_crud.get_by_username(db, username="admin")
        if not admin_user:
            admin_data = UserCreate(
                username="admin",
                email="admin@example.com",
                password="admin123",
                full_name="系统管理员",
                role="admin"
            )
            admin_user = user_crud.create(db, obj_in=admin_data)
            print(f"管理员用户创建成功: {admin_user.username}")
        else:
            print(f"管理员用户已存在: {admin_user.username}")
        
        # 2. 创建普通用户
        print("创建普通用户...")
        demo_users = [
            {
                "username": "demo_user",
                "email": "demo@example.com",
                "password": "demo123",
                "full_name": "演示用户",
                "role": "user"
            },
            {
                "username": "developer",
                "email": "dev@example.com",
                "password": "dev123",
                "full_name": "开发人员",
                "role": "user"
            }
        ]
        
        for user_data in demo_users:
            existing_user = user_crud.get_by_username(db, username=user_data["username"])
            if not existing_user:
                user_create = UserCreate(**user_data)
                user = user_crud.create(db, obj_in=user_create)
                print(f"用户创建成功: {user.username}")
            else:
                print(f"用户已存在: {user_data['username']}")
        
        # 3. 创建API密钥
        print("创建API密钥...")
        users = user_crud.get_multi(db)
        for user in users:
            existing_keys = api_key_crud.get_by_user(db, user_id=user.id)
            if not existing_keys:
                api_key_data = APIKeyCreate(
                    name=f"{user.username}-Key",
                    user_id=user.id
                )
                api_key, raw_key = api_key_crud.create(db, obj_in=api_key_data, user_id=user.id)
                print(f"API密钥创建成功: {user.username} -> {api_key.key_prefix}***")
        
        # 4. 创建模型配置
        print("创建模型配置...")
        demo_models = [
            {
                "name": "gpt-4o",
                "display_name": "GPT-4o",
                "provider": "openai",
                "endpoint_url": "https://api.openai.com/v1/chat/completions",
                "is_active": True,
                "description": "OpenAI GPT-4o 模型",
                "model_metadata": {
                    "version": "2024-05-13",
                    "default_temperature": 0.7,
                    "supports_streaming": True,
                    "supports_functions": True
                }
            },
            {
                "name": "deepseek-coder-v2",
                "display_name": "DeepSeek Coder V2",
                "provider": "deepseek",
                "endpoint_url": "https://api.deepseek.com/v1/chat/completions",
                "is_active": True,
                "max_tokens": 8192,
                "description": "Deepseek Coder V2 编程模型",
                "model_metadata": {
                    "version": "v2.0",
                    "default_temperature": 0.3,
                    "supports_streaming": True,
                    "supports_functions": False
                }
            },
            {
                "name": "claude-3-sonnet",
                "display_name": "Claude 3 Sonnet",
                "provider": "anthropic",
                "endpoint_url": "https://api.anthropic.com/v1/messages",
                "is_active": True,
                "description": "Claude 3 Sonnet 智能助手",
                "model_metadata": {
                    "version": "3.0",
                    "default_temperature": 0.7,
                    "supports_streaming": True,
                    "supports_functions": False
                }
            },
            {
                "name": "mock-model",
                "display_name": "Mock Model",
                "provider": "local",
                "endpoint_url": "http://localhost:8000/mock/chat/completions",
                "is_active": True,
                "max_tokens": 2048,
                "description": "本地演示模型（用于开发测试）",
                "model_metadata": {
                    "version": "1.0",
                    "default_temperature": 0.8,
                    "supports_streaming": True,
                    "supports_functions": False
                }
            }
        ]
        
        for model_data in demo_models:
            existing_model = model_crud.get_by_name(db, name=model_data["name"])
            if not existing_model:
                model_create = ModelCreate(**model_data)
                model = model_crud.create(db, obj_in=model_create)
                print(f"模型配置创建成功: {model.name}")
            else:
                print(f"模型配置已存在: {model_data['name']}")
        
        # 5. 创建演示访问日志
        print("创建演示访问日志...")
        
        # 获取用户和模型
        users = user_crud.get_multi(db, limit=10)
        models = model_crud.get_multi(db, limit=10)
        
        if users and models:
            # 创建一些历史访问记录
            import random
            from datetime import timedelta
            
            base_time = datetime.utcnow() - timedelta(days=7)
            
            for i in range(50):  # 创建50条演示记录
                user = random.choice(users)
                model = random.choice(models)
                
                # 获取用户的API密钥
                user_keys = api_key_crud.get_by_user(db, user_id=user.id)
                if user_keys:
                    api_key = user_keys[0]
                    
                    # 随机生成访问时间
                    created_at = base_time + timedelta(
                        hours=random.randint(0, 24 * 7),
                        minutes=random.randint(0, 59)
                    )
                    
                    # 随机生成状态码和延迟
                    status_codes = [200] * 8 + [400, 401, 429, 500]  # 大部分成功请求
                    status_code = random.choice(status_codes)
                    latency_ms = random.randint(100, 2000) if status_code == 200 else random.randint(50, 500)
                    
                    # 随机生成token使用情况
                    if status_code == 200:
                        prompt_tokens = random.randint(10, 100)
                        completion_tokens = random.randint(20, 200)
                        total_tokens = prompt_tokens + completion_tokens
                    else:
                        prompt_tokens = completion_tokens = total_tokens = None
                    
                    # 错误信息
                    error_message = None
                    if status_code != 200:
                        error_messages = {
                            400: "Invalid request format",
                            401: "Invalid API key",
                            429: "Rate limit exceeded",
                            500: "Internal server error"
                        }
                        error_message = error_messages.get(status_code)
                    
                    log_entry = AccessLog(
                        user_id=user.id,
                        api_key_id=api_key.id,
                        model_id=model.id,
                        request_type=random.choice(["chat", "chat_stream", "completions"]),
                        status_code=status_code,
                        latency_ms=latency_ms,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        error_message=error_message,
                        created_at=created_at
                    )
                    
                    db.add(log_entry)
            
            db.commit()
            print(f"创建了50条演示访问日志")
        
        db.commit()
        print("演示数据初始化完成！")
        
        # 输出重要信息
        print("\n重要信息:")
        print("   管理员账号: admin / admin123")
        print("   演示用户: demo_user / demo123")
        print("   开发用户: developer / dev123")
        print("\n访问地址:")
        print("   前端界面: http://localhost:3000")
        print("   后端API: http://localhost:8000")
        print("   API文档: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    init_demo_data()
