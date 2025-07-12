"""
このファイルの概要:
Akuma（akuma.ai）に手動でログインし、認証情報（state.json）を生成するためのスクリプトです。
生成したstate.jsonは、他の自動化スクリプトで認証状態を引き継ぐために利用します。
"""

import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

def generate_state_json(state_path: str):
    """
    Akumaに手動でログインし、認証情報（state.json）を生成します。
    Args:
        state_path: 保存先のstate.jsonファイルパス
    Returns:
        なし
    """
    with sync_playwright() as p:
        # 実インストール版 Chrome を指定して起動（Google にブロックされにくくする）
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",  # インストール済みの Chrome を使う
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-infobars",
                "--disable-extensions",
                "--start-maximized",
                "--window-size=1280,720"
            ]
        )

        # 最新ブラウザの User-Agent を指定（自動化検出の抑止）
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )

        # state.jsonが存在する場合のみstorage_stateを指定
        if os.path.exists(state_path):
            context = browser.new_context(storage_state=state_path, user_agent=user_agent)
        else:
            context = browser.new_context(user_agent=user_agent)

        page = context.new_page()

        # Akuma トップページへ移動し Login ボタンをクリック
        print("🌐 Akuma トップページを開いています...")
        page.goto("https://akuma.ai/", wait_until="networkidle")

        # Googleログインボタンをクリック
        print("🔐 Googleログインボタンを探しています...")
        page.click('button:has-text("Continue with Google")')

        # 手動でログインを完了するまで待機
        print("\n📝 手動でGoogleログインを完了してください...")
        print("ログインが完了したら、このメッセージが表示されたままにしてください。")
        print("（ブラウザは閉じないでください）")

        # ユーザーが手動でログインを完了するまで待機
        input("\n✅ ログインが完了したら Enter キーを押してください: ")

        # 認証状態を state.json に保存
        context.storage_state(path=state_path)
        print(f"\n✅ 認証状態を保存しました: {state_path}")

        browser.close()

if __name__ == "__main__":
    # source venv/bin/activate
    # python generate_state_json.py
    from constant import AUTH_FILE_NAME
    STATE_FILE = os.path.join(os.path.dirname(__file__), AUTH_FILE_NAME)
    generate_state_json(STATE_FILE)
