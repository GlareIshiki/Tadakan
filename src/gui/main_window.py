"""
メインウィンドウ

統合GUIインターフェースのメインウィンドウ
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import os

from gui.preset_panel import PresetPanel
from gui.input_form import DynamicInputForm
from gui.batch_panel import BatchPanel
from gui.drop_zone import DropZone
from services.workspace_manager import WorkspaceManager
from services.preset_manager import PresetManager
from services.batch_manager import BatchManager
from models.preset import Preset

# tkinterdnd2のインポート
try:
    from tkinterdnd2 import TkinterDnD
    TKINTERDND_AVAILABLE = True
except ImportError:
    TKINTERDND_AVAILABLE = False


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self, root: tk.Tk, workspace_path: Optional[str] = None):
        # tkinterdnd2でTkinterDnDに変換
        if TKINTERDND_AVAILABLE:
            self.root = TkinterDnD.Tk() if not isinstance(root, TkinterDnD.Tk) else root
        else:
            self.root = root
            
        self.root.title("Tadakan - フルGUI版")
        self.root.geometry("1000x700")  # 適切なウィンドウサイズを設定
        self.root.minsize(800, 600)     # 最小サイズを設定
        
        # ワークスペース管理
        self.workspace_manager = WorkspaceManager()
        self.current_workspace = None
        self.workspace_initialized = False
        
        # サービスマネージャーインスタンス
        self.preset_manager = None
        self.batch_manager = None
        
        # 初期化
        self._initialize_workspace(workspace_path)
        self._initialize_managers()
        self._create_components()
        self.setup_layout()
        self._load_initial_data()
    
    def _initialize_workspace(self, workspace_path: Optional[str] = None):
        """ワークスペースの初期化"""
        try:
            if workspace_path:
                target_path = workspace_path
            else:
                target_path = self.workspace_manager.get_default_workspace_path()
            
            result = self.workspace_manager.initialize_workspace(target_path)
            if result.success:
                self.workspace_manager.set_current_workspace(target_path)
                self.current_workspace = self.workspace_manager.current_workspace
                self.workspace_initialized = True
                self.current_workspace_path = target_path
        except Exception:
            self.workspace_initialized = False
    
    def _initialize_managers(self):
        """サービスマネージャーを初期化"""
        try:
            if self.workspace_initialized:
                # ワークスペース内のプリセットディレクトリを指定
                presets_dir = os.path.join(self.current_workspace_path, "presets")
                self.preset_manager = PresetManager(presets_dir)
                self.batch_manager = BatchManager(self.current_workspace_path)
            else:
                # デフォルトのプリセットディレクトリを使用
                self.preset_manager = PresetManager()
                self.batch_manager = BatchManager()
        except Exception as e:
            messagebox.showerror("初期化エラー", f"サービスマネージャーの初期化に失敗しました: {str(e)}")
    
    def _create_components(self):
        """GUIコンポーネントを作成"""
        # プリセット管理パネル
        self.preset_panel = PresetPanel(self.root)
        self.preset_panel.set_selection_handler(self.on_preset_selected)
        
        # 動的入力フォーム
        self.input_form = DynamicInputForm(self.root)
        
        # バッチファイル管理パネル
        self.batch_panel = BatchPanel(self.root)
        
        # ドロップゾーン
        self.drop_zone = DropZone(self.root)
        
        # ワークスペースパス表示ラベル
        self.workspace_path_label = tk.Label(self.root, text="ワークスペース: 未設定")
        
        # 初期表示更新
        if self.workspace_initialized:
            self.workspace_path_label.config(text=f"ワークスペース: {self.current_workspace_path}")
        
        # 初期コンポーネント作成時のマネージャー設定は setup_layout で行う
    
    def setup_layout(self):
        """レイアウトを設定"""
        # ワークスペースパス表示（上部）
        self.workspace_path_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左側フレーム（プリセット専用）
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 中央フレーム（入力フォーム専用）
        center_frame = ttk.Frame(main_frame, width=300)
        center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        center_frame.pack_propagate(False)
        
        # プリセットパネルを左側フレームに再配置
        print("[MainWindow] PresetPanel配置開始")
        self.preset_panel.pack_forget()
        self.preset_panel = PresetPanel(left_frame)
        self.preset_panel.set_selection_handler(self.on_preset_selected)
        
        # マネージャー参照を渡す
        print(f"[MainWindow] マネージャー設定 - preset_manager: {self.preset_manager is not None}")
        self.preset_panel.set_managers(self.preset_manager, self)
        
        # パネルを配置
        self.preset_panel.pack(fill=tk.BOTH, expand=True)
        print("[MainWindow] PresetPanel配置完了")
        
        # 強制的にレイアウトを更新
        left_frame.update_idletasks()
        
        # 入力フォームを中央フレームに再配置
        self.input_form.pack_forget()
        self.input_form = DynamicInputForm(center_frame)
        # マネージャー参照を渡す
        self.input_form.set_managers(self.batch_manager, self)
        self.input_form.pack(fill=tk.BOTH, expand=True)
        
        # 右側フレーム（バッチ管理 + ドロップゾーン）
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # バッチパネルを右側フレームに再配置
        self.batch_panel.pack_forget()
        self.batch_panel = BatchPanel(right_frame)
        # マネージャー参照を渡す
        self.batch_panel.set_managers(self.batch_manager, self)
        self.batch_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # ドロップゾーンを右側フレームに再配置
        self.drop_zone.pack_forget()
        self.drop_zone = DropZone(right_frame)
        # マネージャー参照を渡す
        self.drop_zone.set_managers(self.batch_manager, self)
        self.drop_zone.pack(fill=tk.X, pady=(0, 5))
    
    def on_preset_selected(self, preset: Preset):
        """プリセット選択時のハンドラ"""
        # 動的入力フォームを更新
        self.input_form.generate_form_from_preset(preset)
        self.input_form.current_preset = preset
        
        # バッチパネルにプリセット情報を反映
        self.batch_panel.current_preset = preset
    
    def switch_workspace(self, new_workspace_path: str):
        """ワークスペースを切り替え"""
        result = self.workspace_manager.switch_workspace(new_workspace_path)
        if result.success:
            self.current_workspace_path = new_workspace_path
            self.current_workspace = self.workspace_manager.current_workspace
            if hasattr(self, 'workspace_path_label'):
                self.workspace_path_label.config(text=f"ワークスペース: {new_workspace_path}")
        return result
    
    def get_displayed_workspace_path(self) -> str:
        """表示中のワークスペースパスを取得"""
        return getattr(self, 'current_workspace_path', "")
    
    def _load_initial_data(self):
        """初期データを読み込み"""
        print("[MainWindow] 初期データ読み込み開始")
        
        try:
            # PresetPanel状態確認
            print(f"[MainWindow] PresetPanel存在: {hasattr(self, 'preset_panel')}")
            if hasattr(self, 'preset_panel'):
                print(f"[MainWindow] PresetPanel表示: {self.preset_panel.winfo_viewable()}")
                print(f"[MainWindow] PresetManagerの設定: {self.preset_panel.preset_manager is not None}")
            
            # プリセット一覧の読み込み
            if hasattr(self, 'preset_panel'):
                print("[MainWindow] プリセット一覧読み込み中...")
                self.preset_panel.refresh_preset_list()
            else:
                print("[MainWindow] PresetPanelが存在しません")
            
            # バッチファイル一覧の読み込み
            if hasattr(self, 'batch_panel') and self.batch_manager:
                print("[MainWindow] バッチファイル一覧読み込み中...")
                self.batch_panel.refresh_batch_list()
            
            print("[MainWindow] 初期データ読み込み完了")
                
        except Exception as e:
            print(f"初期データ読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_all_data(self):
        """全データを再読み込み"""
        self._load_initial_data()
    
    def on_preset_created(self, preset: Preset):
        """プリセット作成完了時のコールバック"""
        if hasattr(self, 'preset_panel'):
            self.preset_panel.refresh_preset_list()
    
    def on_batch_created(self, batch_file):
        """バッチファイル作成完了時のコールバック"""
        if hasattr(self, 'batch_panel'):
            self.batch_panel.refresh_batch_list()