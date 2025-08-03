"""
プリセット作成ウィザード

ステップバイステップでプリセットを作成
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

from src.models.preset import Preset


class PresetWizard:
    """プリセット作成ウィザード"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_step = 1
        self.wizard_data = {}
        self.created_preset: Optional[Preset] = None
        self._create_dialog()
    
    def _create_dialog(self):
        """ウィザードダイアログを作成"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("プリセット作成ウィザード")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # ステップ表示フレーム
        step_frame = ttk.Frame(self.dialog)
        step_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.step_label = ttk.Label(step_frame, text="ステップ 1/3", font=("Arial", 12, "bold"))
        self.step_label.pack(anchor=tk.W)
        
        # メインコンテンツフレーム
        self.content_frame = ttk.Frame(self.dialog)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # ナビゲーションボタンフレーム
        nav_frame = ttk.Frame(self.dialog)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.prev_button = ttk.Button(nav_frame, text="< 戻る", command=self.previous_step)
        self.prev_button.pack(side=tk.LEFT)
        
        self.next_button = ttk.Button(nav_frame, text="次へ >", command=self.next_step)
        self.next_button.pack(side=tk.RIGHT)
        
        self.finish_button = ttk.Button(nav_frame, text="完了", command=self._finish)
        self.finish_button.pack(side=tk.RIGHT, padx=5)
        
        # 最初のステップを表示
        self.show_basic_info_step()
    
    def show_basic_info_step(self):
        """基本情報入力ステップ"""
        self.current_step = 1
        self._clear_content()
        self.step_label.config(text="ステップ 1/3: 基本情報")
        
        # プリセット名
        ttk.Label(self.content_frame, text="プリセット名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(self.content_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 説明
        ttk.Label(self.content_frame, text="説明:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.desc_text = tk.Text(self.content_frame, width=30, height=4)
        self.desc_text.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # ボタン状態更新
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)
        self.finish_button.config(state=tk.DISABLED)
        
        self.content_frame.columnconfigure(1, weight=1)
    
    def next_step(self):
        """次のステップへ"""
        if self.current_step == 1:
            self._save_basic_info()
            self._show_fields_step()
        elif self.current_step == 2:
            self._save_fields_info()
            self._show_pattern_step()
    
    def previous_step(self):
        """前のステップへ"""
        if self.current_step == 2:
            self.show_basic_info_step()
        elif self.current_step == 3:
            self._show_fields_step()
    
    def _save_basic_info(self):
        """基本情報を保存"""
        self.wizard_data["name"] = self.name_entry.get()
        self.wizard_data["description"] = self.desc_text.get("1.0", tk.END).strip()
    
    def _show_fields_step(self):
        """フィールド設定ステップ"""
        self.current_step = 2
        self._clear_content()
        self.step_label.config(text="ステップ 2/3: フィールド設定")
        
        ttk.Label(self.content_frame, text="フィールド一覧:").pack(anchor=tk.W, pady=5)
        
        # フィールド入力フレーム
        fields_frame = ttk.Frame(self.content_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fields_listbox = tk.Listbox(fields_frame, height=8)
        self.fields_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # フィールド操作ボタン
        button_frame = ttk.Frame(fields_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        ttk.Button(button_frame, text="追加", command=self._add_field).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="削除", command=self._remove_field).pack(fill=tk.X, pady=2)
        
        # フィールド入力
        entry_frame = ttk.Frame(self.content_frame)
        entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(entry_frame, text="フィールド名:").pack(side=tk.LEFT)
        self.field_entry = ttk.Entry(entry_frame, width=20)
        self.field_entry.pack(side=tk.LEFT, padx=5)
        
        # ボタン状態更新
        self.prev_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.finish_button.config(state=tk.DISABLED)
    
    def _save_fields_info(self):
        """フィールド情報を保存"""
        fields = []
        for i in range(self.fields_listbox.size()):
            fields.append(self.fields_listbox.get(i))
        self.wizard_data["fields"] = fields
    
    def _show_pattern_step(self):
        """命名パターン設定ステップ"""
        self.current_step = 3
        self._clear_content()
        self.step_label.config(text="ステップ 3/3: 命名パターン")
        
        ttk.Label(self.content_frame, text="命名パターン:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pattern_entry = ttk.Entry(self.content_frame, width=40)
        self.pattern_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 対象拡張子
        ttk.Label(self.content_frame, text="対象拡張子:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.ext_text = tk.Text(self.content_frame, width=40, height=4)
        self.ext_text.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.ext_text.insert("1.0", ".png, .jpg, .gif")
        
        # ボタン状態更新
        self.prev_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)
        self.finish_button.config(state=tk.NORMAL)
        
        self.content_frame.columnconfigure(1, weight=1)
    
    def _add_field(self):
        """フィールドを追加"""
        field_name = self.field_entry.get().strip()
        if field_name:
            self.fields_listbox.insert(tk.END, field_name)
            self.field_entry.delete(0, tk.END)
    
    def _remove_field(self):
        """選択されたフィールドを削除"""
        selection = self.fields_listbox.curselection()
        if selection:
            self.fields_listbox.delete(selection[0])
    
    def _clear_content(self):
        """コンテンツフレームをクリア"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def set_wizard_data(self, data: Dict[str, Any]):
        """ウィザードデータを設定"""
        self.wizard_data = data.copy()
    
    def create_preset_from_wizard(self) -> Optional[Preset]:
        """ウィザードデータからプリセットを作成"""
        if not self.wizard_data:
            return None
        
        # 拡張子リストを解析
        ext_text = self.wizard_data.get("target_extensions", "")
        if isinstance(ext_text, str):
            extensions = [ext.strip() for ext in ext_text.split(",")]
        else:
            extensions = ext_text
        
        preset = Preset(
            name=self.wizard_data["name"],
            fields=self.wizard_data["fields"],
            naming_pattern=self.wizard_data["naming_pattern"],
            target_extensions=extensions,
            auto_generate_id=True
        )
        
        self.created_preset = preset
        return preset
    
    def _finish(self):
        """ウィザード完了"""
        # 最終データを保存
        self.wizard_data["naming_pattern"] = self.pattern_entry.get()
        self.wizard_data["target_extensions"] = self.ext_text.get("1.0", tk.END).strip()
        
        # プリセット作成
        self.create_preset_from_wizard()
        
        self.dialog.destroy()