#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seleniumの基本動作テスト
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time

def simple_test():
    """シンプルなSelenium動作テスト"""
    print("=== Selenium 基本テスト ===")
    
    # Chrome設定
    options = Options()
    options.add_argument('--headless')  # 画面表示なし
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        print("[INFO] ChromeDriverをダウンロード中...")
        # 最新のChromeDriverを強制ダウンロード
        driver_path = ChromeDriverManager().install()
        print(f"[INFO] ChromeDriver パス: {driver_path}")
        
        print("[INFO] ブラウザ起動中...")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("[SUCCESS] ブラウザ起動成功！")
        
        # Googleにアクセスしてテスト
        print("[INFO] Google にアクセス中...")
        driver.get("https://www.google.com")
        
        title = driver.title
        print(f"[INFO] ページタイトル: {title}")
        
        # 成功
        driver.quit()
        print("[SUCCESS] テスト成功！Seleniumが正常に動作しています")
        return True
        
    except Exception as e:
        print(f"[ERROR] エラー発生: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

def test_f12_logs():
    """F12ログ収集テスト"""
    print("\n=== F12ログ収集テスト ===")
    
    options = Options()
    options.add_argument('--headless')
    
    # ログ収集設定
    options.set_capability('goog:loggingPrefs', {
        'browser': 'ALL'
    })
    
    try:
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("[INFO] テスト用HTMLページを作成中...")
        
        # エラーが発生するHTMLを直接作成
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>F12 Log Test</title></head>
        <body>
            <h1>F12ログテストページ</h1>
            <button onclick="testError()">エラーボタン</button>
            <script>
                console.log('INFO: ページが読み込まれました');
                console.warn('WARNING: テスト警告');
                console.error('ERROR: テストエラー');
                
                function testError() {
                    throw new Error('ボタンクリックによるエラー');
                }
                
                // 自動的にエラーを発生
                setTimeout(() => {
                    try {
                        throw new Error('自動発生エラー');
                    } catch(e) {
                        console.error('自動エラー:', e.message);
                    }
                }, 500);
            </script>
        </body>
        </html>
        """
        
        # テスト用HTMLファイルを作成
        with open('test_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # HTMLファイルを開く
        import os
        file_path = os.path.abspath('test_page.html')
        file_url = f'file:///{file_path.replace(os.sep, "/")}'
        
        print(f"[INFO] HTMLファイルを開く: {file_url}")
        driver.get(file_url)
        
        # ログが蓄積されるまで待機
        time.sleep(3)
        
        # F12のコンソールログを取得
        print("[INFO] F12コンソールログを取得中...")
        logs = driver.get_log('browser')
        
        print(f"[SUCCESS] 収集したログ数: {len(logs)}")
        
        # ログの内容を表示
        for i, log in enumerate(logs):
            level = log['level']
            message = log['message']
            timestamp = log['timestamp']
            
            # メッセージが長すぎる場合は短縮
            if len(message) > 150:
                message = message[:150] + "..."
            
            print(f"  [{i+1}] {level}: {message}")
        
        # 結果をファイルに保存（AIが読み取り用）
        result = {
            'test_type': 'f12_log_collection',
            'success': True,
            'log_count': len(logs),
            'logs': logs,
            'timestamp': time.time()
        }
        
        with open('f12_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("[INFO] 結果を f12_test_results.json に保存しました")
        
        driver.quit()
        print("[SUCCESS] F12ログ収集テスト成功！")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] F12ログテストエラー: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    print("Seleniumインストールと動作確認を開始します...\n")
    
    # 1. 基本動作テスト
    basic_success = simple_test()
    
    if basic_success:
        # 2. F12ログテスト
        f12_success = test_f12_logs()
        
        if f12_success:
            print("\n[SUCCESS] 全テスト完了！SeleniumでF12ログが取得できます")
            print("[INFO] これでAIが自動的にF12のログを収集できるようになりました")
        else:
            print("\n[WARNING] F12ログテストに失敗しましたが、基本機能は動作します")
    else:
        print("\n[ERROR] 基本動作テストに失敗しました")
        print("[INFO] ChromeDriverまたはChromeブラウザのバージョンに問題がある可能性があります")