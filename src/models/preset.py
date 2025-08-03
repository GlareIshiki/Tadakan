from datetime import datetime
from typing import Dict, List, Optional, Any
import re


class Preset:
    def __init__(
        self,
        name: str,
        fields: List[str],
        naming_pattern: str,
        default_values: Optional[Dict[str, str]] = None,
        target_extensions: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        id: Optional[str] = None,
        auto_generate_id: bool = False
    ):
        self.name = name
        self.fields = fields
        self.naming_pattern = naming_pattern
        self.default_values = default_values or {}
        self.target_extensions = target_extensions or [".jpg", ".png", ".gif", ".mp3", ".txt"]
        self.created_at = created_at or datetime.now().isoformat()
        
        # ID生成
        if auto_generate_id and not id:
            from utils.id_generator import PresetIDGenerator
            generator = PresetIDGenerator()
            self.id = generator.generate()
        elif not id and not auto_generate_id:
            # IDが指定されておらず、auto_generate_idもFalseの場合はデフォルトで生成
            from utils.id_generator import PresetIDGenerator
            generator = PresetIDGenerator()
            self.id = generator.generate()
        else:
            self.id = id
    
    def to_dict(self) -> Dict[str, Any]:
        """PresetをDict形式に変換"""
        return {
            "name": self.name,
            "fields": self.fields,
            "naming_pattern": self.naming_pattern,
            "default_values": self.default_values,
            "target_extensions": self.target_extensions,
            "created_at": self.created_at,
            "id": self.id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Preset':
        """Dict形式からPresetを作成"""
        return cls(
            name=data["name"],
            fields=data["fields"],
            naming_pattern=data["naming_pattern"],
            default_values=data.get("default_values", {}),
            target_extensions=data.get("target_extensions", [".jpg", ".png", ".gif", ".mp3", ".txt"]),
            created_at=data.get("created_at"),
            id=data.get("id")
        )
    
    def validate_naming_pattern(self) -> bool:
        """命名パターンのバリデーション"""
        # パターン内の{}で囲まれた項目を抽出
        pattern_fields = re.findall(r'\{([^}]+)\}', self.naming_pattern)
        
        # 全ての項目がfieldsに含まれているかチェック
        for field in pattern_fields:
            if field not in self.fields:
                return False
        
        return True
    
    def get_field_value(self, field_name: str, input_values: Dict[str, str]) -> Optional[str]:
        """フィールド値を取得（入力値 > デフォルト値 > None）"""
        if field_name in input_values and input_values[field_name]:
            return input_values[field_name]
        
        if field_name in self.default_values:
            return self.default_values[field_name]
        
        return None
    
    def generate_batch_filename(self, values: Dict[str, str]) -> str:
        """バッチファイル名を生成（プリセットID_陣営_キャラ名.bat形式）"""
        faction = values.get("陣営", "")
        character = values.get("キャラ名", "")
        return f"{self.id}_{faction}_{character}.bat"
    
    def generate_filename_with_sequence(self, values: Dict[str, str], sequence: str, extension: str) -> str:
        """連番付きファイル名を生成（プリセットID_陣営_キャラ名_A00001.ext形式）"""
        faction = values.get("陣営", "")
        character = values.get("キャラ名", "")
        return f"{self.id}_{faction}_{character}_{sequence}{extension}"