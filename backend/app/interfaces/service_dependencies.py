#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 10:45
@Author : caixiaorong01@outlook.com
@File   : service_dependencies.py
"""
import logging
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.service import AppConfigService, FileService, StatusService, AgentService
from app.application.service.session_service import SessionService
from app.domain.repositories import SessionRepository
from app.infrastructure.external.file_storage import CosFileStorage
from app.infrastructure.external.health_checker import PostgresHealthChecker, RedisHealthChecker
from app.infrastructure.external.json_parser import RepairJsonParser
from app.infrastructure.external.llm import OpenAILLM
from app.infrastructure.external.search import BingSearchEngine
from app.infrastructure.external.task import RedisStreamTask
from app.infrastructure.repositories import FileAppConfigRepository, DBFileRepository
from app.infrastructure.sandbox.docker_sandbox import DockerSandbox
from app.infrastructure.storage import get_db_session, RedisClient, get_redis_client, Cos, get_cos
from app.interfaces.repository_dependencies import get_db_session_repository
from core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


@lru_cache()
def get_app_config_service() -> AppConfigService:
    """获取应用配置服务"""
    logger.info("加载获取AppConfigService")
    return AppConfigService(app_config_repository=FileAppConfigRepository(settings.app_config_filepath))


@lru_cache()
def get_status_service(
        db_session: AsyncSession = Depends(get_db_session),
        redis_client: RedisClient = Depends(get_redis_client)
) -> StatusService:
    """获取应用状态服务"""
    logger.info("加载获取StatusService")
    postgres_checker = PostgresHealthChecker(db_session=db_session)
    redis_checker = RedisHealthChecker(redis_client=redis_client)
    return StatusService(checkers=[postgres_checker, redis_checker])


@lru_cache()
def get_file_service(
        cos: Cos = Depends(get_cos),
        db_session: AsyncSession = Depends(get_db_session),
) -> FileService:
    # 初始化文件仓库和文件存储桶
    file_repository = DBFileRepository(db_session=db_session)
    file_storage = CosFileStorage(
        bucket=settings.cos_bucket,
        cos=cos,
        file_repository=file_repository
    )

    # 构建服务并返回
    return FileService(
        file_storage=file_storage,
        file_repository=file_repository,
    )


@lru_cache()
def get_session_service(
        session_repository: SessionRepository = Depends(get_db_session_repository),
) -> SessionService:
    """获取会话服务"""
    logger.info("加载获取SessionService")
    return SessionService(session_repository=session_repository)


def get_agent_service(
        cos: Cos = Depends(get_cos),
        db_session: AsyncSession = Depends(get_db_session),
        session_repository: SessionRepository = Depends(get_db_session_repository),
) -> AgentService:
    app_config_repository = FileAppConfigRepository(config_path=settings.app_config_filepath)
    app_config = app_config_repository.load()
    file_repository = DBFileRepository(db_session=db_session)

    llm = OpenAILLM(app_config.llm_config)
    file_storage = CosFileStorage(
        bucket=settings.cos_bucket,
        cos=cos,
        file_repository=file_repository
    )

    return AgentService(
        session_repository=session_repository,
        llm=llm,
        agent_config=app_config.agent_config,
        mcp_config=app_config.mcp_config,
        a2a_config=app_config.a2a_config,
        sandbox_cls=DockerSandbox,
        task_cls=RedisStreamTask,
        json_parser=RepairJsonParser(),
        search_engine=BingSearchEngine(),
        file_storage=file_storage,
        file_repository=file_repository,
    )
