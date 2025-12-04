#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/4 14:59
@Author : caixiaorong01@outlook.com
@File   : app_config.py
"""
from typing import List

from pydantic import BaseModel, Field

from app.domain.models import MCPTransport


class ListMCPServerItem(BaseModel):
    server_name: str = ""
    enabled: bool = True
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP
    tools: List[str] = Field(default_factory=list)


class ListMCPServerResponse(BaseModel):
    mcp_servers: List[ListMCPServerItem] = Field(default_factory=list)
