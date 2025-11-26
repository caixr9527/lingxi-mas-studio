#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/19 19:41
@Author : caixiaorong01@outlook.com
@File   : base.py
"""
import inspect
from typing import Dict, Any, List, Callable

from app.domain.models import ToolResult


def tool(
        name: str,
        description: str,
        parameters: Dict[str, Dict[str, Any]],
        required: List[str] = None
) -> Callable:
    """
    工具装饰器
    :param name: 工具名称
    :param description: 工具描述
    :param parameters: 工具参数
    :param required: 必填参数
    :return:
    """

    def decorator(func):
        """
        工具装饰器
        :param func:
        :return:
        """
        tool_schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required
                }
            }
        }
        func._tool_name = name
        func._tool_description = description
        func._tool_schema = tool_schema
        return func

    return decorator


class BaseTool:
    """
    工具基类
    """
    name: str = ""  # 工具集合名称

    def __init__(self):
        """
        初始化
        """
        self._tools_cache = None

    @classmethod
    def _filter_parameters(cls, method: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据方法签名过滤传入的参数，只保留方法签名中定义的参数
        :param method: 需要检查签名的方法
        :param kwargs: 待过滤的参数字典
        :return: 过滤后的参数字典
        """
        filtered_kwargs = {}
        sign = inspect.signature(method)

        for key, value in kwargs.items():
            # 检查参数是否在方法签名中定义，如果是则保留
            if key in sign.parameters:
                filtered_kwargs[key] = value
        return filtered_kwargs

    def has_tool(self, tool_name: str) -> bool:
        """
        检查当前工具集合中是否存在指定工具
        :param tool_name: 工具名称
        :return:
        """
        return any(hasattr(method, "_tool_name") and getattr(method, "_tool_name") == tool_name
                   for _, method in inspect.getmembers(self, inspect.ismethod))

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        获取当前工具集合中的所有工具
        :return: 工具列表
        """
        if self._tools_cache is not None:
            return self._tools_cache

        # 如果工具缓存为空，则遍历当前对象的所有方法，查找被@tool装饰器标记的方法
        tools = []
        for _, method in inspect.getmembers(self, inspect.ismethod):
            # 检查方法是否具有_tool_name属性，即是否被@tool装饰器标记过
            if hasattr(method, "_tool_name"):
                # 将该方法的工具模式(_tool_schema)添加到工具列表中
                tools.append(getattr(method, "_tool_schema"))

        # 将获取到的工具列表缓存到_tools_cache属性中，避免重复计算
        self._tools_cache = tools
        # 返回工具列表
        return tools

    async def invoke(self, tool_name: str, **kwargs) -> ToolResult:
        """
        调用工具
        :param tool_name: 工具名称
        :param kwargs: 工具参数
        :return:
        """
        # 遍历当前对象的所有方法，查找与请求的工具名称匹配的方法
        for _, method in inspect.getmembers(self, inspect.ismethod):
            # 检查方法是否具有_tool_name属性且与请求的工具名称相匹配
            if hasattr(method, "_tool_name") and getattr(method, "_tool_name") == tool_name:
                # 过滤掉不在方法签名中的参数，防止传递无效参数
                filtered_kwargs = self._filter_parameters(method, kwargs)
                # 异步调用匹配到的工具方法并返回结果
                return await method(**filtered_kwargs)

        raise ValueError(f"无效工具: {tool_name}")
