"""
バッチファイルモデル

ストック型バッチファイル管理システムのコアモデル
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class BatchFile:
    """バッチファイルオブジェクト"""
    
    def __init__(self, preset_id: str, preset_name: str, field_values: Dict[str, str], 
                 target_extensions: Optional[List[str]] = None, workspace_path: Optional[str] = None):
        self.preset_id = preset_id
        self.preset_name = preset_name
        self.field_values = field_values
        self.target_extensions = target_extensions or []
        self.workspace_path = workspace_path or ""
        self.current_sequence = 0
        self.created_at = datetime.now()
    
    def get_batch_filename(self) -> str:
        """バッチファイル名を生成（プリセットID_陣営_キャラ名.bat形式）"""
        faction = self.field_values.get("陣営", "")
        character = self.field_values.get("キャラ名", "")
        return f"{self.preset_id}_{faction}_{character}.bat"
    
    def generate_batch_content(self) -> str:
        """バッチファイルの内容を生成"""
        content_lines = [
            "@echo off",
            f"REM Preset ID: {self.preset_id}",
            f"REM Generated: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "setlocal enabledelayedexpansion",
            "",
            f"REM Target extensions: {', '.join(self.target_extensions)}",
            ""
        ]
        
        # 拡張子別に移動コマンドを生成
        for ext in self.target_extensions:
            content_lines.extend([
                f"for %%f in (*{ext}) do (",
                f"    echo Moving %%f...",
                f"    move \"%%f\" \"{self.get_batch_filename().replace('.bat', '')}\\\"",
                ")",
                ""
            ])
        
        content_lines.extend([
            "echo ファイル処理が完了しました。",
            "endlocal"
        ])
        
        return "\n".join(content_lines)
    
    def get_next_sequence(self) -> str:
        """次の連番を取得（A00001形式）"""
        self.current_sequence += 1
        return f"A{self.current_sequence:05d}"
    
    def filter_target_files(self, file_list: List[str]) -> List[str]:
        """対象拡張子でファイルをフィルタリング"""
        if "*" in self.target_extensions:
            return file_list
        
        filtered_files = []
        for file_path in file_list:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in self.target_extensions:
                filtered_files.append(file_path)
        
        return filtered_files