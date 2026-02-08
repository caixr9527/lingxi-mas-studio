#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2026/2/8 16:16
@Author : caixiaorong01@outlook.com
@File   : agent_service.py
"""
import logging
from typing import AsyncGenerator, Optional, List, Type

from app.domain.external import Task, Sandbox, LLM, JSONParser, SearchEngine, FileStorage
from app.domain.models import BaseEvent, ErrorEvent, SessionStatus, AgentConfig, MCPConfig, A2AConfig, Session
from app.domain.repositories import SessionRepository, FileRepository
from app.domain.services.agent_task_runner import AgentTaskRunner

logger = logging.getLogger(__name__)


class AgentService:

    def __init__(
            self,
            session_repository: SessionRepository,
            llm: LLM,
            agent_config: AgentConfig,
            mcp_config: MCPConfig,
            a2a_config: A2AConfig,
            sandbox_cls: Type[Sandbox],
            task_cls: Type[Task],
            json_parser: JSONParser,
            search_engine: SearchEngine,
            file_storage: FileStorage,
            file_repository: FileRepository,
    ) -> None:
        self._session_repository = session_repository
        self._sandbox_cls = sandbox_cls
        self._task_cls = task_cls
        self._json_parser = json_parser
        self._search_engine = search_engine
        self._file_storage = file_storage
        self._file_repository = file_repository
        self._mcp_config = mcp_config
        self._llm = llm
        self._agent_config = agent_config
        self._a2a_config = a2a_config
        logger.info(f"初始化会话服务: {self.__class__.__name__}")

    async def _get_task(self, session) -> Optional[Task]:
        task_id = session.task_id
        if not task_id:
            return None

        return self._task_cls.get(task_id=task_id)

    async def _create_task(self, session: Session) -> Task:
        # 获取沙箱实例
        sandbox = None
        sandbox_id = session.sandbox_id
        if sandbox_id:
            sandbox = await self._sandbox_cls.get(id=sandbox_id)

        # 如果没有沙箱，则创建新的沙箱并保存到会话中
        if not sandbox:
            sandbox = await self._sandbox_cls.create()
            session.sandbox_id = sandbox.id
            await self._session_repository.save(session=session)

        # 获取沙箱中的浏览器实例
        browser = await sandbox.get_browser()
        if not browser:
            logger.error(f"会话{session.id}的聊天请求失败: 沙箱{sandbox_id},创建浏览器失败")
            raise RuntimeError(f"会话{session.id}的聊天请求失败: 沙箱{sandbox_id},创建浏览器失败")

        # 创建任务运行器
        task_runner = AgentTaskRunner(
            llm=self._llm,
            agent_config=self._agent_config,
            mcp_config=self._mcp_config,
            a2a_config=self._a2a_config,
            session_id=session.id,
            session_repository=self._session_repository,
            file_storage=self._file_storage,
            file_repository=self._file_repository,
            json_parser=self._json_parser,
            browser=browser,
            search_engine=self._search_engine,
            sandbox=sandbox,
        )

        # 创建任务并关联到会话
        task = self._task_cls.create(task_runner=task_runner)

        session.task_id = task.id
        await self._session_repository.save(session=session)
        return task

    async def chat(
            self,
            session_id: str,
            message: Optional[str] = None,
            attachments: Optional[List[str]] = None,
            latest_event_id: Optional[str] = None,
            timestamp: Optional[int] = None,
    ) -> AsyncGenerator[BaseEvent, None]:
        try:
            session = await self._session_repository.get_by_id(session_id=session_id)
            if not session:
                logger.error(f"会话{session_id}不存在")
                raise RuntimeError(f"会话{session_id}不存在")

            task = await self._get_task(session)

            if message:
                if session.status != SessionStatus.RUNNING:
                    task = await self._create_task(session)
                    if not task:
                        logger.error(f"会话{session_id}的聊天请求失败: 创建任务失败")
                        raise RuntimeError(f"会话{session_id}的聊天请求失败: 创建任务失败")

        except Exception as e:
            logger.error(f"会话{session_id}的聊天请求失败: {e}")
            event = ErrorEvent(error=str(e))
            await self._session_repository.add_event(session_id, event)
            yield event
