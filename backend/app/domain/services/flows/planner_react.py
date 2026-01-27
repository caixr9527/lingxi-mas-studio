#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2026/1/27 10:09
@Author : caixiaorong01@outlook.com
@File   : planner_react.py
"""
import logging
from typing import AsyncGenerator, Optional

from app.domain.external import Sandbox, Browser, SearchEngine, LLM, JSONParser
from app.domain.models import Message, BaseEvent, Plan, AgentConfig
from app.domain.repositories import SessionRepository
from app.domain.services.agents import PlannerAgent, ReActAgent
from app.domain.services.tools import (
    BrowserTool,
    FileTool,
    ShellTool,
    SearchTool,
    MCPTool,
    A2ATool,
    MessageTool,
)
from .base import BaseFlow, FlowStatus

logger = logging.getLogger(__name__)


class PlannerReActFlow(BaseFlow):

    def __init__(
            self,
            llm: LLM,
            agent_config: AgentConfig,
            session_id: str,
            session_repository: SessionRepository,
            json_parser: JSONParser,
            browser: Browser,
            sandbox: Sandbox,
            search_engine: SearchEngine,
            mcp_tool: MCPTool,
            a2a_tool: A2ATool,
    ):
        # 初始化会话ID和会话仓库，用于后续的交互和状态管理
        self._session_id = session_id
        self._session_repository = session_repository

        # 设置流程初始状态为待机状态，并初始化计划为空
        self.status = FlowStatus.IDLE
        self.plan: Optional[Plan] = None

        # 构建工具列表，包括文件操作、shell命令执行、浏览器控制、搜索功能、消息处理、MCP和A2A工具
        tools = [
            FileTool(sandbox=sandbox),  # 文件操作工具
            ShellTool(sandbox=sandbox),  # Shell命令执行工具
            BrowserTool(browser=browser),  # 浏览器控制工具
            SearchTool(search_engine=search_engine),  # 搜索引擎工具
            MessageTool(),  # 消息处理工具
            mcp_tool,  # MCP工具
            a2a_tool,  # A2A工具
        ]

        # 创建规划代理实例，负责制定任务计划
        self.planner = PlannerAgent(
            session_id=self._session_id,
            session_repository=self._session_repository,
            agent_config=agent_config,
            llm=llm,
            tools=tools,
            json_parser=json_parser,
        )
        logger.debug(f"创建PlannerAgent成功, 会话id: {self._session_id}")

        # 创建ReAct代理实例，负责执行计划并进行推理和行动
        self.react = ReActAgent(
            session_id=self._session_id,
            session_repository=self._session_repository,
            agent_config=agent_config,
            llm=llm,
            tools=tools,
            json_parser=json_parser,
        )

        logger.debug(f"创建ReActAgent成功, 会话id: {self._session_id}")

    async def invoke(self, message: Message) -> AsyncGenerator[BaseEvent, None]:
        pass

    @property
    def done(self) -> bool:
        return self.status == FlowStatus.IDLE
