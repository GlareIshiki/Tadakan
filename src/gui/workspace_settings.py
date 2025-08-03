"""
ワークスペース設定ダイアログ

ワークスペースの各種設定を管理
"""

import tkinter as tk
from tkinter import ttk


class WorkspaceSettingsDialog:
    """ワークスペース設定ダイアログ"""
    
    def __init__(self, parent):
        self.parent = parent
        self.settings = {}
        self._create_dialog()
    
    def _create_dialog(self):
        """ダイアログを作成"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("ワークスペース設定")
        self.dialog.geometry("350x250")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 設定フレーム
        settings_frame = ttk.Frame(self.dialog)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ワークスペース名
        ttk.Label(settings_frame, text="ワークスペース名:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(settings_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # 自動バックアップ
        self.auto_backup_var = tk.BooleanVar()
        self.auto_backup_check = ttk.Checkbutton(settings_frame, 
                                                text="自動バックアップを有効にする",
                                                variable=self.auto_backup_var)
        self.auto_backup_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # バックアップ間隔
        ttk.Label(settings_frame, text="バックアップ間隔（日）:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.backup_interval_spinbox = ttk.Spinbox(settings_frame, from_=1, to=30, width=10)
        self.backup_interval_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 最大バックアップ数
        ttk.Label(settings_frame, text="最大バックアップ数:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.max_backup_spinbox = ttk.Spinbox(settings_frame, from_=1, to=50, width=10)
        self.max_backup_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 自動修復
        self.auto_repair_var = tk.BooleanVar()
        self.auto_repair_check = ttk.Checkbutton(settings_frame,
                                                text="自動修復を有効にする",
                                                variable=self.auto_repair_var)
        self.auto_repair_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 列の重みを設定
        settings_frame.columnconfigure(1, weight=1)
        
        # ボタンフレーム
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=2)
        ttk.Button(button_frame, text="キャンセル", command=self._on_cancel).pack(side=tk.RIGHT, padx=2)
    
    def _on_ok(self):
        """OK処理"""
        self.settings = {
            "workspace_name": self.name_entry.get(),
            "auto_backup": self.auto_backup_var.get(),
            "backup_interval_days": int(self.backup_interval_spinbox.get() or "7"),
            "max_backup_count": int(self.max_backup_spinbox.get() or "10"),
            "auto_repair": self.auto_repair_var.get()
        }
        self.dialog.destroy()
    
    def _on_cancel(self):
        """キャンセル処理"""
        self.settings = {}
        self.dialog.destroy()