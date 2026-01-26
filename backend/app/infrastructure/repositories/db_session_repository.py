#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2026/1/26 14:24
@Author : caixiaorong01@outlook.com
@File   : db_session_repository.py
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Session, SessionStatus
from app.domain.repositories import SessionRepository
from app.infrastructure.models import SessionModel


class DBSessionRepository(SessionRepository):

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def save(self, session: Session) -> None:
        # 查询数据库中是否存在具有相同ID的会话记录
        stmt = select(SessionModel).where(SessionModel.id == session.id)
        result = await self.db_session.execute(stmt)
        record = result.scalar_one_or_none()

        # 如果记录不存在，则创建新的会话模型并添加到数据库会话中
        if not record:
            record = SessionModel.from_domain(session)
            self.db_session.add(record)
            return

        # 如果记录已存在，则用新的域对象更新现有的数据库记录
        record.update_from_domain(session)

    async def get_all(self) -> List[Session]:
        """获取所有会话列表"""
        # 构建查询语句，按最新消息时间降序排列
        stmt = select(SessionModel).order_by(SessionModel.latest_message_at.desc())
        # 执行查询
        result = await self.db_session.execute(stmt)
        # 获取所有结果记录
        records = result.scalars().all()

        # 将数据库模型转换为领域模型并返回
        return [record.to_domain() for record in records]

    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """根据id查询会话"""
        # 构建查询语句，根据session_id查找对应的会话记录
        stmt = select(SessionModel).where(SessionModel.id == session_id)
        # 执行查询
        result = await self.db_session.execute(stmt)
        # 获取查询结果，如果不存在则返回None
        record = result.scalar_one_or_none()

        # 如果找到了记录，则转换为领域模型并返回；否则返回None
        return record.to_domain() if record is not None else None

    async def delete_by_id(self, session_id: str) -> None:
        """根据传递的id删除会话"""
        # 构建删除语句，根据session_id删除对应的会话记录
        stmt = delete(SessionModel).where(SessionModel.id == session_id)

        # 执行删除操作
        await self.db_session.execute(stmt)

    async def update_title(self, session_id: str, title: str) -> None:
        """更新会话标题"""
        # 构建更新语句，根据session_id更新对应的会话标题
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(title=title)
        )
        # 执行更新操作
        result = await self.db_session.execute(stmt)

        # 检查是否有行被更新，如果没有则抛出异常
        if result.rowcount == 0:
            raise ValueError(f"会话[{session_id}]不存在，请核实后重试")

    async def update_latest_message(self, session_id: str, message: str, timestamp: datetime) -> None:
        """更新会话最新消息"""
        # 构建更新语句，根据session_id更新对应的会话最新消息内容和时间戳
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(
                latest_message=message,
                latest_message_at=timestamp,
            )
        )
        # 执行更新操作
        result = await self.db_session.execute(stmt)

        # 检查是否有行被更新，如果没有则抛出异常
        if result.rowcount == 0:
            raise ValueError(f"会话[{session_id}]不存在，请核实后重试")

    async def update_status(self, session_id: str, status: SessionStatus) -> None:
        """更新会话状态"""
        """更新会话状态"""
        # 构建更新语句，根据session_id更新对应的会话状态
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(status=status.value)
        )
        # 执行更新操作
        result = await self.db_session.execute(stmt)

        # 检查是否有行被更新，如果没有则抛出异常
        if result.rowcount == 0:
            raise ValueError(f"会话[{session_id}]不存在，请核实后重试")

    async def update_unread_message_count(self, session_id: str, count: int) -> None:
        """更新会话的未读消息数"""
        """更新会话的未读消息数"""
        # 构建更新语句，根据session_id更新对应的会话未读消息数量
        stmt = (
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(unread_message_count=count)
        )
        # 执行更新操作
        result = await self.db_session.execute(stmt)

        # 检查是否有行被更新，如果没有则抛出异常
        if result.rowcount == 0:
            raise ValueError(f"会话[{session_id}]不存在，请核实后重试")