"""
X公式アルゴリズム対応：P(dwell)最大化画像生成

戦略:
- P(dwell)延長: 視認性が高く、じっくり見たくなるデザイン
- 情報密度: 適度に詰まった有益な情報
- 滞在時間: 3-5秒以上見てもらえるインフォグラフィック

技術:
- Google Imagen 3（最新モデル）
- 日本語→英語プロンプト自動翻訳（Gemini）
- Google Cloud Storageに自動保存・公開URL発行
"""
import os
import uuid
from datetime import datetime
from utils import is_mock_mode, log_info, log_success

class InfographicGenerator:
    """
    X公式アルゴリズム対応：P(dwell)最大化画像生成
    """
    def __init__(self, project_id=None, location='us-central1', credentials_path=None, 
                 gemini_api_key=None, model_version="imagen-3", bucket_name=None):
        self.project_id = project_id
        self.location = location
        self.credentials_path = credentials_path
        self.gemini_api_key = gemini_api_key
        self.model_version = model_version
        self.bucket_name = bucket_name or f"{project_id}-viral-tweets" if project_id else None
        self.imagen_model = None
        self.gemini_model = None
        self.storage_client = None
        
        # プロダクションモードで初期化
        if not is_mock_mode():
            self._initialize_production_services()
    
    def _initialize_production_services(self):
        """プロダクションモードでのサービス初期化"""
        try:
            # Vertex AI初期化
            import vertexai
            from vertexai.preview.vision_models import ImageGenerationModel
            
            if self.credentials_path and os.path.exists(self.credentials_path):
                vertexai.init(project=self.project_id, location=self.location, 
                             credentials=self.credentials_path)
            else:
                vertexai.init(project=self.project_id, location=self.location)
            
            # Imagen 3モデル
            self.imagen_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
            
            # Gemini初期化（プロンプト翻訳用）
            if self.gemini_api_key:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Cloud Storage初期化
            from google.cloud import storage
            if self.credentials_path and os.path.exists(self.credentials_path):
                self.storage_client = storage.Client.from_service_account_json(
                    self.credentials_path
                )
            else:
                self.storage_client = storage.Client(project=self.project_id)
            
            # バケットの存在確認、なければ作成
            self._ensure_bucket_exists()
            
            log_success("Image generation services initialized")
            
        except Exception as e:
            log_info(f"Failed to initialize production services: {e}")
            self.imagen_model = None
    
    def _ensure_bucket_exists(self):
        """Cloud Storageバケットの存在確認・作成"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.storage_client.create_bucket(
                    self.bucket_name,
                    location=self.location
                )
                # 公開読み取り権限を設定
                bucket.make_public(recursive=True, future=True)
                log_success(f"Created bucket: {self.bucket_name}")
            else:
                log_info(f"Bucket exists: {self.bucket_name}")
        except Exception as e:
            log_info(f"Bucket check/creation failed: {e}")
    
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
            str: 公開アクセス可能な画像URL
        """
        if is_mock_mode():
            return self._get_mock_image_url(rewritten_tweet)
        
        # プロダクションモード: Imagen 3で実際に画像生成
        if not self.imagen_model:
            log_info("Imagen model not initialized, returning empty URL")
            return ""
        
        try:
            # 1. 日本語プロンプトを英語に翻訳
            english_prompt = await self._translate_to_english_prompt(rewritten_tweet)
            
            # 2. Imagen 3で画像生成
            log_info("Generating image with Imagen 3...")
            images = self.imagen_model.generate_images(
                prompt=english_prompt,
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="block_some",
                person_generation="allow_adult"
            )
            
            # 3. Cloud Storageにアップロード
            if images and len(images) > 0:
                image_url = await self._upload_to_storage(images[0])
                log_success(f"Image generated: {image_url}")
                return image_url
            else:
                log_info("No images generated")
                return ""
                
        except Exception as e:
            log_info(f"Image generation failed: {e}")
            return ""
    
    async def _translate_to_english_prompt(self, rewritten_tweet):
        """
        日本語ツイート内容を英語の画像生成プロンプトに変換
        
        Args:
            rewritten_tweet: リライトされたツイートデータ
        
        Returns:
            str: 英語の画像生成プロンプト
        """
        if not self.gemini_model:
            # Geminiが利用できない場合はシンプルな英語プロンプト
            return "Modern infographic about AI and side business, clean design, Twitter style, information dense"
        
        try:
            # Geminiで日本語→英語プロンプト変換
            japanese_content = rewritten_tweet['main_text']
            if rewritten_tweet.get('thread'):
                japanese_content += "\n" + "\n".join(rewritten_tweet['thread'][:2])
            
            translation_prompt = f"""
以下の日本語ツイート内容を、Imagen 3で視覚的に魅力的なインフォグラフィックを生成するための英語プロンプトに変換してください。

要件:
- P(dwell)最大化: 3-5秒じっくり見たくなるデザイン
- 情報密度: キーポイントを視覚化
- X（Twitter）スタイル: モダン、クリーン、読みやすい
- 16:9の横長フォーマット

ツイート内容:
{japanese_content[:500]}

英語プロンプト（100単語以内、"Create"などの命令文なし、純粋な説明のみ）:
"""
            
            response = self.gemini_model.generate_content(translation_prompt)
            english_prompt = response.text.strip()
            
            # プロンプトを最適化（不要な接頭辞を削除）
            english_prompt = english_prompt.replace("Create ", "").replace("Generate ", "")
            english_prompt = english_prompt.replace("An image of ", "").replace("A ", "")
            
            log_info(f"Translated prompt: {english_prompt[:100]}...")
            return english_prompt
            
        except Exception as e:
            log_info(f"Translation failed: {e}. Using default prompt.")
            return "Modern infographic about AI and side business, clean design, Twitter style, information dense, 16:9 format"
    
    async def _upload_to_storage(self, image):
        """
        生成画像をCloud Storageにアップロード
        
        Args:
            image: Imagen生成画像オブジェクト
        
        Returns:
            str: 公開URL
        """
        try:
            # ユニークなファイル名生成
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = f"viral_tweets/{timestamp}_{unique_id}.png"
            
            # バケット取得
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(filename)
            
            # 画像をバイトデータとしてアップロード
            image_bytes = image._image_bytes
            blob.upload_from_string(image_bytes, content_type='image/png')
            
            # 公開URLを作成
            blob.make_public()
            public_url = blob.public_url
            
            log_success(f"Uploaded to: {public_url}")
            return public_url
            
        except Exception as e:
            log_info(f"Upload to storage failed: {e}")
            return ""
    
    def _get_mock_image_url(self, rewritten_tweet):
        """モック画像URLを生成"""
        log_info(f"Mock mode: Generating infographic (text length: {len(rewritten_tweet.get('main_text', ''))})")
        
        # Placeholder画像サービスを使用（実際はImagen 3で生成）
        import hashlib
        text_hash = hashlib.md5(rewritten_tweet.get('main_text', '').encode()).hexdigest()[:8]
        
        # Placeholder画像URL（実際のImagen 3生成画像のURLを模擬）
        mock_url = f"https://storage.googleapis.com/mock-bucket/infographic_{text_hash}.png"
        
        log_info(f"Mock image URL: {mock_url}")
        return mock_url
