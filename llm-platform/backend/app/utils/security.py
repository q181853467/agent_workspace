from passlib.context import CryptContext
from typing import Optional
import secrets
import string

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def generate_api_key(prefix: str = "llm", length: int = 32) -> tuple[str, str]:
    """
    生成API密钥
    返回: (full_key, key_prefix)
    """
    # 生成随机部分
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # 完整密钥
    full_key = f"{prefix}_{random_part}"
    
    # 密钥前缀 (用于显示)
    key_prefix = f"{prefix}_{random_part[:8]}"
    
    return full_key, key_prefix


def hash_api_key(api_key: str) -> str:
    """对API密钥进行哈希"""
    import hashlib
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """生成安全的随机令牌"""
    return secrets.token_urlsafe(length)
