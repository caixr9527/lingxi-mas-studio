#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/13 14:52
@Author : caixiaorong01@outlook.com
@File   : status_routes.py
"""
import logging
from typing import List

from fastapi import APIRouter, Depends

from app.application.service import StatusService
from app.domain.models import HealthStatus
from app.interfaces.schemas import Response
from app.interfaces.service_dependencies import get_status_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["状态模块"])


@router.get(
    path="",
    response_model=Response[List[HealthStatus]],
    summary="系统健康监测",
    description="系统健康监测",
)
async def get_status(
        status_service: StatusService = Depends(get_status_service)
) -> Response[List[HealthStatus]]:
    """系统健康监测"""
    status = await status_service.check_all()
    if any(item.status == 'ERROR' or item.status == 'error' for item in status):
        return Response.fail(503, "系统服务存在异常", status)
    return Response.success(msg="系统服务正常", data=status)
