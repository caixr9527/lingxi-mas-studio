#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/12 16:56
@Author : caixiaorong01@outlook.com
@File   : main.py
"""
from fastapi import FastAPI

from core.config import get_settings

settings = get_settings()
app = FastAPI()