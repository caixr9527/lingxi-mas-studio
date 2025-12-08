#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/8 17:35
@Author : caixiaorong01@outlook.com
@File   : playwright_browser.py
"""
import asyncio
import logging
from typing import Optional

from playwright.async_api import Playwright, Browser, Page, async_playwright

from app.domain.external import Browser as BrowserProtocol, LLM

logger = logging.getLogger(__name__)


class PlaywrightBrowser(BrowserProtocol):
    """Playwright 浏览器服务实现"""

    def __init__(
            self,
            cdp_url: str,
            llm: Optional[LLM]
    ) -> None:
        self.llm: Optional[LLM] = llm
        self.cdp_url: str = cdp_url
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def _ensure_browser(self) -> None:
        """确保浏览器已启动"""
        # 检查浏览器实例和页面实例是否都已创建，如果没有则尝试初始化
        if not self.browser or not self.page:
            # 调用初始化方法，如果初始化失败则抛出异常
            if not await self.initialize():
                raise Exception("初始化浏览器服务失败")

    async def _ensure_page(self) -> None:
        """确保当前页面已初始化"""
        await self._ensure_browser()

        # 如果当前没有页面，则创建新页面
        if not self.page:
            self.page = await self.browser.new_page()
        else:
            # 检查浏览器上下文是否存在
            contexts = self.browser.contexts
            if contexts:
                # 获取默认上下文（第一个上下文）
                default_context = contexts[0]
                # 获取上下文中的所有页面
                pages = default_context.pages
                if pages:
                    # 获取最新的页面（最后一个页面）
                    latest_page = pages[-1]

                    # 如果当前页面不是最新页面，则更新为最新页面
                    if self.page != latest_page:
                        self.page = latest_page

    async def initialize(self) -> bool:
        """初始化浏览器服务"""
        # 设置最大重试次数和初始重试间隔
        max_retries = 5
        retry_interval = 1

        # 开始重试循环
        for attempt in range(max_retries):
            try:
                # 启动playwright并连接到浏览器
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_url)

                # 获取浏览器上下文
                contexts = self.browser.contexts

                # 如果存在上下文且第一个上下文只有一个页面
                if contexts and len(contexts[0].pages) == 1:
                    page = contexts[0].pages[0]
                    # 检查页面URL是否为初始状态页面
                    if (
                            page.url == "about:blank" or
                            page.url == "chrome://newtab/" or
                            page.url == "chrome://new-tab-page/" or
                            not page.url
                    ):
                        # 如果是初始页面，则直接使用该页面
                        self.page = page
                    else:
                        # 如果不是初始页面，则创建新页面
                        self.page = await contexts[0].new_page()
                else:
                    # 如果没有上下文或上下文页面数不为1，则创建新的上下文和页面
                    context = contexts[0] if contexts else await self.browser.new_context()
                    self.page = await context.new_page()

                # 初始化成功，返回True
                return True

            except Exception as e:
                # 清理已创建的资源
                await self.cleanup()

                # 如果已经达到最大重试次数，则记录错误并返回False
                if attempt == max_retries - 1:
                    logger.error(
                        f"初始化浏览器服务失败,已重试 {max_retries} 次,请检查CDP URL和浏览器服务是否正常启动：{e}")
                    return False

                # 计算下一次重试间隔（指数退避，最大不超过10秒）
                retry_interval = min(retry_interval * 2, 10)
                logger.warning(f"初始化浏览器服务失败,正在重试...(重试次数:{attempt + 1}/{max_retries})")

                # 等待后继续重试
                await asyncio.sleep(retry_interval)

    async def cleanup(self) -> None:
        """清理浏览器服务"""
        try:
            # 关闭所有页面
            if self.browser:
                contexts = self.browser.contexts
                if contexts:
                    for context in contexts:
                        pages = context.pages
                        if pages:
                            for page in pages:
                                if not page.is_closed():
                                    await page.close()

            # 确保当前页面关闭
            if self.page and not self.page.is_closed():
                await self.page.close()

            # 关闭浏览器
            if self.browser:
                await self.browser.close()

            # 停止playwright
            if self.playwright:
                await self.playwright.stop()

        except Exception as e:
            logger.error(f"清理浏览器服务时发生错误: {e}")
        finally:
            # 重置所有引用
            self.page = None
            self.browser = None
            self.playwright = None

    async def wait_for_page_load(self, timeout: int = 15) -> bool:
        """等待页面加载完成"""
        # 确保页面已初始化
        await self._ensure_page()

        # 记录开始时间
        start_time = asyncio.get_event_loop().time()
        # 设置检查间隔为5秒
        check_interval = 5
        # 循环检查页面是否加载完成，直到超时
        while asyncio.get_event_loop().time() - start_time < timeout:
            # 通过执行JavaScript检查页面是否加载完成
            is_completed = await self.page.evaluate("""() => document.readyState === 'complete'""")
            if is_completed:
                # 页面加载完成，返回True
                return True
            # 等待下次检查
            await asyncio.sleep(check_interval)

        # 超时未完成加载，返回False
        return False
