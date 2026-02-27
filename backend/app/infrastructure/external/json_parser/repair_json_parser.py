#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/19 19:31
@Author : caixiaorong01@outlook.com
@File   : repair_json_parser.py
"""
import logging
from typing import Optional, Any, Union, Dict, List

import json_repair

from app.domain.external import JSONParser

logger = logging.getLogger(__name__)


class RepairJsonParser(JSONParser):
    """修复json解析器"""

    async def invoke(self, text: str, default_value: Optional[Any] = None) -> Union[Dict, List, Any]:
        logger.info(f"开始修复json: {text}")
        if not text or text.strip() == "":
            if default_value is not None:
                return default_value
            raise ValueError("输入文本为空")

        return json_repair.repair_json(text, ensure_ascii=False, return_objects=True)
