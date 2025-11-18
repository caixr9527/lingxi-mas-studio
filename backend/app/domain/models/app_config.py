#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 10:18
@Author : caixiaorong01@outlook.com
@File   : app_config.py
"""
from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class LLMConfig(BaseModel):
    """语言模型配置"""
    base_url: HttpUrl = "https://api.deepseek.com"
    api_key: str = ""
    model_name: str = "deepseek-reasoner"
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=8192,ge=0)


class AppConfig(BaseModel):
    """应用配置信息,包含Agent配置,LLM提供商,A2A网络,MCP服务器配置"""
    llm_config: LLMConfig

    # 允许传递额外的字段初始化
    model_config = ConfigDict(extra="allow")
