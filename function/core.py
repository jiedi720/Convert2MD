#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 格式转换工具 - 核心调度模块
Author: Your Name
Date: 2026-01-22
Description: 核心转换逻辑调度，协调各个转换器的工作
"""

import os
from pathlib import Path
from typing import List, Dict, Any




def convert_single_file(file_path: str, output_dir: str = None) -> bool:
    """
    转换单个文件为 Markdown 格式
    :param file_path: 输入文件路径
    :param output_dir: 输出目录，默认为输入文件所在目录
    :return: 转换是否成功
    """
    try:
        # 如果没有指定输出目录，则使用输入文件所在目录
        if output_dir is None:
            output_dir = os.path.dirname(file_path)

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 构建输出文件的完整路径
        from pathlib import Path
        input_filename = Path(file_path).stem  # 获取不带扩展名的文件名
        output_file_path = os.path.join(output_dir, f"{input_filename}.md")

        # 使用转换器工厂创建适当的转换器
        from .converter import ConverterFactory
        converter = ConverterFactory.create_converter(file_path, output_file_path)

        # 执行转换
        return converter.convert()

    except ImportError as e:
        from .logger import app_logger
        app_logger.error(f"导入转换器失败: {e}")
        return False
    except Exception as e:
        from .logger import app_logger
        app_logger.error(f"转换文件时出错 {file_path}: {e}")
        return False


def batch_convert(file_list: List[str], output_dir: str = None) -> Dict[str, Any]:
    """
    批量转换文件
    :param file_list: 文件路径列表
    :param output_dir: 输出目录
    :return: 转换结果统计
    """
    from .logger import app_logger
    from .utils.file_helper import get_file_type

    results = {
        'success': [],
        'failed': [],
        'skipped': [],
        'total': len(file_list),
        'errors': {}  # 存储失败文件的详细错误信息
    }

    for file_path in file_list:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            error_msg = f"文件不存在: {file_path}"
            app_logger.error(error_msg)
            results['failed'].append(file_path)
            results['errors'][file_path] = error_msg
            continue

        # 检查文件类型是否支持
        file_type = get_file_type(file_path)
        if file_type == 'unknown':
            error_msg = f"不支持的文件格式: {file_path}"
            app_logger.warning(error_msg)
            results['skipped'].append(file_path)
            results['errors'][file_path] = error_msg
            continue

        # 执行转换
        try:
            success = convert_single_file(file_path, output_dir)

            if success:
                app_logger.info(f"转换成功: {file_path}")
                results['success'].append(file_path)
            else:
                error_msg = f"转换失败: {file_path} (未知错误)"
                app_logger.error(error_msg)
                results['failed'].append(file_path)
                results['errors'][file_path] = error_msg
        except Exception as e:
            error_msg = f"转换失败: {file_path} - {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            results['failed'].append(file_path)
            results['errors'][file_path] = error_msg

    return results


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
    file_size = os.path.getsize(file_path)
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        return False
        
    return True


if __name__ == "__main__":
    # 测试代码
    from .utils.file_helper import get_file_type
    print("核心调度模块测试")
    print(get_file_type("test.pdf"))
    print(get_file_type("document.docx"))
    print(get_file_type("notes.txt"))