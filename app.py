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
    {"id": 1, "text": "予定を立てるときは、分刻みでバッチリ決めたい", "primary": "assistant", "reverse": False},
    {"id": 2, "text": "写真の加工やリール作成は、つい時間を忘れてこだわっちゃう", "primary": "creator", "reverse": False},
    {"id": 3, "text": "話題のスポットでも、行列に並んでまで行くのは正直しんどい", "primary": "innovator", "reverse": True},
    {"id": 4, "text": "気になるコスメやお店は、口コミを何サイトも見比べないと気が済まない", "primary": "researcher", "reverse": False},
    {"id": 5, "text": "人の話を聞くときは、解決策よりも「共感」が大事だと思う", "primary": "partner", "reverse": False},
    {"id": 6, "text": "マニュアルや説明書を読むより、とりあえず触って覚えたい派だ", "primary": "assistant", "reverse": True},
    {"id": 7, "text": "周りの人が「良い」と言っているものより、誰も知らない新しいものを見つけたい", "primary": "innovator", "reverse": False},
    {"id": 8, "text": "完成されたものを見るより「どうやって作られているか」の裏側が気になる", "primary": "researcher", "reverse": False},
    {"id": 9, "text": "映画やドラマを観て、登場人物に感情移入して泣くことはあまりない", "primary": "partner", "reverse": True},
    {"id": 10, "text": "自分の考えを言葉にするより、絵や図、写真で見せる方が得意だ", "primary": "creator", "reverse": False},
]

# 4段階の回答選択肢と配点
ANSWER_OPTIONS = [
    {"label": "あてはまる", "score": 3},
    {"label": "ややあてはまる", "score": 2},
    {"label": "あまりあてはまらない", "score": 1},
    {"label": "あてはまらない", "score": 0},
]

# ジャンル選択肢（9〜12個、チップ形式で表示）
GENRES = [
    "記事・ブログ作成", "SNS運用", "収益化・副業",
    "画像・デザイン生成", "動画編集", "プログラミング",
    "語学・翻訳", "ビジネス効率化", "データ分析",
    "ゲーム・アプリ開発", "音楽・作曲", "勉強・資格対策",
]

# タイプ別プロンプトテンプレート（{genre}がジャンルに置換される）
PROMPT_TEMPLATES = {
    "assistant": {
        "persona": "最強の右腕AI秘書",
        "template": "あなたはプロの{genre}アシスタントです。以下のタスクを「手順書レベル」で具体的に分解してください。\n\n■ タスク: {genre}を始めたいが、何から手をつければいいかわからない\n■ 条件: 初心者向け、1日30分の作業量、1週間で成果が出るプラン\n■ 出力形式: Day1〜Day7のステップ + 各日の具体的アクション",
    },
    "creator": {
        "persona": "天才クリエイティブディレクター",
        "template": "あなたは{genre}の天才クリエイティブディレクターです。以下のテーマで「思わずシェアしたくなる」コンテンツのアイデアを5つ出してください。\n\n■ テーマ: {genre}\n■ ターゲット: 20〜30代、SNSをよく使う層\n■ 条件: ありきたりNG、「え、こんな切り口！？」と思わせるもの\n■ 各アイデアに「バズるポイント」も一言添えて",
    },
    "researcher": {
        "persona": "鋭い洞察力のAI探偵",
        "template": "あなたは鋭い洞察力を持つAI探偵です。{genre}において、多くの人が見落としている「隠れた真実」を3つ発見してください。\n\n■ 分析対象: {genre}の最新トレンドと落とし穴\n■ 条件: データや根拠を示しつつ、初心者にもわかる言葉で\n■ 出力: 各発見に「だから○○すべき」という具体的アクションも添えて",
    },
    "partner": {
        "persona": "あなた専属のAIコーチ",
        "template": "あなたは優しくも的確な{genre}の専属コーチです。私は{genre}に興味はあるけど、なかなか一歩が踏み出せません。\n\n■ まず私の不安を聞いて、共感してください\n■ その上で「最初の一歩」を3つ提案してください\n■ 各提案に「これならできそう！」と思える難易度の説明を添えて\n■ 最後に背中を押すような一言をお願いします",
    },
    "innovator": {
        "persona": "常識を壊すAIハッカー",
        "template": "あなたは常識を壊すAIハッカーです。{genre}の「当たり前」を破壊する革新的な方法を3つ提案してください。\n\n■ テーマ: {genre}をAIで10倍効率化する\n■ 条件: 既存ツールの組み合わせで今すぐ実現可能なもの\n■ 各提案に: 使うツール名 + 具体的な手順 + 予想される効果\n■ 最後に「これを知ってるのは上位1%だけ」的な裏技を1つ",
    },
}

RESULTS = {
    "assistant": {
        "id": "assistant",
        "name": "最強の右腕！「AI事務総長」タイプ",
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
        "name": "発想が止まらない！「AIアーティスト」タイプ",
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
        "name": "沼の住人！「AI探偵」タイプ",
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
        "name": "心の翻訳家！「AI相談役」タイプ",
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
        "name": "常識ぶっ壊し系！「AIハッカー」タイプ",
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
    return templates.TemplateResponse(name="index.html", request=request, context={"questions": QUESTIONS, "answer_options": ANSWER_OPTIONS, "genres": GENRES, "ga_id": GA_MEASUREMENT_ID})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse(name="privacy.html", request=request, context={"ga_id": GA_MEASUREMENT_ID})


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse(name="terms.html", request=request, context={"ga_id": GA_MEASUREMENT_ID})


@app.get("/result/{type_id}", response_class=HTMLResponse)
async def result(request: Request, type_id: str, genres: str = ""):
    result_data = RESULTS.get(type_id)
    if not result_data:
        result_data = RESULTS["assistant"]

    # ジャンルからパーソナライズプロンプト生成
    selected_genres = [g for g in genres.split(",") if g] if genres else []
    tmpl = PROMPT_TEMPLATES.get(type_id, PROMPT_TEMPLATES["assistant"])
    personalized_prompts = []
    for genre in selected_genres[:3]:
        personalized_prompts.append({
            "genre": genre,
            "persona": tmpl["persona"],
            "text": tmpl["template"].replace("{genre}", genre),
        })

    return templates.TemplateResponse(name="result.html", request=request, context={
        "result": result_data,
        "personalized_prompts": personalized_prompts,
        "ga_id": GA_MEASUREMENT_ID,
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
