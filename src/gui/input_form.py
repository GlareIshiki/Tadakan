"""
動的入力フォーム

プリセットに基づいて動的にフォームを生成
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional

from src.models.preset import Preset
from src.models.batch_file import BatchFile


class DynamicInputForm(ttk.Frame):
    """動的入力フォーム"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.input_fields: Dict[str, tk.StringVar] = {}
        self.current_preset: Optional[Preset] = None
        self._suggestion_data: Dict[str, List[str]] = {}
        self.batch_manager = None
        self.main_window = None
        self._form_widgets: List[tk.Widget] = []  # フォーム内ウィジェットを追跡
        self._create_base_widgets()
    
    def _create_base_widgets(self):
        """基本ウィジェットを作成"""
        # タイトルラベル
        title_label = ttk.Label(self, text="入力フォーム", font=("Arial", 10, "bold"))
        title_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # フォーム用フレーム
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # バッチ作成ボタン
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.create_batch_button = ttk.Button(button_frame, text="バッチファイル作成",
                                            command=self._on_create_batch_clicked)
        self.create_batch_button.pack(side=tk.RIGHT)
    
    def generate_form_from_preset(self, preset: Preset):
        """プリセットから動的にフォームを生成"""
        # 既存のフィールドをクリア
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        
        self.input_fields.clear()
        self.current_preset = preset
        
        # 各フィールドのウィジェットを作成
        for i, field_name in enumerate(preset.fields):
            # ラベル
            label = ttk.Label(self.form_frame, text=f"{field_name}:")
            label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            
            # 入力フィールド
            var = tk.StringVar()
            entry = ttk.Entry(self.form_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            
            # デフォルト値を設定
            if field_name in preset.default_values:
                var.set(preset.default_values[field_name])
            
            self.input_fields[field_name] = var
        
        # 列の重みを設定
        self.form_frame.columnconfigure(1, weight=1)
    
    def enable_suggestions(self, field_name: str, suggestions: List[str]):
        """指定フィールドにサジェスト機能を有効化"""
        self._suggestion_data[field_name] = suggestions
    
    def has_suggestions(self, field_name: str) -> bool:
        """フィールドにサジェスト機能があるかチェック"""
        return field_name in self._suggestion_data
    
    def get_current_suggestions(self, field_name: str) -> List[str]:
        """現在の入力に基づくサジェスト一覧を取得"""
        if field_name not in self._suggestion_data or field_name not in self.input_fields:
            return []
        
        current_value = self.input_fields[field_name].get().lower()
        if not current_value:
            return self._suggestion_data[field_name]
        
        # 部分マッチでフィルタリング
        return [s for s in self._suggestion_data[field_name] 
                if current_value in s.lower()]
    
    def set_form_data(self, form_data: Dict[str, str]):
        """フォームデータを設定"""
        for field_name, value in form_data.items():
            if field_name in self.input_fields:
                self.input_fields[field_name].set(value)
    
    def create_batch_from_form(self) -> Optional[BatchFile]:
        """フォームからバッチファイルを作成"""
        if not self.current_preset:
            return None
        
        # フォームの値を取得
        values = {}
        for field_name, var in self.input_fields.items():
            values[field_name] = var.get()
        
        # バッチファイルを作成
        batch_file = BatchFile(
            preset_id=self.current_preset.id,
            preset_name=self.current_preset.name,
            field_values=values,
            target_extensions=self.current_preset.target_extensions
        )
        
        return batch_file
    
    def set_managers(self, batch_manager, main_window):
        """マネージャー参照を設定"""
        self.batch_manager = batch_manager
        self.main_window = main_window
    
    def _on_create_batch_clicked(self):
        """バッチファイル作成ボタンクリック時の処理"""
        try:
            if not self.current_preset:
                messagebox.showwarning("警告", "プリセットが選択されていません。")
                return
            
            if not self.batch_manager:
                messagebox.showerror("エラー", "バッチマネージャーが設定されていません。")
                return
            
            # 入力値の検証
            missing_fields = []
            for field_name in self.current_preset.fields:
                value = self.input_fields.get(field_name, tk.StringVar()).get().strip()
                if not value:
                    missing_fields.append(field_name)
            
            if missing_fields:
                messagebox.showwarning(
                    "入力エラー",
                    f"以下のフィールドが未入力です:\n{', '.join(missing_fields)}"
                )
                return
            
            # バッチファイル作成
            batch_file = self.create_batch_from_form()
            if not batch_file:
                messagebox.showerror("エラー", "バッチファイルの作成に失敗しました。")
                return
            
            # バッチファイル保存
            saved_path = self.batch_manager.save_batch_file(batch_file)
            
            # 成功メッセージ
            messagebox.showinfo(
                "完了",
                f"バッチファイルを作成しました:\n{saved_path}\n\n"
                f"プリセット: {batch_file.preset_name}\n"
                f"ファイル名: {batch_file.get_batch_filename()}"
            )
            
            # MainWindowにコールバック
            if self.main_window and hasattr(self.main_window, 'on_batch_created'):
                self.main_window.on_batch_created(batch_file)
            
            # フォームをクリア
            self._clear_form_values()
            
        except Exception as e:
            messagebox.showerror("エラー", f"バッチファイル作成中にエラーが発生しました:\n{str(e)}")
    
    def _clear_form_values(self):
        """フォームの値をクリア"""
        for field_var in self.input_fields.values():
            field_var.set("")
    
    def validate_form_data(self) -> bool:
        """フォームデータの妥当性を検証"""
        if not self.current_preset:
            return False
        
        # 必須フィールドのチェック
        for field_name in self.current_preset.fields:
            value = self.input_fields.get(field_name, tk.StringVar()).get().strip()
            if not value:
                return False
        
        return True
    
    def get_form_data(self) -> Dict[str, str]:
        """フォームデータを取得"""
        form_data = {}
        for field_name, field_var in self.input_fields.items():
            form_data[field_name] = field_var.get().strip()
        return form_data
    
    def set_form_enabled(self, enabled: bool):
        """フォームの有効/無効を切り替え"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        # 入力フィールドの状態変更
        for widget in self.form_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.config(state=state)
        
        # ボタンの状態変更
        self.create_batch_button.config(state=state)
    
    def disable_form(self):
        """フォームを無効化"""
        self.set_form_enabled(False)
    
    def enable_form(self):
        """フォームを有効化"""
        self.set_form_enabled(True)