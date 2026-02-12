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
import asyncio
import json
import os
from utils import is_mock_mode, log_info


class TweetAnalyzer:
    """
    X公式アルゴリズム（2026年版）準拠の分析エンジン
    """
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key
        self._model = None
        if gemini_api_key and not is_mock_mode():
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                self._model = genai.GenerativeModel("gemini-2.5-flash")
                log_info("Gemini analyzer initialized successfully")
            except Exception as e:
                log_info(f"Gemini analyzer init failed: {e}")

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
        if self._model is None:
            log_info("Gemini not available, using mock analysis")
            return self._get_mock_analysis(tweet_data)

        text = tweet_data.get("text", "")
        likes = tweet_data.get("likes", 0)
        retweets = tweet_data.get("retweets", 0)
        replies = tweet_data.get("replies", 0)

        prompt = f"""あなたは𝕏のバズ分析の専門家です。
以下のツイートを分析し、「なぜ伸びたか」を構造・本質・心理の3層で説明してください。

【分析対象ツイート】
{text}

【エンゲージメント実績】
いいね: {likes} / RT: {retweets} / リプライ: {replies}

【𝕏アルゴリズムの重み（分析の前提知識）】
リプライ+著者返信=150x / リプライ=27x / ブックマーク=20x / 滞在2分超=20x / RT=2x / いいね=1x
→ リプライと滞在時間を伸ばす要素を最も重視して分析せよ

【分析の観点（7つ）】
1. **フックの型**: 冒頭10文字の型を特定（感情爆発/数字/断定/ストーリー/体言止め/その他）
2. **構造の型**: 全体構造を特定（リスト型/ビフォーアフター型/断定+理由型/計算型/感情吐露型/その他）
3. **本質**: このツイートの「テーマ」「核心」を一言で。リライトで絶対に変えてはいけない要素
4. **P(dwell)**: なぜ最後まで読むか（滞在時間を伸ばす要素）
5. **P(reply)**: なぜリプライしたくなるか（問いかけ・議論余地・共感）
6. **P(bookmark)**: なぜ保存したくなるか（有益性・再現性・具体性）
7. **なぜ伸びたか仮説**: 最も重要な理由を3つ（Hayatti式分析）

以下のJSON形式のみで回答。各説明は25文字以内。scoresは1-10の整数。

{{
  "positive_signals": {{
    "dwell_factors": "滞在を伸ばす要素",
    "reply_triggers": "リプライを誘う要素",
    "engagement_hooks": "保存・RTを誘う要素"
  }},
  "negative_signals": {{
    "not_interested_risks": "興味を失わせるリスク",
    "block_mute_risks": "ブロックのリスク"
  }},
  "scores": {{
    "dwell_potential": 8,
    "reply_potential": 7,
    "favorite_potential": 7,
    "repost_potential": 7
  }},
  "essence": "本質を1文で（20字以内）",
  "structure_type": "リスト/ビフォーアフター/断定+理由/計算/感情吐露/その他",
  "hook_type": "感情爆発/数字/断定/ストーリー/体言止め/その他",
  "why_viral": ["仮説1（20字以内）", "仮説2", "仮説3"]
}}
"""
        try:
            response = await asyncio.to_thread(
                self._model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 4096,
                    "response_mime_type": "application/json",
                }
            )
            if response and response.text:
                out = self._parse_analysis(response.text)
                log_info("Gemini analysis completed")
                return out
        except Exception as e:
            log_info(f"Gemini analysis error: {e}")

        log_info("Gemini analysis failed, falling back to mock")
        return self._get_mock_analysis(tweet_data)

    def _get_mock_analysis(self, tweet_data):
        """モック分析結果を生成"""
        log_info(f"Mock mode: Analyzing tweet (engagement: {tweet_data.get('engagement_score', 0):.0f})")

        # ツイートの特徴から分析をシミュレート
        text = tweet_data.get('text', '')
        has_question = '？' in text or '?' in text
        has_bullets = '✓' in text or '・' in text or '\n' in text
        has_numbers = any(char.isdigit() for char in text)

        # フック型を推定
        hook_type = "その他"
        first_line = text.split('\n')[0] if text else ""
        if any(w in first_line for w in ['やばい', 'えぐい', 'うおお', 'マジで']):
            hook_type = "感情爆発"
        elif has_numbers and any(w in first_line for w in ['選', '個', 'TOP', 'ステップ']):
            hook_type = "数字"
        elif any(w in first_line for w in ['断言', '何度でも', '9割', '知らない']):
            hook_type = "断定"
        elif any(w in first_line for w in ['昨日', '年前', 'したら', 'した結果']):
            hook_type = "ストーリー"

        # 構造型を推定
        structure_type = "その他"
        if has_bullets and ('選' in text or '・' in text):
            structure_type = "リスト"
        elif '前は' in text or '以前' in text or '→' in text:
            structure_type = "ビフォーアフター"
        elif has_question:
            structure_type = "断定+理由"

        return {
            "positive_signals": {
                "dwell_factors": f"{'箇条書き構成で読みやすい' if has_bullets else '短文で一気読みさせる'}",
                "reply_triggers": f"{'問いかけでリプ誘発' if has_question else '共感で意見を引き出す'}",
                "engagement_hooks": f"{'具体的数字で説得力' if has_numbers else '実用的で保存したくなる'}"
            },
            "negative_signals": {
                "not_interested_risks": "なし",
                "block_mute_risks": "なし"
            },
            "scores": {
                "dwell_potential": min(10, 7 + (1 if has_bullets else 0) + (1 if has_numbers else 0)),
                "reply_potential": min(10, 6 + (2 if has_question else 0) + 1),
                "favorite_potential": min(10, 6 + (1 if has_bullets else 0)),
                "repost_potential": min(10, 6),
                "virality": min(10, int(tweet_data.get('engagement_score', 0) / 300))
            },
            "essence": f"{text[:30]}の核心",
            "structure_type": structure_type,
            "hook_type": hook_type,
            "why_viral": [
                "ターゲット層に刺さるテーマ",
                f"{'具体的数字で信頼性' if has_numbers else '感情に訴える表現'}",
                f"{'問いかけでリプ誘発' if has_question else '共感で拡散'}"
            ]
        }

    def _parse_analysis(self, response_text):
        """GeminiのレスポンスからJSONをパース"""
        try:
            # ```json ... ``` で囲まれている場合を処理
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3].strip()
            # まず直接パースを試みる
            return json.loads(text)
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
                    "favorite_potential": 5,
                    "repost_potential": 5,
                    "virality": 5
                }
            }
