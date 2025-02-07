#作者：凌封 (微信fengin)
#GITHUB: https://github.com/fengin/image-gen-server.git
#相关知识可以看AI全书：https://aibook.ren 


"""对话补全相关功能"""

import re
import time
from typing import Dict, List, Optional, Union, Generator
import random

from . import utils
from .images import generate_images, DEFAULT_MODEL
from .exceptions import API_REQUEST_PARAMS_INVALID

MAX_RETRY_COUNT = 3
RETRY_DELAY = 5000

def parse_model(model: str) -> Dict[str, Union[str, int]]:
    """解析模型参数
    
    Args:
        model: 模型名称
        
    Returns:
        Dict: 模型信息
    """
    model_name, size = model.split(':') if ':' in model else (model, None)
    if not size:
        return {
            'model': model_name,
            'width': 1024,
            'height': 1024
        }
        
    match = re.search(r'(\d+)[\W\w](\d+)', size)
    if not match:
        return {
            'model': model_name,
            'width': 1024,
            'height': 1024
        }
        
    width, height = match.groups()
    return {
        'model': model_name,
        'width': int((int(width) + 1) // 2 * 2),  # 确保是偶数
        'height': int((int(height) + 1) // 2 * 2)  # 确保是偶数
    }

async def create_completion(
    messages: List[Dict[str, str]],
    refresh_token: str,
    model: str = DEFAULT_MODEL,
    retry_count: int = 0
) -> Dict:
    """同步对话补全
    
    Args:
        messages: 消息列表
        refresh_token: 刷新token
        model: 模型名称
        retry_count: 重试次数
        
    Returns:
        Dict: 补全结果
        
    Raises:
        API_REQUEST_PARAMS_INVALID: 参数无效
    """
    try:
        if not messages:
            raise API_REQUEST_PARAMS_INVALID("消息不能为空")
            
        # 解析模型参数
        model_info = parse_model(model)
        
        # 生成图像
        image_urls = generate_images(
            model=model_info['model'],
            prompt=messages[-1]['content'],
            width=model_info['width'],
            height=model_info['height'],
            refresh_token=refresh_token
        )
        
        # 构造返回结果
        return {
            'id': utils.generate_uuid(),
            'model': model or model_info['model'],
            'object': 'chat.completion',
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': ''.join(f'![image_{i}]({url})\n' for i, url in enumerate(image_urls))
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': 1,
                'completion_tokens': 1,
                'total_tokens': 2
            },
            'created': utils.get_timestamp()
        }
    except Exception as e:
        if retry_count < MAX_RETRY_COUNT:
            print(f"Response error: {str(e)}")
            print(f"Try again after {RETRY_DELAY / 1000}s...")
            time.sleep(RETRY_DELAY / 1000)
            return await create_completion(messages, refresh_token, model, retry_count + 1)
        raise e

async def create_completion_stream(
    messages: List[Dict[str, str]],
    refresh_token: str,
    model: str = DEFAULT_MODEL,
    retry_count: int = 0
) -> Generator[Dict, None, None]:
    """流式对话补全
    
    Args:
        messages: 消息列表
        refresh_token: 刷新token
        model: 模型名称
        retry_count: 重试次数
        
    Yields:
        Dict: 补全结果片段
    """
    try:
        if not messages:
            yield {
                'id': utils.generate_uuid(),
                'model': model,
                'object': 'chat.completion.chunk',
                'choices': [{
                    'index': 0,
                    'delta': {'role': 'assistant', 'content': '消息为空'},
                    'finish_reason': 'stop'
                }]
            }
            return
            
        # 解析模型参数
        model_info = parse_model(model)
        
        # 发送开始生成消息
        yield {
            'id': utils.generate_uuid(),
            'model': model or model_info['model'],
            'object': 'chat.completion.chunk',
            'choices': [{
                'index': 0,
                'delta': {'role': 'assistant', 'content': '🎨 图像生成中，请稍候...'},
                'finish_reason': None
            }]
        }
        
        try:
            # 生成图像
            image_urls = generate_images(
                model=model_info['model'],
                prompt=messages[-1]['content'],
                width=model_info['width'],
                height=model_info['height'],
                refresh_token=refresh_token
            )
            
            # 发送图像URL
            for i, url in enumerate(image_urls):
                yield {
                    'id': utils.generate_uuid(),
                    'model': model or model_info['model'],
                    'object': 'chat.completion.chunk',
                    'choices': [{
                        'index': i + 1,
                        'delta': {
                            'role': 'assistant',
                            'content': f'![image_{i}]({url})\n'
                        },
                        'finish_reason': None if i < len(image_urls) - 1 else 'stop'
                    }]
                }
                
            # 发送完成消息
            yield {
                'id': utils.generate_uuid(),
                'model': model or model_info['model'],
                'object': 'chat.completion.chunk',
                'choices': [{
                    'index': len(image_urls) + 1,
                    'delta': {
                        'role': 'assistant',
                        'content': '图像生成完成！'
                    },
                    'finish_reason': 'stop'
                }]
            }
                
        except Exception as e:
            # 发送错误消息
            yield {
                'id': utils.generate_uuid(),
                'model': model or model_info['model'],
                'object': 'chat.completion.chunk',
                'choices': [{
                    'index': 1,
                    'delta': {
                        'role': 'assistant',
                        'content': f'生成图片失败: {str(e)}'
                    },
                    'finish_reason': 'stop'
                }]
            }
    except Exception as e:
        if retry_count < MAX_RETRY_COUNT:
            print(f"Response error: {str(e)}")
            print(f"Try again after {RETRY_DELAY / 1000}s...")
            time.sleep(RETRY_DELAY / 1000)
            async for chunk in create_completion_stream(messages, refresh_token, model, retry_count + 1):
                yield chunk
            return
        raise e 