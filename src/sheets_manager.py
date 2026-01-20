"""
Google Sheets保存機能
- モックモード: CSVファイルに保存
- プロダクションモード: 実際のGoogle Sheetsに保存
"""
import csv
import os
from datetime import datetime
from utils import is_mock_mode, log_info, log_success

class SheetsManager:
    """
    Google Sheetsにデータを保存
    - 自動で行を追加
    - Drive共有リンクも管理
    """
    def __init__(self, credentials_path=None, spreadsheet_id=None):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        
        # 親ディレクトリのoutputフォルダを参照
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.mock_csv_path = os.path.join(parent_dir, "output/results.csv")
        
        # モックモード用のCSVファイル準備
        if is_mock_mode():
            os.makedirs(os.path.dirname(self.mock_csv_path), exist_ok=True)
            self._initialize_mock_csv()
        
        # TODO: プロダクションモードでGoogle Sheets初期化
    
    def _initialize_mock_csv(self):
        """モックCSVファイルのヘッダーを初期化"""
        if not os.path.exists(self.mock_csv_path):
            headers = [
                '収集日',
                '元URL',
                'カテゴリ',
                '元ツイート本文',
                'いいね数',
                'リツイート数',
                'リプライ数',
                'エンゲージメントスコア',
                'P(dwell)要因',
                'P(reply)要因',
                'リライト本文',
                'スレッド',
                '問いかけ',
                '図解画像URL'
            ]
            with open(self.mock_csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            log_info(f"Mock CSV initialized: {self.mock_csv_path}")
    
    async def save_result(self, data):
        """
        分析・リライト結果を保存
        
        Args:
            data: {
                'original_tweet': dict,
                'analysis': dict,
                'rewritten': dict,
                'image_url': str
            }
        """
        if is_mock_mode():
            self._save_to_mock_csv(data)
        else:
            # TODO: 実装 - Google Sheetsに保存
            log_info("Production mode: Google Sheets save not yet implemented")
            self._save_to_mock_csv(data)
    
    def _save_to_mock_csv(self, data):
        """モックCSVファイルに保存"""
        row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data['original_tweet']['url'],
            data['original_tweet'].get('category', ''),
            data['original_tweet']['text'][:100] + '...',  # 100文字まで
            data['original_tweet']['likes'],
            data['original_tweet']['retweets'],
            data['original_tweet']['replies'],
            data['original_tweet']['engagement_score'],
            data['analysis']['positive_signals']['dwell_factors'][:100] + '...',
            data['analysis']['positive_signals']['reply_triggers'][:100] + '...',
            data['rewritten']['main_text'][:100] + '...',
            ' | '.join(data['rewritten'].get('thread', []))[:100] + '...' if data['rewritten'].get('thread') else '',
            data['rewritten']['call_to_action'],
            data['image_url']
        ]
        
        with open(self.mock_csv_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        log_success(f"Saved to {self.mock_csv_path}")
