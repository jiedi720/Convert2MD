#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志记录模块
Author: Your Name
Date: 2026-01-22
Description: 提供应用的日志记录功能
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = 'Convert2MD', log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    :param name: 日志记录器名称
    :param log_file: 日志文件路径，如果为None则使用默认路径
    :param level: 日志级别
    :return: 配置好的日志记录器
    """
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器到logger
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，则添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # 默认日志文件位置
        default_log_dir = Path('./logs')
        default_log_dir.mkdir(exist_ok=True)
        default_log_file = default_log_dir / f"convert2md_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(default_log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_log_file_path() -> str:
    """
    获取当前日志文件路径
    :return: 日志文件路径
    """
    default_log_dir = Path('./logs')
    default_log_dir.mkdir(exist_ok=True)
    log_file = default_log_dir / f"convert2md_{datetime.now().strftime('%Y%m%d')}.log"
    return str(log_file)


# 创建全局日志记录器实例
app_logger = setup_logger()


if __name__ == "__main__":
    # 测试日志功能
    logger = setup_logger()
    logger.info("日志系统测试")
    logger.warning("这是一个警告")
    logger.error("这是一个错误")