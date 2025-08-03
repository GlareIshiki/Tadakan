"""
ドロップゾーン

ファイル・フォルダのドラッグ&ドロップ機能を提供
"""

import tkinter as tk
from tkinter import ttk
from typing import List
from dataclasses import dataclass
import os

# tkinterdnd2のインポート（インストールされていない場合のフォールバック）
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKINTERDND_AVAILABLE = True
except ImportError:
    TKINTERDND_AVAILABLE = False
    print("警告: tkinterdnd2がインストールされていません。ドラッグ&ドロップ機能は制限されます。")


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
        self.batch_manager = None
        self.main_window = None
        self._create_widgets()
        self._setup_layout()
        self._setup_drag_drop()
    
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
        self.drop_label = tk.Label(self.drop_area, 
                                  text="ファイルをここにドラッグ&ドロップ",
                                  bg="lightgray",
                                  fg="gray")
        self.drop_label.pack(expand=True)
        
        # ステータスラベル
        self.status_label = tk.Label(self, text="準備完了", fg="green")
        
        # プレビューエリア（ファイル一覧表示用）
        preview_frame = ttk.Frame(self)
        self.preview_area = tk.Listbox(preview_frame, height=3)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL,
                                         command=self.preview_area.yview)
        self.preview_area.configure(yscrollcommand=preview_scrollbar.set)
        
        # フレーム参照を保存
        self.preview_frame = preview_frame
        self.preview_scrollbar = preview_scrollbar
    
    def _setup_layout(self):
        """レイアウトを設定"""
        # タイトルラベル
        title_label = ttk.Label(self, text="ファイルドロップゾーン", font=("Arial", 10, "bold"))
        title_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # ドロップエリア
        self.drop_area.pack(fill=tk.X, padx=5, pady=2)
        
        # ステータスラベル
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # プレビューエリア
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.preview_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _setup_drag_drop(self):
        """ドラッグ&ドロップ機能を設定"""
        if TKINTERDND_AVAILABLE:
            try:
                # ドロップエリアにドラッグ&ドロップを設定
                self.drop_area.drop_target_register(DND_FILES)
                self.drop_area.dnd_bind('<<Drop>>', self._on_drop)
                self.drop_area.dnd_bind('<<DragEnter>>', self._on_drag_enter)
                self.drop_area.dnd_bind('<<DragLeave>>', self._on_drag_leave)
                
                # ドロップラベルにも設定
                self.drop_label.drop_target_register(DND_FILES)
                self.drop_label.dnd_bind('<<Drop>>', self._on_drop)
                self.drop_label.dnd_bind('<<DragEnter>>', self._on_drag_enter)
                self.drop_label.dnd_bind('<<DragLeave>>', self._on_drag_leave)
                
            except Exception as e:
                print(f"ドラッグ&ドロップ設定エラー: {e}")
                self._setup_fallback_drop()
        else:
            self._setup_fallback_drop()
    
    def _setup_fallback_drop(self):
        """フォールバック用のドロップ機能設定"""
        # tkinterdnd2が利用できない場合のフォールバック
        # クリックでファイル選択ダイアログを表示
        self.drop_area.bind("<Button-1>", self._on_click_fallback)
        self.drop_label.bind("<Button-1>", self._on_click_fallback)
        
        # 説明テキストを更新
        self.drop_label.config(text="クリックしてファイルを選択")
    
    def _on_click_fallback(self, event):
        """フォールバック用のクリックハンドラ"""
        from tkinter import filedialog
        
        files = filedialog.askopenfilenames(
            title="処理するファイルを選択",
            filetypes=[
                ("画像ファイル", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("すべてのファイル", "*.*")
            ]
        )
        
        if files:
            file_list = list(files)
            self.handle_file_drop(file_list)
    
    def _on_drop(self, event):
        """ドロップイベントハンドラ"""
        try:
            # ドロップされたファイルパスを取得
            files = event.data.split()
            # パスの正規化
            file_list = [os.path.normpath(f.strip('{}')) for f in files]
            
            # ファイルとフォルダを分別
            files_only = []
            folders = []
            
            for path in file_list:
                if os.path.isfile(path):
                    files_only.append(path)
                elif os.path.isdir(path):
                    folders.append(path)
            
            # ファイル処理
            if files_only:
                self.handle_file_drop(files_only)
            
            # フォルダ処理
            for folder in folders:
                self.handle_folder_drop(folder)
            
            # ハイライトを解除
            self.show_drop_feedback(False)
            
        except Exception as e:
            self.status_label.config(text=f"ドロップエラー: {str(e)}", fg="red")
    
    def _on_drag_enter(self, event):
        """ドラッグエンターイベントハンドラ"""
        self.show_drop_feedback(True)
    
    def _on_drag_leave(self, event):
        """ドラッグリーブイベントハンドラ"""
        self.show_drop_feedback(False)
    
    def set_managers(self, batch_manager, main_window):
        """マネージャー参照を設定"""
        self.batch_manager = batch_manager
        self.main_window = main_window
    
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