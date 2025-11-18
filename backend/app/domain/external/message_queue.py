#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 16:54
@Author : caixiaorong01@outlook.com
@File   : message_queue.py
"""
from typing import Protocol, Any, Tuple


class MessageQueue(Protocol):
    """消息队列抽象类"""

    async def put(self, message: Any) -> str:
        """
        将消息放入队列
        """
        ...

    async def get(self, start_id: str = None, block_ms: int = None) -> Tuple[str, Any]:
        """
        从队列中取出消息
        """
        ...

    async def pop(self) -> Tuple[str, Any]:
        """
        从队列中取出消息
        """
        ...

    async def clear(self) -> None:
        """
        清空队列
        """
        ...

    async def is_empty(self) -> bool:
        """
        判断队列是否为空
        """
        ...

    async def size(self) -> int:
        """
        获取队列长度
        """
        ...

    async def delete_message(self, message_id: str) -> bool:
        """
        删除消息
        """
        ...
