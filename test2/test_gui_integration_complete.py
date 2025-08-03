"""
完全なGUI統合テスト

GUIの全機能が正しく動作することをテストします。
"""

import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

# テスト対象のインポート
from models.preset import Preset
from models.batch_file import BatchFile
from services.preset_manager import PresetManager
from services.batch_manager import BatchManager
from services.workspace_manager import WorkspaceManager


class TestGUIIntegrationComplete(unittest.TestCase):
    """完全なGUI統合テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_workspace = tempfile.mkdtemp()
        self.preset_manager = PresetManager(os.path.join(self.test_workspace, "presets"))
        self.batch_manager = BatchManager(self.test_workspace)
        self.workspace_manager = WorkspaceManager()
        
        # サンプルプリセットを作成
        self.sample_preset = Preset(
            name="テスト用プリセット",
            fields=["陣営", "キャラ名"],
            naming_pattern="{陣営}_{キャラ名}_{番号}",
            id="TST001"
        )
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)
    
    def test_preset_panel_functionality(self):
        """PresetPanel機能テスト"""
        from gui.preset_panel import PresetPanel
        
        root = tk.Tk()
        try:
            # PresetPanelインスタンス作成
            preset_panel = PresetPanel(root)
            preset_panel.set_managers(self.preset_manager, Mock())
            
            # プリセット一覧表示テスト
            presets = [self.sample_preset]
            preset_panel.load_presets(presets)
            
            # リストボックスにデータが表示されることを確認
            self.assertEqual(preset_panel.preset_listbox.size(), 1)
            
            # プリセット選択テスト
            preset_panel.preset_listbox.selection_set(0)
            selection_handler = Mock()
            preset_panel.set_selection_handler(selection_handler)
            
            # 選択イベントをシミュレート
            event = Mock()
            preset_panel.on_preset_select(event)
            
            # ハンドラーが呼ばれることを確認
            selection_handler.assert_called_once()
            
        finally:
            root.destroy()
    
    def test_batch_panel_functionality(self):
        """BatchPanel機能テスト"""
        from gui.batch_panel import BatchPanel
        
        root = tk.Tk()
        try:
            # BatchPanelインスタンス作成
            batch_panel = BatchPanel(root)
            batch_panel.set_managers(self.batch_manager, Mock())
            
            # サンプルバッチファイルデータ
            sample_batches = [
                {
                    "filename": "TST001_テスト_キャラ.bat",
                    "created_at": "2024-01-01T10:00:00",
                    "size": "2"
                }
            ]
            
            # バッチファイル一覧表示テスト
            batch_panel.load_batch_files(sample_batches)
            self.assertEqual(batch_panel.batch_listbox.size(), 1)
            
            # 検索機能テスト
            batch_panel.search_entry.insert(0, "テスト")
            search_results = batch_panel.search_batch_files()
            self.assertEqual(len(search_results), 1)
            
            # 存在しないキーワードで検索
            batch_panel.search_entry.delete(0, tk.END)
            batch_panel.search_entry.insert(0, "存在しない")
            search_results = batch_panel.search_batch_files()
            self.assertEqual(len(search_results), 0)
            
        finally:
            root.destroy()
    
    def test_preset_wizard_functionality(self):
        """PresetWizard機能テスト"""
        from gui.preset_wizard import PresetWizard
        
        root = tk.Tk()
        try:
            # PresetWizardインスタンス作成
            wizard = PresetWizard(root)
            
            # ウィザードデータ設定テスト
            test_data = {
                "name": "テストプリセット",
                "fields": ["フィールド1", "フィールド2"],
                "naming_pattern": "{フィールド1}_{フィールド2}",
                "target_extensions": [".jpg", ".png"]
            }
            
            wizard.set_wizard_data(test_data)
            self.assertEqual(wizard.wizard_data["name"], "テストプリセット")
            
            # プリセット作成テスト
            created_preset = wizard.create_preset_from_wizard()
            self.assertIsNotNone(created_preset)
            self.assertEqual(created_preset.name, "テストプリセット")
            self.assertEqual(len(created_preset.fields), 2)
            
        finally:
            root.destroy()
    
    def test_dynamic_input_form_functionality(self):
        """DynamicInputForm機能テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            # DynamicInputFormインスタンス作成
            input_form = DynamicInputForm(root)
            input_form.set_managers(self.batch_manager, Mock())
            
            # プリセットからフォーム生成テスト
            input_form.generate_form_from_preset(self.sample_preset)
            
            # フィールドが生成されることを確認
            self.assertEqual(len(input_form.input_fields), 2)
            self.assertIn("陣営", input_form.input_fields)
            self.assertIn("キャラ名", input_form.input_fields)
            
            # フォームデータ設定テスト
            form_data = {"陣営": "テスト陣営", "キャラ名": "テストキャラ"}
            input_form.set_form_data(form_data)
            
            # 設定された値を確認
            self.assertEqual(input_form.input_fields["陣営"].get(), "テスト陣営")
            self.assertEqual(input_form.input_fields["キャラ名"].get(), "テストキャラ")
            
        finally:
            root.destroy()
    
    def test_workspace_integration(self):
        """ワークスペース統合テスト"""
        # ワークスペース初期化テスト
        result = self.workspace_manager.initialize_workspace(self.test_workspace)
        self.assertTrue(result.success)
        
        # 必要なディレクトリが作成されることを確認
        expected_dirs = ["presets", "rename_batches", "filter_batches", "display"]
        for dir_name in expected_dirs:
            dir_path = os.path.join(self.test_workspace, dir_name)
            self.assertTrue(os.path.exists(dir_path))
    
    def test_preset_manager_integration(self):
        """PresetManager統合テスト"""
        # プリセット保存テスト
        saved_path = self.preset_manager.save_preset(self.sample_preset)
        self.assertTrue(os.path.exists(saved_path))
        
        # プリセット一覧取得テスト
        presets = self.preset_manager.list_presets()
        self.assertEqual(len(presets), 1)
        self.assertEqual(presets[0].name, "テスト用プリセット")
        
        # プリセット削除テスト
        self.preset_manager.delete_preset(self.sample_preset.id)
        presets = self.preset_manager.list_presets()
        self.assertEqual(len(presets), 0)
    
    def test_batch_manager_integration(self):
        """BatchManager統合テスト"""
        # バッチファイル作成テスト
        values = {"陣営": "テスト陣営", "キャラ名": "テストキャラ"}
        batch_file = self.batch_manager.create_batch_file(self.sample_preset, values)
        
        self.assertEqual(batch_file.preset_id, "TST001")
        self.assertEqual(batch_file.field_values["陣営"], "テスト陣営")
        
        # バッチファイル保存テスト
        saved_path = self.batch_manager.save_batch_file(batch_file)
        self.assertTrue(os.path.exists(saved_path))
        
        # バッチファイル一覧取得テスト
        batch_files = self.batch_manager.load_batch_files()
        self.assertEqual(len(batch_files), 1)
        
        # バッチファイル削除テスト
        filename = batch_file.get_batch_filename()
        result = self.batch_manager.delete_batch_file(filename)
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_batch_execution(self, mock_subprocess):
        """バッチファイル実行テスト"""
        from gui.batch_panel import BatchPanel
        
        # subprocess.runのモック設定
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stderr = ""
        
        root = tk.Tk()
        try:
            batch_panel = BatchPanel(root)
            batch_panel.set_managers(self.batch_manager, Mock())
            
            # バッチファイル作成
            values = {"陣営": "テスト陣営", "キャラ名": "テストキャラ"}
            batch_file = self.batch_manager.create_batch_file(self.sample_preset, values)
            self.batch_manager.save_batch_file(batch_file)
            
            # バッチファイル一覧を読み込み
            batch_panel.refresh_batch_list()
            
            # リストボックスに項目があることを確認
            self.assertGreater(batch_panel.batch_listbox.size(), 0)
            
        finally:
            root.destroy()
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        from gui.preset_panel import PresetPanel
        
        root = tk.Tk()
        try:
            preset_panel = PresetPanel(root)
            
            # 無効なマネージャーでエラーハンドリングテスト
            preset_panel.set_managers(None, Mock())
            
            # プリセット削除時のエラーハンドリング
            with patch('tkinter.messagebox.showwarning') as mock_warning:
                preset_panel.delete_selected_preset()
                mock_warning.assert_called_once()
            
        finally:
            root.destroy()
    
    def test_data_persistence(self):
        """データ永続化テスト"""
        # プリセット保存
        self.preset_manager.save_preset(self.sample_preset)
        
        # 新しいインスタンスで読み込み
        new_preset_manager = PresetManager(os.path.join(self.test_workspace, "presets"))
        presets = new_preset_manager.list_presets()
        
        self.assertEqual(len(presets), 1)
        self.assertEqual(presets[0].name, "テスト用プリセット")


if __name__ == '__main__':
    unittest.main()