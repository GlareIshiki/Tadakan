"""
ワークスペース状態インジケーター

ワークスペースの健康状態を表示
"""

import tkinter as tk
from tkinter import ttk


class WorkspaceStatusIndicator(ttk.Frame):
    """ワークスペース状態インジケーター"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_status = "unknown"
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # ステータスアイコン（色付きの円）
        self.status_canvas = tk.Canvas(self, width=16, height=16)
        self.status_circle = self.status_canvas.create_oval(2, 2, 14, 14, 
                                                           fill="gray", outline="")
        
        # ステータステキスト
        self.status_text = ttk.Label(self, text="状態: 不明")
        
        # 詳細情報ラベル
        self.detail_text = ttk.Label(self, text="", font=("Arial", 8))
    
    def _setup_layout(self):
        """レイアウトを設定"""
        self.status_canvas.pack(side=tk.LEFT, padx=2)
        self.status_text.pack(side=tk.LEFT, padx=5)
        self.detail_text.pack(side=tk.LEFT, padx=5)
    
    def show_status(self, status: str, message: str):
        """ステータスを表示"""
        self.current_status = status
        
        # ステータスに応じて色を変更
        color_map = {
            "healthy": "#00ff00",    # 緑
            "warning": "#ffff00",    # 黄
            "error": "#ff0000",      # 赤
            "unknown": "#808080"     # グレー
        }
        
        color = color_map.get(status, "#808080")
        self.status_canvas.itemconfig(self.status_circle, fill=color)
        
        # テキスト更新
        status_names = {
            "healthy": "正常",
            "warning": "警告",
            "error": "エラー",
            "unknown": "不明"
        }
        
        status_name = status_names.get(status, "不明")
        self.status_text.config(text=f"状態: {status_name}")
        self.detail_text.config(text=message)