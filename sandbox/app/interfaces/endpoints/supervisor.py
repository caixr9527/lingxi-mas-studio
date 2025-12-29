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
from app.models import ProcessInfo, SupervisorActionResult
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


@router.post(
    path="/stop-all-processes",
    response_model=Response[SupervisorActionResult],
    summary="停止所有进程",
    description="停止所有进程",
)
async def stop_all_processes(
        supervisor_service: SupervisorService = Depends(get_supervisor_service)
) -> Response[SupervisorActionResult]:
    result = await supervisor_service.stop_all_processes()
    return Response.success(
        msg="停止所有进程成功",
        data=result
    )


@router.post(
    path="/shutdown",
    response_model=Response[SupervisorActionResult],
)
async def shutdown(
        supervisor_service: SupervisorService = Depends(get_supervisor_service)
) -> Response[SupervisorActionResult]:
    result = await supervisor_service.shutdown()
    return Response.success(
        msg="关闭Supervisor成功",
        data=result
    )


@router.post(
    path="/restart",
    response_model=Response[SupervisorActionResult],
    summary="重启Supervisor",
    description="重启Supervisor",
)
async def restart(
        supervisor_service: SupervisorService = Depends(get_supervisor_service)
) -> Response[SupervisorActionResult]:
    result = await supervisor_service.restart()
    return Response.success(
        msg="重启Supervisor成功",
        data=result
    )
