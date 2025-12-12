#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/12 12:05
@Author : caixiaorong01@outlook.com
@File   : main.py
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import get_settings
from app.interfaces.endpoints import router


def setup_logging() -> None:
    """设置沙箱API应用日志"""
    # 获取项目配置
    settings = get_settings()

    # 获取根日志处理器
    root_logger = logging.getLogger()

    # 设置根日志处理器等级
    log_level = getattr(logging, settings.log_level)
    root_logger.setLevel(log_level)

    # 日志输出格式定义
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建控制台日志输出处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # 将控制台日志处理器添加到根日志处理器中
    root_logger.addHandler(console_handler)

    root_logger.info("沙箱系统系统日志模块初始化完成")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI生命周期上下文管理器"""
    # 应用开始运行之前的操作
    logger.info("沙箱正在初始化")

    try:
        # lifespan关键节点
        yield
    finally:
        # 应用结束后的操作
        logger.info("沙箱关闭成功")


# 初始化日志系统
setup_logging()
logger = logging.getLogger(__name__)

# 定义FastAPI路由tags标签
openapi_tags = [
    {
        "name": "文件模块",
        "description": "包含 **文件增删改查** 等 API 接口，用于实现对沙箱文件的操作。",
    },
    {
        "name": "Shell模块",
        "description": "包含 **执行/查看Shell** 等 API 接口，用于实现操控沙箱内部的 Shell 命令。",
    },
    {
        "name": "Supervisor模块",
        "description": "使用接口+Supervisor实现管理沙箱系统的程序逻辑",
    },
]

# 实例化FastAPI项目实例
app = FastAPI(
    title="沙箱系统",
    description="该沙箱系统中预装了Chrome、Python、Node.js，支持运行 Shell 命令、文件管理等功能",
    openapi_tags=openapi_tags,
    lifespan=lifespan,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册错误并处理
# register_exception_handlers(app)

# 集成路由
app.include_router(router, prefix="/api")
