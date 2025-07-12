"""
このファイルの概要:
Playwrightを使ってAkuma（akuma.ai）にアクセスする際の共通ユーティリティ関数をまとめたモジュールです。
認証情報の引き継ぎやヘッドレスモードの切り替えなど、ブラウザ自動化の初期化処理を簡単にします。
"""

from playwright.sync_api import sync_playwright

def get_playwright_context(state_file=None, headless=True):
    """
    Playwrightのcontext（ブラウザ操作用の環境）を取得します。
    Args:
        state_file: 認証情報のパス。指定しない場合は未ログイン状態。
        headless: ヘッドレスモード（画面を表示しない）で起動するかどうか。
    Returns:
        p: Playwrightのインスタンス
        browser: ブラウザのインスタンス
        context: ブラウザの操作用コンテキスト
    """
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=headless)
    if state_file:
        context = browser.new_context(storage_state=state_file)
    else:
        context = browser.new_context()
    return p, browser, context
