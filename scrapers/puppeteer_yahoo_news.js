#!/usr/bin/env node
/**
 * Puppeteer でYahooニュースデータを収集（学習・研究目的）
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');

class PuppeteerYahooNewsScraper {
    constructor() {
        this.browser = null;
        this.page = null;
        this.newsData = [];
    }

    async setupBrowser() {
        console.log('[INFO] Puppeteerでブラウザを起動...');
        
        try {
            // システムのChromeを使用
            const chromePath = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
            
            this.browser = await puppeteer.launch({
                executablePath: chromePath,
                headless: true, // バックグラウンド実行
                args: [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                ]
            });
            
            this.page = await this.browser.newPage();
            
            // User-Agentを設定
            await this.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
            
            console.log('[SUCCESS] ブラウザ起動成功！');
            return true;
            
        } catch (error) {
            console.log(`[ERROR] ブラウザ起動エラー: ${error.message}`);
            return false;
        }
    }

    async scrapeYahooNews() {
        console.log('\n=== Puppeteer Yahooニュース収集 ===');

        if (!await this.setupBrowser()) {
            return false;
        }

        try {
            const url = 'https://news.yahoo.co.jp/';
            console.log(`[INFO] アクセス: ${url}`);
            
            await this.page.goto(url, { waitUntil: 'networkidle0' });
            console.log('[INFO] ページ読み込み完了');
            
            // ニュース記事のリンクを収集
            console.log('[INFO] ニュース記事を検索中...');
            
            const newsLinks = await this.page.evaluate(() => {
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
            });
            
            console.log(`[INFO] ${newsLinks.length}件のニュースリンクを発見`);
            
            // 重複を除去
            const uniqueLinks = [];
            const seenUrls = new Set();
            
            for (const link of newsLinks) {
                if (!seenUrls.has(link.url)) {
                    uniqueLinks.push(link);
                    seenUrls.add(link.url);
                }
            }
            
            console.log(`[INFO] 重複除去後: ${uniqueLinks.length}件`);
            
            // 詳細情報を取得（最初の10件）
            const maxArticles = Math.min(10, uniqueLinks.length);
            
            for (let i = 0; i < maxArticles; i++) {
                try {
                    const link = uniqueLinks[i];
                    console.log(`[INFO] 記事 ${i+1}/${maxArticles} を処理中...`);
                    
                    // 記事ページにアクセス
                    await this.page.goto(link.url, { waitUntil: 'networkidle0' });
                    
                    // 記事の詳細情報を取得
                    const articleData = await this.page.evaluate((url, title) => {
                        const data = {
                            url: url,
                            title: title,
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
                                if (data.category) break;
                            }
                        }
                        
                        return data;
                    }, link.url, link.title);
                    
                    this.newsData.push(articleData);
                    console.log(`[SUCCESS] 記事収集完了: ${articleData.title.substring(0, 50)}...`);
                    
                    // 少し待機（サーバー負荷軽減）
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                } catch (error) {
                    console.log(`[WARN] 記事処理エラー: ${error.message}`);
                    continue;
                }
            }
            
            // 結果をファイルに保存
            const result = {
                tool: 'puppeteer',
                success: this.newsData.length > 0,
                timestamp: new Date().toISOString(),
                total_articles: this.newsData.length,
                articles: this.newsData,
                source_url: url
            };
            
            const outputFile = 'puppeteer_yahoo_news.json';
            fs.writeFileSync(outputFile, JSON.stringify(result, null, 2), 'utf-8');
            
            console.log(`\\n[SUMMARY] Puppeteer収集結果:`);
            console.log(`  - 総記事数: ${this.newsData.length}`);
            console.log(`  - 保存ファイル: ${outputFile}`);
            
            this.newsData.slice(0, 5).forEach((article, i) => {
                console.log(`  [${i+1}] ${article.title.substring(0, 60)}...`);
            });
            
            await this.browser.close();
            
            if (this.newsData.length > 0) {
                console.log(`\\n[SUCCESS] Puppeteerによるニュース収集が成功しました！`);
                return true;
            } else {
                console.log(`\\n[ERROR] ニュースが1件も収集できませんでした`);
                return false;
            }
            
        } catch (error) {
            console.log(`[ERROR] スクレイピングエラー: ${error.message}`);
            if (this.browser) {
                await this.browser.close();
            }
            return false;
        }
    }
}

// メイン実行
async function main() {
    console.log('Puppeteer Yahoo!ニュース収集を開始します...\\n');

    const scraper = new PuppeteerYahooNewsScraper();
    const success = await scraper.scrapeYahooNews();

    if (success) {
        console.log('\\n' + '='.repeat(60));
        console.log('[SUCCESS] Puppeteerでニュース収集完了！');
        console.log('[INFO] 高速で安定したスクレイピングが実現できました');
        console.log('='.repeat(60));
    } else {
        console.log('\\n[ERROR] ニュース収集に失敗しました');
    }
}

if (require.main === module) {
    main().catch(console.error);
}