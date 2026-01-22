#!/bin/bash
# 手動入力モードのテストスクリプト

cd "$(dirname "$0")/src"

echo "=== 手動入力モード テスト ==="
echo ""
echo "テストツイートURL: https://x.com/test_user/status/1234567890"
echo ""

# モックモードで実行
python3 manual_mode.py https://x.com/test_user/status/1234567890

echo ""
echo "=== テスト完了 ==="
