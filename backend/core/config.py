#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/12 16:53
@Author : caixiaorong01@outlook.com
@File   : config.py
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    log_level: str = "INFO"
    app_config_filepath: str = "config.yaml"

    sqlalchemy_database_uri: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/lingxi-mas"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    cos_region: str = "ap-guangzhou"
    cos_secret_id: str = ""
    cos_secret_key: str = ""
    cos_scheme: str = "https"
    cos_bucket: str = ""
    cos_domain: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
