"""
Xスクレイピング機能
- モックモード: サンプルデータを返す
- 手動モード: ツイートURLから個別取得
- APIモード: X API v2で取得
- Playwrightモード: 自動スクレイピング（未実装）
"""
import asyncio
import random
import re
import os
from datetime import datetime, timedelta
from utils import get_random_user_agent, is_mock_mode, log_info, log_error, log_success
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    log_info("tweepy not installed. X API mode will not work.")

class XScraper:
    def __init__(self, guest_token_manager, proxy_manager=None, twitter_api_key=None, twitter_api_secret=None, twitter_bearer_token=None):
        self.guest_token_manager = guest_token_manager
        self.proxy_manager = proxy_manager
        self.twitter_bearer_token = twitter_bearer_token
        
        # X API v2 クライアント初期化
        self.twitter_client = None
        if TWEEPY_AVAILABLE and twitter_bearer_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=twitter_bearer_token)
                log_success("X API v2 client initialized")
            except Exception as e:
                log_error(f"Failed to initialize X API client: {e}")
    
    async def scrape_account_timeline(self, username, max_tweets=100):
        """
        特定アカウントの最新ツイートを取得
        
        Args:
            username: Xのユーザー名（@なし）
            max_tweets: 取得するツイート数（デフォルト100）
        
        Returns:
            list: ツイートデータのリスト
        """
        if is_mock_mode():
            return await self._get_mock_tweets(username, max_tweets)
        
        # X API v2を使用
        if self.twitter_client:
            return await self._scrape_with_api(username, max_tweets)
        
        # TODO: 実装 - Playwrightで実際にスクレイピング
        log_info(f"Production mode: Scraping @{username} (not yet implemented)")
        log_info("Hint: Set TWITTER_BEARER_TOKEN in .env to use X API v2")
        return []
    
    async def scrape_tweet_by_url(self, tweet_url):
        """
        ツイートURLから個別のツイートを取得（手動入力モード）
        
        Args:
            tweet_url: ツイートのURL（例: https://x.com/username/status/1234567890）
        
        Returns:
            dict: ツイートデータ、取得失敗時はNone
        """
        # URLからツイートIDを抽出
        tweet_id = self._extract_tweet_id(tweet_url)
        if not tweet_id:
            log_error(f"Invalid tweet URL: {tweet_url}")
            return None
        
        if is_mock_mode():
            log_info(f"Mock mode: Generating sample data for tweet ID {tweet_id}")
            return await self._get_mock_single_tweet(tweet_url, tweet_id)
        
        # X API v2を使用
        if self.twitter_client:
            return await self._get_tweet_by_id_api(tweet_id, tweet_url)
        
        log_error("X API not configured. Please set TWITTER_BEARER_TOKEN in .env")
        return None
    
    async def _scrape_with_api(self, username, max_tweets):
        """X API v2を使用してツイートを取得"""
        log_info(f"Using X API v2 to fetch tweets from @{username}")
        
        try:
            # ユーザーIDを取得
            user = self.twitter_client.get_user(username=username)
            if not user.data:
                log_error(f"User @{username} not found")
                return []
            
            user_id = user.data.id
            
            # ツイートを取得
            tweets_response = self.twitter_client.get_users_tweets(
                id=user_id,
                max_results=min(max_tweets, 100),  # API制限
                tweet_fields=['created_at', 'public_metrics', 'text'],
                exclude=['retweets', 'replies']
            )
            
            if not tweets_response.data:
                log_info(f"No tweets found for @{username}")
                return []
            
            # データ整形
            tweets = []
            for tweet in tweets_response.data:
                metrics = tweet.public_metrics
                tweet_data = {
                    'id': str(tweet.id),
                    'text': tweet.text,
                    'likes': metrics['like_count'],
                    'retweets': metrics['retweet_count'],
                    'replies': metrics['reply_count'],
                    'timestamp': tweet.created_at.isoformat(),
                    'url': f'https://x.com/{username}/status/{tweet.id}',
                    'engagement_score': 0
                }
                
                # エンゲージメントスコア計算
                tweet_data['engagement_score'] = (
                    tweet_data['likes'] + 
                    (tweet_data['retweets'] * 2) + 
                    (tweet_data['replies'] * 1.5)
                )
                
                tweets.append(tweet_data)
            
            log_success(f"Fetched {len(tweets)} tweets from @{username} via X API")
            return tweets
            
        except Exception as e:
            log_error(f"X API error: {e}")
            return []
    
    async def _get_tweet_by_id_api(self, tweet_id, tweet_url):
        """X API v2を使用して個別ツイートを取得"""
        log_info(f"Fetching tweet ID {tweet_id} via X API v2")
        
        try:
            tweet_response = self.twitter_client.get_tweet(
                id=tweet_id,
                tweet_fields=['created_at', 'public_metrics', 'text', 'author_id']
            )
            
            if not tweet_response.data:
                log_error(f"Tweet {tweet_id} not found")
                return None
            
            tweet = tweet_response.data
            metrics = tweet.public_metrics
            
            # ユーザー名を取得
            user_response = self.twitter_client.get_user(id=tweet.author_id)
            username = user_response.data.username if user_response.data else 'unknown'
            
            tweet_data = {
                'id': str(tweet.id),
                'text': tweet.text,
                'likes': metrics['like_count'],
                'retweets': metrics['retweet_count'],
                'replies': metrics['reply_count'],
                'timestamp': tweet.created_at.isoformat(),
                'url': tweet_url,
                'engagement_score': 0
            }
            
            # エンゲージメントスコア計算
            tweet_data['engagement_score'] = (
                tweet_data['likes'] + 
                (tweet_data['retweets'] * 2) + 
                (tweet_data['replies'] * 1.5)
            )
            
            log_success(f"Successfully fetched tweet {tweet_id}")
            return tweet_data
            
        except Exception as e:
            log_error(f"Failed to fetch tweet {tweet_id}: {e}")
            return None
    
    def _extract_tweet_id(self, tweet_url):
        """ツイートURLからIDを抽出"""
        # https://x.com/username/status/1234567890
        # https://twitter.com/username/status/1234567890
        pattern = r'(?:x\.com|twitter\.com)/\w+/status/(\d+)'
        match = re.search(pattern, tweet_url)
        return match.group(1) if match else None
    
    async def _get_mock_single_tweet(self, tweet_url, tweet_id):
        """モック用の単一ツイートデータを生成"""
        sample = {
            "text": "AIを使った副業で月10万円達成するための完全ロードマップ\n\n1. ChatGPT/Claude活用スキル習得\n2. ポートフォリオ作成\n3. クラウドソーシングで実績\n4. 単価交渉で収益アップ\n\n重要なのは「AIを使える」だけじゃなく「AIで価値を生み出せる」こと。\n\nあなたなら何から始める？",
            "likes": 1850,
            "retweets": 420,
            "replies": 95
        }
        
        return {
            'id': tweet_id,
            'text': sample['text'],
            'likes': sample['likes'],
            'retweets': sample['retweets'],
            'replies': sample['replies'],
            'timestamp': datetime.now().isoformat(),
            'url': tweet_url,
            'engagement_score': sample['likes'] + (sample['retweets'] * 2) + (sample['replies'] * 1.5)
        }
    
    async def _get_mock_tweets(self, username, max_tweets):
        """モックツイートデータを生成"""
        log_info(f"Mock mode: Generating sample tweets for @{username}")
        
        sample_tweets = [
            {
                "text": "AIエージェントが2026年の副業を変える。ChatGPTやClaudeを使った自動化で、月10万円稼ぐ人が続出。重要なのは「何を自動化するか」の選択眼。\n\n✓ コンテンツ生成\n✓ データ分析\n✓ カスタマーサポート\n\nあなたならどれから始める？",
                "likes": 1250,
                "retweets": 340,
                "replies": 89
            },
            {
                "text": "副業でAIツールを使う時の3つの落とし穴：\n\n1. ツールに依存しすぎる\n2. 品質チェックを怠る\n3. 差別化を考えない\n\n結局、AIは「加速装置」であって「魔法の杖」じゃない。あなたの専門性×AIが最強。\n\nこれ、実感してる人いる？",
                "likes": 890,
                "retweets": 210,
                "replies": 67
            },
            {
                "text": "2026年、最も稼げるAI副業スキル TOP5\n\n1位: プロンプトエンジニアリング\n2位: AIツール導入コンサル\n3位: AI生成コンテンツの編集\n4位: データラベリング（高品質）\n5位: AI倫理監査\n\n意外と「AIを使う」より「AIを正しく使わせる」スキルが高単価。",
                "likes": 2100,
                "retweets": 580,
                "replies": 142
            },
            {
                "text": "ChatGPTで副業始めて3ヶ月の収益報告\n\n月5万→月18万に成長\n\n✓ ブログ記事執筆代行\n✓ SNS投稿テンプレート販売\n✓ プロンプト設計サポート\n\nコツは「自分の経験×AI」を掛け算すること。AIだけじゃ差別化できない時代。\n\nあなたの強みは何？",
                "likes": 1680,
                "retweets": 450,
                "replies": 103
            },
            {
                "text": "AI副業で月10万円稼ぐための現実的なロードマップ\n\n1ヶ月目: スキル習得（無料教材）\n2ヶ月目: ポートフォリオ作成\n3ヶ月目: 低単価案件で実績\n4ヶ月目: 単価アップ交渉\n5ヶ月目: リピーター獲得\n6ヶ月目: 月10万達成\n\nこの通りやって成功した人、意外と多い。",
                "likes": 1420,
                "retweets": 380,
                "replies": 95
            }
        ]
        
        tweets = []
        for i, sample in enumerate(sample_tweets[:max_tweets]):
            tweet_id = f"mock_{username}_{i+1}"
            timestamp = (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat()
            
            tweet_data = {
                'id': tweet_id,
                'text': sample['text'],
                'likes': sample['likes'] + random.randint(-100, 100),
                'retweets': sample['retweets'] + random.randint(-50, 50),
                'replies': sample['replies'] + random.randint(-20, 20),
                'timestamp': timestamp,
                'url': f'https://x.com/{username}/status/{tweet_id}',
                'engagement_score': 0
            }
            
            # エンゲージメントスコア計算
            tweet_data['engagement_score'] = (
                tweet_data['likes'] + 
                (tweet_data['retweets'] * 2) + 
                (tweet_data['replies'] * 1.5)
            )
            
            tweets.append(tweet_data)
        
        # エンゲージメントスコアでソート
        tweets.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        return tweets[:max_tweets]
    
    def _get_random_user_agent(self):
        """ランダムなUser-Agentを取得"""
        return get_random_user_agent()
