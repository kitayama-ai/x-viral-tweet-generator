"""
FastAPI バックエンド
X バズ投稿生成AI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os

# 親ディレクトリのsrcをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from scraper import XScraper
from guest_token_manager import GuestTokenManager
from analyzer import TweetAnalyzer
from rewriter import TweetRewriter
from image_generator import InfographicGenerator
import asyncio

app = FastAPI(
    title="X バズ投稿生成AI API",
    description="X公式アルゴリズム（2026年版）準拠のバズ投稿生成システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストモデル
class GenerateRequest(BaseModel):
    accounts: List[str]
    settings: Dict[str, Any]

# レスポンスモデル
class GenerateResponse(BaseModel):
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {
        "status": "ok",
        "service": "X バズ投稿生成AI",
        "version": "1.0.0",
        "algorithm": "X Official Algorithm (2026)",
        "features": [
            "P(dwell) maximization",
            "P(reply) triggering",
            "Negative signal elimination"
        ]
    }

@app.get("/api/health")
async def health():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}

@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    バズ投稿を生成
    
    Args:
        request: アカウントリストと設定
    
    Returns:
        生成結果
    """
    try:
        # サービス初期化
        guest_token_manager = GuestTokenManager()
        scraper = XScraper(guest_token_manager, proxy_manager=None)
        analyzer = TweetAnalyzer(gemini_api_key=os.getenv('GEMINI_API_KEY'))
        rewriter = TweetRewriter(gemini_api_key=os.getenv('GEMINI_API_KEY'))
        image_gen = InfographicGenerator(
            project_id=os.getenv('GCP_PROJECT_ID'),
            location='us-central1',
            credentials_path='../../config/credentials.json',
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        
        # ステップ1: ツイート収集
        all_tweets = []
        for account in request.accounts:
            tweets = await scraper.scrape_account_timeline(
                username=account,
                max_tweets=100  # 固定
            )
            for tweet in tweets:
                tweet['category'] = 'AI×副業'
            all_tweets.extend(tweets)
            await asyncio.sleep(1)
        
        # ステップ2: エンゲージメントフィルタリング
        min_likes = request.settings.get('min_likes', 500)
        min_retweets = request.settings.get('min_retweets', 50)
        
        viral_tweets = [
            t for t in all_tweets
            if t['likes'] >= min_likes and t['retweets'] >= min_retweets
        ]
        viral_tweets.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        if len(viral_tweets) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"エンゲージメント閾値を満たすツイートが見つかりませんでした（いいね≥{min_likes}, RT≥{min_retweets}）"
            )
        
        # ステップ3: 分析
        tweets_to_analyze = min(
            len(viral_tweets),
            request.settings.get('tweets_to_analyze', 10)
        )
        analyzed_tweets = []
        
        for tweet in viral_tweets[:tweets_to_analyze]:
            analysis = await analyzer.analyze_tweet(tweet)
            analyzed_tweets.append({
                'original': tweet,
                'analysis': analysis
            })
            await asyncio.sleep(0.1)
        
        # ステップ4: リライト＋画像生成
        tweets_to_rewrite = min(
            len(analyzed_tweets),
            request.settings.get('tweets_to_rewrite', 5)
        )
        results = []
        
        for item in analyzed_tweets[:tweets_to_rewrite]:
            # リライト
            rewritten = await rewriter.rewrite_tweet(
                item['original'],
                item['analysis']
            )
            
            # 画像生成（モックモードでは省略）
            image_url = await image_gen.generate_infographic(rewritten)
            
            # 結果を整形
            result = {
                'category': item['original'].get('category', 'AI×副業'),
                'original_text': item['original']['text'],
                'original_likes': item['original']['likes'],
                'original_retweets': item['original']['retweets'],
                'original_replies': item['original']['replies'],
                'original_url': item['original']['url'],
                'rewritten_text': rewritten['main_text'],
                'thread': rewritten.get('thread', []),
                'call_to_action': rewritten.get('call_to_action', ''),
                'scores': item['analysis']['scores'],
                'positive_signals': item['analysis']['positive_signals'],
                'negative_signals': item['analysis']['negative_signals'],
                'image_url': image_url
            }
            results.append(result)
            await asyncio.sleep(0.1)
        
        # サマリー
        summary = {
            'total_collected': len(all_tweets),
            'total_filtered': len(viral_tweets),
            'total_analyzed': len(analyzed_tweets),
            'total_rewritten': len(results),
            'accounts_processed': len(request.accounts)
        }
        
        return GenerateResponse(results=results, summary=summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
