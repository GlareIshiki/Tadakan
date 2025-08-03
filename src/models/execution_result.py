"""
実行結果モデル

バッチファイル実行結果を表現するモデル
"""

from datetime import datetime
from typing import Optional


class ExecutionResult:
    """バッチファイル実行結果"""
    
    def __init__(self, batch_filename: str, executed_at: Optional[str] = None,
                 processed_files_count: int = 0, success_count: int = 0, 
                 error_count: int = 0, processing_time_seconds: float = 0.0,
                 started_at: Optional[str] = None, completed_at: Optional[str] = None):
        self.batch_filename = batch_filename
        self.executed_at = executed_at or datetime.now().isoformat()
        self.processed_files_count = processed_files_count
        self.success_count = success_count
        self.error_count = error_count
        self.processing_time_seconds = processing_time_seconds
        self.started_at = started_at
        self.completed_at = completed_at
    
    def get_success_rate(self) -> float:
        """成功率を計算"""
        if self.processed_files_count == 0:
            return 0.0
        return self.success_count / self.processed_files_count
    
    def get_duration_seconds(self) -> float:
        """実行時間を計算（started_atとcompleted_atから）"""
        if not self.started_at or not self.completed_at:
            return self.processing_time_seconds
        
        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            return (end - start).total_seconds()
        except:
            return self.processing_time_seconds