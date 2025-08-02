import unittest
import tempfile
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.preset import Preset
from models.file_item import FileItem


class TestPresetModel(unittest.TestCase):
    
    def test_preset_class_exists(self):
        """Presetクラスが存在すること"""
        # Presetクラスをインスタンス化できることを確認
        preset = Preset(
            name="テスト",
            fields=["項目1"],
            naming_pattern="{項目1}"
        )
        self.assertIsInstance(preset, Preset)
    
    def test_create_preset_instance(self):
        """Presetインスタンスを作成できること"""
        preset = Preset(
            name="テストプリセット",
            fields=["項目1", "項目2", "項目3"],
            default_values={"項目1": "デフォルト1", "項目3": "デフォルト3"},
            naming_pattern="{項目1}_{項目2}_{項目3}",
            target_extensions=[".jpg", ".png", ".gif"]
        )
        
        self.assertEqual(preset.name, "テストプリセット")
        self.assertEqual(preset.fields, ["項目1", "項目2", "項目3"])
        self.assertEqual(preset.default_values, {"項目1": "デフォルト1", "項目3": "デフォルト3"})
        self.assertEqual(preset.naming_pattern, "{項目1}_{項目2}_{項目3}")
        self.assertEqual(preset.target_extensions, [".jpg", ".png", ".gif"])
    
    def test_preset_to_dict(self):
        """PresetをDict形式に変換できること"""
        preset = Preset(
            name="辞書テスト",
            fields=["フィールドA", "フィールドB"],
            naming_pattern="{フィールドA}_{フィールドB}"
        )
        
        preset_dict = preset.to_dict()
        
        self.assertEqual(preset_dict['name'], "辞書テスト")
        self.assertEqual(preset_dict['fields'], ["フィールドA", "フィールドB"])
        self.assertEqual(preset_dict['naming_pattern'], "{フィールドA}_{フィールドB}")
        self.assertIn('created_at', preset_dict)
    
    def test_preset_from_dict(self):
        """Dict形式からPresetを作成できること"""
        preset_data = {
            "name": "辞書から作成",
            "fields": ["項目X", "項目Y"],
            "default_values": {"項目X": "デフォルトX"},
            "naming_pattern": "{項目X}_{項目Y}",
            "target_extensions": [".txt"],
            "created_at": "2024-01-01T00:00:00"
        }
        
        preset = Preset.from_dict(preset_data)
        
        self.assertEqual(preset.name, "辞書から作成")
        self.assertEqual(preset.fields, ["項目X", "項目Y"])
        self.assertEqual(preset.default_values, {"項目X": "デフォルトX"})
    
    def test_validate_naming_pattern(self):
        """命名パターンのバリデーションが動作すること"""
        # 有効なパターン
        valid_preset = Preset(
            name="有効テスト",
            fields=["項目1", "項目2"],
            naming_pattern="{項目1}_{項目2}"
        )
        self.assertTrue(valid_preset.validate_naming_pattern())
        
        # 無効なパターン（存在しないフィールド参照）
        invalid_preset = Preset(
            name="無効テスト",
            fields=["項目1", "項目2"],
            naming_pattern="{項目1}_{存在しない項目}"
        )
        self.assertFalse(invalid_preset.validate_naming_pattern())
    
    def test_get_field_value_with_default(self):
        """フィールド値取得時にデフォルト値が適用されること"""
        preset = Preset(
            name="デフォルトテスト",
            fields=["項目1", "項目2", "項目3"],
            naming_pattern="{項目1}_{項目2}_{項目3}",
            default_values={"項目1": "デフォルト1", "項目3": "デフォルト3"}
        )
        
        input_values = {"項目2": "入力値2"}
        
        # デフォルト値が設定されている項目
        self.assertEqual(preset.get_field_value("項目1", input_values), "デフォルト1")
        
        # 入力値がある項目
        self.assertEqual(preset.get_field_value("項目2", input_values), "入力値2")
        
        # デフォルト値が設定されている項目（入力値なし）
        self.assertEqual(preset.get_field_value("項目3", {}), "デフォルト3")


class TestFileItemModel(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_item_class_exists(self):
        """FileItemクラスが存在すること"""
        # FileItemクラスをインスタンス化できることを確認
        file_item = FileItem(
            original_path="/test/file.txt",
            original_name="file.txt"
        )
        self.assertIsInstance(file_item, FileItem)
    
    def test_create_file_item_instance(self):
        """FileItemインスタンスを作成できること"""
        file_item = FileItem(
            original_path="/test/path/original.jpg",
            original_name="original.jpg",
            new_name="new_name.jpg",
            file_size=1024,
            file_type="image"
        )
        
        self.assertEqual(file_item.original_path, "/test/path/original.jpg")
        self.assertEqual(file_item.original_name, "original.jpg")
        self.assertEqual(file_item.new_name, "new_name.jpg")
        self.assertEqual(file_item.file_size, 1024)
        self.assertEqual(file_item.file_type, "image")
    
    def test_get_original_extension(self):
        """元ファイルの拡張子を取得できること"""
        file_item = FileItem(
            original_path="/test/sample.JPG",
            original_name="sample.JPG"
        )
        
        extension = file_item.get_original_extension()
        self.assertEqual(extension, ".JPG")
    
    def test_get_original_extension_normalized(self):
        """正規化された拡張子を取得できること"""
        file_item = FileItem(
            original_path="/test/sample.JPG",
            original_name="sample.JPG"
        )
        
        normalized_ext = file_item.get_original_extension(normalize=True)
        self.assertEqual(normalized_ext, ".jpg")
    
    def test_generate_new_path(self):
        """新しいファイルパスを生成できること"""
        file_item = FileItem(
            original_path="/original/path/old_name.txt",
            original_name="old_name.txt",
            new_name="new_name.txt"
        )
        
        new_path = file_item.generate_new_path("/target/directory")
        self.assertEqual(new_path, "/target/directory/new_name.txt")
    
    def test_file_item_to_dict(self):
        """FileItemをDict形式に変換できること"""
        file_item = FileItem(
            original_path="/test/file.png",
            original_name="file.png",
            new_name="renamed.png",
            file_size=2048,
            file_type="image"
        )
        
        item_dict = file_item.to_dict()
        
        self.assertEqual(item_dict['original_path'], "/test/file.png")
        self.assertEqual(item_dict['original_name'], "file.png")
        self.assertEqual(item_dict['new_name'], "renamed.png")
        self.assertEqual(item_dict['file_size'], 2048)
        self.assertEqual(item_dict['file_type'], "image")
    
    def test_file_item_from_dict(self):
        """Dict形式からFileItemを作成できること"""
        item_data = {
            "original_path": "/from/dict.mp3",
            "original_name": "dict.mp3",
            "new_name": "from_dict.mp3",
            "file_size": 4096,
            "file_type": "audio"
        }
        
        file_item = FileItem.from_dict(item_data)
        
        self.assertEqual(file_item.original_path, "/from/dict.mp3")
        self.assertEqual(file_item.original_name, "dict.mp3")
        self.assertEqual(file_item.new_name, "from_dict.mp3")
        self.assertEqual(file_item.file_size, 4096)
        self.assertEqual(file_item.file_type, "audio")
    
    def test_validate_file_exists(self):
        """ファイル存在チェックが動作すること"""
        # 存在しないファイル
        file_item = FileItem(
            original_path="/nonexistent/file.txt",
            original_name="file.txt"
        )
        
        self.assertFalse(file_item.validate_file_exists())
    
    def test_get_file_info_from_path(self):
        """ファイルパスから情報を自動取得できること"""
        # 一時ファイル作成
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            file_item = FileItem.from_path(tmp_path)
            
            self.assertEqual(file_item.original_path, tmp_path)
            self.assertEqual(file_item.original_name, os.path.basename(tmp_path))
            self.assertGreater(file_item.file_size, 0)
            
        finally:
            os.unlink(tmp_path)


if __name__ == '__main__':
    unittest.main()