# 即梦AI Python模块

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

这是一个用于调用即梦AI图像生成功能的Python模块。支持多账号token，提供简单易用的API接口。

## 功能特点

- 强大的图像生成能力
- 支持多种模型选择
- 多账号token支持
- 简单易用的API设计
- 完整的错误处理
- 支持同步和流式输出

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 获取Token

从[即梦官网](https://jimeng.jianying.com/)获取sessionid:
1. 登录账号
2. 打开开发者工具(F12)
3. 从Application > Cookies中找到`sessionid`的值

### 2. 基础使用

```python
from jimeng import generate_images

# 生成图像
urls = generate_images(
    model="jimeng-2.1",  # 可选模型
    prompt="可爱的熊猫漫画",  # 图像描述
    width=1024,  # 图像宽度(可选)
    height=1024,  # 图像高度(可选)
    sample_strength=0.5,  # 生成精细度(可选)
    negative_prompt="",  # 反向提示词(可选)
    refresh_token="your_session_id"  # 必填，从即梦网站获取的sessionid
)

print(urls)  # 返回生成的图片URL列表
```

### 3. 对话模式

```python
from jimeng import create_completion, create_completion_stream

# 同步模式
result = create_completion(
    messages=[{
        "role": "user",
        "content": "可爱的熊猫漫画"
    }],
    refresh_token="your_session_id",
    model="jimeng-2.1"  # 可选
)

print(result)

# 流式模式
for chunk in create_completion_stream(
    messages=[{
        "role": "user",
        "content": "可爱的熊猫漫画"
    }],
    refresh_token="your_session_id",
    model="jimeng-2.1"  # 可选
):
    print(chunk)
```

### 4. 多账号支持

```python
# 使用多个账号token
tokens = "token1,token2,token3"  # 使用逗号分隔多个sessionid
result = create_completion(
    messages=[{"role": "user", "content": "prompt"}],
    refresh_token=tokens  # 会随机选择一个token使用
)
```

## API文档

### generate_images

生成图像的主要函数。

参数:
- `model` (str): 使用的模型名称，可选值:
  - jimeng-2.1 (默认)
  - jimeng-2.0-pro
  - jimeng-2.0
  - jimeng-1.4
  - jimeng-xl-pro
- `prompt` (str): 图像描述文本
- `width` (int): 图像宽度，默认1024
- `height` (int): 图像高度，默认1024
- `sample_strength` (float): 生成精细度，范围0-1，默认0.5
- `negative_prompt` (str): 反向提示词，默认空字符串
- `refresh_token` (str): 访问token，必填

返回:
- List[str]: 生成图像的URL列表

### create_completion

同步方式生成图像。

参数:
- `messages` (List[Dict]): 消息列表，每个消息包含role和content
- `refresh_token` (str): 访问token
- `model` (str): 使用的模型，默认jimeng-2.1

返回:
- Dict: 包含生成结果的字典

### create_completion_stream

流式方式生成图像。

参数:
- `messages` (List[Dict]): 消息列表，每个消息包含role和content
- `refresh_token` (str): 访问token
- `model` (str): 使用的模型，默认jimeng-2.1

返回:
- Generator[Dict]: 生成结果的流式输出

## 错误处理

模块定义了以下异常类型:
- API_REQUEST_PARAMS_INVALID: 请求参数非法
- API_REQUEST_FAILED: 请求失败
- API_TOKEN_EXPIRES: Token已失效
- API_CONTENT_FILTERED: 内容被过滤
- API_IMAGE_GENERATION_FAILED: 图像生成失败
- API_IMAGE_GENERATION_INSUFFICIENT_POINTS: 积分不足

建议使用try-except进行错误处理:

```python
try:
    urls = generate_images(...)
except API_IMAGE_GENERATION_INSUFFICIENT_POINTS:
    print("积分不足")
except API_REQUEST_FAILED as e:
    print(f"请求失败: {e}")
```

## 注意事项

1. 请确保有足够的积分用于生成图像
2. 建议在生产环境中做好错误处理
3. 图像生成可能需要一定时间，请耐心等待
4. 建议合理使用多账号功能，避免单个账号请求过于频繁
5. 如遇到网络问题，模块会自动重试，最多重试3次

## 许可证

MIT License 

作者：凌封 (微信fengin)

更多AI知识，见AI全书(https://aibook.ren)