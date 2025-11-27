#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/27 18:39
@Author : caixiaorong01@outlook.com
@File   : search.py
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class SearchResultItem(BaseModel):
    # 搜索结果项的URL链接
    url: str
    # 搜索结果项的标题
    title: str
    # 搜索结果项的摘要片段，默认为空字符串
    snippet: str = ""


class SearchResults(BaseModel):
    """
    搜索结果
    """
    query: str
    date_range: Optional[str] = None
    total_results: int = 0
    results: List[SearchResultItem] = Field(default_factory=list)
