# Web版デプロイガイド

X風UIのWebアプリケーションをGitHub Pages + Railwayで公開する手順

## アーキテクチャ

```
┌─────────────────┐
│  GitHub Pages   │  ← フロントエンド（静的HTML/CSS/JS）
│  (Frontend)     │
└────────┬────────┘
         │ API Call
         ▼
┌─────────────────┐
│    Railway      │  ← バックエンド（FastAPI）
│  (Backend API)  │
└─────────────────┘
```

## 1. GitHubリポジトリの準備

### リポジトリを作成

```bash
cd x-viral-tweet-generator

# Git初期化
git init
git add .
git commit -m "Initial commit: X Viral Tweet Generator"

# GitHubにプッシュ
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/x-viral-tweet-generator.git
git push -u origin main
```

### GitHub Pages設定

1. GitHubリポジトリの **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` → `/web/frontend` → Save

または、GitHub Actionsを使用：

1. **Settings** → **Pages** → **Source**: GitHub Actions
2. `.github/workflows/deploy-pages.yml` が自動的にデプロイ

**フロントエンドURL**: `https://YOUR_USERNAME.github.io/x-viral-tweet-generator/`

## 2. Railwayでバックエンドをデプロイ

### Railway CLI インストール

```bash
# macOS
brew install railway

# または npm
npm install -g @railway/cli
```

### Railwayにデプロイ

```bash
# ログイン
railway login

# プロジェクト作成
cd web/backend
railway init

# 環境変数を設定
railway variables set MODE=mock
railway variables set GEMINI_API_KEY=your_key_here
railway variables set GCP_PROJECT_ID=your_project_id

# デプロイ
railway up
```

### Railway URL取得

```bash
railway domain
```

出力例: `https://x-viral-tweet-generator-production.up.railway.app`

## 3. フロントエンドとバックエンドを接続

### `web/frontend/app.js` を編集

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://YOUR-RAILWAY-APP.up.railway.app'; // ← あなたのRailway URLに置き換え
```

変更をコミット＆プッシュ：

```bash
git add web/frontend/app.js
git commit -m "Update API endpoint"
git push
```

## 4. ローカルでテスト

### バックエンドを起動

```bash
cd web/backend
pip install -r requirements.txt
uvicorn api:app --reload
```

バックエンドが http://localhost:8000 で起動

### フロントエンドを開く

```bash
cd web/frontend
# Pythonの簡易サーバー
python3 -m http.server 3000
```

ブラウザで http://localhost:3000 を開く

## 5. 公開URLの確認

### フロントエンド（GitHub Pages）
```
https://YOUR_USERNAME.github.io/x-viral-tweet-generator/
```

### バックエンド（Railway）
```
https://YOUR-RAILWAY-APP.up.railway.app
```

### API動作確認
```bash
curl https://YOUR-RAILWAY-APP.up.railway.app/
```

## トラブルシューティング

### CORSエラーが出る

`web/backend/api.py` の CORS設定を確認：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://YOUR_USERNAME.github.io"],  # 本番URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Railwayでビルドエラー

`web/backend/requirements.txt` の依存関係を確認。playwright は不要な場合は削除可能。

### GitHub Pagesが404

- Settings → Pages で正しいディレクトリ（`/web/frontend`）を指定
- GitHub Actionsのデプロイログを確認

## コスト

- **GitHub Pages**: 無料（パブリックリポジトリ）
- **Railway**: 
  - Hobby Plan: $5/月（500時間実行可能）
  - 従量課金: 使った分だけ

## セキュリティ

- APIキーは環境変数で管理（Railwayの Variables）
- フロントエンドにAPIキーを含めない
- 本番環境ではCORSを適切に設定

## 次のステップ

1. カスタムドメインを設定（オプション）
2. Google Analyticsを追加（オプション）
3. プロダクションモードでAPI連携
