"""
X バズ投稿自動生成システム - メイン実行ファイル

X公式アルゴリズム（2026年版）完全準拠
参考: https://github.com/xai-org/x-algorithm
"""
import asyncio
import json
import os
import sys
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
from utils import load_json_file, log_info, log_success, log_error, is_mock_mode

async def main():
    """メイン実行フロー"""
    
    # モード表示
    mode = "モックモード（テスト用）" if is_mock_mode() else "プロダクションモード"
    log_info(f"=== X バズ投稿自動生成システム 起動 ===")
    log_info(f"モード: {mode}")
    log_info(f"X公式アルゴリズム（2026年版）準拠")
    print()
    
    # 設定読み込み
    try:
        # 親ディレクトリのconfigフォルダを参照
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        accounts_config = load_json_file(os.path.join(parent_dir, 'config/accounts.json'))
        settings = load_json_file(os.path.join(parent_dir, 'config/settings.json'))
        log_success("設定ファイルを読み込みました")
    except Exception as e:
        log_error(f"設定ファイルの読み込みに失敗: {e}")
        return
    
    # 各サービス初期化
    log_info("サービスを初期化中...")
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
        credentials_path='config/credentials.json',
        gemini_api_key=os.getenv('GEMINI_API_KEY')
    )
    sheets = SheetsManager(
        credentials_path='config/credentials.json',
        spreadsheet_id=os.getenv('SPREADSHEET_ID')
    )
    log_success("サービス初期化完了")
    print()
    
    # ステップ1: ツイート収集
    log_info("=" * 60)
    log_info("ステップ1: ツイート収集")
    log_info("=" * 60)
    all_tweets = []
    
    max_accounts = min(
        len(accounts_config['benchmark_accounts']),
        settings['collection']['max_accounts_per_run']
    )
    
    for i, account in enumerate(accounts_config['benchmark_accounts'][:max_accounts], 1):
        log_info(f"[{i}/{max_accounts}] @{account['username']} から収集中...")
        
        tweets = await scraper.scrape_account_timeline(
            username=account['username'],
            max_tweets=settings['collection']['tweets_per_account']
        )
        
        for tweet in tweets:
            tweet['category'] = account['category']
        
        all_tweets.extend(tweets)
        log_success(f"  → {len(tweets)}件のツイートを取得")
        
        await asyncio.sleep(settings['rate_limiting']['delay_between_accounts'])
    
    log_success(f"合計 {len(all_tweets)} 件のツイートを収集")
    print()
    
    # ステップ2: エンゲージメントフィルタリング
    log_info("=" * 60)
    log_info("ステップ2: エンゲージメントフィルタリング")
    log_info("=" * 60)
    threshold = settings['filtering']['engagement_threshold']
    
    viral_tweets = [
        t for t in all_tweets
        if t['likes'] >= threshold['min_likes']
        and t['retweets'] >= threshold['min_retweets']
    ]
    
    viral_tweets.sort(key=lambda x: x['engagement_score'], reverse=True)
    log_success(f"高エンゲージメントツイート: {len(viral_tweets)} 件")
    
    if len(viral_tweets) == 0:
        log_error("エンゲージメント閾値を満たすツイートがありません")
        log_info(f"閾値を下げてください（現在: いいね{threshold['min_likes']}以上、RT{threshold['min_retweets']}以上）")
        return
    print()
    
    # ステップ3: X公式アルゴリズム分析
    log_info("=" * 60)
    log_info("ステップ3: X公式アルゴリズム分析")
    log_info("=" * 60)
    analyzed_tweets = []
    
    tweets_to_analyze = min(len(viral_tweets), settings['processing']['tweets_to_analyze'])
    
    for i, tweet in enumerate(viral_tweets[:tweets_to_analyze], 1):
        log_info(f"[{i}/{tweets_to_analyze}] 分析中...")
        log_info(f"  URL: {tweet['url']}")
        log_info(f"  エンゲージメント: {tweet['engagement_score']:.0f}")
        
        analysis = await analyzer.analyze_tweet(tweet)
        analyzed_tweets.append({
            'original': tweet,
            'analysis': analysis
        })
        
        log_success(f"  → P(dwell): {analysis['scores']['dwell_potential']}/10")
        log_success(f"  → P(reply): {analysis['scores']['reply_potential']}/10")
        
        await asyncio.sleep(0.1)
    
    log_success(f"{len(analyzed_tweets)} 件のツイートを分析完了")
    print()
    
    # ステップ4: リライト＋画像生成
    log_info("=" * 60)
    log_info("ステップ4: X公式アルゴリズム対応リライト＋画像生成")
    log_info("=" * 60)
    
    tweets_to_rewrite = min(len(analyzed_tweets), settings['processing']['tweets_to_rewrite'])
    
    for i, item in enumerate(analyzed_tweets[:tweets_to_rewrite], 1):
        log_info(f"[{i}/{tweets_to_rewrite}] 処理中...")
        log_info(f"  元URL: {item['original']['url']}")
        
        # リライト
        log_info("  → リライト生成中...")
        rewritten = await rewriter.rewrite_tweet(
            item['original'],
            item['analysis']
        )
        log_success(f"     リライト完了（{len(rewritten['main_text'])}文字）")
        
        # 画像生成
        if settings['processing']['generate_images']:
            log_info("  → 図解画像生成中...")
            image_url = await image_gen.generate_infographic(rewritten)
            log_success(f"     画像生成完了")
        else:
            image_url = None
        
        # Google Sheetsに保存
        log_info("  → 結果を保存中...")
        await sheets.save_result({
            'original_tweet': item['original'],
            'analysis': item['analysis'],
            'rewritten': rewritten,
            'image_url': image_url
        })
        log_success("  → 保存完了")
        print()
        
        await asyncio.sleep(0.1)
    
    # 完了
    log_info("=" * 60)
    log_success("✅ すべての処理が完了しました！")
    log_info("=" * 60)
    
    if is_mock_mode():
        log_info("結果: output/results.csv を確認してください")
        log_info("")
        log_info("プロダクションモードで実行するには:")
        log_info("1. .env ファイルを作成（env.template を参考）")
        log_info("2. MODE=production に変更")
        log_info("3. API認証情報を設定")
    else:
        log_info(f"結果: Google Sheets ({os.getenv('SPREADSHEET_ID')}) を確認してください")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_info("\n処理を中断しました")
    except Exception as e:
        log_error(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
