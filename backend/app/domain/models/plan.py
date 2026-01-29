#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/19 18:50
@Author : caixiaorong01@outlook.com
@File   : plan.py
"""
import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Step(BaseModel):
    """
    步骤/子任务
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""  # 子任务描述
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    success: bool = False  # 是否执行成功
    attachments: List[str] = Field(default_factory=list)  # 附件信息

    @property
    def done(self) -> bool:
        """判断任务是否完成"""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]


class Plan(BaseModel):
    """
    计划模型,拆分出来的子任务/子步骤
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""  # 任务标题
    goal: str = ""  # 任务目标
    language: str = ""  # 工作语言
    steps: List[Step] = Field(default_factory=list)  # 子任务列表
    message: str = ""  # 用户输入消息
    status: ExecutionStatus = ExecutionStatus.PENDING  # 状态
    error: Optional[str] = None

    @property
    def done(self) -> bool:
        """判断任务是否完成"""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]

    def get_next_step(self) -> Optional[Step]:
        """获取下一个未完成的步骤"""
        return next((step for step in self.steps if not step.done), None)
