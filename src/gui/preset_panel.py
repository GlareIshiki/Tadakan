"""
プリセット管理パネル

プリセットの一覧・選択・編集・作成機能を提供
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Callable, Optional

from models.preset import Preset
from gui.preset_wizard import PresetWizard


class PresetPanel(ttk.Frame):
    """プリセット管理パネル"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._selection_handler: Optional[Callable] = None
        self.preset_manager = None
        self.main_window = None
        self._presets_data = []  # 実際のプリセットデータを保存
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        print("[PresetPanel] ウィジェット作成開始")
        
        # リストボックス用フレームを最初に作成
        self.list_frame = ttk.Frame(self, relief='groove', borderwidth=2)
        
        # プリセット一覧リストボックス（親フレームを明示的に指定）
        self.preset_listbox = tk.Listbox(self.list_frame, height=10, width=50, selectmode=tk.SINGLE,
                                        bg='white', relief='sunken', borderwidth=1)
        self.preset_listbox.bind("<<ListboxSelect>>", self.on_preset_select)
        
        # スクロールバー（同じ親フレームに配置）
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.preset_listbox.yview)
        self.preset_listbox.configure(yscrollcommand=self.scrollbar.set)
        
        # ボタンフレーム
        self.button_frame = ttk.Frame(self)
        
        # 各種操作ボタン
        self.create_button = ttk.Button(self.button_frame, text="新規作成", 
                                       command=self.create_new_preset)
        self.edit_button = ttk.Button(self.button_frame, text="編集",
                                     command=self.edit_selected_preset)
        self.delete_button = ttk.Button(self.button_frame, text="削除",
                                       command=self.delete_selected_preset)
        self.wizard_button = ttk.Button(self.button_frame, text="ウィザード", 
                                       command=self.show_creation_wizard)
        
        # デバッグ用：初期表示データを追加
        self.preset_listbox.insert(tk.END, "=== プリセット一覧 ===")
        self.preset_listbox.insert(tk.END, "読み込み中...")
        
        print("[PresetPanel] ウィジェット作成完了")
    
    def _setup_layout(self):
        """レイアウトを設定"""
        print("[PresetPanel] レイアウト設定開始")
        
        # タイトルラベル
        title_label = ttk.Label(self, text="プリセット管理", font=("Arial", 12, "bold"))
        title_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # リストボックス用フレーム（既に_create_widgetsで作成済み）
        self.list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # リストボックス内でのレイアウト
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ボタンフレーム（下部）
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # ボタン配置（1行レイアウト）
        self.create_button.pack(side=tk.LEFT, padx=5)
        self.wizard_button.pack(side=tk.LEFT, padx=5)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        print("[PresetPanel] レイアウト設定完了")
        
        # 強制的にレイアウトを更新
        self.update_idletasks()
    
    def load_presets(self, presets: List[Preset]):
        """プリセット一覧を読み込み"""
        print(f"[PresetPanel] load_presets呼び出し: {len(presets)}個のプリセット")
        
        # リストボックスをクリア
        self.preset_listbox.delete(0, tk.END)
        self._presets_data = presets
        
        if not presets:
            # プリセットがない場合の表示
            self.preset_listbox.insert(tk.END, "（プリセットがありません）")
            self.preset_listbox.insert(tk.END, "「新規作成」または「ウィザード」でプリセットを作成してください")
            print("[PresetPanel] プリセットなし - ガイダンス表示")
        else:
            for i, preset in enumerate(presets):
                display_text = f"{preset.id} - {preset.name}"
                if hasattr(preset, 'created_at') and preset.created_at:
                    display_text += f" ({preset.created_at[:10]})"
                self.preset_listbox.insert(tk.END, display_text)
                print(f"[PresetPanel] 項目{i}追加: {display_text}")
        
        # 強制的にウィジェットを更新
        self.preset_listbox.update()
        self.update()
        
        print(f"[PresetPanel] 最終リストボックス項目数: {self.preset_listbox.size()}")
        print(f"[PresetPanel] リストボックス表示状態: {self.preset_listbox.winfo_viewable()}")
    
    def set_selection_handler(self, handler: Callable):
        """選択イベントハンドラーを設定"""
        self._selection_handler = handler
    
    def on_preset_select(self, event):
        """プリセット選択イベント"""
        selection = self.preset_listbox.curselection()
        if selection and self._selection_handler and self._presets_data:
            index = selection[0]
            if 0 <= index < len(self._presets_data):
                selected_preset = self._presets_data[index]
                print(f"[PresetPanel] プリセット選択: {selected_preset.name} (ID: {selected_preset.id})")
                self._selection_handler(selected_preset)
        # 選択されていない場合は何もしない
    
    def set_managers(self, preset_manager, main_window):
        """マネージャー参照を設定"""
        self.preset_manager = preset_manager
        self.main_window = main_window
    
    def create_new_preset(self):
        """新規プリセット作成"""
        self.show_creation_wizard()
    
    def edit_selected_preset(self):
        """選択されたプリセットを編集"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "編集するプリセットを選択してください。")
            return
        
        index = selection[0]
        if 0 <= index < len(self._presets_data):
            selected_preset = self._presets_data[index]
            self.show_creation_wizard(selected_preset)
    
    def delete_selected_preset(self):
        """選択されたプリセットを削除"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除するプリセットを選択してください。")
            return
        
        index = selection[0]
        if 0 <= index < len(self._presets_data):
            selected_preset = self._presets_data[index]
            
            # 削除確認
            result = messagebox.askyesno(
                "削除確認",
                f"プリセット '{selected_preset.name}' を削除しますか？\n"
                f"この操作は元に戻せません。"
            )
            
            if result and self.preset_manager:
                try:
                    self.preset_manager.delete_preset(selected_preset.id)
                    self.refresh_preset_list()
                    messagebox.showinfo("完了", "プリセットを削除しました。")
                except Exception as e:
                    messagebox.showerror("エラー", f"プリセットの削除に失敗しました: {str(e)}")
    
    def show_creation_wizard(self, edit_preset: Optional[Preset] = None):
        """プリセット作成ウィザードを表示"""
        try:
            wizard = PresetWizard(self.winfo_toplevel())
            
            # 編集モードの場合、既存データを設定
            if edit_preset:
                wizard_data = {
                    "name": edit_preset.name,
                    "fields": edit_preset.fields.copy(),
                    "naming_pattern": edit_preset.naming_pattern,
                    "target_extensions": edit_preset.target_extensions.copy() if edit_preset.target_extensions else []
                }
                wizard.set_wizard_data(wizard_data)
            
            # ウィザード完了後の処理
            self.winfo_toplevel().wait_window(wizard.dialog)
            
            if wizard.created_preset and self.preset_manager:
                try:
                    if edit_preset:
                        # 編集モードの場合、既存プリセットを更新
                        wizard.created_preset.id = edit_preset.id
                        self.preset_manager.update_preset(wizard.created_preset)
                        messagebox.showinfo("完了", "プリセットを更新しました。")
                    else:
                        # 新規作成の場合
                        saved_path = self.preset_manager.save_preset(wizard.created_preset)
                        messagebox.showinfo("完了", f"プリセットを保存しました: {saved_path}")
                    
                    # リスト更新
                    self.refresh_preset_list()
                    
                    # MainWindowにコールバック
                    if self.main_window and hasattr(self.main_window, 'on_preset_created'):
                        self.main_window.on_preset_created(wizard.created_preset)
                        
                except Exception as e:
                    messagebox.showerror("エラー", f"プリセットの保存に失敗しました: {str(e)}")
                    
        except Exception as e:
            messagebox.showerror("エラー", f"ウィザードの表示に失敗しました: {str(e)}")
    
    def refresh_preset_list(self):
        """プリセット一覧を再読み込み"""
        print("[PresetPanel] refresh_preset_list呼び出し")
        
        if self.preset_manager:
            try:
                presets = self.preset_manager.list_presets()
                print(f"[PresetPanel] プリセット読み込み: {len(presets)}個")
                self.load_presets(presets)
                
            except Exception as e:
                print(f"プリセット一覧の読み込みエラー: {e}")
                import traceback
                traceback.print_exc()
                
                # エラー時でも表示されるようにデバッグメッセージを表示
                self.preset_listbox.delete(0, tk.END)
                self.preset_listbox.insert(tk.END, f"エラー: {str(e)}")
                
        else:
            print("preset_managerが設定されていません")
            # マネージャー未設定でも表示されるようにメッセージを表示
            self.preset_listbox.delete(0, tk.END)
            self.preset_listbox.insert(tk.END, "（プリセットマネージャーが未設定）")
            self.preset_listbox.insert(tk.END, "MainWindow初期化待ち...")