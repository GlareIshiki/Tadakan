"""
プリセットID生成器

B63EF9形式の6桁英数字ランダムIDを生成
"""

import random
import string
import re
from typing import Set


class PresetIDGenerator:
    """プリセットID生成器"""
    
    def __init__(self):
        # 英数字（大文字）から生成
        self.chars = string.ascii_uppercase + string.digits
    
    def generate(self) -> str:
        """6桁英数字ランダムIDを生成"""
        return self._generate_random_id()
    
    def _generate_random_id(self) -> str:
        """内部的なランダムID生成"""
        # 数字のみ、文字のみを避けるため、最低1つずつ含める
        letters = string.ascii_uppercase
        digits = string.digits
        
        # 最低1文字と1数字を含む
        id_chars = [
            random.choice(letters),
            random.choice(digits)
        ]
        
        # 残り4文字をランダム生成
        for _ in range(4):
            id_chars.append(random.choice(self.chars))
        
        # シャッフルして6桁IDに
        random.shuffle(id_chars)
        return ''.join(id_chars)
    
    def generate_unique(self, existing_ids: Set[str]) -> str:
        """既存IDと重複しない一意のIDを生成"""
        max_attempts = 1000
        
        for _ in range(max_attempts):
            new_id = self._generate_random_id()
            if new_id not in existing_ids:
                return new_id
        
        # 極稀に重複回避できない場合の処理
        raise RuntimeError("Failed to generate unique ID after maximum attempts")
    
    def validate_preset_id(self, preset_id: str) -> bool:
        """プリセットIDのバリデーション"""
        # 6桁英数字チェック
        if not re.match(r'^[A-Z0-9]{6}$', preset_id):
            return False
        
        # 数字のみ、文字のみを除外
        if preset_id.isdigit() or preset_id.isalpha():
            return False
        
        return True
    
    def validate(self, preset_id: str) -> bool:
        """バリデーションのエイリアス"""
        return self.validate_preset_id(preset_id)