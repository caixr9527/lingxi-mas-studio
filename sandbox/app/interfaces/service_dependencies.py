#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/12 12:10
@Author : caixiaorong01@outlook.com
@File   : service_dependencies.py
"""
from functools import lru_cache

from app.services import ShellService, FileService


@lru_cache()
def get_shell_service() -> ShellService:
    return ShellService()


@lru_cache()
def get_file_service() -> FileService:
    return FileService()
