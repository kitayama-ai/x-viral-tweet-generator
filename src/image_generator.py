"""
Nano Banana Pro 画像生成エンジン

戦略:
- Xタイムラインで目を止めさせる画像を生成
- ツイート内容のわかりやすい図解・ビジュアル化
- Cloud Storageに保存して公開URLを返す

技術:
- Google Nano Banana Pro (google-genai パッケージ)
- Google Cloud Storage に保存 → 公開URLをスプシに納品
"""
import asyncio
import os
import uuid
from datetime import datetime
from utils import is_mock_mode, log_info, log_success


class InfographicGenerator:
    """
    Nano Banana Pro でインフォグラフィック画像を生成し、Cloud Storageにアップロード
    """
    def __init__(self, project_id=None, location=None, credentials_path=None,
                 gemini_api_key=None, model_version=None, bucket_name=None):
        self.gemini_api_key = gemini_api_key
        self._client = None
        self._storage_client = None
        self._model_name = "nano-banana-pro-preview"
        self._bucket_name = bucket_name or os.getenv("GCS_IMAGE_BUCKET", "x-viral-tweet-images")

        # ローカル保存先（フォールバック用）
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.images_dir = os.path.join(parent_dir, "output", "images")
        os.makedirs(self.images_dir, exist_ok=True)

        # プロダクションモードで初期化
        if not is_mock_mode() and gemini_api_key:
            self._initialize()

    def _initialize(self):
        """Nano Banana Pro + Cloud Storage クライアント初期化"""
        try:
            from google import genai
            self._client = genai.Client(api_key=self.gemini_api_key)
            log_success(f"Nano Banana Pro initialized (model: {self._model_name})")
        except Exception as e:
            log_info(f"Nano Banana Pro init failed: {e}")
            self._client = None

        # Cloud Storage初期化
        try:
            from google.cloud import storage
            self._storage_client = storage.Client()
            log_success(f"Cloud Storage initialized (bucket: {self._bucket_name})")
        except Exception as e:
            log_info(f"Cloud Storage init failed (will save locally): {e}")
            self._storage_client = None

    def _upload_to_gcs(self, image_data, filename, content_type="image/jpeg"):
        """Cloud Storageに画像をアップロードして公開URLを返す"""
        if not self._storage_client:
            return None
        try:
            bucket = self._storage_client.bucket(self._bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(image_data, content_type=content_type)
            public_url = f"https://storage.googleapis.com/{self._bucket_name}/{filename}"
            log_success(f"Uploaded to GCS: {public_url}")
            return public_url
        except Exception as e:
            log_info(f"GCS upload failed: {e}")
            return None

    async def generate_infographic(self, rewritten_tweet):
        """
        リライトしたツイート内容を図解化

        Args:
            rewritten_tweet: {
                'main_text': str,
                'thread': list[str],
                'call_to_action': str
            }

        Returns:
            str: 画像の公開URL（Cloud Storage）またはローカルURL
        """
        if is_mock_mode():
            return self._get_mock_image_url(rewritten_tweet)

        if not self._client:
            log_info("Nano Banana Pro not available, skipping image generation")
            return ""

        try:
            # 1. ツイート内容から画像生成プロンプトを構築
            prompt = self._build_image_prompt(rewritten_tweet)

            # 2. Nano Banana Pro で画像生成
            log_info("Generating image with Nano Banana Pro...")
            from google.genai import types

            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self._model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                )
            )

            # 3. レスポンスから画像を取得
            if response and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                        image_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type or "image/jpeg"

                        # ファイル名生成
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        unique_id = str(uuid.uuid4())[:8]
                        ext = "jpg" if "jpeg" in mime_type else "png"
                        filename = f"{timestamp}_{unique_id}.{ext}"

                        # Cloud Storageにアップロード試行
                        public_url = self._upload_to_gcs(image_data, filename, mime_type)
                        if public_url:
                            log_success(f"Image generated & uploaded: {public_url} ({len(image_data)} bytes)")
                            return public_url

                        # フォールバック: ローカル保存
                        filepath = os.path.join(self.images_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        local_url = f"/api/images/{filename}"
                        log_success(f"Image generated (local): {local_url} ({len(image_data)} bytes)")
                        return local_url

            log_info("No image in Nano Banana Pro response")
            return ""

        except Exception as e:
            log_info(f"Image generation failed: {e}")
            return ""

    def _build_image_prompt(self, rewritten_tweet):
        """ツイート内容からXバズ特化の画像プロンプトを構築"""
        main_text = rewritten_tweet.get('main_text', '')
        thread = rewritten_tweet.get('thread', [])

        # ツイート本文＋スレッドの要点
        content = main_text
        if thread:
            content += "\n\n" + "\n".join(thread[:2])

        prompt = f"""以下のツイート内容を「Xのタイムラインで絶対にスクロールを止める1枚の図解画像」にしてください。

━━━━━━━━━━━━━━━━
■ ツイート内容
━━━━━━━━━━━━━━━━
{content}

━━━━━━━━━━━━━━━━
■ 画像デザインの鉄則
━━━━━━━━━━━━━━━━
【目的】
- Xタイムラインで目を止めさせる（P(dwell)最大化）
- ツイートの内容をパッと見で理解できる図解にする
- 「保存したい」と思わせる情報密度

【レイアウト】
- 16:9の横長（Xカード最適）
- 背景: ダーク系（#0a0a0a〜#1a1a2e）にネオンカラーのアクセント
- 左上にキャッチーな見出し（ツイートの核心を5-10文字で）
- 本文のポイントを箇条書き or フローチャートで図解
- アイコンや矢印で視覚的にわかりやすく
- 余白を適度に。詰め込みすぎない

【テキスト】
- 日本語で。フォントは太く読みやすく
- 数字は大きく目立たせる
- 重要キーワードはアクセントカラーで強調

【NGルール】
- 写真・人物・リアル画像は使わない（図解・グラフィックのみ）
- ウォーターマーク・ロゴなし
- 安っぽいクリップアート感なし
- 文字が小さすぎて読めないのはNG

【スタイル参考】
- プレミアムなテック系インフォグラフィック
- ダークモードUI風のクールなデザイン
- 情報を「見える化」する図解スタイル
"""
        return prompt

    def _get_mock_image_url(self, rewritten_tweet):
        """モック画像URLを生成"""
        log_info(f"Mock mode: Generating infographic (text length: {len(rewritten_tweet.get('main_text', ''))})")
        import hashlib
        text_hash = hashlib.md5(rewritten_tweet.get('main_text', '').encode()).hexdigest()[:8]
        mock_url = f"/api/images/mock_{text_hash}.png"
        log_info(f"Mock image URL: {mock_url}")
        return mock_url
