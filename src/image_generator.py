"""
Nano Banana Pro 画像生成エンジン

戦略:
- P(dwell)延長: 視認性が高く、じっくり見たくなるデザイン
- 情報密度: 適度に詰まった有益な情報
- 滞在時間: 3-5秒以上見てもらえるインフォグラフィック

技術:
- Google Nano Banana Pro (google-genai パッケージ)
- ローカル保存 → FastAPIで静的配信
"""
import asyncio
import os
import uuid
from datetime import datetime
from utils import is_mock_mode, log_info, log_success


class InfographicGenerator:
    """
    Nano Banana Pro でインフォグラフィック画像を生成
    """
    def __init__(self, project_id=None, location=None, credentials_path=None,
                 gemini_api_key=None, model_version=None, bucket_name=None):
        self.gemini_api_key = gemini_api_key
        self._client = None
        self._model_name = "nano-banana-pro-preview"

        # 画像保存先（プロジェクトルート/output/images/）
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.images_dir = os.path.join(parent_dir, "output", "images")
        os.makedirs(self.images_dir, exist_ok=True)

        # プロダクションモードで初期化
        if not is_mock_mode() and gemini_api_key:
            self._initialize()

    def _initialize(self):
        """Nano Banana Pro クライアント初期化"""
        try:
            from google import genai
            self._client = genai.Client(api_key=self.gemini_api_key)
            log_success(f"Nano Banana Pro initialized (model: {self._model_name})")
        except Exception as e:
            log_info(f"Nano Banana Pro init failed: {e}")
            self._client = None

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
            str: 画像のURL（/api/images/<filename> 形式）
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

            # 3. レスポンスから画像を取得して保存
            if response and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                        # ファイル名生成
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        unique_id = str(uuid.uuid4())[:8]
                        ext = "jpg" if "jpeg" in (part.inline_data.mime_type or "") else "png"
                        filename = f"{timestamp}_{unique_id}.{ext}"
                        filepath = os.path.join(self.images_dir, filename)

                        # 保存
                        with open(filepath, 'wb') as f:
                            f.write(part.inline_data.data)

                        image_url = f"/api/images/{filename}"
                        log_success(f"Image generated: {image_url} ({len(part.inline_data.data)} bytes)")
                        return image_url

            log_info("No image in Nano Banana Pro response")
            return ""

        except Exception as e:
            log_info(f"Image generation failed: {e}")
            return ""

    def _build_image_prompt(self, rewritten_tweet):
        """ツイート内容からNano Banana Pro用プロンプトを構築"""
        main_text = rewritten_tweet.get('main_text', '')
        thread = rewritten_tweet.get('thread', [])

        # ツイートの核心をまとめる
        content_summary = main_text[:200]
        if thread:
            content_summary += "\n" + thread[0][:150]

        prompt = f"""Create a visually striking infographic for a Japanese Twitter/X post.

Content to visualize:
{content_summary}

Design requirements:
- Modern dark theme with accent colors (blue, purple, or green gradients)
- Clean, professional layout suitable for Twitter timeline
- Key points displayed as a visual list with icons or numbers
- Large, readable Japanese text for the main headline
- Aspect ratio: 16:9 (landscape, optimized for Twitter card)
- High information density but not cluttered
- No watermarks, no stock photo feel
- Style: premium tech infographic, like a top-tier newsletter visual
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
