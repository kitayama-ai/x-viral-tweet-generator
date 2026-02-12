#!/bin/bash
# X バズ投稿自動生成 - 実行スクリプト（仮想環境を使います）

cd "$(dirname "$0")"

# 仮想環境がなければ作成して必要なパッケージを入れる
if [ ! -d ".venv" ]; then
  echo "初回: 仮想環境を作成してパッケージを入れています..."
  python3 -m venv .venv
  .venv/bin/pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    python-dotenv tweepy google-generativeai gspread google-auth 2>/dev/null || true
  echo "完了。もう一度 ./run.sh を実行してください。"
  exit 0
fi

# プロジェクトルートで実行（.env を読むため）
.venv/bin/python src/main.py
