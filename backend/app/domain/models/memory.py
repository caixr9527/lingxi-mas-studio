#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/19 18:39
@Author : caixiaorong01@outlook.com
@File   : memory.py
"""
import logging
from typing import Any, List, Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Memory(BaseModel):
    """记忆类,定义Agent的记忆基础信息"""

    messages: List[Dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def get_message_role(cls, message: Dict[str, Any]) -> str:
        """获取消息的role"""
        return message.get("role")

    def add_message(self, message: Dict[str, Any]) -> None:
        """添加一条消息"""
        self.messages.append(message)

    def add_messages(self, messages: List[Dict[str, Any]]) -> None:
        """添加多条消息"""
        self.messages.extend(messages)

    def get_messages(self) -> List[Dict[str, Any]]:
        """获取所有消息"""
        return self.messages

    def get_last_message(self) -> Optional[Dict[str, Any]]:
        """获取最后一条消息"""
        return self.messages[-1] if len(self.messages) > 0 else None

    def roll_back(self) -> None:
        """回滚最后一条消息"""
        self.messages = self.messages[:-1]

    def compact(self) -> None:
        """压缩记忆"""
        # 遍历所有消息，进行记忆压缩处理
        for message in self.messages:
            # 如果消息角色为"tool"，并且是浏览器相关工具调用，则清空其内容
            if self.get_message_role(message) == "tool":
                if message.get("function_name") in ["browser_view", "browser_navigate"]:
                    message["content"] = "(removed)"  # 将内容标记为已移除
                    logger.debug(f"从记忆中删除了工具调用结果: {message['function_name']}")

            # 如果消息中包含推理内容，则将其移除以节省存储空间
            if "reasoning_content" in message:
                logger.debug(f"从记忆中移除工具思考结果: {message['reasoning_content'][:50]}...")  # 记录日志，仅显示前50个字符
                del message["reasoning_content"]  # 删除推理内容字段

    @property
    def empty(self) -> bool:
        """判断记忆是否为空"""
        return len(self.messages) == 0
