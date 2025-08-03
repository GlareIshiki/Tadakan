"""
プリセット管理パネル

プリセットの一覧・選択・編集・作成機能を提供
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional

from src.models.preset import Preset


class PresetPanel(ttk.Frame):
    """プリセット管理パネル"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._selection_handler: Optional[Callable] = None
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # プリセット一覧リストボックス
        self.preset_listbox = tk.Listbox(self, height=10)
        self.preset_listbox.bind("<<ListboxSelect>>", self.on_preset_select)
        
        # ボタンフレーム
        button_frame = ttk.Frame(self)
        
        # 各種操作ボタン
        self.create_button = ttk.Button(button_frame, text="新規作成")
        self.edit_button = ttk.Button(button_frame, text="編集")
        self.delete_button = ttk.Button(button_frame, text="削除")
        self.wizard_button = ttk.Button(button_frame, text="ウィザード", 
                                       command=self.show_creation_wizard)
        
        # スクロールバー
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.preset_listbox.yview)
        self.preset_listbox.configure(yscrollcommand=self.scrollbar.set)
        
        self.button_frame = button_frame
    
    def _setup_layout(self):
        """レイアウトを設定"""
        # リストボックスとスクロールバー
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ボタンフレーム（下部）
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # ボタン配置
        self.create_button.pack(side=tk.LEFT, padx=2)
        self.wizard_button.pack(side=tk.LEFT, padx=2)
        self.edit_button.pack(side=tk.LEFT, padx=2)
        self.delete_button.pack(side=tk.LEFT, padx=2)
    
    def load_presets(self, presets: List[Dict[str, Any]]):
        """プリセット一覧を読み込み"""
        self.preset_listbox.delete(0, tk.END)
        
        for preset_data in presets:
            display_text = f"{preset_data['id']} - {preset_data['name']}"
            if 'created_at' in preset_data:
                display_text += f" ({preset_data['created_at'][:10]})"
            self.preset_listbox.insert(tk.END, display_text)
    
    def set_selection_handler(self, handler: Callable):
        """選択イベントハンドラーを設定"""
        self._selection_handler = handler
    
    def on_preset_select(self, event):
        """プリセット選択イベント"""
        selection = self.preset_listbox.curselection()
        if selection and self._selection_handler:
            # 実際のプリセットオブジェクトを作成
            # 実装では適切なプリセットデータから作成する
            selected_preset = Preset(
                name="選択されたプリセット",
                fields=["陣営", "キャラ名"],
                naming_pattern="{陣営}_{キャラ名}_{番号}",
                id="B63EF9"
            )
            self._selection_handler(selected_preset)
    
    def show_creation_wizard(self):
        """プリセット作成ウィザードを表示"""
        # ウィザードダイアログを表示（実装は後で）
        return {"success": True, "preset": None}