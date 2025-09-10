#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F12ログが確実に取得できるかテスト
"""

import requests
import zipfile
import os
import tempfile
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import time

def get_chrome_version():
    """Chromeバージョン取得"""
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        result = subprocess.run([chrome_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            return version
    except:
        pass
    return "139.0.7258.155"

def download_chromedriver():
    """ChromeDriverをダウンロード"""
    chrome_version = get_chrome_version()
    major_version = chrome_version.split('.')[0]
    
    try:
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        for version_info in data['versions']:
            if version_info['version'].startswith(f"{major_version}."):
                if 'chromedriver' in version_info['downloads']:
                    for download in version_info['downloads']['chromedriver']:
                        if download['platform'] == 'win64':
                            # ダウンロードと展開
                            temp_dir = tempfile.mkdtemp()
                            zip_path = os.path.join(temp_dir, 'chromedriver.zip')
                            
                            with requests.get(download['url'], stream=True, timeout=30) as r:
                                r.raise_for_status()
                                with open(zip_path, 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                            
                            extract_path = os.path.join(temp_dir, 'extracted')
                            os.makedirs(extract_path, exist_ok=True)
                            
                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                zip_ref.extractall(extract_path)
                            
                            # chromedriver.exeを探す
                            for root, dirs, files in os.walk(extract_path):
                                for file in files:
                                    if file == 'chromedriver.exe':
                                        return os.path.join(root, file)
                            break
                    break
    except Exception as e:
        print(f"[ERROR] ChromeDriverダウンロード失敗: {e}")
    return None

def test_f12_collection():
    """F12ログ収集の詳細テスト"""
    print("=== F12ログ収集詳細テスト ===")
    
    driver_path = download_chromedriver()
    if not driver_path:
        print("[ERROR] ChromeDriverが取得できません")
        return False
    
    print(f"[INFO] ChromeDriver: {driver_path}")
    
    # Chrome設定
    options = Options()
    # options.add_argument('--headless')  # デバッグのため表示ON
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # ログ収集設定を詳しく
    options.set_capability('goog:loggingPrefs', {
        'browser': 'ALL',
        'driver': 'ALL',
        'performance': 'ALL'
    })
    
    try:
        print("[INFO] ブラウザ起動...")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("[SUCCESS] ブラウザ起動成功")
        
        # 確実にエラーが発生するHTMLページを作成
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>F12ログテスト</title>
        </head>
        <body>
            <h1>F12ログ収集テストページ</h1>
            <button id="error-btn">エラー発生ボタン</button>
            <button id="warn-btn">警告発生ボタン</button>
            <div id="output"></div>
            
            <script>
                // 即座にログを出力
                console.log('INFO: ページが読み込まれました - ' + new Date().toISOString());
                console.warn('WARNING: 警告テストメッセージ');
                console.error('ERROR: エラーテストメッセージ');
                
                // ボタンイベント
                document.getElementById('error-btn').onclick = function() {
                    console.log('ボタンがクリックされました');
                    try {
                        // 意図的にエラーを発生
                        var undefinedVar = null;
                        undefinedVar.someMethod();
                    } catch(e) {
                        console.error('ボタンエラー:', e.message);
                    }
                };
                
                document.getElementById('warn-btn').onclick = function() {
                    console.warn('警告ボタンがクリックされました');
                };
                
                // 自動的にいくつかのログを生成
                setTimeout(function() {
                    console.log('1秒後の自動ログ');
                    console.error('自動エラー: ' + Math.random());
                }, 1000);
                
                setTimeout(function() {
                    console.warn('2秒後の自動警告');
                    console.log('テスト完了');
                }, 2000);
                
                // 未定義変数エラー（実際のJSエラー）
                setTimeout(function() {
                    try {
                        nonExistentFunction();
                    } catch(e) {
                        console.error('実際のJSエラー:', e.message);
                    }
                }, 1500);
            </script>
        </body>
        </html>
        """
        
        # HTMLファイルとして保存
        html_file = os.path.abspath('f12_test_page.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(error_html)
        
        print(f"[INFO] テストページ作成: {html_file}")
        
        # ページを開く
        file_url = f'file:///{html_file.replace(os.sep, "/")}'
        print(f"[INFO] ページを開く: {file_url}")
        driver.get(file_url)
        
        # ページが読み込まれるまで待機
        time.sleep(1)
        print("[INFO] ページ読み込み完了")
        
        # ボタンをクリックしてさらにログを生成
        try:
            error_btn = driver.find_element(By.ID, 'error-btn')
            warn_btn = driver.find_element(By.ID, 'warn-btn')
            
            print("[INFO] エラーボタンをクリック")
            error_btn.click()
            time.sleep(0.5)
            
            print("[INFO] 警告ボタンをクリック")
            warn_btn.click()
            time.sleep(0.5)
        except Exception as e:
            print(f"[WARN] ボタン操作エラー: {e}")
        
        # 追加の待機時間
        time.sleep(3)
        print("[INFO] 全ログ生成完了")
        
        # F12ログを取得
        print("[INFO] コンソールログを取得...")
        console_logs = []
        try:
            logs = driver.get_log('browser')
            console_logs = logs
            print(f"[SUCCESS] コンソールログ {len(logs)} 件取得")
        except Exception as e:
            print(f"[ERROR] コンソールログ取得エラー: {e}")
        
        # パフォーマンスログも取得
        performance_logs = []
        try:
            perf_logs = driver.get_log('performance')
            performance_logs = perf_logs
            print(f"[INFO] パフォーマンスログ {len(perf_logs)} 件取得")
        except Exception as e:
            print(f"[WARN] パフォーマンスログ取得エラー: {e}")
        
        # ログ内容を分析
        error_count = 0
        warning_count = 0
        info_count = 0
        
        print(f"\n[INFO] 取得したコンソールログの内容:")
        for i, log in enumerate(console_logs):
            level = log.get('level', 'UNKNOWN')
            message = log.get('message', '')
            timestamp = log.get('timestamp', 0)
            
            if level == 'SEVERE':
                error_count += 1
            elif level == 'WARNING':
                warning_count += 1
            else:
                info_count += 1
            
            # メッセージを短縮
            if len(message) > 150:
                message = message[:150] + "..."
            
            print(f"  [{i+1}] {level}: {message}")
        
        print(f"\n[SUMMARY] 統計:")
        print(f"  - エラー (SEVERE): {error_count}")
        print(f"  - 警告 (WARNING): {warning_count}")  
        print(f"  - 情報 (INFO/LOG): {info_count}")
        print(f"  - 合計: {len(console_logs)}")
        
        # 結果をファイルに保存
        result = {
            'test_type': 'detailed_f12_collection',
            'success': len(console_logs) > 0,
            'chrome_version': get_chrome_version(),
            'chromedriver_path': driver_path,
            'html_file': html_file,
            'test_timestamp': time.time(),
            'console_log_count': len(console_logs),
            'performance_log_count': len(performance_logs),
            'error_count': error_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'console_logs': console_logs,
            'performance_logs': performance_logs[:10]  # 最初の10件だけ保存
        }
        
        output_file = 'detailed_f12_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] 詳細結果を {output_file} に保存")
        
        driver.quit()
        
        if len(console_logs) > 0:
            print(f"\n[SUCCESS] F12ログ収集が正常に動作しています！")
            print(f"[SUCCESS] {len(console_logs)} 件のログを正常に取得しました")
            return True
        else:
            print(f"\n[ERROR] F12ログが1件も取得できませんでした")
            return False
        
    except Exception as e:
        print(f"[ERROR] テスト実行エラー: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    print("F12ログ収集の詳細テストを開始します...\n")
    success = test_f12_collection()
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] SeleniumによるF12ログ収集が完全に動作しています！")
        print("[INFO] これでAIが自動的にJavaScriptエラーを検出できます")
        print("="*60)
    else:
        print("\n[ERROR] F12ログ収集に問題があります")
        print("[INFO] ブラウザの設定やSeleniumの設定を確認してください")