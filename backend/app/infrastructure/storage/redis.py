#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/12 17:02
@Author : caixiaorong01@outlook.com
@File   : redis.py
"""
import logging
from functools import lru_cache
from redis.asyncio import Redis

from core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis客户端"""

    def __init__(self):
        """初始化Redis客户端"""
        self._client: Redis | None = None
        self._settings: Settings = get_settings()

    async def init(self) -> None:
        """初始化Redis客户端"""
        if self._client:
            logger.warning("Redis客户端已初始化")
            return
        try:
            self._client = Redis(
                host=self._settings.redis_host,
                port=self._settings.redis_port,
                db=self._settings.redis_db,
                password=self._settings.redis_password,
                decode_responses=True
            )

            await self._client.ping()
            logger.info("初始化Redis客户端成功")
        except Exception as e:
            logger.error(f"初始化Redis客户端失败: {e}")
            raise e

    async def close(self) -> None:
        """关闭Redis客户端"""
        if not self._client:
            logger.warning("Redis客户端未初始化")
            return
        try:
            await self._client.aclose()
            self._client = None
            get_redis_client.cache_clear()
            logger.info("关闭Redis客户端成功")
        except Exception as e:
            logger.error(f"关闭Redis客户端失败: {e}")
            raise e

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis客户端未初始化")
        return self._client


@lru_cache
def get_redis_client() -> RedisClient:
    """获取Redis客户端"""
    return RedisClient()
