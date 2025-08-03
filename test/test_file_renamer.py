import unittest
import os
import tempfile
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.file_renamer import FileRenamer
from models.preset import Preset
from models.file_item import FileItem


class TestFileRenamer(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_renamer = FileRenamer()
        
        # テスト用プリセット
        self.test_preset = Preset(
            name="テストプリセット",
            fields=["陣営", "キャラ名", "番号"],
            default_values={"陣営": "青軍", "番号": "001"},
            naming_pattern="{陣営}_{キャラ名}_{番号}"
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_new_filename(self):
        """プリセットに基づいて新しいファイル名を生成できること"""
        input_values = {
            "陣営": "赤軍",
            "キャラ名": "田中",
            "番号": "002"
        }
        
        new_filename = self.file_renamer.generate_filename(
            self.test_preset, 
            input_values, 
            original_extension=".jpg"
        )
        
        self.assertEqual(new_filename, "赤軍_田中_002.jpg")
    
    def test_use_default_values(self):
        """入力されていない項目にデフォルト値を使用すること"""
        input_values = {
            "キャラ名": "佐藤"
            # 陣営と番号は未入力
        }
        
        new_filename = self.file_renamer.generate_filename(
            self.test_preset,
            input_values,
            original_extension=".png"
        )
        
        self.assertEqual(new_filename, "青軍_佐藤_001.png")
    
    def test_validate_filename_characters(self):
        """ファイル名に使用できない文字をチェックできること"""
        invalid_values = {
            "陣営": "青軍",
            "キャラ名": "田中<>太郎",  # 無効な文字を含む
            "番号": "001"
        }
        
        with self.assertRaises(ValueError) as context:
            self.file_renamer.generate_filename(
                self.test_preset,
                invalid_values,
                original_extension=".jpg"
            )
        
        self.assertIn("無効な文字", str(context.exception))
    
    def test_check_duplicate_filenames(self):
        """重複するファイル名をチェックできること"""
        # テスト用ファイルを作成
        existing_file = os.path.join(self.temp_dir, "青軍_田中_001.jpg")
        with open(existing_file, 'w') as f:
            f.write("test")
        
        input_values = {
            "陣営": "青軍",
            "キャラ名": "田中",
            "番号": "001"
        }
        
        is_duplicate = self.file_renamer.check_duplicate(
            self.test_preset,
            input_values,
            ".jpg",
            target_directory=self.temp_dir
        )
        
        self.assertTrue(is_duplicate)
    
    def test_generate_preview_list(self):
        """複数ファイルのリネームプレビューを生成できること"""
        # テスト用ファイル作成
        test_files = []
        for i, name in enumerate(["file1.jpg", "file2.png", "file3.txt"]):
            file_path = os.path.join(self.temp_dir, name)
            with open(file_path, 'w') as f:
                f.write(f"test content {i}")
            test_files.append(file_path)
        
        input_values = {
            "陣営": "緑軍",
            "キャラ名": "鈴木"
            # 番号は自動採番される想定
        }
        
        preview_list = self.file_renamer.generate_preview_list(
            self.test_preset,
            test_files,
            input_values
        )
        
        self.assertEqual(len(preview_list), 3)
        
        # 自動採番の確認
        expected_names = [
            "緑軍_鈴木_001.jpg",
            "緑軍_鈴木_002.png", 
            "緑軍_鈴木_003.txt"
        ]
        
        actual_names = [item.new_name for item in preview_list]
        self.assertEqual(actual_names, expected_names)
    
    def test_validate_ng_words(self):
        """NGワードチェックが動作すること"""
        ng_words = ["禁止", "ダメ", "NG"]
        
        invalid_values = {
            "陣営": "禁止軍",  # NGワードを含む
            "キャラ名": "田中",
            "番号": "001"
        }
        
        with self.assertRaises(ValueError) as context:
            self.file_renamer.generate_filename(
                self.test_preset,
                invalid_values,
                original_extension=".jpg",
                ng_words=ng_words
            )
        
        self.assertIn("NGワード", str(context.exception))
    
    def test_handle_missing_fields(self):
        """必須フィールドが未入力の場合にエラーになること"""
        incomplete_values = {
            "陣営": "赤軍"
            # キャラ名が未入力で、デフォルト値もない
        }
        
        with self.assertRaises(ValueError) as context:
            self.file_renamer.generate_filename(
                self.test_preset,
                incomplete_values,
                original_extension=".jpg"
            )
        
        self.assertIn("必須項目", str(context.exception))
    
    def test_auto_numbering(self):
        """自動採番機能が動作すること"""
        # 既存ファイルがある状態で自動採番
        existing_files = [
            "青軍_田中_001.jpg",
            "青軍_田中_002.jpg"
        ]
        
        for filename in existing_files:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write("test")
        
        input_values = {
            "陣営": "青軍",
            "キャラ名": "田中"
            # 番号は自動採番
        }
        
        new_filename = self.file_renamer.generate_filename_with_auto_number(
            self.test_preset,
            input_values,
            original_extension=".jpg",
            target_directory=self.temp_dir
        )
        
        self.assertEqual(new_filename, "青軍_田中_003.jpg")
    
    def test_preserve_original_extension(self):
        """元のファイル拡張子が保持されること"""
        input_values = {
            "陣営": "白軍",
            "キャラ名": "山田",
            "番号": "001"
        }
        
        # 様々な拡張子でテスト
        extensions = [".jpg", ".PNG", ".mp3", ".TXT", ".gif"]
        
        for ext in extensions:
            new_filename = self.file_renamer.generate_filename(
                self.test_preset,
                input_values,
                original_extension=ext
            )
            
            self.assertTrue(new_filename.endswith(ext.lower()))


if __name__ == '__main__':
    unittest.main()