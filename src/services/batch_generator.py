import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from models.file_item import FileItem


class BatchGenerator:
    def __init__(self):
        self.encoding = 'shift_jis'  # Windows batファイル用
    
    def generate_rename_batch(
        self,
        file_items: List[FileItem],
        target_directory: str,
        include_error_handling: bool = False,
        log_file: Optional[str] = None
    ) -> str:
        """リネーム用バッチファイルを生成"""
        if not file_items:
            raise ValueError("ファイルリストが空です")
        
        if not target_directory or not target_directory.strip():
            raise ValueError("ターゲットディレクトリが指定されていません")
        
        lines = []
        lines.append("@echo off")
        lines.append("chcp 65001 > nul")  # UTF-8コードページ設定
        
        # ログ開始
        if log_file:
            lines.append(f'echo 開始時刻: %date% %time% >> "{log_file}"')
        
        # ターゲットディレクトリ作成
        lines.append(f'if not exist "{target_directory}" mkdir "{target_directory}"')
        lines.append("")
        
        # 各ファイルのリネーム・移動処理
        for file_item in file_items:
            if not file_item.new_name:
                continue
            
            # ファイル名をエスケープ
            original_name = self._escape_filename(file_item.original_name)
            new_name = self._escape_filename(file_item.new_name)
            
            # リネームコマンド
            lines.append(f'ren "{original_name}" "{new_name}"')
            
            # エラーハンドリング
            if include_error_handling:
                lines.append("if errorlevel 1 (")
                lines.append(f'    echo エラーが発生しました: {original_name}')
                lines.append("    pause")
                lines.append("    goto :eof")
                lines.append(")")
            
            # 移動コマンド
            lines.append(f'move "{new_name}" "{target_directory}"')
            
            if include_error_handling:
                lines.append("if errorlevel 1 (")
                lines.append(f'    echo 移動エラーが発生しました: {new_name}')
                lines.append("    pause")
                lines.append("    goto :eof")
                lines.append(")")
            
            lines.append("")
        
        # ログ終了
        if log_file:
            lines.append(f'echo 完了時刻: %date% %time% >> "{log_file}"')
        
        lines.append("echo 処理が完了しました。")
        lines.append("pause")
        
        return "\n".join(lines)
    
    def generate_filter_batch(
        self,
        filter_conditions: Dict[str, str],
        source_directory: str,
        temp_directory: str
    ) -> str:
        """フィルタ用バッチファイルを生成"""
        lines = []
        lines.append("@echo off")
        lines.append("chcp 65001 > nul")
        
        # 表示用ディレクトリ作成
        lines.append(f'if not exist "{temp_directory}" mkdir "{temp_directory}"')
        lines.append("")
        
        # フィルタ条件に基づくファイル移動
        for field, condition in filter_conditions.items():
            if "*" in condition:
                # ワイルドカード対応
                pattern = condition.replace("*", "*")
                lines.append(f'for %%f in ("{source_directory}\\*{pattern}*") do (')
                lines.append(f'    move "%%f" "{temp_directory}"')
                lines.append(")")
            else:
                # 完全一致
                lines.append(f'for %%f in ("{source_directory}\\*{condition}*") do (')
                lines.append(f'    move "%%f" "{temp_directory}"')
                lines.append(")")
        
        lines.append("")
        lines.append("echo フィルタリングが完了しました。")
        lines.append("pause")
        
        return "\n".join(lines)
    
    def generate_restore_batch(
        self,
        moved_files: List[str],
        temp_directory: str,
        original_directory: str
    ) -> str:
        """フィルタ解除（復元）用バッチファイルを生成"""
        lines = []
        lines.append("@echo off")
        lines.append("chcp 65001 > nul")
        
        # 各ファイルを元のディレクトリに戻す
        for filename in moved_files:
            escaped_filename = self._escape_filename(filename)
            lines.append(f'move "{temp_directory}\\{escaped_filename}" "{original_directory}"')
        
        lines.append("")
        lines.append("echo 復元が完了しました。")
        lines.append("pause")
        
        return "\n".join(lines)
    
    def generate_undo_batch(self, undo_operations: List[Dict[str, str]]) -> str:
        """アンドゥ用バッチファイルを生成"""
        lines = []
        lines.append("@echo off")
        lines.append("chcp 65001 > nul")
        
        for operation in undo_operations:
            current_name = self._escape_filename(operation['current_name'])
            original_name = self._escape_filename(operation['original_name'])
            directory = operation.get('directory', '.')
            
            # カレントディレクトリを変更
            lines.append(f'cd /d "{directory}"')
            lines.append(f'ren "{current_name}" "{original_name}"')
        
        lines.append("")
        lines.append("echo アンドゥが完了しました。")
        lines.append("pause")
        
        return "\n".join(lines)
    
    def save_batch_file(
        self,
        batch_content: str,
        output_directory: str,
        filename: str
    ) -> str:
        """バッチファイルをディスクに保存"""
        if not filename.endswith('.bat'):
            filename += '.bat'
        
        output_path = os.path.join(output_directory, filename)
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(output_directory, exist_ok=True)
        
        with open(output_path, 'w', encoding=self.encoding) as f:
            f.write(batch_content)
        
        return output_path
    
    def generate_batch_metadata(
        self,
        preset_name: str,
        operation_type: str,
        file_count: int,
        target_directory: str
    ) -> Dict[str, Any]:
        """バッチファイルのメタデータを生成"""
        return {
            "preset_name": preset_name,
            "operation_type": operation_type,
            "file_count": file_count,
            "target_directory": target_directory,
            "created_at": datetime.now().isoformat()
        }
    
    def _escape_filename(self, filename: str) -> str:
        """特殊文字を含むファイル名をエスケープ"""
        # バッチファイルで問題となる文字をエスケープ
        special_chars = ['&', '(', ')', '[', ']', '{', '}', '^', '=', ';', '!', "'", '+', ',', '`', '~']
        
        escaped = filename
        for char in special_chars:
            if char in escaped:
                escaped = escaped.replace(char, f'^{char}')
        
        return escaped