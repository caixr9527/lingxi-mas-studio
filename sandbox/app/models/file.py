#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/14 14:35
@Author : caixiaorong01@outlook.com
@File   : file.py
"""
from pydantic import BaseModel, Field


class FileReadResult(BaseModel):
    filepath: str = Field(..., description="文件路径")
    content: str = Field(..., description="文件内容")
