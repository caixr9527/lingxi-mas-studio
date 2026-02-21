#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2026/2/8 15:43
@Author : caixiaorong01@outlook.com
@File   : session_service.py
"""
import logging
from typing import List, Callable

from app.application.errors import NotFoundError
from app.domain.models import Session
from app.domain.repositories import IUnitOfWork

logger = logging.getLogger(__name__)


class SessionService:
    """会话服务"""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self._uow_factory = uow_factory
        self._uow = uow_factory()

    async def create_session(self) -> Session:
        logger.info("创建任务会话")
        session = Session(title="新会话")
        async with self._uow:
            await self._uow.session.save(session)
        logger.info(f"创建任务会话成功: {session.id}")
        return session

    async def get_all_sessions(self) -> List[Session]:
        async with self._uow:
            return await self._uow.session.get_all()

    async def clear_unread_message_count(self, session_id: str) -> None:
        logger.info(f"清除任务会话未读消息数: {session_id}")
        async with self._uow:
            await self._uow.session.update_unread_message_count(session_id=session_id, count=0)

    async def delete_session(self, session_id: str) -> None:
        logger.info(f"删除任务会话: {session_id}")
        async with self._uow:
            session = await self._uow.session.get_by_id(session_id=session_id)
        if not session:
            logger.error(f"任务会话不存在: {session_id}")
            raise NotFoundError(msg=f"任务会话不存在: {session_id}")
        async with self._uow:
            await self._uow.session.delete_by_id(session_id=session_id)
        logger.info(f"删除任务会话成功: {session_id}")
