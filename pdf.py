import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from PyPDF2 import PdfMerger

class PDFMergerApp:    
    def __init__(self, root):
        # 初始化PDF合并应用
        # 参数: root - Tkinter主窗口对象
        self.root = root
        # 设置窗口标题和初始大小
        self.root.title("PDF合并工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置中文字体
        self.font = ("SimHei", 10)
        
        # 创建文件列表
        self.file_listbox = tk.Listbox(root, height=15, width=80, font=self.font)
        self.file_listbox.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 创建提示标签
        self.info_label = ttk.Label(
            root,
            text="请点击下方按钮添加PDF文件进行合并",
            font=("SimHei", 12),
            justify=tk.CENTER
        )
        self.info_label.pack(pady=10)
        
        # 创建按钮框架
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(pady=15)
        
        self.add_button = ttk.Button(
            self.button_frame,
            text="添加文件",
            command=self.add_files
        )
        self.add_button.pack(side=tk.LEFT, padx=10)
        
        self.remove_button = ttk.Button(
            self.button_frame,
            text="移除选中",
            command=self.remove_selected
        )
        self.remove_button.pack(side=tk.LEFT, padx=10)
        
        self.merge_button = ttk.Button(
            self.button_frame,
            text="生成合并PDF",
            command=self.merge_pdfs
        )
        self.merge_button.pack(side=tk.LEFT, padx=10)
        
        # 状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("就绪: 点击添加按钮选择PDF文件")
        self.status_label = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 存储文件路径
        self.pdf_files = []
        

    
    def add_files(self):
        # 通过文件对话框手动选择PDF文件
        from tkinter import filedialog
        file_paths = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_paths:
            self.add_file_paths(file_paths)
    
    def add_file_paths(self, file_paths):
        # 添加文件路径到列表
        added_count = 0
        for file_path in file_paths:
            # 检查是否是PDF文件
            if file_path.lower().endswith(".pdf"):
                if file_path not in self.pdf_files:
                    self.pdf_files.append(file_path)
                    self.file_listbox.insert(tk.END, file_path)
                    added_count += 1
                    self.status_var.set(f"已添加: {os.path.basename(file_path)}")
                else:
                    self.status_var.set(f"文件已存在: {os.path.basename(file_path)}")
            else:
                self.status_var.set(f"跳过非PDF文件: {os.path.basename(file_path)}")
        if added_count > 0:
            self.status_var.set(f"成功添加 {added_count} 个文件")
    
    def remove_selected(self):
        # 移除列表中选中的PDF文件
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "请先选择要移除的文件")
            return
        
        # 从后往前删除，避免索引变化
        for i in sorted(selected_indices, reverse=True):
            removed_file = self.pdf_files.pop(i)
            self.file_listbox.delete(i)
            self.status_var.set(f"已移除: {os.path.basename(removed_file)}")
    
    def merge_pdfs(self):
        # PDF合并核心逻辑
        # 1. 验证输入：检查是否已添加PDF文件
        if not self.pdf_files:
            messagebox.showwarning("警告", "请先添加PDF文件")
            return
        
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        output_path = os.path.join(current_dir, "merged_output.pdf")
        
        # 检查输出文件是否存在
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(current_dir, f"merged_output_{counter}.pdf")
            counter += 1
        
        try:
            self.status_var.set("正在合并PDF文件...")
            self.merge_button.config(state=tk.DISABLED)
            
            # 执行PDF合并
            merger = PdfMerger()
            for i, pdf in enumerate(self.pdf_files, 1):
                self.status_var.set(f"正在处理: {os.path.basename(pdf)} ({i}/{len(self.pdf_files)})")
                merger.append(pdf)
                self.root.update()  # 更新UI以显示状态变化

            merger.write(output_path)
            merger.close()

            # 合并成功后显示对话框
            self.status_var.set("PDF文件合并完成！")
            
            # 创建自定义对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("合并成功")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            
            # 居中显示对话框
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() - dialog.winfo_reqwidth()) // 2
            y = (dialog.winfo_screenheight() - dialog.winfo_reqheight()) // 2
            dialog.geometry(f"+{x}+{y}")
            
            # 添加消息标签
            message = f"PDF合并完成！\n文件已保存至：\n{output_path}"
            label = ttk.Label(dialog, text=message, wraplength=280, justify=tk.LEFT, font=self.font)
            label.pack(pady=15)
            
            # 创建按钮框架
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=5)
            
            # 打开文件夹按钮
            def open_folder():
                folder_path = os.path.dirname(output_path)
                if sys.platform.startswith('win'):
                    os.startfile(folder_path)
                elif sys.platform.startswith('darwin'):
                    os.system(f'open "{folder_path}"')
                else:
                    os.system(f'xdg-open "{folder_path}"')
                dialog.destroy()
            
            open_btn = ttk.Button(button_frame, text="打开文件夹", command=open_folder, width=12)
            open_btn.pack(side=tk.LEFT, padx=10)
            
            # 确定按钮
            ok_btn = ttk.Button(button_frame, text="确定", command=dialog.destroy, width=12)
            ok_btn.pack(side=tk.LEFT, padx=10)
            
            # 设置对话框模态
            dialog.grab_set()
            self.root.wait_window(dialog)
            
        except Exception as e:
            self.status_var.set(f"合并失败: {str(e)}")
            messagebox.showerror("错误", f"合并失败：{str(e)}")
        finally:
            self.merge_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    # 程序主入口
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()