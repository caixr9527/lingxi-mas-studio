#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/12 12:06
@Author : caixiaorong01@outlook.com
@File   : shell.py
"""
import os.path

from fastapi import APIRouter, Depends

from app.interfaces.schemas import ExecCommandRequest
from app.interfaces.schemas import Response
from app.interfaces.service_dependencies import get_shell_service
from app.models import ShellExecResult
from app.services import ShellService

router = APIRouter(prefix="/shell", tags=["shell模块"])


@router.post(
    path="/exec-command",
    response_model=Response[ShellExecResult],
    summary="执行命令",
    description="执行命令",
    response_description="返回命令执行结果"
)
async def exec_command(
        request: ExecCommandRequest,
        shell_service: ShellService = Depends(get_shell_service)
) -> Response[ShellExecResult]:
    if not request.session_id or request.session_id == "":
        request.session_id = shell_service.create_session_id()

    if not request.exec_dir or request.exec_dir == "":
        request.exec_dir = os.path.expanduser("~")

    result = await shell_service.exec_command(
        session_id=request.session_id,
        exec_dir=request.exec_dir,
        command=request.command,
    )

    return Response.success(data=result)
