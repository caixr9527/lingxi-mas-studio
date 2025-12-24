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
import socket
import uuid
from typing import Dict, Optional, List

from app.interfaces.errors import BadRequestException, AppException, NotFoundException
from app.models import (
    ShellExecuteResult,
    Shell,
    ConsoleRecord,
    ShellWaitResult,
    ShellReadResult,
    ShellWriteResult,
    ShellKillResult
)

logger = logging.getLogger(__name__)


class ShellService:
    active_shells: Dict[str, Shell]

    def __init__(self) -> None:
        self.active_shells = {}

    @classmethod
    def _get_display_path(cls, path: str) -> str:
        """
        获取显示路径
        :param path:
        :return:
        """
        # 获取用户的主目录路径
        home_dir = os.path.expanduser("~")
        logger.debug(f"home_dir: {home_dir}, 路径为: {path}")
        # 如果路径以主目录开头，则将主目录部分替换为波浪号(~)以简化显示
        if path.startswith(home_dir):
            return path.replace(home_dir, "~", 1)
        else:
            # 如果路径不以主目录开头，则直接返回原路径
            return path

    def _format_ps1(self, exec_dir: str) -> str:
        """
        格式化PS1提示符
        :param exec_dir: 执行目录
        :return: 格式化后的PS1字符串
        """
        username = getpass.getuser()  # 获取当前用户名
        hostname = socket.gethostname()  # 获取主机名
        display_dir = self._get_display_path(exec_dir)  # 获取显示路径
        return f"{username}@{hostname}:{display_dir}"  # 返回格式化后的PS1提示符

    @classmethod
    async def _create_process(cls, exec_dir: str, command: str) -> asyncio.subprocess.Process:
        """
        创建异步子进程来执行Shell命令
        
        :param exec_dir: 执行目录路径
        :param command: 要执行的命令
        :return: 异步子进程对象
        """
        logger.debug(f"正在创建Shell进程, 执行目录: {exec_dir}, 命令: {command}")
        shell_exec = None
        # 根据操作系统选择合适的Shell解释器
        if os.path.exists("/bin/bash"):
            shell_exec = "/bin/bash"
        elif os.path.exists("/bin/zsh"):
            shell_exec = "/bin/zsh"

        # 创建异步子进程
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
        encoding = "utf-8"
        # 创建增量编码器（解决字符被切断的问题）
        decoder = codecs.getincrementaldecoder(encoding)(errors="replace")
        shell = self.active_shells.get(session_id)

        while True:
            if process.stdout:
                try:
                    # 从进程的标准输出中读取数据，每次最多读取4096个字节
                    buffer = await process.stdout.read(4096)
                    # 如果没有读取到数据，说明进程已经结束，跳出循环
                    if not buffer:
                        break

                    # 使用增量解码器解码读取到的字节数据，final=False表示这不是最后的数据块
                    output = decoder.decode(buffer, final=False)

                    # 如果shell会话存在，则将解码后的输出追加到会话的输出记录中
                    if shell:
                        shell.output += output
                        # 如果控制台记录列表不为空，则将输出追加到最后一条控制台记录中
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
        """
        从指定会话中获取控制台记录列表，并清理ANSI转义码
        
        :param session_id: Shell会话ID
        :return: 清理后的控制台记录列表
        """
        logger.debug(f"正在获取Shell会话的控制台记录: {session_id}")
        # 检查会话是否存在
        if session_id not in self.active_shells:
            logger.error(f"Shell会话不存在: {session_id}")
            raise NotFoundException(f"Shell会话不存在: {session_id}")

        # 获取原始控制台记录
        console_records = self.active_shells[session_id].console_records
        clean_console_records = []

        # 遍历所有控制台记录，清理ANSI转义码后添加到新列表中
        for console_record in console_records:
            clean_console_records.append(ConsoleRecord(
                ps1=console_record.ps1,
                command=console_record.command,
                output=self._remove_ansi_escape_codes(console_record.output),
            ))

        return clean_console_records

    async def wait_process(self, session_id: str, seconds: Optional[int] = None) -> ShellWaitResult:
        # 设置默认超时时间为60秒，如果传入的seconds为None或小于等于0，则使用默认值
        seconds = 60 if seconds is None or seconds <= 0 else seconds
        logger.debug(f"正在等待Shell进程, 会话: {session_id}, 超时为: {seconds}秒")

        # 检查指定的会话是否存在，不存在则抛出异常
        if session_id not in self.active_shells:
            logger.error(f"会话: {session_id} 不存在")
            raise NotFoundException(f"会话: {session_id} 不存在")

        # 获取会话对应的Shell对象和进程对象
        shell = self.active_shells[session_id]
        process = shell.process

        try:
            # 等待进程结束，设置超时时间
            await asyncio.wait_for(process.wait(), timeout=seconds)
            logger.info(f"Shell进程已结束, 会话: {session_id} 返回代码: {process.returncode}")
            # 返回进程结束后的返回码
            return ShellWaitResult(
                returncode=process.returncode,
            )
        except asyncio.TimeoutError:
            # 处理等待超时的情况，记录日志并抛出异常
            logger.warning(f"Shell进程等待超时: {seconds} s, 会话: {session_id}")
            raise BadRequestException(f"Shell进程等待超时: {seconds} s")
        except Exception as e:
            # 处理其他异常情况，记录日志并抛出异常
            logger.error(f"等待Shell进程时错误: {str(e)}")
            raise AppException(f"等待Shell进程时错误: {str(e)}")

    async def read_shell_output(self, session_id: str, console: bool = False) -> ShellReadResult:
        """
        查看指定会话的Shell内容
        
        :param session_id: Shell会话ID
        :param console: 是否返回控制台记录列表
        :return: ShellViewResult对象，包含会话ID、清理后的输出和控制台记录列表
        """
        logger.debug(f"正在查看Shell内容, 会话: {session_id}, 是否返回控制台记录列表: {console}")
        # 检查会话是否存在，不存在则抛出异常
        if session_id not in self.active_shells:
            logger.error(f"会话: {session_id} 不存在")
            raise NotFoundException(f"会话: {session_id} 不存在")
        shell = self.active_shells[session_id]

        # 获取原始输出并清理ANSI转义码
        raw_output = shell.output
        clean_output = self._remove_ansi_escape_codes(raw_output)

        # 根据参数决定是否获取控制台记录列表
        if console:
            console_records = self.get_console_records(session_id)
        else:
            console_records = []

        # 返回包含会话信息、清理后输出和控制台记录的结果对象
        return ShellReadResult(
            session_id=session_id,
            output=clean_output,
            console_records=console_records,
        )

    async def exec_command(
            self,
            session_id: str,
            exec_dir: str,
            command: str,
    ) -> ShellExecuteResult:
        """
        执行Shell命令
        :param session_id:
        :param exec_dir:
        :param command:
        :return:
        """
        logger.info(f"会话: {session_id} 执行Shell命令: {command}")
        # 检查执行目录，如果为空则使用用户主目录
        if not exec_dir or exec_dir == "":
            exec_dir = os.path.expanduser("~")

        # 验证执行目录是否存在
        if not os.path.exists(exec_dir):
            logger.error(f"会话: {session_id} 执行Shell命令: {command} 失败, 目标目录不存在: {exec_dir}")
            raise BadRequestException(f"目标目录不存在: {exec_dir}")

        try:
            # 格式化PS1提示符
            ps1 = self._format_ps1(exec_dir)
            # 检查会话是否已存在
            if session_id not in self.active_shells:
                logger.debug(f"创建Shell会话: {session_id}")
                # 创建新的进程和会话
                process = await self._create_process(exec_dir, command)
                self.active_shells[session_id] = Shell(
                    process=process,
                    exec_dir=exec_dir,
                    output="",
                    console_records=[ConsoleRecord(ps1=ps1, command=command, output="")]
                )

                # 启动输出读取器任务
                await asyncio.create_task(self._start_output_reader(session_id, process))
            else:
                logger.debug(f"会话: {session_id} 存在, 执行命令: {command}")
                shell = self.active_shells[session_id]

                # 终止旧进程
                old_process = shell.process

                if old_process.returncode is None:
                    logger.debug(f"正在终止旧进程,会话: {session_id}")
                    try:
                        old_process.terminate()
                        await asyncio.wait_for(old_process.wait(), timeout=1)
                    except Exception as e:
                        logger.warning(f"终止旧进程失败,会话: {session_id}, 错误: {e}")
                        old_process.kill()

                # 创建新进程
                process = await self._create_process(exec_dir, command)

                # 更新会话信息
                shell.process = process
                shell.exec_dir = exec_dir
                shell.output = ""
                shell.console_records.append(ConsoleRecord(ps1=ps1, command=command, output=""))

                # 启动输出读取器任务
                await asyncio.create_task(self._start_output_reader(session_id, process))

            try:
                logger.debug(f"正在等待会话中的命令执行完成,会话: {session_id}")
                # 等待进程执行完成（最多5秒）
                wait_result = await self.wait_process(session_id, seconds=5)

                # 如果进程已完成，返回结果
                if wait_result.returncode is not None:
                    logger.debug(f"Shell会话进程已结束, 代码: {wait_result.returncode}")
                    view_result = await self.read_shell_output(session_id)

                    return ShellExecuteResult(
                        session_id=session_id,
                        command=command,
                        status="completed",
                        returncode=wait_result.returncode,
                        output=view_result.output
                    )
            except BadRequestException as _:
                # 处理超时情况（进程仍在运行）
                logger.warning(f"进程在会话超时后仍在运行: {session_id}")
                pass
            except Exception as e:
                # 处理其他异常
                logger.warning(f"等待进程时出现异常: {str(e)}")
                pass

            # 默认返回运行中状态
            return ShellExecuteResult(
                session_id=session_id,
                command=command,
                status="running",
            )

        except Exception as e:
            # 处理执行过程中的任何异常
            logger.error(f"执行Shell命令: {command} 失败, 错误: {str(e)}", exc_info=True)
            raise AppException(
                msg=f"执行Shell命令: {command} 错误: {str(e)}",
                data={
                    "session_id": session_id,
                    "command": command
                }
            )

    async def write_to_process(
            self,
            session_id: str,
            input_text: str,
            press_enter: bool = True
    ) -> ShellWriteResult:
        """
        向指定会话的Shell进程中写入数据
        
        :param session_id: Shell会话ID
        :param input_text: 要写入的文本内容
        :param press_enter: 是否在文本末尾添加回车符，默认为True
        :return: ShellWriteResult对象，表示写入操作的结果状态
        """
        logger.debug(f"会话: {session_id} 向进程写入数据: {input_text} press_enter: {press_enter}")
        # 检查会话是否存在，不存在则抛出异常
        if session_id not in self.active_shells:
            logger.error(f"会话: {session_id} 不存在")
            raise BadRequestException(f"会话: {session_id} 不存在")

        # 获取会话对应的Shell对象和进程对象
        shell = self.active_shells[session_id]
        process = shell.process

        try:
            # 检查进程是否已经结束，如果已结束则抛出异常
            if process.returncode is not None:
                logger.error(f"会话: {session_id} 进程已结束")
                raise BadRequestException(f"会话: {session_id} 进程已结束")

            # 根据操作系统确定编码方式和换行符
            encoding = "utf-8"
            line_ending = "\n"

            # 构造要发送的文本
            text_to_send = input_text
            if press_enter:
                text_to_send += line_ending

            # 将文本编码为字节数据
            input_data = text_to_send.encode(encoding)

            # 记录写入的文本到输出历史中
            log_text = input_text + ("\n" if press_enter else "")
            shell.output += log_text
            if shell.console_records:
                shell.console_records[-1].output += log_text

            # 向进程的标准输入写入数据并刷新缓冲区
            process.stdin.write(input_data)
            await process.stdin.drain()

            logger.info(f"会话: {session_id} 向进程写入数据: {input_text} press_enter: {press_enter} 成功")
            return ShellWriteResult(status="success")
        except UnicodeError as e:
            # 处理Unicode编码错误
            logger.error(f"编码错误: {str(e)}")
            raise AppException(msg=f"编码错误: {str(e)}")
        except Exception as e:
            # 处理其他异常情况
            logger.error(f"向进程写入数据失败: {str(e)}")
            raise AppException(msg=f"向进程写入数据失败: {str(e)}")

    async def kill_process(self, session_id: str) -> ShellKillResult:
        """
        终止指定会话的Shell进程
        
        :param session_id: Shell会话ID
        :return: ShellKillResult对象，表示终止操作的结果状态
        """
        logger.debug(f"正在关闭会话进程: {session_id}")
        # 检查会话是否存在，不存在则抛出异常
        if session_id not in self.active_shells:
            logger.error(f"会话: {session_id} 不存在")
            raise BadRequestException(f"会话: {session_id} 不存在")
        # 获取会话对应的Shell对象和进程对象
        shell = self.active_shells[session_id]
        process = shell.process

        try:
            # 检查进程是否仍在运行
            if process.returncode is None:
                logger.info(f"正在关闭会话进程: {session_id}")
                # 发送终止信号
                process.terminate()
                try:
                    # 等待进程正常结束，超时时间为3秒
                    await asyncio.wait_for(process.wait(), timeout=3)
                except asyncio.TimeoutError:
                    # 如果等待超时，则强制杀死进程
                    logger.warning(f"等待进程结束超时: {session_id}")
                    process.kill()

                logger.info(f"会话: {session_id} 进程已结束, 状态码: {process.returncode}")
                # 返回终止成功的结果
                return ShellKillResult(status="terminated", returncode=process.returncode)
            else:
                logger.info(f"会话: {session_id} 进程已结束, 返回码: {process.returncode}")
                # 返回进程已结束的结果
                return ShellKillResult(status="already_terminated", returncode=process.returncode)
        except Exception as e:
            # 处理关闭进程时出现的异常
            logger.error(f"关闭进程失败: {str(e)}", exc_info=True)
            raise AppException(msg=f"关闭进程失败: {str(e)}")
