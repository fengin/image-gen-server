#描述：基于即梦AI的图像生成服务，专门设计用于与Cursor IDE集成。它接收来自Cursor的文本描述，生成相应的图像，并提供图片下载和保存功能。
#作者：凌封 (微信fengin)
#GITHUB: https://github.com/fengin/image-gen-server.git
#相关知识可以看AI全书：https://aibook.ren 

import os
import logging
from sys import stdin, stdout
import requests
import json
from fastmcp import FastMCP
import mcp.types as types
import base64
from proxy.jimeng import generate_images  # 导入proxy.jimeng模块

# API配置
JIMENG_API_TOKEN = "057f7addf85602***af9d29**5386f**" # 你登录即梦获得的session_id   
IMG_SAVA_FOLDER = "D:\code\image-gen-server\images" # 图片默认保存路径


stdin.reconfigure(encoding='utf-8')
stdout.reconfigure(encoding='utf-8')
# 配置日志
logging.basicConfig(
    level=logging.INFO,
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
                        "description": "图片的文本prompt描述,800字符长度限制，一个汉字算一个字符长度",
                        "required": True
                    },
                    "file_name": {
                        "type": "string", 
                        "description": "生成图片的文件名(必选,不含路径，带后缀)",
                        "required": True
                    },
                    "save_folder": {
                        "type": "string",
                        "description": f"图片保存绝对地址目录(必选)",
                        "required": False
                    },
                    "sample_strength": {
                        "type": "number",
                        "description": "生成图片的精细度(可选,范围0-1,默认0.5)",
                        "required": False
                    },
                    "width": {
                        "type": "number",
                        "description": "生成图片的宽度(可选,默认1024，最大1024)",
                        "required": False
                    },
                    "height": {
                        "type": "number",
                        "description": "生成图片的高度(可选,默认1024，最大1024)",
                        "required": False
                    }
                }
            }
        ]
    }

@mcp.tool("generate_image")
async def generate_image(prompt: str, file_name: str, save_folder: str, sample_strength: float = 0.5, width: int = 1024, height: int = 1024) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """根据文本描述生成图片
    
    Args:
        prompt: 图片的文本prompt描述，800字符长度限制，一个汉字算一个字符长度
        file_name: 生成图片的文件名，含后辍名(不含路径，如果没有后缀则默认使用.jpg)
        save_folder: 图片保存绝对地址目录(必选)
        sample_strength: 生成图片的精细度(可选,范围0-1,默认0.5)
        width: 生成图片的宽度(可选,默认1024，最大1024)
        height: 生成图片的高度(可选,默认1024，最大1024)
        
    Returns:
        List: 包含生成结果的JSON字符串
    """
    logger.info(f"收到生成请求: {prompt}")
    
    # 验证prompt参数
    if not prompt or len(prompt) > 800:
        error_msg = "prompt不能为空,且长度不能超过800"
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
    # 验证save_folder参数
    if not save_folder:
        error_msg = "save_folder不能为空"
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
    
    # 验证width和height参数
    if width <= 0 or height <= 0 or width>1024 or height>1024:
        error_msg = f"width和height必须大于0,小于1024，当前值: width={width}, height={height}"
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
    
    # 检查并创建保存目录
    save_folder = save_folder or IMG_SAVA_FOLDER
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        logger.info(f"创建保存目录: {save_folder}")
    
    try:
        # 调用proxy.jimeng模块生成图像
        image_urls = generate_images(
            model="jimeng-2.1",
            prompt=prompt,
            width=width,
            height=height,
            sample_strength=sample_strength,
            negative_prompt="",
            refresh_token=JIMENG_API_TOKEN
        )
        
        # 下载并保存图片
        saved_images = []
        for i, url in enumerate(image_urls):
            # 构造保存路径
            save_path = os.path.join(save_folder, file_name)
            base_name, ext = os.path.splitext(save_path)
            if i > 0:
                save_path = f"{base_name}_{i}{ext}"
            
            # 下载图片
            response = requests.get(url)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                saved_images.append(save_path)
                logger.info(f"图片已保存: {save_path}")
            else:
                logger.error(f"下载图片失败: {url}")
        
        # 返回结果
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "error": None,
                    "images": saved_images
                }, ensure_ascii=False)
            )
        ]
        
    except Exception as e:
        error_msg = f"生成图片失败: {str(e)}"
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


if __name__ == "__main__":
    logger.info("启动图像生成服务...")
    mcp.run() 