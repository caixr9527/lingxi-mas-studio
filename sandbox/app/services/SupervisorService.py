#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/29 10:23
@Author : caixiaorong01@outlook.com
@File   : supervisorService.py
"""
import asyncio
import http.client
import logging
import socket
import xmlrpc.client
from typing import List, Any

from app.interfaces.errors import BadRequestException, AppException
from app.models import ProcessInfo

logger = logging.getLogger(__name__)


class UnixStreamHTTPConnection(http.client.HTTPConnection):
    """
    UnixStreamHTTPConnection
    """

    def __init__(self, host: str, socket_path: str, timeout=None) -> None:
        http.client.HTTPConnection.__init__(self, host, timeout=timeout)
        self.socket_path = socket_path

    def connect(self) -> None:
        """
        Connect to a host on a given (unix) port.
        """
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)


class UnixStreamTransport(xmlrpc.client.Transport):

    def __init__(self, socket_path: str) -> None:
        xmlrpc.client.Transport.__init__(self)
        self.socket_path = socket_path

    def make_connection(self, host) -> http.client.HTTPConnection:
        return UnixStreamHTTPConnection(host, self.socket_path)


class SupervisorService:

    def __init__(self) -> None:
        self.rpc_url = "/tmp/supervisor.sock"
        self._connect_rpc()

    def _connect_rpc(self) -> None:

        try:
            self.server = xmlrpc.client.ServerProxy(
                "http://localhost",
                transport=UnixStreamTransport(self.rpc_url),
            )
        except Exception as e:
            logger.error(f"连接Supervisor RPC服务失败: {e}")
            raise BadRequestException(msg=f"连接Supervisor RPC服务失败: {e}")

    @classmethod
    async def _call_rpc(cls, method, *args) -> Any:
        try:
            return await asyncio.to_thread(method, *args)
        except Exception as e:
            logger.error(f"调用Supervisor RPC服务失败: {e}")
            raise BadRequestException(msg=f"调用Supervisor RPC服务失败: {e}")

    async def get_all_process(self) -> List[ProcessInfo]:
        try:
            processes = await self._call_rpc(self.server.supervisor.getAllProcessInfo)
            return [ProcessInfo(**process) for process in processes]
        except Exception as e:
            logger.error(f"获取Supervisor所有进程失败: {e}")
            raise AppException(msg=f"获取Supervisor所有进程失败: {e}")
