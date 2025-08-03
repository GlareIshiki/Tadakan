"""
Tadakan 設定管理システム
"""

import os
import json
from typing import Dict, Any, List
from pathlib import Path


class Settings:
    """アプリケーション設定管理"""
    
    # デフォルト設定
    DEFAULT_SETTINGS = {
        "app": {
            "name": "Tadakan",
            "version": "0.1.0",
            "default_preset_dir": "presets",
            "default_batch_dir": "batch_files",
            "default_output_dir": "output"
        },
        "file_processing": {
            "supported_extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", 
                                   ".mp3", ".wav", ".flac", ".aac", ".ogg",
                                   ".txt", ".md", ".csv", ".json", ".xml",
                                   ".mp4", ".avi", ".mkv", ".mov", ".wmv"],
            "auto_numbering_limit": 9999,
            "invalid_chars": "<>:\"/\\|?*",
            "default_ng_words": ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", 
                               "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", 
                               "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", 
                               "LPT7", "LPT8", "LPT9"]
        },
        "batch": {
            "encoding": "shift_jis",
            "include_error_handling": True,
            "include_logging": False,
            "log_directory": "logs"
        },
        "ui": {
            "language": "ja",
            "theme": "default",
            "window_size": [800, 600]
        }
    }
    
    def __init__(self, config_file: str = "tadakan_config.json"):
        self.config_file = Path(config_file)
        self._settings = self.DEFAULT_SETTINGS.copy()
        self.load()
    
    def load(self):
        """設定ファイルを読み込み"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                    self._merge_settings(user_settings)
            except Exception as e:
                print(f"設定ファイル読み込みエラー: {e}")
                print("デフォルト設定を使用します")
    
    def save(self):
        """設定ファイルに保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")
    
    def _merge_settings(self, user_settings: Dict[str, Any]):
        """ユーザー設定をデフォルト設定にマージ"""
        def merge_dict(default: dict, user: dict):
            for key, value in user.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dict(default[key], value)
                else:
                    default[key] = value
        
        merge_dict(self._settings, user_settings)
    
    def get(self, key_path: str, default=None):
        """設定値を取得 (例: "app.name" または "file_processing.supported_extensions")"""
        keys = key_path.split('.')
        value = self._settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value):
        """設定値を設定"""
        keys = key_path.split('.')
        target = self._settings
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
    
    def get_app_name(self) -> str:
        """アプリケーション名取得"""
        return self.get("app.name", "Tadakan")
    
    def get_version(self) -> str:
        """バージョン取得"""
        return self.get("app.version", "0.1.0")
    
    def get_supported_extensions(self) -> List[str]:
        """サポート拡張子一覧取得"""
        return self.get("file_processing.supported_extensions", [])
    
    def get_default_preset_dir(self) -> str:
        """デフォルトプリセットディレクトリ取得"""
        return self.get("app.default_preset_dir", "presets")
    
    def get_default_batch_dir(self) -> str:
        """デフォルトバッチディレクトリ取得"""
        return self.get("app.default_batch_dir", "batch_files")
    
    def get_auto_numbering_limit(self) -> int:
        """自動採番上限取得"""
        return self.get("file_processing.auto_numbering_limit", 9999)
    
    def get_invalid_chars(self) -> str:
        """無効文字取得"""
        return self.get("file_processing.invalid_chars", "<>:\"/\\|?*")
    
    def get_ng_words(self) -> List[str]:
        """NGワード一覧取得"""
        return self.get("file_processing.default_ng_words", [])
    
    def get_batch_encoding(self) -> str:
        """バッチファイルエンコーディング取得"""
        return self.get("batch.encoding", "shift_jis")
    
    def is_error_handling_enabled(self) -> bool:
        """エラーハンドリング有効判定"""
        return self.get("batch.include_error_handling", True)
    
    def is_logging_enabled(self) -> bool:
        """ログ出力有効判定"""
        return self.get("batch.include_logging", False)


# グローバル設定インスタンス
settings = Settings()