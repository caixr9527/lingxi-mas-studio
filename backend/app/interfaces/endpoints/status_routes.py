#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/13 14:52
@Author : caixiaorong01@outlook.com
@File   : status_routes.py
"""
import logging

from fastapi import APIRouter

from app.interfaces.schemas import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["状态模块"])


@router.get(
    path="",
    response_model=Response,
    summary="系统健康监测",
    description="系统健康监测",
)
async def get_status() -> Response:
    """系统健康监测"""
    return Response.success()
