#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/13 17:21
@Author : caixiaorong01@outlook.com
@File   : shell.py
"""
import asyncio.subprocess
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class ConsoleRecord(BaseModel):
    """控制台记录结构体"""
    ps1: str = Field(..., description="控制台PS1")
    command: str = Field(..., description="执行命令")
    output: str = Field(default="", description="命令执行结果输出")


class Shell(BaseModel):
    process: asyncio.subprocess.Process = Field(..., description="会话子进程")
    exec_dir: str = Field(..., description="会话执行目录")
    output: str = Field(..., description="会话输出")
    console_records: List[ConsoleRecord] = Field(default_factory=list, description="控制台记录列表")

    model_config = ConfigDict(
        arbitrary_types_allowed=True  # 允许任意类型
    )


class ShellWaitResult(BaseModel):
    returncode: int = Field(..., description="命令执行结果状态码")


class ShellViewResult(BaseModel):
    session_id: str = Field(..., description="目标 Shell 会话的唯一标识符")
    output: str = Field(..., description="命令执行结果输出")
    console_records: List[ConsoleRecord] = Field(default_factory=list, description="控制台记录列表")


class ShellExecResult(BaseModel):
    """Shell命令执行结果结构体"""
    session_id: str = Field(..., description="目标 Shell 会话的唯一标识符")
    command: str = Field(..., description="执行的 Shell 命令")
    status: str = Field(..., description="命令执行结果状态")
    returncode: Optional[int] = Field(default=None, description="命令执行结果状态码")
    output: Optional[str] = Field(default=None, description="命令执行结果输出")


class ShellWriteResult(BaseModel):
    status: str = Field(..., description="写入状态")


class ShellKillResult(BaseModel):
    status: str = Field(..., description="关闭状态")
    returncode: int = Field(default=None, description="命令执行结果状态码")
