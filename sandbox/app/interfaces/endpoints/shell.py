#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/12 12:06
@Author : caixiaorong01@outlook.com
@File   : shell.py
"""
import os.path

from fastapi import APIRouter, Depends

from app.interfaces.errors import BadRequestException
from app.interfaces.schemas import Response
from app.interfaces.schemas import (
    ShellExecutedRequest,
    ShellReadRequest,
    ShellWaitRequest,
    ShellWriteRequest,
    ShellKillRequest
)
from app.interfaces.service_dependencies import get_shell_service
from app.models import ShellExecuteResult, ShellReadResult, ShellWaitResult, ShellWriteResult, ShellKillResult
from app.services import ShellService

router = APIRouter(prefix="/shell", tags=["shell模块"])


@router.post(
    path="/exec-command",
    response_model=Response[ShellExecuteResult],
    summary="执行命令",
    description="执行命令",
    response_description="返回命令执行结果"
)
async def exec_command(
        request: ShellExecutedRequest,
        shell_service: ShellService = Depends(get_shell_service)
) -> Response[ShellExecuteResult]:
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


@router.post(
    path="/read-shell-output",
    response_model=Response[ShellReadResult],
    description="查看shell",
    summary="查看shell"
)
async def read_shell_output(
        request: ShellReadRequest,
        shell_service: ShellService = Depends(get_shell_service)
) -> Response[ShellReadResult]:
    if not request.session_id or request.session_id == "":
        raise BadRequestException("session_id不能为空")

    result = await shell_service.read_shell_output(session_id=request.session_id, console=request.console)

    return Response.success(data=result)


@router.post(
    path="/wait-process",
    response_model=Response[ShellWaitResult],
    description="等待进程结束",
    summary="等待进程结束"
)
async def wait_process(
        request: ShellWaitRequest,
        shell_service: ShellService = Depends(get_shell_service)
) -> Response[ShellWaitResult]:
    if not request.session_id or request.session_id == "":
        raise BadRequestException("session_id不能为空")

    result = await shell_service.wait_process(session_id=request.session_id, seconds=request.seconds)

    return Response.success(
        msg=f"进程结束，返回状态嘛(returncode): {result.returncode}",
        data=result
    )


@router.post(
    path="/write-shell-input",
    response_model=Response[ShellWriteResult],
    description="向进程写入数据",
    summary="向进程写入数据"
)
async def write_shell_input(
        request: ShellWriteRequest,
        shell_service: ShellService = Depends(get_shell_service)
) -> Response[ShellWriteResult]:
    if not request.session_id or request.session_id == "":
        raise BadRequestException("session_id不能为空")

    result = await shell_service.write_to_process(
        session_id=request.session_id,
        input_text=request.input_text,
        press_enter=request.press_enter
    )

    return Response.success(
        msg=f"写入数据成功",
        data=result
    )


@router.post(
    path="/kill-process",
    response_model=Response[ShellKillResult],
    description="关闭进程",
    summary="关闭进程"
)
async def kill_process(
        request: ShellKillRequest,
        shell_service: ShellService = Depends(get_shell_service)
) -> Response[ShellKillResult]:
    if not request.session_id or request.session_id == "":
        raise BadRequestException("session_id不能为空")

    result = await shell_service.kill_process(session_id=request.session_id)

    return Response.success(
        msg="进程终止" if result.status == "terminated" else "进程已结束",
        data=result
    )
