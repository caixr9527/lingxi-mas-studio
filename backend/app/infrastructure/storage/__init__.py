#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/12 17:01
@Author : caixiaorong01@outlook.com
@File   : __init__.py.py
"""
from .redis import get_redis_client
from .postgres import get_postgres
from .cos import get_cos

__all__ = [
    "get_redis_client",
    "get_postgres",
    "get_cos",
]