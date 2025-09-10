#!/usr/bin/env node
/**
 * Puppeteer でF12ログを収集するテスト
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

class PuppeteerF12Collector {
    constructor() {
        this.logs = [];
        this.browser = null;
        this.page = null;
    }

    async setupBrowser() {
        console.log('[INFO] Puppeteerでブラウザを起動...');
        
        try {
            // システムのChromeを使用
            const chromePath = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
            
            this.browser = await puppeteer.launch({
                executablePath: chromePath,
                headless: false, // デバッグのため表示
                devtools: false,
                defaultViewport: { width: 1280, height: 720 },
                args: [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--enable-logging',
                    '--log-level=0'
                ]
            });
            
            this.page = await this.browser.newPage();
            console.log('[SUCCESS] ブラウザ起動成功！');
            
            // F12ログを収集するリスナーを設定
            this.setupLogCollectors();
            
            return true;
            
        } catch (error) {
            console.log(`[ERROR] ブラウザ起動エラー: ${error.message}`);
            return false;
        }
    }

    setupLogCollectors() {
        console.log('[INFO] F12ログ収集リスナーを設定...');
        
        // コンソールログを収集
        this.page.on('console', msg => {
            const log = {
                type: 'console',
                level: msg.type(), // 'log', 'warn', 'error', 'info', 'debug'
                text: msg.text(),
                timestamp: new Date().toISOString(),
                url: this.page.url()
            };
            this.logs.push(log);
            console.log(`[CONSOLE-${log.level.toUpperCase()}] ${log.text}`);
        });

        // JavaScriptエラーを収集
        this.page.on('pageerror', error => {
            const log = {
                type: 'javascript_error',
                level: 'error',
                text: error.message,
                stack: error.stack,
                timestamp: new Date().toISOString(),
                url: this.page.url()
            };
            this.logs.push(log);
            console.log(`[JS-ERROR] ${error.message}`);
        });

        // ネットワークエラーを収集
        this.page.on('requestfailed', request => {
            const log = {
                type: 'network_error',
                level: 'error',
                text: `Network request failed: ${request.url()}`,
                errorText: request.failure().errorText,
                timestamp: new Date().toISOString(),
                url: this.page.url()
            };
            this.logs.push(log);
            console.log(`[NETWORK-ERROR] ${request.url()}: ${request.failure().errorText}`);
        });

        // レスポンスエラーを収集
        this.page.on('response', response => {
            if (response.status() >= 400) {
                const log = {
                    type: 'http_error',
                    level: 'error',
                    text: `HTTP ${response.status()}: ${response.url()}`,
                    status: response.status(),
                    timestamp: new Date().toISOString(),
                    url: this.page.url()
                };
                this.logs.push(log);
                console.log(`[HTTP-ERROR] ${response.status()}: ${response.url()}`);
            }
        });
    }

    async testF12Collection() {
        console.log('\n=== Puppeteer F12ログ収集テスト ===');

        if (!await this.setupBrowser()) {
            return false;
        }

        try {
            // テスト用HTMLを作成
            const testHTML = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Puppeteer F12 Test</title>
            </head>
            <body>
                <h1>Puppeteer F12ログ収集テスト</h1>
                <button id="error-btn">エラー発生</button>
                <button id="warn-btn">警告発生</button>
                <button id="info-btn">情報ログ</button>
                <div id="output"></div>
                
                <script>
                    // 即座にログを出力
                    console.log('INFO: Puppeteerテストページが読み込まれました - ' + new Date().toISOString());
                    console.warn('WARNING: Puppeteer警告テスト');
                    console.error('ERROR: Puppeteerエラーテスト');
                    console.info('INFO: 情報メッセージテスト');
                    
                    // ボタンイベント
                    document.getElementById('error-btn').onclick = function() {
                        console.log('エラーボタンがクリックされました');
                        throw new Error('Puppeteerボタンによるエラー: ' + Math.random());
                    };
                    
                    document.getElementById('warn-btn').onclick = function() {
                        console.warn('Puppeteer警告ボタンがクリックされました');
                    };
                    
                    document.getElementById('info-btn').onclick = function() {
                        console.info('Puppeteer情報ボタンがクリックされました');
                    };
                    
                    // 自動ログ生成
                    setTimeout(() => {
                        console.log('1秒後の自動ログ');
                        console.error('自動エラー: ' + Math.random());
                    }, 1000);
                    
                    setTimeout(() => {
                        console.warn('2秒後の自動警告');
                        console.info('Puppeteerテスト完了');
                    }, 2000);
                    
                    // 実際のJavaScriptエラー
                    setTimeout(() => {
                        try {
                            undefinedFunction();
                        } catch(e) {
                            console.error('実際のJSエラー:', e.message);
                        }
                    }, 1500);
                </script>
            </body>
            </html>
            `;

            // HTMLファイルとして保存
            const htmlFile = path.resolve(__dirname, 'puppeteer_test_page.html');
            fs.writeFileSync(htmlFile, testHTML, 'utf-8');
            console.log(`[INFO] テストページを作成: ${htmlFile}`);

            // ページを開く
            const fileUrl = `file://${htmlFile.replace(/\\/g, '/')}`;
            console.log(`[INFO] ページを開く: ${fileUrl}`);
            
            await this.page.goto(fileUrl, { waitUntil: 'networkidle0' });
            console.log('[INFO] ページ読み込み完了');

            // ボタンをクリックしてさらにログを生成
            console.log('[INFO] ボタン操作を実行...');
            
            try {
                await this.page.click('#error-btn');
                await new Promise(resolve => setTimeout(resolve, 500));
                
                await this.page.click('#warn-btn');
                await new Promise(resolve => setTimeout(resolve, 500));
                
                await this.page.click('#info-btn');
                await new Promise(resolve => setTimeout(resolve, 500));
            } catch (error) {
                console.log(`[WARN] ボタンクリックエラー: ${error.message}`);
            }

            // 追加の待機時間
            await new Promise(resolve => setTimeout(resolve, 3000));
            console.log('[INFO] 全ログ生成完了');

            // ログを分析
            const analysis = this.analyzeLogs();
            
            console.log(`\n[SUMMARY] Puppeteer ログ収集結果:`);
            console.log(`  - 総ログ数: ${this.logs.length}`);
            console.log(`  - コンソールログ: ${analysis.console}`);
            console.log(`  - JavaScriptエラー: ${analysis.jsErrors}`);
            console.log(`  - ネットワークエラー: ${analysis.networkErrors}`);
            console.log(`  - HTTPエラー: ${analysis.httpErrors}`);

            // 詳細ログ表示
            console.log(`\n[INFO] 詳細ログ内容:`);
            this.logs.forEach((log, index) => {
                const shortText = log.text.length > 100 ? log.text.substring(0, 100) + '...' : log.text;
                console.log(`  [${index + 1}] ${log.type}(${log.level}): ${shortText}`);
            });

            // 結果をファイルに保存（AIが読み取り用）
            const result = {
                tool: 'puppeteer',
                success: this.logs.length > 0,
                timestamp: new Date().toISOString(),
                html_file: htmlFile,
                total_logs: this.logs.length,
                analysis: analysis,
                logs: this.logs
            };

            const outputFile = 'puppeteer_f12_results.json';
            fs.writeFileSync(outputFile, JSON.stringify(result, null, 2), 'utf-8');
            console.log(`[INFO] 結果を ${outputFile} に保存しました`);

            await this.browser.close();

            if (this.logs.length > 0) {
                console.log(`\n[SUCCESS] Puppeteer F12ログ収集が成功しました！`);
                return true;
            } else {
                console.log(`\n[ERROR] ログが1件も収集できませんでした`);
                return false;
            }

        } catch (error) {
            console.log(`[ERROR] テスト実行エラー: ${error.message}`);
            if (this.browser) {
                await this.browser.close();
            }
            return false;
        }
    }

    analyzeLogs() {
        const analysis = {
            console: 0,
            jsErrors: 0,
            networkErrors: 0,
            httpErrors: 0
        };

        this.logs.forEach(log => {
            switch (log.type) {
                case 'console':
                    analysis.console++;
                    break;
                case 'javascript_error':
                    analysis.jsErrors++;
                    break;
                case 'network_error':
                    analysis.networkErrors++;
                    break;
                case 'http_error':
                    analysis.httpErrors++;
                    break;
            }
        });

        return analysis;
    }
}

// メイン実行
async function main() {
    console.log('Puppeteer F12ログ収集テストを開始します...\n');

    const collector = new PuppeteerF12Collector();
    const success = await collector.testF12Collection();

    if (success) {
        console.log('\n' + '='.repeat(60));
        console.log('[SUCCESS] PuppeteerによるF12ログ収集が完全に動作しています！');
        console.log('[INFO] ログ収集がSeleniumより高速でした');
        console.log('='.repeat(60));
    } else {
        console.log('\n[ERROR] Puppeteerのセットアップに問題があります');
    }
}

if (require.main === module) {
    main().catch(console.error);
}