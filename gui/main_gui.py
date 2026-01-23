import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from pathlib import Path

# Import required functions and classes from the existing script
from marker.scripts.convert import worker_init, process_single_pdf
from marker.config.parser import ConfigParser
from marker.logger import configure_logging, get_logger
from marker.models import create_model_dict
from marker.output import output_exists, save_output
from marker.utils.gpu import GPUManager
from marker.utils.batch import get_batch_sizes_worker_counts

import atexit
import time
import math
import traceback
import torch
import torch.multiprocessing as mp
import psutil
import gc
from tqdm import tqdm

# Import for drag and drop functionality
try:
    from tkinterdnd2 import Tk, DND_FILES, Text
    USE_DND = True
    print("tkinterdnd2 successfully imported")
except ImportError:
    # If tkinterdnd2 is not available, we'll handle it gracefully
    USE_DND = False
    print("Warning: tkinterdnd2 not available. Drag and drop functionality will be disabled.")


configure_logging()
logger = get_logger()


class PDFConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Converter")
        self.root.geometry("600x500")
        
        # Variables to store user selections
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar(value=os.getcwd())
        self.max_files = tk.IntVar(value=0)  # 0 means no limit
        self.skip_existing = tk.BooleanVar(value=True)
        self.debug_print = tk.BooleanVar(value=False)
        
        # Progress tracking
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="准备就绪")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Input folder selection
        ttk.Label(main_frame, text="输入文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_path)
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="浏览", command=self.select_input_folder).grid(row=0, column=1)
        
        # Enable drag and drop for input folder if available
        if USE_DND:
            self.input_entry.drop_target_register(DND_FILES)
            self.input_entry.dnd_bind('<<Drop>>', self.on_drop_input)
        
        # Output folder selection
        ttk.Label(main_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="浏览", command=self.select_output_folder).grid(row=0, column=1)
        
        # Enable drag and drop for output folder if available
        if USE_DND:
            self.output_entry.drop_target_register(DND_FILES)
            self.output_entry.dnd_bind('<<Drop>>', self.on_drop_output)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Max files option
        ttk.Label(options_frame, text="最大文件数:").grid(row=0, column=0, sticky=tk.W, pady=2)
        max_files_spinbox = ttk.Spinbox(options_frame, from_=0, to=10000, textvariable=self.max_files, width=10)
        max_files_spinbox.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Skip existing files option
        skip_checkbox = ttk.Checkbutton(options_frame, text="跳过已存在的文件", variable=self.skip_existing)
        skip_checkbox.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Debug print option
        debug_checkbox = ttk.Checkbutton(options_frame, text="调试打印", variable=self.debug_print)
        debug_checkbox.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Progress bar
        ttk.Label(main_frame, text="进度:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(20, 5), padx=(5, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=1)
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Convert button
        self.convert_button = ttk.Button(main_frame, text="开始转换", command=self.start_conversion)
        self.convert_button.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        # Log text area
        ttk.Label(main_frame, text="日志:").grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        self.log_text = tk.Text(main_frame, height=10, state=tk.DISABLED)
        self.log_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure row weights for resizing
        main_frame.rowconfigure(7, weight=1)
    
    def select_input_folder(self):
        folder_selected = filedialog.askdirectory(title="选择输入文件夹")
        if folder_selected:
            self.input_path.set(folder_selected)

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory(title="选择输出文件夹")
        if folder_selected:
            self.output_path.set(folder_selected)
    
    def on_drop_input(self, event):
        """Handle drag and drop for input folder"""
        if USE_DND:
            # Get the dropped file path(s)
            paths = self.root.tk.splitlist(event.data)
            # Take the first path and check if it's a directory
            path = paths[0]  # Get the first dropped item
            if os.path.isdir(path):
                self.input_path.set(path)
            elif os.path.isfile(path):
                # If a file is dropped, use its parent directory
                self.input_path.set(os.path.dirname(path))
    
    def on_drop_output(self, event):
        """Handle drag and drop for output folder"""
        if USE_DND:
            # Get the dropped file path(s)
            paths = self.root.tk.splitlist(event.data)
            # Take the first path and check if it's a directory
            path = paths[0]  # Get the first dropped item
            if os.path.isdir(path):
                self.output_path.set(path)
            elif os.path.isfile(path):
                # If a file is dropped, use its parent directory
                self.output_path.set(os.path.dirname(path))
    
    def log_message(self, message):
        """Add a message to the log text area"""
        self.root.after(0, lambda: self._add_log_message(message))
    
    def _add_log_message(self, message):
        """Actually add the message to the log text area (called from main thread)"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入文件夹")
            return
        
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出文件夹")
            return
        
        # Disable the convert button during conversion
        self.convert_button.config(state=tk.DISABLED)
        
        # Start conversion in a separate thread
        conversion_thread = threading.Thread(target=self.run_conversion)
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def run_conversion(self):
        """Run the actual conversion process"""
        try:
            # Prepare arguments for the conversion function
            in_folder = self.input_path.get()
            output_dir = self.output_path.get()
            max_files = self.max_files.get() if self.max_files.get() > 0 else None
            skip_existing = self.skip_existing.get()
            debug_print = self.debug_print.get()
            
            # Update status
            self.update_status("开始转换...")
            self.log_message(f"开始转换文件夹: {in_folder}")
            
            # Actual conversion process based on the original convert_cli function
            total_pages = 0
            in_folder = os.path.abspath(in_folder)
            files = [os.path.join(in_folder, f) for f in os.listdir(in_folder)]
            files = [f for f in files if os.path.isfile(f) and f.lower().endswith('.pdf')]  # Only PDF files
            
            # Limit files converted if needed
            if max_files:
                files = files[:max_files]

            self.log_message(
                f"找到 {len(files)} 个PDF文件待转换"
            )
            
            if not files:
                self.log_message("没有找到PDF文件，转换结束")
                self.update_status("转换完成!")
                return
            
            # Update progress bar range
            self.root.after(0, lambda: self.progress_var.set(0))
            self.root.after(0, lambda: self.progress_bar.config(maximum=len(files)))
            
            start_time = time.time()
            
            # Initialize models once for the entire process
            self.log_message("正在初始化模型...")
            try:
                # Create model dictionary in the worker thread
                model_dict = create_model_dict()
                model_refs = model_dict
                self.log_message("模型初始化完成")
            except Exception as e:
                self.log_message(f"模型初始化出错: {str(e)}")
                self.log_message(f"错误详情: {traceback.format_exc()}")
                raise e

            # Process files sequentially to avoid multiprocessing issues in GUI
            for i, file_path in enumerate(files):
                try:
                    self.log_message(f"正在处理: {os.path.basename(file_path)} ({i+1}/{len(files)})")
                    
                    # Prepare arguments for a single file
                    kwargs = {
                        'output_dir': output_dir,
                        'max_files': max_files,
                        'skip_existing': skip_existing,
                        'debug_print': debug_print,
                        'chunk_idx': 0,
                        'num_chunks': 1,
                        'max_tasks_per_worker': 10,
                        'workers': None,
                        'disable_multiprocessing': True,
                        'total_torch_threads': 2,  # Default thread count
                    }
                    
                    # Add config options from ConfigParser
                    config_parser = ConfigParser(kwargs)
                    kwargs.update(config_parser.generate_config_dict())

                    # Add the specific file and its options to the args tuple
                    arg = (file_path, kwargs)

                    # Process the file in a way that doesn't block the UI
                    self.root.update_idletasks()  # Allow UI to update
                    
                    # Create converter instance directly instead of calling process_single_pdf
                    torch.set_num_threads(kwargs["total_torch_threads"])
                    del kwargs["total_torch_threads"]

                    config_parser = ConfigParser(kwargs)

                    out_folder = config_parser.get_output_folder(file_path)
                    base_name = config_parser.get_base_filename(file_path)
                    if kwargs.get("skip_existing") and output_exists(out_folder, base_name):
                        continue

                    converter_cls = config_parser.get_converter_cls()
                    config_dict = config_parser.generate_config_dict()
                    config_dict["disable_tqdm"] = True

                    try:
                        if kwargs.get("debug_print"):
                            logger.debug(f"Converting {file_path}")
                        converter = converter_cls(
                            config=config_dict,
                            artifact_dict=model_refs,
                            processor_list=config_parser.get_processors(),
                            renderer=config_parser.get_renderer(),
                            llm_service=config_parser.get_llm_service(),
                        )
                        rendered = converter(file_path)
                        out_folder = config_parser.get_output_folder(file_path)
                        save_output(rendered, out_folder, base_name)
                        page_count = converter.page_count

                        if kwargs.get("debug_print"):
                            logger.debug(f"Converted {file_path}")
                        del rendered
                        del converter
                    except Exception as e:
                        logger.error(f"Error converting {file_path}: {e}")
                        self.log_message(f"转换文件时出错 {file_path}: {str(e)}")
                        continue

                    total_pages += converter.page_count
                    
                    # Update progress
                    progress_percent = ((i + 1) / len(files)) * 100
                    self.root.after(0, lambda pct=progress_percent: self.progress_var.set(pct))
                    self.root.after(0, lambda pct=progress_percent: self.progress_label.config(text=f"{pct:.0f}%"))
                    
                    self.log_message(f"已完成: {os.path.basename(file_path)} ({converter.page_count} 页)")
                    
                except Exception as e:
                    self.log_message(f"处理文件时出错 {file_path}: {str(e)}")
                    self.log_message(f"错误详情: {traceback.format_exc()}")
                    continue
            
            total_time = time.time() - start_time
            self.log_message(
                f"处理完成 {total_pages} 页，耗时 {total_time:.2f} 秒，吞吐量 {total_pages / total_time:.2f} 页/秒"
            )
            
            # Conversion completed
            self.update_status("转换完成!")
            self.log_message("所有文件转换完成!")
            
        except Exception as e:
            error_msg = f"转换过程中发生错误: {str(e)}"
            self.update_status("转换失败!")
            self.log_message(error_msg)
            self.log_message(f"错误详情: {traceback.format_exc()}")
            # Show error in main thread
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        finally:
            # Re-enable the convert button in the main thread
            self.root.after(0, lambda: self.convert_button.config(state=tk.NORMAL))
    
    def update_status(self, status):
        """Update the status label (thread-safe)"""
        self.root.after(0, lambda: self.status_var.set(status))


def center_window(window, width, height):
    """Center the window on the screen"""
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position to center the window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    # Set the geometry
    window.geometry(f'{width}x{height}+{x}+{y}')


def main():
    if USE_DND:
        root = Tk()
    else:
        root = tk.Tk()

    # Temporarily withdraw the window to prevent flickering
    root.withdraw()

    # Set window properties before showing
    root.title("PDF Converter")
    root.geometry("600x500")

    # Center the window
    center_window(root, 600, 500)

    # Create the app instance
    app = PDFConverterGUI(root)

    # Update the window to calculate all widget sizes
    root.update_idletasks()

    # Now show the window at the centered position
    root.deiconify()

    # Bring window to front
    root.lift()
    root.focus_force()

    root.mainloop()


if __name__ == "__main__":
    main()