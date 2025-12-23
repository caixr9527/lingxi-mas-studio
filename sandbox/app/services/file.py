#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/14 14:41
@Author : caixiaorong01@outlook.com
@File   : file.py
"""
import asyncio
import logging
import os.path
from typing import Optional

from app.interfaces.errors import NotFoundException, BadRequestException, AppException
from app.models import FileReadResult, FileWriteResult

logger = logging.getLogger(__name__)


class FileService:

    def __init__(self) -> None:
        pass

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
        try:
            if not os.path.exists(filepath) and not sudo:
                logger.error(f"文件不存在或没有权限访问: {filepath}")
                raise NotFoundException(f"文件不存在或没有权限访问: {filepath}")

            # 获取系统推荐的编码格式，Windows系统使用locale编码，其他系统默认使用UTF-8
            encoding = "utf-8"

            # 如果需要sudo权限且不是Windows系统，则使用sudo命令读取文件
            if sudo:
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
                    except Exception as ex:
                        # 捕获异常并抛出自定义异常
                        raise AppException(
                            msg=f"获取文件内容失败: {ex}"
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
        except Exception as e:
            logger.error(f"获取文件内容失败: {e}")
            if isinstance(e, BadRequestException):
                raise
            raise AppException(
                msg=f"获取文件内容失败: {e}"
            )

    @classmethod
    async def write_file(
            cls,
            filepath: str,
            content: str,
            append: bool = False,
            leading_newline: bool = False,
            trailing_newline: bool = False,
            sudo: bool = False
    ) -> FileWriteResult:
        """
        写入文件
        :param filepath: 文件路径
        :param content: 写入内容
        :param append: 是否追加写入
        :param leading_newline: 是否在内容前添加换行符
        :param trailing_newline: 是否在内容后添加换行符
        :param sudo: 是否使用sudo权限
        """
        try:
            # 处理前置换行符
            if leading_newline:
                content = "\n" + content
            # 处理后置换行符
            if trailing_newline:
                content += "\n"

            # 如果需要sudo权限且不是Windows系统，则使用sudo命令写入文件
            if sudo:
                # 确定写入模式：追加(>>)或覆盖(>)
                mode = ">>" if append else ">"

                # 创建临时文件路径
                temp_file = f"/tmp/file_write_{os.getpid()}.tmp"

                # 定义异步写入临时文件的函数
                def async_write_temp_file() -> int:
                    with open(temp_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    # 返回写入的字节数
                    return len(content.encode("utf-8"))

                # 在线程池中执行临时文件写入操作
                bytes_written = await asyncio.to_thread(async_write_temp_file)

                # 构造sudo命令将临时文件内容写入目标文件
                command = f"sudo bash -c \"cat {temp_file} {mode} {filepath}\""

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
                    raise BadRequestException(f"写入文件失败: {stderr.decode('utf-8')}")

                # 删除临时文件
                os.unlink(temp_file)

            # 普通文件写入方式（无需sudo或Windows系统）
            else:
                # 确保文件所在目录存在
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                # 定义异步写入文件的函数
                def async_write_file() -> int:
                    # 根据append参数选择写入模式：追加(a)或覆盖(w)
                    with open(filepath, "a" if append else "w", encoding="utf-8") as f:
                        f.write(content)
                    # 返回写入的字节数
                    return len(content.encode("utf-8"))

                # 在线程池中执行文件写入操作
                bytes_written = await asyncio.to_thread(async_write_file)

            # 返回文件写入结果对象
            return FileWriteResult(
                filepath=filepath,
                bytes_written=bytes_written
            )
        except Exception as e:
            logger.error(f"写入文件失败: {e}")
            # 如果是已知的BadRequestException异常则直接抛出
            if isinstance(e, BadRequestException):
                raise
            # 其他异常统一包装成AppException抛出
            raise AppException(
                msg=f"写入文件失败: {e}"
            )
