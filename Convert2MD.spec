# -*- mode: python ; coding: utf-8 -*-
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
ICON_PATH = os.path.join(current_dir, 'icons', 'markdown.png') if os.path.exists(os.path.join(current_dir, 'icons', 'markdown.png')) else None

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
    ['Convert2MD.py'],
    pathex=[],
    binaries=unique_bins,
    datas=[
        # Include project directories
        ('gui', 'gui'),
        ('function', 'function'),
        ('function/converters', 'function/converters'),
        ('function/utils', 'function/utils'),
        ('icons', 'icons'),
        # 配置文件支持：动态包含配置文件
    ] + all_datas + ([(os.path.join(current_dir, 'config.json'), '.')] if os.path.exists(os.path.join(current_dir, 'config.json')) else []),
    hiddenimports=[
        # 项目模块
        'function.core',
        'function.converter',
        'function.converters.pdf_converter',
        'function.converters.docx_converter',
        'function.converters.txt_converter',
        'function.utils.file_helper',
        'function.logger',
        'function.config',
        'gui.main_window',
        # 第三方库依赖
        'PyPDF2',
        'docx',
        'pathlib',
        'typing',
        'os',
        're',
        'json',
        'sys',
    ] + all_hiddenimports,
    hookspath=[],
    hooksconfig={},
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
    name='Convert2MD',
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
    name='Convert2MD',  # Final folder name that will be generated
)
