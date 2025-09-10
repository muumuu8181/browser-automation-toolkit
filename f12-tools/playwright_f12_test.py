#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright でF12ログを収集するテスト
"""

import json
import time
import os
import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

class PlaywrightF12Collector:
    def __init__(self):
        self.logs = []
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def setup_browser(self):
        """ブラウザを起動してログ収集の準備をする"""
        print("[INFO] Playwrightでブラウザを起動...")
        
        try:
            self.playwright = await async_playwright().start()
            
            # Chromiumブラウザを起動
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # デバッグのため表示
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            # ブラウザコンテキストを作成
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            
            # ページを作成
            self.page = await self.context.new_page()
            
            print("[SUCCESS] ブラウザ起動成功！")
            
            # F12ログ収集リスナーを設定
            await self.setup_log_collectors()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] ブラウザ起動エラー: {e}")
            return False

    async def setup_log_collectors(self):
        """F12ログ収集リスナーを設定"""
        print("[INFO] F12ログ収集リスナーを設定...")
        
        # コンソールログを収集
        def handle_console(msg):
            log = {
                'type': 'console',
                'level': msg.type,  # 'log', 'warn', 'error', 'info', 'debug'
                'text': msg.text,
                'timestamp': time.time(),
                'url': self.page.url if self.page else 'unknown'
            }
            self.logs.append(log)
            print(f"[CONSOLE-{log['level'].upper()}] {log['text']}")
        
        self.page.on('console', handle_console)
        
        # JavaScriptエラーを収集
        def handle_page_error(error):
            log = {
                'type': 'javascript_error',
                'level': 'error',
                'text': str(error),
                'timestamp': time.time(),
                'url': self.page.url if self.page else 'unknown'
            }
            self.logs.append(log)
            print(f"[JS-ERROR] {error}")
        
        self.page.on('pageerror', handle_page_error)
        
        # ネットワークエラーを収集
        def handle_request_failed(request):
            log = {
                'type': 'network_error',
                'level': 'error',
                'text': f"Network request failed: {request.url}",
                'failure_text': request.failure.error_text if request.failure else None,
                'timestamp': time.time(),
                'url': self.page.url if self.page else 'unknown'
            }
            self.logs.append(log)
            print(f"[NETWORK-ERROR] {request.url}: {request.failure.error_text if request.failure else 'Unknown'}")
        
        self.page.on('requestfailed', handle_request_failed)
        
        # レスポンスエラーを収集
        def handle_response(response):
            if response.status >= 400:
                log = {
                    'type': 'http_error',
                    'level': 'error',
                    'text': f"HTTP {response.status}: {response.url}",
                    'status': response.status,
                    'timestamp': time.time(),
                    'url': self.page.url if self.page else 'unknown'
                }
                self.logs.append(log)
                print(f"[HTTP-ERROR] {response.status}: {response.url}")
        
        self.page.on('response', handle_response)

    async def test_f12_collection(self):
        """F12ログ収集の詳細テスト"""
        print("\n=== Playwright F12ログ収集テスト ===")
        
        if not await self.setup_browser():
            return False
        
        try:
            # テスト用HTMLを作成
            test_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Playwright F12 Test</title>
            </head>
            <body>
                <h1>Playwright F12ログ収集テスト</h1>
                <button id="error-btn">エラー発生</button>
                <button id="warn-btn">警告発生</button>
                <button id="info-btn">情報ログ</button>
                <div id="output"></div>
                
                <script>
                    // 即座にログを出力
                    console.log('INFO: Playwrightテストページが読み込まれました - ' + new Date().toISOString());
                    console.warn('WARNING: Playwright警告テスト');
                    console.error('ERROR: Playwrightエラーテスト');
                    console.info('INFO: Playwright情報メッセージテスト');
                    
                    // ボタンイベント
                    document.getElementById('error-btn').onclick = function() {
                        console.log('Playwrightエラーボタンがクリックされました');
                        throw new Error('Playwrightボタンによるエラー: ' + Math.random());
                    };
                    
                    document.getElementById('warn-btn').onclick = function() {
                        console.warn('Playwright警告ボタンがクリックされました');
                    };
                    
                    document.getElementById('info-btn').onclick = function() {
                        console.info('Playwright情報ボタンがクリックされました');
                    };
                    
                    // 自動ログ生成
                    setTimeout(() => {
                        console.log('1秒後のPlaywright自動ログ');
                        console.error('自動エラー: ' + Math.random());
                    }, 1000);
                    
                    setTimeout(() => {
                        console.warn('2秒後のPlaywright自動警告');
                        console.info('Playwrightテスト完了');
                    }, 2000);
                    
                    // 実際のJavaScriptエラー
                    setTimeout(() => {
                        try {
                            playwrightUndefinedFunction();
                        } catch(e) {
                            console.error('Playwright実際のJSエラー:', e.message);
                        }
                    }, 1500);
                </script>
            </body>
            </html>
            """
            
            # HTMLファイルとして保存
            html_file = os.path.abspath('playwright_test_page.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(test_html)
            
            print(f"[INFO] テストページを作成: {html_file}")
            
            # ページを開く
            file_url = f'file:///{html_file.replace(os.sep, "/")}'
            print(f"[INFO] ページを開く: {file_url}")
            
            await self.page.goto(file_url)
            print("[INFO] ページ読み込み完了")
            
            # ページが安定するまで待機
            await self.page.wait_for_load_state('networkidle')
            
            # ボタンをクリックしてさらにログを生成
            print("[INFO] ボタン操作を実行...")
            
            try:
                await self.page.click('#error-btn')
                await self.page.wait_for_timeout(500)
                
                await self.page.click('#warn-btn')
                await self.page.wait_for_timeout(500)
                
                await self.page.click('#info-btn')
                await self.page.wait_for_timeout(500)
            except Exception as e:
                print(f"[WARN] ボタンクリックエラー: {e}")
            
            # 追加の待機時間
            await self.page.wait_for_timeout(3000)
            print("[INFO] 全ログ生成完了")
            
            # ログを分析
            analysis = self.analyze_logs()
            
            print(f"\n[SUMMARY] Playwright ログ収集結果:")
            print(f"  - 総ログ数: {len(self.logs)}")
            print(f"  - コンソールログ: {analysis['console']}")
            print(f"  - JavaScriptエラー: {analysis['jsErrors']}")
            print(f"  - ネットワークエラー: {analysis['networkErrors']}")
            print(f"  - HTTPエラー: {analysis['httpErrors']}")
            
            # 詳細ログ表示
            print(f"\n[INFO] 詳細ログ内容:")
            for i, log in enumerate(self.logs[:15]):  # 最初の15件
                short_text = log['text'][:100] + '...' if len(log['text']) > 100 else log['text']
                print(f"  [{i+1}] {log['type']}({log['level']}): {short_text}")
            
            # 結果をファイルに保存（AIが読み取り用）
            result = {
                'tool': 'playwright',
                'success': len(self.logs) > 0,
                'timestamp': time.time(),
                'html_file': html_file,
                'total_logs': len(self.logs),
                'analysis': analysis,
                'logs': self.logs
            }
            
            output_file = 'playwright_f12_results.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"[INFO] 結果を {output_file} に保存しました")
            
            await self.cleanup()
            
            if len(self.logs) > 0:
                print(f"\n[SUCCESS] Playwright F12ログ収集が成功しました！")
                return True
            else:
                print(f"\n[ERROR] ログが1件も収集できませんでした")
                return False
                
        except Exception as e:
            print(f"[ERROR] テスト実行エラー: {e}")
            await self.cleanup()
            return False

    def analyze_logs(self):
        """ログを分析して統計を作成"""
        analysis = {
            'console': 0,
            'jsErrors': 0,
            'networkErrors': 0,
            'httpErrors': 0
        }
        
        for log in self.logs:
            if log['type'] == 'console':
                analysis['console'] += 1
            elif log['type'] == 'javascript_error':
                analysis['jsErrors'] += 1
            elif log['type'] == 'network_error':
                analysis['networkErrors'] += 1
            elif log['type'] == 'http_error':
                analysis['httpErrors'] += 1
        
        return analysis

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
    print("Playwright F12ログ収集テストを開始します...\n")
    
    collector = PlaywrightF12Collector()
    success = await collector.test_f12_collection()
    
    if success:
        print('\n' + '='*60)
        print('[SUCCESS] PlaywrightによるF12ログ収集が完全に動作しています！')
        print('[INFO] 複数ブラウザ対応とモダンなAPIが特徴です')
        print('='*60)
    else:
        print('\n[ERROR] Playwrightのセットアップに問題があります')
        print('[INFO] playwright install chromium を実行してください')

if __name__ == "__main__":
    asyncio.run(main())