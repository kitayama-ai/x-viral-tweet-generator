# Python 3.11ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ設定
WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
COPY web/backend/requirements.txt backend-requirements.txt

# 両方のrequirements.txtからインストール
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r backend-requirements.txt

# アプリケーションコードをコピー
COPY src/ ./src/
COPY config/ ./config/
COPY web/backend/ ./web/backend/

# Pythonパスを設定
ENV PYTHONPATH=/app

# ポート設定
ENV PORT=8080
EXPOSE 8080

# Cloud Run用のヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/api/health')"

# FastAPIサーバー起動
CMD cd web/backend && exec uvicorn api:app --host 0.0.0.0 --port ${PORT}
