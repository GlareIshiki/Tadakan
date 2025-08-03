"""
作業ワークスペース管理のテスト

要件定義02.mdのFR-801〜FR-805に基づく失敗するテストを記述
- デフォルトワークスペース：ピクチャ/Tadakan（自動作成）
- サブフォルダ自動作成：rename_batches、filter_batches、display
- ワークスペースパスGUI切替機能
- フォルダ構造初期化と自動修復機能
- ワークスペースバックアップ・復元機能
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from src.services.workspace_manager import WorkspaceManager
from src.models.workspace import Workspace


class TestWorkspaceModel(unittest.TestCase):
    """Workspaceモデルのテスト"""
    
    def test_workspace_creation(self):
        """Workspaceオブジェクトの作成をテスト"""
        # 失敗するテスト：Workspaceクラスが未実装
        workspace = Workspace(
            name="テストワークスペース",
            path="C:/Users/Test/Pictures/Tadakan",
            auto_create_folders=True
        )
        
        # 基本属性の確認
        self.assertEqual(workspace.name, "テストワークスペース")
        self.assertEqual(workspace.path, "C:/Users/Test/Pictures/Tadakan")
        self.assertTrue(workspace.auto_create_folders)
    
    def test_required_subfolder_structure(self):
        """必須サブフォルダ構造をテスト"""
        # 失敗するテスト：get_required_subfoldersメソッドが未実装
        workspace = Workspace("テスト", "C:/test")
        
        required_folders = workspace.get_required_subfolders()
        expected_folders = ["rename_batches", "filter_batches", "display"]
        
        self.assertEqual(set(required_folders), set(expected_folders))
    
    def test_workspace_validation(self):
        """ワークスペースバリデーションをテスト"""
        # 失敗するテスト：validateメソッドが未実装
        workspace = Workspace("テスト", "C:/test")
        
        # 存在しないパスの場合
        validation_result = workspace.validate()
        self.assertFalse(validation_result.is_valid)
        self.assertIn("path_not_exists", validation_result.errors)
        
        # 書き込み権限がない場合のテスト（モック）
        with patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=False):
            validation_result = workspace.validate()
            self.assertFalse(validation_result.is_valid)
            self.assertIn("no_write_permission", validation_result.errors)


class TestWorkspaceManager(unittest.TestCase):
    """WorkspaceManagerのテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_manager = WorkspaceManager()
    
    def tearDown(self):
        """テスト後清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_default_workspace_path(self):
        """デフォルトワークスペースパス取得をテスト"""
        # 失敗するテスト：get_default_workspace_pathメソッドが未実装
        default_path = self.workspace_manager.get_default_workspace_path()
        
        # Windows環境でのデフォルトパス確認
        expected = os.path.join(os.path.expanduser("~"), "Pictures", "Tadakan")
        self.assertEqual(default_path, expected)
    
    def test_initialize_workspace(self):
        """ワークスペース初期化をテスト"""
        # 失敗するテスト：initialize_workspaceメソッドが未実装
        workspace_path = os.path.join(self.temp_dir, "Tadakan")
        
        result = self.workspace_manager.initialize_workspace(workspace_path)
        
        # ワークスペースが作成されることをテスト
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(workspace_path))
        
        # 必須サブフォルダが作成されることをテスト
        self.assertTrue(os.path.exists(os.path.join(workspace_path, "rename_batches")))
        self.assertTrue(os.path.exists(os.path.join(workspace_path, "filter_batches")))
        self.assertTrue(os.path.exists(os.path.join(workspace_path, "display")))
    
    def test_auto_repair_workspace(self):
        """ワークスペース自動修復をテスト"""
        # 失敗するテスト：auto_repair_workspaceメソッドが未実装
        workspace_path = os.path.join(self.temp_dir, "Tadakan")
        os.makedirs(workspace_path)
        
        # rename_batchesフォルダのみ作成（他は欠損状態）
        os.makedirs(os.path.join(workspace_path, "rename_batches"))
        
        # 自動修復実行
        repair_result = self.workspace_manager.auto_repair_workspace(workspace_path)
        
        # 欠損フォルダが復旧されることをテスト
        self.assertTrue(repair_result.success)
        self.assertTrue(os.path.exists(os.path.join(workspace_path, "filter_batches")))
        self.assertTrue(os.path.exists(os.path.join(workspace_path, "display")))
        
        # 修復ログが記録されることをテスト
        self.assertIn("filter_batches", repair_result.repaired_items)
        self.assertIn("display", repair_result.repaired_items)
    
    def test_workspace_switching(self):
        """ワークスペース切替をテスト"""
        # 失敗するテスト：switch_workspaceメソッドが未実装
        old_workspace = os.path.join(self.temp_dir, "OldTadakan")
        new_workspace = os.path.join(self.temp_dir, "NewTadakan")
        
        # 両方のワークスペースを初期化
        self.workspace_manager.initialize_workspace(old_workspace)
        self.workspace_manager.initialize_workspace(new_workspace)
        
        # 最初のワークスペースを設定
        self.workspace_manager.set_current_workspace(old_workspace)
        self.assertEqual(self.workspace_manager.current_workspace.path, old_workspace)
        
        # ワークスペース切替
        switch_result = self.workspace_manager.switch_workspace(new_workspace)
        
        # 切替が成功することをテスト
        self.assertTrue(switch_result.success)
        self.assertEqual(self.workspace_manager.current_workspace.path, new_workspace)
    
    def test_workspace_backup_creation(self):
        """ワークスペースバックアップ作成をテスト"""
        # 失敗するテスト：create_backupメソッドが未実装
        workspace_path = os.path.join(self.temp_dir, "Tadakan")
        self.workspace_manager.initialize_workspace(workspace_path)
        
        # テスト用ファイル作成
        with open(os.path.join(workspace_path, "rename_batches", "test.bat"), 'w') as f:
            f.write("@echo off\necho test")
        
        # バックアップ作成
        backup_result = self.workspace_manager.create_backup(workspace_path)
        
        # バックアップが作成されることをテスト
        self.assertTrue(backup_result.success)
        self.assertTrue(os.path.exists(backup_result.backup_path))
        
        # バックアップ内容の確認
        backup_files = os.listdir(backup_result.backup_path)
        self.assertIn("rename_batches", backup_files)
    
    def test_workspace_restoration(self):
        """ワークスペース復元をテスト"""
        # 失敗するテスト：restore_from_backupメソッドが未実装
        workspace_path = os.path.join(self.temp_dir, "Tadakan")
        self.workspace_manager.initialize_workspace(workspace_path)
        
        # バックアップ作成
        backup_result = self.workspace_manager.create_backup(workspace_path)
        
        # ワークスペースを破損状態にする
        shutil.rmtree(os.path.join(workspace_path, "rename_batches"))
        
        # バックアップから復元
        restore_result = self.workspace_manager.restore_from_backup(
            workspace_path, backup_result.backup_path
        )
        
        # 復元が成功することをテスト
        self.assertTrue(restore_result.success)
        self.assertTrue(os.path.exists(os.path.join(workspace_path, "rename_batches")))
    
    def test_workspace_health_check(self):
        """ワークスペースヘルスチェックをテスト"""
        # 失敗するテスト：perform_health_checkメソッドが未実装
        workspace_path = os.path.join(self.temp_dir, "Tadakan")
        self.workspace_manager.initialize_workspace(workspace_path)
        
        # ヘルスチェック実行
        health_result = self.workspace_manager.perform_health_check(workspace_path)
        
        # 健全なワークスペースの場合
        self.assertTrue(health_result.is_healthy)
        self.assertEqual(len(health_result.issues), 0)
        
        # フォルダを削除して再チェック
        shutil.rmtree(os.path.join(workspace_path, "display"))
        health_result = self.workspace_manager.perform_health_check(workspace_path)
        
        # 問題が検出されることをテスト
        self.assertFalse(health_result.is_healthy)
        self.assertTrue(len(health_result.issues) > 0)
        self.assertIn("missing_display_folder", [issue.type for issue in health_result.issues])


class TestWorkspaceConfiguration(unittest.TestCase):
    """ワークスペース設定のテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_manager = WorkspaceManager()
    
    def tearDown(self):
        """テスト後清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_workspace_settings_persistence(self):
        """ワークスペース設定の永続化をテスト"""
        # 失敗するテスト：save_workspace_settingsメソッドが未実装
        workspace_path = os.path.join(self.temp_dir, "Tadakan")
        
        settings = {
            "workspace_name": "マイワークスペース",
            "auto_backup": True,
            "backup_interval_days": 7,
            "max_backup_count": 10,
            "auto_repair": True
        }
        
        # 設定保存
        self.workspace_manager.save_workspace_settings(workspace_path, settings)
        
        # 設定読み込み
        loaded_settings = self.workspace_manager.load_workspace_settings(workspace_path)
        
        # 設定が正しく保存・読み込みされることをテスト
        self.assertEqual(loaded_settings["workspace_name"], "マイワークスペース")
        self.assertTrue(loaded_settings["auto_backup"])
        self.assertEqual(loaded_settings["backup_interval_days"], 7)
    
    def test_workspace_migration(self):
        """ワークスペース移行をテスト"""
        # 失敗するテスト：migrate_workspaceメソッドが未実装
        old_path = os.path.join(self.temp_dir, "OldTadakan")
        new_path = os.path.join(self.temp_dir, "NewTadakan")
        
        # 古いワークスペース初期化
        self.workspace_manager.initialize_workspace(old_path)
        
        # テストデータ追加
        with open(os.path.join(old_path, "rename_batches", "test.bat"), 'w') as f:
            f.write("test content")
        
        # ワークスペース移行
        migration_result = self.workspace_manager.migrate_workspace(old_path, new_path)
        
        # 移行が成功することをテスト
        self.assertTrue(migration_result.success)
        self.assertTrue(os.path.exists(new_path))
        self.assertTrue(os.path.exists(os.path.join(new_path, "rename_batches", "test.bat")))
        
        # 元のワークスペースが保持されることをテスト（コピー移行の場合）
        self.assertTrue(os.path.exists(old_path))
    
    def test_multiple_workspace_management(self):
        """複数ワークスペース管理をテスト"""
        # 失敗するテスト：get_workspace_listメソッドが未実装
        workspace1 = os.path.join(self.temp_dir, "Workspace1")
        workspace2 = os.path.join(self.temp_dir, "Workspace2")
        
        # 複数ワークスペース作成
        self.workspace_manager.initialize_workspace(workspace1)
        self.workspace_manager.initialize_workspace(workspace2)
        
        # ワークスペース一覧取得
        workspace_list = self.workspace_manager.get_workspace_list()
        
        # 複数ワークスペースが管理されることをテスト
        self.assertTrue(len(workspace_list) >= 2)
        workspace_paths = [ws.path for ws in workspace_list]
        self.assertIn(workspace1, workspace_paths)
        self.assertIn(workspace2, workspace_paths)


class TestWorkspaceGUIIntegration(unittest.TestCase):
    """ワークスペースGUI統合のテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """テスト後清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_workspace_selector_dialog(self):
        """ワークスペース選択ダイアログをテスト"""
        # 失敗するテスト：WorkspaceSelectorDialogクラスが未実装
        from src.gui.workspace_selector import WorkspaceSelectorDialog
        
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        try:
            dialog = WorkspaceSelectorDialog(root)
            
            # ダイアログの基本コンポーネント確認
            self.assertIsNotNone(dialog.workspace_listbox)
            self.assertIsNotNone(dialog.browse_button)
            self.assertIsNotNone(dialog.create_new_button)
            
        finally:
            root.destroy()
    
    def test_workspace_settings_dialog(self):
        """ワークスペース設定ダイアログをテスト"""
        # 失敗するテスト：WorkspaceSettingsDialogクラスが未実装
        from src.gui.workspace_settings import WorkspaceSettingsDialog
        
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        try:
            dialog = WorkspaceSettingsDialog(root)
            
            # 設定項目の確認
            self.assertIsNotNone(dialog.name_entry)
            self.assertIsNotNone(dialog.auto_backup_check)
            self.assertIsNotNone(dialog.backup_interval_spinbox)
            
        finally:
            root.destroy()
    
    def test_workspace_status_indicator(self):
        """ワークスペース状態インジケーターをテスト"""
        # 失敗するテスト：WorkspaceStatusIndicatorクラスが未実装
        from src.gui.components.workspace_status import WorkspaceStatusIndicator
        
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        try:
            indicator = WorkspaceStatusIndicator(root)
            
            # 正常状態の表示
            indicator.show_status("healthy", "ワークスペースは正常です")
            self.assertEqual(indicator.current_status, "healthy")
            
            # 警告状態の表示
            indicator.show_status("warning", "一部フォルダが見つかりません")
            self.assertEqual(indicator.current_status, "warning")
            
        finally:
            root.destroy()


if __name__ == '__main__':
    unittest.main()