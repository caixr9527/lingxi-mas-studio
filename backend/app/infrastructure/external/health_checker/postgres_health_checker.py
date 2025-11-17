#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 15:57
@Author : caixiaorong01@outlook.com
@File   : postgres_health_checker.py
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.external import HealthChecker
from app.domain.models import HealthStatus

logger = logging.getLogger(__name__)


class PostgresHealthChecker(HealthChecker):
    """Postgres数据库健康检查"""

    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def check(self) -> HealthStatus:
        """检查Postgres数据库健康状态"""
        try:
            await self._db_session.execute(text("SELECT 1"))
            return HealthStatus(
                service="Postgres",
                status="OK",
            )
        except Exception as e:
            logger.error(f"Postgres数据库检查异常: {e}")
            return HealthStatus(
                service="Postgres",
                status="ERROR",
                details=f"Postgres数据库检查异常: {str(e)}",
            )
