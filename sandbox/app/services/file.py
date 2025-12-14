#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/14 14:41
@Author : caixiaorong01@outlook.com
@File   : file.py
"""
import asyncio
import locale
import logging
import os.path
import sys
from typing import Optional

from app.interfaces.errors import NotFoundException, BadRequestException, AppException
from app.models import FileReadResult

logger = logging.getLogger(__name__)


class FileService:

    @classmethod
    async def read_file(
            cls,
            filepath: str,
            start_line: Optional[int] = None,
            end_line: Optional[int] = None,
            sudo: bool = False,
            max_length: int = 10000
    ) -> FileReadResult:
        """
        读取文件
        :param filepath: 文件路径
        :param start_line: 开始行数，索引从0开始
        :param end_line: 结束行数，不包括该行
        :param sudo: 是否使用sudo权限
        :param max_length: 最大读取行数
        """
        if not os.path.exists(filepath) and not sudo:
            logger.error(f"文件不存在或没有权限访问: {filepath}")
            raise NotFoundException(f"文件不存在或没有权限访问: {filepath}")

        # 获取系统推荐的编码格式，Windows系统使用locale编码，其他系统默认使用UTF-8
        encoding = locale.getpreferredencoding() if sys.platform == "win32" else "utf-8"

        # 如果需要sudo权限且不是Windows系统，则使用sudo命令读取文件
        if sudo and sys.platform != "win32":
            # 构造sudo cat命令来读取文件内容
            command = f"sudo cat '{filepath}'"
            # 创建异步子进程执行sudo命令
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # 等待命令执行完成并获取输出
            stdout, stderr = process.communicate()

            # 检查命令执行是否成功
            if process.returncode != 0:
                raise BadRequestException(f"获取文件内容失败: {stderr.decode(encoding)}")

            # 使用指定编码解码文件内容
            content = stdout.decode(encoding, errors="replace")

        # 普通文件读取方式（无需sudo或Windows系统）
        else:
            def async_read_file() -> str:
                try:
                    # 以指定编码打开并读取文件
                    with open(filepath, "r", encoding=encoding) as f:
                        return f.read()
                except Exception as e:
                    # 捕获异常并抛出自定义异常
                    raise AppException(
                        msg=f"获取文件内容失败: {e}"
                    )

            # 在线程池中执行文件读取操作，避免阻塞事件循环
            content = await asyncio.to_thread(async_read_file)

        # 根据指定的行范围截取文件内容
        if start_line is not None or end_line is not None:
            lines = content.splitlines()  # 将内容按行分割
            start = start_line if start_line is not None else 0  # 设置起始行，默认为0
            end = end_line if end_line is not None else len(lines)  # 设置结束行，默认为总行数
            content = "\n".join(lines[start:end])  # 重新组合指定范围的行

        # 如果设置了最大长度限制且内容超出限制，则截断内容
        if max_length is not None and 0 < max_length < len(content):
            content = content[:max_length] + "(truncated)"

        # 返回文件读取结果对象
        return FileReadResult(
            filepath=filepath,
            content=content
        )
