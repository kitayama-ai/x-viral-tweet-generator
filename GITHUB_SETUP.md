# GitHubセットアップ（1分で完了）

## ステップ1: GitHubでリポジトリを作成（30秒）

1. このリンクを開く: https://github.com/new

2. 以下を入力：
   - Repository name: `x-viral-tweet-generator`
   - Description: `X公式アルゴリズム準拠のバズ投稿生成AI（Web版あり）`
   - Public を選択
   - ✅ **Create repository** をクリック

## ステップ2: リモートURLをコピー（10秒）

作成後のページで、HTTPSのURLをコピー：
```
https://github.com/YOUR_USERNAME/x-viral-tweet-generator.git
```

## ステップ3: ターミナルで実行（10秒）

```bash
cd "/Users/yamatokitada/マイドライブ（yamato.kitada@cyan-inc.net）/Cursor/portfolio/x-viral-tweet-generator"

# ここにコピーしたURLを貼り付け
git remote add origin https://github.com/YOUR_USERNAME/x-viral-tweet-generator.git

# プッシュ
git push -u origin main
```

## ステップ4: GitHub Pagesを有効化（10秒）

1. リポジトリページで **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` → **フォルダ**: `/web/frontend`
4. **Save** をクリック

## 完了！

数分後、以下のURLでアクセス可能になります：
```
https://YOUR_USERNAME.github.io/x-viral-tweet-generator/
```

---

## 🎉 もっと簡単な方法: gh CLI（推奨）

GitHub CLIを使えば、ブラウザ不要で全自動：

```bash
# GitHub CLI インストール（初回のみ）
brew install gh

# ログイン
gh auth login

# リポジトリ作成＆プッシュ（自動）
gh repo create x-viral-tweet-generator --public --source=. --remote=origin --push

# GitHub Pages有効化
gh api repos/:owner/x-viral-tweet-generator/pages -X POST \
  -F source[branch]=main -F source[path]=/web/frontend

# URLを取得
gh repo view --web
```

これで完全自動です！
