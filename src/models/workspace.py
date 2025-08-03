"""
ワークスペースモデル

作業ワークスペース管理のためのモデル
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """バリデーション結果"""
    is_valid: bool
    errors: List[str]


@dataclass
class InitializationResult:
    """初期化結果"""
    success: bool
    created_folders: List[str]
    error_message: str = ""


class Workspace:
    """ワークスペースオブジェクト"""
    
    def __init__(self, name: str, path: str, auto_create_folders: bool = True):
        self.name = name
        self.path = path
        self.auto_create_folders = auto_create_folders
    
    def get_required_subfolders(self) -> List[str]:
        """必須サブフォルダのリストを取得"""
        return ["rename_batches", "filter_batches", "display"]
    
    def validate(self) -> ValidationResult:
        """ワークスペースのバリデーション"""
        errors = []
        
        # パスの存在チェック
        if not os.path.exists(self.path):
            errors.append("path_not_exists")
        
        # 書き込み権限チェック
        if os.path.exists(self.path) and not os.access(self.path, os.W_OK):
            errors.append("no_write_permission")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def initialize(self) -> InitializationResult:
        """ワークスペースの初期化"""
        created_folders = []
        
        try:
            # メインフォルダ作成
            if not os.path.exists(self.path):
                os.makedirs(self.path)
                created_folders.append(self.path)
            
            # 必須サブフォルダ作成
            for subfolder in self.get_required_subfolders():
                subfolder_path = os.path.join(self.path, subfolder)
                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)
                    created_folders.append(subfolder_path)
            
            return InitializationResult(success=True, created_folders=created_folders)
        
        except Exception as e:
            return InitializationResult(success=False, created_folders=created_folders, 
                                      error_message=str(e))