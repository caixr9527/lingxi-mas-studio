#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/13 17:15
@Author : caixiaorong01@outlook.com
@File   : shell.py
"""
import asyncio
import codecs
import getpass
import logging
import os
import re
import shutil
import socket
import sys
import uuid
from typing import Dict, Optional, List

from app.interfaces.errors import BadRequestException, AppException, NotFoundException
from app.models import ShellExecResult, Shell, ConsoleRecord, ShellWaitResult, ShellViewResult

logger = logging.getLogger(__name__)


class ShellService:
    active_shells: Dict[str, Shell] = {}

    @classmethod
    def _get_display_path(cls, path: str) -> str:
        """
        获取显示路径
        :param path:
        :return:
        """
        home_dir = os.path.expanduser("~")
        logger.debug(f"home_dir: {home_dir}, 路径为: {path}")
        if path.startswith(home_dir):
            return path.replace(home_dir, "~", 1)
        else:
            return path

    def _format_ps1(self, exec_dir: str) -> str:
        username = getpass.getuser()
        hostname = socket.gethostname()
        display_dir = self._get_display_path(exec_dir)
        return f"{username}@{hostname}:{display_dir}"

    async def _create_process(self, exec_dir: str, command: str) -> asyncio.subprocess.Process:
        logger.debug(f"正在创建Shell进程, 执行目录: {exec_dir}, 命令: {command}")
        shell_exec = None
        if sys.platform != "win32":
            if os.path.exists("/bin/bash"):
                shell_exec = "/bin/bash"
            elif os.path.exists("/bin/zsh"):
                shell_exec = "/bin/zsh"
        elif sys.platform == "win32":
            shell_exec = shutil.which("powershell")
            if not shell_exec:
                shell_exec = shutil.which("cmd")
        return await asyncio.create_subprocess_shell(
            command,  # 要执行的命令
            executable=shell_exec,  # 执行解释器
            cwd=exec_dir,
            stdout=asyncio.subprocess.PIPE,  # 创建管道以捕获标准输出
            stderr=asyncio.subprocess.STDOUT,  # 将标准错误重定向到标准输出流
            stdin=asyncio.subprocess.PIPE,  # 创建管道以允许标准输入
            limit=1024 * 1024,  # 设置缓冲区大小并限制为1MB
        )

    async def _start_output_reader(self, session_id: str, process: asyncio.subprocess.Process) -> None:
        logger.debug(f"正在启动Shell输出读取器, 会话: {session_id}")
        if sys.platform == "win32":
            encoding = "gb18030"  # gb18030比gbk支持的生僻字更多，且兼容gbk
        else:
            encoding = "utf-8"

        # 创建增量编码器（解决字符被切断的问题）
        decoder = codecs.getincrementaldecoder(encoding)(errors="replace")
        shell = self.active_shells.get(session_id)

        while True:
            if process.stdout:
                try:
                    buffer = await process.stdout.read(4096)
                    if not buffer:
                        break

                    output = decoder.decode(buffer, final=False)

                    if shell:
                        shell.output += output
                        if shell.console_records:
                            shell.console_records[-1].output += output
                except Exception as e:
                    logger.error(f"读取进程输出时错误: {str(e)}")
                    break
            else:
                break

        logger.debug(f"Shell输出读取器已结束, 会话: {session_id}")

    @classmethod
    def _remove_ansi_escape_codes(cls, text: str) -> str:
        """
        去除ANSI转义码
        :param text:
        :return:
        """
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub("", text)

    @classmethod
    def create_session_id(cls) -> str:
        """
        创建Shell会话ID
        :return:
        """
        session_id = str(uuid.uuid4())
        logger.info(f"创建Shell会话ID: {session_id}")
        return session_id

    def get_console_records(self, session_id: str) -> List[ConsoleRecord]:
        """从指定会话中获取控制台记录"""
        logger.debug(f"正在获取Shell会话的控制台记录: {session_id}")
        if session_id not in self.active_shells:
            logger.error(f"Shell会话不存在: {session_id}")
            raise NotFoundException(f"Shell会话不存在: {session_id}")

        console_records = self.active_shells[session_id].console_records
        clean_console_records = []

        for console_record in console_records:
            clean_console_records.append(ConsoleRecord(
                ps1=console_record.ps1,
                command=console_record.command,
                output=self._remove_ansi_escape_codes(console_record.output),
            ))

        return clean_console_records

    async def wait_for_process(self, session_id: str, seconds: Optional[int] = None) -> ShellWaitResult:
        seconds = 60 if seconds is None or seconds <= 0 else seconds
        logger.debug(f"正在等待Shell进程, 会话: {session_id}, 超时为: {seconds}秒")
        if session_id not in self.active_shells:
            logger.error(f"会话: {session_id} 不存在")
            raise NotFoundException(f"会话: {session_id} 不存在")
        shell = self.active_shells[session_id]
        process = shell.process

        try:

            await asyncio.wait_for(process.wait(), timeout=seconds)
            logger.info(f"Shell进程已结束, 会话: {session_id} 返回代码: {process.returncode}")
            return ShellWaitResult(
                returncode=process.returncode,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Shell进程等待超时: {seconds} s, 会话: {session_id}")
            raise BadRequestException(f"Shell进程等待超时: {seconds} s")
        except Exception as e:
            logger.error(f"等待Shell进程时错误: {str(e)}")
            raise AppException(f"等待Shell进程时错误: {str(e)}")

    async def view_shell(self, session_id: str, console: bool = False) -> ShellViewResult:
        logger.debug(f"正在查看Shell内容, 会话: {session_id}, 是否返回控制台记录列表: {console}")
        if session_id not in self.active_shells:
            logger.error(f"会话: {session_id} 不存在")
            raise NotFoundException(f"会话: {session_id} 不存在")
        shell = self.active_shells[session_id]

        raw_output = shell.output
        clean_output = self._remove_ansi_escape_codes(raw_output)

        if console:
            console_records = self.get_console_records(session_id)
        else:
            console_records = []

        return ShellViewResult(
            session_id=session_id,
            output=clean_output,
            console_records=console_records,
        )

    async def exec_command(
            self,
            session_id: str,
            exec_dir: str,
            command: str,
    ) -> ShellExecResult:
        """
        执行Shell命令
        :param session_id:
        :param exec_dir:
        :param command:
        :return:
        """
        logger.info(f"会话: {session_id} 执行Shell命令: {command}")
        if not exec_dir or exec_dir == "":
            exec_dir = os.path.expanduser("~")

        if not os.path.exists(exec_dir):
            logger.error(f"会话: {session_id} 执行Shell命令: {command} 失败, 目标目录不存在: {exec_dir}")
            raise BadRequestException(f"目标目录不存在: {exec_dir}")

        try:
            ps1 = self._format_ps1(exec_dir)
            if session_id not in self.active_shells:
                logger.debug(f"创建Shell会话: {session_id}")
                process = await self._create_process(exec_dir, command)
                self.active_shells[session_id] = Shell(
                    process=process,
                    exec_dir=exec_dir,
                    output="",
                    console_records=[ConsoleRecord(ps1=ps1, command=command, output="")]
                )

                await asyncio.create_task(self._start_output_reader(session_id, process))
            else:
                logger.debug(f"会话: {session_id} 存在, 执行命令: {command}")
                shell = self.active_shells[session_id]

                old_process = shell.process

                if old_process.returncode is None:
                    logger.debug(f"正在终止旧进程,会话: {session_id}")
                    try:
                        old_process.terminate()
                        await asyncio.wait_for(old_process.wait(), timeout=1)
                    except Exception as e:
                        logger.warning(f"终止旧进程失败,会话: {session_id}, 错误: {e}")
                        old_process.kill()

                process = await self._create_process(exec_dir, command)

                shell.process = process
                shell.exec_dir = exec_dir
                shell.output = ""
                shell.console_records.append(ConsoleRecord(ps1=ps1, command=command, output=""))

                await asyncio.create_task(self._start_output_reader(session_id, process))

            try:
                logger.debug(f"正在等待会话中的命令执行完成,会话: {session_id}")
                wait_result = await self.wait_for_process(session_id, seconds=5)

                if wait_result.returncode is not None:
                    logger.debug(f"Shell会话进程已结束, 代码: {wait_result.returncode}")
                    view_result = await self.view_shell(session_id)

                    return ShellExecResult(
                        session_id=session_id,
                        command=command,
                        status="completed",
                        returncode=wait_result.returncode,
                        output=view_result.output
                    )
            except BadRequestException as _:
                logger.warning(f"进程在会话超时后仍在运行: {session_id}")
                pass
            except Exception as e:
                logger.warning(f"等待进程时出现异常: {str(e)}")
                pass

            return ShellExecResult(
                session_id=session_id,
                command=command,
                status="running",
            )

        except Exception as e:
            logger.error(f"执行Shell命令: {command} 失败, 错误: {str(e)}", exc_info=True)
            raise AppException(
                msg=f"执行Shell命令: {command} 错误: {str(e)}",
                data={
                    "session_id": session_id,
                    "command": command
                }
            )
