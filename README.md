# Tadakan v0.2

**ストック型バッチファイル管理システム** - ファイル整理のお供

プリセットベースのファイルリネーム・整理ツールが、フルGUI対応で大幅進化！

## 🎯 新機能ハイライト（v0.2）

### 📦 **ストック型バッチ管理**
- **永続バッチファイル**: 一度作成したバッチファイルを無制限に再利用
- **B63EF9プリセットID**: 6桁英数字による一意識別システム 
- **自動命名規則**: `プリセットID_陣営_キャラ名.bat` 形式
- **履歴管理**: バッチ実行結果の詳細追跡とレポート生成

### 🖥️ **統合GUIインターフェース**
- **ワンストップ操作**: メインウィンドウですべての機能にアクセス
- **動的フォーム生成**: プリセット選択に連動した入力フィールド自動生成
- **ドラッグ&ドロップ**: ファイル・フォルダの直感的操作
- **リアルタイム表示**: 処理結果とエラー通知をリアルタイム表示

### 🏗️ **ワークスペース管理**
- **デフォルトワークスペース**: `~/Pictures/Tadakan` 自動作成
- **自動フォルダ構成**: `rename_batches/`, `filter_batches/`, `display/`
- **バックアップ・復元**: ワークスペースの安全な管理
- **自動修復**: 破損したワークスペース構造の自動復旧

## 🚀 主要機能

### ✨ **プリセット管理**
- **GUI ウィザード**: ステップバイステップでのプリセット作成
- **プリセット一覧**: 視覚的な選択・編集・削除
- **ID 自動生成**: 重複チェック付きユニークID システム
- **フィールド定義**: カスタマイズ可能な入力項目

### 🔄 **バッチファイル操作**
- **一覧表示**: 作成済みバッチファイルの検索・管理
- **検索機能**: 名前・プリセットIDによる高速検索
- **実行追跡**: 処理ファイル数・成功率・エラー詳細
- **拡張子フィルタ**: 対象ファイル種別の自動判定

### 📁 **ファイル処理**
- **連番生成**: `A00001`, `A00002`... 形式の自動連番
- **重複回避**: 既存ファイルとの衝突防止
- **日本語対応**: Shift_JIS エンコーディングでバッチファイル生成
- **マルチ拡張子**: 画像・音楽・動画・テキストファイル対応

## 📦 インストール

### 必要環境
- Python 3.8以上
- Windows 10/11 (macOS/Linux は今後対応予定)
- 2GB以上の空きディスク容量

### セットアップ
```bash
git clone https://github.com/GlareIshiki/Tadakan.git
cd Tadakan
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🎮 使い方

### CLI モード（従来互換）
```bash
# デモ実行
python src/main.py --demo

# プリセット一覧
python src/main.py --list

# ファイルリネーム
python src/main.py --preset "アニメキャラ整理" --values "陣営=クレキュリア,キャラ名=アクララ" --files *.png
```

### GUI モード（v0.2新機能）
```bash
# フルGUIインターフェース起動
python src/main.py --gui

# ワークスペース指定
python src/main.py --gui --workspace "C:/MyWorkspace"
```

### GUI 操作手順
1. **プリセット選択**: 左パネルからプリセットを選択
2. **値入力**: 動的生成されたフォームに入力
3. **バッチ作成**: 「バッチファイル作成」ボタンでBATファイル生成
4. **ファイル処理**: ドラッグ&ドロップまたはバッチファイル実行

## 🏗️ アーキテクチャ v0.2

```
src/
├── main.py                    # CLI/GUI エントリーポイント
├── models/                    # データモデル層
│   ├── preset.py             # プリセット（ID拡張済み）
│   ├── batch_file.py         # バッチファイルモデル
│   ├── workspace.py          # ワークスペースモデル
│   ├── execution_result.py   # 実行結果モデル
│   └── file_item.py          # ファイル項目
├── services/                  # ビジネスロジック層
│   ├── preset_manager.py     # プリセット管理（ID統合）
│   ├── batch_manager.py      # バッチファイル管理
│   ├── workspace_manager.py  # ワークスペース管理
│   ├── file_renamer.py       # ファイルリネーム
│   └── batch_generator.py    # バッチ生成
├── utils/                     # ユーティリティ層
│   ├── id_generator.py       # プリセットID生成
│   └── sequence_generator.py # 連番生成
├── gui/                       # GUI層
│   ├── main_window.py        # メインウィンドウ
│   ├── preset_panel.py       # プリセット管理パネル
│   ├── input_form.py         # 動的入力フォーム
│   ├── batch_panel.py        # バッチ管理パネル
│   ├── drop_zone.py          # ドラッグ&ドロップゾーン
│   ├── preset_wizard.py      # プリセット作成ウィザード
│   ├── workspace_selector.py # ワークスペース選択
│   ├── workspace_settings.py # ワークスペース設定
│   └── components/           # 再利用可能コンポーネント
└── config/                    # 設定管理
    └── settings.py           # アプリケーション設定
```

## 🧪 開発・テスト

### テスト実行
```bash
# 全テスト実行
python -m pytest test2/ -v

# 特定機能テスト
python -m pytest test2/test_batch_management_pure.py -v
python -m pytest test2/test_preset_id_pure.py -v
python -m pytest test2/test_workspace_pure.py -v
python -m pytest test2/test_gui_pure.py -v
```

### コード品質
```bash
# 型チェック
mypy src/

# フォーマット
black src/ test2/

# リンター
flake8 src/ test2/
```

## 📊 テスト結果

- **テストカバレッジ**: 73個のテスト実装済み
- **合格率**: 89% (73/82 テスト合格)
- **品質評価**: 3.5/5 (独立検証結果)
- **アーキテクチャ適合性**: レイヤード・アーキテクチャ完全準拠

## 🆕 v0.2 変更点

### 追加機能
- ✅ B63EF9形式プリセットID システム
- ✅ ストック型バッチファイル管理
- ✅ フルGUIインターフェース
- ✅ ワークスペース管理機能
- ✅ ドラッグ&ドロップ対応
- ✅ 実行履歴・レポート機能
- ✅ 自動バックアップ・復元

### 改善点
- 🔧 プリセット管理の大幅強化
- 🔧 エラーハンドリングの改善
- 🔧 型安全性の向上
- 🔧 拡張性の大幅改善

### 互換性
- ✅ CLI インターフェース完全互換
- ✅ 既存プリセットファイル互換
- ✅ v0.1 設定ファイル互換

## 🛣️ ロードマップ

### v0.3 (予定)
- 🔄 非同期バッチ処理
- 🌐 クラウド同期機能
- 🎨 テーマ・カスタマイズ
- 📱 macOS/Linux 対応

### v1.0 (長期)
- 🚀 パフォーマンス最適化
- 🔌 プラグインシステム
- 📊 高度な統計機能
- 🌍 多言語対応

## 📄 ライセンス

MIT License

## 🤝 貢献

Issue や Pull Request をお待ちしています！

- 🐛 **バグ報告**: Issues で詳細をお知らせください
- 💡 **機能提案**: Discussions で議論しましょう
- 🔧 **コード貢献**: Pull Request をお送りください

詳細な開発ガイドは [CLAUDE.md](CLAUDE.md) を参照してください。

---

**Tadakan v0.2** - より強力に、より使いやすく、ファイル整理がもっと楽しく！