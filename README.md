# CreateAuthAkumaAI

akuma.ai の認証ファイルを作成するリポジトリ

## 前提条件

### Python3 のインストール

#### Ubuntu/Debian (WSL2 含む)

```bash
# システムパッケージの更新
sudo apt update

# Python3とpip3のインストール
sudo apt install python3 python3-pip python3-venv

# バージョン確認
python3 --version
pip3 --version
```

#### macOS

```bash
# Homebrewを使用
brew install python3

# または公式インストーラーを使用
# https://www.python.org/downloads/macos/
```

#### Windows

```bash
# 公式インストーラーを使用
# https://www.python.org/downloads/windows/
# インストール時に「Add Python to PATH」にチェックを入れる
```

### 依存関係の確認

```bash
# Python3が利用可能か確認
python3 --version

# pip3が利用可能か確認
pip3 --version

# venvモジュールが利用可能か確認
python3 -m venv --help
```

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd create-auth-akumaAI
```

### 2. 仮想環境の作成

```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境をアクティベート
# Ubuntu/Debian/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
# pipを最新版にアップグレード
pip install --upgrade pip

# requirements.txtからすべてのパッケージをインストール
pip install -r requirements.txt
```

### 4. Playwright のセットアップ

```bash
# Playwrightのブラウザをインストール
playwright install chromium
```

### 5. 環境変数の設定

```bash
# .env.exampleファイルをコピー
cp .env.example .env

# 必要に応じて.envファイルを編集
nano .env
```

## 使用方法

### 認証ファイルの生成

```bash
# 仮想環境をアクティベート
source venv/bin/activate

# 認証ファイルを生成
python generate_state_json.py
```

### Akuma スクレイピング

```bash
# 仮想環境をアクティベート
source venv/bin/activate

# スクレイピング実行
python akuma_scraping.py
```
