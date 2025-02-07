#作者：凌封 (微信fengin)
#GITHUB: https://github.com/fengin/image-gen-server.git
#相关知识可以看AI全书：https://aibook.ren 


"""图像生成相关功能"""

import time
from typing import Dict, List, Optional, Union
import random

from . import utils
from .core import request, DEFAULT_ASSISTANT_ID
from .exceptions import API_IMAGE_GENERATION_FAILED, API_CONTENT_FILTERED

# 默认模型
DEFAULT_MODEL = "jimeng-2.1"

# 草稿版本
DRAFT_VERSION = "3.0.2"

# 模型映射
MODEL_MAP = {
    "jimeng-2.1": "high_aes_general_v21_L:general_v2.1_L",
    "jimeng-2.0-pro": "high_aes_general_v20_L:general_v2.0_L",
    "jimeng-2.0": "high_aes_general_v20:general_v2.0",
    "jimeng-1.4": "high_aes_general_v14:general_v1.4",
    "jimeng-xl-pro": "text2img_xl_sft",
}

def get_model(model: str) -> str:
    """获取模型映射
    
    Args:
        model: 模型名称
        
    Returns:
        str: 映射后的模型名称
    """
    return MODEL_MAP.get(model, MODEL_MAP[DEFAULT_MODEL])

def get_credit(refresh_token: str) -> Dict[str, int]:
    """获取积分信息
    
    Args:
        refresh_token: 刷新token
        
    Returns:
        Dict: 积分信息
    """
    result = request(
        "POST",
        "/commerce/v1/benefits/user_credit",
        refresh_token,
        data={},
        headers={
            "Referer": "https://jimeng.jianying.com/ai-tool/image/generate"
        }
    )
    credit = result.get('credit', {})
    gift_credit = credit.get('gift_credit', 0)
    purchase_credit = credit.get('purchase_credit', 0)
    vip_credit = credit.get('vip_credit', 0)
    return {
        'giftCredit': gift_credit,
        'purchaseCredit': purchase_credit,
        'vipCredit': vip_credit,
        'totalCredit': gift_credit + purchase_credit + vip_credit
    }

def receive_credit(refresh_token: str) -> None:
    """领取积分
    
    Args:
        refresh_token: 刷新token
    """
    request(
        "POST",
        "/commerce/v1/benefits/credit_receive",
        refresh_token,
        data={
            "time_zone": "Asia/Shanghai"
        },
        headers={
            "Referer": "https://jimeng.jianying.com/ai-tool/image/generate"
        }
    )

def generate_images(
    model: str,
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    sample_strength: float = 0.5,
    negative_prompt: str = "",
    refresh_token: str = None
) -> List[str]:
    """生成图像
    
    Args:
        model: 模型名称
        prompt: 提示词
        width: 图像宽度
        height: 图像高度
        sample_strength: 精细度
        negative_prompt: 反向提示词
        refresh_token: 刷新token
        
    Returns:
        List[str]: 图像URL列表
        
    Raises:
        API_IMAGE_GENERATION_FAILED: 图像生成失败
        API_CONTENT_FILTERED: 内容被过滤
    """
    # 参数验证
    if not prompt or not isinstance(prompt, str):
        raise ValueError("prompt must be a non-empty string")
    if not refresh_token:
        raise ValueError("refresh_token is required")
        
    # 获取实际模型
    _model = get_model(model)
    
    # 检查积分
    credit_info = get_credit(refresh_token)
    if credit_info.get('totalCredit', 0) <= 0:
        receive_credit(refresh_token)
        
    # 生成组件ID
    component_id = utils.generate_uuid()
    
    # 发送生成请求
    result = request(
        "post",
        "/mweb/v1/aigc_draft/generate",
        refresh_token,
        params={
            "babi_param": utils.url_encode(utils.json_encode({
                "scenario": "image_video_generation",
                "feature_key": "aigc_to_image",
                "feature_entrance": "to_image",
                "feature_entrance_detail": f"to_image-{_model}",
            }))
        },
        data={
            "extend": {
                "root_model": _model,
                "template_id": "",
            },
            "submit_id": utils.generate_uuid(),
            "metrics_extra": utils.json_encode({
                "templateId": "",
                "generateCount": 1,
                "promptSource": "custom",
                "templateSource": "",
                "lastRequestId": "",
                "originRequestId": "",
            }),
            "draft_content": utils.json_encode({
                "type": "draft",
                "id": utils.generate_uuid(),
                "min_version": DRAFT_VERSION,
                "is_from_tsn": True,
                "version": DRAFT_VERSION,
                "main_component_id": component_id,
                "component_list": [{
                    "type": "image_base_component",
                    "id": component_id,
                    "min_version": DRAFT_VERSION,
                    "generate_type": "generate",
                    "aigc_mode": "workbench",
                    "abilities": {
                        "type": "",
                        "id": utils.generate_uuid(),
                        "generate": {
                            "type": "",
                            "id": utils.generate_uuid(),
                            "core_param": {
                                "type": "",
                                "id": utils.generate_uuid(),
                                "model": _model,
                                "prompt": prompt,
                                "negative_prompt": negative_prompt,
                                "seed": int(random.random() * 100000000) + 2500000000,
                                "sample_strength": sample_strength,
                                "image_ratio": 1,
                                "large_image_info": {
                                    "type": "",
                                    "id": utils.generate_uuid(),
                                    "height": height,
                                    "width": width,
                                }
                            },
                            "history_option": {
                                "type": "",
                                "id": utils.generate_uuid(),
                            }
                        }
                    }
                }]
            }),
            "http_common_info": {
                "aid": int(DEFAULT_ASSISTANT_ID)
            }
        }
    )
    
    # 获取历史记录ID
    history_id = result.get('aigc_data', {}).get('history_record_id')
    if not history_id:
        raise API_IMAGE_GENERATION_FAILED("记录ID不存在")
        
    # 轮询获取结果
    status = 20
    fail_code = None
    item_list = []
    
    while status == 20:
        time.sleep(1)
        result = request(
            "post",
            "/mweb/v1/get_history_by_ids",
            refresh_token,
            data={
                "history_ids": [history_id],
                "image_info": {
                    "width": 2048,
                    "height": 2048,
                    "format": "webp",
                    "image_scene_list": [
                        {"scene": "smart_crop", "width": 360, "height": 360, "uniq_key": "smart_crop-w:360-h:360", "format": "webp"},
                        {"scene": "smart_crop", "width": 480, "height": 480, "uniq_key": "smart_crop-w:480-h:480", "format": "webp"},
                        {"scene": "smart_crop", "width": 720, "height": 720, "uniq_key": "smart_crop-w:720-h:720", "format": "webp"},
                        {"scene": "smart_crop", "width": 720, "height": 480, "uniq_key": "smart_crop-w:720-h:480", "format": "webp"},
                        {"scene": "smart_crop", "width": 360, "height": 240, "uniq_key": "smart_crop-w:360-h:240", "format": "webp"},
                        {"scene": "smart_crop", "width": 240, "height": 320, "uniq_key": "smart_crop-w:240-h:320", "format": "webp"},
                        {"scene": "smart_crop", "width": 480, "height": 640, "uniq_key": "smart_crop-w:480-h:640", "format": "webp"},
                        {"scene": "normal", "width": 2400, "height": 2400, "uniq_key": "2400", "format": "webp"},
                        {"scene": "normal", "width": 1080, "height": 1080, "uniq_key": "1080", "format": "webp"},
                        {"scene": "normal", "width": 720, "height": 720, "uniq_key": "720", "format": "webp"},
                        {"scene": "normal", "width": 480, "height": 480, "uniq_key": "480", "format": "webp"},
                        {"scene": "normal", "width": 360, "height": 360, "uniq_key": "360", "format": "webp"}
                    ]
                },
                "http_common_info": {
                    "aid": int(DEFAULT_ASSISTANT_ID)
                }
            }
        )
        
        record = result.get(history_id)
        if not record:
            raise API_IMAGE_GENERATION_FAILED("记录不存在")
            
        status = record.get('status')
        fail_code = record.get('fail_code')
        item_list = record.get('item_list', [])
        
    if status == 30:
        if fail_code == '2038':
            raise API_CONTENT_FILTERED()
        raise API_IMAGE_GENERATION_FAILED()
        
    # 提取图片URL
    return [
        item.get('image', {}).get('large_images', [{}])[0].get('image_url') or 
        item.get('common_attr', {}).get('cover_url')
        for item in item_list
        if item
    ] 