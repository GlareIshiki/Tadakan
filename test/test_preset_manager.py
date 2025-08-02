import unittest
import json
import os
import tempfile
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.preset_manager import PresetManager
from models.preset import Preset


class TestPresetManager(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.preset_manager = PresetManager(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_new_preset(self):
        """新しいプリセットを作成できること"""
        preset_name = "テスト陣営プリセット"
        fields = ["陣営", "キャラ名", "番号"]
        default_values = {"陣営": "青", "番号": "001"}
        naming_pattern = "{陣営}_{キャラ名}_{番号}"
        
        preset = self.preset_manager.create_preset(
            name=preset_name,
            fields=fields,
            default_values=default_values,
            naming_pattern=naming_pattern
        )
        
        self.assertIsInstance(preset, Preset)
        self.assertEqual(preset.name, preset_name)
        self.assertEqual(preset.fields, fields)
        self.assertEqual(preset.default_values, default_values)
        self.assertEqual(preset.naming_pattern, naming_pattern)
    
    def test_save_preset_to_file(self):
        """プリセットをJSONファイルに保存できること"""
        preset_name = "保存テスト"
        preset = self.preset_manager.create_preset(
            name=preset_name,
            fields=["項目1", "項目2"],
            naming_pattern="{項目1}_{項目2}"
        )
        
        saved_path = self.preset_manager.save_preset(preset)
        
        self.assertTrue(os.path.exists(saved_path))
        with open(saved_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['name'], preset_name)
        self.assertEqual(saved_data['fields'], ["項目1", "項目2"])
    
    def test_load_preset_from_file(self):
        """JSONファイルからプリセットを読み込めること"""
        preset_data = {
            "name": "読み込みテスト",
            "fields": ["フィールド1", "フィールド2"],
            "default_values": {"フィールド1": "デフォルト"},
            "naming_pattern": "{フィールド1}_{フィールド2}",
            "target_extensions": [".jpg", ".png"]
        }
        
        test_file = os.path.join(self.temp_dir, "test_preset.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, ensure_ascii=False)
        
        loaded_preset = self.preset_manager.load_preset(test_file)
        
        self.assertEqual(loaded_preset.name, "読み込みテスト")
        self.assertEqual(loaded_preset.fields, ["フィールド1", "フィールド2"])
        self.assertEqual(loaded_preset.default_values, {"フィールド1": "デフォルト"})
    
    def test_list_available_presets(self):
        """利用可能なプリセット一覧を取得できること"""
        # 複数のプリセットを作成・保存
        preset1 = self.preset_manager.create_preset("プリセット1", ["項目A"], "{項目A}")
        preset2 = self.preset_manager.create_preset("プリセット2", ["項目B"], "{項目B}")
        
        self.preset_manager.save_preset(preset1)
        self.preset_manager.save_preset(preset2)
        
        preset_list = self.preset_manager.list_presets()
        
        self.assertEqual(len(preset_list), 2)
        preset_names = [p.name for p in preset_list]
        self.assertIn("プリセット1", preset_names)
        self.assertIn("プリセット2", preset_names)
    
    def test_delete_preset(self):
        """プリセットを削除できること"""
        preset = self.preset_manager.create_preset("削除テスト", ["項目"], "{項目}")
        saved_path = self.preset_manager.save_preset(preset)
        
        self.assertTrue(os.path.exists(saved_path))
        
        self.preset_manager.delete_preset("削除テスト")
        
        self.assertFalse(os.path.exists(saved_path))
    
    def test_export_preset(self):
        """プリセットをエクスポートできること"""
        preset = self.preset_manager.create_preset(
            "エクスポートテスト", 
            ["項目1", "項目2"], 
            "{項目1}_{項目2}"
        )
        
        export_path = os.path.join(self.temp_dir, "exported.json")
        self.preset_manager.export_preset(preset, export_path)
        
        self.assertTrue(os.path.exists(export_path))
        with open(export_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        
        self.assertEqual(exported_data['name'], "エクスポートテスト")
    
    def test_import_preset(self):
        """プリセットをインポートできること"""
        # エクスポート用データを準備
        preset_data = {
            "name": "インポートテスト",
            "fields": ["項目X", "項目Y"],
            "naming_pattern": "{項目X}_{項目Y}"
        }
        
        import_file = os.path.join(self.temp_dir, "import.json")
        with open(import_file, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, ensure_ascii=False)
        
        imported_preset = self.preset_manager.import_preset(import_file)
        
        self.assertEqual(imported_preset.name, "インポートテスト")
        self.assertEqual(imported_preset.fields, ["項目X", "項目Y"])
    
    def test_validate_preset_data(self):
        """プリセットデータのバリデーションが動作すること"""
        # 必須フィールドが不足している場合
        with self.assertRaises(ValueError):
            self.preset_manager.create_preset("", [], "")  # 空の名前
        
        with self.assertRaises(ValueError):
            self.preset_manager.create_preset("テスト", [], "{存在しない項目}")  # 不正なパターン


if __name__ == '__main__':
    unittest.main()