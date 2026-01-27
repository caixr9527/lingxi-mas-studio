#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2026/1/27 10:04
@Author : caixiaorong01@outlook.com
@File   : base.py
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import AsyncGenerator

from app.domain.models import Message, BaseEvent


class FlowStatus(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    SUMMARIZING = "summarizing"
    UPDATING = "updating"
    COMPLETED = "completed"


class BaseFlow(ABC):

    @abstractmethod
    async def invoke(self, message: Message) -> AsyncGenerator[BaseEvent, None]:
        ...

    @property
    @abstractmethod
    def done(self) -> bool:
        """只读属性，用于返回流是否结束"""
        ...
