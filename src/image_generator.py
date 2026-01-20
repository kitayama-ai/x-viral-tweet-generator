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
from utils import is_mock_mode, log_info

class InfographicGenerator:
    """
    X公式アルゴリズム対応：P(dwell)最大化画像生成
    """
    def __init__(self, project_id=None, location='us-central1', credentials_path=None, 
                 gemini_api_key=None, model_version="imagen-3"):
        self.project_id = project_id
        self.location = location
        self.credentials_path = credentials_path
        self.gemini_api_key = gemini_api_key
        self.model_version = model_version
        
        # TODO: プロダクションモードで初期化
        # if not is_mock_mode():
        #     from vertexai.preview.vision_models import ImageGenerationModel
        #     import vertexai
        #     # 初期化処理
    
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
        
        # TODO: 実装 - Imagen 3で実際に画像生成
        log_info("Production mode: Imagen 3 generation not yet implemented")
        return self._get_mock_image_url(rewritten_tweet)
    
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
