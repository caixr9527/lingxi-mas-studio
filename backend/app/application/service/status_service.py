#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 15:32
@Author : caixiaorong01@outlook.com
@File   : status_service.py
"""
import asyncio
from typing import List

from app.domain.external import HealthChecker
from app.domain.models import HealthStatus


class StatusService:
    """系统状态服务"""

    def __init__(self, checkers: List[HealthChecker]) -> None:
        self._checkers = checkers

    async def check_all(self) -> List[HealthStatus]:
        """检查所有服务"""
        results = await asyncio.gather(
            *(checker.check() for checker in self._checkers),
            return_exceptions=True
        )
        processed_results = []
        for res in results:
            if isinstance(res, Exception):
                # 服务本身异常
                processed_results.append(HealthStatus(
                    service="未知服务",
                    status="error",
                    details=f"未知检查器发生错误: {str(res)}",
                ))
            else:
                processed_results.append(res)

        return processed_results
