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
            raise RuntimeError("MODE=mock: Geminiリライトはモックモードでは使用できません。.envのMODE=productionに設定してください")
        if self._model is None:
            raise RuntimeError("Gemini APIの初期化に失敗しました。GEMINI_API_KEYを確認してください")

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
元ツイートをリライトしてください。

━━━━━━━━━━━━━━━━━━
■ 最重要ルール: 型・書き方・テーマを真似しつつ中身を変えろ
━━━━━━━━━━━━━━━━━━
- 元ツイートの「書き方」「フォーマット」「構造」を徹底的に真似しろ
- テーマ・ジャンルは同じにしろ（AI副業ならAI副業、ニッチ事業ならニッチ事業）
- ★ただし具体的な中身（項目・事例・数字）は微妙に変えろ★
  例: 「AI副業TOP5」→「AI副業TOP7」にして、ランキング内容を一部入れ替える
  例: 「ニッチ事業10選」→「ニッチ事業8選」にして、いくつかの事業を別のものに差し替える
  例: 「月10万→月18万」→「月8万→月25万」のように数字をリアルに変える
- フォーマットは完全に保持: ランキング→ランキング、リスト→リスト、箇条書き→箇条書き
- 項目数は±2程度の変化OK（5項目→7項目、10項目→8項目など）
- 書き方の特徴（絵文字使い、改行パターン、語尾）を忠実に再現しろ
- 丸パクリはNG。パッと見で同じツイートに見えないレベルにしろ

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
上記ルールをすべて適用してリライトせよ。
元ツイートの書き方・フォーマット・テーマを真似しつつ、具体的な中身（項目・数字・事例）を微妙に変えろ。
丸パクリに見えないが、同じジャンル・同じ型のバズツイートに見える程度に。AI臭ゼロ。
- main_text: 元ツイートと同程度の長さでリライト（長文なら長文のまま。短くまとめるな）
- thread: 空配列でOK。1つのmain_textにすべてまとめろ
- call_to_action: リプライ誘発の問いかけ or 共感誘発の一言

JSON形式のみで回答。重要ルール:
1. 文中の改行は必ず \\n で表現すること（生の改行をJSON値に入れるな）
2. main_textは元ツイートと同程度の長さにしろ。長文ツイートなら長文のままリライト。短くまとめるな
3. threadは使わなくてOK（空配列[]でよい）。1つのmain_textに全部入れろ
4. optimization_reportは各項目10字以内で超簡潔に
{{
  "main_text": "リライト全文をここに1つにまとめる",
  "thread": [],
  "call_to_action": "問いかけ",
  "optimization_report": {{
    "dwell_optimization": "10字以内",
    "reply_optimization": "10字以内",
    "negative_signal_removal": "10字以内"
  }}
}}
"""
        # 最大2回リトライ（JSONパース失敗対策）
        for attempt in range(2):
            try:
                response = await asyncio.to_thread(
                    self._model.generate_content,
                    prompt,
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 8192,
                        "response_mime_type": "application/json",
                    }
                )
                if response and response.candidates:
                    # Gemini 2.5 Flash (thinking model) は複数partを返す場合がある
                    # thought=True のpartはスキップし、JSONテキストだけ取り出す
                    json_text = None
                    for part in response.candidates[0].content.parts:
                        if getattr(part, 'thought', False):
                            continue  # thinking partはスキップ
                        if hasattr(part, 'text') and part.text:
                            json_text = part.text
                            break
                    if json_text:
                        out = self._parse_rewrite(json_text)
                        if out.get("main_text") != "リライト失敗":
                            log_info("Gemini rewrite completed (original theme preserved)")
                            return out
                        else:
                            log_info(f"Gemini JSON parse failed (attempt {attempt+1}). Raw (first 300): {repr(json_text[:300])}")
                elif response and response.text:
                    out = self._parse_rewrite(response.text)
                    if out.get("main_text") != "リライト失敗":
                        log_info("Gemini rewrite completed (original theme preserved)")
                        return out
            except Exception as e:
                import traceback
                log_info(f"Gemini rewrite error (attempt {attempt+1}): {type(e).__name__}: {e}")
                traceback.print_exc()
            if attempt < 1:
                log_info("Retrying Gemini rewrite...")
                await asyncio.sleep(1)

        raise RuntimeError("Geminiリライトが2回連続で失敗しました。APIの状態を確認してください")

    def _get_mock_rewrite(self, original_tweet, analysis):
        """
        モックリライト結果を生成
        元ツイートの内容・フォーマットをそのまま活かし、
        フック＋CTA だけ追加する動的モック
        """
        text = original_tweet.get('text', '')
        log_info(f"Mock mode: Rewriting tweet (original length: {len(text)})")

        # 元ツイートのテキストをそのまま活用して簡易リライト
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # フック（1行目）を強化
        first_line = lines[0] if lines else text[:50]
        hook = f"これえぐい。{first_line}"

        # 本文（2行目以降）はそのまま保持
        body_lines = lines[1:] if len(lines) > 1 else []
        body = '\n'.join(body_lines)

        # CTA追加
        cta = "これ、どう思う？"

        main_text = f"{hook}\n\n{body}\n\n{cta}" if body else f"{hook}\n\n{cta}"

        return {
            "main_text": main_text,
            "thread": [
                f"補足すると、{first_line}がバズったのは内容そのものが刺さったから。\n\n構造だけ真似ても意味ない。中身が大事。"
            ],
            "call_to_action": cta,
            "optimization_report": {
                "dwell_optimization": "元ツイートの構造を保持して滞在時間を維持",
                "reply_optimization": "問いかけCTAでリプライ誘発",
                "negative_signal_removal": "元の内容を尊重しネガティブ要素なし"
            }
        }

    def _fix_raw_newlines(self, text):
        """JSON文字列内の生改行を \\n にエスケープ"""
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
        return ''.join(chars)

    def _parse_rewrite(self, response_text):
        """GeminiのレスポンスからJSONをパース（複数フォールバック付き）"""
        text = response_text.strip()

        # ```json ... ``` で囲まれている場合を処理
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3].strip()

        # Attempt 1: 直接パース
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            log_info(f"JSON parse error (attempt 1): {e}")

        # Attempt 2: 生改行をエスケープしてパース
        try:
            fixed = self._fix_raw_newlines(text)
            return json.loads(fixed)
        except Exception as e:
            log_info(f"JSON parse error (attempt 2): {e}")

        # Attempt 3: { から最後の } までを切り出して同処理
        try:
            start = text.index('{')
            end = text.rindex('}') + 1
            raw = text[start:end]
            fixed = self._fix_raw_newlines(raw)
            return json.loads(fixed)
        except Exception as e:
            log_info(f"JSON parse error (attempt 3): {e}")

        # Attempt 4: 正規表現で main_text を直接抽出
        try:
            import re
            mt = re.search(r'"main_text"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
            if mt:
                main_text = mt.group(1).replace('\n', '\\n')
                # thread
                th = re.search(r'"thread"\s*:\s*\[(.*?)\]', text, re.DOTALL)
                thread_raw = th.group(1).strip() if th else ""
                threads = [s.strip().strip('"').replace('\n', '\\n')
                           for s in thread_raw.split('",') if s.strip()] if thread_raw else []
                # CTA
                cta = re.search(r'"call_to_action"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
                cta_text = cta.group(1).replace('\n', '\\n') if cta else ""

                log_info("JSON parse recovered via regex extraction")
                return {
                    "main_text": main_text,
                    "thread": threads,
                    "call_to_action": cta_text,
                    "optimization_report": {
                        "dwell_optimization": "regex recovered",
                        "reply_optimization": "regex recovered",
                        "negative_signal_removal": "regex recovered"
                    }
                }
        except Exception as e:
            log_info(f"JSON parse error (attempt 4 regex): {e}")

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
