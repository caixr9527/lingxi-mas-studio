#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/14 14:37
@Author : caixiaorong01@outlook.com
@File   : file.py
"""
from typing import Optional

from pydantic import BaseModel, Field


class ReadFileRequest(BaseModel):
    filepath: str = Field(..., description="文件路径")
    start_line: Optional[int] = Field(None, description="(可选)开始行数，索引从0开始")
    end_line: Optional[int] = Field(None, description="(可选)结束行数，不包括该行")
    sudo: Optional[bool] = Field(default=False, description="(可选)是否使用sudo权限")
    max_length: Optional[int] = Field(default=10000, description="(可选)最大读取行数")
