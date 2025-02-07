#作者：凌封 (微信fengin)
#GITHUB: https://github.com/fengin/image-gen-server.git
#相关知识可以看AI全书：https://aibook.ren 

from setuptools import setup, find_packages

setup(
    name="jimeng",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="即梦AI Python模块",
    long_description=open("jimeng/README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jimeng",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 