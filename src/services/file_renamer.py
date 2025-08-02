import os
import re
from typing import List, Dict, Optional
from models.preset import Preset
from models.file_item import FileItem


class FileRenamer:
    def __init__(self):
        # Windows で使用できない文字
        self.invalid_chars = r'<>:"/\\|?*'
        self.invalid_char_pattern = re.compile(f'[{re.escape(self.invalid_chars)}]')
    
    def generate_filename(
        self,
        preset: Preset,
        input_values: Dict[str, str],
        original_extension: str,
        ng_words: Optional[List[str]] = None
    ) -> str:
        """プリセットに基づいて新しいファイル名を生成"""
        # 必須フィールドチェック
        missing_fields = []
        for field in preset.fields:
            value = preset.get_field_value(field, input_values)
            if value is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"必須項目が未入力です: {', '.join(missing_fields)}")
        
        # 命名パターンに値を適用
        filename = preset.naming_pattern
        for field in preset.fields:
            value = preset.get_field_value(field, input_values)
            filename = filename.replace(f"{{{field}}}", value)
        
        # 無効な文字をチェック
        if self.invalid_char_pattern.search(filename):
            raise ValueError(f"無効な文字が含まれています: {self.invalid_chars}")
        
        # NGワードチェック
        if ng_words:
            for ng_word in ng_words:
                if ng_word in filename:
                    raise ValueError(f"NGワードが含まれています: {ng_word}")
        
        # 拡張子を追加（正規化）
        if original_extension:
            extension = original_extension.lower()
        else:
            extension = ""
        
        return filename + extension
    
    def check_duplicate(
        self,
        preset: Preset,
        input_values: Dict[str, str],
        extension: str,
        target_directory: str
    ) -> bool:
        """重複するファイル名をチェック"""
        try:
            filename = self.generate_filename(preset, input_values, extension)
            file_path = os.path.join(target_directory, filename)
            return os.path.exists(file_path)
        except ValueError:
            return False
    
    def generate_preview_list(
        self,
        preset: Preset,
        file_paths: List[str],
        input_values: Dict[str, str]
    ) -> List[FileItem]:
        """複数ファイルのリネームプレビューを生成"""
        preview_list = []
        
        for i, file_path in enumerate(file_paths):
            file_item = FileItem.from_path(file_path)
            
            # 自動採番のため、番号フィールドがある場合は自動設定
            auto_input_values = input_values.copy()
            if "番号" in preset.fields:
                auto_input_values["番号"] = f"{i + 1:03d}"
            
            try:
                new_name = self.generate_filename(
                    preset,
                    auto_input_values,
                    file_item.get_original_extension()
                )
                file_item.new_name = new_name
            except ValueError as e:
                # エラーの場合は元の名前を保持
                file_item.new_name = file_item.original_name
                print(f"リネームエラー ({file_item.original_name}): {e}")
            
            preview_list.append(file_item)
        
        return preview_list
    
    def generate_filename_with_auto_number(
        self,
        preset: Preset,
        input_values: Dict[str, str],
        original_extension: str,
        target_directory: str,
        number_field: str = "番号"
    ) -> str:
        """自動採番機能付きファイル名生成"""
        if number_field not in preset.fields:
            # 番号フィールドがない場合は通常の生成
            return self.generate_filename(preset, input_values, original_extension)
        
        # 既存ファイルから次の番号を決定
        number = 1
        auto_input_values = input_values.copy()
        
        while True:
            auto_input_values[number_field] = f"{number:03d}"
            
            if not self.check_duplicate(preset, auto_input_values, original_extension, target_directory):
                break
            
            number += 1
            
            # 無限ループ防止
            if number > 9999:
                raise ValueError("自動採番の上限に達しました")
        
        return self.generate_filename(preset, auto_input_values, original_extension)
    
    def validate_filename_characters(self, filename: str) -> bool:
        """ファイル名の文字が有効かチェック"""
        return not self.invalid_char_pattern.search(filename)
    
    def sanitize_filename(self, filename: str, replacement: str = "_") -> str:
        """ファイル名の無効な文字を置換"""
        return self.invalid_char_pattern.sub(replacement, filename)