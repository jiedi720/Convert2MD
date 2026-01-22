#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件辅助工具
Author: Your Name
Date: 2026-01-22
Description: 提供文件相关的辅助功能
"""

import os
from pathlib import Path
from typing import List, Tuple


def get_file_type(file_path: str) -> str:
    """
    根据文件扩展名判断文件类型
    :param file_path: 文件路径
    :return: 文件类型 ('pdf', 'docx', 'txt', 'unknown')
    """
    extension = Path(file_path).suffix.lower()
    if extension == '.pdf':
        return 'pdf'
    elif extension == '.docx':
        return 'docx'
    elif extension == '.txt':
        return 'txt'
    else:
        return 'unknown'


def validate_file(file_path: str) -> bool:
    """
    验证文件是否有效
    :param file_path: 文件路径
    :return: 文件是否有效
    """
    if not os.path.exists(file_path):
        return False
    
    if not os.path.isfile(file_path):
        return False
        
    # 检查文件大小（防止过大文件）
    try:
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            return False
    except OSError:
        return False
        
    return True


def get_supported_files(directory: str, recursive: bool = False) -> List[str]:
    """
    获取目录中所有支持的文档文件
    :param directory: 目录路径
    :param recursive: 是否递归搜索子目录
    :return: 支持的文件路径列表
    """
    supported_extensions = {'.pdf', '.docx', '.txt'}
    files = []
    
    if recursive:
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if Path(filename).suffix.lower() in supported_extensions:
                    files.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and Path(filename).suffix.lower() in supported_extensions:
                files.append(filepath)
                
    return files


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符
    :param filename: 原始文件名
    :return: 清理后的文件名
    """
    # 移除或替换不安全字符
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # 限制文件名长度
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
        
    return filename


def ensure_directory_exists(path: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    :param path: 目录路径
    :return: 是否成功
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def get_unique_filepath(base_path: str, extension: str) -> str:
    """
    获取唯一的文件路径（如果文件已存在则添加数字后缀）
    :param base_path: 基础路径（不含扩展名）
    :param extension: 文件扩展名
    :return: 唯一的文件路径
    """
    full_path = f"{base_path}.{extension}"
    counter = 1
    
    while os.path.exists(full_path):
        full_path = f"{base_path}_{counter}.{extension}"
        counter += 1
        
    return full_path


if __name__ == "__main__":
    # 测试代码
    print("文件辅助工具测试")
    print(get_file_type("test.pdf"))
    print(get_file_type("document.docx"))
    print(get_file_type("notes.txt"))
    print(get_file_type("image.jpg"))