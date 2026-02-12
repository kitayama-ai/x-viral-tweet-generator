"""
X（Twitter）リアルタイムリサーチエンジン

Hayatti氏の x-research-skills 手法を参考に構築:
https://github.com/HayattiQ/x-research-skills

戦略:
1. Grok (xAI API) の x_search でリアルタイムのXトレンドを取得
2. 「広く薄く」探索 → クラスター抽出 → 深掘りの3段階
3. 情報の優先順位: 公式 > GitHub > 二次情報 > X投稿
4. Geminiフォールバック: xAI APIキーが無い場合はGemini+Web検索で代替
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from utils import is_mock_mode, log_info, log_error, log_success


class XResearcher:
    """
    xAI Grok API (x_search) を使ったXリアルタイムリサーチ
    Grokが使えない場合はGeminiにフォールバック
    """

    def __init__(self, xai_api_key=None, gemini_api_key=None):
        self.xai_api_key = xai_api_key
        self.gemini_api_key = gemini_api_key
        self._grok_available = bool(xai_api_key)
        self._gemini_model = None

        if xai_api_key:
            log_info("xAI Grok researcher initialized (x_search enabled)")
        elif gemini_api_key and not is_mock_mode():
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                log_info("Gemini researcher initialized (Grok fallback)")
            except Exception as e:
                log_info(f"Gemini researcher init failed: {e}")

    async def research_topic(self, topic, locale="ja", audience="both", days=7):
        """
        トピックについてXのリアルタイム情報をリサーチ

        Args:
            topic: 調査するトピック
            locale: "ja" or "global"
            audience: "engineer" / "investor" / "both"
            days: 検索期間（日）

        Returns:
            dict: Context Pack形式のリサーチ結果
        """
        if is_mock_mode():
            return self._get_mock_research(topic)

        if self._grok_available:
            return await self._research_with_grok(topic, locale, audience, days)

        if self._gemini_model:
            return await self._research_with_gemini(topic, locale, audience, days)

        log_info("No research API available, using mock")
        return self._get_mock_research(topic)

    async def analyze_viral_patterns(self, topic, count=10):
        """
        指定トピックのバズツイートパターンを分析

        Hayatti氏の手法:
        1. 広く薄く探索してクラスターを抽出
        2. クラスターごとに代表ポストを選定
        3. 各ポストの「なぜ伸びたか」仮説を立てる

        Args:
            topic: 分析するトピック
            count: 取得する素材数

        Returns:
            dict: バズパターン分析結果
        """
        if is_mock_mode():
            return self._get_mock_viral_analysis(topic)

        if self._grok_available:
            return await self._analyze_viral_with_grok(topic, count)

        if self._gemini_model:
            return await self._analyze_viral_with_gemini(topic, count)

        return self._get_mock_viral_analysis(topic)

    async def _research_with_grok(self, topic, locale, audience, days):
        """xAI Grok API (x_search) でリサーチ"""
        log_info(f"Grok x_search: researching '{topic}'")

        now = datetime.utcnow()
        locale_line = (
            "検索・収集は日本語圏を優先。必要なら英語一次情報も併用。"
            if locale == "ja"
            else "検索・収集はグローバル一次情報（英語中心）を優先。"
        )

        prompt = f"""日本語で回答して。

目的: 𝕏でバズるツイートを作るための周辺リサーチ
トピック: {topic}
時点: {now.isoformat()}
検索窓の目安: 直近{days}日

前提:
- {locale_line}
- 数字/仕様/制限は捏造しない。不明は unknown と書く。
- 長文の直接引用はしない（要旨で）。
- X投稿の検索がメイン。バズっている投稿を優先的に拾う。
- 可能なら min_faves:500 等の検索オペレータでバズを拾う

やること（Hayatti式3段階リサーチ）:
1) まず「広く薄く」探索して、タイムラインの空気（論点のクラスター）を抽出:
   - {topic}に関連する広めのクエリを8個以上作ってX検索
   - 収集した投稿から「繰り返し出てくるキーワード/言い回し」を抽出し、3-5クラスターにまとめる
   - 各クラスターの代表ポストを2つずつ選ぶ

2) クラスターごとに深掘り:
   - 代表ポストのエンゲージメント指標（likes, RT, replies, views）を記録
   - 「なぜ伸びたか」仮説を各3つ
   - ここから作れるツイートネタ案（1-2行のフック案を3つ）

3) 全体の空気感まとめ:
   - 今この瞬間に伸びやすいテーマ/切り口
   - 避けるべきテーマ/表現
   - おすすめの投稿タイミング

出力形式（JSON）:
{{
  "clusters": [
    {{
      "name": "クラスター名",
      "keywords": ["キーワード1", "キーワード2"],
      "representative_posts": [
        {{
          "summary": "投稿の要旨（1-2行）",
          "engagement": {{"likes": 0, "rt": 0, "replies": 0}},
          "why_viral": ["仮説1", "仮説2", "仮説3"],
          "hook_ideas": ["フック案1", "フック案2", "フック案3"]
        }}
      ]
    }}
  ],
  "trending_themes": ["今伸びやすいテーマ1", "テーマ2", "テーマ3"],
  "avoid_themes": ["避けるべきテーマ/表現"],
  "best_timing": "おすすめの投稿タイミング",
  "overall_mood": "タイムラインの全体的な空気感（1-2文）"
}}
"""

        try:
            import httpx
            payload = {
                "model": "grok-3-fast",
                "input": prompt,
                "tools": [{"type": "x_search"}],
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "https://api.x.ai/v1/responses",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.xai_api_key}",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

            text = self._extract_grok_text(data)
            result = self._parse_json_response(text)
            log_success(f"Grok research completed for '{topic}'")
            return result

        except Exception as e:
            log_error(f"Grok research error: {e}")
            if self._gemini_model:
                return await self._research_with_gemini(topic, locale, audience, days)
            return self._get_mock_research(topic)

    async def _analyze_viral_with_grok(self, topic, count):
        """Grokでバズツイートパターン分析"""
        log_info(f"Grok x_search: analyzing viral patterns for '{topic}'")

        prompt = f"""日本語で回答して。

目的: 𝕏で「{topic}」に関してバズっている投稿のパターンを分析し、
     再現可能な投稿テンプレートを抽出する。

やること:
1) X検索で「{topic}」関連のバズ投稿を{count}件以上収集
   - min_faves:100 以上を優先
   - 日本語圏を優先
   - プレゼント企画・リンク宣伝のみのポストは除外

2) 各投稿について分析:
   - 構造（フック→本体→CTA）
   - 使われているフックのパターン
   - 心理トリガー（好奇心ギャップ/損失回避/社会的証明等）
   - エンゲージメント指標
   - なぜ伸びたか仮説3つ

3) 全体パターンを抽出:
   - 最も効果的なフックの型TOP5
   - 最もリプライが多い構造
   - 最もブックマークされる構造
   - 共通する文体の特徴
   - NG（伸びなかったパターン）

出力形式（JSON）:
{{
  "top_hooks": [
    {{"pattern": "フックの型", "example": "実例", "effectiveness": "効果説明"}}
  ],
  "viral_structures": [
    {{"name": "構造名", "template": "テンプレート", "best_for": "最適な用途"}}
  ],
  "psychology_triggers": ["効果的なトリガー"],
  "style_insights": ["文体の発見"],
  "ng_patterns": ["伸びなかったパターン"],
  "sample_posts": [
    {{
      "summary": "要旨",
      "engagement": {{"likes": 0, "rt": 0, "replies": 0}},
      "why_viral": ["仮説1", "仮説2", "仮説3"],
      "structure": "構造分析"
    }}
  ]
}}
"""

        try:
            import httpx
            payload = {
                "model": "grok-3-fast",
                "input": prompt,
                "tools": [{"type": "x_search"}],
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    "https://api.x.ai/v1/responses",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.xai_api_key}",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

            text = self._extract_grok_text(data)
            result = self._parse_json_response(text)
            log_success(f"Grok viral analysis completed for '{topic}'")
            return result

        except Exception as e:
            log_error(f"Grok viral analysis error: {e}")
            return self._get_mock_viral_analysis(topic)

    async def _research_with_gemini(self, topic, locale, audience, days):
        """GeminiフォールバックでWebリサーチ"""
        log_info(f"Gemini fallback: researching '{topic}'")

        prompt = f"""あなたは𝕏のトレンドリサーチの専門家です。

「{topic}」について、直近{days}日の𝕏の空気感を分析してください。

あなたの知識から以下を推測・分析してください:
1. このトピックに関する主要な論点クラスター（3-5個）
2. 各クラスターでバズりやすいフック案（各3つ）
3. 今伸びやすいテーマ/切り口
4. 避けるべきテーマ/表現

JSON形式のみで回答:
{{
  "clusters": [
    {{
      "name": "クラスター名",
      "keywords": ["キーワード1", "キーワード2"],
      "representative_posts": [
        {{
          "summary": "想定される投稿の要旨",
          "engagement": {{"likes": 0, "rt": 0, "replies": 0}},
          "why_viral": ["仮説1", "仮説2", "仮説3"],
          "hook_ideas": ["フック案1", "フック案2", "フック案3"]
        }}
      ]
    }}
  ],
  "trending_themes": ["テーマ1", "テーマ2"],
  "avoid_themes": ["避けるべきもの"],
  "best_timing": "推奨投稿タイミング",
  "overall_mood": "全体の空気感"
}}
"""

        try:
            response = await asyncio.to_thread(
                self._gemini_model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4096,
                    "response_mime_type": "application/json",
                }
            )
            if response and response.text:
                result = self._parse_json_response(response.text)
                log_success(f"Gemini research completed for '{topic}'")
                return result
        except Exception as e:
            log_error(f"Gemini research error: {e}")

        return self._get_mock_research(topic)

    async def _analyze_viral_with_gemini(self, topic, count):
        """Geminiフォールバックでバズ分析"""
        log_info(f"Gemini fallback: analyzing viral patterns for '{topic}'")

        prompt = f"""あなたは𝕏のバズ分析の専門家です。

「{topic}」に関して𝕏でバズりやすい投稿パターンを分析してください。
あなたの知識と経験から、再現可能なパターンを抽出してください。

JSON形式のみで回答:
{{
  "top_hooks": [
    {{"pattern": "フックの型", "example": "実例", "effectiveness": "効果説明"}}
  ],
  "viral_structures": [
    {{"name": "構造名", "template": "テンプレート", "best_for": "最適な用途"}}
  ],
  "psychology_triggers": ["効果的なトリガー"],
  "style_insights": ["文体の発見"],
  "ng_patterns": ["伸びなかったパターン"],
  "sample_posts": [
    {{
      "summary": "要旨",
      "engagement": {{"likes": 0, "rt": 0, "replies": 0}},
      "why_viral": ["仮説1", "仮説2", "仮説3"],
      "structure": "構造分析"
    }}
  ]
}}
"""

        try:
            response = await asyncio.to_thread(
                self._gemini_model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4096,
                    "response_mime_type": "application/json",
                }
            )
            if response and response.text:
                result = self._parse_json_response(response.text)
                log_success(f"Gemini viral analysis completed for '{topic}'")
                return result
        except Exception as e:
            log_error(f"Gemini viral analysis error: {e}")

        return self._get_mock_viral_analysis(topic)

    def _extract_grok_text(self, resp):
        """Grok APIレスポンスからテキストを抽出"""
        if isinstance(resp, dict):
            # v1/responses 形式
            output = resp.get("output", [])
            if isinstance(output, list):
                parts = []
                for item in output:
                    if not isinstance(item, dict):
                        continue
                    content = item.get("content", [])
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict):
                                t = c.get("text", "")
                                if t.strip():
                                    parts.append(t)
                if parts:
                    return "\n".join(parts).strip()

            # 他の形式にフォールバック
            for key in ["output_text", "text", "content"]:
                v = resp.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()

        return json.dumps(resp, indent=2)

    def _parse_json_response(self, text):
        """レスポンステキストからJSONをパース"""
        text = text.strip()
        # ```json ... ``` を除去
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # JSON文字列内の生改行をエスケープして再試行
            try:
                fixed = self._fix_json_newlines(text)
                return json.loads(fixed)
            except Exception:
                pass
            # { から } を切り出す
            try:
                start = text.index("{")
                end = text.rindex("}") + 1
                raw = text[start:end]
                fixed = self._fix_json_newlines(raw)
                return json.loads(fixed)
            except Exception:
                return {"raw_text": text[:500], "parse_error": True}

    @staticmethod
    def _fix_json_newlines(text):
        """JSON文字列値内の生改行を\\nに変換"""
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

    def _get_mock_research(self, topic):
        """モックリサーチ結果"""
        return {
            "clusters": [
                {
                    "name": f"{topic}の基礎",
                    "keywords": [topic, "入門", "始め方"],
                    "representative_posts": [
                        {
                            "summary": f"{topic}を始めて3ヶ月で成果が出た話",
                            "engagement": {"likes": 500, "rt": 80, "replies": 45},
                            "why_viral": [
                                "具体的な期間と成果がある",
                                "再現可能性を感じさせる",
                                "自分も始めたいと思わせる"
                            ],
                            "hook_ideas": [
                                f"{topic}を3ヶ月やった結果、",
                                f"9割が知らない{topic}の始め方",
                                f"{topic}で人生変わった話をする"
                            ]
                        }
                    ]
                }
            ],
            "trending_themes": [f"{topic}×AI", f"{topic}の失敗談", f"{topic}ロードマップ"],
            "avoid_themes": ["商材販売感", "断定的な収益保証"],
            "best_timing": "平日21時〜23時、休日12時〜14時",
            "overall_mood": f"{topic}への関心は高いが、具体的なノウハウと実体験が求められている"
        }

    def _get_mock_viral_analysis(self, topic):
        """モックバズ分析結果"""
        return {
            "top_hooks": [
                {"pattern": "感情爆発+数字", "example": f"やばい。{topic}で月50万稼いだ方法", "effectiveness": "最もリプライが多い"},
                {"pattern": "リスト型", "example": f"{topic}で使えるツール7選", "effectiveness": "ブックマーク率最高"},
                {"pattern": "ビフォーアフター", "example": f"1年前は〇〇だったのが今は{topic}で独立", "effectiveness": "共感リプ3倍"},
            ],
            "viral_structures": [
                {"name": "リスト型", "template": "フック\\n\\n・項目1\\n・項目2\\n...\\n\\nCTA", "best_for": "ブックマーク狙い"},
                {"name": "感情吐露型", "template": "感情語\\n\\n本音展開\\n\\n共感締め", "best_for": "リプライ狙い"},
            ],
            "psychology_triggers": ["好奇心ギャップ", "損失回避", "社会的証明"],
            "style_insights": ["口語体が圧倒的に強い", "1行15-25文字が読みやすい"],
            "ng_patterns": ["がちがちノウハウだけ", "セールス感", "改行なし長文"],
            "sample_posts": []
        }
