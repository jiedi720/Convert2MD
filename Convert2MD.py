#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 格式转换工具 - 程序入口
Author: Your Name
Date: 2026-01-22
Description: 程序的唯一启动点，初始化并启动 GUI 界面
"""

import sys
import os

# 添加 function 目录到路径，以便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'function'))

from gui.main_window import MainWindow
import tkinter as tk


def main():
    """
    程序主入口函数
    """
    try:
        # 初始化主窗口（内部会处理 TkinterDnD 的兼容性）
        app = MainWindow()

        # 启动 GUI 事件循环
        app.root.mainloop()

    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()