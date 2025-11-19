#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/19 19:08
@Author : caixiaorong01@outlook.com
@File   : event.py
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Literal, List, Any, Union

from pydantic import BaseModel, Field
from .plan import Plan, Step


class PlanEventStatus(str, Enum):
    """规划事件状态"""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"


class StepEventStatus(str, Enum):
    """步骤事件状态"""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseEvent(BaseModel):
    """基础事件模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal[""] = ""  # 事件类型
    created_at: datetime = Field(default_factory=datetime.now)


class PlanEvent(BaseEvent):
    """计划事件模型"""
    type: Literal["plan"] = "plan"
    plan: Plan  # 规划
    status: PlanEventStatus = PlanEventStatus.CREATED


class TitleEvent(BaseEvent):
    """标题事件模型"""
    type: Literal["title"] = "title"
    title: str = ""


class StepEvent(BaseEvent):
    """步骤事件模型"""
    type: Literal["step"] = "step"
    step: Step
    status: StepEventStatus = StepEventStatus.STARTED


class MessageEvent(BaseEvent):
    """消息事件模型"""
    type: Literal["message"] = "message"
    role: Literal["user", "assistant"] = "assistant"
    message: str = ""
    attachments: List[Any] = Field(default_factory=list)  # todo 附件信息


class ToolEvent(BaseEvent):
    """工具事件模型"""
    type: Literal["tool"] = "tool"


class WaiteEvent(BaseEvent):
    """等待事件模型"""
    type: Literal["wait"] = "wait"


class ErrorEvent(BaseEvent):
    """错误事件模型"""
    type: Literal["error"] = "error"
    error: str = ""


class DoneEvent(BaseEvent):
    """完成事件模型"""
    type: Literal["done"] = "done"


Event = Union[
    PlanEvent,
    TitleEvent,
    StepEvent,
    MessageEvent,
    ToolEvent,
    WaiteEvent,
    ErrorEvent,
    DoneEvent
]
