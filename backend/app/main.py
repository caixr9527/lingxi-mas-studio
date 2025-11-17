#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/12 16:56
@Author : caixiaorong01@outlook.com
@File   : main.py
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.logging import setup_logging
from app.infrastructure.storage import get_redis_client, get_postgres, get_cos
from app.interfaces.endpoints.routes import router
from app.interfaces.errors.exception_handlers import register_exception_handlers
from core.config import get_settings

settings = get_settings()

setup_logging()
logger = logging.getLogger()

openapi_tags = [
    {
        "name": "状态模块",
        "description": "包含 **状态监测** 等API接口，用于监测系统的运行状态。"
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期上下文管理"""
    logger.info(f"Starting app in {settings.env} mode")
    # 初始化数据库连接
    await get_redis_client().init()
    await get_postgres().init()
    await get_cos().init()

    try:
        yield
    finally:
        await get_redis_client().close()
        await get_postgres().close()
        await get_cos().close()
        logger.info("Shutting down app")


app = FastAPI(
    title="灵析通用智能体",
    description="灵析是一个通用的AI Agent系统,可以完全私有化部署,使用A2A+MCP连接Agent/Tool。",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
    version="0.1.0",
)

# 跨域处理
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 异常处理
register_exception_handlers(app=app)

# 路由集成
app.include_router(router=router, prefix="/api")
