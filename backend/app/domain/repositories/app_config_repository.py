#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 10:24
@Author : caixiaorong01@outlook.com
@File   : app_config_repository.py
"""
from typing import Protocol, Optional

from app.domain.models import AppConfig


class AppConfigRepository(Protocol):
    """应用配置仓库"""

    def load(self) -> Optional[AppConfig]:
        """加载应用配置"""
        ...

    def save(self, app_config: AppConfig) -> None:
        """保存应用配置"""
        ...
