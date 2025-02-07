#作者：凌封 (微信fengin)
#GITHUB: https://github.com/fengin/image-gen-server.git
#相关知识可以看AI全书：https://aibook.ren 


"""使用示例"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # 添加proxy目录到模块搜索路径

from jimeng import generate_images, create_completion, create_completion_stream

async def main():
    # 替换为你的sessionid
    token = "57f7addf85602***af9d29**5386f**"
    
    # 1. 基础图像生成
    print("1. 生成图像:")
    try:
        urls = generate_images(
            model="jimeng-2.1",
            prompt="可爱的熊猫漫画",
            width=1024,
            height=1024,
            sample_strength=0.5,
            negative_prompt="",
            refresh_token=token
        )
        print("生成的图片URLs:", urls)
    except Exception as e:
        print("生成失败:", e)
    
    print("\n" + "="*50 + "\n")
    
    # 2. 同步对话补全
    print("2. 同步对话补全:")
    try:
        result = await create_completion(
            messages=[{
                "role": "user",
                "content": "可爱的熊猫漫画"
            }],
            refresh_token=token,
            model="jimeng-2.1"
        )
        print("补全结果:", result)
    except Exception as e:
        print("补全失败:", e)
    
    print("\n" + "="*50 + "\n")
    
    # 3. 流式对话补全
    print("3. 流式对话补全:")
    try:
        async for chunk in create_completion_stream(
            messages=[{
                "role": "user",
                "content": "可爱的熊猫漫画"
            }],
            refresh_token=token,
            model="jimeng-2.1"
        ):
            print("收到chunk:", chunk)
    except Exception as e:
        print("流式补全失败:", e)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序出错: {e}")
    finally:
        # 确保所有异步任务都被清理
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 