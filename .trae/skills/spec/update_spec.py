#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec 文件重写工具
根据参考 .spec 文件的配置逻辑，重写项目的 .spec 文件
确保生成的 .exe 文件标题栏正常显示图标，且程序运行后能准确识别并读取同级目录下的配置文件
适用于任何需要 PyInstaller 打包的 Python 项目
"""

import os
import sys
import argparse

def main():
    """
    主函数，处理命令行参数并更新 spec 文件
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Spec 文件重写工具')
    parser.add_argument('main_script', nargs='?', default=None, help='主入口脚本文件（如：main.py）')
    parser.add_argument('--name', '-n', help='生成的可执行文件名称')
    parser.add_argument('--icon', '-i', help='图标文件路径')
    parser.add_argument('--output', '-o', help='输出 spec 文件路径')
    args = parser.parse_args()
    
    # 获取当前目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 回到项目根目录
    project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
    
    # 自动检测主入口文件
    if not args.main_script:
        args.main_script = detect_main_script(project_root)
    
    # 自动检测可执行文件名称
    if not args.name:
        args.name = os.path.splitext(os.path.basename(args.main_script))[0]
    
    # 自动检测图标文件
    if not args.icon:
        args.icon = detect_icon_file(project_root)
    
    # 自动检测输出 spec 文件路径
    if not args.output:
        args.output = os.path.join(project_root, f'{args.name}.spec')
    
    # 生成新的 spec 文件内容
    spec_content = generate_spec_content(project_root, args.main_script, args.name, args.icon)
    
    # 写入到输出文件
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"[SUCCESS] 已成功生成 {args.output}")
    print("[INFO] 生成的配置文件包含以下特性：")
    print(f"   - 主入口文件：{args.main_script}")
    print(f"   - 可执行文件名称：{args.name}")
    print(f"   - 图标配置：{args.icon if args.icon else '未指定，使用默认配置'}")
    print("   - 配置文件支持：程序运行时能识别同级目录下的配置文件")
    print("   - 依赖管理：自动收集所有必要的依赖模块")
    print("   - 打包优化：使用 UPX 压缩可执行文件，排除不必要的模块")

def detect_main_script(project_root):
    """
    自动检测项目的主入口文件
    
    Args:
        project_root: 项目根目录路径
    
    Returns:
        检测到的主入口文件路径
    """
    # 常见的主入口文件名称
    main_script_names = ['main.py', 'app.py', 'run.py', 'start.py']
    
    # 检查根目录下的文件
    for script_name in main_script_names:
        script_path = os.path.join(project_root, script_name)
        if os.path.exists(script_path):
            return script_name
    
    # 检查是否有与目录同名的 .py 文件
    project_name = os.path.basename(project_root)
    project_script = os.path.join(project_root, f'{project_name}.py')
    if os.path.exists(project_script):
        return f'{project_name}.py'
    
    # 如果都没有找到，返回第一个 .py 文件
    for file in os.listdir(project_root):
        if file.endswith('.py') and not file.startswith('_'):
            return file
    
    # 默认返回 main.py
    return 'main.py'

def detect_icon_file(project_root):
    """
    自动检测项目的图标文件
    
    Args:
        project_root: 项目根目录路径
    
    Returns:
        检测到的图标文件路径
    """
    # 检查 icons 目录
    icons_dir = os.path.join(project_root, 'icons')
    if os.path.exists(icons_dir):
        # 常见的图标文件名称
        icon_names = ['app_icon.png', 'icon.png', 'app.png', 'logo.png', 
                      'app_icon.ico', 'icon.ico', 'app.ico', 'logo.ico']
        
        for icon_name in icon_names:
            icon_path = os.path.join(icons_dir, icon_name)
            if os.path.exists(icon_path):
                return f'icons/{icon_name}'
    
    # 检查根目录
    for ext in ['.png', '.ico']:
        for icon_name in ['icon', 'app', 'logo']:
            icon_path = os.path.join(project_root, f'{icon_name}{ext}')
            if os.path.exists(icon_path):
                return f'{icon_name}{ext}'
    
    # 没有找到图标文件
    return None

def detect_project_structure(project_root):
    """
    自动检测项目结构，包括目录和模块
    
    Args:
        project_root: 项目根目录路径
    
    Returns:
        项目结构信息字典
    """
    structure = {
        'directories': [],
        'modules': [],
        'dependencies': []
    }
    
    # 检测常见目录
    common_dirs = ['gui', 'function', 'utils', 'src', 'components', 'assets']
    for dir_name in common_dirs:
        dir_path = os.path.join(project_root, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            structure['directories'].append(dir_name)
    
    # 检测依赖模块
    # 这里可以根据需要扩展，例如从 requirements.txt 中读取
    try:
        with open(os.path.join(project_root, 'requirements.txt'), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 提取包名
                    pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0]
                    structure['dependencies'].append(pkg_name)
    except FileNotFoundError:
        pass
    
    return structure

def generate_spec_content(project_root, main_script, app_name, icon_path):
    """
    生成 spec 文件内容
    
    Args:
        project_root: 项目根目录路径
        main_script: 主入口脚本文件
        app_name: 可执行文件名称
        icon_path: 图标文件路径
    
    Returns:
        生成的 spec 文件内容字符串
    """
    # 检测项目结构
    project_structure = detect_project_structure(project_root)
    
    # 构建 datas 列表
    datas = []
    for directory in project_structure['directories']:
        datas.append((directory, directory))
    # 添加配置文件支持
    datas.append(('# 配置文件支持：如果有配置文件，取消下面的注释', ''))
    datas.append(('# (\'config.ini\', \'.\'),', ''))
    
    # 构建 hiddenimports 列表
    hiddenimports = []
    # 添加常见的隐式导入
    common_imports = ['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox']
    hiddenimports.extend(common_imports)
    
    # 生成 spec 文件内容
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules, collect_all

# Get the absolute path of the current directory
# 使用 sys.argv[0] 获取 spec 文件路径，因为 __file__ 在 PyInstaller 中不可用
if hasattr(sys, '_MEIPASS'):
    # 如果是在打包后的环境中运行
    current_dir = sys._MEIPASS
else:
    # 如果是在开发环境中运行
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if len(sys.argv) > 0 else os.getcwd()

# Full path to the icon file
ICON_PATH = {f"os.path.join(current_dir, '{icon_path}')" if icon_path else "None"}

# 使用 collect_all 自动收集依赖模块
# collect_all 返回 (binaries, datas, hiddenimports)
all_binaries = []
all_datas = []
all_hiddenimports = []

# 尝试收集常见模块的依赖
try:
    tk_binaries, tk_datas, tk_hiddenimports = collect_all('tkinter')
    all_binaries.extend(tk_binaries)
    all_datas.extend(tk_datas)
    all_hiddenimports.extend(tk_hiddenimports)
except Exception:
    pass

try:
    tkdnd_binaries, tkdnd_datas, tkdnd_hiddenimports = collect_all('tkinterdnd2')
    all_binaries.extend(tkdnd_binaries)
    all_datas.extend(tkdnd_datas)
    all_hiddenimports.extend(tkdnd_hiddenimports)
except Exception:
    pass

# 去重处理：确保每个 DLL 只被打包一次
seen_binaries = set()
unique_bins = []
# PyInstaller 的 binaries 格式为 (src_path, dest_path) 或 (src_path, dest_path, kind)
for binary in all_binaries:
    # 解析 binary 格式
    if len(binary) == 3:
        src_path, dest_path, kind = binary
    else:
        src_path, dest_path = binary
        kind = None

    # 提取文件名
    file_name = os.path.basename(src_path)

    # 只对通用的 .dll 文件执行严格的文件名去重
    if file_name.endswith('.dll'):
        if file_name not in seen_binaries:
            if kind is not None:
                unique_bins.append((src_path, dest_path, kind))
            else:
                unique_bins.append((src_path, dest_path))
            seen_binaries.add(file_name)
    else:
        # 对于 .pyd 文件和其他文件，不进行去重
        if kind is not None:
            unique_bins.append((src_path, dest_path, kind))
        else:
            unique_bins.append((src_path, dest_path))

a = Analysis(
    ['{main_script}'],
    pathex=[],
    binaries=unique_bins,
    datas=[
        # Include project directories
        {',\n        '.join([f'({repr(d[0])}, {repr(d[1])})' for d in datas if d[1]])},
    ] + all_datas,
    hiddenimports=[
        # 项目模块：根据实际情况添加
        # 'module.submodule',
        # 第三方库依赖：根据实际情况添加
        # 'dependency',
    ] + all_hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'pytest',
        'unittest',
        # GUI 库相关（根据实际使用情况调整）
        'PySide6',
        'PyQt5',
        'PyQt6',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe,                # Include the EXE object defined above (main program)
    a.binaries,         # Collect all dependent DLLs/dynamic libraries
    a.datas,            # Collect all resource files (images, configs, etc.)
    strip=False,        # Whether to remove symbol table (usually False to avoid errors)
    upx=True,           # Whether to use UPX compression/obfuscation
    upx_exclude=[],     # Files to exclude from compression
    name='{app_name}',  # Final folder name that will be generated
)
'''
    return spec_content

if __name__ == "__main__":
    main()
