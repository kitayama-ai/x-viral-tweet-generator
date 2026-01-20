"""
Xのゲストトークン管理
- モックモード: ダミートークンを返す
- プロダクションモード: 実際のトークンを取得
"""
import time
from utils import is_mock_mode, log_info

class GuestTokenManager:
    """
    Xのゲストトークンを管理
    - 2〜4時間ごとに自動更新
    - IP紐付けに対応
    """
    def __init__(self):
        self.token = None
        self.expires_at = 0
        self.bearer_token = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    
    async def get_token(self):
        """有効なゲストトークンを取得"""
        if self.token and time.time() < self.expires_at:
            return self.token
        
        # 新しいトークンを取得
        self.token = await self._fetch_new_token()
        self.expires_at = time.time() + 7200  # 2時間有効
        return self.token
    
    async def _fetch_new_token(self):
        """X APIからゲストトークンを取得"""
        if is_mock_mode():
            log_info("Mock mode: Returning dummy guest token")
            return "mock_guest_token_12345"
        
        try:
            # TODO: 実装 - curl_cffiでリクエスト
            # from curl_cffi import requests as cffi_requests
            # response = cffi_requests.post(
            #     'https://api.twitter.com/1.1/guest/activate.json',
            #     headers={
            #         'Authorization': f'Bearer {self.bearer_token}',
            #     },
            #     impersonate='chrome131'
            # )
            # return response.json()['guest_token']
            
            log_info("Production mode: Guest token fetch not yet implemented")
            return "dummy_token_production"
        except Exception as e:
            print(f"Guest token fetch error: {e}")
            return None
