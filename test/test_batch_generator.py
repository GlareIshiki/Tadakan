import unittest
import os
import tempfile
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.batch_generator import BatchGenerator
from models.file_item import FileItem


class TestBatchGenerator(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.batch_generator = BatchGenerator()
        
        # テスト用ファイルアイテム
        self.test_files = [
            FileItem(
                original_path="/test/file1.jpg",
                original_name="file1.jpg",
                new_name="赤軍_田中_001.jpg"
            ),
            FileItem(
                original_path="/test/file2.png", 
                original_name="file2.png",
                new_name="赤軍_佐藤_002.png"
            )
        ]
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_rename_batch_file(self):
        """リネーム用バッチファイルを生成できること"""
        target_directory = "/target/folder"
        
        batch_content = self.batch_generator.generate_rename_batch(
            self.test_files,
            target_directory
        )
        
        # バッチファイルの内容確認
        self.assertIn("@echo off", batch_content)
        self.assertIn('ren "file1.jpg" "赤軍_田中_001.jpg"', batch_content)
        self.assertIn('ren "file2.png" "赤軍_佐藤_002.png"', batch_content)
        self.assertIn(f'move "赤軍_田中_001.jpg" "{target_directory}"', batch_content)
    
    def test_save_batch_file(self):
        """バッチファイルをディスクに保存できること"""
        batch_content = self.batch_generator.generate_rename_batch(
            self.test_files,
            "/target"
        )
        
        batch_filename = "test_rename.bat"
        saved_path = self.batch_generator.save_batch_file(
            batch_content,
            self.temp_dir,
            batch_filename
        )
        
        self.assertTrue(os.path.exists(saved_path))
        self.assertTrue(saved_path.endswith(".bat"))
        
        # ファイル内容の確認
        with open(saved_path, 'r', encoding='shift_jis') as f:
            content = f.read()
        
        self.assertEqual(content, batch_content)
    
    def test_generate_filter_batch_file(self):
        """フィルタ用バッチファイルを生成できること"""
        filter_conditions = {
            "陣営": "赤軍",
            "キャラ名": "*田中*"  # ワイルドカード対応
        }
        
        source_directory = "/source/folder"
        temp_directory = "/temp/filter"
        
        batch_content = self.batch_generator.generate_filter_batch(
            filter_conditions,
            source_directory,
            temp_directory
        )
        
        # フィルタ条件に基づくファイル移動コマンドの確認
        self.assertIn("@echo off", batch_content)
        self.assertIn(f'mkdir "{temp_directory}"', batch_content)
        self.assertIn("赤軍", batch_content)
        self.assertIn("田中", batch_content)
    
    def test_generate_restore_batch_file(self):
        """フィルタ解除（復元）用バッチファイルを生成できること"""
        temp_directory = "/temp/filter"
        original_directory = "/original/folder"
        
        # 移動されたファイルのリスト
        moved_files = [
            "赤軍_田中_001.jpg",
            "赤軍_田中_002.png"
        ]
        
        batch_content = self.batch_generator.generate_restore_batch(
            moved_files,
            temp_directory,
            original_directory
        )
        
        # 復元コマンドの確認
        self.assertIn("@echo off", batch_content)
        self.assertIn(f'move "{temp_directory}\\赤軍_田中_001.jpg" "{original_directory}"', batch_content)
        self.assertIn(f'move "{temp_directory}\\赤軍_田中_002.png" "{original_directory}"', batch_content)
    
    def test_add_error_handling(self):
        """バッチファイルにエラーハンドリングが含まれること"""
        batch_content = self.batch_generator.generate_rename_batch(
            self.test_files,
            "/target",
            include_error_handling=True
        )
        
        # エラーハンドリングの確認
        self.assertIn("if errorlevel 1", batch_content)
        self.assertIn("echo エラーが発生しました", batch_content)
        self.assertIn("pause", batch_content)
    
    def test_add_logging(self):
        """バッチファイルにログ出力が含まれること"""
        log_file = "/logs/rename.log"
        
        batch_content = self.batch_generator.generate_rename_batch(
            self.test_files,
            "/target",
            log_file=log_file
        )
        
        # ログ出力の確認
        self.assertIn(f"echo 開始時刻: %date% %time% >> \"{log_file}\"", batch_content)
        self.assertIn(f"echo 完了時刻: %date% %time% >> \"{log_file}\"", batch_content)
    
    def test_escape_special_characters(self):
        """特殊文字を含むファイル名を適切にエスケープできること"""
        special_files = [
            FileItem(
                original_path="/test/file (1).jpg",
                original_name="file (1).jpg",
                new_name="赤軍_田中&佐藤_001.jpg"
            )
        ]
        
        batch_content = self.batch_generator.generate_rename_batch(
            special_files,
            "/target"
        )
        
        # 特殊文字のエスケープ確認
        self.assertIn('"file ^^(1^^).jpg"', batch_content)
        self.assertIn('"赤軍_田中^^&佐藤_001.jpg"', batch_content)
    
    def test_generate_batch_metadata(self):
        """バッチファイルのメタデータを生成できること"""
        metadata = self.batch_generator.generate_batch_metadata(
            preset_name="テストプリセット",
            operation_type="rename",
            file_count=len(self.test_files),
            target_directory="/target"
        )
        
        self.assertEqual(metadata['preset_name'], "テストプリセット")
        self.assertEqual(metadata['operation_type'], "rename")
        self.assertEqual(metadata['file_count'], 2)
        self.assertEqual(metadata['target_directory'], "/target")
        self.assertIn('created_at', metadata)
    
    def test_validate_batch_parameters(self):
        """バッチ生成パラメータのバリデーションが動作すること"""
        # 空のファイルリスト
        with self.assertRaises(ValueError):
            self.batch_generator.generate_rename_batch([], "/target")
        
        # 無効なターゲットディレクトリ
        with self.assertRaises(ValueError):
            self.batch_generator.generate_rename_batch(self.test_files, "")
    
    def test_generate_undo_batch_file(self):
        """アンドゥ用バッチファイルを生成できること"""
        # リネーム操作の逆操作
        undo_operations = [
            {
                'current_name': '赤軍_田中_001.jpg',
                'original_name': 'file1.jpg',
                'directory': '/target'
            },
            {
                'current_name': '赤軍_佐藤_002.png', 
                'original_name': 'file2.png',
                'directory': '/target'
            }
        ]
        
        batch_content = self.batch_generator.generate_undo_batch(undo_operations)
        
        # アンドゥコマンドの確認
        self.assertIn('@echo off', batch_content)
        self.assertIn('ren "赤軍_田中_001.jpg" "file1.jpg"', batch_content)
        self.assertIn('ren "赤軍_佐藤_002.png" "file2.png"', batch_content)
    
    def test_batch_file_encoding(self):
        """バッチファイルが適切な文字エンコーディング（Shift_JIS）で保存されること"""
        japanese_files = [
            FileItem(
                original_path="/test/ファイル１.jpg",
                original_name="ファイル１.jpg", 
                new_name="赤軍_田中_001.jpg"
            )
        ]
        
        batch_content = self.batch_generator.generate_rename_batch(
            japanese_files,
            "/target"
        )
        
        batch_path = self.batch_generator.save_batch_file(
            batch_content,
            self.temp_dir,
            "japanese_test.bat"
        )
        
        # Shift_JISで読み込めることを確認
        with open(batch_path, 'r', encoding='shift_jis') as f:
            content = f.read()
        
        self.assertIn("ファイル１.jpg", content)


if __name__ == '__main__':
    unittest.main()