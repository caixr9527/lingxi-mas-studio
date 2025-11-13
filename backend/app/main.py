#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/12 16:56
@Author : caixiaorong01@outlook.com
@File   : main.py
"""
import logging

from fastapi import FastAPI

from app.infrastructure.logging import setup_logging
from core.config import get_settings

settings = get_settings()

setup_logging()
logger = logging.getLogger()

app = FastAPI()

logger.info(f"Starting app in {settings.env} mode")