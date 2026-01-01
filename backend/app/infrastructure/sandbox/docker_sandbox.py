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

from app.domain.external import Sandbox, Browser
from app.domain.models import ToolResult
from app.infrastructure.external.browser import PlaywrightBrowser
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
    def _create_task(cls) -> Self:
        # 获取配置信息
        settings = get_settings()
        image = settings.sandbox_image
        name_prefix = settings.sandbox_name_prefix
        # 生成唯一容器名称
        container_name = f"{name_prefix}-{str(uuid.uuid4())}"

        try:
            # 创建docker客户端
            docker_client = docker.from_env()
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
            container = docker_client.containers.run(**container_config)

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

    async def destroy(self) -> bool:
        try:
            # 关闭HTTP客户端连接
            if self.client:
                await self.client.aclose()

            # 如果存在容器名称，则从Docker中移除对应的容器
            if self._container_name:
                docker_client = docker.from_env()
                docker_client.containers.get(self._container_name).remove(force=True)
            return True
        except Exception as e:
            # 记录销毁沙盒失败的错误日志
            logger.error(f"销毁docker沙盒[{self._container_name}]失败: {e}")
            return False

    @classmethod
    @alru_cache(maxsize=128, typed=True)
    async def get(cls, id: str) -> Self:
        # 获取系统配置
        settings = get_settings()

        # 如果配置了沙盒地址，则直接使用该地址创建沙盒实例
        if settings.sandbox_address:
            # 解析沙盒地址为IP地址
            ip = await cls._resolve_hostname_to_ip(settings.sandbox_address)
            # 创建并返回DockerSandbox实例
            return DockerSandbox(ip=ip, container_name=id)

        # 从Docker获取指定名称的容器
        docker_client = docker.from_env()
        container = docker_client.containers.get(id)
        # 重新加载容器信息以获取最新状态
        container.reload()
        # 获取容器IP地址
        ip = cls._get_container_ip(container)
        # 创建并返回DockerSandbox实例
        return DockerSandbox(ip=ip, container_name=id)

    async def get_browser(self) -> Browser:
        # todo 扩展llm
        return PlaywrightBrowser(self.cdp_url, llm=None)

    async def ensure_sandbox(self) -> None:
        """确保沙箱一定存在/服务全部都开启了才执行后续步骤"""
        # 等待沙箱中所有服务启动完成
        # 最多重试30次，每次间隔2秒
        max_retries = 30
        retry_interval = 2

        for attempt in range(max_retries):
            try:
                # 发送请求获取supervisor状态
                response = await self.client.get(f"{self._base_url}/api/supervisor/status")
                response.raise_for_status()

                # 解析响应结果
                tool_result = ToolResult.from_sandbox(**response.json())

                # 检查请求是否成功
                if not tool_result.success:
                    logger.warning(f"Supervisor进程状态监测失败: {tool_result.message}")
                    await asyncio.sleep(retry_interval)
                    continue

                # 获取服务列表
                services = tool_result.data or []
                if not services:
                    logger.warning(f"Supervisor进程中未发现任何服务")
                    await asyncio.sleep(retry_interval)
                    continue

                # 检查所有服务是否都处于RUNNING状态
                all_running = True
                non_running_services = []
                for service in services:
                    service_name = service.get("name", "unknown")
                    state_name = service.get("statename", "")

                    # 如果服务状态不是RUNNING，则标记为未全部运行
                    if state_name != "RUNNING":
                        all_running = False
                        non_running_services.append(f"{service_name}({state_name})")

                # 如果所有服务都在运行，则返回
                if all_running:
                    logger.info("Sandbox Supervisor所有进程服务运行正常")
                    return
                else:
                    # 否则继续等待并记录未运行的服务
                    logger.info(f"正在等待Sandbox Supervisor进程服务运行, 还未运行的服务列表: {non_running_services}")
                    await asyncio.sleep(retry_interval)
            except Exception as e:
                # 捕获异常并记录日志，然后继续重试
                logger.warning(f"无法确认Sandbox Supervisor进程状态: {str(e)}")
                await asyncio.sleep(retry_interval)

        # 重试次数用尽后抛出异常
        logger.error(f"在经过{max_retries}次尝试后仍无法确认Sandbox Supervisor状态信息")
        raise Exception(f"在经过{max_retries}次尝试后仍无法确认Sandbox Supervisor状态信息")
