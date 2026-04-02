"""
tweet_post.py - X (Twitter) にツイートを投稿するスクリプト

使い方:
    python tweet_post.py "投稿したいテキスト"

環境変数（必須）:
    TWITTER_API_KEY          - API Key (Consumer Key)
    TWITTER_API_SECRET       - API Secret (Consumer Secret)
    TWITTER_ACCESS_TOKEN     - Access Token
    TWITTER_ACCESS_TOKEN_SECRET - Access Token Secret

事前準備:
    pip install tweepy
"""

import os
import sys
import tweepy


def get_client():
    """環境変数からAPIキーを読み込み、tweepy Clientを作成する"""
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    # 必須の環境変数チェック
    missing = []
    if not api_key:
        missing.append("TWITTER_API_KEY")
    if not api_secret:
        missing.append("TWITTER_API_SECRET")
    if not access_token:
        missing.append("TWITTER_ACCESS_TOKEN")
    if not access_token_secret:
        missing.append("TWITTER_ACCESS_TOKEN_SECRET")

    if missing:
        print(f"エラー: 以下の環境変数が設定されていません: {', '.join(missing)}")
        print()
        print("設定方法（Windows PowerShell）:")
        for var in missing:
            print(f'  $env:{var} = "your_value_here"')
        print()
        print("設定方法（bash）:")
        for var in missing:
            print(f'  export {var}="your_value_here"')
        sys.exit(1)

    # tweepy Client (v2 API) を作成
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    return client


def post_tweet(text):
    """ツイートを投稿する"""
    if len(text) > 280:
        print(f"警告: テキストが280文字を超えています（{len(text)}文字）。投稿できない可能性があります。")

    client = get_client()

    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"投稿成功!")
        print(f"Tweet ID: {tweet_id}")
        print(f"URL: https://x.com/china_keiba/status/{tweet_id}")
        return tweet_id
    except tweepy.TweepyException as e:
        print(f"投稿エラー: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("使い方: python tweet_post.py \"投稿したいテキスト\"")
        print()
        print("例: python tweet_post.py \"こんにちは！テスト投稿です。\"")
        sys.exit(1)

    tweet_text = sys.argv[1]
    post_tweet(tweet_text)


if __name__ == "__main__":
    main()
