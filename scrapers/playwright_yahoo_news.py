#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright でYahooニュースデータを収集（学習・研究目的）
"""

import json
import time
import asyncio
from playwright.async_api import async_playwright

class PlaywrightYahooNewsScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.news_data = []

    async def setup_browser(self):
        """ブラウザを起動してスクレイピングの準備をする"""
        print("[INFO] Playwrightでブラウザを起動...")
        
        try:
            self.playwright = await async_playwright().start()
            
            # Chromiumブラウザを起動
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # バックグラウンド実行
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            # ブラウザコンテキストを作成
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # ページを作成
            self.page = await self.context.new_page()
            
            print("[SUCCESS] ブラウザ起動成功！")
            return True
            
        except Exception as e:
            print(f"[ERROR] ブラウザ起動エラー: {e}")
            return False

    async def scrape_yahoo_news(self):
        """Yahooニュースをスクレイピング"""
        print("\n=== Playwright Yahooニュース収集 ===")
        
        if not await self.setup_browser():
            return False
        
        try:
            url = "https://news.yahoo.co.jp/"
            print(f"[INFO] アクセス: {url}")
            
            await self.page.goto(url)
            await self.page.wait_for_load_state('networkidle')
            print("[INFO] ページ読み込み完了")
            
            # ニュース記事のリンクを収集
            print("[INFO] ニュース記事を検索中...")
            
            news_links = await self.page.evaluate("""
                () => {
                    const links = [];
                    
                    // 複数のセレクターを試す
                    const selectors = [
                        'a[href*="/articles/"]',
                        'div[class*="newsList"] a',
                        'div[class*="topicsListItem"] a', 
                        'article a',
                        '.newsFeed a',
                        '[data-cl-params*="articles"] a'
                    ];
                    
                    selectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(element => {
                            const href = element.href;
                            const text = element.textContent?.trim();
                            
                            if (href && href.includes('yahoo.co.jp') && text && text.length > 10) {
                                links.push({
                                    url: href,
                                    title: text,
                                    selector: selector
                                });
                            }
                        });
                    });
                    
                    return links;
                }
            """)
            
            print(f"[INFO] {len(news_links)}件のニュースリンクを発見")
            
            # 重複を除去
            unique_links = []
            seen_urls = set()
            
            for link in news_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            print(f"[INFO] 重複除去後: {len(unique_links)}件")
            
            # 詳細情報を取得（最初の10件）
            max_articles = min(10, len(unique_links))
            
            for i in range(max_articles):
                try:
                    link = unique_links[i]
                    print(f"[INFO] 記事 {i+1}/{max_articles} を処理中...")
                    
                    # 記事ページにアクセス
                    await self.page.goto(link['url'])
                    await self.page.wait_for_load_state('networkidle')
                    
                    # 記事の詳細情報を取得
                    article_data = await self.page.evaluate("""
                        () => {
                            const data = {
                                url: window.location.href,
                                title: document.title || document.querySelector('h1')?.textContent || 'No title',
                                content: '',
                                timestamp: '',
                                category: '',
                                source: 'yahoo_news',
                                scraped_at: Date.now()
                            };
                            
                            // 記事本文を取得
                            const contentSelectors = [
                                'div[class*="articleBody"] p',
                                'div[class*="article"] p',
                                '.article-body p',
                                'article p',
                                '.article-main p'
                            ];
                            
                            for (const selector of contentSelectors) {
                                const paragraphs = document.querySelectorAll(selector);
                                if (paragraphs.length > 0) {
                                    const contentParts = Array.from(paragraphs)
                                        .map(p => p.textContent?.trim())
                                        .filter(text => text && text.length > 10);
                                    
                                    if (contentParts.length > 0) {
                                        data.content = contentParts.join('\\n');
                                        break;
                                    }
                                }
                            }
                            
                            // タイムスタンプを取得
                            const timeSelectors = [
                                'time',
                                '.article-date',
                                '.timestamp',
                                '[class*="time"]',
                                '[class*="date"]'
                            ];
                            
                            for (const selector of timeSelectors) {
                                const timeElement = document.querySelector(selector);
                                if (timeElement) {
                                    data.timestamp = timeElement.textContent?.trim() || 
                                                    timeElement.getAttribute('datetime') || '';
                                    if (data.timestamp) break;
                                }
                            }
                            
                            // カテゴリを取得
                            const categorySelectors = [
                                '.category',
                                '[class*="category"]',
                                '.breadcrumb a',
                                'nav a'
                            ];
                            
                            for (const selector of categorySelectors) {
                                const categoryElement = document.querySelector(selector);
                                if (categoryElement) {
                                    data.category = categoryElement.textContent?.trim() || '';
                                    if (data.category && data.category.length < 50) break;
                                }
                            }
                            
                            return data;
                        }
                    """)
                    
                    self.news_data.append(article_data)
                    print(f"[SUCCESS] 記事収集完了: {article_data['title'][:50]}...")
                    
                    # 少し待機（サーバー負荷軽減）
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"[WARN] 記事処理エラー: {e}")
                    continue
            
            # 結果をファイルに保存
            result = {
                'tool': 'playwright',
                'success': len(self.news_data) > 0,
                'timestamp': time.time(),
                'total_articles': len(self.news_data),
                'articles': self.news_data,
                'source_url': url
            }
            
            output_file = 'playwright_yahoo_news.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n[SUMMARY] Playwright収集結果:")
            print(f"  - 総記事数: {len(self.news_data)}")
            print(f"  - 保存ファイル: {output_file}")
            
            for i, article in enumerate(self.news_data[:5]):
                print(f"  [{i+1}] {article['title'][:60]}...")
            
            await self.cleanup()
            
            if len(self.news_data) > 0:
                print(f"\n[SUCCESS] Playwrightによるニュース収集が成功しました！")
                return True
            else:
                print(f"\n[ERROR] ニュースが1件も収集できませんでした")
                return False
                
        except Exception as e:
            print(f"[ERROR] スクレイピングエラー: {e}")
            await self.cleanup()
            return False

    async def cleanup(self):
        """リソースをクリーンアップ"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("[INFO] ブラウザを閉じました")
        except Exception as e:
            print(f"[WARN] クリーンアップエラー: {e}")

async def main():
    """メイン実行関数"""
    print("Playwright Yahoo!ニュース収集を開始します...\n")
    
    scraper = PlaywrightYahooNewsScraper()
    success = await scraper.scrape_yahoo_news()
    
    if success:
        print('\n' + '='*60)
        print('[SUCCESS] Playwrightでニュース収集完了！')
        print('[INFO] 複数ブラウザ対応の高性能スクレイピングツールです')
        print('='*60)
    else:
        print('\n[ERROR] ニュース収集に失敗しました')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] ユーザーによって中断されました")
    except Exception as e:
        print(f"\n[ERROR] 実行エラー: {e}")