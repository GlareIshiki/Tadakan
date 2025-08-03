import os
import json
from typing import List, Dict, Any, Optional
from models.preset import Preset
from utils.id_generator import PresetIDGenerator


class PresetManager:
    def __init__(self, presets_directory: str = "presets"):
        self.presets_directory = presets_directory
        self.id_generator = PresetIDGenerator()
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """プリセットディレクトリが存在することを確認"""
        if not os.path.exists(self.presets_directory):
            os.makedirs(self.presets_directory)
    
    def create_preset(
        self,
        name: str,
        fields: List[str],
        naming_pattern: str,
        default_values: Optional[Dict[str, str]] = None,
        target_extensions: Optional[List[str]] = None
    ) -> Preset:
        """新しいプリセットを作成"""
        if not name or not name.strip():
            raise ValueError("プリセット名は必須です")
        
        if not fields:
            raise ValueError("フィールドリストは必須です")
        
        if not naming_pattern or not naming_pattern.strip():
            raise ValueError("命名パターンは必須です")
        
        preset = Preset(
            name=name.strip(),
            fields=fields,
            naming_pattern=naming_pattern,
            default_values=default_values,
            target_extensions=target_extensions
        )
        
        # 命名パターンのバリデーション
        if not preset.validate_naming_pattern():
            raise ValueError("命名パターンに存在しないフィールドが含まれています")
        
        return preset
    
    def save_preset(self, preset: Preset) -> str:
        """プリセットをJSONファイルに保存"""
        filename = f"{preset.name}.json"
        file_path = os.path.join(self.presets_directory, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(preset.to_dict(), f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def load_preset(self, file_path: str) -> Preset:
        """JSONファイルからプリセットを読み込み"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"プリセットファイルが見つかりません: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Preset.from_dict(data)
    
    def list_presets(self) -> List[Preset]:
        """利用可能なプリセット一覧を取得"""
        presets = []
        
        if not os.path.exists(self.presets_directory):
            return presets
        
        for filename in os.listdir(self.presets_directory):
            if filename.endswith('.json'):
                file_path = os.path.join(self.presets_directory, filename)
                try:
                    preset = self.load_preset(file_path)
                    presets.append(preset)
                except Exception as e:
                    # ログに記録して継続
                    print(f"プリセット読み込みエラー ({filename}): {e}")
                    continue
        
        return presets
    
    def delete_preset(self, preset_name: str) -> bool:
        """プリセットを削除"""
        filename = f"{preset_name}.json"
        file_path = os.path.join(self.presets_directory, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
    
    def export_preset(self, preset: Preset, export_path: str):
        """プリセットをエクスポート"""
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(preset.to_dict(), f, ensure_ascii=False, indent=2)
    
    def import_preset(self, import_path: str) -> Preset:
        """プリセットをインポート"""
        preset = self.load_preset(import_path)
        
        # インポートしたプリセットを保存
        self.save_preset(preset)
        
        return preset
    
    def get_preset_by_name(self, name: str) -> Optional[Preset]:
        """名前でプリセットを取得"""
        filename = f"{name}.json"
        file_path = os.path.join(self.presets_directory, filename)
        
        if os.path.exists(file_path):
            return self.load_preset(file_path)
        
        return None
    
    def create_preset_with_id(self, preset_data: Dict[str, Any]) -> Preset:
        """プリセットIDを自動生成してプリセットを作成"""
        # 既存IDを収集
        existing_ids = set()
        for preset in self.list_presets():
            if preset.id:
                existing_ids.add(preset.id)
        
        # 一意のIDを生成
        new_id = self.id_generator.generate_unique(existing_ids)
        
        # プリセット作成
        preset = Preset(
            name=preset_data["name"],
            fields=preset_data["fields"],
            naming_pattern=preset_data["naming_pattern"],
            default_values=preset_data.get("default_values", {}),
            target_extensions=preset_data.get("target_extensions"),
            id=new_id
        )
        
        return preset
    
