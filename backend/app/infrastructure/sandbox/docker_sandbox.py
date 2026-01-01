#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2026/1/1 16:04
@Author : caixiaorong01@outlook.com
@File   : docker_sandbox.py
"""
import asyncio
import logging
import socket
import uuid
from typing import Optional, Self

import docker
import httpx
from async_lru import alru_cache
from docker.models.resource import Model

from app.domain.external import Sandbox
from core.config import get_settings

logger = logging.getLogger(__name__)


class DockerSandbox(Sandbox):

    def __init__(
            self,
            ip: Optional[str] = None,
            container_name: Optional[str] = None,
    ) -> None:
        self.client = httpx.AsyncClient(timeout=600)
        self._ip = ip
        self._container_name = container_name
        self._base_url = f"http://{ip}:8081"
        self._vnc_url = f"ws://{ip}:5901"
        self._cdp_url = f"http://{ip}:9222"

    @property
    def id(self) -> str:
        if not self._container_name:
            return "lingxi-sandbox"
        return self._container_name

    @property
    def vnc_url(self) -> str:
        return self._vnc_url

    @property
    def cdp_url(self) -> str:
        return self._cdp_url

    @classmethod
    @alru_cache(maxsize=128, typed=True)
    async def _resolve_hostname_to_ip(cls, hostname: str) -> Optional[str]:
        try:
            # 首先检查hostname是否已经是IP地址格式
            try:
                socket.inet_pton(socket.AF_INET, hostname)
                # 如果是IP地址格式，直接返回
                return hostname
            except OSError:
                # 如果不是IP地址格式，继续进行域名解析
                pass

            # 使用socket.getaddrinfo解析主机名到IP地址
            addr_info = socket.getaddrinfo(hostname, None, family=socket.AF_INET)
            if addr_info and len(addr_info) > 0:
                # 返回解析到的第一个IP地址
                return addr_info[0][4][0]
            return None
        except Exception as e:
            # 记录域名解析失败的错误日志
            logger.error(f"解析域名 {hostname} 失败: {e}")
            return None

    @classmethod
    def _get_container_ip(cls, container: Model) -> str:
        # 从容器属性中获取网络设置
        network_settings = container.attrs["NetworkSettings"]
        # 尝试直接获取IP地址
        ip_address = network_settings["IPAddress"]

        # 如果直接获取不到IP地址，则从网络配置中查找
        if not ip_address and "Networks" in network_settings:
            networks = network_settings["Networks"]
            # 遍历所有网络，查找有效的IP地址
            for network_name, network_config in networks.items():
                if "IPAddress" in network_config and network_config["IPAddress"]:
                    ip_address = network_config["IPAddress"]
                    break
        return ip_address

    @classmethod
    async def _create_task(cls) -> Self:
        # 获取配置信息
        settings = get_settings()
        image = settings.sandbox_image
        name_prefix = settings.sandbox_name_prefix
        # 生成唯一容器名称
        container_name = f"{name_prefix}-{str(uuid.uuid4())}"

        try:
            # 创建docker客户端
            client = docker.from_env()
            # 构建容器配置
            container_config = {
                "image": image,
                "name": container_name,
                "detach": True,  # 后台运行容器
                "remove": True,  # 容器停止时自动删除
                "environment": {
                    "SERVICE_TIMEOUT_MINUTES": settings.sandbox_ttl_minutes,  # 沙盒服务超时时间
                    "CHROME_ARGS": settings.sandbox_chrome_args,  # Chrome启动参数
                    "HTTPS_PROXY": settings.sandbox_https_proxy,  # HTTPS代理
                    "HTTP_PROXY": settings.sandbox_http_proxy,  # HTTP代理
                    "NO_PROXY": settings.sandbox_no_proxy,  # 不使用代理的地址
                }
            }

            # 如果配置了网络，则设置容器网络
            if settings.sandbox_network:
                container_config["network"] = settings.sandbox_network

            # 运行容器
            container = client.containers.run(**container_config)

            # 重新加载容器信息以获取最新状态
            container.reload()

            # 获取容器IP地址
            ip = cls._get_container_ip(container)
            # 返回DockerSandbox实例
            return DockerSandbox(ip=ip, container_name=container_name)

        except Exception as e:
            # 记录错误日志并抛出异常
            logger.error(f"创建docker沙盒失败: {e}")
            raise Exception(f"创建docker沙盒失败: {e}")

    @classmethod
    async def create(cls) -> Self:
        settings = get_settings()
        # 如果配置了沙盒地址，则直接使用该地址创建沙盒实例
        if settings.sandbox_address:
            ip = await cls._resolve_hostname_to_ip(settings.sandbox_address)
            return DockerSandbox(ip=ip)

        # 否则创建一个新的docker容器作为沙盒
        return await asyncio.to_thread(cls._create_task)
