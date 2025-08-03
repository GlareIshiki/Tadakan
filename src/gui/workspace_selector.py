"""
ワークスペース選択ダイアログ

ワークスペースの選択・作成機能を提供
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class WorkspaceSelectorDialog:
    """ワークスペース選択ダイアログ"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self._create_dialog()
    
    def _create_dialog(self):
        """ダイアログを作成"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("ワークスペース選択")
        self.dialog.geometry("400x300")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # ワークスペース一覧
        list_frame = ttk.Frame(self.dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(list_frame, text="利用可能なワークスペース:").pack(anchor=tk.W)
        
        self.workspace_listbox = tk.Listbox(list_frame)
        self.workspace_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.browse_button = ttk.Button(button_frame, text="参照...", 
                                       command=self._browse_workspace)
        self.browse_button.pack(side=tk.LEFT, padx=2)
        
        self.create_new_button = ttk.Button(button_frame, text="新規作成", 
                                           command=self._create_new_workspace)
        self.create_new_button.pack(side=tk.LEFT, padx=2)
        
        # OK/Cancelボタン
        ok_cancel_frame = ttk.Frame(self.dialog)
        ok_cancel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.ok_button = ttk.Button(ok_cancel_frame, text="OK", 
                                   command=self._on_ok)
        self.ok_button.pack(side=tk.RIGHT, padx=2)
        
        self.cancel_button = ttk.Button(ok_cancel_frame, text="キャンセル", 
                                       command=self._on_cancel)
        self.cancel_button.pack(side=tk.RIGHT, padx=2)
    
    def _browse_workspace(self):
        """ワークスペースフォルダを参照"""
        folder = filedialog.askdirectory(title="ワークスペースフォルダを選択")
        if folder:
            self.workspace_listbox.insert(tk.END, folder)
    
    def _create_new_workspace(self):
        """新しいワークスペースを作成"""
        folder = filedialog.askdirectory(title="新しいワークスペースの場所を選択")
        if folder:
            # 新しいワークスペース作成処理
            self.workspace_listbox.insert(tk.END, folder)
    
    def _on_ok(self):
        """OKボタン処理"""
        selection = self.workspace_listbox.curselection()
        if selection:
            self.result = self.workspace_listbox.get(selection[0])
        self.dialog.destroy()
    
    def _on_cancel(self):
        """キャンセルボタン処理"""
        self.result = None
        self.dialog.destroy()