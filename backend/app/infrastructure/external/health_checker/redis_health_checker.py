#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 16:02
@Author : caixiaorong01@outlook.com
@File   : redis_health_checker.py
"""
import logging

from app.domain.external import HealthChecker
from app.domain.models import HealthStatus
from app.infrastructure.storage import RedisClient

logger = logging.getLogger(__name__)


class RedisHealthChecker(HealthChecker):
    """Redis健康检查器"""

    def __init__(self, redis_client: RedisClient):
        self._redis_client = redis_client

    async def check(self) -> HealthStatus:
        """检查Redis服务"""
        try:
            if await self._redis_client.client.ping():
                return HealthStatus(
                    service="Redis",
                    status="OK",
                )
            else:
                return HealthStatus(
                    service="Redis",
                    status="ERROR",
                    details="Redis服务异常",
                )
        except Exception as e:
            logger.error(f"Redis检查异常: {e}")
            return HealthStatus(
                service="Redis",
                status="ERROR",
                details=f"Redis检查异常: {str(e)}",
            )
