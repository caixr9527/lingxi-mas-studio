#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/12 12:06
@Author : caixiaorong01@outlook.com
@File   : file.py
"""
from fastapi import APIRouter, Depends

from app.interfaces.schemas import Response, ReadFileRequest
from app.interfaces.service_dependencies import get_file_service
from app.models import FileReadResult
from app.services import FileService

router = APIRouter(prefix="/file", tags=["文件模块"])


@router.post(
    path="/read-file",
    response_model=Response[FileReadResult],
    summary="读取文件",
    description="读取文件",
)
async def read_file(
        request: ReadFileRequest,
        file_service: FileService = Depends(get_file_service)
) -> Response[FileReadResult]:
    result = await file_service.read_file(
        filepath=request.filepath,
        start_line=request.start_line,
        end_line=request.end_line,
        sudo=request.sudo,
        max_length=request.max_length
    )
    return Response.success(
        msg="读取文件成功",
        data=result
    )
