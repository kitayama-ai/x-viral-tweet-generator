# X バズ投稿生成AI - Web版

XのトンマナにあわせたスタイリッシュなWebアプリケーション

## 特徴

- ✨ **X風ダークモードUI**: 公式Xアプリのような洗練されたデザイン
- ⚡ **リアルタイム生成**: ブラウザで即座にバズ投稿を生成
- 📊 **可視化されたスコア**: P(dwell)、P(reply)、Viralityを数値化
- 🎨 **レスポンシブデザイン**: PC・タブレット・スマホ対応

## デモ

![Screenshot](https://via.placeholder.com/800x600/000000/1d9bf0?text=X+Viral+Tweet+Generator)

## クイックスタート

### 1. ローカル開発

```bash
# バックエンドを起動
cd web/backend
pip install -r requirements.txt
uvicorn api:app --reload

# 別ターミナルでフロントエンドを起動
cd web/frontend
python3 -m http.server 3000

# ブラウザで開く
open http://localhost:3000
```

### 2. Web公開

詳細は [WEB_DEPLOYMENT.md](../WEB_DEPLOYMENT.md) を参照

- **フロントエンド**: GitHub Pages（無料）
- **バックエンド**: Railway（$5/月〜）

## アーキテクチャ

```
Frontend (HTML/CSS/JS)
    ↓ API Call
Backend (FastAPI)
    ↓ Processing
Core System (Python)
```

## 使い方

1. **アカウント設定**: 監視したいXアカウントを入力（@なし）
2. **処理設定**: 分析数・リライト数を調整
3. **生成**: ボタンをクリックしてバズ投稿を自動生成
4. **結果確認**: P(dwell)スコアやリライト結果を確認

## 技術スタック

### フロントエンド
- Pure HTML/CSS/JavaScript（フレームワーク不要）
- X風カスタムCSSフレームワーク
- レスポンシブデザイン

### バックエンド
- FastAPI（高速なPython Webフレームワーク）
- 非同期処理対応
- CORS対応

### デプロイ
- GitHub Pages（フロントエンド）
- Railway（バックエンド）
- GitHub Actions（自動デプロイ）

## カスタマイズ

### UIカラーの変更

`web/frontend/styles.css` の変数を編集：

```css
:root {
    --accent-blue: #1d9bf0;  /* アクセントカラー */
    --bg-primary: #000000;   /* 背景色 */
}
```

### API エンドポイントの変更

`web/frontend/app.js` を編集：

```javascript
const API_BASE_URL = 'https://your-api-url.com';
```

## ライセンス

MIT License
