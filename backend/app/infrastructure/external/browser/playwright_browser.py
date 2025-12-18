#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/8 17:35
@Author : caixiaorong01@outlook.com
@File   : playwright_browser.py
"""
import asyncio
import logging
from typing import Optional, List, Any

from markdownify import markdownify
from playwright.async_api import Playwright, Browser, Page, async_playwright

from app.domain.external import Browser as BrowserProtocol, LLM
from app.domain.models import ToolResult
from .playwright_browser_fun import GET_VISIBLE_CONTENT_FUNC, GET_INTERACTIVE_ELEMENTS_FUNC, INJECT_CONSOLE_LOGS_FUNC

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

    async def _extract_content(self) -> str:
        # 获取页面可见内容
        visible_content = await self.page.evaluate(GET_VISIBLE_CONTENT_FUNC)
        # 将HTML内容转换为Markdown格式
        markdown_content = markdownify(visible_content)
        # 限制内容长度最多为50000字符
        max_content_length = min(len(markdown_content), 50000)
        # 如果配置了LLM，则使用LLM处理内容
        if self.llm:
            # 调用LLM提取并格式化内容
            response = await self.llm.invoke([
                {
                    "role": "system",
                    "content": "您是一名专业的网页信息提取助手。请从当前页面内容中提取所有信息并将其转换为markdown格式。",
                },
                {
                    "role": "user",
                    "content": markdown_content[:max_content_length],
                }
            ])
            # 返回LLM处理后的内容
            return response.get("content", "")
        else:
            # 没有LLM时直接返回截取后的Markdown内容
            return markdown_content[:max_content_length]

    async def _extract_interactive_elements(self) -> List[str]:
        """提取当前页面上的可交互元素"""
        # 确保页面已初始化
        await self._ensure_page()

        # 清空页面的交互元素缓存
        self.page.interactive_elements_cache = []

        # 执行JavaScript函数获取页面上所有可交互的元素
        interactive_elements = await self.page.evaluate(GET_INTERACTIVE_ELEMENTS_FUNC)

        # 将获取到的交互元素存储到页面缓存中
        self.page.interactive_elements_cache = interactive_elements

        # 格式化交互元素列表，生成易于阅读的字符串格式
        formatted_elements = []
        for element in interactive_elements:
            # 将每个元素格式化为"索引:<标签名>文本内容</标签名>"的形式
            formatted_elements.append(f"{element['index']}:<{element['tag']}>{element['text']}</{element['tag']}>")

        # 返回格式化后的交互元素列表
        return formatted_elements

    async def _get_element_by_id(self, index: int) -> Optional[Any]:
        """根据索引获取页面上的交互元素"""
        # 检查页面是否具有交互元素缓存、缓存是否为空或者索引是否超出范围
        if (
                not hasattr(self.page, "interactive_elements_cache") or
                not self.page.interactive_elements_cache or
                index >= len(self.page.interactive_elements_cache)
        ):
            return None
        # 构造CSS选择器来定位具有特定data-manus-id属性的元素
        selector = f'[data-manus-id="manus-element-{index}"]'
        # 使用选择器查询页面元素并返回
        return await self.page.query_selector(selector)

    async def click(
            self,
            index: Optional[int] = None,
            coordinate_x: Optional[float] = None,
            coordinate_y: Optional[float] = None,
    ) -> ToolResult:
        """点击页面上的元素"""
        await self._ensure_page()
        if coordinate_x is not None and coordinate_y is not None:
            # 根据坐标点击页面
            await self.page.mouse.click(coordinate_x, coordinate_y)
        elif index is not None:
            try:
                # 根据索引点击页面
                element = await self._get_element_by_id(index)
                if not element:
                    return ToolResult(
                        success=False,
                        message=f"未找到索引为 {index} 的元素",
                    )
                # 检查元素是否可见
                is_visible = await self.page.evaluate("""(element) => {
                                    if (!element) return false;
                                    const rect = element.getBoundingClientRect();
                                    const style = window.getComputedStyle(element);
                                    return !(
                                        rect.width === 0 ||
                                        rect.height === 0 ||
                                        style.display === 'none' ||
                                        style.visibility === 'hidden' ||
                                        style.opacity === '0'
                                    );
                                }""", element)

                # 如果元素不可见，则将其滚动到视图中
                if not is_visible:
                    await self.page.evaluate("""(element) => {
                                                        if (element) {
                                                            element.scrollIntoView({behavior: 'smooth', block: 'center'})
                                                        }
                                                    }""", element)
                    await asyncio.sleep(1)

                # 点击元素
                await element.click(timeout=5000)
            except Exception as e:
                return ToolResult(
                    success=False,
                    message=f"点击元素失败: {e}",
                )
        return ToolResult(
            success=True,
        )

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

    async def navigate(self, url: str) -> ToolResult:
        """导航到指定URL"""
        await self._ensure_page()

        try:
            self.page.interactive_elements_cache = []
            await self.page.goto(url)
            return ToolResult(
                success=True,
                data={"interactive_elements": await self._extract_interactive_elements()}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"导航到URL {url} 失败: {str(e)}"
            )

    async def view_page(self) -> ToolResult:
        """查看当前页面内容"""
        await self._ensure_page()
        await self.wait_for_page_load()

        interactive_elements = await self._extract_interactive_elements()
        return ToolResult(
            success=True,
            data={
                "content": await self._extract_content(),
                "interactive_elements": interactive_elements,
            }
        )

    async def input(
            self,
            text: str,
            press_enter: bool,
            index: Optional[int] = None,
            coordinate_x: Optional[float] = None,
            coordinate_y: Optional[float] = None,
    ) -> ToolResult:
        """根据传递的文本+换行标识+索引+xy位置实现输入框文本输入"""
        await self._ensure_page()

        # 根据提供的坐标或索引在相应元素上输入文本
        if coordinate_x is not None and coordinate_y is not None:
            # 如果提供了坐标，则在指定坐标位置点击并输入文本
            await self.page.mouse.click(coordinate_x, coordinate_y)
            await self.page.keyboard.type(text)
        elif index is not None:
            # 如果提供了索引，则查找对应元素并输入文本
            try:
                element = await self._get_element_by_id(index)
                if not element:
                    return ToolResult(success=False, message=f"输入文本失败, 该元素不存在")

                try:
                    # 清空元素现有内容并输入新文本
                    await element.fill("")
                    await element.type(text)
                except Exception as e:
                    await element.click()
                    await element.type(text)
            except Exception as e:
                return ToolResult(success=False, message=f"输入文本失败: {str(e)}")

        # 如果需要按下回车键，则执行回车操作
        if press_enter:
            await self.page.keyboard.press("Enter")

        return ToolResult(success=True)

    async def move_mouse(self, coordinate_x: float, coordinate_y: float) -> ToolResult:
        """传递xy坐标移动鼠标"""
        await self._ensure_page()
        await self.page.mouse.move(coordinate_x, coordinate_y)
        return ToolResult(success=True)

    async def press_key(self, key: str) -> ToolResult:
        """传递按键进行模拟"""
        await self._ensure_page()
        await self.page.keyboard.press(key)
        return ToolResult(success=True)

    async def select_option(self, index: int, option: int) -> ToolResult:
        """传递索引+下拉菜单选项选择指定的菜单信息"""
        await self._ensure_page()

        try:
            # 根据索引获取下拉菜单元素
            element = await self._get_element_by_id(index)
            if not element:
                return ToolResult(success=False, message=f"使用索引[{index}]查找该下拉菜单元素不存在")

            # 选择指定的选项
            await element.select_option(index=option)
            return ToolResult(success=True)
        except Exception as e:
            # 处理选择下拉菜单选项时可能出现的异常
            return ToolResult(success=False, message=f"选择下拉菜单选项失败: {str(e)}")

    async def restart(self, url: str) -> ToolResult:
        """重启浏览器并导航到指定URL"""
        await self.cleanup()
        return await self.navigate(url)

    async def scroll_up(self, to_top: Optional[bool] = None) -> ToolResult:
        """向上滚动当前页面"""
        await self._ensure_page()
        if to_top:
            await self.page.evaluate("window.scrollTo(0, 0)")
        else:
            await self.page.evaluate("window.scrollBy(0, -window.innerHeight)")

        return ToolResult(
            success=True
        )

    async def scroll_down(self, to_bottom: Optional[bool] = None) -> ToolResult:
        """向下滚动当前页面"""
        await self._ensure_page()
        if to_bottom:
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        else:
            await self.page.evaluate("window.scrollBy(0, window.innerHeight)")

        return ToolResult(
            success=True
        )

    async def screenshot(self, full_page: Optional[bool] = None) -> bytes:
        """获取当前页面截图"""
        await self._ensure_page()
        screenshot_option = {
            "full_page": full_page,
            "type": "png",
        }
        return await self.page.screenshot(**screenshot_option)

    async def console_exec(self, javascript: str) -> ToolResult:
        """在浏览器控制台执行 JavaScript 脚本"""
        await self._ensure_page()
        try:
            await self.page.evaluate(INJECT_CONSOLE_LOGS_FUNC)
        except Exception as e:
            logger.warning(f"执行window.console.logs失败:{e}")
        result = await self.page.evaluate(javascript)
        return ToolResult(
            success=True,
            data={"result": result}
        )

    async def console_view(self, max_lines: Optional[int] = None) -> ToolResult:
        """查看浏览器控制台输出"""
        await self._ensure_page()
        # 从页面中获取控制台日志，如果不存在则返回空数组
        logs = await self.page.evaluate("""() => {
            return window.console.logs || [];
        }""")

        # 如果指定了最大行数，则只返回最后的max_lines条日志
        if max_lines is not None:
            logs = logs[-max_lines:]

        return ToolResult(
            success=True,
            data={"logs": logs}
        )
