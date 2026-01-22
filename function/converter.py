#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换器抽象基类
Author: Your Name
Date: 2026-01-22
Description: 定义转换器的标准接口，确保所有转换器实现一致的方法
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class BaseConverter(ABC):
    """
    转换器抽象基类
    所有具体的转换器都应该继承此类并实现其方法
    """

    def __init__(self, input_path: str, output_path: Optional[str] = None):
        """
        初始化转换器
        :param input_path: 输入文件路径
        :param output_path: 输出文件路径，如果为None则自动生成
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else self._generate_output_path()

        # 验证输入文件
        if not self.input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        if not self.input_path.is_file():
            raise ValueError(f"输入路径不是文件: {input_path}")

    def _generate_output_path(self) -> Path:
        """
        生成输出文件路径
        :return: 输出文件路径
        """
        input_stem = self.input_path.stem
        output_dir = self.input_path.parent
        return output_dir / f"{input_stem}.md"

    @abstractmethod
    def convert(self) -> bool:
        """
        执行转换操作
        :return: 转换是否成功
        """
        pass

    @abstractmethod
    def extract_metadata(self) -> Dict[str, Any]:
        """
        提取文档元数据
        :return: 包含元数据的字典
        """
        pass

    @abstractmethod
    def extract_structure(self) -> Dict[str, Any]:
        """
        提取文档结构信息
        :return: 包含结构信息的字典
        """
        pass


class ConverterFactory:
    """
    转换器工厂类
    根据文件类型创建相应的转换器实例
    """

    @staticmethod
    def create_converter(file_path: str, output_path: Optional[str] = None):
        """
        创建适当的转换器实例
        :param file_path: 输入文件路径
        :param output_path: 输出文件路径
        :return: 转换器实例
        """
        from .converters.pdf_converter import PDFConverter
        from .converters.docx_converter import DocxConverter
        from .converters.txt_converter import TxtConverter

        file_extension = Path(file_path).suffix.lower()

        if file_extension == '.pdf':
            return PDFConverter(file_path, output_path)
        elif file_extension == '.docx':
            return DocxConverter(file_path, output_path)
        elif file_extension == '.txt':
            return TxtConverter(file_path, output_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")


if __name__ == "__main__":
    # 测试代码
    print("抽象基类测试")