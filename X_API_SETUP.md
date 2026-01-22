# X API Free Tier セットアップガイド

手動入力モードで使用するX API Bearer Tokenの取得方法

---

## 🔑 Bearer Token取得手順（無料）

### 1. X Developer Portalにアクセス

https://developer.x.com/en/portal/dashboard

### 2. アカウント作成・ログイン

- Xアカウントでログイン
- 開発者規約に同意

### 3. 新しいAppを作成

1. **「+ Create Project」** または **「+ Add App」** をクリック
2. プロジェクト名を入力（例: `viral-tweet-analyzer`）
3. 使用目的を選択:
   - **「Exploring the API」** を選択（学習・テスト用）
4. App名を入力（例: `viral-tweet-app`）

### 4. Bearer Tokenを取得

1. App作成後、自動的に **API Keys** 画面が表示される
2. 以下の3つが表示されます:
   - API Key
   - API Key Secret
   - **Bearer Token** ← これをコピー
3. **Bearer Token**を必ず保存（後から再表示できない）

**⚠️ 重要**: Bearer Tokenは1度しか表示されません。必ずコピーして安全に保存してください。

### 5. App設定を確認

1. Appの **Settings** タブを開く
2. **App permissions** を確認:
   - デフォルトは **Read** のみ（これでOK）
3. **User authentication settings** は設定不要（Bearer Tokenのみ使用）

---

## ✅ Free Tierでできること

### 制限
- **月間500ツイート読み取り**
- **月間1,500ツイート投稿**（今回は使用しない）
- 1リクエストあたり最大100ツイート

### 推奨用途
- 手動入力モード（個別ツイート分析）
- 1日あたり約16ツイート分析可能
- バズツイートの厳選分析に最適

---

## 🔒 セキュリティ

### Bearer Tokenの管理

✅ **やるべきこと**:
- `.env`ファイルに保存
- `.gitignore`に`.env`を追加（既に設定済み）
- ローカル環境のみで使用

❌ **やってはいけないこと**:
- GitHubなどにコミットしない
- 公開リポジトリに含めない
- 他人と共有しない

### トークンが漏洩した場合

1. X Developer Portal → App設定
2. **「Regenerate」** ボタンでトークンを再生成
3. 古いトークンは無効化される

---

## 💡 トラブルシューティング

### Bearer Tokenが見つからない

再表示はできませんが、再生成は可能です:

1. App Settings → **Keys and tokens** タブ
2. Bearer Token欄の **「Regenerate」** をクリック
3. 新しいトークンをコピー

### 認証エラーが出る

```
401 Unauthorized
```

**原因**:
- Bearer Tokenが間違っている
- トークンが再生成されて無効化された
- X Developer Portalでのアカウント設定が未完了

**対処法**:
1. Bearer Tokenを再確認
2. `.env`ファイルの設定を確認
3. 必要に応じてトークンを再生成

### Rate Limit エラー

```
429 Too Many Requests
```

**原因**: 月間500ツイートの制限に達した

**対処法**:
- 翌月まで待つ
- Basic tier ($100/月) にアップグレード
- または、モックモードで動作確認を続ける

---

## 📊 使用量の確認

### X Developer Portalで確認

1. Dashboard → 該当のApp
2. **「Usage」** タブ
3. リクエスト数・残り回数を確認

### コストゼロで運用するコツ

- 本当にバズっているツイートだけを厳選
- 1日5-10ツイート程度に抑える
- 分析結果をスプレッドシートに蓄積
- 月末に使用状況を確認

---

## 🚀 次のステップ

Bearer Tokenを取得したら:

1. `.env`ファイルに設定
2. `manual_mode.py`で実際のツイートを分析
3. Google Sheetsに結果を保存

詳しくは `README.md` を参照してください。
