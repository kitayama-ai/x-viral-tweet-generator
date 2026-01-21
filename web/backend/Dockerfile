# Cloud Run用Dockerfile
FROM python:3.11-slim

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージの更新とインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 親ディレクトリのsrcをコピー
COPY ../../src /app/src

# ポート設定
ENV PORT=8080
EXPOSE 8080

# アプリケーション起動
CMD exec uvicorn api:app --host 0.0.0.0 --port ${PORT}
