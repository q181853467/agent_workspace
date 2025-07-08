import hashlib
import secrets
import string
from typing import Any, Dict, Optional
from datetime import datetime, timezone


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_string(text: str) -> str:
    """对字符串进行哈希"""
    return hashlib.sha256(text.encode()).hexdigest()


def get_utc_now() -> datetime:
    """获取当前UTC时间"""
    return datetime.now(timezone.utc)


def format_response(data: Any = None, message: str = "Success", code: int = 0) -> Dict[str, Any]:
    """格式化API响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


def format_error_response(message: str = "Error", code: int = 40000, data: Any = None) -> Dict[str, Any]:
    """格式化错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


def truncate_string(text: str, max_length: int = 100) -> str:
    """截断字符串"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_email(email: str) -> bool:
    """简单的邮箱格式验证"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
