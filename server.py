import os
import logging
from sys import stdin, stdout
import requests
import json
from fastmcp import FastMCP
import mcp.types as types
import base64

# API配置
JIMENG_API_URL = "http://192.168.1.20:8000" # jimeng-free-api 部署地址
JIMENG_API_TOKEN = "Bearer 057f7addf85602af5af9d298d5386fe0" # 你登录即梦获得的session_id   
IMG_SAVA_FOLDER = "D:\code\image-gen-service\images" # 图片默认保存路径


stdin.reconfigure(encoding='utf-8')
stdout.reconfigure(encoding='utf-8')
# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# 创建FastMCP实例
mcp = FastMCP("image-gen-server")

@mcp.tool("use_description")
async def list_tools():
    """列出所有可用的工具及其参数"""
    return {
        "tools": [
            {
                "name": "生成图片",
                "description": "根据文本描述生成图片",
                "parameters": {
                    "prompt": {
                        "type": "string",
                        "description": "图片的文本prompt描述",
                        "required": True
                    },
                    "file_name": {
                        "type": "string", 
                        "description": "生成图片的文件名(必选,不含路径，带后缀)",
                        "required": True
                    },
                    "save_folder": {
                        "type": "string",
                        "description": f"图片保存绝对地址目录(可选,默认:{IMG_SAVA_FOLDER})",
                        "required": False
                    },
                    "sample_strength": {
                        "type": "number",
                        "description": "生成图片的精细度(可选,范围0-1,默认0.5)",
                        "required": False
                    }
                }
            }
        ]
    }

@mcp.tool("generate_image")
async def generate_image(prompt: str, file_name: str, save_folder: str = None, sample_strength: float = 0.5) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """根据文本描述生成图片
    
    Args:
        prompt: 图片的文本prompt描述
        file_name: 生成图片的文件名(不含路径，如果没有后缀则默认使用.jpg)
        save_folder: 图片保存绝对地址目录(可选,默认使用IMG_SAVA_FOLDER)
        sample_strength: 生成图片的精细度(可选,范围0-1,默认0.5)
        
    Returns:
        List: 包含生成结果的JSON字符串
    """
    logger.info(f"收到生成请求: {prompt}")
    
    # 验证sample_strength参数范围
    if not 0 <= sample_strength <= 1:
        error_msg = f"sample_strength参数必须在0-1范围内,当前值: {sample_strength}"
        logger.error(error_msg)
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": error_msg,
                    "images": []
                }, ensure_ascii=False)
            )
        ]
    
    # 检查并处理文件后缀
    if not os.path.splitext(file_name)[1]:
        file_name = f"{file_name}.jpg"
        logger.info(f"文件名没有后缀,使用默认后缀: {file_name}")
    
    # 如果未指定保存目录,使用默认目录
    if not save_folder:
        save_folder = IMG_SAVA_FOLDER
        logger.info(f"使用默认保存目录: {save_folder}")
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": JIMENG_API_TOKEN
        }
        
        payload = {
            "model": "jimeng-2.1",
            "prompt": prompt,
            "negativePrompt": "",
            "width": 1024,
            "height": 1024,
            "sample_strength": sample_strength
        }

        response = requests.post(
            f"{JIMENG_API_URL}/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=300
        )
        
        if response.status_code != 200:
            error_text = response.text
            logger.error(f"API调用失败: {response.status_code} - {error_text}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"生成图片失败: {error_text}",
                        "images": []
                    }, ensure_ascii=False)
                )
            ]
        
        result = response.json()
        image_urls = [img["url"] for img in result["data"]]
        logger.info(f"获取到 {len(image_urls)} 张图片")
        
        save_results = []
        for i, url in enumerate(image_urls):
            result = download_and_save_image(url, save_folder, file_name, i)
            if result:  # 只添加非None的结果
                save_results.append(result)
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": "图片生成完成",
                    "images": save_results
                }, ensure_ascii=False)
            )
        ]
                    
    except requests.Timeout:
        logger.error("请求超时")
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "请求超时,请稍后重试",
                    "images": []
                }, ensure_ascii=False)
            )
        ]
    except Exception as e:
        logger.error(f"生成图片时出错: {str(e)}", exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"生成图片出错: {str(e)}",
                    "images": []
                }, ensure_ascii=False)
            )
        ]


def download_and_save_image(image_url, save_folder, file_name, index):
    """下载并保存单张图片
    
    Args:
        image_url: 图片URL
        save_folder: 保存目录路径
        file_name: 文件名(不含路径，带后辍)
        index: 图片索引
        
    Returns:
        str: 成功时返回图保存地址,失败时返回None
    """
    try:
        file_name_no_ext, ext = os.path.splitext(file_name)
        indexed_file_name = f"{file_name_no_ext}_{index}{ext}"
        save_path = os.path.join(save_folder, indexed_file_name)
        
        response = requests.get(image_url, timeout=60)
        if response.status_code != 200:
            logger.error(f"下载图片失败: {response.status_code} - {image_url}")
            return None
        
        os.makedirs(save_folder, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(response.content)
            
        logger.info(f"图片已保存: {save_path}")
        return save_path
            
    except requests.Timeout:
        logger.error(f"下载图片超时: {image_url}")
        return None
    except Exception as e:
        logger.error(f"保存图片时出错: {str(e)}")
        return None


if __name__ == "__main__":
    logger.info("启动图像生成服务...")
    mcp.run() 