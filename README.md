# Image-Gen-Server

基于即梦AI的图像生成服务，专门设计用于与Cursor IDE集成。它接收来自Cursor的文本描述，生成相应的图像，并提供图片下载和保存功能。

## 特性

- 与Cursor IDE完美集成
- 支持文本到图像的生成
- 自动保存生成的图像
- 支持自定义保存路径
- 当前版本依赖jimeng-free-api，需要先部署jimeng-free-api,详见https://github.com/LLM-Red-Team/jimeng-free-api

## 安装

1. 克隆项目
```bash
git clone https://your-repository/image-gen-server.git
cd image-gen-server
```

2. 安装依赖
```bash
pip install -r requirements.txt
pip install uv
```

3. 设置即梦逆向接口和Token以及图片默认保存地址
修改server.py文件下面三个配置
```bash
# API配置
JIMENG_API_URL = "http://192.168.1.20:8000" # jimeng-free-api 部署地址
JIMENG_API_TOKEN = "Bearer 057f7addf85dxxxxxxxxxxxxx" # 你登录即梦获得的session_id，支持多个，在后面用逗号分隔   
IMG_SAVA_FOLDER = "D:\code\image-gen-service\images" # 图片默认保存路径
```


## Cursor集成

1. 打开Cursor设置
   - 点击左下角的设置图标
   - 选择 Features > MCP Servers
   - 点击 "Add new MCP server"

2. 填写服务器配置
   - Name: `image-gen-server`（或其他你喜欢的名称）
   - Type: `command`
   - Command: 
     ```bash
     uv run --with fastmcp fastmcp run D:\code\image-gen-service\server.py
     ```
     注意：将路径替换为你的实际项目路径
     - Windows示例: ` uv run --with fastmcp fastmcp run D:\code\image-gen-service\server.py`
     - macOS/Linux示例: ` uv run --with fastmcp fastmcp run /Users/username/code/image-gen-server/server.py`

    填写完后，会弹出一个黑窗口，然后你就可以在Cursor中使用/generate_image命令生成图片了，目前黑窗口会一直运行，目前还没办法解决弹出这个的问题

## 使用方法

在Cursor中，你要让cursor生成图片，在agent模式下，你提示它了解下图片工具使用方法，然后直接提你要生成的图片要求，保存位置就行了


## 获取即梦Token

1. 访问 [即梦](https://jimeng.jianying.com/)
2. 登录账号
3. 按F12打开开发者工具
4. 在Application > Cookies中找到`sessionid`
5. 将找到的sessionid设置为JIMENG_TOKEN环境变量

## 工具函数说明

### generate_image

```python
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
```

## 许可证

MIT License 

## 故障排除

待补充