#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 10:45
@Author : caixiaorong01@outlook.com
@File   : dependencies.py
"""
import logging
from functools import lru_cache

from app.application.service.app_config_service import AppConfigService
from app.infrastructure.repositories import FileAppConfigRepository
from core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


@lru_cache()
def get_app_config_service():
    """获取应用配置服务"""
    logger.info("加载获取AppConfigService")
    return AppConfigService(app_config_repository=FileAppConfigRepository(settings.app_config_filepath))
