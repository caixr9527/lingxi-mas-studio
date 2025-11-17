#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 15:28
@Author : caixiaorong01@outlook.com
@File   : health_status.py
"""
from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """
    健康状态
    """

    service: str = Field(default="", description="服务名称")
    status: str = Field(default="", description="服务状态")
    details: str = Field(default="", description="服务详情")