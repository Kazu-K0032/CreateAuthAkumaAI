"""
このファイルの概要:
Akuma（akuma.ai）のジョブ詳細ページから画像や説明文（プロンプト）を自動取得するためのスクリプトです。
事前にstate.jsonを生成しておくことで、認証状態を引き継いでデータ取得が可能です。
"""

import os
import json
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests
from lib.get_playwright_context import get_playwright_context
from urllib.parse import urlparse, parse_qs, urljoin, unquote

load_dotenv()

def fetch_image_url_with_saved_state(job_url: str, state_file: str) -> str:
    """
    （非推奨）Akumaのジョブページから__NEXT_DATA__を使って画像URLを取得します。
    Args:
        job_url: 取得対象のAkumaジョブページのURL
        state_file: 認証情報（state.json）のパス
    Returns:
        画像のURL（文字列）
    Note:
        現在のAkumaの仕様では__NEXT_DATA__が存在しない場合があるため、
        fetch_akuma_job_infoの利用を推奨します。
    """
    with sync_playwright() as p:
        # ① 認証情報を引き継いでブラウザ起動
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=state_file)
        page = context.new_page()

        # ② ジョブページへ移動
        print(f"📄 ジョブページを開く: {job_url}")
        page.goto(job_url, wait_until="networkidle")
        time.sleep(2)

        # ③ HTML 取得→__NEXT_DATA__ 抽出
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            raise RuntimeError("__NEXT_DATA__ が見つからない")

        data = json.loads(script.string)
        props = data["props"]["pageProps"]
        image_url = props.get("image", {}).get("url")
        if not image_url:
            raise RuntimeError("画像 URL が取得できなかった")

        browser.close()
        return image_url

def fetch_akuma_job_info(job_url, output_dir=None, state_file=None):
    """
    Akumaのジョブ詳細ページから画像と説明文を取得し、画像を保存します。
    Args:
        job_url: 取得対象のAkumaジョブページのURL
        output_dir: 画像保存先ディレクトリ（Noneの場合はデフォルト値を使用）
        state_file: 認証情報（state.json）のパス
    Returns:
        なし
    """
    from constant import OUTPUT_DIR
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    p, browser, context = get_playwright_context(state_file=state_file, headless=True)
    page = context.new_page()
    page.goto(job_url, wait_until="networkidle")

    # 画像URL取得
    img_selector = 'main img'
    page.wait_for_selector(img_selector)
    img_url = page.get_attribute(img_selector, "src")
    if img_url.startswith("/_next/image"):
        img_url_full = "https://akuma.ai" + img_url
        parsed = urlparse(img_url_full)
        qs = parse_qs(parsed.query)
        if "url" in qs:
            img_url = unquote(qs["url"][0])
        else:
            img_url = urljoin("https://akuma.ai", img_url)
    elif img_url.startswith("/"):
        img_url = urljoin("https://akuma.ai", img_url)

    # 説明文取得
    desc_selector = 'main .text-sm'
    page.wait_for_selector(desc_selector)
    description = page.inner_text(desc_selector).strip()

    # descriptionが空の場合、main内の全テキストから抽出を試みる
    if not description:
        main_text = page.inner_text("main")
        lines = [line.strip() for line in main_text.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            if line == "Publish" and i + 1 < len(lines):
                description = lines[i + 1]
                break

    print("画像URL:", img_url)
    print("説明文:", description)

    # 画像ダウンロード
    if img_url:
        os.makedirs(output_dir, exist_ok=True)
        img_data = requests.get(img_url).content
        
        # ユニークなファイル名を生成
        from datetime import datetime
        import re
        
        # URLからファイル拡張子を取得
        url_path = urlparse(img_url).path
        file_extension = os.path.splitext(url_path)[1]
        if not file_extension:
            file_extension = ".png"  # デフォルト拡張子
        
        # タイムスタンプベースのファイル名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # URLからジョブIDを抽出（オプション）
        job_id = ""
        if "jobs/" in job_url:
            job_match = re.search(r'jobs/([^/?]+)', job_url)
            if job_match:
                job_id = f"_{job_match.group(1)[:8]}"  # 最初の8文字
        
        filename = f"akuma_image{job_id}_{timestamp}{file_extension}"
        img_path = os.path.join(output_dir, filename)
        
        with open(img_path, "wb") as f:
            f.write(img_data)
        print(f"画像を保存しました: {img_path}")

    browser.close()
    p.stop()

if __name__ == "__main__":
    # 事前に手動ログインして state.json を生成しておくこと
    # source venv/bin/activate
    # python scraping.py
    from constant import AUTH_FILE_NAME, OUTPUT_DIR
    STATE_FILE = os.path.join(os.path.dirname(__file__), AUTH_FILE_NAME)
    fetch_akuma_job_info(os.getenv("AKUMA_JOB_URL"), state_file=STATE_FILE)
