"""
即梦AI Python模块

提供即梦AI的图像生成功能，支持多账号token。
"""

from .images import generate_images
from .chat import create_completion, create_completion_stream

__version__ = "0.0.1"

__all__ = [
    "generate_images",
    "create_completion",
    "create_completion_stream"
] 