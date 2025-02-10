# 作者：凌封 (微信fengin)
# GITHUB: https://github.com/fengin/image-gen-server.git
# 相关知识可以看AI全书：https://aibook.ren


"""核心功能实现"""

import json
from typing import Any, Dict, Optional, Union
import requests
import logging

from . import utils
from .exceptions import API_REQUEST_FAILED, API_IMAGE_GENERATION_INSUFFICIENT_POINTS

import gzip
import brotli
import json
from io import BytesIO

# 常量定义
MODEL_NAME = "jimeng"
DEFAULT_ASSISTANT_ID = "513695"
VERSION_CODE = "5.8.0"
PLATFORM_CODE = "7"
DEVICE_ID = utils.generate_device_id()
WEB_ID = utils.generate_web_id()
USER_ID = utils.generate_uuid(False)
MAX_RETRY_COUNT = 3
RETRY_DELAY = 5000
FILE_MAX_SIZE = 100 * 1024 * 1024

# 请求头
FAKE_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-language": "zh-CN,zh;q=0.9",
    "Cache-control": "no-cache",
    "Last-event-id": "undefined",
    "Appid": DEFAULT_ASSISTANT_ID,
    "Appvr": VERSION_CODE,
    "Origin": "https://jimeng.jianying.com",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
    "Referer": "https://jimeng.jianying.com",
    "Pf": PLATFORM_CODE,
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}


def acquire_token(refresh_token: str) -> str:
    """获取访问token

    目前jimeng的access_token是固定的，暂无刷新功能

    Args:
        refresh_token: 用于刷新access_token的refresh_token

    Returns:
        str: access_token
    """
    return refresh_token


def generate_cookie(token: str) -> str:
    """生成Cookie

    Args:
        token: 访问token

    Returns:
        str: Cookie字符串
    """
    return f"sessionid={token}; sessionid_ss={token}; sid_tt={token}; uid_tt={token}; uid_tt_ss={token}"


def check_result(response: requests.Response) -> Dict[str, Any]:
    """检查请求结果

    Args:
        response: 请求响应

    Returns:
        Dict: 响应数据

    Raises:
        API_IMAGE_GENERATION_INSUFFICIENT_POINTS: 积分不足
        API_REQUEST_FAILED: 请求失败
    """
    result = response.json()
    ret, errmsg, data = result.get('ret'), result.get('errmsg'), result.get('data')

    if not utils.is_finite(ret):
        return result

    if ret == '0':
        return data

    if ret == '5000':
        raise API_IMAGE_GENERATION_INSUFFICIENT_POINTS(f"即梦积分可能不足，{errmsg}")

    raise API_REQUEST_FAILED(f"请求jimeng失败: {errmsg}")


def request(
    method: str,
    uri: str,
    refresh_token: str,
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """请求即梦API

    Args:
        method: 请求方法
        uri: 请求路径
        refresh_token: 刷新token
        params: URL参数
        data: 请求数据
        headers: 请求头
        **kwargs: 其他参数

    Returns:
        Dict: 响应数据
    """
    token = acquire_token(refresh_token)
    device_time = utils.get_timestamp()
    sign = utils.md5(f"9e2c|{uri[-7:]}|{PLATFORM_CODE}|{VERSION_CODE}|{device_time}||11ac")

    _headers = {
        **FAKE_HEADERS,
        "Cookie": generate_cookie(token),
        "Device-Time": str(device_time),
        "Sign": sign,
        "Sign-Ver": "1"
    }
    if headers:
        _headers.update(headers)

    _params = {
        "aid": DEFAULT_ASSISTANT_ID,
        "device_platform": "web",
        "region": "CN",
        "web_id": WEB_ID
    }
    if params:
        _params.update(params)

    response = requests.request(
        method=method.lower(),
        url=f"https://jimeng.jianying.com{uri}",
        params=_params,
        json=data,
        headers=_headers,
        timeout=15,
        verify=True,
        **kwargs
    )

    # 检查响应
    try:
        logging.debug(f'请求uri:{uri},响应状态:{response.status_code}')
        # 检查Content-Encoding
        logging.debug(f'请求uri:{uri},响应状态:{response.status_code}')
        # 检查Content-Encoding并解压
        try:
            content = decompress_response(response)
            logging.debug(f'响应结果:{content}')
        except Exception as e:
            logging.debug(f'解压失败,使用原始响应: {str(e)}')
            content = response.text
            logging.debug(f'响应结果:{content}')
        # result = response.json()
        result = json.loads(content)
    except:
        raise API_REQUEST_FAILED("响应格式错误")

    ret = result.get('ret')
    if ret is None:
        return result

    if str(ret) == '0':
        return result.get('data', {})

    if str(ret) == '5000':
        raise API_IMAGE_GENERATION_INSUFFICIENT_POINTS(f"[无法生成图像]: 即梦积分可能不足，{result.get('errmsg')}")

    raise API_REQUEST_FAILED(f"[请求jimeng失败]: {result.get('errmsg')}")


def decompress_response(response: requests.Response) -> str:
    """解压响应内容

    Args:
        response: 请求响应

    Returns:
        str: 解压后的内容
    """
    content = response.content
    encoding = response.headers.get('Content-Encoding', '').lower()

    if encoding == 'gzip':
        buffer = BytesIO(content)
        with gzip.GzipFile(fileobj=buffer) as f:
            content = f.read()
    elif encoding == 'br':
        content = brotli.decompress(content)
    # 如果之后需要支持其他压缩格式(如zstd),可以在这里添加

    return content.decode('utf-8')