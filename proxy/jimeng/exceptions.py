#作者：凌封 (微信fengin)
#GITHUB: https://github.com/fengin/image-gen-server.git
#相关知识可以看AI全书：https://aibook.ren 


"""异常定义"""

class JimengException(Exception):
    """即梦API异常基类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

# 异常定义
EXCEPTIONS = {
    "API_REQUEST_PARAMS_INVALID": [-2000, '请求参数非法'],
    "API_REQUEST_FAILED": [-2001, '请求失败'],
    "API_TOKEN_EXPIRES": [-2002, 'Token已失效'],
    "API_FILE_URL_INVALID": [-2003, '远程文件URL非法'],
    "API_FILE_EXECEEDS_SIZE": [-2004, '远程文件超出大小'],
    "API_CHAT_STREAM_PUSHING": [-2005, '已有对话流正在输出'],
    "API_CONTENT_FILTERED": [-2006, '内容由于合规问题已被阻止生成'],
    "API_IMAGE_GENERATION_FAILED": [-2007, '图像生成失败'],
    "API_VIDEO_GENERATION_FAILED": [-2008, '视频生成失败'],
    "API_IMAGE_GENERATION_INSUFFICIENT_POINTS": [-2009, '即梦积分不足']
}

# 导出异常类
for name, (code, message) in EXCEPTIONS.items():
    globals()[name] = type(name, (JimengException,), {
        '__init__': lambda self, msg=None: JimengException.__init__(
            self, code, msg or message)
    }) 