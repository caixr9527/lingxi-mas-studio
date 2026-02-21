#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2026/2/8 16:16
@Author : caixiaorong01@outlook.com
@File   : agent_service.py
"""
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional, List, Type, Callable

from pydantic import TypeAdapter

from app.domain.external import Task, Sandbox, LLM, JSONParser, SearchEngine, FileStorage
from app.domain.models import (
    BaseEvent,
    ErrorEvent,
    SessionStatus,
    AgentConfig,
    MCPConfig,
    A2AConfig,
    Session,
    MessageEvent,
    File,
    Event,
    DoneEvent,
    WaitEvent
)
from app.domain.repositories import IUnitOfWork
from app.domain.services.agent_task_runner import AgentTaskRunner

logger = logging.getLogger(__name__)


class AgentService:

    def __init__(
            self,
            llm: LLM,
            agent_config: AgentConfig,
            mcp_config: MCPConfig,
            a2a_config: A2AConfig,
            sandbox_cls: Type[Sandbox],
            task_cls: Type[Task],
            json_parser: JSONParser,
            search_engine: SearchEngine,
            file_storage: FileStorage,
            uow_factory: Callable[[], IUnitOfWork]
    ) -> None:
        self._sandbox_cls = sandbox_cls
        self._task_cls = task_cls
        self._json_parser = json_parser
        self._search_engine = search_engine
        self._file_storage = file_storage
        self._uow_factory = uow_factory
        self._uow = uow_factory()
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
            await self._uow.session.save(session=session)

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
            uow_factory=self._uow_factory,
            file_storage=self._file_storage,
            json_parser=self._json_parser,
            browser=browser,
            search_engine=self._search_engine,
            sandbox=sandbox,
        )

        # 创建任务并关联到会话
        task = self._task_cls.create(task_runner=task_runner)

        session.task_id = task.id
        await self._uow.session.save(session=session)
        return task

    async def chat(
            self,
            session_id: str,
            message: Optional[str] = None,
            attachments: Optional[List[str]] = None,
            latest_event_id: Optional[str] = None,
            timestamp: Optional[datetime] = None,
    ) -> AsyncGenerator[BaseEvent, None]:
        try:
            # 获取会话信息
            session = await self._uow.session.get_by_id(session_id=session_id)
            if not session:
                logger.error(f"会话{session_id}不存在")
                raise RuntimeError(f"会话{session_id}不存在")

            # 获取当前会话的任务实例
            task = await self._get_task(session)

            # 处理用户发送的消息
            if message:
                # 如果会话未处于运行状态，则创建新任务
                if session.status != SessionStatus.RUNNING:
                    task = await self._create_task(session)
                    if not task:
                        logger.error(f"会话{session_id}的聊天请求失败: 创建任务失败")
                        raise RuntimeError(f"会话{session_id}的聊天请求失败: 创建任务失败")

                # 更新会话的最新消息
                await self._uow.session.update_latest_message(
                    session_id=session_id,
                    message=message,
                    timestamp=timestamp,
                )

                # 创建用户消息事件
                message_event = MessageEvent(
                    role="user",
                    message=message,
                    attachments=[File(id=attachment) for attachment in attachments] if attachments else [],
                )

                # 将消息事件放入任务输入流
                event_id = await task.input_stream.put(message_event.model_dump_json())
                message_event.id = event_id

                # 将消息事件保存到会话历史中
                await self._uow.session.add_event(session_id=session_id, event=message_event)

                # 启动任务执行
                await task.invoke()

                logger.info(f"会话{session_id},输入消息队列写入消息: {message[:50]}...")

            logger.info(f"会话{session_id},已启动,任务实例: {task}")

            # 持续监听任务输出流，直到任务完成
            while task and not task.done:
                # 从输出流获取下一个事件
                event_id, event_str = await task.output_stream.get(start_id=latest_event_id, block_ms=0)
                latest_event_id = event_id
                if event_str is None:
                    logger.debug(f"会话{session_id},输出队列中未发现事件内容")
                    continue

                # 解析事件数据
                event = TypeAdapter(Event).validate_json(event_str)
                event.id = event_id
                logger.debug(f"会话{session_id},输出队列中已发现事件: {type(event).__name__}")

                # 重置未读消息计数
                await self._uow.session.update_unread_message_count(session_id=session_id, count=0)

                # 返回事件给调用方
                yield event

                # 如果遇到终止类型的事件，则退出循环
                if isinstance(event, (DoneEvent, ErrorEvent, WaitEvent)):
                    break

            logger.info(f"会话{session_id},任务本轮运行结束")
        except Exception as e:
            # 处理异常情况，记录错误日志并返回错误事件
            logger.error(f"会话{session_id}的聊天请求失败: {e}")
            event = ErrorEvent(error=str(e))
            await self._uow.session.add_event(session_id, event)
            yield event
        finally:
            # 确保最终重置未读消息计数
            await self._uow.session.update_unread_message_count(session_id=session_id, count=0)
