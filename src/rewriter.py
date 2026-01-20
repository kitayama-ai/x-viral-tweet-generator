"""
X公式アルゴリズム対応リライトエンジン

戦略:
1. 正のシグナル最大化
   - P(dwell): 滞在時間延長
   - P(reply): リプライ誘発
   - P(favorite/repost): 有益性強調

2. 負のシグナル完全排除
   - P(not_interested): つまらない・無関係
   - P(block/mute): 押し付けがましい・不快
"""
import json
from utils import is_mock_mode, log_info

class TweetRewriter:
    """
    X公式アルゴリズム（2026年版）に最適化したリライトエンジン
    """
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key
        # TODO: プロダクションモードでGemini初期化
    
    async def rewrite_tweet(self, original_tweet, analysis):
        """
        X公式アルゴリズムに最適化してリライト
        
        Args:
            original_tweet: dict (元ツイートデータ)
            analysis: dict (X公式アルゴリズム分析結果)
        
        Returns:
            dict: リライト結果
        """
        if is_mock_mode():
            return self._get_mock_rewrite(original_tweet, analysis)
        
        # TODO: 実装 - Gemini APIで実際にリライト
        log_info("Production mode: Gemini rewrite not yet implemented")
        return self._get_mock_rewrite(original_tweet, analysis)
    
    def _get_mock_rewrite(self, original_tweet, analysis):
        """モックリライト結果を生成"""
        log_info(f"Mock mode: Rewriting tweet (original length: {len(original_tweet.get('text', ''))})")
        
        # 元ツイートの要素を分析
        text = original_tweet.get('text', '')
        
        # サンプルリライトパターン
        rewrite_samples = [
            {
                "main_text": "2026年、AIで副業する人の9割が知らない「3つの致命的ミス」\n\n1. ツールに丸投げ → 品質が低下\n2. 差別化ゼロ → 価格競争に巻き込まれる\n3. 学習を怠る → すぐに時代遅れに\n\n成功者は「AI×自分の専門性」を武器にしてる。\n\nあなたの専門性、言語化できてる？",
                "thread": [
                    "特に重要なのが「2. 差別化」。\n\nAIツールは誰でも使える時代だから、「何を」作るかより「誰のために」作るかが勝負。\n\nニッチな専門知識 × AI = 高単価案件",
                    "実例：医療ライター×ChatGPT\n→ 一般ライターの3倍の単価\n\n理由：専門用語の正確性と、患者目線の表現をAIだけでは出せない。\n\n「あなただけの掛け算」を見つけよう。"
                ],
                "call_to_action": "あなたの専門性は何ですか？AIとどう掛け算しますか？",
                "optimization_report": {
                    "dwell_optimization": "冒頭に「9割が知らない」で好奇心を刺激。箇条書きで読みやすく、具体例で説得力を強化。",
                    "reply_optimization": "最後に「あなたの専門性は？」と直接問いかけ、自己開示を促す構成。",
                    "negative_signal_removal": "スクール勧誘を完全排除。押し付けがましさをなくし、純粋な学びに焦点。"
                }
            },
            {
                "main_text": "ChatGPT副業で月10万稼ぐロードマップ（実証済み）\n\n【1-2ヶ月目】\n✓ プロンプト100本ノック\n✓ ポートフォリオ5本作成\n\n【3-4ヶ月目】\n✓ クラウドソーシングで実績\n✓ 低単価でも評価を集める\n\n【5-6ヶ月目】\n✓ 単価交渉＆リピーター獲得\n✓ 月10万達成\n\nこの順番、間違えると挫折する。\n\n今どのステップにいる？",
                "thread": [
                    "多くの人が失敗するのは「いきなり高単価を狙う」こと。\n\n実績ゼロで単価交渉は無理。まずは低単価でも「5つ星評価10件」を目指す。\n\nこれが次の単価アップの武器になる。"
                ],
                "call_to_action": "今どのステップにいますか？次に何をしますか？",
                "optimization_report": {
                    "dwell_optimization": "ステップバイステップの構成で、自分の現在地を確認したくなる。具体的な行動リストで実践しやすさを強調。",
                    "reply_optimization": "「今どのステップ？」で自己開示を促し、コメント欄でのコミュニティ形成を誘発。",
                    "negative_signal_removal": "「実証済み」で信頼性を担保しつつ、商材販売の匂いは完全排除。"
                }
            }
        ]
        
        # ランダムに1つ選択（実際はGeminiが生成）
        import random
        return random.choice(rewrite_samples)
    
    def _parse_rewrite(self, response_text):
        """GeminiのレスポンスからJSONをパース"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        except Exception as e:
            print(f"JSON parse error: {e}")
            return {
                "main_text": "リライト失敗",
                "thread": [],
                "call_to_action": "",
                "optimization_report": {
                    "dwell_optimization": "失敗",
                    "reply_optimization": "失敗",
                    "negative_signal_removal": "失敗"
                }
            }
