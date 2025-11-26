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
    max_tokens: int = Field(default=8192, ge=0)


class AgentConfig(BaseModel):
    """Agent配置信息"""
    max_iterations: int = Field(default=100, gt=0, lt=1000)  # Agent执行的最大迭代次数，有效范围(0, 1000)
    max_retries: int = Field(default=3, gt=1, lt=10)  # Agent执行失败后的最大重试次数，有效范围(1, 10)
    max_search_results: int = Field(default=10, gt=1, lt=30)  # Agent搜索结果的最大返回数量，有效范围(1, 30)


class AppConfig(BaseModel):
    """应用配置信息,包含Agent配置,LLM提供商,A2A网络,MCP服务器配置"""
    llm_config: LLMConfig
    agent_config: AgentConfig

    # 允许传递额外的字段初始化
    model_config = ConfigDict(extra="allow")
