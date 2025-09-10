#!/usr/bin/env python3
"""
Seleniumの簡単な動作テスト
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time

def simple_test():
    """シンプルなSelenium動作テスト"""
    print("=== Selenium 簡単テスト ===")
    
    # Chrome設定
    options = Options()
    options.add_argument('--headless')  # 画面表示なし
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        print("🚀 ChromeDriverをダウンロード中...")
        # 最新のChromeDriverを強制ダウンロード
        driver_path = ChromeDriverManager().install()
        print(f"📂 ChromeDriver パス: {driver_path}")
        
        print("🌐 ブラウザ起動中...")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ ブラウザ起動成功！")
        
        # Googleにアクセスしてテスト
        print("📝 Google にアクセス中...")
        driver.get("https://www.google.com")
        
        title = driver.title
        print(f"📄 ページタイトル: {title}")
        
        # 成功
        driver.quit()
        print("✅ テスト成功！Seleniumが正常に動作しています")
        return True
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        return False

def test_f12_logs_simple():
    """F12ログ収集の最小テスト"""
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
        
        # エラーが発生するHTMLを直接作成
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>F12ログテスト</h1>
            <script>
                console.log('INFO: ページが読み込まれました');
                console.warn('WARNING: テスト警告');
                console.error('ERROR: テストエラー');
                
                // 意図的にエラーを発生
                setTimeout(() => {
                    throw new Error('意図的なJavaScriptエラー');
                }, 1000);
            </script>
        </body>
        </html>
        """
        
        # HTMLをdata URLとして読み込み
        data_url = "data:text/html;charset=utf-8," + html_content.replace('\n', '').replace(' ', '%20')
        driver.get(data_url)
        
        # ログが蓄積されるまで待機
        time.sleep(2)
        
        # F12のコンソールログを取得
        logs = driver.get_log('browser')
        
        print(f"📝 収集したログ数: {len(logs)}")
        
        for log in logs:
            level = log['level']
            message = log['message'][:100] + '...' if len(log['message']) > 100 else log['message']
            print(f"  [{level}] {message}")
        
        # 結果をファイルに保存
        with open('simple_f12_test.json', 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        driver.quit()
        print("✅ F12ログ収集テスト成功！")
        return True
        
    except Exception as e:
        print(f"❌ F12ログテストエラー: {e}")
        return False

if __name__ == "__main__":
    # 1. 基本動作テスト
    basic_success = simple_test()
    
    if basic_success:
        # 2. F12ログテスト
        test_f12_logs_simple()
    else:
        print("❌ 基本動作テストに失敗したため、F12ログテストをスキップします")