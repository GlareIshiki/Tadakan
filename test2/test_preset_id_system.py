"""
B63EF9形式プリセットIDシステムのテスト

要件定義02.mdのFR-101〜FR-104に基づく失敗するテストを記述
- B63EF9形式6桁英数字ランダムIDによる一意識別
- プリセットIDと入力値を組み合わせたバッチファイル名生成
- プリセットIDと連番サフィックスによるファイル名生成
- プリセットID重複チェックと自動再生成機能
"""

import unittest
import re
from unittest.mock import Mock, patch
from src.models.preset import Preset
from src.utils.id_generator import PresetIDGenerator


class TestPresetIDSystem(unittest.TestCase):
    """B63EF9形式プリセットIDシステムのテスト"""
    
    def setUp(self):
        """テスト前準備"""
        self.id_generator = PresetIDGenerator()
    
    def test_generate_preset_id_format(self):
        """プリセットIDがB63EF9形式（6桁英数字）で生成されることをテスト"""
        # 失敗するテスト：まだPresetIDGeneratorクラスが存在しない
        preset_id = self.id_generator.generate()
        
        # 6桁英数字の形式チェック
        self.assertEqual(len(preset_id), 6)
        self.assertTrue(re.match(r'^[A-Z0-9]{6}$', preset_id))
        
        # 数字のみ、文字のみではないことをチェック
        self.assertFalse(preset_id.isdigit())
        self.assertFalse(preset_id.isalpha())
    
    def test_preset_id_uniqueness(self):
        """プリセットIDの一意性をテスト"""
        # 失敗するテスト：重複チェック機能が未実装
        generated_ids = set()
        
        for _ in range(1000):
            preset_id = self.id_generator.generate()
            self.assertNotIn(preset_id, generated_ids)
            generated_ids.add(preset_id)
    
    def test_preset_with_id_creation(self):
        """プリセットIDを持つPresetクラスの作成をテスト"""
        # 失敗するテスト：PresetクラスにidフィールドとID生成機能が未実装
        preset = Preset(
            name="テストプリセット",
            fields=["陣営", "キャラ名"],
            naming_pattern="{陣営}_{キャラ名}_{番号}",
            auto_generate_id=True
        )
        
        # プリセットIDが自動生成されることをテスト
        self.assertIsNotNone(preset.id)
        self.assertEqual(len(preset.id), 6)
        self.assertTrue(re.match(r'^[A-Z0-9]{6}$', preset.id))
    
    def test_batch_filename_generation(self):
        """バッチファイル名生成をテスト（プリセットID_陣営_キャラ名.bat形式）"""
        # 失敗するテスト：generate_batch_filenameメソッドが未実装
        preset = Preset(
            name="テストプリセット",
            fields=["陣営", "キャラ名"],
            naming_pattern="{陣営}_{キャラ名}_{番号}",
            id="B63EF9"
        )
        
        values = {"陣営": "クレキュリア", "キャラ名": "アクララ"}
        batch_filename = preset.generate_batch_filename(values)
        
        expected = "B63EF9_クレキュリア_アクララ.bat"
        self.assertEqual(batch_filename, expected)
    
    def test_file_naming_with_sequence(self):
        """連番サフィックス付きファイル名生成をテスト"""
        # 失敗するテスト：generate_filename_with_sequenceメソッドが未実装
        preset = Preset(
            name="テストプリセット",
            fields=["陣営", "キャラ名"],
            naming_pattern="{陣営}_{キャラ名}_{番号}",
            id="B63EF9"
        )
        
        values = {"陣営": "クレキュリア", "キャラ名": "アクララ"}
        filename = preset.generate_filename_with_sequence(values, "A00001", ".png")
        
        expected = "B63EF9_クレキュリア_アクララ_A00001.png"
        self.assertEqual(filename, expected)
    
    def test_sequence_number_generation(self):
        """A00001形式連番生成をテスト"""
        # 失敗するテスト：SequenceGeneratorクラスが未実装
        from src.utils.sequence_generator import SequenceGenerator
        
        seq_gen = SequenceGenerator()
        
        # 初回は A00001
        seq1 = seq_gen.next_sequence()
        self.assertEqual(seq1, "A00001")
        
        # 2回目は A00002
        seq2 = seq_gen.next_sequence()
        self.assertEqual(seq2, "A00002")
        
        # 10回目は A00010
        for _ in range(8):
            seq_gen.next_sequence()
        seq10 = seq_gen.next_sequence()
        self.assertEqual(seq10, "A00010")
    
    def test_preset_id_duplicate_check_and_regeneration(self):
        """プリセットID重複チェックと再生成をテスト"""
        # 失敗するテスト：重複チェック機能が未実装
        existing_ids = {"B63EF9", "X1Y2Z3", "A9B8C7"}
        
        # 重複しないIDが生成されることをテスト
        new_id = self.id_generator.generate_unique(existing_ids)
        self.assertNotIn(new_id, existing_ids)
        self.assertEqual(len(new_id), 6)
        self.assertTrue(re.match(r'^[A-Z0-9]{6}$', new_id))
    
    def test_preset_id_validation(self):
        """プリセットIDのバリデーションをテスト"""
        # 失敗するテスト：validate_preset_idメソッドが未実装
        validator = self.id_generator
        
        # 有効なID
        self.assertTrue(validator.validate_preset_id("B63EF9"))
        self.assertTrue(validator.validate_preset_id("A1B2C3"))
        
        # 無効なID
        self.assertFalse(validator.validate_preset_id("b63ef9"))  # 小文字
        self.assertFalse(validator.validate_preset_id("B63EF"))   # 5桁
        self.assertFalse(validator.validate_preset_id("B63EF9A"))  # 7桁
        self.assertFalse(validator.validate_preset_id("B63-F9"))   # ハイフン含む
        self.assertFalse(validator.validate_preset_id("123456"))   # 数字のみ
        self.assertFalse(validator.validate_preset_id("ABCDEF"))   # 文字のみ
    
    def test_preset_id_collision_handling(self):
        """プリセットID衝突処理をテスト"""
        # 失敗するテスト：衝突回避ロジックが未実装
        # モックで同じIDが2回生成される状況を作る
        with patch.object(self.id_generator, '_generate_random_id') as mock_gen:
            mock_gen.side_effect = ["B63EF9", "B63EF9", "X1Y2Z3"]  # 最初に重複、3回目で成功
            
            existing_ids = {"B63EF9"}
            unique_id = self.id_generator.generate_unique(existing_ids)
            
            # 重複を避けて新しいIDが生成されることをテスト
            self.assertEqual(unique_id, "X1Y2Z3")
            self.assertEqual(mock_gen.call_count, 3)  # 3回呼び出される


class TestPresetIDIntegration(unittest.TestCase):
    """プリセットIDシステム統合テスト"""
    
    def test_preset_creation_workflow(self):
        """プリセット作成ワークフロー全体をテスト"""
        # 失敗するテスト：統合ワークフローが未実装
        from src.services.preset_manager import PresetManager
        
        manager = PresetManager()
        
        # 新しいプリセット作成
        preset_data = {
            "name": "アニメキャラ整理",
            "fields": ["陣営", "キャラ名"],
            "naming_pattern": "{陣営}_{キャラ名}_{番号}",
            "target_extensions": [".png", ".jpg"]
        }
        
        preset = manager.create_preset(preset_data)
        
        # プリセットIDが自動生成されていることをテスト
        self.assertIsNotNone(preset.id)
        self.assertEqual(len(preset.id), 6)
        
        # バッチファイル名が正しく生成されることをテスト
        values = {"陣営": "クレキュリア", "キャラ名": "アクララ"}
        batch_filename = preset.generate_batch_filename(values)
        expected_pattern = f"{preset.id}_クレキュリア_アクララ.bat"
        self.assertEqual(batch_filename, expected_pattern)
    
    def test_multiple_preset_id_uniqueness(self):
        """複数プリセット作成時のID一意性をテスト"""
        # 失敗するテスト：複数プリセット管理機能が未実装
        from src.services.preset_manager import PresetManager
        
        manager = PresetManager()
        generated_ids = set()
        
        # 100個のプリセットを作成してID重複がないことをテスト
        for i in range(100):
            preset_data = {
                "name": f"テストプリセット{i}",
                "fields": ["フィールド1"],
                "naming_pattern": "{フィールド1}_{番号}"
            }
            
            preset = manager.create_preset(preset_data)
            self.assertNotIn(preset.id, generated_ids)
            generated_ids.add(preset.id)


if __name__ == '__main__':
    unittest.main()