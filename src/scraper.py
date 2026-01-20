"""
Xスクレイピング機能
- モックモード: サンプルデータを返す
- プロダクションモード: Playwrightで実際にスクレイピング
"""
import asyncio
import random
from datetime import datetime, timedelta
from utils import get_random_user_agent, is_mock_mode, log_info

class XScraper:
    def __init__(self, guest_token_manager, proxy_manager=None):
        self.guest_token_manager = guest_token_manager
        self.proxy_manager = proxy_manager
    
    async def scrape_account_timeline(self, username, max_tweets=100):
        """
        特定アカウントの最新ツイートを取得（ゲストモード）
        
        Args:
            username: Xのユーザー名（@なし）
            max_tweets: 取得するツイート数（デフォルト100）
        
        Returns:
            list: ツイートデータのリスト
        """
        if is_mock_mode():
            return await self._get_mock_tweets(username, max_tweets)
        
        # TODO: 実装 - Playwrightで実際にスクレイピング
        log_info(f"Production mode: Scraping @{username} (not yet implemented)")
        return []
    
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
