# X バズ投稿自動生成システム

X公式アルゴリズム（2026年版）完全準拠  
参考: [X Algorithm GitHub](https://github.com/xai-org/x-algorithm)

**💰 月間コスト: 約100-200円**（画像生成10-20枚、Google Cloud Run無料枠利用）

## 🚀 4つの使い方

### 1. **モックモード** - テスト実行
サンプルデータで動作確認。APIキー不要。

### 2. **手動入力モード** - ツイートURL指定 🆕
特定のツイートURLから分析・リライト。X API使用時は月500ツイートまで無料。

### 3. **APIモード** - 自動収集 🆕
X API v2でアカウントのツイートを自動収集。Basic tier ($100/月) 推奨。

### 4. **Webアプリモード** - ブラウザで実行
X風のスタイリッシュなUIで直感的に操作。

📖 **本番環境デプロイガイド**: [DEPLOY_PRODUCTION.md](DEPLOY_PRODUCTION.md)

## 特徴

### X公式アルゴリズム対応

- ✅ **P(dwell) - 滞在時間**: 最大化
- ✅ **P(reply) - リプライ**: 誘発
- ✅ **正のシグナル**: 最大化（いいね、リツイート、共有）
- ✅ **負のシグナル**: 完全排除（not_interested, block, mute）

### 主要機能

1. **ゲストモードスクレイピング**: アカウント停止リスクなし
2. **AI分析**: Gemini APIでツイートを分析
3. **自動リライト**: 有益性に特化
4. **選択的画像生成**: 必要な時だけImagen 3で生成（コスト削減）🆕
5. **Google Sheets保存**: 一元管理
6. **管理画面**: 後から選択して画像生成🆕

## クイックスタート

### モックモード（APIキー不要）

```bash
# 1. リポジトリをクローン
cd x-viral-tweet-generator

# 2. 依存関係をインストール
pip3 install -r requirements.txt

# 3. 設定ファイルを編集
# config/accounts.json - 監視したいXアカウントを追加
# config/settings.json - 収集数・分析数を調整

# 4. 環境変数を設定（モックモード用）
cp env.template .env
# .env を開いて MODE=mock を確認

# 5. 実行
cd src
python3 main.py
```

結果は `output/results.csv` に保存されます。

---

### 手動入力モード（ツイートURL指定）🆕

特定のバズツイートを分析・リライトしたい場合に最適。

```bash
# 1. 環境変数を設定
# .env ファイルを編集:
# GEMINI_API_KEY=your_key_here
# MODE=manual
# TWITTER_BEARER_TOKEN=your_token_here（オプション）

# 2. ツイートURLを指定して実行
cd src
python3 manual_mode.py https://x.com/username/status/1234567890

# 複数のツイートも一度に処理可能
python3 manual_mode.py https://x.com/user1/status/111 https://x.com/user2/status/222
```

**X API Free tier使用時の制限**:
- 月間500ツイート読み取りまで無料
- それ以上はBasic tier ($100/月) が必要

**TWITTER_BEARER_TOKENなしの場合**:
- モックデータで動作（テスト用）

## プロダクションモードの設定

### 1. 必要なAPIキーを取得

#### X API v2 Bearer Token（オプション）🆕

手動入力モード・APIモードで実際のツイートを取得する場合に必要。

1. https://developer.x.com/ にアクセス
2. アカウント作成（X Premium推奨）
3. 新しいProjectとAppを作成
4. **Keys and tokens** → **Bearer Token** を生成
5. トークンをコピー

**料金プラン**:
- **Free tier**: 月間500ツイート読み取り（手動入力モードで利用可能）
- **Basic tier**: $100/月、月間10,000ツイート（APIモードで推奨）

#### Gemini API Key
1. https://aistudio.google.com/app/apikey にアクセス
2. APIキーを取得

#### Google Cloud設定
1. https://console.cloud.google.com/ でプロジェクト作成
2. 以下のAPIを有効化:
   - Google Sheets API
   - Google Drive API
   - Vertex AI API（Imagen 3用）
3. サービスアカウントを作成
4. 認証情報JSONをダウンロード → `config/credentials.json` に保存

#### Google Sheets準備
1. 新しいSpreadsheetを作成
2. サービスアカウントのメールアドレスに編集権限を付与
3. Spreadsheet IDをコピー（URLから取得）

### 2. 環境変数を設定

`.env` ファイルを編集:

```bash
GEMINI_API_KEY=your_actual_key_here
GCP_PROJECT_ID=your_project_id_here
SPREADSHEET_ID=your_spreadsheet_id_here
MODE=production
```

### 3. 実行

```bash
cd src
python main.py
```

## 設定のカスタマイズ

### ベンチマークアカウントの追加

`config/accounts.json` を編集:

```json
{
  "benchmark_accounts": [
    {
      "username": "your_target_account",
      "category": "AI技術",
      "priority": "high",
      "description": "説明"
    }
  ]
}
```

### 収集数・分析数の調整

`config/settings.json` を編集:

```json
{
  "collection": {
    "tweets_per_account": 100,
    "max_accounts_per_run": 50
  },
  "processing": {
    "tweets_to_analyze": 30,
    "tweets_to_rewrite": 10
  }
}
```

## GitHub Actions定時実行

`.github/workflows/daily-collection.yml` が設定済みです。

### セットアップ

1. GitHubリポジトリにプッシュ
2. Settings → Secrets and variables → Actions で以下を登録:
   - `GEMINI_API_KEY`
   - `GCP_PROJECT_ID`
   - `SPREADSHEET_ID`
   - `GOOGLE_CREDENTIALS_BASE64` (credentials.jsonをbase64エンコード)

```bash
# credentials.jsonをBase64エンコード
base64 config/credentials.json | pbcopy
```

3. Actions タブで確認

## コスト試算

| 項目 | 日額 | 月額（30日） |
|------|------|-------------|
| Gemini API | $0.05 | $1.50 |
| Imagen 3（10枚） | $0.20 | $6.00 |
| **合計** | **$0.25** | **$7.50** |

## X公式アルゴリズム準拠度

| 指標 | 対応状況 |
|------|---------|
| P(dwell) - 滞在時間 | ⭐⭐⭐⭐⭐ |
| P(reply) - リプライ | ⭐⭐⭐⭐⭐ |
| P(favorite) - いいね | ⭐⭐⭐⭐ |
| P(repost) - リツイート | ⭐⭐⭐⭐ |
| 負のシグナル排除 | ⭐⭐⭐⭐⭐ |

## トラブルシューティング

### モックモードで動かない

- `python-dotenv` がインストールされているか確認
- `.env` ファイルが存在するか確認

### プロダクションモードでエラー

- APIキーが正しく設定されているか確認
- `config/credentials.json` が存在するか確認
- Google Cloud APIが有効化されているか確認

## ライセンス

MIT License
