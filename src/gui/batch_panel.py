"""
バッチファイル管理パネル

バッチファイルの一覧・検索・削除・実行機能を提供
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Dict, Any, Optional
import os
import subprocess
import threading
import queue
from datetime import datetime

from src.models.preset import Preset


class BatchPanel(ttk.Frame):
    """バッチファイル管理パネル"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.current_preset: Optional[Preset] = None
        self._drag_drop_enabled = False
        self.batch_manager = None
        self.main_window = None
        self._batch_files_data = []  # 実際のバッチファイルデータを保存
        self._execution_thread = None  # 実行スレッド
        self._log_queue = queue.Queue()  # ログメッセージキュー
        self._is_executing = False  # 実行中フラグ
        self._create_widgets()
        self._setup_layout()
        self._start_log_monitor()
    
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
        self.stop_button = ttk.Button(button_frame, text="停止", state=tk.DISABLED,
                                     command=self._on_stop_execution)
        
        # 実行ログ表示エリア
        log_frame = ttk.LabelFrame(self, text="実行ログ")
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=50,
                                                 wrap=tk.WORD, state=tk.DISABLED)
        self.clear_log_button = ttk.Button(log_frame, text="ログクリア",
                                          command=self._clear_log)
        
        # ステータス表示
        status_frame = ttk.Frame(self)
        self.status_label = ttk.Label(status_frame, text="待機中", 
                                     foreground="green")
        
        # 実行中インジケーター（スピナー）
        self.spinner_label = ttk.Label(status_frame, text="", foreground="orange")
        self._spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._spinner_index = 0
        self._spinner_active = False
        
        # フレーム参照を保存
        self.search_frame = search_frame
        self.list_frame = list_frame
        self.button_frame = button_frame
        self.log_frame = log_frame
        self.status_frame = status_frame
        self.scrollbar = scrollbar
    
    def _setup_layout(self):
        """レイアウトを設定"""
        # タイトルラベル
        title_label = ttk.Label(self, text="バッチファイル管理", font=("Arial", 10, "bold"))
        title_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # 検索フレーム（上部）
        self.search_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # リストフレーム（中央）
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.batch_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ボタンフレーム（中間）
        self.button_frame.pack(fill=tk.X, padx=5, pady=2)
        self.delete_button.pack(side=tk.LEFT, padx=2)
        self.execute_button.pack(side=tk.LEFT, padx=2)
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        # ステータスフレーム
        self.status_frame.pack(fill=tk.X, padx=5, pady=2)
        self.status_label.pack(side=tk.LEFT)
        self.spinner_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # ログフレーム（下部）
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.clear_log_button.pack(side=tk.RIGHT, pady=(0, 5))
    
    def load_batch_files(self, batch_files: List[Dict[str, Any]]):
        """バッチファイル一覧を読み込み"""
        self.batch_listbox.delete(0, tk.END)
        self._batch_files_data = batch_files
        
        for batch_data in batch_files:
            filename = batch_data.get("filename", "")
            created_at = batch_data.get("created_at", "")
            file_size = batch_data.get("size", "")
            
            display_text = filename
            if created_at:
                display_text += f" ({created_at[:10]})"
            if file_size:
                display_text += f" [{file_size}KB]"
            
            self.batch_listbox.insert(tk.END, display_text)
    
    def search_batch_files(self, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """バッチファイルを検索"""
        if search_term is None:
            search_term = self.search_entry.get().strip()
        
        if not search_term:
            return self._batch_files_data
        
        # 検索条件でフィルタリング
        results = []
        for batch_data in self._batch_files_data:
            filename = batch_data.get("filename", "").lower()
            if search_term.lower() in filename:
                results.append(batch_data)
        
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
    
    def set_managers(self, batch_manager, main_window):
        """マネージャー参照を設定"""
        self.batch_manager = batch_manager
        self.main_window = main_window
    
    def _on_search_changed(self, event):
        """検索文字列変更時のハンドラ"""
        try:
            # リアルタイム検索実行
            search_results = self.search_batch_files()
            self.load_batch_files(search_results)
        except Exception as e:
            print(f"検索エラー: {e}")
    
    def _on_delete_selected(self):
        """選択されたバッチファイルを削除"""
        selection = self.batch_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除するバッチファイルを選択してください。")
            return
        
        index = selection[0]
        if 0 <= index < len(self._batch_files_data):
            selected_batch = self._batch_files_data[index]
            filename = selected_batch.get("filename", "")
            
            # 削除確認
            result = messagebox.askyesno(
                "削除確認",
                f"バッチファイル '{filename}' を削除しますか？\n"
                f"この操作は元に戻せません。"
            )
            
            if result and self.batch_manager:
                try:
                    success = self.batch_manager.delete_batch_file(filename)
                    if success:
                        self.refresh_batch_list()
                        messagebox.showinfo("完了", "バッチファイルを削除しました。")
                    else:
                        messagebox.showerror("エラー", "バッチファイルの削除に失敗しました。")
                except Exception as e:
                    messagebox.showerror("エラー", f"削除中にエラーが発生しました: {str(e)}")
    
    def _on_execute_selected(self):
        """選択されたバッチファイルを実行"""
        if self._is_executing:
            messagebox.showwarning("警告", "既に実行中です。停止してから再実行してください。")
            return
            
        selection = self.batch_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "実行するバッチファイルを選択してください。")
            return
        
        index = selection[0]
        if 0 <= index < len(self._batch_files_data):
            selected_batch = self._batch_files_data[index]
            filename = selected_batch.get("filename", "")
            
            # 実行確認
            result = messagebox.askyesno(
                "実行確認",
                f"バッチファイル '{filename}' を実行しますか？\n"
                f"ファイル操作が実行されます。"
            )
            
            if result and self.batch_manager:
                # バッチファイルのフルパスを取得
                batch_path = os.path.join(
                    self.batch_manager.workspace_path, 
                    "rename_batches", 
                    filename
                )
                
                if not os.path.exists(batch_path):
                    messagebox.showerror("エラー", f"バッチファイルが見つかりません: {batch_path}")
                    return
                
                # 非同期で実行
                self._start_batch_execution(batch_path, filename)
    
    def _start_batch_execution(self, batch_path: str, filename: str):
        """バッチファイル実行を開始"""
        self._is_executing = True
        self._update_execution_state(True)
        
        # ログをクリア
        self._add_log(f"=== バッチファイル実行開始: {filename} ===")
        self._add_log(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._add_log(f"ファイルパス: {batch_path}")
        self._add_log("")
        
        # 別スレッドで実行
        self._execution_thread = threading.Thread(
            target=self._execute_batch_in_thread,
            args=(batch_path, filename),
            daemon=True
        )
        self._execution_thread.start()
    
    def _execute_batch_in_thread(self, batch_path: str, filename: str):
        """別スレッドでバッチファイルを実行"""
        try:
            # プロセス実行（最も安全なcmd.exe経由で実行）
            self._log_queue.put(('info', f"cmd.exe経由でバッチファイルを実行: {filename}"))
            
            process = subprocess.Popen(
                ['cmd.exe', '/c', batch_path],  # リスト形式、手動クオートなし
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(batch_path),
                encoding='cp932',  # Windows標準エンコーディング
                errors='replace',
                shell=False  # shellを使わない
            )
            
            # 並行出力読み取り（PIPEバッファ詰まりを防ぐ）
            def read_stdout():
                """標準出力を読み取り"""
                try:
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            self._log_queue.put(('stdout', line.strip()))
                        if process.poll() is not None:
                            break
                except Exception as e:
                    self._log_queue.put(('error', f"標準出力読み取りエラー: {str(e)}"))
                finally:
                    if process.stdout:
                        process.stdout.close()
            
            def read_stderr():
                """標準エラー出力を読み取り"""
                try:
                    for line in iter(process.stderr.readline, ''):
                        if line:
                            self._log_queue.put(('stderr', line.strip()))
                        if process.poll() is not None:
                            break
                except Exception as e:
                    self._log_queue.put(('error', f"エラー出力読み取りエラー: {str(e)}"))
                finally:
                    if process.stderr:
                        process.stderr.close()
            
            # 並行読み取りスレッドを開始
            import threading
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()
            
            # プロセス完了を待機
            process.wait()
            
            # 読み取りスレッドの完了を待機（最大5秒）
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            
            # 実行結果
            return_code = process.poll()
            
            # 完了メッセージ
            if return_code == 0:
                self._log_queue.put(('info', f"実行完了: {filename} (終了コード: {return_code})"))
                self._log_queue.put(('success', "バッチファイルの実行が正常に完了しました。"))
            else:
                self._log_queue.put(('error', f"実行エラー: {filename} (終了コード: {return_code})"))
                self._log_queue.put(('error', "バッチファイルの実行中にエラーが発生しました。"))
            
        except Exception as e:
            self._log_queue.put(('error', f"実行中に例外が発生: {str(e)}"))
        
        finally:
            # 実行完了
            self._log_queue.put(('status', 'completed'))
    
    def _on_stop_execution(self):
        """実行を停止"""
        if self._execution_thread and self._execution_thread.is_alive():
            # スレッドの強制終了（プロセスの終了は困難なため警告表示）
            self._add_log("停止要求を受信しました。")
            self._add_log("注意: 実行中のバッチプロセスは継続される可能性があります。")
            
        self._is_executing = False
        self._update_execution_state(False)
        self._add_log("実行停止しました。")
    
    def _update_execution_state(self, is_executing: bool):
        """実行状態に応じてUIを更新"""
        if is_executing:
            # 実行関連ボタンを無効化
            self.execute_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 他のパネルへの影響を防ぐため、MainWindow経由でUI制御
            if self.main_window:
                self._disable_other_ui_elements()
            
            self.status_label.config(text="実行中...", foreground="orange")
            self._start_spinner()
        else:
            # ボタンを再有効化
            self.execute_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # 他のパネルを再有効化
            if self.main_window:
                self._enable_other_ui_elements()
                
            self.status_label.config(text="待機中", foreground="green")
            self._stop_spinner()
    
    def _start_log_monitor(self):
        """ログキューを監視してUIに反映"""
        try:
            while True:
                try:
                    log_type, message = self._log_queue.get_nowait()
                    
                    if log_type == 'status':
                        if message == 'completed':
                            self._is_executing = False
                            self._update_execution_state(False)
                    elif log_type == 'stdout':
                        self._add_log(f"[OUT] {message}")
                    elif log_type == 'stderr':
                        self._add_log(f"[ERR] {message}")
                    elif log_type == 'info':
                        self._add_log(f"[INFO] {message}")
                    elif log_type == 'success':
                        self._add_log(f"[SUCCESS] {message}")
                    elif log_type == 'error':
                        self._add_log(f"[ERROR] {message}")
                    else:
                        self._add_log(message)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"ログ監視エラー: {e}")
        
        # 100msごとに再実行
        self.after(100, self._start_log_monitor)
    
    def _add_log(self, message: str):
        """ログメッセージを追加"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)  # 最下部にスクロール
        self.log_text.config(state=tk.DISABLED)
    
    def _clear_log(self):
        """ログをクリア"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _disable_other_ui_elements(self):
        """他のUI要素を無効化（実行中の状態不整合を防ぐ）"""
        try:
            # プリセットパネルのボタンを無効化
            if hasattr(self.main_window, 'preset_panel'):
                preset_panel = self.main_window.preset_panel
                if hasattr(preset_panel, 'create_button'):
                    preset_panel.create_button.config(state=tk.DISABLED)
                if hasattr(preset_panel, 'wizard_button'):
                    preset_panel.wizard_button.config(state=tk.DISABLED)
                if hasattr(preset_panel, 'edit_button'):
                    preset_panel.edit_button.config(state=tk.DISABLED)
                if hasattr(preset_panel, 'delete_button'):
                    preset_panel.delete_button.config(state=tk.DISABLED)
                # プリセット選択も無効化
                if hasattr(preset_panel, 'preset_listbox'):
                    preset_panel.preset_listbox.config(state=tk.DISABLED)
            
            # 入力フォームを無効化
            if hasattr(self.main_window, 'input_form'):
                input_form = self.main_window.input_form
                if hasattr(input_form, 'disable_form'):
                    input_form.disable_form()
                
        except Exception as e:
            print(f"UI無効化エラー: {e}")
    
    def _enable_other_ui_elements(self):
        """他のUI要素を再有効化"""
        try:
            # プリセットパネルのボタンを再有効化
            if hasattr(self.main_window, 'preset_panel'):
                preset_panel = self.main_window.preset_panel
                if hasattr(preset_panel, 'create_button'):
                    preset_panel.create_button.config(state=tk.NORMAL)
                if hasattr(preset_panel, 'wizard_button'):
                    preset_panel.wizard_button.config(state=tk.NORMAL)
                if hasattr(preset_panel, 'edit_button'):
                    preset_panel.edit_button.config(state=tk.NORMAL)
                if hasattr(preset_panel, 'delete_button'):
                    preset_panel.delete_button.config(state=tk.NORMAL)
                # プリセット選択も再有効化
                if hasattr(preset_panel, 'preset_listbox'):
                    preset_panel.preset_listbox.config(state=tk.NORMAL)
            
            # 入力フォームを再有効化
            if hasattr(self.main_window, 'input_form'):
                input_form = self.main_window.input_form
                if hasattr(input_form, 'enable_form'):
                    input_form.enable_form()
                    
        except Exception as e:
            print(f"UI再有効化エラー: {e}")
    
    def _start_spinner(self):
        """スピナーアニメーションを開始"""
        self._spinner_active = True
        self._update_spinner()
    
    def _stop_spinner(self):
        """スピナーアニメーションを停止"""
        self._spinner_active = False
        self.spinner_label.config(text="")
    
    def _update_spinner(self):
        """スピナーを更新"""
        if self._spinner_active:
            self.spinner_label.config(text=self._spinner_chars[self._spinner_index])
            self._spinner_index = (self._spinner_index + 1) % len(self._spinner_chars)
            # 200msごとに更新
            self.after(200, self._update_spinner)
    
    def refresh_batch_list(self):
        """バッチファイル一覧を再読み込み"""
        if self.batch_manager:
            try:
                batch_files = self.batch_manager.load_batch_files()
                
                # ファイル情報を詳細化
                detailed_batch_files = []
                rename_batches_dir = os.path.join(self.batch_manager.workspace_path, "rename_batches")
                
                for batch_file in batch_files:
                    filename = batch_file.get_batch_filename()
                    file_path = os.path.join(rename_batches_dir, filename)
                    
                    batch_info = {
                        "filename": filename,
                        "created_at": batch_file.created_at.isoformat() if hasattr(batch_file, 'created_at') else "",
                        "size": ""
                    }
                    
                    # ファイルサイズを取得
                    if os.path.exists(file_path):
                        size_bytes = os.path.getsize(file_path)
                        batch_info["size"] = f"{size_bytes // 1024}"
                    
                    detailed_batch_files.append(batch_info)
                
                self.load_batch_files(detailed_batch_files)
                
            except Exception as e:
                print(f"バッチファイル一覧の読み込みエラー: {e}")
                # エラー時は空のリストを表示
                self.load_batch_files([])