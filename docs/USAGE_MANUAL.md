# 3つのスクレイピングツール使い方マニュアル

## 作業フォルダ
```
C:\Users\user\Desktop\work\90_cc\20250908\contract-programming-tutorial\
```

## 1. Selenium（Python）

### 📁 ファイル
- `selenium_yahoo_news.py` - Yahooニュース収集
- `test_f12_logs.py` - F12ログ収集テスト
- `selenium_version_match.py` - バージョンマッチテスト

### ⚙️ セットアップ
```bash
# 依存関係インストール
pip install selenium webdriver-manager

# 実行
cd "C:/Users/user/Desktop/work/90_cc/20250908/contract-programming-tutorial"
python selenium_yahoo_news.py
```

### 📊 出力ファイル
- `selenium_yahoo_news.json` - 収集したニュースデータ
- `detailed_f12_results.json` - F12ログ結果

### 💡 使い方例
```python
# カスタムスクレイピング
from selenium_yahoo_news import SeleniumYahooNewsScraper

scraper = SeleniumYahooNewsScraper()
success = scraper.scrape_yahoo_news()
```

### 🔧 カスタマイズ方法
```python
# 収集記事数を変更
for i, link in enumerate(unique_links[:20]):  # 10件 → 20件

# 対象サイト変更
url = "https://other-news-site.com/"
```

---

## 2. Puppeteer（JavaScript/Node.js）

### 📁 ファイル
- `puppeteer_yahoo_news.js` - Yahooニュース収集
- `puppeteer_f12_test.js` - F12ログ収集テスト
- `package.json` - Node.js設定ファイル

### ⚙️ セットアップ
```bash
# 依存関係インストール（初回のみ）
cd "C:/Users/user/Desktop/work/90_cc/20250908/contract-programming-tutorial"
npm install puppeteer-core

# 実行
node puppeteer_yahoo_news.js
```

### 📊 出力ファイル
- `puppeteer_yahoo_news.json` - 収集したニュースデータ
- `puppeteer_f12_results.json` - F12ログ結果

### 💡 使い方例
```javascript
// カスタムスクレイピング
const { PuppeteerYahooNewsScraper } = require('./puppeteer_yahoo_news.js');

const scraper = new PuppeteerYahooNewsScraper();
const success = await scraper.scrapeYahooNews();
```

### 🔧 カスタマイズ方法
```javascript
// ヘッドレスモード変更
headless: false,  // ブラウザ表示
headless: true,   // バックグラウンド実行

// 収集記事数変更
const maxArticles = Math.min(20, uniqueLinks.length);  // 10件 → 20件

// 対象サイト変更
const url = 'https://other-news-site.com/';
```

---

## 3. Playwright（Python）

### 📁 ファイル
- `playwright_yahoo_news.py` - Yahooニュース収集
- `playwright_f12_test.py` - F12ログ収集テスト

### ⚙️ セットアップ
```bash
# 依存関係インストール（初回のみ）
pip install playwright
python -m playwright install chromium

# 実行
cd "C:/Users/user/Desktop/work/90_cc/20250908/contract-programming-tutorial"
python playwright_yahoo_news.py
```

### 📊 出力ファイル
- `playwright_yahoo_news.json` - 収集したニュースデータ
- `playwright_f12_results.json` - F12ログ結果

### 💡 使い方例
```python
# カスタムスクレイピング
import asyncio
from playwright_yahoo_news import PlaywrightYahooNewsScraper

async def main():
    scraper = PlaywrightYahooNewsScraper()
    success = await scraper.scrape_yahoo_news()

asyncio.run(main())
```

### 🔧 カスタマイズ方法
```python
# ヘッドレスモード変更
headless=False,  # ブラウザ表示
headless=True,   # バックグラウンド実行

# 収集記事数変更
max_articles = min(20, len(unique_links))  # 10件 → 20件

# 対象サイト変更
url = "https://other-news-site.com/"
```

---

## 🏆 ツール選択の指針

### JavaScript環境
```bash
# Puppeteerがおすすめ
npm install puppeteer-core
node puppeteer_yahoo_news.js
```

### Python環境
```bash
# 安定性重視 → Selenium
python selenium_yahoo_news.py

# 高機能重視 → Playwright
python playwright_yahoo_news.py
```

---

## 🚀 高度な使い方

### 1. 複数サイト同時スクレイピング
```python
# Selenium例
sites = [
    "https://news.yahoo.co.jp/",
    "https://news.livedoor.com/",
    "https://www.asahi.com/"
]

for site in sites:
    scraper = SeleniumYahooNewsScraper()
    # URLを動的変更
    scraper.scrape_news(site)
```

### 2. スケジュール実行
```bash
# Windows タスクスケジューラー
# 毎日12:00にニュース収集
schtasks /create /tn "NewsCollection" /tr "python selenium_yahoo_news.py" /sc daily /st 12:00
```

### 3. エラー処理強化
```python
# リトライ機能付き
import time

def scrape_with_retry(max_retries=3):
    for i in range(max_retries):
        try:
            scraper = SeleniumYahooNewsScraper()
            return scraper.scrape_yahoo_news()
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(5)  # 5秒待機してリトライ
                continue
            else:
                raise e
```

---

## 📝 ログファイル

### 実行ログの確認
```bash
# コンソール出力を保存
python selenium_yahoo_news.py > execution.log 2>&1

# ログファイル確認
type execution.log  # Windows
cat execution.log   # Linux/Mac
```

### 収集データの確認
```bash
# JSONファイルの中身確認（最初の10行）
type selenium_yahoo_news.json | head -10
```

---

## 🔧 トラブルシューティング

### Selenium
```bash
# ChromeDriverエラーの場合
python selenium_version_match.py  # バージョンマッチ版を使用
```

### Puppeteer
```bash
# Chromiumダウンロードエラーの場合
set PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
npm install puppeteer-core  # システムChromeを使用
```

### Playwright
```bash
# ブラウザインストールエラーの場合
python -m playwright install chromium --force
```

---

## 📊 パフォーマンス比較

| ツール | 記事収集数 | 実行時間 | メモリ使用量 | 安定性 |
|--------|------------|----------|--------------|--------|
| **Selenium** | 10件 | 約2分 | 中程度 | ⭐⭐⭐⭐ |
| **Puppeteer** | 10件 | 約1分 | 少ない | ⭐⭐⭐⭐⭐ |
| **Playwright** | 8件 | 約1.5分 | 少ない | ⭐⭐⭐ |

---

## 📞 サポート

### よくある質問
1. **Q: 収集できる記事数は？**
   A: デフォルト10件、コード変更で増減可能

2. **Q: 他のサイトでも使える？**
   A: セレクター部分を変更すれば対応可能

3. **Q: 商用利用は可能？**
   A: 各サイトの利用規約を確認してください

### 参考リンク
- [Selenium公式ドキュメント](https://selenium-python.readthedocs.io/)
- [Puppeteer公式ドキュメント](https://pptr.dev/)
- [Playwright公式ドキュメント](https://playwright.dev/python/)

---

**🎯 このマニュアルですべてのツールが使いこなせます！**