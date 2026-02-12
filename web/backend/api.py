"""
FastAPI バックエンド
X バズ投稿生成AI
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os

# プロジェクトルートの .env を読む（uvicorn の cwd に依存しないよう絶対パスで）
_base = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
_env_path = os.path.join(_base, '.env')
try:
    from dotenv import load_dotenv
    if os.path.exists(_env_path):
        load_dotenv(_env_path)
    else:
        load_dotenv()  # cwd の .env をフォールバック
except Exception:
    pass

# 親ディレクトリのsrcをパスに追加
sys.path.insert(0, os.path.join(_base, 'src'))

from scraper import XScraper
from guest_token_manager import GuestTokenManager
from analyzer import TweetAnalyzer
from rewriter import TweetRewriter
from image_generator import InfographicGenerator
from sheets_manager import SheetsManager
from x_research import XResearcher
import asyncio

app = FastAPI(
    title="X バズ投稿生成AI API",
    description="X公式アルゴリズム（2026年版）準拠のバズ投稿生成システム",
    version="1.0.0"
)

@app.on_event("startup")
def _log_mode():
    """起動時に .env の MODE を表示（本番でモックになる不具合の確認用）"""
    mode = os.getenv("MODE", "(not set)")
    print(f"[API] MODE={mode} (production=本番, mock=モック)", flush=True)

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

class ImageGenerateRequest(BaseModel):
    sheet_row_id: int
    rewritten_text: str
    thread: List[str] = []
    call_to_action: str = ""

class ImageGenerateResponse(BaseModel):
    success: bool
    image_url: str
    row_id: int
    message: str

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
async def generate(request: GenerateRequest, req: Request):
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
        scraper = XScraper(
            guest_token_manager,
            proxy_manager=None,
            twitter_bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
        )
        analyzer = TweetAnalyzer(gemini_api_key=os.getenv('GEMINI_API_KEY'))
        rewriter = TweetRewriter(gemini_api_key=os.getenv('GEMINI_API_KEY'))
        image_gen = InfographicGenerator(
            project_id=os.getenv('GCP_PROJECT_ID'),
            location='us-central1',
            credentials_path=os.path.join(_base, 'config', 'credentials.json'),
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        sheets_manager = SheetsManager(
            spreadsheet_id=os.getenv('SPREADSHEET_ID'),
            credentials_path=os.path.join(_base, 'config', 'credentials.json')
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
            
            # 画像生成（Nano Banana Pro）
            image_url = await image_gen.generate_infographic(rewritten)
            # 相対パスを絶対URLに変換（スプシで参照できるように）
            if image_url and image_url.startswith("/"):
                base_url = str(req.base_url).rstrip("/")
                image_url = f"{base_url}{image_url}"
            
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
        
        # Google Sheetsに保存
        for i, result in enumerate(results):
            try:
                # SheetsManagerが期待する形式に変換
                sheets_data = {
                    'original_tweet': {
                        'text': result['original_text'],
                        'likes': result['original_likes'],
                        'retweets': result['original_retweets'],
                        'replies': result['original_replies'],
                        'url': result['original_url'],
                        'category': result['category']
                    },
                    'analysis': {
                        'scores': result['scores'],
                        'positive_signals': result['positive_signals'],
                        'negative_signals': result['negative_signals']
                    },
                    'rewritten': {
                        'main_text': result['rewritten_text'],
                        'thread': result['thread'],
                        'call_to_action': result['call_to_action']
                    },
                    'image_url': result['image_url']
                }
                await sheets_manager.save_result(sheets_data)
            except Exception as e:
                print(f"[WARN] Failed to save result {i+1} to Sheets: {e}", flush=True)
        
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
        import traceback
        print(f"[ERROR] {type(e).__name__}: {str(e)}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-image", response_model=ImageGenerateResponse)
async def generate_image_for_row(request: ImageGenerateRequest):
    """
    Google Sheetsの特定行に対して画像を生成
    
    Args:
        request: 行ID、リライトテキスト、スレッド、問いかけ
    
    Returns:
        画像生成結果
    """
    try:
        # 画像生成サービス初期化
        image_gen = InfographicGenerator(
            project_id=os.getenv('GCP_PROJECT_ID'),
            location='us-central1',
            credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            bucket_name=os.getenv('GCS_BUCKET_NAME')
        )
        
        # リライトデータを構築
        rewritten = {
            'main_text': request.rewritten_text,
            'thread': request.thread,
            'call_to_action': request.call_to_action
        }
        
        # 画像生成
        image_url = await image_gen.generate_infographic(rewritten)
        
        if not image_url:
            raise HTTPException(
                status_code=500,
                detail="画像生成に失敗しました"
            )
        
        # Google Sheetsを更新
        from sheets_manager import SheetsManager
        sheets = SheetsManager(
            credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            spreadsheet_id=os.getenv('SPREADSHEET_ID')
        )
        
        success = sheets.update_image_url(request.sheet_row_id, image_url)
        
        return ImageGenerateResponse(
            success=success,
            image_url=image_url,
            row_id=request.sheet_row_id,
            message="画像生成が完了しました" if success else "画像生成は成功しましたが、Sheetsの更新に失敗しました"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sheet-rows")
async def get_sheet_rows(limit: int = 50):
    """
    Google Sheetsのデータを取得（管理画面用）
    
    Args:
        limit: 取得する行数の上限
    
    Returns:
        行データのリスト
    """
    try:
        from sheets_manager import SheetsManager
        sheets = SheetsManager(
            credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            spreadsheet_id=os.getenv('SPREADSHEET_ID')
        )
        
        if not sheets.worksheet:
            raise HTTPException(
                status_code=503,
                detail="Google Sheetsに接続できません"
            )
        
        # 全行データを取得（ヘッダー以降）
        all_rows = sheets.worksheet.get_all_values()
        
        # ヘッダーをスキップ、最新から取得
        data_rows = all_rows[1:limit+1] if len(all_rows) > 1 else []
        
        # 辞書形式に変換
        result = []
        for idx, row in enumerate(data_rows, start=2):  # 行番号は2から（1はヘッダー）
            if len(row) >= 13:
                result.append({
                    'row_number': idx,
                    'collected_date': row[0],
                    'original_url': row[1],
                    'category': row[2],
                    'original_text': row[3],
                    'likes': row[4],
                    'retweets': row[5],
                    'replies': row[6],
                    'rewritten_text': row[10],
                    'thread': row[11],
                    'call_to_action': row[12],
                    'image_url': row[13] if len(row) > 13 else '',
                    'image_generated': row[14] if len(row) > 14 else 'FALSE'
                })
        
        return {"rows": result, "count": len(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── 画像配信エンドポイント ───

@app.get("/api/images/{filename}")
async def serve_image(filename: str):
    """生成画像を配信"""
    images_dir = os.path.join(_base, "output", "images")
    filepath = os.path.join(images_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    media_type = "image/jpeg" if filename.endswith(".jpg") else "image/png"
    return FileResponse(filepath, media_type=media_type)

# ─── リサーチエンドポイント（Hayatti式 Grok x_search 統合） ───

class ResearchRequest(BaseModel):
    topic: str
    locale: str = "ja"
    audience: str = "both"
    days: int = 7

class ViralAnalysisRequest(BaseModel):
    topic: str
    count: int = 10

@app.post("/api/research")
async def research_topic(request: ResearchRequest):
    """
    トピックについてXのリアルタイム情報をリサーチ（Hayatti式3段階リサーチ）

    Grok (xAI API) の x_search でリアルタイムのXトレンドを取得。
    Grok未設定時はGeminiにフォールバック。
    """
    try:
        researcher = XResearcher(
            xai_api_key=os.getenv('XAI_API_KEY'),
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        result = await researcher.research_topic(
            topic=request.topic,
            locale=request.locale,
            audience=request.audience,
            days=request.days
        )
        return {"status": "ok", "research": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/viral-analysis")
async def analyze_viral_patterns(request: ViralAnalysisRequest):
    """
    指定トピックのバズツイートパターンを分析

    Grokでリアルタイムのバズ投稿を収集し、
    フックの型・構造・心理トリガー・「なぜ伸びたか」を抽出。
    """
    try:
        researcher = XResearcher(
            xai_api_key=os.getenv('XAI_API_KEY'),
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        result = await researcher.analyze_viral_patterns(
            topic=request.topic,
            count=request.count
        )
        return {"status": "ok", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
