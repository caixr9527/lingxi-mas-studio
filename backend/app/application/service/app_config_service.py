#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/17 10:23
@Author : caixiaorong01@outlook.com
@File   : app_config_service.py
"""
from app.domain.models import AppConfig, LLMConfig, AgentConfig, MCPConfig
from app.domain.repositories import AppConfigRepository
from app.application.errors import NotFoundError


class AppConfigService:
    """应用配置服务"""

    def __init__(self, app_config_repository: AppConfigRepository):
        self.app_config_repository = app_config_repository

    async def _load_app_config(self) -> AppConfig:
        """
        加载应用配置
        
        Returns:
            AppConfig: 应用配置对象
        """
        return self.app_config_repository.load()

    async def get_llm_config(self) -> LLMConfig:
        """
        获取LLM配置
        
        Returns:
            LLMConfig: LLM配置对象
        """
        app_config = await self._load_app_config()
        return app_config.llm_config

    async def update_llm_config(self, llm_config: LLMConfig) -> LLMConfig:
        """
        更新LLM配置
        
        Args:
            llm_config (LLMConfig): 新的LLM配置对象
            
        Returns:
            LLMConfig: 更新后的LLM配置对象
        """
        app_config = await self._load_app_config()

        # 如果新的api_key为空，则保留原有的api_key
        if not llm_config.api_key.strip():
            llm_config.api_key = app_config.llm_config.api_key
        app_config.llm_config = llm_config

        self.app_config_repository.save(app_config)

        return app_config.llm_config

    async def get_agent_config(self) -> AgentConfig:
        """
        获取Agent配置
        
        Returns:
            AgentConfig: Agent配置对象
        """
        app_config = await self._load_app_config()
        return app_config.agent_config

    async def update_agent_config(self, agent_config: AgentConfig) -> AgentConfig:
        """
        更新Agent配置
        
        Args:
            agent_config (AgentConfig): 新的Agent配置对象
            
        Returns:
            AgentConfig: 更新后的Agent配置对象
        """
        app_config = await self._load_app_config()
        app_config.agent_config = agent_config
        self.app_config_repository.save(app_config)
        return app_config.agent_config

    async def update_and_create_mcp_servers(self, mcp_config: MCPConfig) -> MCPConfig:
        """
        更新并创建MCP服务器配置
        
        Args:
            mcp_config (MCPConfig): 新的MCP配置对象
            
        Returns:
            MCPConfig: 更新后的MCP配置对象
        """
        app_config = await self._load_app_config()
        # 更新MCP服务器配置信息
        app_config.mcp_config.mcpServers.update(mcp_config.mcpServers)
        # 保存更新后的应用配置
        self.app_config_repository.save(app_config)
        # 返回更新后的MCP配置
        return app_config.mcp_config

    async def delete_mcp_server(self, server_name: str) -> MCPConfig:
        """
        删除MCP服务器配置

        Args:
            server_name (str): 要删除的MCP服务器名称

        Returns:
            MCPConfig: 删除后的MCP配置对象
        """
        # 加载应用配置
        app_config = await self._load_app_config()
        # 检查要删除的MCP服务器是否存在
        if server_name not in app_config.mcp_config.mcpServers:
            raise NotFoundError(f"MCP服务器 {server_name} 不存在")

        # 从配置中删除指定的MCP服务器
        del app_config.mcp_config.mcpServers[server_name]
        # 保存更新后的应用配置
        self.app_config_repository.save(app_config)
        # 返回更新后的MCP配置
        return app_config.mcp_config

    async def set_mcp_server_enabled(self, server_name: str, enabled: bool) -> MCPConfig:
        # 加载应用配置
        app_config = await self._load_app_config()
        # 检查要删除的MCP服务器是否存在
        if server_name not in app_config.mcp_config.mcpServers:
            raise NotFoundError(f"MCP服务器 {server_name} 不存在")

        # 设置指定MCP服务器的启用状态
        app_config.mcp_config.mcpServers[server_name].enabled = enabled
        # 保存更新后的应用配置
        self.app_config_repository.save(app_config)
        # 返回更新后的MCP配置
        return app_config.mcp_config
