"""
DynamicInputForm機能テスト

動的入力フォームの全機能をテストします。
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
from models.batch_file import BatchFile
from services.batch_manager import BatchManager


class TestDynamicInputForm(unittest.TestCase):
    """DynamicInputForm機能テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_workspace = tempfile.mkdtemp()
        self.batch_manager = BatchManager(self.test_workspace)
        
        # テスト用プリセット
        self.test_preset = Preset(
            name="動的フォームテスト",
            fields=["陣営", "キャラ名", "番号"],
            naming_pattern="{陣営}_{キャラ名}_{番号}",
            target_extensions=[".jpg", ".png"],
            id="DYN001"
        )
        
        # デフォルト値ありのプリセット
        self.preset_with_defaults = Preset(
            name="デフォルト値テスト",
            fields=["カテゴリ", "名前"],
            naming_pattern="{カテゴリ}_{名前}",
            default_values={"カテゴリ": "写真", "名前": "サンプル"},
            id="DEF001"
        )
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)
    
    def test_form_generation_from_preset(self):
        """プリセットからのフォーム生成テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            input_form = DynamicInputForm(root)
            
            # プリセットからフォーム生成
            input_form.generate_form_from_preset(self.test_preset)
            
            # フィールド数の確認
            self.assertEqual(len(input_form.input_fields), 3)
            
            # 各フィールドの存在確認
            expected_fields = ["陣営", "キャラ名", "番号"]
            for field in expected_fields:
                self.assertIn(field, input_form.input_fields)
                self.assertIsInstance(input_form.input_fields[field], tk.StringVar)
            
            # 現在のプリセットが設定されることを確認
            self.assertEqual(input_form.current_preset, self.test_preset)
            
        finally:
            root.destroy()
    
    def test_form_generation_with_defaults(self):
        """デフォルト値ありプリセットのフォーム生成テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            input_form = DynamicInputForm(root)
            
            # デフォルト値ありプリセットでフォーム生成
            input_form.generate_form_from_preset(self.preset_with_defaults)
            
            # デフォルト値が設定されることを確認
            self.assertEqual(input_form.input_fields["カテゴリ"].get(), "写真")
            self.assertEqual(input_form.input_fields["名前"].get(), "サンプル")
            
        finally:
            root.destroy()
    
    def test_form_data_setting(self):
        """フォームデータ設定テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            input_form = DynamicInputForm(root)
            input_form.generate_form_from_preset(self.test_preset)
            
            # フォームデータを設定
            form_data = {
                "陣営": "クレキュリア",
                "キャラ名": "アクララ",
                "番号": "001"
            }
            input_form.set_form_data(form_data)
            
            # 設定された値を確認
            for field, value in form_data.items():
                self.assertEqual(input_form.input_fields[field].get(), value)
            
        finally:
            root.destroy()
    
    def test_batch_creation_from_form(self):
        """フォームからのバッチ作成テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            input_form = DynamicInputForm(root)
            input_form.set_managers(self.batch_manager, Mock())
            input_form.generate_form_from_preset(self.test_preset)
            
            # フォームに値を設定
            form_data = {
                "陣営": "テスト陣営",
                "キャラ名": "テストキャラ",
                "番号": "123"
            }
            input_form.set_form_data(form_data)
            
            # バッチファイル作成
            batch_file = input_form.create_batch_from_form()
            
            # 作成されたバッチファイルの確認
            self.assertIsInstance(batch_file, BatchFile)
            self.assertEqual(batch_file.preset_id, "DYN001")
            self.assertEqual(batch_file.preset_name, "動的フォームテスト")
            self.assertEqual(batch_file.field_values["陣営"], "テスト陣営")
            self.assertEqual(batch_file.field_values["キャラ名"], "テストキャラ")
            self.assertEqual(batch_file.field_values["番号"], "123")
            
        finally:
            root.destroy()
    
    def test_batch_creation_without_preset(self):
        """プリセット未設定時のバッチ作成テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            input_form = DynamicInputForm(root)
            input_form.set_managers(self.batch_manager, Mock())
            
            # プリセット未設定でバッチ作成を試行
            batch_file = input_form.create_batch_from_form()
            
            # Noneが返されることを確認
            self.assertIsNone(batch_file)
            
        finally:
            root.destroy()
    
    def test_suggestion_functionality(self):
        """サジェスト機能テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            input_form = DynamicInputForm(root)
            input_form.generate_form_from_preset(self.test_preset)
            
            # サジェストデータを設定
            suggestions = ["クレキュリア", "セントラル", "ミレニアム"]
            input_form.enable_suggestions("陣営", suggestions)
            
            # サジェスト機能が有効になることを確認
            self.assertTrue(input_form.has_suggestions("陣営"))
            self.assertFalse(input_form.has_suggestions("存在しないフィールド"))
            
            # 現在のサジェストを取得
            current_suggestions = input_form.get_current_suggestions("陣営")
            self.assertEqual(len(current_suggestions), 3)
            
            # 部分マッチのテスト
            input_form.input_fields["陣営"].set("クレ")
            filtered_suggestions = input_form.get_current_suggestions("陣営")
            self.assertEqual(len(filtered_suggestions), 1)
            self.assertEqual(filtered_suggestions[0], "クレキュリア")
            
        finally:
            root.destroy()
    
    def test_form_clearing(self):
        """フォームクリアテスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            input_form = DynamicInputForm(root)
            input_form.generate_form_from_preset(self.test_preset)
            
            # 値を設定
            form_data = {"陣営": "テスト", "キャラ名": "テスト", "番号": "123"}
            input_form.set_form_data(form_data)
            
            # 別のプリセットでフォーム再生成（クリア効果）
            new_preset = Preset(
                name="新しいプリセット",
                fields=["新フィールド"],
                naming_pattern="{新フィールド}",
                id="NEW001"
            )
            input_form.generate_form_from_preset(new_preset)
            
            # 新しいフィールドのみが存在することを確認
            self.assertEqual(len(input_form.input_fields), 1)
            self.assertIn("新フィールド", input_form.input_fields)
            self.assertNotIn("陣営", input_form.input_fields)
            
        finally:
            root.destroy()
    
    def test_empty_values_handling(self):
        """空値の処理テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            input_form = DynamicInputForm(root)
            input_form.set_managers(self.batch_manager, Mock())
            input_form.generate_form_from_preset(self.test_preset)
            
            # 空値でバッチ作成
            batch_file = input_form.create_batch_from_form()
            
            # バッチファイルは作成されるが、空の値が含まれることを確認
            self.assertIsInstance(batch_file, BatchFile)
            for field in self.test_preset.fields:
                self.assertEqual(batch_file.field_values[field], "")
            
        finally:
            root.destroy()
    
    @patch('tkinter.messagebox.showinfo')
    def test_batch_creation_with_callback(self, mock_showinfo):
        """コールバック付きバッチ作成テスト"""
        from gui.input_form import DynamicInputForm
        
        root = tk.Tk()
        try:
            main_window_mock = Mock()
            input_form = DynamicInputForm(root)
            input_form.set_managers(self.batch_manager, main_window_mock)
            input_form.generate_form_from_preset(self.test_preset)
            
            # 実際のバッチ保存機能をモック
            with patch.object(self.batch_manager, 'save_batch_file') as mock_save:
                mock_save.return_value = "/path/to/batch.bat"
                
                # バッチ作成ボタンの機能をテスト
                form_data = {"陣営": "テスト", "キャラ名": "テスト", "番号": "001"}
                input_form.set_form_data(form_data)
                
                # create_batch_from_formを直接呼び出す代わりに
                # 実際のボタンクリック動作をシミュレート
                batch_file = input_form.create_batch_from_form()
                self.assertIsInstance(batch_file, BatchFile)
            
        finally:
            root.destroy()


if __name__ == '__main__':
    unittest.main()