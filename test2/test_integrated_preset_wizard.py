"""
統合プリセットウィザードのテストケース

1画面統合形式のプリセット作成ウィザードをTDDで実装
"""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# テスト用パス設定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gui.preset_wizard import PresetWizard
from models.preset import Preset
from services.preset_manager import PresetManager


class TestIntegratedPresetWizard:
    """統合プリセットウィザードのテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行"""
        self.root = tk.Tk()
        self.root.withdraw()  # テスト時は非表示
        
    def teardown_method(self):
        """各テストメソッドの後に実行"""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_wizard_window_creation(self):
        """ウィザードウィンドウが正常に作成されること"""
        wizard = PresetWizard(self.root)
        
        # ウィンドウが作成されること
        assert wizard.dialog is not None
        assert wizard.dialog.winfo_exists()
        
        # タイトルが設定されていること
        assert "プリセット作成" in wizard.dialog.title()
        
        wizard.dialog.destroy()
    
    def test_all_input_fields_present(self):
        """全ての入力フィールドが1画面に表示されること"""
        wizard = PresetWizard(self.root)
        
        # 基本情報フィールド
        assert hasattr(wizard, 'name_entry')
        assert hasattr(wizard, 'description_entry')
        
        # 拡張子フィールド
        assert hasattr(wizard, 'extensions_entry')
        
        # 命名規則フィールド
        assert hasattr(wizard, 'naming_pattern_entry')
        
        # カスタムフィールド管理
        assert hasattr(wizard, 'fields_frame')
        assert hasattr(wizard, 'add_field_button')
        
        # 操作ボタン
        assert hasattr(wizard, 'save_button')
        assert hasattr(wizard, 'cancel_button')
        
        wizard.dialog.destroy()
    
    def test_custom_fields_management(self):
        """カスタムフィールドの追加・削除ができること"""
        wizard = PresetWizard(self.root)
        
        # 初期状態ではカスタムフィールドがないこと
        initial_field_count = len(wizard.custom_fields)
        assert initial_field_count == 0
        
        # フィールド追加
        wizard._add_custom_field()
        assert len(wizard.custom_fields) == initial_field_count + 1
        
        # フィールドが正しく追加されていること
        field_widgets = wizard.custom_fields[0]
        assert 'name_entry' in field_widgets
        assert 'type_combobox' in field_widgets
        assert 'delete_button' in field_widgets
        
        # フィールド削除
        wizard._remove_custom_field(0)
        assert len(wizard.custom_fields) == initial_field_count
        
        wizard.dialog.destroy()
    
    def test_field_validation(self):
        """入力フィールドのバリデーションが動作すること"""
        wizard = PresetWizard(self.root)
        
        # 空の名前でバリデーションエラー
        wizard.name_entry.delete(0, tk.END)
        assert not wizard._validate_inputs()
        
        # 名前を入力
        wizard.name_entry.insert(0, "テストプリセット")
        
        # 空の命名規則でバリデーションエラー
        wizard.naming_pattern_entry.delete(0, tk.END)
        assert not wizard._validate_inputs()
        
        # 命名規則を入力
        wizard.naming_pattern_entry.insert(0, "{id}_{faction}_{character}")
        
        # 全て入力されていればバリデーション成功
        assert wizard._validate_inputs()
        
        wizard.dialog.destroy()
    
    def test_preset_data_collection(self):
        """プリセットデータが正しく収集されること"""
        wizard = PresetWizard(self.root)
        
        # テストデータ入力
        wizard.name_entry.insert(0, "テストプリセット")
        wizard.description_entry.insert(0, "テスト用の説明")
        wizard.extensions_entry.insert(0, "jpg,png,gif")
        wizard.naming_pattern_entry.insert(0, "{id}_{faction}_{character}")
        
        # カスタムフィールド追加
        wizard._add_custom_field()
        wizard.custom_fields[0]['name_entry'].insert(0, "陣営")
        wizard.custom_fields[0]['type_combobox'].set("text")
        
        wizard._add_custom_field()
        wizard.custom_fields[1]['name_entry'].insert(0, "キャラ名")
        wizard.custom_fields[1]['type_combobox'].set("text")
        
        # データ収集
        collected_data = wizard._collect_preset_data()
        
        # 基本情報が正しく収集されること
        assert collected_data['name'] == "テストプリセット"
        assert collected_data['description'] == "テスト用の説明"
        assert collected_data['target_extensions'] == ["jpg", "png", "gif"]
        assert collected_data['naming_pattern'] == "{id}_{faction}_{character}"
        
        # カスタムフィールドが正しく収集されること（List形式）
        assert len(collected_data['fields']) == 2
        assert "陣営" in collected_data['fields']
        assert "キャラ名" in collected_data['fields']
        
        wizard.dialog.destroy()
    
    @patch('gui.preset_wizard.PresetIDGenerator')
    def test_preset_creation_with_id_generation(self, mock_id_generator):
        """プリセット作成時にIDが自動生成されること"""
        mock_generator_instance = Mock()
        mock_generator_instance.generate_unique.return_value = "A1B2C3"
        mock_id_generator.return_value = mock_generator_instance
        
        wizard = PresetWizard(self.root)
        
        # テストデータ入力
        wizard.name_entry.insert(0, "テストプリセット")
        wizard.naming_pattern_entry.insert(0, "{id}_{faction}_{character}")
        
        # プリセット作成
        preset = wizard._create_preset_from_data()
        
        # IDが生成されていること
        assert preset.id == "A1B2C3"
        assert preset.name == "テストプリセット"
        assert preset.naming_pattern == "{id}_{faction}_{character}"
        
        wizard.dialog.destroy()
    
    def test_edit_mode_data_loading(self):
        """編集モード時に既存データが正しく読み込まれること"""
        # 編集用プリセットデータ
        existing_preset = Preset(
            id="TEST01",
            name="既存プリセット",
            fields=["陣営", "キャラ名"],
            naming_pattern="{id}_{faction}_{character}",
            target_extensions=["jpg", "png"]
        )
        # description属性を後から追加（Presetモデルの制約対応）
        existing_preset.description = "編集テスト"
        
        wizard = PresetWizard(self.root, edit_preset=existing_preset)
        
        # 基本情報が正しく読み込まれること
        assert wizard.name_entry.get() == "既存プリセット"
        assert wizard.description_entry.get() == "編集テスト"
        assert wizard.naming_pattern_entry.get() == "{id}_{faction}_{character}"
        assert wizard.extensions_entry.get() == "jpg,png"
        
        # カスタムフィールドが正しく読み込まれること
        assert len(wizard.custom_fields) == 2
        
        wizard.dialog.destroy()
    
    @patch('tkinter.messagebox.showinfo')
    @patch('gui.preset_wizard.PresetIDGenerator')
    def test_save_button_functionality(self, mock_id_generator, mock_messagebox):
        """保存ボタンが正常に動作すること"""
        mock_generator_instance = Mock()
        mock_generator_instance.generate_unique.return_value = "SAVE01"
        mock_id_generator.return_value = mock_generator_instance
        
        wizard = PresetWizard(self.root)
        
        # テストデータ入力
        wizard.name_entry.insert(0, "保存テスト")
        wizard.naming_pattern_entry.insert(0, "{id}_{character}")
        
        # コールバック設定
        mock_callback = Mock()
        wizard.set_save_callback(mock_callback)
        
        # 保存実行
        wizard._on_save_clicked()
        
        # プリセットが作成されていること
        assert wizard.created_preset is not None
        assert wizard.created_preset.id == "SAVE01"
        assert wizard.created_preset.name == "保存テスト"
        
        # コールバックが呼ばれていること
        mock_callback.assert_called_once_with(wizard.created_preset)
        
        wizard.dialog.destroy()
    
    def test_cancel_button_functionality(self):
        """キャンセルボタンが正常に動作すること"""
        wizard = PresetWizard(self.root)
        
        # データ入力
        wizard.name_entry.insert(0, "キャンセルテスト")
        
        # キャンセル実行
        wizard._on_cancel_clicked()
        
        # プリセットが作成されていないこと
        assert wizard.created_preset is None
        
        # ダイアログが閉じられること（ウィンドウが存在しない）
        assert not wizard.dialog.winfo_exists()


class TestPresetSelectionToBatchCreationWorkflow:
    """プリセット選択からバッチ作成までのワークフローテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行"""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def teardown_method(self):
        """各テストメソッドの後に実行"""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    @patch('services.preset_manager.PresetManager')
    @patch('services.batch_manager.BatchManager')
    def test_preset_list_display(self, mock_batch_manager, mock_preset_manager):
        """プリセット一覧が正しく表示されること"""
        # モックプリセットデータ
        mock_presets = [
            Preset(id="PRESET1", name="アニメキャラ整理", fields=["陣営", "キャラ名"], naming_pattern="{id}_{faction}_{character}"),
            Preset(id="PRESET2", name="画像ファイル分類", fields=["カテゴリ", "日付"], naming_pattern="{id}_{category}_{date}")
        ]
        mock_preset_manager.list_presets.return_value = mock_presets
        
        from gui.preset_panel import PresetPanel
        preset_panel = PresetPanel(self.root)
        preset_panel.set_managers(mock_preset_manager, None)
        
        # プリセット一覧読み込み
        preset_panel.refresh_preset_list()
        
        # リストボックスにプリセットが表示されること
        assert preset_panel.preset_listbox.size() == 2
        assert "PRESET1 - アニメキャラ整理" in preset_panel.preset_listbox.get(0)
        assert "PRESET2 - 画像ファイル分類" in preset_panel.preset_listbox.get(1)
    
    @patch('services.preset_manager.PresetManager')
    @patch('services.batch_manager.BatchManager')
    def test_preset_selection_triggers_form_generation(self, mock_batch_manager, mock_preset_manager):
        """プリセット選択時に動的フォームが生成されること"""
        # テスト用プリセット
        test_preset = Preset(
            id="TEST01",
            name="テストプリセット",
            fields=["陣営", "キャラ名"],
            naming_pattern="{id}_{faction}_{character}"
        )
        
        from gui.input_form import DynamicInputForm
        input_form = DynamicInputForm(self.root)
        
        # プリセットからフォーム生成
        input_form.generate_form_from_preset(test_preset)
        
        # フィールドが生成されていること
        assert len(input_form.input_fields) == 2
        assert "陣営" in input_form.input_fields
        assert "キャラ名" in input_form.input_fields
    
    @patch('services.batch_manager.BatchManager')
    def test_batch_file_creation_from_form_data(self, mock_batch_manager):
        """フォームデータからバッチファイルが作成されること"""
        from gui.input_form import DynamicInputForm
        
        # テスト用プリセット
        test_preset = Preset(
            id="BATCH01",
            name="バッチテスト",
            fields=["陣営", "キャラ名"],
            naming_pattern="{id}_{faction}_{character}"
        )
        
        input_form = DynamicInputForm(self.root)
        input_form.set_managers(mock_batch_manager, None)
        input_form.generate_form_from_preset(test_preset)
        input_form.current_preset = test_preset
        
        # フォームに値入力
        input_form.input_fields["陣営"].set("テスト陣営")
        input_form.input_fields["キャラ名"].set("テストキャラ")
        
        # バッチファイル作成モック設定
        mock_batch_file = Mock()
        mock_batch_file.filename = "BATCH01_テスト陣営_テストキャラ.bat"
        mock_batch_manager.create_batch_file.return_value = mock_batch_file
        
        # バッチ作成実行
        input_form._on_create_batch_clicked()
        
        # BatchManagerが正しい引数で呼ばれること
        mock_batch_manager.create_batch_file.assert_called_once()
        call_args = mock_batch_manager.create_batch_file.call_args
        assert call_args[0][0] == test_preset  # プリセット
        assert call_args[0][1]["陣営"] == "テスト陣営"  # 値
        assert call_args[0][1]["キャラ名"] == "テストキャラ"  # 値
    
    def test_integrated_workflow_validation(self):
        """統合ワークフローの段階的検証"""
        # 1. プリセット作成ウィザードでプリセット作成
        # 2. プリセット一覧に表示
        # 3. プリセット選択で動的フォーム生成
        # 4. フォーム入力でバッチファイル作成
        # このワークフロー全体が正常に動作することを確認
        
        # この統合テストは実装後に詳細を追加
        assert True  # プレースホルダー


if __name__ == "__main__":
    pytest.main([__file__, "-v"])