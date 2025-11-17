#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 15:33
@Author : caixiaorong01@outlook.com
@File   : health_checker.py
"""
from typing import Protocol

from app.domain.models import HealthStatus


class HealthChecker(Protocol):
    """健康检查接口协议"""

    async def check(self) -> HealthStatus:
        """检查服务"""
        ...
