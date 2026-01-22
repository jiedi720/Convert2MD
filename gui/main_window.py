#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 格式转换工具 - GUI 界面层
Author: Your Name
Date: 2026-01-22
Description: 主窗口定义，实现图形用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
try:
    # 尝试导入 tkinterdnd2 用于拖放功能
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKINTER_DND_AVAILABLE = True
except ImportError:
    # 如果没有安装 tkinterdnd2，则不支持拖放
    TKINTER_DND_AVAILABLE = False
    print("提示: 未安装 tkinterdnd2，拖放功能不可用。可通过 'pip install tkinterdnd2' 安装。")


class MainWindow:
    def __init__(self, root=None):
        """
        初始化主窗口
        :param root: Tkinter 根窗口，如果为 None 则创建新的
        """
        if TKINTER_DND_AVAILABLE:
            if root is None:
                self.root = TkinterDnD.Tk()
            else:
                self.root = root
            # 启用拖放功能
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        else:
            if root is None:
                self.root = tk.Tk()
            else:
                self.root = root

        # 先隐藏窗口，避免显示时的闪烁
        self.root.withdraw()

        self.conversion_cancelled = threading.Event()
        self.conversion_in_progress = False  # 标记转换是否正在进行
        self.setup_window()
        self.create_widgets()
        self.center_window()

    def on_drop(self, event):
        """
        处理文件拖放事件
        :param event: 拖放事件
        """
        # 获取拖放的文件路径
        files = self.root.tk.splitlist(event.data)
        # 过滤出支持的文件类型
        supported_extensions = {'.pdf', '.docx', '.txt'}
        supported_files = []
        for file_path in files:
            if os.path.splitext(file_path)[1].lower() in supported_extensions:
                supported_files.append(file_path)

        if supported_files:
            self.selected_files = supported_files
            self.update_file_list_display()
            self.convert_btn.config(state=tk.NORMAL)
            self.status_var.set(f"已添加 {len(supported_files)} 个文件到转换列表")
        
    def setup_window(self):
        """设置窗口基本属性"""
        self.root.title("Markdown 格式转换工具")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "markdown.png")
        if os.path.exists(icon_path):
            try:
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
            except Exception as e:
                print(f"设置图标失败: {e}")

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
    def center_window(self):
        """窗口居中加载，消除启动时的视觉闪烁"""
        # 更新窗口以获取实际尺寸
        self.root.update_idletasks()

        # 获取屏幕宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 获取窗口宽度和高度
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # 计算居中位置
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 显示窗口
        self.root.deiconify()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 文件选择区域
        selection_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        selection_frame.columnconfigure(0, weight=1)
        
        # 选择文件按钮
        self.select_file_btn = ttk.Button(
            selection_frame, 
            text="选择文件", 
            command=self.select_files
        )
        self.select_file_btn.grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        
        # 选择目录按钮
        self.select_dir_btn = ttk.Button(
            selection_frame, 
            text="选择目录", 
            command=self.select_directory
        )
        self.select_dir_btn.grid(row=0, column=1, padx=(0, 5), sticky=tk.W)
        
        # 文件列表显示区域
        list_frame = ttk.LabelFrame(main_frame, text="已选择文件", padding="5")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 创建 Treeview 显示文件列表
        columns = ('filename', 'size', 'type')
        self.file_treeview = ttk.Treeview(list_frame, columns=columns, show='headings')

        # 设置列标题
        self.file_treeview.heading('filename', text='文件名')
        self.file_treeview.heading('size', text='大小')
        self.file_treeview.heading('type', text='类型')

        # 设置列宽
        self.file_treeview.column('filename', width=300, anchor=tk.W)
        self.file_treeview.column('size', width=100, anchor=tk.E)
        self.file_treeview.column('type', width=80, anchor=tk.CENTER)

        # 创建滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_treeview.yview)
        self.file_treeview.configure(yscrollcommand=scrollbar.set)

        self.file_treeview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 配置列表框所在行和列的权重
        main_frame.rowconfigure(1, weight=1)
        
        # 控制按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        
        # 开始转换按钮
        self.convert_btn = ttk.Button(
            button_frame, 
            text="开始转换", 
            command=self.start_conversion,
            state=tk.DISABLED
        )
        self.convert_btn.grid(row=0, column=0, padx=(0, 5))
        
        # 取消转换按钮
        self.cancel_btn = ttk.Button(
            button_frame, 
            text="取消", 
            command=self.cancel_conversion,
            state=tk.DISABLED
        )
        self.cancel_btn.grid(row=0, column=1, padx=(0, 5))
        
        # 打开输出目录按钮
        self.open_output_btn = ttk.Button(
            button_frame,
            text="打开输出目录",
            command=self.open_output_directory
        )
        self.open_output_btn.grid(row=0, column=2, padx=(0, 5))

        # 设置按钮
        self.settings_btn = ttk.Button(
            button_frame,
            text="设置",
            command=self.open_settings_dialog
        )
        self.settings_btn.grid(row=0, column=3, padx=(0, 5))

        # 历史记录按钮
        self.history_btn = ttk.Button(
            button_frame,
            text="历史记录",
            command=self.open_history_dialog
        )
        self.history_btn.grid(row=0, column=4)

        # 进度条区域
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # 进度标签
        self.progress_label_var = tk.StringVar(value="0/0")
        self.progress_label = ttk.Label(
            progress_frame,
            textvariable=self.progress_label_var,
            width=15
        )
        self.progress_label.pack(side=tk.RIGHT)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 存储选中的文件路径
        self.selected_files = []
        
    def select_files(self):
        """选择文件"""
        # 从 .ini 配置文件读取上次使用的目录
        from function.config import get_input_directory, set_input_directory
        initial_dir = get_input_directory()

        file_paths = filedialog.askopenfilenames(
            title="选择要转换的文件",
            initialdir=initial_dir if initial_dir and os.path.exists(initial_dir) else '',
            filetypes=[
                ("支持的文档文件", "*.pdf;*.docx;*.txt"),
                ("PDF 文件", "*.pdf"),
                ("Word 文档", "*.docx"),
                ("文本文件", "*.txt")
            ]
        )

        if file_paths:
            # 验证文件格式
            supported_extensions = {'.pdf', '.docx', '.txt'}
            unsupported_files = []
            supported_files = []

            for file_path in file_paths:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in supported_extensions:
                    supported_files.append(file_path)
                else:
                    unsupported_files.append(os.path.basename(file_path))

            # 如果有不支持的文件，提示用户
            if unsupported_files:
                unsupported_info = "\n".join(f"  • {f}" for f in unsupported_files[:5])
                if len(unsupported_files) > 5:
                    unsupported_info += f"\n  ... 还有 {len(unsupported_files) - 5} 个文件"

                messagebox.showwarning(
                    "文件格式警告",
                    f"以下文件格式不支持，将被跳过:\n{unsupported_info}\n\n支持的格式: PDF (.pdf)、Word (.docx)、文本 (.txt)"
                )

            if supported_files:
                self.selected_files = supported_files
                self.update_file_list_display()
                self.convert_btn.config(state=tk.NORMAL)
                self.status_var.set(f"已选择 {len(supported_files)} 个文件")

                # 保存输入目录（使用第一个文件的目录）
                input_dir = os.path.dirname(supported_files[0])
                set_input_directory(input_dir)
            else:
                self.status_var.set("没有选择支持的文件格式")
            
    def select_directory(self):
        """选择目录"""
        from function.config import get_input_directory, set_input_directory

        # 从 .ini 配置文件读取上次使用的目录
        initial_dir = get_input_directory()

        directory = filedialog.askdirectory(
            title="选择包含文档的目录",
            initialdir=initial_dir if initial_dir and os.path.exists(initial_dir) else ''
        )

        if directory:
            # 保存输入目录
            set_input_directory(directory)

            # 获取目录中的所有文档文件
            supported_extensions = {'.pdf', '.docx', '.txt'}
            files_in_dir = []
            unsupported_count = 0

            try:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        file_ext = os.path.splitext(filename)[1].lower()
                        if file_ext in supported_extensions:
                            files_in_dir.append(file_path)
                        else:
                            unsupported_count += 1

                if files_in_dir:
                    self.selected_files = files_in_dir
                    self.update_file_list_display()
                    self.convert_btn.config(state=tk.NORMAL)

                    # 如果有不支持的文件，提示用户
                    if unsupported_count > 0:
                        self.status_var.set(f"已选择 {len(files_in_dir)} 个文件（跳过 {unsupported_count} 个不支持的文件）")
                    else:
                        self.status_var.set(f"已选择 {len(files_in_dir)} 个文件")
                else:
                    messagebox.showinfo(
                        "提示",
                        f"所选目录中没有找到支持的文档文件。\n\n支持的格式: PDF (.pdf)、Word (.docx)、文本 (.txt)"
                    )
            except PermissionError:
                messagebox.showerror("错误", "没有权限访问该目录，请选择其他目录。")
            except Exception as e:
                messagebox.showerror("错误", f"读取目录时出错: {str(e)}")
                
    def update_file_list_display(self):
        """更新文件列表显示"""
        # 清空现有列表
        for item in self.file_treeview.get_children():
            self.file_treeview.delete(item)

        # 添加文件到列表
        for file_path in self.selected_files:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            file_type = os.path.splitext(file_path)[1].upper().replace('.', '')

            # 格式化文件大小
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            self.file_treeview.insert('', tk.END, values=(filename, size_str, file_type))
            
    def start_conversion(self):
        """开始转换"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要转换的文件。")
            return

        # 重置取消事件
        self.conversion_cancelled.clear()

        # 禁用转换按钮，启用取消按钮
        self.convert_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)

        # 重置进度条
        self.progress_var.set(0)
        self.progress_label_var.set(f"0/{len(self.selected_files)}")

        # 更新状态
        self.status_var.set(f"正在转换... (0/{len(self.selected_files)})")

        # 设置转换进行中标志
        self.conversion_in_progress = True

        # 从 .ini 配置文件获取输出目录
        from function.config import get_output_directory
        output_dir = get_output_directory()

        # 在新线程中执行转换以避免界面冻结
        conversion_thread = threading.Thread(target=self.perform_conversion, args=(output_dir,))
        conversion_thread.daemon = True
        conversion_thread.start()
        
    def perform_conversion(self, output_dir=None):
        """执行转换操作"""
        try:
            from function.core import convert_single_file

            total_files = len(self.selected_files)
            converted_count = 0
            failed_files = []

            # 执行逐个转换，支持实时进度更新和取消
            for i, file_path in enumerate(self.selected_files):
                # 检查是否被取消
                if self.conversion_cancelled.is_set():
                    self.status_var.set(f"转换已取消，已处理: {converted_count}/{total_files}")
                    break

                # 更新状态
                self.status_var.set(f"正在转换... ({converted_count + 1}/{total_files}) - {os.path.basename(file_path)}")

                # 更新进度条
                progress = ((i + 1) / total_files) * 100
                self.progress_var.set(progress)
                self.progress_label_var.set(f"{i + 1}/{total_files}")

                # 如果输出目录为空或 None，则使用原始文件目录
                file_output_dir = output_dir
                if not output_dir or output_dir.strip() == '' or output_dir == './output':
                    file_output_dir = None  # 让 convert_single_file 使用原始文件目录

                # 调用转换函数，传入输出目录
                success = convert_single_file(file_path, file_output_dir)

                if success:
                    converted_count += 1
                else:
                    failed_files.append(os.path.basename(file_path))

                # 强制更新UI
                self.root.update_idletasks()

            # 显示最终结果
            if not self.conversion_cancelled.is_set():
                self.status_var.set(f"转换完成! 成功: {converted_count}, 总计: {total_files}")
                # 完成进度条
                self.progress_var.set(100)

                # 如果有失败的文件，显示详细信息
                if failed_files:
                    failed_info = f"\n以下文件转换失败:\n" + "\n".join(f"  • {f}" for f in failed_files[:5])
                    if len(failed_files) > 5:
                        failed_info += f"\n  ... 还有 {len(failed_files) - 5} 个文件"
                    messagebox.showwarning("转换完成", f"成功转换 {converted_count} 个文件，{len(failed_files)} 个文件失败。{failed_info}\n\n请检查文件是否损坏或格式是否正确。")

                # 记录转换历史
                from function.config import add_conversion_history
                results = {
                    'success': [f for f in self.selected_files[:converted_count]],
                    'failed': failed_files,
                    'skipped': []
                }
                add_conversion_history(self.selected_files, results)
            else:
                self.status_var.set(f"转换已取消，成功: {converted_count}, 总计: {total_files}")

        except ImportError:
            error_msg = "程序组件缺失，无法完成转换。请确保所有依赖已正确安装。"
            self.status_var.set("错误: 程序组件缺失")
            messagebox.showerror("错误", error_msg)
        except Exception as e:
            error_msg = f"转换过程中发生错误: {str(e)}\n\n建议：\n1. 检查文件是否损坏\n2. 确认文件格式是否支持\n3. 查看日志文件获取详细信息"
            self.status_var.set("转换过程中发生错误")
            messagebox.showerror("错误", error_msg)
        finally:
            # 恢复按钮状态
            self.root.after(0, lambda: self.convert_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.cancel_btn.config(state=tk.DISABLED))
            # 清除取消事件和转换进行中标志
            self.root.after(0, lambda: self.conversion_cancelled.clear())
            self.root.after(0, lambda: setattr(self, 'conversion_in_progress', False))
            
    def cancel_conversion(self):
        """取消转换"""
        # 设置取消事件
        self.conversion_cancelled.set()
        self.status_var.set("正在取消转换...")
        
    def open_output_directory(self):
        """打开输出目录"""
        from function.config import get_output_directory

        # 从配置文件读取输出目录
        output_dir = get_output_directory()

        # 如果输出目录为空，则打开第一个选中文件所在的目录
        if not output_dir or output_dir.strip() == '':
            if self.selected_files:
                output_dir = os.path.dirname(self.selected_files[0])
            else:
                # 如果没有选中文件，则打开程序目录
                output_dir = os.path.dirname(os.path.dirname(__file__))

        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), output_dir)

        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 尝试打开输出目录
        try:
            os.startfile(output_dir)
        except AttributeError:
            # 在非 Windows 系统上的处理
            import subprocess
            try:
                subprocess.run(['xdg-open', output_dir])
            except:
                subprocess.run(['open', output_dir])

    def open_settings_dialog(self):
        """打开设置对话框"""
        from function.config import get_config_value, set_config_value

        # 创建设置对话框窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)

        # 居中显示设置窗口
        settings_window.update_idletasks()
        screen_width = settings_window.winfo_screenwidth()
        screen_height = settings_window.winfo_screenheight()
        window_width = settings_window.winfo_width()
        window_height = settings_window.winfo_height()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 创建主框架
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 输出目录设置
        ttk.Label(main_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        output_dir_var = tk.StringVar(value=get_config_value('output_directory', ''))
        output_dir_entry = ttk.Entry(main_frame, textvariable=output_dir_var, width=40)
        output_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

        # 提示信息
        hint_label = ttk.Label(main_frame, text="提示：留空则输出到原始文件所在目录", font=('Arial', 8), foreground='gray')
        hint_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        def browse_output_dir():
            directory = filedialog.askdirectory(title="选择输出目录")
            if directory:
                output_dir_var.set(directory)

        browse_btn = ttk.Button(main_frame, text="浏览...", command=browse_output_dir)
        browse_btn.grid(row=0, column=2, padx=(5, 0), pady=(0, 10))

        # 覆盖已存在文件设置
        overwrite_var = tk.BooleanVar(value=get_config_value('overwrite_existing', False))
        overwrite_check = ttk.Checkbutton(
            main_frame,
            text="覆盖已存在的文件",
            variable=overwrite_var
        )
        overwrite_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # 自动打开输出目录设置
        auto_open_var = tk.BooleanVar(value=get_config_value('auto_open_output', False))
        auto_open_check = ttk.Checkbutton(
            main_frame,
            text="转换完成后自动打开输出目录",
            variable=auto_open_var
        )
        auto_open_check.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(20, 0))

        def save_settings():
            """保存设置"""
            set_config_value('output_directory', output_dir_var.get())
            set_config_value('overwrite_existing', overwrite_var.get())
            set_config_value('auto_open_output', auto_open_var.get())
            messagebox.showinfo("设置", "设置已保存！")
            settings_window.destroy()

        save_btn = ttk.Button(button_frame, text="保存", command=save_settings)
        save_btn.pack(side=tk.LEFT, padx=(0, 5))

        cancel_btn = ttk.Button(button_frame, text="取消", command=settings_window.destroy)
        cancel_btn.pack(side=tk.LEFT)

        # 配置列权重
        main_frame.columnconfigure(1, weight=1)

    def open_history_dialog(self):
        """打开历史记录对话框"""
        from function.config import get_conversion_history, clear_conversion_history

        # 创建历史记录对话框窗口
        history_window = tk.Toplevel(self.root)
        history_window.title("转换历史记录")
        history_window.geometry("800x500")

        # 居中显示历史记录窗口
        history_window.update_idletasks()
        screen_width = history_window.winfo_screenwidth()
        screen_height = history_window.winfo_screenheight()
        window_width = history_window.winfo_width()
        window_height = history_window.winfo_height()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        history_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 创建主框架
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建 Treeview 显示历史记录
        columns = ('timestamp', 'total', 'success', 'failed', 'skipped')
        history_treeview = ttk.Treeview(main_frame, columns=columns, show='headings')

        # 设置列标题
        history_treeview.heading('timestamp', text='时间')
        history_treeview.heading('total', text='总数')
        history_treeview.heading('success', text='成功')
        history_treeview.heading('failed', text='失败')
        history_treeview.heading('skipped', text='跳过')

        # 设置列宽
        history_treeview.column('timestamp', width=180, anchor=tk.W)
        history_treeview.column('total', width=80, anchor=tk.CENTER)
        history_treeview.column('success', width=80, anchor=tk.CENTER)
        history_treeview.column('failed', width=80, anchor=tk.CENTER)
        history_treeview.column('skipped', width=80, anchor=tk.CENTER)

        # 创建滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=history_treeview.yview)
        history_treeview.configure(yscrollcommand=scrollbar.set)

        history_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 加载历史记录
        history_list = get_conversion_history()
        for entry in history_list:
            history_treeview.insert('', tk.END, values=(
                entry['timestamp'],
                entry['total_files'],
                entry['success_count'],
                entry['failed_count'],
                entry['skipped_count']
            ))

        # 按钮区域
        button_frame = ttk.Frame(history_window)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 清空历史记录按钮
        def clear_history():
            if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
                clear_conversion_history()
                # 清空列表
                for item in history_treeview.get_children():
                    history_treeview.delete(item)
                messagebox.showinfo("成功", "历史记录已清空！")

        clear_btn = ttk.Button(button_frame, text="清空历史", command=clear_history)
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 关闭按钮
        close_btn = ttk.Button(button_frame, text="关闭", command=history_window.destroy)
        close_btn.pack(side=tk.RIGHT)

    def on_window_close(self):
        """窗口关闭时的处理"""
        try:
            # 检查是否有正在进行的转换
            if hasattr(self, 'conversion_in_progress') and self.conversion_in_progress:
                # 如果有转换正在进行，询问用户是否要退出
                if messagebox.askyesno(
                    "确认退出",
                    "有转换正在进行，确定要退出吗？\n\n转换将被中断。"
                ):
                    # 设置取消标志
                    self.conversion_cancelled.set()
                    # 稍等一下让转换线程有机会清理
                    self.root.after(100, self._do_close)
                else:
                    return
            else:
                # 没有转换正在进行，直接关闭
                self._do_close()
        except Exception as e:
            print(f"窗口关闭时出错: {e}")
            self._do_close()

    def _do_close(self):
        """执行关闭操作"""
        try:
            # 保存当前的输出目录到 .ini 文件
            from function.config import get_output_directory

            # 如果用户在设置中修改了输出目录，确保它被保存
            # 这里不需要额外操作，因为设置对话框已经保存了配置

            # 销毁窗口
            self.root.destroy()
        except Exception as e:
            print(f"执行关闭操作时出错: {e}")
            self.root.destroy()