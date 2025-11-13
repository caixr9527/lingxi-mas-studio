#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/13 18:50
@Author : caixiaorong01@outlook.com
@File   : base.py
"""
from sqlalchemy.orm import declarative_base

# 定义基础ORM类，让所有模型都继承这个类
Base = declarative_base()
