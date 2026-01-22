# 🚀 手動入力モード クイックスタート

X API Free + 手動入力モードで今すぐ始める

---

## 前提条件

✅ Bearer Tokenを取得済み（[X_API_SETUP.md](X_API_SETUP.md)参照）
✅ Gemini APIキーを取得済み
✅ Python 3.8以上

---

## 3ステップで開始

### ステップ1: 依存関係のインストール

```bash
cd /Users/yamatokitada/マイドライブ（yamato.kitada@cyan-inc.net）/Cursor/portfolio/x-viral-tweet-generator

# tweepyがまだの場合
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org tweepy
```

### ステップ2: .envファイルを設定

Cursor上で `.env` ファイルを開く（**Cmd + P** → `.env`）

以下の項目を更新:

```bash
# Gemini API Key（必須）
GEMINI_API_KEY=あなたのGemini APIキー

# Google Cloud Project（Google Sheets使用時）
GCP_PROJECT_ID=x-viral-tweet-results

# Google Sheets（オプション - CSVでも保存可能）
SPREADSHEET_ID=あなたのSpreadsheet ID

# X API Bearer Token（必須 - 手動入力モード用）
TWITTER_BEARER_TOKEN=あなたのBearer Token

# モード設定（手動入力モード）
MODE=manual
```

**最小構成（Gemini + X API のみ）**:
```bash
GEMINI_API_KEY=your_key_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
MODE=manual
```

### ステップ3: 実行！

```bash
cd src

# 単一ツイートを分析
python3 manual_mode.py https://x.com/username/status/1234567890

# 複数ツイートを一度に分析
python3 manual_mode.py \
  https://x.com/user1/status/111 \
  https://x.com/user2/status/222 \
  https://x.com/user3/status/333
```

---

## 📝 使い方の例

### バズツイートを見つけて分析

1. **Xで気になるバズツイートを探す**
   - いいね1,000以上
   - リツイート100以上
   - 自分のジャンル（AI、副業など）

2. **ツイートURLをコピー**
   - ツイートの「共有」→「リンクをコピー」
   - または、ブラウザのURL欄からコピー

3. **manual_mode.pyで分析**
   ```bash
   python3 manual_mode.py https://x.com/example/status/1234567890
   ```

4. **結果を確認**
   - ターミナルに分析結果が表示
   - Google Sheets（または`output/results.csv`）に保存
   - リライト案も自動生成

### 実際の出力例

```
============================================================
ツイートURL: https://x.com/example/status/1234567890
============================================================

ステップ1: ツイート取得
✅ ツイート取得成功
  本文: AIを使った副業で月10万円達成するための完全ロードマップ...
  いいね: 1,850
  リツイート: 420
  リプライ: 95
  エンゲージメント: 3,007

ステップ2: X公式アルゴリズム分析
✅ 分析完了
  P(dwell): 9/10
  P(reply): 8/10
  P(favorite): 9/10
  P(repost): 8/10

ステップ3: X公式アルゴリズム対応リライト
✅ リライト完了（280文字）
  本文: [あなた専用のバズツイート案]

ステップ4: 結果を保存
✅ 保存完了
```

---

## 💰 コスト管理

### X API Free Tierの制限

- **月間500ツイート**まで無料
- 1日あたり約16ツイート
- 厳選したバズツイートのみ分析

### おすすめの使い方

**1日5ツイート分析の場合**:
- 月間150ツイート（制限の30%）
- コスト: $0
- 十分な分析データが蓄積

**制限を超えた場合**:
- モックモードに切り替え（`MODE=mock`）
- または翌月を待つ
- Basic tier ($100/月) にアップグレード

---

## 📊 結果の活用

### Google Sheetsで管理

1. 分析結果が自動保存される
2. スプレッドシートで一覧表示
3. フィルター・並び替えで分析
4. 最も効果的なパターンを発見

### CSVで管理（Google Sheets未設定の場合）

- `output/results.csv`に保存
- Excel、Googleスプレッドシートで開ける
- データ分析・可視化が可能

---

## 🔧 トラブルシューティング

### エラー: `401 Unauthorized`

**原因**: Bearer Tokenが無効

**対処法**:
1. `.env`のTWITTER_BEARER_TOKENを確認
2. X Developer Portalでトークンを再生成
3. `.env`に新しいトークンを設定

### エラー: `429 Too Many Requests`

**原因**: 月間500ツイート制限に達した

**対処法**:
```bash
# モックモードに切り替え
# .env ファイルで:
MODE=mock
```

### ツイートが取得できない

**原因**: 
- ツイートが削除された
- アカウントが非公開
- URLが間違っている

**対処法**:
- 別のツイートで試す
- URLを再確認
- 公開アカウントのツイートを使用

---

## 📚 次のステップ

### さらに活用する

1. **定期的に分析**
   - 週に20-30ツイート分析
   - パターンを学習
   - 自分の投稿に活用

2. **カテゴリ別に整理**
   - AI技術
   - 副業・起業
   - マーケティング
   - など

3. **A/Bテスト**
   - リライト案を実際に投稿
   - エンゲージメントを比較
   - 改善を繰り返す

### より高度な使い方

- 自動収集モード（Basic tier契約後）
- 画像生成機能の追加
- Webアプリモードの活用

---

## ✅ チェックリスト

開始前に確認:

- [ ] Bearer Token取得済み
- [ ] Gemini APIキー取得済み
- [ ] tweepyインストール済み
- [ ] `.env`ファイル設定済み
- [ ] `MODE=manual`に設定

すべてチェックしたら実行！

```bash
cd src
python3 manual_mode.py https://x.com/example/status/1234567890
```

---

問題が発生した場合は、`X_API_SETUP.md`や`README.md`を参照してください。
