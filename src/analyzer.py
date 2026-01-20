"""
X公式アルゴリズム（2026年版）準拠の分析エンジン

参考: https://github.com/xai-org/x-algorithm

Xの公式アルゴリズムが予測する指標:
- P(dwell): 滞在時間（最重要）
- P(reply): リプライ（最重要）
- P(favorite): いいね
- P(repost): リツイート
- P(not_interested): 興味なし（負のシグナル）
- P(block_author): ブロック（負のシグナル）

最終スコア = Σ (weight_i × P(action_i))
"""
import json
from utils import is_mock_mode, log_info

class TweetAnalyzer:
    """
    X公式アルゴリズム（2026年版）準拠の分析エンジン
    """
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key
        # TODO: プロダクションモードでGemini初期化
        # if not is_mock_mode():
        #     import google.generativeai as genai
        #     genai.configure(api_key=gemini_api_key)
        #     self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def analyze_tweet(self, tweet_data):
        """
        X公式アルゴリズムの視点でツイートを分析
        
        Args:
            tweet_data: {
                'text': str,
                'likes': int,
                'retweets': int,
                'replies': int
            }
        
        Returns:
            dict: 分析結果
        """
        if is_mock_mode():
            return self._get_mock_analysis(tweet_data)
        
        # TODO: 実装 - Gemini APIで実際に分析
        log_info("Production mode: Gemini analysis not yet implemented")
        return self._get_mock_analysis(tweet_data)
    
    def _get_mock_analysis(self, tweet_data):
        """モック分析結果を生成"""
        log_info(f"Mock mode: Analyzing tweet (engagement: {tweet_data.get('engagement_score', 0):.0f})")
        
        # ツイートの特徴から分析をシミュレート
        text = tweet_data.get('text', '')
        has_question = '？' in text or '?' in text
        has_bullets = '✓' in text or '・' in text or '\n' in text
        has_numbers = any(char.isdigit() for char in text)
        
        return {
            "positive_signals": {
                "dwell_factors": f"冒頭の強力なフック（{text[:20]}...）が目を引く。{'箇条書き' if has_bullets else '段落構成'}で情報が整理され、読み進めたくなる。{'具体的な数字' if has_numbers else '事例'}を使って説得力を高めている。",
                "reply_triggers": f"{'最後の問いかけ' if has_question else '議論の余地を残す表現'}がリプライを誘発。共感を呼ぶ内容で、自分の意見を述べたくなる構成。",
                "engagement_hooks": "実用的で有益な情報が詰まっており、保存・共有したくなる。「これは役立つ」と感じさせる具体性。"
            },
            "negative_signals": {
                "not_interested_risks": "なし - ターゲット層（AI×副業に興味がある人）に的確にリーチする内容。",
                "block_mute_risks": "なし - スクール勧誘や押し付けがましさがなく、純粋な情報提供。"
            },
            "scores": {
                "dwell_potential": min(10, 7 + (1 if has_bullets else 0) + (1 if has_numbers else 0)),
                "reply_potential": min(10, 6 + (2 if has_question else 0) + 1),
                "virality": min(10, int(tweet_data.get('engagement_score', 0) / 300))
            }
        }
    
    def _parse_analysis(self, response_text):
        """GeminiのレスポンスからJSONをパース"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        except Exception as e:
            print(f"JSON parse error: {e}")
            return {
                "positive_signals": {
                    "dwell_factors": "分析失敗",
                    "reply_triggers": "分析失敗",
                    "engagement_hooks": "分析失敗"
                },
                "negative_signals": {
                    "not_interested_risks": "不明",
                    "block_mute_risks": "不明"
                },
                "scores": {
                    "dwell_potential": 5,
                    "reply_potential": 5,
                    "virality": 5
                }
            }
