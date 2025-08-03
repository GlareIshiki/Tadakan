"""
バッチファイル管理パネル

バッチファイルの一覧・検索・削除・実行機能を提供
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional

from src.models.preset import Preset


class BatchPanel(ttk.Frame):
    """バッチファイル管理パネル"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_preset: Optional[Preset] = None
        self._drag_drop_enabled = False
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # 検索フレーム
        search_frame = ttk.Frame(self)
        ttk.Label(search_frame, text="検索:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        
        # バッチファイル一覧
        list_frame = ttk.Frame(self)
        self.batch_listbox = tk.Listbox(list_frame, height=8)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.batch_listbox.yview)
        self.batch_listbox.configure(yscrollcommand=scrollbar.set)
        
        # ボタンフレーム
        button_frame = ttk.Frame(self)
        self.delete_button = ttk.Button(button_frame, text="削除",
                                       command=self._on_delete_selected)
        self.execute_button = ttk.Button(button_frame, text="実行",
                                        command=self._on_execute_selected)
        
        # フレーム参照を保存
        self.search_frame = search_frame
        self.list_frame = list_frame
        self.button_frame = button_frame
        self.scrollbar = scrollbar
    
    def _setup_layout(self):
        """レイアウトを設定"""
        # 検索フレーム（上部）
        self.search_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # リストフレーム（中央）
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.batch_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ボタンフレーム（下部）
        self.button_frame.pack(fill=tk.X, padx=5, pady=2)
        self.delete_button.pack(side=tk.LEFT, padx=2)
        self.execute_button.pack(side=tk.LEFT, padx=2)
    
    def load_batch_files(self, batch_files: List[Dict[str, Any]]):
        """バッチファイル一覧を読み込み"""
        self.batch_listbox.delete(0, tk.END)
        
        for batch_data in batch_files:
            filename = batch_data["filename"]
            created_at = batch_data.get("created_at", "")
            display_text = f"{filename}"
            if created_at:
                display_text += f" ({created_at[:10]})"
            self.batch_listbox.insert(tk.END, display_text)
    
    def search_batch_files(self, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """バッチファイルを検索"""
        if search_term is None:
            search_term = self.search_entry.get()
        
        # 検索結果をモック（実際には BatchManager を使用）
        results = [
            {"filename": f"B63EF9_クレキュリア_アクララ.bat", "created_at": "2024-01-01"},
            {"filename": f"X1Y2Z3_セントラル_ノノミ.bat", "created_at": "2024-01-02"}
        ]
        
        # 検索条件でフィルタリング
        if search_term:
            results = [r for r in results if search_term.lower() in r["filename"].lower()]
        
        return results
    
    def enable_drag_drop(self):
        """ドラッグ&ドロップ機能を有効化"""
        self._drag_drop_enabled = True
        # 実際のドラッグ&ドロップ設定は省略
    
    def handle_file_drop(self, file_list: List[str]) -> bool:
        """ファイルドロップを処理"""
        if not self._drag_drop_enabled:
            return False
        
        # ファイル処理（実際の処理はここで実装）
        print(f"Dropped files: {file_list}")
        return True
    
    def _on_search_changed(self, event):
        """検索文字列変更時のハンドラ"""
        # リアルタイム検索（実装は省略）
        pass
    
    def _on_delete_selected(self):
        """選択されたバッチファイルを削除"""
        selection = self.batch_listbox.curselection()
        if selection:
            # 削除処理（実装は省略）
            pass
    
    def _on_execute_selected(self):
        """選択されたバッチファイルを実行"""
        selection = self.batch_listbox.curselection()
        if selection:
            # 実行処理（実装は省略）
            pass