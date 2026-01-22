#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TXT 到 Markdown 转换器
Author: Your Name
Date: 2026-01-22
Description: 将纯文本文件转换为 Markdown 格式
"""

from pathlib import Path
import os
import re
from typing import Dict, Any
from ..logger import app_logger


def convert_txt_to_md(txt_path: str, output_dir: str = None) -> bool:
    """
    将 TXT 文件转换为 Markdown 格式
    :param txt_path: TXT 文件路径
    :param output_dir: 输出目录，默认为 TXT 文件所在目录
    :return: 转换是否成功
    """
    try:
        # 确定输出目录
        if output_dir is None:
            output_dir = os.path.dirname(txt_path)

        # 生成输出文件名
        txt_filename = Path(txt_path).stem
        output_path = os.path.join(output_dir, f"{txt_filename}.md")

        # 读取 TXT 文件
        with open(txt_path, 'r', encoding='utf-8') as txt_file:
            content = txt_file.read()

        # 转换为 Markdown 格式
        md_content = convert_text_to_markdown(content)

        # 写入 Markdown 文件
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(md_content)

        app_logger.info(f"TXT 转换成功: {txt_path} -> {output_path}")
        return True

    except Exception as e:
        app_logger.error(f"TXT 转换失败 {txt_path}: {e}")
        return False


def convert_text_to_markdown(text: str) -> str:
    """
    将纯文本内容转换为 Markdown 格式
    :param text: 纯文本内容
    :return: Markdown 格式文本
    """
    lines = text.split('\n')

    # 第一步：提取目录结构
    outline_titles = extract_outline_from_text(lines)

    # 创建标题集合，用于快速查找
    title_set = {t['text']: t['level'] for t in outline_titles}

    # 第二步：转换文本
    md_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            md_lines.append('')
            i += 1
            continue

        # 检查是否为标题（以 # 开头的行视为已格式化的 Markdown 标题）
        if line.startswith('#'):
            md_lines.append(line)
            i += 1
            continue

        # 检查是否为目录中的标题
        if line in title_set:
            level = title_set[line]
            md_lines.append('#' * level + ' ' + line)
            i += 1
            continue

        # 检查是否为列表项
        if is_list_item(line):
            md_lines.append(format_list_item(line))
            # 检查后续行是否也是列表项
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    break
                if is_list_item(next_line):
                    md_lines.append(format_list_item(next_line))
                    i += 1
                else:
                    break
            continue

        # 检查是否为引用
        if line.startswith('>'):
            md_lines.append(line)
            i += 1
            continue

        # 检查是否为代码块
        if line.startswith('    ') or line.startswith('\t'):
            md_lines.append('```')
            md_lines.append(line.strip())  # 添加第一行代码
            # 查找所有连续的缩进行
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip() == '' or (not next_line.startswith('    ') and not next_line.startswith('\t')):
                    break
                md_lines.append(next_line.strip())
                i += 1
            md_lines.append('```')
            continue

        # 普通段落
        md_lines.append(line)
        i += 1

    # 优化段落合并逻辑，保留原有换行结构
    final_lines = []
    paragraph = []

    for line in md_lines:
        if line.startswith(('#', '*', '-', '+', '>', '```', '1.', '2.', '3.')):
            # 如果当前有累积的段落，先保存
            if paragraph:
                # 将段落作为一个整体，用空格连接
                final_lines.append(' '.join(paragraph))
                paragraph = []
            # 添加特殊格式行
            final_lines.append(line)
        elif line == '':
            # 空行表示段落结束或分隔
            if paragraph:
                # 将当前段落作为一个整体
                final_lines.append(' '.join(paragraph))
                paragraph = []
            final_lines.append(line)  # 保留原始空行
        else:
            # 普通文本行，加入当前段落
            paragraph.append(line)

    # 处理最后的段落
    if paragraph:
        final_lines.append(' '.join(paragraph))

    return '\n'.join(final_lines)


def extract_outline_from_text(lines: list) -> list:
    """
    从文本中提取目录结构
    :param lines: 文本行列表
    :return: 目录标题列表，包含标题文本和层级
    """
    outline_titles = []
    outline_pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+(.+)$')
    outline_end_pattern = re.compile(r'^\d+\s+Overview|^Contents|^Table of Contents', re.IGNORECASE)

    in_outline_section = False
    outline_end_found = False

    for line in lines:
        stripped = line.strip()

        # 检测目录开始
        if not in_outline_section and not outline_end_found:
            if outline_end_pattern.match(stripped):
                in_outline_section = True
                continue

        # 检测目录结束
        if in_outline_section and not outline_end_found:
            if outline_end_pattern.match(stripped):
                outline_end_found = True
                in_outline_section = False
                continue

        # 提取目录项
        if in_outline_section and not outline_end_found:
            match = outline_pattern.match(stripped)
            if match:
                number_str = match.group(1)
                title_text = match.group(2)

                # 计算层级（根据数字的点数）
                level = number_str.count('.') + 1

                outline_titles.append({
                    'text': title_text.strip(),
                    'level': level
                })

            # 检测目录结束（遇到非目录格式的行）
            elif stripped and not outline_pattern.match(stripped):
                # 如果连续多行都不是目录格式，认为目录结束
                outline_end_found = True
                in_outline_section = False

    return outline_titles


def is_heading_line(line: str) -> bool:
        """
        判断是否为标题行
        :param line: 文本行
        :return: 是否为标题
        """
        stripped = line.strip()

        # 检查是否为全大写的短行（可能是标题）
        if len(stripped) < 100 and stripped.isupper() and not stripped.isdigit():
            return True

        # 检查是否以数字+句点开头（如 "1. 标题"）
        if re.match(r'^\d+\.\s+', stripped):
            return True

        # 检查是否为特殊格式的标题（如 "=== 标题 ===" 或 "--- 标题 ---"）
        if re.match(r'^={3,}\s.*\s={3,}$', stripped) or re.match(r'^-{3,}\s.*\s-{3,}$', stripped):
            return True

        return False

def determine_heading_level(line: str) -> int:
    """
    确定标题级别
    :param line: 标题行
    :return: 标题级别 (1-6)
    """
    stripped = line.strip()

    # 检查是否为特殊格式的标题
    if re.match(r'^={3,}\s.*\s={3,}$', stripped):
        return 1
    elif re.match(r'^-{3,}\s.*\s-{3,}$', stripped):
        return 2

    # 检查是否以数字+句点开头
    match = re.match(r'^(\d+)\.\s+', stripped)
    if match:
        num = int(match.group(1))
        return min(num, 6)  # 最多6级标题

    # 默认为二级标题
    return 2


def is_list_item(line: str) -> bool:
    """
    判断是否为列表项
    :param line: 文本行
    :return: 是否为列表项
    """
    stripped = line.strip()

    # 检查是否为无序列表 (*, -, +)
    if re.match(r'^[\*\-\+]\s+', stripped):
        return True

    # 检查是否为有序列表 (数字.)
    if re.match(r'^\d+\.\s+', stripped):
        return True

    return False


def format_list_item(line: str) -> str:
    """
    格式化列表项
    :param line: 列表项文本
    :return: 格式化后的列表项
    """
    stripped = line.strip()

    # 保持原有的列表格式
    return stripped


class TxtConverter:
    """
    TXT 转换器实现类
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

            # 读取 TXT 文件
            with open(self.input_path, 'r', encoding='utf-8') as txt_file:
                content = txt_file.read()

            # 转换为 Markdown 格式
            md_content = convert_text_to_markdown(content)

# 写入 Markdown 文件
            with open(self.output_path, 'w', encoding='utf-8') as md_file:
                md_file.write(md_content)

            app_logger.info(f"TXT 转换成功: {self.input_path} -> {self.output_path}")
            return True

        except Exception as e:
            app_logger.error(f"TXT 转换失败 {self.input_path}: {e}")
            return False

    def extract_metadata(self) -> Dict[str, Any]:
        """
        提取文档元数据
        :return: 包含元数据的字典
        """
        # TXT 文件通常没有元数据，返回基本文件信息
        try:
            stat = self.input_path.stat()
            return {
                'filename': self.input_path.name,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'title': self.input_path.stem
            }
        except Exception as e:
            app_logger.error(f"提取 TXT 元数据失败 {self.input_path}: {e}")
            return {}

    def extract_structure(self) -> Dict[str, Any]:
        """
        提取文档结构信息
        :return: 包含结构信息的字典
        """
        try:
            with open(self.input_path, 'r', encoding='utf-8') as txt_file:
                content = txt_file.read()

            # 分析文本结构
            lines = content.split('\n')
            structure = {
                'title': self.input_path.stem,
                'line_count': len(lines),
                'char_count': len(content),
                'word_count': len(content.split()),
                'paragraphs': [],
                'headings': [],
                'lists': [],
                'has_tables': False,
                'has_code_blocks': False
            }

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                # 检测标题
                if stripped.startswith('#'):
                    structure['headings'].append(stripped)
                # 检测列表
                elif is_list_item(stripped):
                    structure['lists'].append(stripped)
                # 检测代码块
                elif stripped.startswith('```'):
                    structure['has_code_blocks'] = True
                # 检测普通段落
                else:
                    structure['paragraphs'].append(stripped)

            return structure

        except Exception as e:
            app_logger.error(f"提取 TXT 结构失败 {self.input_path}: {e}")
            return {}


if __name__ == "__main__":
    # 测试代码
    app_logger.info("TXT 转换器测试")
    sample_text = """
这是第一段文本。
它包含多行内容。

# 这是一个标题

- 这是一个列表项
- 这是另一个列表项

1. 有序列表第一项
2. 有序列表第二项

    代码块示例
    第二行代码
    """

    result = convert_text_to_markdown(sample_text)
    print(result)