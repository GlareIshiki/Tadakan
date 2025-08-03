"""
プリセット作成ウィザード

1画面統合形式でプリセットを作成
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List, Callable

from models.preset import Preset
from utils.id_generator import PresetIDGenerator


class PresetWizard:
    """統合プリセット作成ウィザード"""
    
    def __init__(self, parent, edit_preset: Optional[Preset] = None):
        self.parent = parent
        self.edit_preset = edit_preset
        self.created_preset: Optional[Preset] = None
        self.custom_fields: List[Dict[str, Any]] = []
        self.save_callback: Optional[Callable] = None
        self._create_dialog()
        self._load_existing_data()
    
    def _create_dialog(self):
        """統合ウィザードダイアログを作成"""
        self.dialog = tk.Toplevel(self.parent)
        title = "プリセット編集" if self.edit_preset else "プリセット作成"
        self.dialog.title(title)
        self.dialog.geometry("600x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # スクロール可能なメインフレーム
        main_canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # レイアウト
        main_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        self.content_frame = scrollable_frame
        
        # 全項目を1画面に配置
        self._create_all_widgets()
        
        # ボタンフレーム（ダイアログ直下）
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.cancel_button = ttk.Button(button_frame, text="キャンセル", command=self._on_cancel_clicked)
        self.cancel_button.pack(side=tk.LEFT)
        
        self.save_button = ttk.Button(button_frame, text="保存", command=self._on_save_clicked)
        self.save_button.pack(side=tk.RIGHT)
    
    def _create_all_widgets(self):
        """全ての入力ウィジェットを1画面に作成"""
        row = 0
        
        # タイトル
        title_text = "プリセット編集" if self.edit_preset else "プリセット作成"
        title_label = ttk.Label(self.content_frame, text=title_text, font=("Arial", 14, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 15), sticky=tk.W)
        row += 1
        
        # 基本情報セクション
        basic_label = ttk.Label(self.content_frame, text="基本情報", font=("Arial", 12, "bold"))
        basic_label.grid(row=row, column=0, columnspan=3, pady=(10, 5), sticky=tk.W)
        row += 1
        
        # プリセット名
        ttk.Label(self.content_frame, text="プリセット名:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(self.content_frame, width=40)
        self.name_entry.grid(row=row, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        row += 1
        
        # 説明
        ttk.Label(self.content_frame, text="説明:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.description_entry = tk.Text(self.content_frame, width=40, height=3)
        self.description_entry.grid(row=row, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        row += 1
        
        # 拡張子セクション
        ext_label = ttk.Label(self.content_frame, text="対象拡張子", font=("Arial", 12, "bold"))
        ext_label.grid(row=row, column=0, columnspan=3, pady=(15, 5), sticky=tk.W)
        row += 1
        
        ttk.Label(self.content_frame, text="拡張子 (カンマ区切り):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.extensions_entry = ttk.Entry(self.content_frame, width=40)
        self.extensions_entry.grid(row=row, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.extensions_entry.insert(0, "jpg,png,gif")  # デフォルト値
        row += 1
        
        # 命名規則セクション
        pattern_label = ttk.Label(self.content_frame, text="命名規則", font=("Arial", 12, "bold"))
        pattern_label.grid(row=row, column=0, columnspan=3, pady=(15, 5), sticky=tk.W)
        row += 1
        
        ttk.Label(self.content_frame, text="命名パターン:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.naming_pattern_entry = ttk.Entry(self.content_frame, width=40)
        self.naming_pattern_entry.grid(row=row, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.naming_pattern_entry.insert(0, "{id}_{faction}_{character}")  # デフォルト値
        row += 1
        
        # カスタムフィールドセクション
        fields_label = ttk.Label(self.content_frame, text="カスタムフィールド", font=("Arial", 12, "bold"))
        fields_label.grid(row=row, column=0, columnspan=3, pady=(15, 5), sticky=tk.W)
        row += 1
        
        # フィールド追加ボタン
        self.add_field_button = ttk.Button(self.content_frame, text="フィールド追加", command=self._add_custom_field)
        self.add_field_button.grid(row=row, column=0, pady=5, sticky=tk.W)
        row += 1
        
        # カスタムフィールド管理フレーム
        self.fields_frame = ttk.Frame(self.content_frame, relief="flat", borderwidth=0)
        self.fields_frame.grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=5)
        row += 1
        
        # 列の重みを設定
        self.content_frame.columnconfigure(1, weight=1)
    
    def _add_custom_field(self):
        """カスタムフィールドを追加"""
        field_index = len(self.custom_fields)
        
        # フィールド用フレーム
        field_frame = ttk.Frame(self.fields_frame, relief="flat", borderwidth=0)
        field_frame.grid(row=field_index, column=0, columnspan=3, sticky=tk.EW, pady=2)
        
        # フィールド名入力
        ttk.Label(field_frame, text="フィールド名:").grid(row=0, column=0, sticky=tk.W, padx=5)
        name_entry = ttk.Entry(field_frame, width=20)
        name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        # フィールドタイプ選択
        ttk.Label(field_frame, text="タイプ:").grid(row=0, column=2, sticky=tk.W, padx=5)
        type_combobox = ttk.Combobox(field_frame, values=["text", "number", "date"], width=10, state="readonly")
        type_combobox.grid(row=0, column=3, sticky=tk.W, padx=5)
        type_combobox.set("text")  # デフォルト値
        
        # 削除ボタン
        delete_button = ttk.Button(field_frame, text="削除", 
                                 command=lambda idx=field_index: self._remove_custom_field(idx))
        delete_button.grid(row=0, column=4, sticky=tk.W, padx=5)
        
        # フィールド情報を保存
        field_widgets = {
            'frame': field_frame,
            'name_entry': name_entry,
            'type_combobox': type_combobox,
            'delete_button': delete_button
        }
        
        self.custom_fields.append(field_widgets)
        
        # 列の重みを設定
        field_frame.columnconfigure(1, weight=1)
    
    def _remove_custom_field(self, field_index: int):
        """指定されたカスタムフィールドを削除"""
        if 0 <= field_index < len(self.custom_fields):
            # ウィジェットを削除
            self.custom_fields[field_index]['frame'].destroy()
            
            # リストから削除
            del self.custom_fields[field_index]
            
            # インデックスを再調整
            for i, field_widgets in enumerate(self.custom_fields):
                field_widgets['frame'].grid(row=i, column=0, columnspan=3, sticky=tk.EW, pady=2)
                # 削除ボタンのコマンドも更新
                field_widgets['delete_button'].config(command=lambda idx=i: self._remove_custom_field(idx))
    
    def _validate_inputs(self) -> bool:
        """入力データの妥当性を検証"""
        # プリセット名の検証
        if not self.name_entry.get().strip():
            messagebox.showerror("入力エラー", "プリセット名を入力してください。")
            return False
        
        # 命名パターンの検証
        if not self.naming_pattern_entry.get().strip():
            messagebox.showerror("入力エラー", "命名パターンを入力してください。")
            return False
        
        return True
    
    def _collect_preset_data(self) -> Dict[str, Any]:
        """プリセットデータを収集"""
        # 基本情報
        data = {
            'name': self.name_entry.get().strip(),
            'description': self.description_entry.get("1.0", tk.END).strip(),
            'naming_pattern': self.naming_pattern_entry.get().strip()
        }
        
        # 拡張子データ
        extensions_text = self.extensions_entry.get().strip()
        if extensions_text:
            data['target_extensions'] = [ext.strip() for ext in extensions_text.split(',')]
        else:
            data['target_extensions'] = []
        
        # カスタムフィールドデータ（Presetモデルは List[str] を期待）
        fields = []
        for field_widgets in self.custom_fields:
            field_name = field_widgets['name_entry'].get().strip()
            if field_name:
                fields.append(field_name)
        
        data['fields'] = fields
        
        return data
    
    def _create_preset_from_data(self) -> Optional[Preset]:
        """収集したデータからプリセットを作成"""
        try:
            preset_data = self._collect_preset_data()
            
            # IDを生成（編集モードでない場合）
            if self.edit_preset:
                preset_id = self.edit_preset.id
            else:
                # 既存IDリストは実際の実装では取得する必要がある
                existing_ids = set()  # プレースホルダー
                generator = PresetIDGenerator()
                preset_id = generator.generate_unique(existing_ids)
            
            preset = Preset(
                id=preset_id,
                name=preset_data['name'],
                description=preset_data.get('description', ''),
                naming_pattern=preset_data['naming_pattern'],
                fields=preset_data['fields'],
                target_extensions=preset_data['target_extensions']
            )
            
            return preset
            
        except Exception as e:
            messagebox.showerror("エラー", f"プリセット作成中にエラーが発生しました: {str(e)}")
            return None
    
    def _load_existing_data(self):
        """編集モード時に既存データを読み込み"""
        if not self.edit_preset:
            return
        
        # 基本情報を設定
        self.name_entry.insert(0, self.edit_preset.name)
        if hasattr(self.edit_preset, 'description') and self.edit_preset.description:
            self.description_entry.insert("1.0", self.edit_preset.description)
        
        # 拡張子を設定
        if self.edit_preset.target_extensions:
            self.extensions_entry.delete(0, tk.END)
            self.extensions_entry.insert(0, ",".join(self.edit_preset.target_extensions))
        
        # 命名パターンを設定
        self.naming_pattern_entry.delete(0, tk.END)
        self.naming_pattern_entry.insert(0, self.edit_preset.naming_pattern)
        
        # カスタムフィールドを設定
        if self.edit_preset.fields:
            for field_name in self.edit_preset.fields:
                self._add_custom_field()
                # 最後に追加されたフィールドに値を設定
                last_field = self.custom_fields[-1]
                last_field['name_entry'].insert(0, field_name)
                last_field['type_combobox'].set("text")  # デフォルトタイプ
    
    def set_save_callback(self, callback: Callable):
        """保存コールバックを設定"""
        self.save_callback = callback
    
    def _on_save_clicked(self):
        """保存ボタンクリック時の処理"""
        if not self._validate_inputs():
            return
        
        self.created_preset = self._create_preset_from_data()
        if self.created_preset:
            # コールバック実行
            if self.save_callback:
                self.save_callback(self.created_preset)
            
            messagebox.showinfo("完了", "プリセットを保存しました。")
            self.dialog.destroy()
    
    def _on_cancel_clicked(self):
        """キャンセルボタンクリック時の処理"""
        self.created_preset = None
        self.dialog.destroy()


# 旧メソッドとの互換性のため
    def next_step(self):
        """互換性のためのダミーメソッド"""
        pass
    
    def previous_step(self):
        """互換性のためのダミーメソッド"""
        pass
    
    def set_wizard_data(self, data: Dict[str, Any]):
        """ウィザードデータを設定（互換性維持）"""
        if 'name' in data:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, data['name'])
        
        if 'description' in data:
            self.description_entry.delete("1.0", tk.END)
            self.description_entry.insert("1.0", data['description'])
        
        if 'naming_pattern' in data:
            self.naming_pattern_entry.delete(0, tk.END)
            self.naming_pattern_entry.insert(0, data['naming_pattern'])
        
        if 'target_extensions' in data:
            self.extensions_entry.delete(0, tk.END)
            if isinstance(data['target_extensions'], list):
                self.extensions_entry.insert(0, ",".join(data['target_extensions']))
            else:
                self.extensions_entry.insert(0, data['target_extensions'])
        
        if 'fields' in data:
            if isinstance(data['fields'], dict):
                # 旧形式（Dict）のサポート
                for field_name, field_type in data['fields'].items():
                    self._add_custom_field()
                    last_field = self.custom_fields[-1]
                    last_field['name_entry'].insert(0, field_name)
                    last_field['type_combobox'].set(field_type)
            elif isinstance(data['fields'], list):
                # 新形式（List）のサポート
                for field_name in data['fields']:
                    self._add_custom_field()
                    last_field = self.custom_fields[-1]
                    last_field['name_entry'].insert(0, field_name)
                    last_field['type_combobox'].set("text")