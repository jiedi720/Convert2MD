#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 到 Markdown 转换器
Author: Your Name
Date: 2026-01-22
Description: 将 PDF 文件转换为 Markdown 格式
"""

import PyPDF2
import os
from pathlib import Path
from typing import Dict, Any
from ..logger import app_logger


def convert_pdf_to_md(pdf_path: str, output_dir: str = None) -> bool:
    """
    将 PDF 文件转换为 Markdown 格式
    :param pdf_path: PDF 文件路径
    :param output_dir: 输出目录，默认为 PDF 文件所在目录
    :return: 转换是否成功
    """
    try:
        # 确定输出目录
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)

        # 生成输出文件名
        pdf_filename = Path(pdf_path).stem
        output_path = os.path.join(output_dir, f"{pdf_filename}.md")

        # 读取 PDF 文件
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # 提取目录中的标题
            outline_titles = []
            if pdf_reader.outline:
                outline_titles = extract_outline_titles(pdf_reader.outline)

            # 提取所有文本内容
            all_text = []
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text:
                    all_text.append(text)

            # 合并所有文本
            full_text = '\n'.join(all_text)

            # 转换为 Markdown 格式
            md_content = convert_text_to_markdown(full_text, outline_titles)

        # 写入 Markdown 文件
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(md_content)

        app_logger.info(f"PDF 转换成功: {pdf_path} -> {output_path}")
        return True

    except Exception as e:
        app_logger.error(f"PDF 转换失败 {pdf_path}: {e}")
        return False


def extract_outline_titles(outline, level=0):
    """
    从 PDF 目录中提取标题
    :param outline: PDF 目录对象
    :param level: 当前层级
    :return: 标题列表，包含标题文本和层级
    """
    titles = []
    if outline is None:
        return titles

    for item in outline:
        if isinstance(item, list):
            # 递归处理子目录
            titles.extend(extract_outline_titles(item, level + 1))
        else:
            # 提取标题文本
            title = item.title
            if title:
                titles.append({
                    'text': title.strip(),
                    'level': level + 1
                })

    return titles


def convert_text_to_markdown(text: str, outline_titles: list) -> str:
    """
    将文本转换为 Markdown 格式，根据目录中的标题识别标题
    :param text: 原始文本
    :param outline_titles: 目录中的标题列表
    :return: Markdown 格式文本
    """
    # 创建标题集合，用于快速查找
    title_set = {t['text']: t['level'] for t in outline_titles}

    # 按段落分割文本
    paragraphs = text.split('\n')

    md_lines = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # 检查是否是目录中的标题
        if para in title_set:
            level = title_set[para]
            md_lines.append(f"{'#' * level} {para}\n")
        else:
            # 普通段落
            md_lines.append(f"{para}\n")

    return '\n'.join(md_lines)


def extract_text_and_structure(pdf_path: str) -> dict:
    """
    提取 PDF 的文本和结构信息
    :param pdf_path: PDF 文件路径
    :return: 包含文本和结构信息的字典
    """
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            content = {
                'title': '',
                'paragraphs': [],
                'lists': [],
                'metadata': {}
            }

            # 提取元数据
            if pdf_reader.metadata:
                metadata = pdf_reader.metadata
                content['metadata'] = {
                    'title': getattr(metadata, 'title', ''),
                    'author': getattr(metadata, 'author', ''),
                    'subject': getattr(metadata, 'subject', ''),
                    'creator': getattr(metadata, 'creator', ''),
                }

                # 如果没有标题，尝试从元数据获取
                if not content['title']:
                    content['title'] = content['metadata']['title']

            # 提取页面内容
            for page in pdf_reader.pages:
                text = page.extract_text()

                # 分割段落
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        content['paragraphs'].append(para)

        return content

    except Exception as e:
        app_logger.error(f"提取 PDF 结构失败 {pdf_path}: {e}")
        return {}


class PDFConverter:
    """
    PDF 转换器实现类
    """

    def __init__(self, input_path: str, output_path: str = None):
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

    def _generate_output_path(self):
        """
        生成输出文件路径
        :return: 输出文件路径
        """
        input_stem = self.input_path.stem
        output_dir = self.input_path.parent
        return output_dir / f"{input_stem}.md"

    def convert(self) -> bool:
        """
        执行转换操作
        :return: 转换是否成功
        """
        try:
            # 确保输出目录存在
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # 读取 PDF 文件
            with open(self.input_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                # 提取目录中的标题
                outline_titles = []
                if pdf_reader.outline:
                    outline_titles = extract_outline_titles(pdf_reader.outline)

                # 提取所有文本内容
                all_text = []
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text:
                        all_text.append(text)

                # 合并所有文本
                full_text = '\n'.join(all_text)

                # 转换为 Markdown 格式
                md_content = convert_text_to_markdown(full_text, outline_titles)

            # 写入 Markdown 文件
            with open(self.output_path, 'w', encoding='utf-8') as md_file:
                md_file.write(md_content)

            app_logger.info(f"PDF 转换成功: {self.input_path} -> {self.output_path}")
            return True

        except Exception as e:
            app_logger.error(f"PDF 转换失败 {self.input_path}: {e}")
            return False

    def extract_metadata(self) -> Dict[str, Any]:
        """
        提取文档元数据
        :return: 包含元数据的字典
        """
        try:
            with open(self.input_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                # 提取元数据
                if pdf_reader.metadata:
                    metadata = pdf_reader.metadata
                    return {
                        'title': getattr(metadata, 'title', ''),
                        'author': getattr(metadata, 'author', ''),
                        'subject': getattr(metadata, 'subject', ''),
                        'creator': getattr(metadata, 'creator', ''),
                        'producer': getattr(metadata, 'producer', ''),
                    }

            return {}

        except Exception as e:
            app_logger.error(f"提取 PDF 元数据失败 {self.input_path}: {e}")
            return {}

    def extract_structure(self) -> Dict[str, Any]:
        """
        提取文档结构信息
        :return: 包含结构信息的字典
        """
        try:
            with open(self.input_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                content = {
                    'title': '',
                    'paragraphs': [],
                    'lists': [],
                    'metadata': {},
                    'page_count': len(pdf_reader.pages)
                }

                # 提取元数据
                if pdf_reader.metadata:
                    metadata = pdf_reader.metadata
                    content['metadata'] = {
                        'title': getattr(metadata, 'title', ''),
                        'author': getattr(metadata, 'author', ''),
                        'subject': getattr(metadata, 'subject', ''),
                        'creator': getattr(metadata, 'creator', ''),
                    }

                    # 如果没有标题，尝试从元数据获取
                    if not content['title']:
                        content['title'] = content['metadata']['title']

                # 提取页面内容
                for page in pdf_reader.pages:
                    text = page.extract_text()

                    # 分割段落
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            content['paragraphs'].append(para)

            return content

        except Exception as e:
            app_logger.error(f"提取 PDF 结构失败 {self.input_path}: {e}")
            return {}


if __name__ == "__main__":
    # 测试代码
    app_logger.info("PDF 转换器测试")