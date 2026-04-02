"""
tweet_headless.py - ヘッドレスPlaywrightでX (Twitter) にツイートを投稿する

使い方:
    python tweet_headless.py "投稿したいテキスト"
    python tweet_headless.py "投稿したいテキスト" --visible   # ブラウザ表示モード（デバッグ用）

事前準備:
    pip install playwright
    playwright install chromium

認証: x_cookies.json にXのセッションCookieを保存（Playwright MCPから取得）
Xのツイート入力欄はReact (Draft.js) の contenteditable div なので、
keyboard.type() でキーストローク送信する方式を採用。
"""

import argparse
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).parent
COOKIES_FILE = SCRIPT_DIR / "x_cookies.json"
X_HOME = "https://x.com/home"
X_COMPOSE = "https://x.com/compose/post"


def load_cookies():
    """x_cookies.json からCookieを読み込む"""
    if not COOKIES_FILE.exists():
        print(f"エラー: {COOKIES_FILE} が見つかりません。")
        print("Playwright MCPでXにログイン後、cookieを保存してください。")
        sys.exit(1)
    with open(COOKIES_FILE) as f:
        return json.load(f)


def launch_browser(pw, headless=True):
    """ブラウザを起動してCookieを注入"""
    browser = pw.chromium.launch(
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="ja-JP",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    )
    cookies = load_cookies()
    context.add_cookies(cookies)
    return browser, context


def is_logged_in(page):
    """Xにログイン済みか確認"""
    page.goto(X_HOME, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    url = page.url
    if "/login" in url or "/i/flow/login" in url:
        return False
    try:
        page.wait_for_selector('[data-testid="tweetTextarea_0"], [data-testid="SideNav_NewTweet_Button"]', timeout=10000)
        return True
    except Exception:
        return False


def post_tweet(text, headless=True):
    """ヘッドレスでツイートを投稿する"""
    if len(text) > 280:
        print(f"警告: テキストが280文字を超えています（{len(text)}文字）")

    with sync_playwright() as pw:
        browser, context = launch_browser(pw, headless=headless)
        page = context.new_page()

        # ログイン確認
        if not is_logged_in(page):
            print("エラー: Xにログインできません。Cookieが期限切れの可能性があります。")
            print("Playwright MCPでXにログインし、cookieを再取得してください。")
            browser.close()
            sys.exit(1)

        print("Xにログイン確認OK")

        # ツイート作成ページに直接移動
        page.goto(X_COMPOSE, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # ツイート入力欄を探す（Draft.js の contenteditable div）
        editor_selector = '[data-testid="tweetTextarea_0"]'
        try:
            page.wait_for_selector(editor_selector, timeout=10000)
        except Exception:
            # フォールバック: ホームのツイートボックスを使う
            print("compose画面が開けません。ホームから投稿を試みます...")
            page.goto(X_HOME, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            try:
                page.wait_for_selector(editor_selector, timeout=10000)
            except Exception:
                print("エラー: ツイート入力欄が見つかりません。")
                browser.close()
                sys.exit(1)

        # 入力欄をクリックしてフォーカス
        page.click(editor_selector)
        time.sleep(0.5)

        # keyboard.type() でテキスト入力（React仮想DOMに対応）
        page.keyboard.type(text, delay=30)
        time.sleep(1)

        # 投稿ボタンをクリック
        post_button = '[data-testid="tweetButton"], [data-testid="tweetButtonInline"]'
        try:
            page.wait_for_selector(post_button, timeout=5000)
            page.click(post_button)
            print("投稿ボタンをクリック...")
            time.sleep(3)
            print("投稿成功！ @china_keiba")
            try:
                print(f"テキスト: {text[:80]}{'...' if len(text) > 80 else ''}")
            except UnicodeEncodeError:
                print(f"テキスト: {text[:80].encode('ascii', 'replace').decode()}{'...' if len(text) > 80 else ''}")
        except Exception as e:
            print(f"エラー: 投稿ボタンが見つかりません: {e}")
            browser.close()
            sys.exit(1)

        browser.close()


def main():
    parser = argparse.ArgumentParser(description="ヘッドレスPlaywrightでXにツイートを投稿")
    parser.add_argument("text", nargs="?", help="投稿するテキスト")
    parser.add_argument("--visible", action="store_true", help="ブラウザを表示する（デバッグ用）")
    args = parser.parse_args()

    if not args.text:
        parser.print_help()
        sys.exit(1)

    headless = not args.visible
    post_tweet(args.text, headless=headless)


if __name__ == "__main__":
    main()
