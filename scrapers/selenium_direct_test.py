#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriverの最新版を直接ダウンロードしてテスト
"""

import requests
import zipfile
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
import time

def get_chrome_version():
    """現在のChromeバージョンを取得"""
    import subprocess
    try:
        # Windows版Chrome
        result = subprocess.run([
            'reg', 'query', 
            'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon',
            '/v', 'version'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'version' in line:
                    version = line.split()[-1]
                    return version
    except:
        pass
    
    # 代替手段：Chrome実行ファイルから
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            return version
    except:
        pass
    
    return "139.0.7258.155"  # デフォルト値（エラーメッセージから取得）

def download_latest_chromedriver():
    """最新のChromeDriverをダウンロード"""
    print("[INFO] Chromeバージョンを確認中...")
    chrome_version = get_chrome_version()
    major_version = chrome_version.split('.')[0]
    print(f"[INFO] Chromeバージョン: {chrome_version} (メジャー: {major_version})")
    
    # ChromeDriver APIから最新バージョンを取得
    try:
        print("[INFO] 最新ChromeDriverバージョンを取得中...")
        api_url = f"https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        # Stableバージョンを取得
        stable_version = data['channels']['Stable']['version']
        downloads = data['channels']['Stable']['downloads']['chromedriver']
        
        # Windows版を探す
        win64_url = None
        for download in downloads:
            if download['platform'] == 'win64':
                win64_url = download['url']
                break
        
        if not win64_url:
            raise Exception("Windows版ChromeDriverが見つかりません")
        
        print(f"[INFO] 最新ChromeDriverバージョン: {stable_version}")
        print(f"[INFO] ダウンロード URL: {win64_url}")
        
        # 一時ディレクトリにダウンロード
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'chromedriver.zip')
        
        print("[INFO] ChromeDriverをダウンロード中...")
        with requests.get(win64_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # ZIPファイルを展開
        extract_path = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # chromedriver.exeのパスを見つける
        chromedriver_path = None
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file == 'chromedriver.exe':
                    chromedriver_path = os.path.join(root, file)
                    break
            if chromedriver_path:
                break
        
        if not chromedriver_path:
            raise Exception("chromedriver.exeが見つかりません")
        
        print(f"[SUCCESS] ChromeDriver準備完了: {chromedriver_path}")
        return chromedriver_path
        
    except Exception as e:
        print(f"[ERROR] ChromeDriverダウンロードエラー: {e}")
        return None

def test_with_latest_driver():
    """最新のChromeDriverでテスト"""
    print("\n=== 最新ChromeDriverでテスト ===")
    
    # 最新のChromeDriverをダウンロード
    driver_path = download_latest_chromedriver()
    
    if not driver_path:
        print("[ERROR] ChromeDriverが取得できませんでした")
        return False
    
    # Selenium テスト
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # F12ログ収集設定
    options.set_capability('goog:loggingPrefs', {
        'browser': 'ALL'
    })
    
    try:
        print("[INFO] ブラウザ起動中...")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("[SUCCESS] ブラウザ起動成功！")
        
        # テスト用HTMLを作成
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head><title>Selenium Test</title></head>
        <body>
            <h1>F12ログテスト</h1>
            <button id="errorBtn">エラーボタン</button>
            <script>
                console.log('INFO: ページ読み込み完了');
                console.warn('WARNING: テスト警告メッセージ');
                console.error('ERROR: テストエラーメッセージ');
                
                document.getElementById('errorBtn').onclick = function() {
                    throw new Error('ボタンクリックエラー');
                };
                
                // 自動エラー
                setTimeout(() => {
                    console.error('自動発生エラー');
                }, 1000);
            </script>
        </body>
        </html>
        '''
        
        # HTMLをdata URLとして読み込み
        driver.execute_script("document.write(arguments[0]);", html_content)
        time.sleep(2)  # ログ蓄積待ち
        
        # F12ログを取得
        print("[INFO] F12コンソールログを取得...")
        logs = driver.get_log('browser')
        
        print(f"[SUCCESS] ログ収集完了: {len(logs)}件")
        
        # ログ内容表示
        for i, log in enumerate(logs[:10]):  # 最初の10件
            level = log['level']
            message = log['message']
            if len(message) > 100:
                message = message[:100] + "..."
            print(f"  [{i+1}] {level}: {message}")
        
        # 結果保存
        result = {
            'success': True,
            'chrome_version': get_chrome_version(),
            'chromedriver_path': driver_path,
            'log_count': len(logs),
            'logs': logs
        }
        
        with open('selenium_success_results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        driver.quit()
        print("[SUCCESS] 全テスト完了！Seleniumが正常に動作し、F12ログが取得できました")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] テストエラー: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    print("ChromeDriverの最新版を取得してテストします...\n")
    success = test_with_latest_driver()
    
    if success:
        print("\n[SUCCESS] Seleniumが完全に動作します！")
        print("[INFO] これでAIがF12ログを自動収集できるようになりました")
    else:
        print("\n[ERROR] Seleniumの設定に問題があります")