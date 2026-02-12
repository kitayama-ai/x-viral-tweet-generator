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
import asyncio
import json
import os
from utils import is_mock_mode, log_info


class TweetRewriter:
    """
    X公式アルゴリズム（2026年版）に最適化したリライトエンジン
    """
    def __init__(self, gemini_api_key=None):
        self.gemini_api_key = gemini_api_key
        self._model = None
        if gemini_api_key and not is_mock_mode():
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                self._model = genai.GenerativeModel("gemini-2.5-flash")
                log_info("Gemini rewriter initialized successfully")
            except Exception as e:
                log_info(f"Gemini rewriter init failed: {e}")

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
        if self._model is None:
            log_info("Gemini not available, using mock rewrite")
            return self._get_mock_rewrite(original_tweet, analysis)

        text = original_tweet.get("text", "")
        essence = (analysis or {}).get("essence") or "（分析の本質が未設定）"
        structure_type = (analysis or {}).get("structure_type") or "その他"
        hook_type = (analysis or {}).get("hook_type") or "その他"
        why_viral = (analysis or {}).get("why_viral") or []
        why_viral_str = "、".join(why_viral) if why_viral else "（未分析）"
        pos = (analysis or {}).get("positive_signals") or {}
        dwell_factors = pos.get("dwell_factors") or ""
        reply_triggers = pos.get("reply_triggers") or ""

        prompt = f"""あなたは𝕏で15万フォロワー・累計6億円稼いだバズの天才です。
元ツイートのテーマ・本質を絶対に変えず、𝕏アルゴリズムに最適化してリライトしてください。

━━━━━━━━━━━━━━━━━━
■ 𝕏アルゴリズム重み付け（2026年版）
━━━━━━━━━━━━━━━━━━
- リプライ+著者返信: 150x（最強。会話を生む設計にする）
- リプライ: 27x
- ブックマーク: 20x（「保存したくなる」有益情報を入れる）
- 滞在時間2分超: 20x（最後まで読ませる構成にする）
- RT: 2x / いいね: 1x（最弱。いいね狙いは非効率）

━━━━━━━━━━━━━━━━━━
■ フック（1行目）の鉄則
━━━━━━━━━━━━━━━━━━
最初の10文字でスクロールを止める。以下から最適なパターンを選べ:

【感情爆発系】（最強。共感リプが殺到する）
- 「やばい。マジでやばい。」
- 「うおおおお」「これえぐい」
- 「これ。何度でも言う。」

【具体数字インパクト系】（保存・RTされやすい）
- 「〇〇を3ヶ月やった結果、」
- 「月○万円稼いだ方法を公開」
- 「〇〇選（偶数OK：10選、7選）」

【断定・挑発系】（議論リプが増える）
- 「断言しますが、」「何度でも言うけど、」
- 「9割が知らない」「知らないと損するんだけど、」
- 「これ知ってる人ほぼいない。」

【ストーリー系】（滞在時間が伸びる）
- 「昨日〇〇したら、とんでもないことが起きた。」
- 「数年前は〇〇だったのが、今では〇〇。」
- 「ぶっちゃけると、」

【体言止め短文系】（TLでの視認性が高い）
- 「〇〇の作り方。」
- 「これマジでそう。」
- 「結論出た。」

━━━━━━━━━━━━━━━━━━
■ 構造パターン（実績データから抽出）
━━━━━━━━━━━━━━━━━━
以下の5パターンから最適なものを選べ:

【パターンA: リスト型】（ブックマーク最強）
フック（「〇〇選」「〇〇まとめ」）
空行
・項目1：補足
・項目2：補足
...
空行
CTA

【パターンB: ビフォーアフター型】（共感リプ最強）
フック（過去の状態）
空行
過去→現在の変化を描写
空行
教訓・メッセージ
空行
CTA

【パターンC: 断定＋理由型】（議論リプ狙い）
フック（強い主張）
空行
理由1
理由2
理由3
空行
CTA

【パターンD: 計算・数字型】（保存されやすい）
フック（具体数字）
空行
計算式や内訳を箇条書き
空行
結論
空行
CTA

【パターンE: 感情吐露型】（いいね+リプ両方伸びる）
感情的な一言（短文）
空行
本音を2-3行で展開
空行
共感を誘う締め or 問いかけ

━━━━━━━━━━━━━━━━━━
■ 共通構造ルール
━━━━━━━━━━━━━━━━━━
- 改行多め（8-12行）でTL占有面積を最大化
- 1行は15-25文字。短いほどインパクト
- 箇条書きには ・ → ✓ 【】 を使う
- 空行を効果的に使い「間」を作る
- 140文字ギリギリまで使い切る（「もっと読む」をクリックさせる）

━━━━━━━━━━━━━━━━━━
■ 心理トリガー（必ず2つ以上を織り込む）
━━━━━━━━━━━━━━━━━━
- 好奇心ギャップ: 結論を隠し「知りたい」を生む
- 損失回避: 「知らないと損」「やらないとヤバい」
- 社会的証明: 「〇万人が実践」「話題の」
- 自己投影: 「昔の自分に言いたい」「〇〇な人あるある」
- 希少性: 「ここだけの話」「有料級」
- 実体験の説得力: 「自分がやってみた結果」「実際に〇〇した」
- ビフォーアフター: 「以前は〇〇だったのが今は〇〇」

━━━━━━━━━━━━━━━━━━
■ CTA（最後の行）
━━━━━━━━━━━━━━━━━━
リプライ誘発を最優先（いいねの27-150倍の価値）:

【問いかけ型】
- 「あなたならどれから始める？」
- 「これ、どう思う？」
- 「あなたの経験、教えて」

【共感誘発型】（これが実は最強）
- 「ほんとうに頑張ってよかった。」
- 「マジでこれ。」
- 「マジでこれ。実感してる人いる？」

【保存促進型】
- 「永久保存版。ブクマしておいて」
- 「これ知っておくだけで全然違う」

━━━━━━━━━━━━━━━━━━
■ 日本語スタイルルール（超重要）
━━━━━━━━━━━━━━━━━━
トップインフルエンサーの文体を完全コピーせよ:

【語尾パターン】
- 体言止め多用:「〜な時代。」「〜という結論。」「〜一択。」
- 口語の語尾:「〜なんだけど」「〜してる」「〜だよな」「〜かも」
- 感嘆:「〜すぎるw」「〜やばすぎ」「〜えぐい」

【感情語・強調語】
- 「マジで」「ぶっちゃけ」「ガチで」
- 「やばい」「えぐい」「最強」「神」
- 「、、、」（三点リーダの代わりに読点3つ）

【文体の鉄則】
- 句読点は最小限。改行やスペースで代替
- 𝕏の特殊フォントXを使う（𝕏）
- 絵文字は0-2個。使うなら🔥💰👀程度
- 「w」は文末に1つだけOK（wwwは古い）
- 一人称は「僕」が親近感UP

【AI臭を絶対に消す】
NG: 「〜について解説します」「まとめると」「〜が重要です」「つまり」「〜しましょう」「〜ではないでしょうか」
OK: 口語体、体言止め、倒置法、感情語、「〜なんだけど」「〜してみた」

━━━━━━━━━━━━━━━━━━
■ 絶対NG（ペナルティ直結）
━━━━━━━━━━━━━━━━━━
- 外部リンクを本文に入れない（リーチ激減）
- ハッシュタグ3個以上（-40%ペナルティ）
- ネガティブ・攻撃的トーン（Grok感情分析で配信減）
- スクール勧誘・商材販売の匂い
- 嘘・誇張（「たった1日で100万」系）
- 改行なしの長文ブロック
- 「です。ます。」の連続（教科書臭くなる）
- がちがちのノウハウのみ（人間味がない）
- セールス感の強いポスト（実績報告だけ、感想RTばかり）

━━━━━━━━━━━━━━━━━━
■ バズツイートの成功法則（実データ分析120件から抽出）
━━━━━━━━━━━━━━━━━━
1. 「〇〇選」リスト型は平均いいね2000超え。項目は具体的＋意外性を入れる
2. 感情爆発の短文（「やばい」「えぐい」）＋具体数字の組み合わせが最強
3. ビフォーアフター（昔は〇〇→今は〇〇）は共感リプが3倍増
4. 「計算してみろ」系（単価×人数=売上）はブックマーク率が高い
5. 本音吐露・愚痴系は意外とリプが伸びる（人間味）
6. 1ツイートに情報を詰めすぎない。1メッセージ1ツイート

━━━━━━━━━━━━━━━━━━
■ 元ツイート
━━━━━━━━━━━━━━━━━━
{text}

■ 分析結果
- 本質: {essence}
- 構造タイプ: {structure_type}
- フックの型: {hook_type}
- なぜ伸びたか: {why_viral_str}
- 滞在を伸ばす要素: {dwell_factors}
- リプライを誘う要素: {reply_triggers}

━━━━━━━━━━━━━━━━━━
■ 出力指示
━━━━━━━━━━━━━━━━━━
上記ルールをすべて適用し、元ツイートのテーマ・核心を維持したままリライトせよ。
人間が書いたとしか思えない自然な文体で。AI臭ゼロ。
- main_text: 140文字ギリギリのメインツイート
- thread: スレッド0-3本（情報の深掘り。各スレッドも同じ文体で）
- call_to_action: リプライ誘発の問いかけ or 共感誘発の一言

JSON形式のみで回答。重要: 文中の改行は必ず \\n で表現すること（生の改行をJSON値に入れるな）:
{{
  "main_text": "1行目\\n\\n2行目\\n3行目のように\\nで改行",
  "thread": ["スレッド1", "スレッド2"],
  "call_to_action": "問いかけ",
  "optimization_report": {{
    "dwell_optimization": "滞在時間向けの工夫（15字以内）",
    "reply_optimization": "リプライ誘発の工夫（15字以内）",
    "negative_signal_removal": "負のシグナル排除の工夫（15字以内）"
  }}
}}
"""
        try:
            response = await asyncio.to_thread(
                self._model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4096,
                    "response_mime_type": "application/json",
                }
            )
            if response and response.text:
                out = self._parse_rewrite(response.text)
                log_info("Gemini rewrite completed (original theme preserved)")
                return out
        except Exception as e:
            log_info(f"Gemini rewrite error: {e}")

        log_info("Gemini rewrite failed, falling back to mock")
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
            # ```json ... ``` で囲まれている場合を処理
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3].strip()
            # まず直接パースを試みる
            return json.loads(text)
        except json.JSONDecodeError as e:
            log_info(f"JSON parse error (attempt 1): {e}")
            # JSON文字列内の生改行をエスケープして再試行
            try:
                # 方式: JSONの構造外の改行を\\nに変換
                # ダブルクォート内の生改行だけを\\nに置換
                in_string = False
                escaped = False
                chars = list(text)
                for i, c in enumerate(chars):
                    if escaped:
                        escaped = False
                        continue
                    if c == '\\':
                        escaped = True
                        continue
                    if c == '"':
                        in_string = not in_string
                        continue
                    if in_string and c == '\n':
                        chars[i] = '\\n'
                fixed = ''.join(chars)
                return json.loads(fixed)
            except Exception as e2:
                log_info(f"JSON parse error (attempt 2): {e2}")
                # 最後の手段: { から最後の } までを切り出して同じ処理
                try:
                    start = text.index('{')
                    end = text.rindex('}') + 1
                    raw = text[start:end]
                    # 同じ生改行エスケープ処理
                    in_string = False
                    escaped = False
                    chars = list(raw)
                    for i, c in enumerate(chars):
                        if escaped:
                            escaped = False
                            continue
                        if c == '\\':
                            escaped = True
                            continue
                        if c == '"':
                            in_string = not in_string
                            continue
                        if in_string and c == '\n':
                            chars[i] = '\\n'
                    return json.loads(''.join(chars))
                except Exception as e3:
                    log_info(f"JSON parse error (attempt 3): {e3}")
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
