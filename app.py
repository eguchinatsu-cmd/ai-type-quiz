"""AI活用タイプ診断 - あなたと相性最高のAIは？"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).parent

app = FastAPI(title="AI活用タイプ診断")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

import os
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "")

# --- 診断データ ---
QUESTIONS = [
    {
        "id": 1,
        "text": "AIに一番期待することは？",
        "choices": [
            {"label": "A", "text": "めんどくさい作業を自動化して時間を節約したい", "scores": {"assistant": 3, "creator": 0, "researcher": 0, "partner": 0, "innovator": 1}},
            {"label": "B", "text": "新しいアイデアや企画の壁打ち相手になってほしい", "scores": {"assistant": 0, "creator": 3, "researcher": 0, "partner": 1, "innovator": 0}},
            {"label": "C", "text": "知りたい情報を素早く正確にまとめてほしい", "scores": {"assistant": 1, "creator": 0, "researcher": 3, "partner": 0, "innovator": 0}},
            {"label": "D", "text": "複雑な問題解決やアドバイスがほしい", "scores": {"assistant": 0, "creator": 0, "researcher": 1, "partner": 3, "innovator": 0}},
            {"label": "E", "text": "文章・画像・コードなど、一緒にモノづくりしたい", "scores": {"assistant": 0, "creator": 1, "researcher": 0, "partner": 0, "innovator": 3}},
        ],
    },
    {
        "id": 2,
        "text": "AIを使う上で一番大事にしたいことは？",
        "choices": [
            {"label": "A", "text": "スピードと正確さ。とにかく速く、ミスなく", "scores": {"assistant": 3, "creator": 0, "researcher": 1, "partner": 0, "innovator": 0}},
            {"label": "B", "text": "柔軟な発想とクリエイティブな刺激", "scores": {"assistant": 0, "creator": 3, "researcher": 0, "partner": 1, "innovator": 0}},
            {"label": "C", "text": "信頼できる情報と深い分析力", "scores": {"assistant": 0, "creator": 0, "researcher": 3, "partner": 0, "innovator": 1}},
            {"label": "D", "text": "自分の意図をちゃんと理解してくれること", "scores": {"assistant": 1, "creator": 0, "researcher": 0, "partner": 3, "innovator": 0}},
            {"label": "E", "text": "最新技術やトレンドへの対応力", "scores": {"assistant": 0, "creator": 1, "researcher": 0, "partner": 0, "innovator": 3}},
        ],
    },
    {
        "id": 3,
        "text": "AIとの理想の関係は？",
        "choices": [
            {"label": "A", "text": "優秀な秘書。指示すれば完璧にこなしてくれる", "scores": {"assistant": 3, "creator": 0, "researcher": 0, "partner": 0, "innovator": 1}},
            {"label": "B", "text": "刺激的な共同制作者。一緒に新しいものを作る", "scores": {"assistant": 0, "creator": 3, "researcher": 0, "partner": 1, "innovator": 0}},
            {"label": "C", "text": "頼れる専門家。疑問に答えて解決策を出してくれる", "scores": {"assistant": 0, "creator": 0, "researcher": 3, "partner": 0, "innovator": 0}},
            {"label": "D", "text": "親しい友人。気軽に話せて的確なアドバイスをくれる", "scores": {"assistant": 0, "creator": 0, "researcher": 0, "partner": 3, "innovator": 0}},
            {"label": "E", "text": "最強の相棒。どんな困難も一緒に乗り越える", "scores": {"assistant": 0, "creator": 1, "researcher": 0, "partner": 0, "innovator": 3}},
        ],
    },
    {
        "id": 4,
        "text": "AIをどんな場面で使いたい？",
        "choices": [
            {"label": "A", "text": "メール作成、資料の要約、議事録作成", "scores": {"assistant": 3, "creator": 0, "researcher": 1, "partner": 0, "innovator": 0}},
            {"label": "B", "text": "ブログのネタ出し、キャッチコピー、企画書づくり", "scores": {"assistant": 0, "creator": 3, "researcher": 0, "partner": 0, "innovator": 1}},
            {"label": "C", "text": "市場調査、競合分析、論文の要約、勉強", "scores": {"assistant": 0, "creator": 0, "researcher": 3, "partner": 0, "innovator": 0}},
            {"label": "D", "text": "プレゼン練習、ブレスト、悩み相談", "scores": {"assistant": 0, "creator": 0, "researcher": 0, "partner": 3, "innovator": 0}},
            {"label": "E", "text": "プログラミング、デザイン、動画編集の補助", "scores": {"assistant": 0, "creator": 1, "researcher": 0, "partner": 0, "innovator": 3}},
        ],
    },
    {
        "id": 5,
        "text": "AIとの会話スタイルは？",
        "choices": [
            {"label": "A", "text": "指示は明確に、簡潔に。無駄なく効率的に", "scores": {"assistant": 3, "creator": 0, "researcher": 0, "partner": 0, "innovator": 1}},
            {"label": "B", "text": "ふわっとした問いかけから対話でアイデアを広げたい", "scores": {"assistant": 0, "creator": 3, "researcher": 0, "partner": 1, "innovator": 0}},
            {"label": "C", "text": "色んな角度から質問して、深く掘り下げたい", "scores": {"assistant": 0, "creator": 0, "researcher": 3, "partner": 0, "innovator": 0}},
            {"label": "D", "text": "丁寧に話しかけて、いい関係を築きたい", "scores": {"assistant": 0, "creator": 0, "researcher": 0, "partner": 3, "innovator": 0}},
            {"label": "E", "text": "AIの限界を試すような無茶振りもする", "scores": {"assistant": 0, "creator": 0, "researcher": 1, "partner": 0, "innovator": 3}},
        ],
    },
]

RESULTS = {
    "assistant": {
        "id": "assistant",
        "name": "効率化の達人！「AIアシスタント」タイプ",
        "emoji": "briefcase",
        "color": "#2563eb",
        "color_light": "#dbeafe",
        "description": "あなたは日々の業務を効率化し、時間を最大限に活用したい実用主義者。AIを優秀な秘書として使いこなせば、ルーティン作業から解放されて本当に大事なことに集中できます！",
        "recommended_ai": [
            {"name": "ChatGPT Plus", "desc": "メール・要約・議事録、何でもこなす万能選手", "url": "https://chatgpt.com/"},
            {"name": "Microsoft Copilot", "desc": "Office製品と連携して資料作成が爆速に", "url": "https://copilot.microsoft.com/"},
            {"name": "Gemini Advanced", "desc": "テキスト・画像・動画もまとめて処理", "url": "https://gemini.google.com/"},
        ],
        "prompts": [
            {"title": "メール作成", "text": "以下の内容でビジネスメールを作成してください。\n件名：○○の件\n宛先：取引先の担当者\n内容：納期を1週間延長してほしい\nトーン：丁寧だけど簡潔に"},
            {"title": "議事録の要約", "text": "以下の議事録を300字以内で要約し、決定事項とTODOを箇条書きでまとめてください。\n[ここに議事録を貼り付け]"},
            {"title": "タスク整理", "text": "以下のタスクを優先度（高・中・低）に分類し、今日やるべきことを3つ選んでください。\n[タスクリストを貼り付け]"},
        ],
    },
    "creator": {
        "id": "creator",
        "name": "アイデアの泉！「AIクリエイター」タイプ",
        "emoji": "art",
        "color": "#7c3aed",
        "color_light": "#ede9fe",
        "description": "あなたは常に新しいものを生み出す情熱を持つクリエイター。AIを単なるツールではなく、創造的なパートナーとして活用すれば、アイデアも表現も無限に広がります！",
        "recommended_ai": [
            {"name": "Claude 3", "desc": "長文の理解力が抜群。物語や企画書の骨子作りに最適", "url": "https://claude.ai/"},
            {"name": "ChatGPT Plus", "desc": "アイデア出しからコンテンツ生成まで幅広く対応", "url": "https://chatgpt.com/"},
            {"name": "Gemini Advanced", "desc": "画像生成AIとの連携で視覚的なアウトプットも", "url": "https://gemini.google.com/"},
        ],
        "prompts": [
            {"title": "アイデア出し", "text": "「在宅ワーカー向けの新しいサブスクサービス」のアイデアを10個出してください。ありきたりでないユニークなものをお願いします。"},
            {"title": "キャッチコピー", "text": "以下の商品のキャッチコピーを5つ考えてください。\n商品：AIが自動で家計簿をつけてくれるアプリ\nターゲット：20代の一人暮らし\nトーン：カジュアルで親しみやすい"},
            {"title": "ブログ記事の構成", "text": "「AI初心者が最初にやるべきこと5選」というブログ記事の構成案を作ってください。各見出しと、その見出しで書く内容の概要も含めて。"},
        ],
    },
    "researcher": {
        "id": "researcher",
        "name": "知識の探求者！「AIリサーチャー」タイプ",
        "emoji": "mag",
        "color": "#059669",
        "color_light": "#d1fae5",
        "description": "あなたは知的好奇心が旺盛で、常に新しい知識を求める探求者。AIを頼れる専門家として活用すれば、膨大な情報から必要なものを瞬時に見つけ出し、深く分析できます！",
        "recommended_ai": [
            {"name": "Perplexity AI", "desc": "Web検索+情報源表示で信頼性の高いリサーチに最適", "url": "https://www.perplexity.ai/"},
            {"name": "Gemini Advanced", "desc": "最新情報へのアクセスと詳細な回答が得意", "url": "https://gemini.google.com/"},
            {"name": "ChatGPT Plus (Browse)", "desc": "Web検索機能で幅広い情報を収集・整理", "url": "https://chatgpt.com/"},
        ],
        "prompts": [
            {"title": "市場調査", "text": "日本の「AIチャットボット市場」について、最新のトレンド、主要プレイヤー、今後の成長予測をまとめてください。情報源も明記してください。"},
            {"title": "用語解説", "text": "「プロンプトエンジニアリング」について、AI初心者にもわかるように500字以内で解説してください。具体例も2つ含めて。"},
            {"title": "比較分析", "text": "ChatGPT、Gemini、Claudeの3つのAIを比較してください。それぞれの得意分野、苦手分野、価格、おすすめの使い方を表形式でまとめて。"},
        ],
    },
    "partner": {
        "id": "partner",
        "name": "心の通訳者！「AIパートナー」タイプ",
        "emoji": "handshake",
        "color": "#d97706",
        "color_light": "#fef3c7",
        "description": "あなたは人との対話を大切にし、AIにも人間らしいコミュニケーションを求めます。AIを親しい相談相手として活用すれば、考えの整理やスキルアップの強力な味方になります！",
        "recommended_ai": [
            {"name": "Claude 3", "desc": "自然で人間らしい対話が得意。共感的な応答が魅力", "url": "https://claude.ai/"},
            {"name": "ChatGPT Plus", "desc": "ロールプレイ機能が充実。練習相手に最適", "url": "https://chatgpt.com/"},
            {"name": "Pi (Personal AI)", "desc": "パーソナライズされた対話で寄り添ってくれる", "url": "https://pi.ai/"},
        ],
        "prompts": [
            {"title": "プレゼン練習", "text": "あなたは厳しめのクライアントです。私がプレゼンをするので、鋭い質問や指摘をしてください。プレゼン内容：[ここに概要を書く]"},
            {"title": "壁打ち相談", "text": "転職すべきか悩んでいます。今の仕事は安定しているけど成長を感じない。でも転職は不安。私の話を聞いて、考えを整理する手伝いをしてください。一方的にアドバイスするのではなく、質問しながら進めて。"},
            {"title": "英会話練習", "text": "英語の日常会話を練習したいです。あなたはカフェの店員です。私が注文するので、自然な英語で対応してください。間違いがあったら優しく教えて。"},
        ],
    },
    "innovator": {
        "id": "innovator",
        "name": "未来の開拓者！「AIイノベーター」タイプ",
        "emoji": "rocket",
        "color": "#dc2626",
        "color_light": "#fee2e2",
        "description": "あなたは最先端技術に目を向け、AIの未知の可能性を探求する真のイノベーター。既存の枠にとらわれず、AIの限界に挑戦し、新しい活用法を生み出すパイオニアです！",
        "recommended_ai": [
            {"name": "全てのAIを使い分け", "desc": "ChatGPT、Gemini、Claude、Perplexityを場面で使い分けるのが最強", "url": "https://chatgpt.com/"},
            {"name": "Claude Code / Cursor", "desc": "AIでコーディング。アプリやツールを自分で作れる", "url": "https://www.cursor.com/"},
            {"name": "Midjourney / Suno", "desc": "画像や音楽もAIで生成。クリエイティブの限界を超える", "url": "https://www.midjourney.com/"},
        ],
        "prompts": [
            {"title": "ビジネスモデル考案", "text": "AI技術を活用した「ペット業界」の新しいビジネスモデルを5つ提案してください。実現可能性、収益モデル、ターゲット顧客も含めて。"},
            {"title": "コード生成", "text": "Pythonで、Webサイトの更新を自動検知してSlackに通知するスクリプトを書いてください。ライブラリの説明とコメント付きで。"},
            {"title": "未来予測", "text": "2030年までにAIが最も大きく変える業界TOP5を予測し、それぞれどんな変化が起きるか具体的に説明してください。"},
        ],
    },
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(name="index.html", request=request, context={"questions": QUESTIONS, "ga_id": GA_MEASUREMENT_ID})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse(name="privacy.html", request=request, context={"ga_id": GA_MEASUREMENT_ID})


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse(name="terms.html", request=request, context={"ga_id": GA_MEASUREMENT_ID})


@app.get("/result/{type_id}", response_class=HTMLResponse)
async def result(request: Request, type_id: str):
    result_data = RESULTS.get(type_id)
    if not result_data:
        result_data = RESULTS["assistant"]
    return templates.TemplateResponse(name="result.html", request=request, context={"result": result_data, "ga_id": GA_MEASUREMENT_ID})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
