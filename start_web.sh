#!/bin/bash
# ブラウザで使う用：バックエンド + フロントエンドを起動

cd "$(dirname "$0")"

# 仮想環境がなければ run.sh と同様に作成
if [ ! -d ".venv" ]; then
  echo "仮想環境がありません。先に ./run.sh を1回実行してから ./start_web.sh を実行してください。"
  exit 1
fi

# FastAPI/uvicorn がなければ入れる
.venv/bin/pip install fastapi 'uvicorn[standard]' --quiet 2>/dev/null || true

echo "バックエンド起動中（http://localhost:8000）..."
.venv/bin/python -m uvicorn web.backend.api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2
echo "フロントエンド起動中（http://localhost:3000）..."
.venv/bin/python -m http.server 3000 --directory web/frontend &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "  ブラウザで開く: http://localhost:3000"
echo "  止めるときは Ctrl+C"
echo "=========================================="
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
