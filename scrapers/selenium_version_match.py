#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome 139に対応するChromeDriverをダウンロードしてテスト
"""

import requests
import zipfile
import os
import tempfile
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
import time

def download_chromedriver_for_version(chrome_version):
    """指定されたChromeバージョンに対応するChromeDriverをダウンロード"""
    major_version = chrome_version.split('.')[0]  # 139
    print(f"[INFO] Chrome {major_version} に対応するChromeDriverを検索中...")
    
    try:
        # Chrome for Testing APIから該当バージョンを取得
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        # バージョン139系を探す
        target_version = None
        for version_info in data['versions']:
            if version_info['version'].startswith(f"{major_version}."):
                if 'chromedriver' in version_info['downloads']:
                    target_version = version_info
                    break
        
        if not target_version:
            print(f"[ERROR] Chrome {major_version} 対応のChromeDriverが見つかりません")
            return None
        
        version_number = target_version['version']
        print(f"[INFO] 対応するChromeDriverバージョン: {version_number}")
        
        # Windows版のURLを取得
        chromedriver_downloads = target_version['downloads']['chromedriver']
        win64_url = None
        
        for download in chromedriver_downloads:
            if download['platform'] == 'win64':
                win64_url = download['url']
                break
        
        if not win64_url:
            print("[ERROR] Windows版が見つかりません")
            return None
        
        print(f"[INFO] ダウンロード URL: {win64_url}")
        
        # ダウンロードと展開
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'chromedriver.zip')
        
        print("[INFO] ダウンロード中...")
        with requests.get(win64_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # 展開
        extract_path = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # chromedriver.exeを探す
        chromedriver_path = None
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file == 'chromedriver.exe':
                    chromedriver_path = os.path.join(root, file)
                    break
            if chromedriver_path:
                break
        
        if chromedriver_path:
            print(f"[SUCCESS] ChromeDriver準備完了: {chromedriver_path}")
            return chromedriver_path
        else:
            print("[ERROR] chromedriver.exeが見つかりません")
            return None
        
    except Exception as e:
        print(f"[ERROR] ダウンロードエラー: {e}")
        return None

def get_chrome_version_simple():
    """Chromeバージョンを取得（簡略版）"""
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        result = subprocess.run([chrome_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.strip()
            # "Google Chrome 139.0.7258.155" から "139.0.7258.155" を抽出
            version = version_line.split()[-1]
            return version
    except:
        pass
    
    return "139.0.7258.155"  # デフォルト

def test_f12_logs_matched():
    """バージョンマッチしたChromeDriverでF12ログテスト"""
    print("\n=== バージョンマッチテスト ===")
    
    chrome_version = get_chrome_version_simple()
    print(f"[INFO] 現在のChromeバージョン: {chrome_version}")
    
    driver_path = download_chromedriver_for_version(chrome_version)
    
    if not driver_path:
        print("[ERROR] 対応するChromeDriverが取得できませんでした")
        return False
    
    # テスト実行
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # F12ログ収集設定
    options.set_capability('goog:loggingPrefs', {
        'browser': 'ALL'
    })
    
    try:
        print("[INFO] ブラウザ起動...")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("[SUCCESS] ブラウザ起動成功！")
        
        # 契約プログラミングのデモページがあるかチェック
        html_file = "chart_with_contracts.html"
        if os.path.exists(html_file):
            print(f"[INFO] デモページを読み込み: {html_file}")
            file_path = os.path.abspath(html_file)
            file_url = f'file:///{file_path.replace(os.sep, "/")}'
            driver.get(file_url)
        else:
            # テスト用HTMLを直接作成
            print("[INFO] テスト用HTMLを作成...")
            driver.execute_script("""
                document.write(`
                <!DOCTYPE html>
                <html>
                <head><title>F12 Test</title></head>
                <body>
                    <h1>F12ログ収集テスト</h1>
                    <button onclick="makeError()">エラー発生</button>
                    <script>
                        console.log('テストページが読み込まれました');
                        console.warn('警告メッセージのテスト');
                        console.error('エラーメッセージのテスト');
                        
                        function makeError() {
                            throw new Error('ボタンによるエラー');
                        }
                        
                        // 自動エラー
                        setTimeout(() => {
                            console.error('自動発生エラー: ' + new Date().toISOString());
                        }, 1000);
                    </script>
                </body>
                </html>
                `);
            """)
        
        # ログが蓄積されるまで待機
        time.sleep(3)
        
        # F12ログを取得
        print("[INFO] F12コンソールログを取得...")
        logs = driver.get_log('browser')
        
        print(f"[SUCCESS] ログ収集完了: {len(logs)}件のログを取得しました")
        
        # ログを分析
        error_count = 0
        warning_count = 0
        info_count = 0
        
        print("[INFO] ログ内容:")
        for i, log in enumerate(logs):
            level = log['level']
            message = log['message']
            
            if level == 'SEVERE':
                error_count += 1
            elif level == 'WARNING':
                warning_count += 1
            else:
                info_count += 1
            
            # 長いメッセージは短縮
            if len(message) > 120:
                message = message[:120] + "..."
            
            print(f"  [{i+1}] {level}: {message}")
        
        print(f"[INFO] 統計: エラー={error_count}, 警告={warning_count}, 情報={info_count}")
        
        # 結果をファイルに保存（AIが読み取り用）
        result = {
            'success': True,
            'chrome_version': chrome_version,
            'chromedriver_path': driver_path,
            'test_timestamp': time.time(),
            'log_count': len(logs),
            'error_count': error_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'logs': logs
        }
        
        with open('f12_collection_results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("[INFO] 結果を f12_collection_results.json に保存しました")
        
        driver.quit()
        print("[SUCCESS] テスト完了！F12ログの自動収集が動作しています")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] テストエラー: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    print("Chrome/ChromeDriverのバージョンマッチテストを実行します...\n")
    
    success = test_f12_logs_matched()
    
    if success:
        print("\n" + "="*50)
        print("[SUCCESS] Seleniumが完全に動作します！")
        print("[SUCCESS] AIがF12ログを自動収集できるようになりました")
        print("[INFO] 契約プログラミング + F12ログ自動収集の組み合わせで")
        print("[INFO] AIの自動デバッグサイクルが実現可能です")
        print("="*50)
    else:
        print("\n[ERROR] まだ設定に問題があります")
        print("[INFO] 手動でChromeを最新版に更新してみてください")