#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テトリスゲームのF12コンソールログ自動取得スクリプト
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import os
from datetime import datetime

class TetrisF12Logger:
    def __init__(self):
        self.driver = None
        self.logs = []
        
    def setup_driver(self):
        """コンソールログ取得可能なブラウザを設定"""
        # ログ取得を有効にする
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL', 'performance': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        print("[INFO] Chrome起動完了（F12ログ取得モード）")
        
    def capture_console_logs(self):
        """現在のコンソールログを取得"""
        logs = self.driver.get_log('browser')
        for log in logs:
            self.logs.append({
                'timestamp': datetime.fromtimestamp(log['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'level': log['level'],
                'message': log['message']
            })
        return logs
    
    def play_tetris_and_log(self):
        """テトリスを実行してログを収集"""
        try:
            # テトリスファイルを開く
            tetris_path = r"C:\Users\user\Desktop\work\90_cc\20250809\test_create-3-cli_tetris\01_CloudCode\tetris.html"
            file_url = f"file:///{tetris_path}"
            
            print(f"[INFO] テトリスゲームを開いています: {file_url}")
            self.driver.get(file_url)
            time.sleep(2)
            
            print("[INFO] ゲーム開始前のログを取得...")
            self.capture_console_logs()
            
            # JavaScriptでゲームの状態を確認
            game_state = self.driver.execute_script("""
                return {
                    title: document.title,
                    hasCanvas: document.querySelector('canvas') !== null,
                    bodyText: document.body.innerText.substring(0, 200)
                }
            """)
            
            print(f"[INFO] ページタイトル: {game_state['title'].encode('ascii', 'ignore').decode('ascii')}")
            print(f"[INFO] Canvas要素: {'あり' if game_state['hasCanvas'] else 'なし'}")
            
            # ゲームを少し操作
            print("\n[INFO] ゲームを自動操作します...")
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # スペースキーでゲーム開始（もしあれば）
            body.send_keys(Keys.SPACE)
            time.sleep(1)
            self.capture_console_logs()
            
            # 矢印キーで操作
            movements = [
                (Keys.LEFT, "左移動"),
                (Keys.RIGHT, "右移動"),
                (Keys.DOWN, "高速落下"),
                (Keys.UP, "回転"),
                (Keys.SPACE, "即落下")
            ]
            
            for key, action in movements:
                print(f"[ACTION] {action}")
                body.send_keys(key)
                time.sleep(0.5)
                self.capture_console_logs()
            
            # エラーを意図的に発生させる（デバッグ用）
            print("\n[INFO] デバッグ用のログを生成...")
            self.driver.execute_script("""
                console.log('[TETRIS] ゲーム状態チェック');
                console.warn('[TETRIS] 警告: テストメッセージ');
                console.error('[TETRIS] エラー: これはテストエラーです');
                console.info('[TETRIS] 情報: F12ログ取得テスト中');
                
                // ゲーム固有の情報を出力
                if (typeof score !== 'undefined') {
                    console.log('[TETRIS] 現在のスコア:', score);
                }
                if (typeof level !== 'undefined') {
                    console.log('[TETRIS] 現在のレベル:', level);
                }
            """)
            
            time.sleep(1)
            final_logs = self.capture_console_logs()
            
            # 結果を保存
            self.save_logs()
            
            print(f"\n[SUCCESS] ログ取得完了！")
            print(f"[INFO] 総ログ数: {len(self.logs)}")
            
            # ログの内訳を表示
            log_levels = {}
            for log in self.logs:
                level = log['level']
                log_levels[level] = log_levels.get(level, 0) + 1
            
            print("\n[ログレベル別集計]")
            for level, count in log_levels.items():
                print(f"  {level}: {count}件")
            
            # サンプルログを表示
            print("\n[最新のログ（最大5件）]")
            for log in self.logs[-5:]:
                print(f"  [{log['timestamp']}] {log['level']}: {log['message'][:100]}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] ログ取得中にエラー: {str(e)}")
            return False
    
    def save_logs(self):
        """ログをファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON形式で保存
        json_file = f"tetris_console_logs_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'game': 'Tetris',
                'timestamp': timestamp,
                'total_logs': len(self.logs),
                'logs': self.logs
            }, f, indent=2, ensure_ascii=False)
        
        # 読みやすいテキスト形式でも保存
        txt_file = f"tetris_console_logs_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("=== Tetris F12 Console Logs ===\n")
            f.write(f"取得日時: {timestamp}\n")
            f.write(f"総ログ数: {len(self.logs)}\n")
            f.write("="*50 + "\n\n")
            
            for log in self.logs:
                f.write(f"[{log['timestamp']}] {log['level']}\n")
                f.write(f"{log['message']}\n")
                f.write("-"*30 + "\n")
        
        print(f"[INFO] ログを保存しました:")
        print(f"  - {json_file}")
        print(f"  - {txt_file}")
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            print("[INFO] ブラウザを閉じました")

def main():
    """メイン実行関数"""
    print("=== Tetris F12コンソールログ取得デモ ===\n")
    
    logger = TetrisF12Logger()
    
    try:
        logger.setup_driver()
        success = logger.play_tetris_and_log()
        
        if success:
            print("\n[SUCCESS] F12ログ取得デモ完了！")
            print("[INFO] AIがこれらのログを使ってデバッグできます")
            input("\n[Enter]キーを押すとブラウザを閉じます...")
        
    except KeyboardInterrupt:
        print("\n[INFO] ユーザーによって中断されました")
    finally:
        logger.cleanup()

if __name__ == "__main__":
    main()