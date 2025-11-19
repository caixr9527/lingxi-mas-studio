#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/19 20:22
@Author : caixiaorong01@outlook.com
@File   : file.py
"""
import uuid

from pydantic import BaseModel, Field


class File(BaseModel):
    """文件模型,记录上传的文件"""
    # 文件唯一标识符，使用UUID生成默认值
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # 原始文件名
    file_name: str = ""
    # 文件存储路径
    filepath: str = ""
    # 文件在存储系统中的键名
    key: str = ""
    # 文件扩展名
    extension: str = ""
    # 文件MIME类型
    mime_type: str = ""
    # 文件大小(字节)
    size: int = 0
