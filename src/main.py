#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tadakan - ファイル名一括変更ツール
ファイル名の一括変更を行うツール
"""

import sys
import os
import argparse
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.preset_manager import PresetManager
from src.services.file_renamer import FileRenamer
from src.services.batch_generator import BatchGenerator
from src.models.preset import Preset
from src.models.file_item import FileItem


class TadakanCLI:
    """Tadakan コマンドラインインターフェース"""
    
    def __init__(self):
        self.preset_manager = PresetManager()
        self.file_renamer = FileRenamer()
        self.batch_generator = BatchGenerator()
    
    def create_preset(self, name: str, fields: list, pattern: str, defaults: dict = None):
        """プリセット作成"""
        try:
            preset = self.preset_manager.create_preset(
                name=name,
                fields=fields,
                naming_pattern=pattern,
                default_values=defaults or {}
            )
            saved_path = self.preset_manager.save_preset(preset)
            print(f"プリセット '{name}' を保存しました: {saved_path}")
            return preset
        except Exception as e:
            print(f"プリセット作成エラー: {e}")
            return None
    
    def list_presets(self):
        """プリセット一覧表示"""
        presets = self.preset_manager.list_presets()
        if not presets:
            print("プリセットが見つかりません")
            return
        
        print("利用可能なプリセット:")
        for preset in presets:
            print(f"  - {preset.name}: {preset.naming_pattern}")
    
    def generate_batch(self, preset_name: str, input_values: dict, target_files: list, output_dir: str):
        """バッチファイル生成"""
        try:
            # プリセット取得
            preset = self.preset_manager.get_preset_by_name(preset_name)
            if not preset:
                print(f"プリセット '{preset_name}' が見つかりません")
                return None
            
            # ファイル処理
            file_items = []
            for file_path in target_files:
                if os.path.exists(file_path):
                    file_item = FileItem.from_path(file_path)
                    # 新しいファイル名生成
                    try:
                        new_name = self.file_renamer.generate_filename(
                            preset, input_values, file_item.get_original_extension()
                        )
                        file_item.new_name = new_name
                        file_items.append(file_item)
                    except Exception as e:
                        print(f"ファイル {file_path} の処理エラー: {e}")
                else:
                    print(f"ファイルが見つかりません: {file_path}")
            
            if not file_items:
                print("処理可能なファイルが見つかりません")
                return None
            
            # バッチファイル生成
            batch_content = self.batch_generator.generate_rename_batch(file_items, output_dir)
            batch_path = self.batch_generator.save_batch_file(
                batch_content, 
                "batch_files", 
                f"{preset_name}_rename.bat"
            )
            
            print(f"バッチファイルを生成しました: {batch_path}")
            print(f"処理ファイル数: {len(file_items)}")
            return batch_path
            
        except Exception as e:
            print(f"バッチ生成エラー: {e}")
            return None
    
    def demo_usage(self):
        """デモ実行"""
        print("\n=== Tadakan デモ実行 ===")
        print("=" * 40)
        
        # プリセット作成
        demo_preset = self.create_preset(
            name="デモ用",
            fields=["カテゴリ", "タイトル", "番号"],
            pattern="{カテゴリ}_{タイトル}_{番号}",
            defaults={"カテゴリ": "写真", "番号": "001"}
        )
        
        if demo_preset:
            print(f"\n=== 作成されたプリセット:")
            print(f"   名前: {demo_preset.name}")
            print(f"   パターン: {demo_preset.naming_pattern}")
            print(f"   フィールド: {demo_preset.fields}")
            print(f"   デフォルト値: {demo_preset.default_values}")
        
        print(f"\n=== 使用例:")
        print(f"   python src/main.py --preset デモ用 --values タイトル=テスト --files file1.jpg file2.png")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Tadakan - ファイル名一括変更ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # プリセット一覧表示:
  python src/main.py --list

  # デモ実行
  python src/main.py --demo

  # GUIインターフェース起動
  python src/main.py --gui

  # ワークスペース指定でGUI起動
  python src/main.py --gui --workspace "C:/MyWorkspace"

  # バッチファイル生成
  python src/main.py --preset "プリセット名" --values "フィールド1=値1,フィールド2=値2" --files file1.jpg file2.png --output ./renamed/
        """
    )
    
    parser.add_argument('--list', action='store_true', help='プリセット一覧表示')
    parser.add_argument('--demo', action='store_true', help='デモを実行')
    parser.add_argument('--gui', action='store_true', help='GUIインターフェースを起動')
    parser.add_argument('--workspace', type=str, help='ワークスペースディレクトリを指定')
    parser.add_argument('--preset', type=str, help='使用するプリセット名')
    parser.add_argument('--values', type=str, help='フィールド値 (例: "カテゴリ=写真,タイトル=テスト")')
    parser.add_argument('--files', nargs='+', help='対象ファイルリスト')
    parser.add_argument('--output', type=str, default='./output', help='出力ディレクトリ (デフォルト: ./output)')
    
    args = parser.parse_args()
    
    cli = TadakanCLI()
    
    # プリセット一覧表示
    if args.list:
        cli.list_presets()
        return
    
    # GUI起動
    if args.gui:
        try:
            # 既にプロジェクトルートは追加済み
            
            # GUIモジュールをインポート
            from src.gui import main_window as gui_module
            import tkinter as tk
            
            # tkinterdnd2の使用を試行
            try:
                from tkinterdnd2 import TkinterDnD
                root = TkinterDnD.Tk()
            except ImportError:
                root = tk.Tk()
            
            workspace_path = args.workspace if args.workspace else None
            app = gui_module.MainWindow(root, workspace_path)
            root.mainloop()
        except ImportError as e:
            print(f"GUIモジュールのインポートエラー: {e}")
            print("GUI機能を使用するには、必要なライブラリがインストールされていることを確認してください。")
        except Exception as e:
            print(f"GUI起動エラー: {e}")
        return
    
    # デモ実行
    if args.demo:
        cli.demo_usage()
        return
    
    # バッチ生成
    if args.preset and args.values and args.files:
        # 値の解析
        input_values = {}
        for pair in args.values.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                input_values[key.strip()] = value.strip()
        
        cli.generate_batch(args.preset, input_values, args.files, args.output)
        return
    
    # ヘルプ表示
    if len(sys.argv) == 1:
        print("=== Tadakan - ファイル名一括変更ツール ===")
        print("\n=== 使用方法:")
        print("python src/main.py --help")
        print("\n=== デモ実行:")
        print("python src/main.py --demo")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()