#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 10:13
@Author : caixiaorong01@outlook.com
@File   : app_config_routes.py
"""
import logging

from fastapi import APIRouter, Depends

from app.application.service import AppConfigService
from app.domain.models import LLMConfig
from app.interfaces.dependencies import get_app_config_service
from app.interfaces.schemas import Response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api-config", tags=["设置模块"])


@router.get(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="获取LLM配置信息",
    description="包含LLM提供商的base_url、temperature"
)
async def get_llm_config(
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[LLMConfig]:
    """
    获取LLM配置信息
    """
    return Response.success(data=app_config_service.get_llm_config().model_dump(exclude={"api_key"}))


@router.post(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="更新LLM配置信息",
    description="更新LLM配置信息,当api_key为空,不更新该字段"
)
async def update_llm_config(
        new_llm_config: LLMConfig,
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[LLMConfig]:
    """
    更新LLM配置信息
    """
    updated_llm_config = app_config_service.update_llm_config(new_llm_config)
    return Response.success(
        msg="更新LLM配置信息成功",
        data=updated_llm_config.model_dump(exclude={"api_key"})
    )
