#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/19 19:28
@Author : caixiaorong01@outlook.com
@File   : json_parser.py
"""
from typing import Protocol, Optional, Any, Union, Dict, List


class JSONParser(Protocol):
    """JSON解析器协议"""

    async def invoke(self, text: str, default_value: Optional[Any] = None) -> Union[Dict, List, Any]:
        """调用解析器"""
        ...
