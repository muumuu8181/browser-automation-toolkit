#!/usr/bin/env python3
"""
Seleniumを使ってF12のコンソールログを取得するデモ
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import time
import os

class F12LogCollector:
    def __init__(self, headless=True):
        """
        F12ログを収集するSeleniumクラス
        
        Args:
            headless (bool): ブラウザを非表示で動作させるか
        """
        self.headless = headless
        self.driver = None
        
    def setup_browser(self):
        """ブラウザを起動してログ収集の準備をする"""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        # F12のコンソールログを取得可能にする設定
        options.set_capability('goog:loggingPrefs', {
            'browser': 'ALL',        # コンソールログ
            'performance': 'ALL',    # ネットワークログ
            'driver': 'ALL'          # Seleniumドライバログ
        })
        
        # 自動でChromeDriverをダウンロードして設定
        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ ブラウザ起動完了")
        
    def test_html_file(self, html_file_path):
        """
        HTMLファイルを開いてF12ログを収集
        
        Args:
            html_file_path (str): テストするHTMLファイルのフルパス
            
        Returns:
            dict: ログ収集結果
        """
        if not self.driver:
            self.setup_browser()
            
        # 絶対パスに変換
        abs_path = os.path.abspath(html_file_path)
        file_url = f'file:///{abs_path.replace(os.sep, "/")}'
        
        print(f"📂 HTMLファイルを開く: {file_url}")
        
        try:
            # HTMLファイルを開く
            self.driver.get(file_url)
            time.sleep(2)  # ページ読み込み待機
            
            # 可能な操作を実行（ボタンクリックなど）
            self._perform_page_interactions()
            
            # F12ログを収集
            console_logs = self._get_console_logs()
            performance_logs = self._get_performance_logs()
            
            # 結果をまとめる
            result = {
                'success': self._analyze_logs(console_logs),
                'url': file_url,
                'console_logs': console_logs,
                'network_logs': performance_logs,
                'timestamp': time.time()
            }
            
            # 結果を保存（AIが読み取り用）
            self._save_results(result)
            
            return result
            
        except Exception as e:
            print(f"❌ エラー発生: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': file_url
            }
    
    def _perform_page_interactions(self):
        """ページ内のボタンなどを自動操作してログを発生させる"""
        try:
            # 契約プログラミングのデモページの赤いボタンをクリック
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button.danger')
            for i, button in enumerate(buttons[:3]):  # 最初の3つだけ
                print(f"🔴 危険ボタン{i+1}をクリック")
                button.click()
                time.sleep(1)  # ログが出る時間を待つ
                
        except Exception as e:
            print(f"⚠️ ボタン操作でエラー: {e}")
    
    def _get_console_logs(self):
        """F12のコンソールログを取得"""
        try:
            logs = self.driver.get_log('browser')
            formatted_logs = []
            
            for log in logs:
                formatted_logs.append({
                    'timestamp': log['timestamp'],
                    'level': log['level'],      # INFO, WARNING, SEVERE
                    'message': log['message'],
                    'source': log.get('source', 'unknown')
                })
            
            print(f"📝 コンソールログ {len(formatted_logs)} 件取得")
            return formatted_logs
            
        except Exception as e:
            print(f"⚠️ コンソールログ取得エラー: {e}")
            return []
    
    def _get_performance_logs(self):
        """パフォーマンス/ネットワークログを取得"""
        try:
            logs = self.driver.get_log('performance')
            network_logs = []
            
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    if message.get('message', {}).get('method') in ['Network.responseReceived', 'Network.loadingFailed']:
                        network_logs.append({
                            'timestamp': log['timestamp'],
                            'method': message['message']['method'],
                            'params': message['message'].get('params', {})
                        })
                except:
                    pass  # パース不可能なログは無視
            
            print(f"🌐 ネットワークログ {len(network_logs)} 件取得")
            return network_logs
            
        except Exception as e:
            print(f"⚠️ パフォーマンスログ取得エラー: {e}")
            return []
    
    def _analyze_logs(self, console_logs):
        """ログを分析してテスト成功/失敗を判定"""
        severe_errors = [log for log in console_logs if log['level'] == 'SEVERE']
        
        if severe_errors:
            print(f"❌ 重大エラー {len(severe_errors)} 件検出")
            for error in severe_errors:
                print(f"   - {error['message']}")
            return False
        else:
            print("✅ 重大エラーなし")
            return True
    
    def _save_results(self, result):
        """結果をJSONファイルに保存（AIが読み取り用）"""
        output_file = 'f12_logs_results.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 結果を保存: {output_file}")
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            print("🔒 ブラウザを閉じました")


def main():
    """メイン実行関数"""
    print("=== Selenium F12ログ収集デモ ===\n")
    
    # HTMLファイルのパス（契約プログラミングのデモページ）
    html_file = "C:/Users/user/Desktop/work/90_cc/20250908/contract-programming-tutorial/chart_with_contracts.html"
    
    if not os.path.exists(html_file):
        print(f"❌ HTMLファイルが見つかりません: {html_file}")
        return
    
    # ログ収集開始
    collector = F12LogCollector(headless=False)  # ブラウザを表示して動作確認
    
    try:
        result = collector.test_html_file(html_file)
        
        # 結果表示
        print(f"\n=== 結果 ===")
        print(f"成功: {result['success']}")
        print(f"コンソールログ数: {len(result.get('console_logs', []))}")
        print(f"ネットワークログ数: {len(result.get('network_logs', []))}")
        
        # エラーログの詳細表示
        if result.get('console_logs'):
            print("\n📝 コンソールログの内容:")
            for log in result['console_logs'][:5]:  # 最初の5件だけ
                print(f"  [{log['level']}] {log['message'][:100]}...")
        
    finally:
        collector.close()


if __name__ == "__main__":
    main()