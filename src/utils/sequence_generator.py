"""
連番生成器

A00001形式の連番を生成
"""


class SequenceGenerator:
    """連番生成器"""
    
    def __init__(self):
        self.current_number = 0
    
    def next_sequence(self) -> str:
        """次の連番を生成（A00001形式）"""
        self.current_number += 1
        return f"A{self.current_number:05d}"
    
    def reset(self):
        """連番をリセット"""
        self.current_number = 0
    
    def get_current_number(self) -> int:
        """現在の連番を取得"""
        return self.current_number