"""
ストック型バッチファイル管理システムのテスト

要件定義02.mdのFR-301〜FR-306に基づく失敗するテストを記述
- バッチファイル命名規則（プリセットID_陣営_キャラ名.bat）
- バッチファイルの永続保存と無制限再利用機能
- rename_batchesフォルダでの自動管理
- バッチファイル一覧表示・検索・削除・GUI管理
- 対象拡張子フィルタ機能内蔵
- バッチ実行結果の履歴管理とレポート機能
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch
from src.models.batch_file import BatchFile
from src.services.batch_manager import BatchManager


class TestBatchFileModel(unittest.TestCase):
    """BatchFileモデルのテスト"""
    
    def test_batch_file_creation(self):
        """BatchFileオブジェクトの作成をテスト"""
        # 失敗するテスト：BatchFileクラスが未実装
        batch_file = BatchFile(
            preset_id="B63EF9",
            preset_name="アニメキャラ整理",
            field_values={"陣営": "クレキュリア", "キャラ名": "アクララ"},
            target_extensions=[".png", ".jpg"],
            workspace_path="C:/Users/Test/Pictures/Tadakan"
        )
        
        # 基本属性の確認
        self.assertEqual(batch_file.preset_id, "B63EF9")
        self.assertEqual(batch_file.field_values["陣営"], "クレキュリア")
        self.assertEqual(batch_file.target_extensions, [".png", ".jpg"])
    
    def test_batch_filename_generation(self):
        """バッチファイル名の生成をテスト"""
        # 失敗するテスト：get_batch_filenameメソッドが未実装
        batch_file = BatchFile(
            preset_id="B63EF9",
            preset_name="テスト",
            field_values={"陣営": "クレキュリア", "キャラ名": "アクララ"},
            target_extensions=[".png"]
        )
        
        filename = batch_file.get_batch_filename()
        expected = "B63EF9_クレキュリア_アクララ.bat"
        self.assertEqual(filename, expected)
    
    def test_batch_file_content_generation(self):
        """バッチファイルの内容生成をテスト"""
        # 失敗するテスト：generate_batch_contentメソッドが未実装
        batch_file = BatchFile(
            preset_id="B63EF9",
            preset_name="テスト",
            field_values={"陣営": "クレキュリア", "キャラ名": "アクララ"},
            target_extensions=[".png", ".jpg"],
            workspace_path="C:/Pictures/Tadakan"
        )
        
        content = batch_file.generate_batch_content()
        
        # バッチファイルの内容チェック
        self.assertIn("@echo off", content)
        self.assertIn("B63EF9_クレキュリア_アクララ", content)
        self.assertIn("*.png", content)
        self.assertIn("*.jpg", content)
        self.assertIn("move", content)
    
    def test_sequence_number_tracking(self):
        """連番追跡機能をテスト"""
        # 失敗するテスト：get_next_sequenceメソッドが未実装
        batch_file = BatchFile(
            preset_id="B63EF9",
            preset_name="テスト",
            field_values={"陣営": "クレキュリア", "キャラ名": "アクララ"}
        )
        
        # 初回は A00001
        seq1 = batch_file.get_next_sequence()
        self.assertEqual(seq1, "A00001")
        
        # 2回目は A00002
        seq2 = batch_file.get_next_sequence()
        self.assertEqual(seq2, "A00002")
        
        # 現在の連番を確認
        self.assertEqual(batch_file.current_sequence, 2)


class TestBatchManager(unittest.TestCase):
    """BatchManagerのテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.batch_manager = BatchManager(workspace_path=self.temp_dir)
    
    def test_create_batch_file(self):
        """バッチファイル作成をテスト"""
        # 失敗するテスト：BatchManagerクラスが未実装
        from src.models.preset import Preset
        
        preset = Preset(
            name="テストプリセット",
            fields=["陣営", "キャラ名"],
            naming_pattern="{陣営}_{キャラ名}_{番号}",
            id="B63EF9"
        )
        
        values = {"陣営": "クレキュリア", "キャラ名": "アクララ"}
        
        batch_file = self.batch_manager.create_batch_file(preset, values)
        
        # バッチファイルが作成されることをテスト
        self.assertIsNotNone(batch_file)
        self.assertEqual(batch_file.preset_id, "B63EF9")
        self.assertEqual(batch_file.field_values, values)
    
    def test_save_batch_file_to_workspace(self):
        """ワークスペースへのバッチファイル保存をテスト"""
        # 失敗するテスト：save_batch_fileメソッドが未実装
        batch_file = BatchFile(
            preset_id="B63EF9",
            preset_name="テスト",
            field_values={"陣営": "クレキュリア", "キャラ名": "アクララ"}
        )
        
        saved_path = self.batch_manager.save_batch_file(batch_file)
        
        # rename_batchesフォルダに保存されることをテスト
        expected_dir = os.path.join(self.temp_dir, "rename_batches")
        expected_filename = "B63EF9_クレキュリア_アクララ.bat"
        expected_path = os.path.join(expected_dir, expected_filename)
        
        self.assertEqual(saved_path, expected_path)
        self.assertTrue(os.path.exists(expected_path))
    
    def test_load_batch_files(self):
        """バッチファイル一覧読み込みをテスト"""
        # 失敗するテスト：load_batch_filesメソッドが未実装
        # テスト用バッチファイルを事前作成
        batch_files_data = [
            ("B63EF9_クレキュリア_アクララ.bat", "B63EF9"),
            ("X1Y2Z3_セントラル_ノノミ.bat", "X1Y2Z3"),
        ]
        
        rename_batches_dir = os.path.join(self.temp_dir, "rename_batches")
        os.makedirs(rename_batches_dir, exist_ok=True)
        
        for filename, preset_id in batch_files_data:
            with open(os.path.join(rename_batches_dir, filename), 'w', encoding='shift_jis') as f:
                f.write(f"@echo off\nREM Preset ID: {preset_id}\n")
        
        # バッチファイル一覧の読み込み
        batch_files = self.batch_manager.load_batch_files()
        
        self.assertEqual(len(batch_files), 2)
        self.assertEqual(batch_files[0].preset_id, "B63EF9")
        self.assertEqual(batch_files[1].preset_id, "X1Y2Z3")
    
    def test_search_batch_files(self):
        """バッチファイル検索をテスト"""
        # 失敗するテスト：search_batch_filesメソッドが未実装
        # テスト用データ準備
        batch_files = [
            BatchFile("B63EF9", "テスト1", {"陣営": "クレキュリア", "キャラ名": "アクララ"}),
            BatchFile("X1Y2Z3", "テスト2", {"陣営": "セントラル", "キャラ名": "ノノミ"}),
            BatchFile("A9B8C7", "テスト3", {"陣営": "クレキュリア", "キャラ名": "ヒビキ"}),
        ]
        
        self.batch_manager._batch_files = batch_files
        
        # 陣営で検索
        results = self.batch_manager.search_batch_files({"陣営": "クレキュリア"})
        self.assertEqual(len(results), 2)
        
        # キャラ名で検索
        results = self.batch_manager.search_batch_files({"キャラ名": "ノノミ"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].preset_id, "X1Y2Z3")
    
    def test_delete_batch_file(self):
        """バッチファイル削除をテスト"""
        # 失敗するテスト：delete_batch_fileメソッドが未実装
        # テスト用バッチファイル作成
        batch_file = BatchFile(
            preset_id="B63EF9",
            preset_name="テスト",
            field_values={"陣営": "クレキュリア", "キャラ名": "アクララ"}
        )
        
        saved_path = self.batch_manager.save_batch_file(batch_file)
        self.assertTrue(os.path.exists(saved_path))
        
        # 削除実行
        success = self.batch_manager.delete_batch_file("B63EF9_クレキュリア_アクララ.bat")
        self.assertTrue(success)
        self.assertFalse(os.path.exists(saved_path))
    
    def test_execute_batch_with_files(self):
        """ファイルリストでのバッチ実行をテスト"""
        # 失敗するテスト：execute_batch_with_filesメソッドが未実装
        batch_file = BatchFile(
            preset_id="B63EF9",
            preset_name="テスト",
            field_values={"陣営": "クレキュリア", "キャラ名": "アクララ"},
            target_extensions=[".png"]
        )
        
        # テスト用ファイル準備
        test_files = [
            os.path.join(self.temp_dir, "test1.png"),
            os.path.join(self.temp_dir, "test2.png"),
        ]
        
        for file_path in test_files:
            with open(file_path, 'w') as f:
                f.write("test")
        
        # バッチ実行
        result = self.batch_manager.execute_batch_with_files(batch_file, test_files)
        
        # 実行結果の確認
        self.assertIsNotNone(result)
        self.assertEqual(result.processed_files_count, 2)
        self.assertEqual(result.success_count, 2)
        self.assertEqual(result.error_count, 0)


class TestBatchExecutionHistory(unittest.TestCase):
    """バッチ実行履歴管理のテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.batch_manager = BatchManager(workspace_path=self.temp_dir)
    
    def test_execution_result_recording(self):
        """実行結果記録をテスト"""
        # 失敗するテスト：record_execution_resultメソッドが未実装
        from src.models.execution_result import ExecutionResult
        
        result = ExecutionResult(
            batch_filename="B63EF9_クレキュリア_アクララ.bat",
            executed_at="2024-01-01T12:00:00",
            processed_files_count=5,
            success_count=4,
            error_count=1,
            processing_time_seconds=10.5
        )
        
        self.batch_manager.record_execution_result(result)
        
        # 履歴が記録されることをテスト
        history = self.batch_manager.get_execution_history("B63EF9_クレキュリア_アクララ.bat")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].success_count, 4)
    
    def test_execution_report_generation(self):
        """実行レポート生成をテスト"""
        # 失敗するテスト：generate_execution_reportメソッドが未実装
        # テスト用履歴データ準備
        results = [
            {"batch_filename": "B63EF9_クレキュリア_アクララ.bat", "success_count": 10, "error_count": 0},
            {"batch_filename": "X1Y2Z3_セントラル_ノノミ.bat", "success_count": 5, "error_count": 2},
        ]
        
        for result_data in results:
            # 履歴データを設定
            pass
        
        report = self.batch_manager.generate_execution_report(days=30)
        
        # レポート内容の確認
        self.assertIn("total_executions", report)
        self.assertIn("success_rate", report)
        self.assertIn("most_used_batches", report)
        self.assertIn("error_summary", report)
    
    def test_batch_usage_statistics(self):
        """バッチ使用統計をテスト"""
        # 失敗するテスト：get_usage_statisticsメソッドが未実装
        stats = self.batch_manager.get_usage_statistics()
        
        # 統計情報の確認
        self.assertIn("total_batch_files", stats)
        self.assertIn("total_executions", stats)
        self.assertIn("average_files_per_execution", stats)
        self.assertIn("most_popular_presets", stats)


if __name__ == '__main__':
    unittest.main()