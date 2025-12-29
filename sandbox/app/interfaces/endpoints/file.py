#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/12 12:06
@Author : caixiaorong01@outlook.com
@File   : file.py
"""
import os

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse

from app.interfaces.schemas import (
    Response,
    FileReadRequest,
    FileWriteRequest,
    FileReplaceRequest,
    FileSearchRequest,
    FileFindRequest,
    FileCheckRequest,
    FileDeleteRequest
)
from app.interfaces.service_dependencies import get_file_service
from app.models import (
    FileReadResult,
    FileWriteResult,
    FileReplaceResult,
    FileSearchResult,
    FileFindResult,
    FileUploadResult,
    FileCheckResult,
    FileDeleteResult
)
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


@router.post(
    path="/replace-in-file",
    response_model=Response[FileReplaceResult],
    summary="替换文件中的文本",
    description="替换文件中的文本",
)
async def replace_in_file(
        request: FileReplaceRequest,
        file_service: FileService = Depends(get_file_service)
) -> Response[FileReplaceResult]:
    result = await file_service.replace_in_file(
        filepath=request.filepath,
        old_str=request.old_str,
        new_str=request.new_str,
        sudo=request.sudo
    )
    return Response.success(
        msg=f"文件内容替换成功，已替换{result.replace_count}处内容",
        data=result
    )


@router.post(
    path="search-in-file",
    response_model=Response[FileSearchResult],
    summary="在文件中搜索文本",
    description="在文件中搜索文本",
)
async def search_in_file(
        request: FileSearchRequest,
        file_service: FileService = Depends(get_file_service)
) -> Response[FileSearchResult]:
    result = await file_service.search_in_file(
        filepath=request.filepath,
        regex=request.regex,
        sudo=request.sudo
    )
    return Response.success(
        msg=f"文件内容搜索成功,找到{len(result.matches)}个匹配项",
        data=result
    )


@router.post(
    path="/find-files",
    response_model=Response[FileFindResult],
    summary="查找文件",
    description="查找文件",
)
async def find_files(
        request: FileFindRequest,
        file_service: FileService = Depends(get_file_service)
) -> Response[FileFindResult]:
    result = await file_service.find_files(
        dir_path=request.dir_path,
        glob_pattern=request.glob_pattern,
    )
    return Response.success(
        msg=f"文件搜索成功,找到{len(result.files)}个匹配项",
        data=result
    )


@router.post(
    path="/upload-file",
    response_model=Response[FileUploadResult],
    summary="上传文件",
    description="上传文件",
)
async def upload_file(
        file: UploadFile = File(...),
        filepath: str = Form(...),
        file_service: FileService = Depends(get_file_service)
) -> Response[FileUploadResult]:
    if not filepath:
        filepath = f"/tmp/{file.filename}"
    result = await file_service.upload_file(
        file=file,
        filepath=filepath,
    )
    return Response.success(
        msg="文件上传成功",
        data=result
    )


@router.post(
    path="/download-file",
    summary="下载文件",
    description="下载文件",
)
async def download_file(
        filepath: str,
        file_service: FileService = Depends(get_file_service)
) -> FileResponse:
    await file_service.ensure_file(filepath)

    filename = os.path.basename(filepath)
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.post(
    path="/check-file-exists",
    response_model=Response[FileCheckResult],
    summary="检查文件是否存在",
    description="检查文件是否存在",
)
async def check_file_exists(
        request: FileCheckRequest,
        file_service: FileService = Depends(get_file_service)
) -> Response[FileCheckResult]:
    result = await file_service.check_file_exists(filepath=request.filepath)

    return Response.success(
        msg="文件已存在" if result.exists else "文件不存在",
        data=result
    )


@router.post(
    path="/delete-file",
    response_model=Response[FileDeleteResult],
    summary="删除文件",
    description="删除文件",
)
async def delete_file(
        request: FileDeleteRequest,
        file_service: FileService = Depends(get_file_service)
) -> Response[FileDeleteResult]:
    result = await file_service.delete_file(filepath=request.filepath)

    return Response.success(
        msg="文件已删除" if result.deleted else "文件不存在",
        data=result
    )
