#作者：凌封 (微信fengin)
#GITHUB: https://github.com/fengin/image-gen-server.git
#相关知识可以看AI全书：https://aibook.ren 


"""工具函数"""

import re
import uuid
import time
import hashlib
import random
from typing import Any, List, Union
import json
from urllib.parse import quote

def is_string(value: Any) -> bool:
    """判断是否为字符串"""
    return isinstance(value, str)

def is_array(value: Any) -> bool:
    """判断是否为数组"""
    return isinstance(value, (list, tuple))

def is_finite(value: Any) -> bool:
    """判断是否为有限数字"""
    try:
        float_val = float(value)
        return not (float_val == float('inf') or float_val == float('-inf') or float_val != float_val)
    except (TypeError, ValueError):
        return False

def default_to(value: Any, default_value: Any) -> Any:
    """设置默认值"""
    return default_value if value is None else value

def get_timestamp() -> int:
    """获取当前时间戳
    
    Returns:
        int: 时间戳(秒)
    """
    return int(time.time())

def generate_uuid(with_hyphen: bool = True) -> str:
    """生成UUID
    
    Args:
        with_hyphen: 是否包含连字符
        
    Returns:
        str: UUID字符串
    """
    _uuid = str(uuid.uuid4())
    return _uuid if with_hyphen else _uuid.replace('-', '')

def md5(text: str) -> str:
    """计算MD5
    
    Args:
        text: 文本
        
    Returns:
        str: MD5字符串
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def generate_device_id() -> int:
    """生成设备ID
    
    Returns:
        int: 设备ID
    """
    return int(random.random() * 999999999999999999 + 7000000000000000000)

def generate_web_id() -> int:
    """生成网页ID
    
    Returns:
        int: 网页ID
    """
    return int(random.random() * 999999999999999999 + 7000000000000000000)

def token_split(auth: str) -> List[str]:
    """分割token
    
    Args:
        auth: Authorization头部值
        
    Returns:
        List[str]: token列表
    """
    if not auth:
        return []
    auth = auth.replace('Bearer', '').strip()
    return [t.strip() for t in auth.split(',') if t.strip()]

def json_encode(obj: object) -> str:
    """JSON编码
    
    Args:
        obj: 对象
        
    Returns:
        str: JSON字符串
    """
    return json.dumps(obj, separators=(',', ':'))

def url_encode(text: str) -> str:
    """URL编码
    
    Args:
        text: 文本
        
    Returns:
        str: URL编码字符串
    """
    return quote(text) 