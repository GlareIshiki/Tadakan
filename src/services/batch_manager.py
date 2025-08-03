"""
バッチファイル管理サービス

ストック型バッチファイル管理システムのコアサービス
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.batch_file import BatchFile
from src.models.execution_result import ExecutionResult
from src.models.preset import Preset


class BatchManager:
    """バッチファイル管理マネージャー"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or ""
        self._batch_files = []
        self._execution_history = []
    
    def create_batch_file(self, preset: Preset, values: Dict[str, str]) -> BatchFile:
        """プリセットと値からバッチファイルを作成"""
        batch_file = BatchFile(
            preset_id=preset.id,
            preset_name=preset.name,
            field_values=values,
            target_extensions=preset.target_extensions,
            workspace_path=self.workspace_path
        )
        return batch_file
    
    def save_batch_file(self, batch_file: BatchFile) -> str:
        """バッチファイルをワークスペースに保存"""
        # rename_batchesフォルダに保存
        rename_batches_dir = os.path.join(self.workspace_path, "rename_batches")
        os.makedirs(rename_batches_dir, exist_ok=True)
        
        filename = batch_file.get_batch_filename()
        file_path = os.path.join(rename_batches_dir, filename)
        
        # バッチファイル内容を書き込み
        content = batch_file.generate_batch_content()
        with open(file_path, 'w', encoding='shift_jis') as f:
            f.write(content)
        
        return file_path
    
    def load_batch_files(self) -> List[BatchFile]:
        """ワークスペースからバッチファイル一覧を読み込み"""
        batch_files = []
        rename_batches_dir = os.path.join(self.workspace_path, "rename_batches")
        
        if not os.path.exists(rename_batches_dir):
            return batch_files
        
        for filename in os.listdir(rename_batches_dir):
            if filename.endswith('.bat'):
                try:
                    file_path = os.path.join(rename_batches_dir, filename)
                    with open(file_path, 'r', encoding='shift_jis') as f:
                        content = f.read()
                    
                    # プリセットIDを抽出
                    preset_id = None
                    for line in content.split('\n'):
                        if line.startswith('REM Preset ID:'):
                            preset_id = line.split(':', 1)[1].strip()
                            break
                    
                    if preset_id:
                        # ファイル名から値を推定
                        parts = filename.replace('.bat', '').split('_')
                        if len(parts) >= 3:
                            field_values = {
                                "陣営": parts[1] if len(parts) > 1 else "",
                                "キャラ名": parts[2] if len(parts) > 2 else ""
                            }
                            
                            batch_file = BatchFile(
                                preset_id=preset_id,
                                preset_name="",
                                field_values=field_values
                            )
                            batch_files.append(batch_file)
                except:
                    continue
        
        self._batch_files = batch_files
        return batch_files
    
    def search_batch_files(self, criteria: Dict[str, str]) -> List[BatchFile]:
        """バッチファイルを検索"""
        results = []
        
        for batch_file in self._batch_files:
            matches = True
            for key, value in criteria.items():
                if key in batch_file.field_values:
                    if value.lower() not in batch_file.field_values[key].lower():
                        matches = False
                        break
                else:
                    matches = False
                    break
            
            if matches:
                results.append(batch_file)
        
        return results
    
    def delete_batch_file(self, filename: str) -> bool:
        """バッチファイルを削除"""
        try:
            file_path = os.path.join(self.workspace_path, "rename_batches", filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except:
            return False
    
    def execute_batch_with_files(self, batch_file: BatchFile, file_list: List[str]) -> ExecutionResult:
        """ファイルリストでバッチを実行"""
        start_time = datetime.now()
        
        # フィルタリング
        target_files = batch_file.filter_target_files(file_list)
        
        # 実行結果を作成（実際の処理はシミュレート）
        result = ExecutionResult(
            batch_filename=batch_file.get_batch_filename(),
            executed_at=start_time.isoformat(),
            processed_files_count=len(target_files),
            success_count=len(target_files),
            error_count=0,
            processing_time_seconds=1.0
        )
        
        return result
    
    def record_execution_result(self, result: ExecutionResult):
        """実行結果を記録"""
        self._execution_history.append(result)
    
    def get_execution_history(self, batch_filename: str) -> List[ExecutionResult]:
        """指定したバッチファイルの実行履歴を取得"""
        return [r for r in self._execution_history if r.batch_filename == batch_filename]
    
    def generate_execution_report(self, days: int = 30) -> Dict[str, Any]:
        """実行レポートを生成"""
        report = {
            "total_executions": len(self._execution_history),
            "success_rate": 0.95,  # 仮の値
            "most_used_batches": [],
            "error_summary": {}
        }
        return report
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """使用統計を取得"""
        stats = {
            "total_batch_files": len(self._batch_files),
            "total_executions": len(self._execution_history),
            "average_files_per_execution": 5.0,  # 仮の値
            "most_popular_presets": []
        }
        return stats