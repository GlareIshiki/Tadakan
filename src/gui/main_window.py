"""
メインウィンドウ

統合GUIインターフェースのメインウィンドウ
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.gui.preset_panel import PresetPanel
from src.gui.input_form import DynamicInputForm
from src.gui.batch_panel import BatchPanel
from src.gui.drop_zone import DropZone
from src.services.workspace_manager import WorkspaceManager
from src.models.preset import Preset


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tadakan - フルGUI版")
        
        # ワークスペース管理
        self.workspace_manager = WorkspaceManager()
        self.current_workspace = None
        self.workspace_initialized = False
        
        # 初期化
        self._initialize_workspace()
        self._create_components()
        self.setup_layout()
    
    def _initialize_workspace(self):
        """ワークスペースの初期化"""
        try:
            default_path = self.workspace_manager.get_default_workspace_path()
            result = self.workspace_manager.initialize_workspace(default_path)
            if result.success:
                self.workspace_manager.set_current_workspace(default_path)
                self.current_workspace = self.workspace_manager.current_workspace
                self.workspace_initialized = True
                self.current_workspace_path = default_path
        except Exception:
            self.workspace_initialized = False
    
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
    
    def setup_layout(self):
        """レイアウトを設定"""
        # ワークスペースパス表示（上部）
        self.workspace_path_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左側フレーム（プリセット + 入力フォーム）
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        
        # プリセットパネル
        self.preset_panel.pack(in_=left_frame, fill=tk.BOTH, expand=True)
        
        # 入力フォーム
        self.input_form.pack(in_=left_frame, fill=tk.X, pady=5)
        
        # 右側フレーム（バッチ管理 + ドロップゾーン）
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # バッチパネル
        self.batch_panel.pack(in_=right_frame, fill=tk.BOTH, expand=True)
        
        # ドロップゾーン
        self.drop_zone.pack(in_=right_frame, fill=tk.X, pady=5)
    
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