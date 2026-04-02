"""Gemini APIでクイズリニューアルについて相談"""
import json
import os
import urllib.request

API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAO0piaYe-SshhRmX_dFjkYewwjlHa87tU")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={API_KEY}"

prompt = """
あなたはUXデザイナー兼クイズ診断の専門家です。

「AI活用タイプ診断」というWebサービスのクイズ部分をリニューアルしたいです。
現在のサイト: https://ai-type-quiz.onrender.com

【現状の問題】
- 5問×5択で、選択肢が「考えて選ぶ」タイプで直感的に答えにくい
- ユーザーから「直感で選べない」というフィードバック

【リニューアル方針】
MBTI診断を参考に、以下の方式に変更予定:
- ステートメント（文章）に対して4段階で回答: はい / ちょっとはい / ちょっといいえ / いいえ
- 直感で即答できるカジュアルな文章
- 5タイプ（アシスタント/クリエイター/リサーチャー/パートナー/イノベーター）×2問 = 計10問

【現在の案（10問）】
1. やることリストを作るとスッキリする → assistant
2. SNSに載せる写真や文章にはこだわりたい → creator
3. 気になったらとことん調べないと気が済まない → researcher
4. 「聞き上手だね」って言われたことがある → partner
5. 新しいアプリが出たらとりあえず試してみる → innovator
6. 「めんどくさい」が口癖かもしれない → assistant
7. 「それ面白いね！」って言われると最高にうれしい → creator
8. Wikipediaのリンクをたどって気づいたら1時間経ってた、はあるある → researcher
9. 友達の悩み相談にのるのは好きな方だ → partner
10. 「これ、自分で作れそう」ってよく思う → innovator

【追加アイデア】
- 回答内容に応じて、診断結果ページで「あなた向けのおすすめプロンプト」をGemini APIで自動生成すると楽しいかも
- タイプは変わらないけど、回答傾向に合わせたパーソナライズされたプロンプト

【相談したいこと】
1. 上記10問の質の評価（直感で答えやすいか、タイプ判別に有効か）
2. 改善案があれば差し替え候補を提案して
3. 10問で十分？多い？少ない？
4. 回答に応じたプロンプト自動生成について:
   - やるべき？やらないべき？
   - やる場合、Gemini API呼び出しは結果表示時に1回だけ？
   - レイテンシが気になるけどUX的にどう工夫する？
5. その他、このリニューアルで見落としてるポイントがあれば教えて

日本語で、忖度なしで回答してください。箇条書きで簡潔に。
"""

data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})

with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read())
    text = result["candidates"][0]["content"]["parts"][0]["text"]
    print(text)
