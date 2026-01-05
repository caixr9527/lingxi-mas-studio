#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/19 19:39
@Author : caixiaorong01@outlook.com
@File   : tool_result.py
"""
from typing import Optional, TypeVar, Generic, Self

from pydantic import BaseModel

T = TypeVar("T")


class ToolResult(BaseModel, Generic[T]):
    """工具调用结果模型"""
    success: bool = True
    message: Optional[str] = None  # 信息提示
    data: Optional[T] = None

    @classmethod
    def from_sandbox(cls, code: int, msg: str, data: Optional[T], **kwargs) -> Self:
        return cls(
            success=True if code < 300 else False,
            message=msg,
            data=data,
            **kwargs
        )
