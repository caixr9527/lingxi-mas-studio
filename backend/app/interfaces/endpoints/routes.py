#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/13 15:00
@Author : caixiaorong01@outlook.com
@File   : routes.py
"""
from fastapi import APIRouter
from app.interfaces.endpoints import status_routes


def create_api_route() -> APIRouter:
    """路由管理"""
    router = APIRouter()

    router.include_router(status_routes.router)
    return router


router = create_api_route()
