#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/29 15:50
@Author : caixiaorong01@outlook.com
@File   : supervisor.py
"""
from typing import Optional

from pydantic import BaseModel, Field


class TimeoutRequest(BaseModel):
    """激活超时销毁请求"""
    minutes: Optional[int] = Field(default=None, description="分钟数")
