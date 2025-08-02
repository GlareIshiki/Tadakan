import os
from typing import Dict, Any, Optional


class FileItem:
    def __init__(
        self,
        original_path: str,
        original_name: str,
        new_name: Optional[str] = None,
        file_size: Optional[int] = None,
        file_type: Optional[str] = None
    ):
        self.original_path = original_path
        self.original_name = original_name
        self.new_name = new_name
        self.file_size = file_size
        self.file_type = file_type
    
    def get_original_extension(self, normalize: bool = False) -> str:
        """元ファイルの拡張子を取得"""
        _, ext = os.path.splitext(self.original_name)
        return ext.lower() if normalize else ext
    
    def generate_new_path(self, target_directory: str) -> str:
        """新しいファイルパスを生成"""
        if not self.new_name:
            raise ValueError("new_name is not set")
        
        return os.path.join(target_directory, self.new_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """FileItemをDict形式に変換"""
        return {
            "original_path": self.original_path,
            "original_name": self.original_name,
            "new_name": self.new_name,
            "file_size": self.file_size,
            "file_type": self.file_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileItem':
        """Dict形式からFileItemを作成"""
        return cls(
            original_path=data["original_path"],
            original_name=data["original_name"],
            new_name=data.get("new_name"),
            file_size=data.get("file_size"),
            file_type=data.get("file_type")
        )
    
    def validate_file_exists(self) -> bool:
        """ファイル存在チェック"""
        return os.path.exists(self.original_path)
    
    @classmethod
    def from_path(cls, file_path: str) -> 'FileItem':
        """ファイルパスから情報を自動取得してFileItemを作成"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        original_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # ファイルタイプを拡張子から推測
        _, ext = os.path.splitext(original_name)
        ext_lower = ext.lower()
        
        if ext_lower in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            file_type = 'image'
        elif ext_lower in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            file_type = 'audio'
        elif ext_lower in ['.txt', '.md', '.csv', '.json', '.xml']:
            file_type = 'text'
        elif ext_lower in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
            file_type = 'video'
        else:
            file_type = 'other'
        
        return cls(
            original_path=file_path,
            original_name=original_name,
            file_size=file_size,
            file_type=file_type
        )