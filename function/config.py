#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件管理模块
Author: Your Name
Date: 2026-01-22
Description: 处理应用程序的配置文件读取和写入
"""

import json
import os
import configparser
from pathlib import Path


class ConfigManager:
    """
    配置管理器
    """
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        :param config_file: 配置文件路径，默认为程序目录下的 config.json
        """
        if config_file is None:
            # 默认配置文件路径为程序所在目录下的 config.json
            import sys
            # 优先使用 _MEIPASS（打包环境），其次使用 sys.executable，最后使用 sys.argv[0]
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller 打包后的环境
                program_dir = Path(sys._MEIPASS)
            elif getattr(sys, 'frozen', False):
                # 其他打包方式（如 cx_Freeze）
                program_dir = Path(sys.executable).parent
            elif sys.argv[0]:
                # 开发环境
                program_dir = Path(sys.argv[0]).parent
            else:
                # 兜底方案
                program_dir = Path.cwd()

            self.config_file = program_dir / "config.json"
            # .ini 配置文件用于保存目录配置
            self.ini_file = program_dir / "Convert2MD.ini"
        else:
            self.config_file = Path(config_file)
            self.ini_file = Path(config_file).parent / "Convert2MD.ini"

        # 默认配置
        self.default_config = {
            "output_directory": "",  # 空字符串表示使用原始文件目录
            "overwrite_existing": False,
            "auto_open_output": False,
            "last_used_directory": "",
            "supported_formats": [".pdf", ".docx", ".txt"],
            "theme": "light",
            "conversion_history": []  # 转换历史记录
        }

        # 加载现有配置或创建默认配置
        self.config = self.load_config()
        # 加载 .ini 配置
        self.ini_config = self.load_ini_config()
    
    def load_config(self):
        """
        从文件加载配置
        :return: 配置字典
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 确保所有默认键都存在
                    for key, value in self.default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
                return self.default_config.copy()
        else:
            # 如果配置文件不存在，创建默认配置
            self.save_config(self.default_config)
            return self.default_config.copy()

    def load_ini_config(self):
        """
        从 .ini 文件加载配置
        :return: ConfigParser 对象
        """
        ini_config = configparser.ConfigParser()

        if self.ini_file.exists():
            try:
                ini_config.read(self.ini_file, encoding='utf-8')
            except Exception as e:
                print(f"加载 .ini 配置文件失败: {e}")
        else:
            # 创建默认的 .ini 配置
            ini_config['Directories'] = {
                'input_directory': '',
                'output_directory': ''  # 空字符串表示使用原始文件目录
            }
            ini_config['Settings'] = {
                'overwrite_existing': 'False',
                'auto_open_output': 'False',
                'theme': 'light'
            }
            ini_config['History'] = {
                'conversion_history': ''  # JSON 字符串
            }
            self.save_ini_config(ini_config)

        return ini_config

    def save_ini_config(self, ini_config=None):
        """
        保存配置到 .ini 文件
        :param ini_config: ConfigParser 对象，默认使用当前的 ini_config
        """
        if ini_config is None:
            ini_config = self.ini_config

        try:
            # 确保配置文件的目录存在
            self.ini_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.ini_file, 'w', encoding='utf-8') as f:
                ini_config.write(f)
        except Exception as e:
            print(f"保存 .ini 配置文件失败: {e}")

    def save_config(self, config: dict = None):
        """
        保存配置到文件
        :param config: 要保存的配置字典，默认使用当前配置
        """
        if config is None:
            config = self.config

        try:
            # 确保配置文件的目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default=None):
        """
        获取配置值
        :param key: 配置键
        :param default: 默认值
        :return: 配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """
        设置配置值
        :param key: 配置键
        :param value: 配置值
        """
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: dict):
        """
        批量更新配置
        :param updates: 更新的配置字典
        """
        self.config.update(updates)
        self.save_config()

    def get_input_directory(self):
        """
        获取输入目录
        :return: 输入目录路径
        """
        if 'Directories' in self.ini_config and 'input_directory' in self.ini_config['Directories']:
            return self.ini_config['Directories']['input_directory']
        return ''

    def set_input_directory(self, directory: str):
        """
        设置输入目录
        :param directory: 输入目录路径
        """
        if 'Directories' not in self.ini_config:
            self.ini_config['Directories'] = {}
        self.ini_config['Directories']['input_directory'] = directory
        self.save_ini_config()

    def get_output_directory(self):
        """
        获取输出目录
        :return: 输出目录路径，空字符串表示使用原始文件目录
        """
        if 'Directories' in self.ini_config and 'output_directory' in self.ini_config['Directories']:
            return self.ini_config['Directories']['output_directory']
        return ''  # 返回空字符串，表示使用原始文件目录

    def set_output_directory(self, directory: str):
        """
        设置输出目录
        :param directory: 输出目录路径
        """
        if 'Directories' not in self.ini_config:
            self.ini_config['Directories'] = {}
        self.ini_config['Directories']['output_directory'] = directory
        self.save_ini_config()

    def get_conversion_history(self):
        """
        获取转换历史记录
        :return: 历史记录列表
        """
        import json
        if 'History' in self.ini_config and 'conversion_history' in self.ini_config['History']:
            history_str = self.ini_config['History']['conversion_history']
            if history_str:
                try:
                    return json.loads(history_str)
                except:
                    return []
        return []

    def set_conversion_history(self, history: list):
        """
        设置转换历史记录
        :param history: 历史记录列表
        """
        import json
        if 'History' not in self.ini_config:
            self.ini_config['History'] = {}
        self.ini_config['History']['conversion_history'] = json.dumps(history, ensure_ascii=False)
        self.save_ini_config()

    def get_setting(self, key: str, default=None):
        """
        获取设置值
        :param key: 设置键
        :param default: 默认值
        :return: 设置值
        """
        if 'Settings' in self.ini_config and key in self.ini_config['Settings']:
            value = self.ini_config['Settings'][key]
            # 转换布尔值
            if value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False
            return value
        return default

    def set_setting(self, key: str, value):
        """
        设置设置值
        :param key: 设置键
        :param value: 设置值
        """
        if 'Settings' not in self.ini_config:
            self.ini_config['Settings'] = {}
        # 转换布尔值
        if isinstance(value, bool):
            value = str(value)
        self.ini_config['Settings'][key] = value
        self.save_ini_config()


# 全局配置实例
config_manager = ConfigManager()


def get_config_value(key: str, default=None):
    """
    获取配置值的便捷函数
    :param key: 配置键
    :param default: 默认值
    :return: 配置值
    """
    return config_manager.get(key, default)


def set_config_value(key: str, value):
    """
    设置配置值的便捷函数
    :param key: 配置键
    :param value: 配置值
    """
    config_manager.set(key, value)


def add_conversion_history(file_list: list, results: dict):
    """
    添加转换历史记录
    :param file_list: 转换的文件列表
    :param results: 转换结果
    """
    import datetime

    history = config_manager.get_conversion_history()

    # 创建历史记录条目
    history_entry = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': len(file_list),
        'success_count': len(results.get('success', [])),
        'failed_count': len(results.get('failed', [])),
        'skipped_count': len(results.get('skipped', [])),
        'files': file_list
    }

    # 添加到历史记录（最多保留100条）
    history.insert(0, history_entry)
    if len(history) > 100:
        history = history[:100]

    # 保存
    config_manager.set_conversion_history(history)


def get_conversion_history():
    """
    获取转换历史记录
    :return: 历史记录列表
    """
    return config_manager.get_conversion_history()


def clear_conversion_history():
    """
    清空转换历史记录
    """
    config_manager.set_conversion_history([])


def get_input_directory():
    """
    获取输入目录的便捷函数
    :return: 输入目录路径
    """
    return config_manager.get_input_directory()


def set_input_directory(directory: str):
    """
    设置输入目录的便捷函数
    :param directory: 输入目录路径
    """
    config_manager.set_input_directory(directory)


def get_output_directory():
    """
    获取输出目录的便捷函数（优先从 .ini 文件读取）
    :return: 输出目录路径
    """
    return config_manager.get_output_directory()


def set_output_directory(directory: str):
    """
    设置输出目录的便捷函数
    :param directory: 输出目录路径
    """
    config_manager.set_output_directory(directory)


if __name__ == "__main__":
    # 测试配置管理器
    print("配置管理器测试")
    print(f"输出目录: {get_config_value('output_directory')}")
    print(f"支持的格式: {get_config_value('supported_formats')}")
    print(f"输入目录: {get_input_directory()}")
    print(f"输出目录 (.ini): {get_output_directory()}")