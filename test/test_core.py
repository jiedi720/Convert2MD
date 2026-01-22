#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试文件
Author: Your Name
Date: 2026-01-22
Description: 测试核心模块的功能
"""

import unittest
import tempfile
import os
from pathlib import Path


class TestCoreFunctions(unittest.TestCase):
    """测试核心功能"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        
    def test_get_file_type(self):
        """测试文件类型识别功能"""
        from function.utils.file_helper import get_file_type

        self.assertEqual(get_file_type("test.pdf"), "pdf")
        self.assertEqual(get_file_type("document.docx"), "docx")
        self.assertEqual(get_file_type("notes.txt"), "txt")
        self.assertEqual(get_file_type("image.jpg"), "unknown")
        self.assertEqual(get_file_type("data.csv"), "unknown")
        
    def test_validate_file(self):
        """测试文件验证功能"""
        from function.utils.file_helper import validate_file

        # 创建一个临时文件用于测试
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Test content")

        # 验证存在的文件
        self.assertTrue(validate_file(test_file))

        # 验证不存在的文件
        self.assertFalse(validate_file(os.path.join(self.temp_dir, "nonexistent.txt")))
        
    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        import shutil
        shutil.rmtree(self.temp_dir)


class TestConverters(unittest.TestCase):
    """测试转换器功能"""
    
    def test_converter_factory(self):
        """测试转换器工厂"""
        from function.converter import ConverterFactory
        
        # 由于我们只是测试工厂类能否创建实例而不实际转换，
        # 我们只检查是否会抛出异常
        with self.assertRaises(FileNotFoundError):
            # 使用不存在的文件测试，这会引发 FileNotFoundError
            converter = ConverterFactory.create_converter("nonexistent.pdf")
        
        with self.assertRaises(FileNotFoundError):
            converter = ConverterFactory.create_converter("nonexistent.docx")
            
        with self.assertRaises(FileNotFoundError):
            converter = ConverterFactory.create_converter("nonexistent.txt")


class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_file_helper_functions(self):
        """测试文件辅助函数"""
        from function.utils.file_helper import get_file_type, validate_file, sanitize_filename
        
        # 测试文件类型识别
        self.assertEqual(get_file_type("test.pdf"), "pdf")
        self.assertEqual(get_file_type("document.docx"), "docx")
        self.assertEqual(get_file_type("notes.txt"), "txt")
        self.assertEqual(get_file_type("image.jpg"), "unknown")
        
        # 测试文件名清理
        self.assertEqual(sanitize_filename('test<>.txt'), 'test__.txt')
        self.assertEqual(sanitize_filename('a' * 250 + '.txt'), 'a' * (200-4) + '.txt')  # 长文件名测试


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)