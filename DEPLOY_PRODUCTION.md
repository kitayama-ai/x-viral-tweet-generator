# 本番環境デプロイガイド（予算最適化版）

月間コスト: 約100-200円（画像生成10-20枚の場合）

---

## 📋 前提条件

- Googleアカウント
- クレジットカード（Google Cloud課金用）
- gcloud CLIインストール済み

---

## ステップ1: Google Cloudプロジェクト作成

### 1-1. プロジェクト作成

```bash
# Google Cloudコンソールにアクセス
# https://console.cloud.google.com/

# 新しいプロジェクトを作成
# プロジェクト名: x-viral-tweet-generator
# プロジェクトID: x-viral-tweet-XXXXXX（自動生成）
```

### 1-2. 課金を有効化

1. **ナビゲーションメニュー** → **お支払い**
2. **課金アカウントをリンク**
3. クレジットカード情報を入力

### 1-3. 予算アラート設定（重要！）

```bash
# ナビゲーションメニュー → お支払い → 予算とアラート
# 月間予算: 300円
# アラート閾値: 50%, 90%, 100%
```

---

## ステップ2: 必要なAPIを有効化

```bash
# gcloud CLIでログイン
gcloud auth login

# プロジェクトを設定
gcloud config set project YOUR_PROJECT_ID

# 必要なAPIを一括有効化
gcloud services enable \
  run.googleapis.com \
  aiplatform.googleapis.com \
  sheets.googleapis.com \
  drive.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com
```

---

## ステップ3: Gemini APIキー取得

```bash
# AI StudioでAPIキーを取得
# https://aistudio.google.com/app/apikey

# 「APIキーを作成」をクリック
# キーをコピーして保存
```

---

## ステップ4: サービスアカウント作成

```bash
# サービスアカウント作成
gcloud iam service-accounts create x-viral-tweet-sa \
  --display-name="X Viral Tweet Generator Service Account"

# プロジェクトIDを取得
PROJECT_ID=$(gcloud config get-value project)

# 必要な権限を付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:x-viral-tweet-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:x-viral-tweet-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# 認証JSONキーをダウンロード
gcloud iam service-accounts keys create ~/x-viral-tweet-credentials.json \
  --iam-account=x-viral-tweet-sa@${PROJECT_ID}.iam.gserviceaccount.com

# ダウンロードしたJSONファイルを確認
cat ~/x-viral-tweet-credentials.json
```

---

## ステップ5: Google Sheets準備

### 5-1. スプレッドシート作成

```bash
# Google Sheetsにアクセス
# https://sheets.google.com/

# 新しいスプレッドシートを作成
# 名前: X Viral Tweet Results
```

### 5-2. サービスアカウントに権限付与

```bash
# スプレッドシートの「共有」をクリック
# サービスアカウントのメールアドレスを追加:
# x-viral-tweet-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
# 権限: 編集者
```

### 5-3. Spreadsheet ID取得

```bash
# URLから取得:
# https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
# 
# SPREADSHEET_IDをコピー
```

---

## ステップ6: Secret Manager設定

```bash
# Gemini APIキーをSecretに保存
echo -n "YOUR_GEMINI_API_KEY" | \
  gcloud secrets create gemini-api-key --data-file=-

# Secret Managerにアクセス権限を付与
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:x-viral-tweet-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## ステップ7: Cloud Runデプロイ

```bash
# プロジェクトルートに移動
cd x-viral-tweet-generator

# Cloud Runにデプロイ
gcloud run deploy x-viral-tweet-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --service-account x-viral-tweet-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars MODE=production,GCP_PROJECT_ID=${PROJECT_ID},SPREADSHEET_ID=YOUR_SPREADSHEET_ID \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest,GOOGLE_APPLICATION_CREDENTIALS=/secrets/credentials.json \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 3 \
  --min-instances 0

# デプロイ完了後、URLが表示されます
# 例: https://x-viral-tweet-api-xxx-uc.a.run.app
```

---

## ステップ8: フロントエンド更新

### 8-1. API URLを更新

```bash
# web/frontend/app.js を編集
# 133行目付近:
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://x-viral-tweet-api-xxx-uc.a.run.app';  # ← Cloud Run URLに置き換え

# web/frontend/admin.html も同様に更新
```

### 8-2. GitHubにプッシュ

```bash
git add .
git commit -m "Update: Production API URL for Cloud Run"
git push origin main

# GitHub Actions が自動的にGitHub Pagesにデプロイ
# 1-2分待つ
```

---

## ステップ9: 動作確認

### 9-1. バックエンドヘルスチェック

```bash
# Cloud Run URLにアクセス
curl https://YOUR_CLOUD_RUN_URL/

# レスポンス例:
# {
#   "status": "ok",
#   "service": "X バズ投稿生成AI",
#   "version": "1.0.0"
# }
```

### 9-2. フロントエンドテスト

```bash
# GitHub Pagesにアクセス
# https://YOUR_USERNAME.github.io/x-viral-tweet-generator/

# 1. アカウント入力（例: tetumemo）
# 2. 「バズ投稿を生成」をクリック
# 3. 結果が表示されることを確認
# 4. Google Sheetsに保存されていることを確認
```

### 9-3. 管理画面テスト

```bash
# 管理画面にアクセス
# https://YOUR_USERNAME.github.io/x-viral-tweet-generator/admin.html

# 1. データが読み込まれることを確認
# 2. 画像生成したい行を選択
# 3. 「画像生成」ボタンをクリック
# 4. 画像生成完了後、Google Sheetsに画像URLが追加されることを確認
```

---

## コスト監視

### リアルタイム監視

```bash
# Google Cloudコンソール → お支払い → 概要
# 日次・月次のコストを確認
```

### 推定コスト（月間）

| サービス | 使用量 | コスト |
|---|---|---|
| Gemini API | 300ツイート × 2回（分析+リライト） | 約20円 |
| Imagen 3 | 10-20枚 | 約60-120円 |
| Cloud Run | 月200万リクエスト以内 | 無料 |
| Cloud Storage | 画像保存 | 約1円 |
| **合計** | | **約100-150円** |

---

## トラブルシューティング

### Cloud Runデプロイエラー

```bash
# ログを確認
gcloud run services logs read x-viral-tweet-api --region us-central1 --limit 50

# よくあるエラー:
# 1. 認証情報の問題 → Secret Managerの設定を確認
# 2. APIが有効化されていない → gcloud services enable で有効化
# 3. メモリ不足 → --memory 2Gi に増やす
```

### Google Sheets接続エラー

```bash
# サービスアカウントの権限を確認
# 1. スプレッドシートの共有設定
# 2. サービスアカウントのメールアドレスが正しいか
# 3. 編集者権限が付与されているか
```

### 画像生成エラー

```bash
# Vertex AI APIが有効化されているか確認
gcloud services list --enabled | grep aiplatform

# 有効化されていない場合
gcloud services enable aiplatform.googleapis.com

# サービスアカウントに権限があるか確認
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:x-viral-tweet-sa@*"
```

---

## 完了チェックリスト

- [ ] Google Cloudプロジェクト作成
- [ ] 課金有効化・予算アラート設定
- [ ] 必要なAPI有効化（7個）
- [ ] Gemini APIキー取得
- [ ] サービスアカウント作成・権限付与
- [ ] 認証JSONダウンロード
- [ ] Google Sheets作成・権限付与
- [ ] Spreadsheet ID取得
- [ ] Secret Manager設定
- [ ] Cloud Runデプロイ成功
- [ ] フロントエンドAPI URL更新
- [ ] GitHub Pagesデプロイ完了
- [ ] バックエンドヘルスチェックOK
- [ ] フロントエンド動作確認OK
- [ ] 管理画面動作確認OK
- [ ] Google Sheetsに保存確認
- [ ] 画像生成テスト成功

---

## 🎉 完了！

これで本番環境のデプロイが完了しました！

### 次のステップ

1. **定期実行設定**: GitHub ActionsやCloud Schedulerで自動化
2. **モニタリング設定**: Cloud Monitoringでアラート設定
3. **コスト最適化**: 使用状況を見て設定調整

---

## サポート

問題が発生した場合:
1. ログを確認（Cloud Run、GitHub Actions）
2. コストダッシュボードで異常なスパイクがないか確認
3. 各サービスの権限設定を再確認
