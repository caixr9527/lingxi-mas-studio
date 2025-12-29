#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/12 12:07
@Author : caixiaorong01@outlook.com
@File   : supervisor.py
"""
from typing import List

from fastapi import APIRouter, Depends

from app.interfaces.schemas import Response
from app.interfaces.service_dependencies import get_supervisor_service
from app.models import ProcessInfo
from app.services import SupervisorService

router = APIRouter(prefix="/supervisor", tags=["supervisor模块"])


@router.get(
    path="/status",
    response_model=Response[List[ProcessInfo]],
    summary="获取Supervisor状态",
    description="获取Supervisor状态",
)
async def get_status(
        supervisor_service: SupervisorService = Depends(get_supervisor_service)
) -> Response[List[ProcessInfo]]:
    processes = await supervisor_service.get_all_process()
    return Response.success(
        msg="获取沙箱服务进程成功",
        data=processes
    )
