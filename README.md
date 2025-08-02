# Tadakan

ファイルリネーム＆フィルタリングができる作業のお供

「ひたすらファイルをかんたん整理！」

- 命名プリセット×バッチ自動生成
- 画像・音楽・テキスト対応
- 高速フィルタリング
- 物理ファイル移動で確実な整理

## 特徴

### 🚀 高速リネーム
- カスタマイズ可能な命名プリセット
- バッチファイル自動生成でドラッグ&ドロップ操作
- 重複チェック・NGワード検出

### 🎯 フィルタリング
- プリセット項目での絞り込み
- AND/OR条件対応
- 表示用フォルダへの一時移動

### 📁 バッチ管理
- 生成したバッチファイルの履歴管理
- 検索・お気に入り機能
- 再利用可能なワークフロー

### 🎵 マルチファイル対応
- 画像：jpg, png, gif, webp, bmp
- 音楽：mp3, wav, flac, aac, ogg
- テキスト：txt, md, csv, json, xml
- 動画：mp4, avi, mkv, mov, wmv

## インストール

```bash
git clone https://github.com/（ユーザー名）/tadakan.git
cd tadakan
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 使い方

### 基本的な流れ

1. **プリセット作成・選択**
   ```bash
   python src/main.py --demo  # デモンストレーション
   ```

2. **ファイルリネーム**
   ```bash
   python src/main.py --preset "写真整理" --values "陣営=赤軍,キャラ名=田中" --files *.jpg --output ./renamed/
   ```

3. **プリセット一覧確認**
   ```bash
   python src/main.py --list
   ```

### プリセット例

- `世界観_名前_日付`: `ファンタジー_エルフ_20250102`
- `プロジェクト_バージョン_種類`: `GameDev_v1.2_texture`
- `陣営_キャラ名_番号`: `赤軍_田中_001`

## 開発

### テスト実行
```bash
python -m pytest test/ -v
```

### コード品質チェック
```bash
# 型チェック
mypy src/

# コードフォーマット
black src/ test/

# リンター
flake8 src/ test/
```

## アーキテクチャ

```
src/
├── main.py              # CLI エントリーポイント
├── models/              # データモデル
│   ├── preset.py        # プリセット定義
│   └── file_item.py     # ファイル項目
├── services/            # ビジネスロジック
│   ├── preset_manager.py    # プリセット管理
│   ├── file_renamer.py      # ファイルリネーム
│   └── batch_generator.py   # バッチ生成
└── config/              # 設定管理
    └── settings.py      # アプリケーション設定
```

## ライセンス

MIT License

## 貢献

Issue や Pull Request をお待ちしています！

詳細は [CLAUDE.md](CLAUDE.md) を参照してください。