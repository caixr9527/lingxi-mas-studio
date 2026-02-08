#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2026/2/8 15:43
@Author : caixiaorong01@outlook.com
@File   : session_service.py
"""
import logging
from typing import List

from app.application.errors import NotFoundError
from app.domain.models import Session
from app.domain.repositories import SessionRepository

logger = logging.getLogger(__name__)


class SessionService:
    """会话服务"""

    def __init__(self, session_repository: SessionRepository) -> None:
        self._session_repository = session_repository

    async def create_session(self) -> Session:
        logger.info("创建任务会话")
        session = Session(title="新会话")
        await self._session_repository.save(session)
        logger.info(f"创建任务会话成功: {session.id}")
        return session

    async def get_all_sessions(self) -> List[Session]:
        return await self._session_repository.get_all()

    async def clear_unread_message_count(self, session_id: str) -> None:
        logger.info(f"清除任务会话未读消息数: {session_id}")
        await self._session_repository.update_unread_message_count(session_id=session_id, count=0)

    async def delete_session(self, session_id: str) -> None:
        logger.info(f"删除任务会话: {session_id}")
        session = await self._session_repository.get_by_id(session_id=session_id)
        if not session:
            logger.error(f"任务会话不存在: {session_id}")
            raise NotFoundError(msg=f"任务会话不存在: {session_id}")
        await self._session_repository.delete_by_id(session_id=session_id)
        logger.info(f"删除任务会话成功: {session_id}")
