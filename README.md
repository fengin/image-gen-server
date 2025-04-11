# Image-Gen-Server

<div align="center">
  <img src="images/logo_0.png" alt="Image-Gen-Server Logo" width="100%">
</div>

[![smithery badge](https://smithery.ai/badge/@fengin/image-gen-server)](https://smithery.ai/server/@fengin/image-gen-server)

基于即梦AI的图像生成服务，专门设计用于与Cursor IDE集成。它接收来自Cursor的文本描述，生成相应的图像，并提供图片下载和保存功能。

此插件的开发过程可以看我的网站：[开发一个MCP Server与Cursor集成，给Cursor插上翅膀！](https://aibook.ren/archives/mcp-server-for-cursor)

更多AI知识，见AI全书(https://aibook.ren)

<div align="center">
  <img src="images/example.png" alt="Image-Gen-Server Logo" width="100%">
</div>

## 特性

- 与Cursor IDE完美集成
- 支持文本到图像的生成
- 自动保存生成的图像
- 支持自定义保存路径
- 一次生成四张图，供更多选择

## 安装

### Installing via Smithery

To install Image-Gen-Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@fengin/image-gen-server):

```bash
npx -y @smithery/cli install @fengin/image-gen-server --client claude
```

1. 环境准备，MCP比较新的东西，依赖环境版本都比较新
- python 3.10+

- 安装npm

- 安装nodejs（实测v15 v16都不行，开发环境验证v20可以，其他未验证）

- 安装 pip install uv

- 如果要调试，还需要安装这个：npm install -g @modelcontextprotocol/inspector@0.4.0
2. 克隆项目
   
   ```bash
   git clone https://github.com/fengin/image-gen-server.git
   cd image-gen-server
   ```

3. 安装依赖
   
   ```bash
   pip install -r requirements.txt
   pip install uv
   ```

4. 设置即梦Token和图片默认保存地址
   修改server.py文件里面这两个配置
   
   ```bash
   # API配置
   JIMENG_API_TOKEN = "057f7addf85dxxxxxxxxxxxxx" # 你登录即梦获得的session_id，支持多个，在后面用逗号分隔   
   IMG_SAVA_FOLDER = "D:/code/image-gen-server/images" # 图片默认保存路径
   ```

    

## Cursor集成

<div align="center">
  <img src="images/cursor_config.png" alt="Image-Gen-Server Logo" width="100%">
</div>

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
     
     - Windows示例: ` uv run --with fastmcp fastmcp run D:/code/image-gen-service/server.py`
     - macOS/Linux示例: ` uv run --with fastmcp fastmcp run /Users/username/code/image-gen-server/server.py`
     
     windows路径问题比较多，D:/code/image-gen-server/server.py 各种斜杠都试下
     
     填写完后，会弹出一个黑窗口，然后你就可以叫Cursor给你生成需要的图片了，目前黑窗口会一直运行，目前还没办法解决弹出这个的问题

## 使用方法

在Cursor中，你要让cursor生成图片，在agent模式下，你提示它了解下图片工具使用方法，然后直接提你要生成的图片要求，保存位置就行了

## 获取即梦Token

1. 访问 [即梦](https://jimeng.jianying.com/)
2. 登录账号
3. 按F12打开开发者工具
4. 在Application > Cookies中找到`sessionid`
5. 将找到的sessionid设置到server.py的JIMENG_API_TOKEN中

## 工具函数说明

### generate_image

```python
async def generate_image(prompt: str, file_name: str, save_folder: str = None, sample_strength: float = 0.5, width: int = 1024, height: int = 1024) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """根据文本描述生成图片

    Args:
        prompt: 图片的文本prompt描述
        file_name: 生成图片的文件名(不含路径，如果没有后缀则默认使用.jpg)
        save_folder: 图片保存绝对地址目录(可选,默认使用IMG_SAVA_FOLDER)
        sample_strength: 生成图片的精细度(可选,范围0-1,默认0.5)
        width: 生成图片的宽度(可选,默认1024)
        height: 生成图片的高度(可选,默认1024)

    Returns:
        List: 包含生成结果的JSON字符串
    """
```

### 技术实现

1. server.py采用了fastmcp实现了mcp sever的能力，提供给cursor/claude使用

   2.sever.py调用了proxy.jimeng模块逆向与即梦AI进行交互。
proxy.jimeng逆向模块也可以单独install使用，主要提供了以下主要功能：

- 图像生成（generate_images）
- 同步对话补全（create_completion）
- 流式对话补全（create_completion_stream）
- 多账号token支持
- 完整的错误处理

更多详细信息请参考`proxy/jimeng/README.md`。

### 使用示例

```cmd
# cursor agent模式下
#例子一
根据提供过你的项目需求，帮我生成一张产品logo，放在项目目录images下面

#例子二
根据项目需求，帮我制作网站的首页，头部需要有banner图片。
```

## 许可证

MIT License 
作者：凌封

## 故障排除

1.配置完后跳出黑窗口，很快消失，工具状态变成No tools found

  原因：没有正常启动，一般有以下原因

- 配置命令不对，检查命令是否正确，一般是server.py路径不对，或者路径中包含中文，或者正反斜杠不对
- 依赖的环境没准备好
- 依赖运行的终端不对，像我windows的，终端有git bash，cmd，powershell，wsl等，这些终端都试下，cursor配置我这默认终端是cmd，如果你在这对应终端运行报错，一般是环境没装好，安装环境就可以

2.正常运行后，想看调用日志，或者调试怎么弄

  命令改成以下：

```
uv run --with fastmcp fastmcp dev D:/code/image-gen-service/server.py
```


  即把最后一个run 改成 dev。

  或者找个终端运行以下命令进入调试模式：

```
fastmcp dev D:/code/image-gen-service/server.py
```

会有一个调试地址输出：http://localhost:5173/，你可以浏览器打开这地址MCP Inspector进行调试，具体MCP Inspector怎么使用，可以看官方文档
