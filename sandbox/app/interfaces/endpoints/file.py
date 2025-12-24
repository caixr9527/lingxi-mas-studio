#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/12 12:06
@Author : caixiaorong01@outlook.com
@File   : file.py
"""
from fastapi import APIRouter, Depends

from app.interfaces.schemas import Response, FileReadRequest, FileWriteRequest
from app.interfaces.service_dependencies import get_file_service
from app.models import FileReadResult, FileWriteResult
from app.services import FileService

router = APIRouter(prefix="/file", tags=["文件模块"])


@router.post(
    path="/read-file",
    response_model=Response[FileReadResult],
    summary="读取文件",
    description="读取文件",
)
async def read_file(
        request: FileReadRequest,
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


@router.post(
    path="/write-file",
    response_model=Response[FileWriteResult],
    summary="写入文件",
    description="写入文件",
)
async def write_file(
        request: FileWriteRequest,
        file_service: FileService = Depends(get_file_service)
) -> Response[FileWriteResult]:
    result = await file_service.write_file(
        filepath=request.filepath,
        content=request.content,
        append=request.append,
        leading_newline=request.leading_newline,
        trailing_newline=request.trailing_newline,
        sudo=request.sudo
    )
    return Response.success(
        msg="写入文件成功",
        data=result
    )
