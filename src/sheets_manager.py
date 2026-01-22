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
        self.worksheet = None
        
        # 親ディレクトリのoutputフォルダを参照
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.mock_csv_path = os.path.join(parent_dir, "output/results.csv")
        
        # モックモード用のCSVファイル準備
        if is_mock_mode():
            os.makedirs(os.path.dirname(self.mock_csv_path), exist_ok=True)
            self._initialize_mock_csv()
        else:
            # プロダクションモード: Google Sheets初期化
            self._initialize_google_sheets()
    
    def _initialize_google_sheets(self):
        """Google Sheets APIの初期化"""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            # スコープ設定
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 認証情報の読み込み
            if self.credentials_path and os.path.exists(self.credentials_path):
                # ローカル環境: credentials.jsonから認証
                creds = Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=scopes
                )
            else:
                # Cloud Run環境: デフォルト認証を使用（サービスアカウントが自動適用される）
                import google.auth
                creds, project = google.auth.default(scopes=scopes)
            
            # gspreadクライアント作成
            self.gc = gspread.authorize(creds)
            
            # スプレッドシート取得
            self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            self.worksheet = self.spreadsheet.sheet1
            
            # ヘッダーが存在しない場合は初期化
            if self.worksheet.row_count == 0 or not self.worksheet.row_values(1):
                self._initialize_sheet_headers()
            
            log_success(f"Google Sheets initialized: {self.spreadsheet_id}")
            
        except Exception as e:
            log_info(f"Google Sheets initialization failed: {e}. Falling back to CSV.")
            # フォールバック: CSVに保存
            os.makedirs(os.path.dirname(self.mock_csv_path), exist_ok=True)
            self._initialize_mock_csv()
    
    def _initialize_sheet_headers(self):
        """スプレッドシートのヘッダー行を初期化"""
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
            '図解画像URL',
            '画像生成済み'
        ]
        self.worksheet.append_row(headers)
        # ヘッダー行を太字に
        self.worksheet.format('A1:O1', {'textFormat': {'bold': True}})
        log_info("Sheet headers initialized")
    
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
                '図解画像URL',
                '画像生成済み'
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
        # モックモードでも、Google Sheetsが利用可能なら保存する
        if self.worksheet:
            self._save_to_google_sheets(data)
        else:
            log_info("Google Sheets not available, saving to CSV")
            self._save_to_mock_csv(data)
    
    def _save_to_google_sheets(self, data):
        """Google Sheetsに保存"""
        try:
            row = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data['original_tweet'].get('url', ''),
                data['original_tweet'].get('category', 'AI×副業'),
                data['original_tweet']['text'][:500],  # 500文字まで
                data['original_tweet']['likes'],
                data['original_tweet']['retweets'],
                data['original_tweet']['replies'],
                data['original_tweet'].get('engagement_score', 0),
                data['analysis']['positive_signals']['dwell_factors'][:300],
                data['analysis']['positive_signals']['reply_triggers'][:300],
                data['rewritten']['main_text'][:500],
                ' | '.join(data['rewritten'].get('thread', []))[:500] if data['rewritten'].get('thread') else '',
                data['rewritten'].get('call_to_action', ''),
                data.get('image_url', ''),
                'FALSE'  # 画像生成済みフラグ（初期値はFALSE）
            ]
            
            self.worksheet.append_row(row)
            log_success(f"Saved to Google Sheets (ID: {self.spreadsheet_id})")
            
        except Exception as e:
            log_info(f"Failed to save to Google Sheets: {e}. Falling back to CSV.")
            self._save_to_mock_csv(data)
    
    def update_image_url(self, row_number, image_url):
        """
        指定行の画像URLを更新
        
        Args:
            row_number: 行番号（2から開始、1はヘッダー）
            image_url: 生成した画像のURL
        """
        try:
            if not is_mock_mode() and self.worksheet:
                # 画像URL列（N列）と画像生成済みフラグ（O列）を更新
                self.worksheet.update_cell(row_number, 14, image_url)
                self.worksheet.update_cell(row_number, 15, 'TRUE')
                log_success(f"Updated image URL for row {row_number}")
                return True
            else:
                log_info("Mock mode: Cannot update Sheet directly")
                return False
        except Exception as e:
            log_info(f"Failed to update image URL: {e}")
            return False
    
    def get_row_data(self, row_number):
        """
        指定行のデータを取得
        
        Args:
            row_number: 行番号（2から開始）
        
        Returns:
            dict: 行データ
        """
        try:
            if not is_mock_mode() and self.worksheet:
                values = self.worksheet.row_values(row_number)
                if len(values) >= 13:
                    return {
                        'row_number': row_number,
                        'collected_date': values[0],
                        'original_url': values[1],
                        'category': values[2],
                        'original_text': values[3],
                        'likes': values[4],
                        'retweets': values[5],
                        'replies': values[6],
                        'rewritten_text': values[10],
                        'thread': values[11],
                        'call_to_action': values[12],
                        'image_url': values[13] if len(values) > 13 else '',
                        'image_generated': values[14] if len(values) > 14 else 'FALSE'
                    }
            return None
        except Exception as e:
            log_info(f"Failed to get row data: {e}")
            return None
    
    def _save_to_mock_csv(self, data):
        """モックCSVファイルに保存"""
        row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data['original_tweet'].get('url', ''),
            data['original_tweet'].get('category', ''),
            data['original_tweet']['text'][:100] + '...',  # 100文字まで
            data['original_tweet']['likes'],
            data['original_tweet']['retweets'],
            data['original_tweet']['replies'],
            data['original_tweet'].get('engagement_score', 0),
            data['analysis']['positive_signals']['dwell_factors'][:100] + '...',
            data['analysis']['positive_signals']['reply_triggers'][:100] + '...',
            data['rewritten']['main_text'][:100] + '...',
            ' | '.join(data['rewritten'].get('thread', []))[:100] + '...' if data['rewritten'].get('thread') else '',
            data['rewritten'].get('call_to_action', ''),
            data.get('image_url', ''),
            'FALSE'  # 画像生成済みフラグ
        ]
        
        with open(self.mock_csv_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        log_success(f"Saved to {self.mock_csv_path}")
