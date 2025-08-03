"""
DropZone機能テスト

ドラッグ&ドロップ機能のテストケース
"""

import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

from models.preset import Preset
from services.batch_manager import BatchManager


class TestDropZoneFunctionality(unittest.TestCase):
    """DropZone機能テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_workspace = tempfile.mkdtemp()
        self.batch_manager = BatchManager(self.test_workspace)
        
        # テスト用ファイル作成
        self.test_files = []
        for i in range(3):
            test_file = os.path.join(self.test_workspace, f"test_file_{i}.jpg")
            with open(test_file, 'w') as f:
                f.write(f"test content {i}")
            self.test_files.append(test_file)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)
    
    def test_drop_zone_initialization(self):
        """DropZone初期化テスト"""
        from gui.drop_zone import DropZone
        
        root = tk.Tk()
        try:
            drop_zone = DropZone(root)
            drop_zone.set_managers(self.batch_manager, Mock())
            
            # 初期状態の確認
            self.assertFalse(drop_zone.is_highlighted)
            self.assertEqual(drop_zone.status_label.cget("text"), "準備完了")
            
        finally:
            root.destroy()
    
    def test_file_drop_handling(self):
        """ファイルドロップ処理テスト"""
        from gui.drop_zone import DropZone, DropResult
        
        root = tk.Tk()
        try:
            drop_zone = DropZone(root)
            drop_zone.set_managers(self.batch_manager, Mock())
            
            # ファイルドロップシミュレート
            result = drop_zone.handle_file_drop(self.test_files)
            
            # 結果確認
            self.assertIsInstance(result, DropResult)
            self.assertTrue(result.success)
            self.assertEqual(result.processed_count, 3)
            
            # プレビューエリアにファイルが表示されることを確認
            self.assertEqual(drop_zone.preview_area.size(), 3)
            
        finally:
            root.destroy()
    
    def test_folder_drop_handling(self):
        """フォルダドロップ処理テスト"""
        from gui.drop_zone import DropZone
        
        root = tk.Tk()
        try:
            drop_zone = DropZone(root)
            drop_zone.set_managers(self.batch_manager, Mock())
            
            # フォルダドロップシミュレート
            result = drop_zone.handle_folder_drop(self.test_workspace)
            
            # 結果確認
            self.assertTrue(result.success)
            self.assertGreater(result.processed_count, 0)
            
        finally:
            root.destroy()
    
    def test_visual_feedback(self):
        """ビジュアルフィードバックテスト"""
        from gui.drop_zone import DropZone
        
        root = tk.Tk()
        try:
            drop_zone = DropZone(root)
            
            # ハイライト状態テスト
            drop_zone.show_drop_feedback(True)
            self.assertTrue(drop_zone.is_highlighted)
            self.assertEqual(drop_zone.drop_area.cget("bg"), "lightblue")
            
            # 通常状態に戻す
            drop_zone.show_drop_feedback(False)
            self.assertFalse(drop_zone.is_highlighted)
            self.assertEqual(drop_zone.drop_area.cget("bg"), "lightgray")
            
        finally:
            root.destroy()
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        from gui.drop_zone import DropZone
        
        root = tk.Tk()
        try:
            drop_zone = DropZone(root)
            
            # 存在しないファイルでエラーテスト
            non_existent_files = ["/non/existent/file.jpg"]
            result = drop_zone.handle_file_drop(non_existent_files)
            
            # エラーでも処理が完了することを確認
            self.assertTrue(result.success)
            
        finally:
            root.destroy()
    
    def test_file_filtering(self):
        """ファイルフィルタリングテスト"""
        from gui.drop_zone import DropZone
        
        root = tk.Tk()
        try:
            drop_zone = DropZone(root)
            drop_zone.set_managers(self.batch_manager, Mock())
            
            # 異なる拡張子のファイルを作成
            mixed_files = []
            for ext in ['.jpg', '.txt', '.png', '.doc']:
                test_file = os.path.join(self.test_workspace, f"test{ext}")
                with open(test_file, 'w') as f:
                    f.write("test content")
                mixed_files.append(test_file)
            
            # ファイルドロップ
            result = drop_zone.handle_file_drop(mixed_files)
            self.assertTrue(result.success)
            self.assertEqual(result.processed_count, 4)
            
        finally:
            root.destroy()


if __name__ == '__main__':
    unittest.main()