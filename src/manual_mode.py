"""
手動入力モード - ツイートURLから分析・リライト

使い方:
  python manual_mode.py https://x.com/username/status/1234567890
  python manual_mode.py https://x.com/username/status/1234567890 https://x.com/another/status/9876543210
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# モジュールインポート
from scraper import XScraper
from guest_token_manager import GuestTokenManager
from analyzer import TweetAnalyzer
from rewriter import TweetRewriter
from image_generator import InfographicGenerator
from sheets_manager import SheetsManager
from utils import log_info, log_success, log_error

async def analyze_tweet_from_url(tweet_url):
    """ツイートURLから分析・リライト"""
    
    log_info(f"=" * 60)
    log_info(f"ツイートURL: {tweet_url}")
    log_info(f"=" * 60)
    
    # サービス初期化
    guest_token_manager = GuestTokenManager()
    scraper = XScraper(
        guest_token_manager,
        twitter_bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
    )
    analyzer = TweetAnalyzer(gemini_api_key=os.getenv('GEMINI_API_KEY'))
    rewriter = TweetRewriter(gemini_api_key=os.getenv('GEMINI_API_KEY'))
    image_gen = InfographicGenerator(
        project_id=os.getenv('GCP_PROJECT_ID'),
        location='us-central1',
        credentials_path='../config/credentials.json',
        gemini_api_key=os.getenv('GEMINI_API_KEY')
    )
    sheets = SheetsManager(
        credentials_path='../config/credentials.json',
        spreadsheet_id=os.getenv('SPREADSHEET_ID')
    )
    
    # ステップ1: ツイート取得
    log_info("ステップ1: ツイート取得")
    tweet = await scraper.scrape_tweet_by_url(tweet_url)
    
    if not tweet:
        log_error("ツイートの取得に失敗しました")
        return None
    
    log_success(f"ツイート取得成功")
    log_info(f"  本文: {tweet['text'][:100]}...")
    log_info(f"  いいね: {tweet['likes']:,}")
    log_info(f"  リツイート: {tweet['retweets']:,}")
    log_info(f"  リプライ: {tweet['replies']:,}")
    log_info(f"  エンゲージメント: {tweet['engagement_score']:,.0f}")
    print()
    
    # ステップ2: X公式アルゴリズム分析
    log_info("ステップ2: X公式アルゴリズム分析")
    analysis = await analyzer.analyze_tweet(tweet)
    
    log_success(f"分析完了")
    log_info(f"  P(dwell): {analysis['scores']['dwell_potential']}/10")
    log_info(f"  P(reply): {analysis['scores']['reply_potential']}/10")
    log_info(f"  P(favorite): {analysis['scores']['favorite_potential']}/10")
    log_info(f"  P(repost): {analysis['scores']['repost_potential']}/10")
    print()
    
    # ステップ3: リライト生成
    log_info("ステップ3: X公式アルゴリズム対応リライト")
    rewritten = await rewriter.rewrite_tweet(tweet, analysis)
    
    log_success(f"リライト完了（{len(rewritten['main_text'])}文字）")
    log_info(f"  本文: {rewritten['main_text']}")
    if rewritten.get('thread_tweets'):
        log_info(f"  スレッド: {len(rewritten['thread_tweets'])}ツイート")
    print()
    
    # ステップ4: 結果を保存
    log_info("ステップ4: 結果を保存")
    await sheets.save_result({
        'original_tweet': tweet,
        'analysis': analysis,
        'rewritten': rewritten,
        'image_url': None
    })
    log_success("保存完了")
    print()
    
    return {
        'tweet': tweet,
        'analysis': analysis,
        'rewritten': rewritten
    }

async def main():
    """メイン実行フロー"""
    
    log_info("=" * 60)
    log_info("X バズ投稿生成AI - 手動入力モード")
    log_info("=" * 60)
    print()
    
    # コマンドライン引数チェック
    if len(sys.argv) < 2:
        log_error("使い方: python manual_mode.py <ツイートURL> [<ツイートURL2> ...]")
        log_info("例: python manual_mode.py https://x.com/username/status/1234567890")
        return
    
    tweet_urls = sys.argv[1:]
    log_info(f"{len(tweet_urls)}件のツイートを処理します")
    print()
    
    # 各ツイートを処理
    results = []
    for i, url in enumerate(tweet_urls, 1):
        log_info(f"[{i}/{len(tweet_urls)}] 処理中...")
        result = await analyze_tweet_from_url(url)
        if result:
            results.append(result)
        print()
    
    # 完了
    log_info("=" * 60)
    log_success(f"✅ {len(results)}件の処理が完了しました！")
    log_info("=" * 60)
    
    if os.getenv('SPREADSHEET_ID'):
        log_info(f"結果: Google Sheets ({os.getenv('SPREADSHEET_ID')}) を確認してください")
    else:
        log_info("結果: output/results.csv を確認してください")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_info("\n処理を中断しました")
    except Exception as e:
        log_error(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
