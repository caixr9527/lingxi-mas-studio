#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/30 15:27
@Author : caixiaorong01@outlook.com
@File   : bing_search.py
"""
import logging
import re
import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.domain.external import SearchEngine
from app.domain.models import ToolResult, SearchResults, SearchResultItem

logger = logging.getLogger(__name__)


class BingSearchEngine(SearchEngine):
    """bing搜索引擎"""

    def __init__(self):
        """构造函数，完成bing搜索引擎初始化，涵盖基础URL、headers、cookies"""
        self.base_url = "https://www.bing.com/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.cookies = httpx.Cookies()

    async def invoke(self, query: str, date_range: Optional[str] = None) -> ToolResult[SearchResults]:
        """传递query+date_range使用httpx+bs4调用bing搜索并获取搜索结果"""
        # 构造搜索参数
        params = {"q": query}

        # 如果指定了时间范围且不为'all'，则添加时间过滤参数
        if date_range and date_range != "all":
            # 计算从Unix纪元开始的天数，用于构建时间过滤器
            days_since_epoch = int(time.time() / (24 * 60 * 60))

            # 不同时间范围对应的Bing过滤器参数
            date_mapping = {
                "past_hour": "ex1%3a\"ez1\"",   # 过去一小时
                "past_day": "ex1%3a\"ez1\"",    # 过去一天
                "past_week": "ex1%3a\"ez2\"",   # 过去一周
                "past_month": "ex1%3a\"ez3\"",  # 过去一个月
                "past_year": f"ex1%3a\"ez5_{days_since_epoch - 365}_{days_since_epoch}\""  # 过去一年
            }

            # 如果指定的时间范围在映射中，则添加过滤器参数
            if date_range in date_mapping:
                params["filters"] = date_mapping[date_range]

        try:
            # 使用httpx创建异步HTTP客户端进行搜索请求
            async with httpx.AsyncClient(
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=60,
                    follow_redirects=True,
            ) as client:
                # 发送GET请求到Bing搜索接口
                response = await client.get(self.base_url, params=params)
                # 检查响应状态码，如果不是2xx则抛出异常
                response.raise_for_status()

                # 更新cookies，保存会话信息
                self.cookies.update(response.cookies)

                # 使用BeautifulSoup解析HTML响应内容
                soup = BeautifulSoup(response.text, "html.parser")

                # 存储解析后的搜索结果列表
                search_results = []
                # 查找所有搜索结果项，class为'b_algo'
                result_items = soup.find_all("li", class_="b_algo")

                # 遍历每个搜索结果项并提取信息
                for item in result_items:
                    try:
                        title, url = ("", "")

                        # 尝试从<h2>标签中提取标题和链接
                        title_tag = item.find("h2")
                        if title_tag:
                            a_tag = title_tag.find("a")
                            if a_tag:
                                title = a_tag.get_text(strip=True)
                                url = a_tag.get("href", "")

                        # 如果未找到标题，则尝试从其他<a>标签中查找
                        if not title:
                            a_tags = item.find_all("a")
                            for a_tag in a_tags:
                                text = a_tag.get_text(strip=True)
                                # 筛选合适的文本作为标题（长度大于10且不是URL）
                                if len(text) > 10 and not text.startswith("http"):
                                    title = text
                                    url = a_tag.get("href", "")
                                    break

                        # 如果仍未找到标题，则跳过该项
                        if not title:
                            continue

                        # 提取摘要信息
                        snippet = ""
                        # 首先尝试从特定class的元素中提取摘要
                        snippet_items = item.find_all(
                            ["p", "div"],
                            class_=re.compile(r'b_lineclamp|b_descript|b_caption')
                        )
                        if snippet_items:
                            snippet = snippet_items[0].get_text(strip=True)

                        # 如果未找到摘要，则尝试从<p>标签中提取
                        if not snippet:
                            p_tags = item.find_all("p")
                            for p in p_tags:
                                text = p.get_text(strip=True)
                                # 选择长度足够的文本作为摘要
                                if len(text) > 20:
                                    snippet = text
                                    break

                        # 如果仍未找到摘要，则从整个item文本中提取合适的句子
                        if not snippet:
                            all_text = item.get_text(strip=True)
                            sentences = re.split(r'[.!?\n。！]', all_text)
                            for sentence in sentences:
                                clean_sentence = sentence.strip()
                                # 选择长度足够且不同于标题的句子作为摘要
                                if len(clean_sentence) > 20 and clean_sentence != title:
                                    snippet = clean_sentence
                                    break

                        # 处理相对URL，转换为绝对URL
                        if url and not url.startswith("http"):
                            if url.startswith("//"):
                                url = "https:" + url
                            elif url.startswith("/"):
                                url = "https://www.bing.com" + url

                        # 创建搜索结果项对象并添加到结果列表
                        search_results.append(SearchResultItem(
                            title=title,
                            url=url,
                            snippet=snippet,
                        ))

                    except Exception as e:
                        # 记录单个搜索结果解析失败的日志，继续处理下一个结果
                        logger.warning(f"Bing搜索结果解析失败: {str(e)}")
                        continue

                # 提取总结果数
                total_results = 0
                # 首先尝试从包含"results"文本的元素中提取总数
                result_stats = soup.find_all(string=re.compile(r"\d+[,\d+]\s*results"))
                if result_stats:
                    for stat in result_stats:
                        match = re.search(r"([\d,]+)\s*results", stat)
                        if match:
                            try:
                                # 解析匹配到的数字并去除逗号
                                total_results = int(match.group(1).replace(",", ""))
                                break
                            except Exception:
                                continue

                # 如果第一种方法未找到总数，则尝试第二种方法
                if total_results == 0:
                    count_elements = soup.find_all(
                        ["span", "div", "p"],
                        class_=re.compile(r"sb_count|b_focusTextMedium")
                    )
                    for element in count_elements:
                        text = element.get_text(strip=True)
                        match = re.search(r"([\d,]+)\s*results", text)
                        if match:
                            try:
                                # 解析匹配到的数字并去除逗号
                                total_results = int(match.group(1).replace(',', ''))
                                break
                            except Exception:
                                continue

                # 构造最终的搜索结果对象
                results = SearchResults(
                    query=query,
                    date_range=date_range,
                    total_results=total_results,
                    results=search_results,
                )
                # 返回成功的工具执行结果
                return ToolResult(success=True, data=results)
        except Exception as e:
            # 记录搜索过程中的错误日志
            logger.error(f"Bing搜索出错: {str(e)}")
            # 构造错误情况下的搜索结果对象
            error_results = SearchResults(
                query=query,
                date_range=date_range,
                total_results=0,
                results=[],
            )
            # 返回失败的工具执行结果
            return ToolResult(
                success=False,
                message=f"Bing搜索出错: {str(e)}",
                data=error_results,
            )


if __name__ == "__main__":
    import asyncio


    async def main():
        search_engine = BingSearchEngine()
        result = await search_engine.invoke("香港火灾已致128人遇难", "all")

        print(result)
        for item in result.data.results:
            print(item)


    asyncio.run(main())
