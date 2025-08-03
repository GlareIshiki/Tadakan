"""
ドロップゾーン

ファイル・フォルダのドラッグ&ドロップ機能を提供
"""

import tkinter as tk
from tkinter import ttk
from typing import List
from dataclasses import dataclass


@dataclass
class DropResult:
    """ドロップ処理結果"""
    processed_count: int
    success: bool = True
    error_message: str = ""


class DropZone(ttk.Frame):
    """ドロップゾーン"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.is_highlighted = False
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # ドロップエリア
        self.drop_area = tk.Frame(self, 
                                 bg="lightgray", 
                                 relief=tk.SUNKEN, 
                                 bd=2, 
                                 height=80)
        self.drop_area.pack_propagate(False)  # サイズ固定
        
        # ドロップエリア内のラベル
        drop_label = tk.Label(self.drop_area, 
                             text="ファイルをここにドラッグ&ドロップ",
                             bg="lightgray",
                             fg="gray")
        drop_label.pack(expand=True)
        
        # ステータスラベル
        self.status_label = tk.Label(self, text="準備完了", fg="green")
        
        # プレビューエリア（ファイル一覧表示用）
        preview_frame = ttk.Frame(self)
        self.preview_area = tk.Listbox(preview_frame, height=3)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL,
                                         command=self.preview_area.yview)
        self.preview_area.configure(yscrollcommand=preview_scrollbar.set)
        
        # フレーム参照を保存
        self.drop_label = drop_label
        self.preview_frame = preview_frame
        self.preview_scrollbar = preview_scrollbar
    
    def _setup_layout(self):
        """レイアウトを設定"""
        # ドロップエリア
        self.drop_area.pack(fill=tk.X, padx=5, pady=2)
        
        # ステータスラベル
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # プレビューエリア
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.preview_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def handle_file_drop(self, file_list: List[str]) -> DropResult:
        """ファイルドロップを処理"""
        try:
            # ファイル一覧をプレビューエリアに表示
            self.preview_area.delete(0, tk.END)
            for file_path in file_list:
                self.preview_area.insert(tk.END, file_path)
            
            # ステータス更新
            self.status_label.config(text=f"{len(file_list)}個のファイルが選択されました", 
                                   fg="blue")
            
            return DropResult(processed_count=len(file_list), success=True)
        
        except Exception as e:
            self.status_label.config(text=f"エラー: {str(e)}", fg="red")
            return DropResult(processed_count=0, success=False, error_message=str(e))
    
    def handle_folder_drop(self, folder_path: str) -> DropResult:
        """フォルダドロップを処理"""
        try:
            # フォルダ内のファイルを取得（再帰的処理はモック）
            import os
            file_count = 0
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    file_count += len(files)
            
            # プレビューエリアに情報表示
            self.preview_area.delete(0, tk.END)
            self.preview_area.insert(tk.END, f"フォルダ: {folder_path}")
            self.preview_area.insert(tk.END, f"ファイル数: {file_count}")
            
            # ステータス更新
            self.status_label.config(text=f"フォルダが選択されました（{file_count}ファイル）", 
                                   fg="blue")
            
            return DropResult(processed_count=file_count, success=True)
        
        except Exception as e:
            self.status_label.config(text=f"エラー: {str(e)}", fg="red")
            return DropResult(processed_count=0, success=False, error_message=str(e))
    
    def show_drop_feedback(self, is_highlighted: bool):
        """ドラッグオーバー時のビジュアルフィードバック"""
        self.is_highlighted = is_highlighted
        
        if is_highlighted:
            self.drop_area.config(bg="lightblue", relief=tk.RAISED)
            self.drop_label.config(bg="lightblue", text="ドロップしてください")
        else:
            self.drop_area.config(bg="lightgray", relief=tk.SUNKEN)
            self.drop_label.config(bg="lightgray", text="ファイルをここにドラッグ&ドロップ")