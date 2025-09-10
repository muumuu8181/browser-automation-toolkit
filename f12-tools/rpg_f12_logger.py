#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal RPGゲームのF12コンソールログ自動取得スクリプト
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

class RPGF12Logger:
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
    
    def play_rpg_and_log(self):
        """RPGを実行してログを収集"""
        try:
            # RPGファイルを開く
            rpg_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\web_rpg.html"
            file_url = f"file:///{rpg_path}"
            
            print(f"[INFO] RPGゲームを開いています: {file_url}")
            self.driver.get(file_url)
            time.sleep(2)
            
            print("[INFO] ゲーム開始前のログを取得...")
            self.capture_console_logs()
            
            # ゲームを操作
            print("\n[INFO] RPGゲームを自動操作します...")
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # ゲームプレイシミュレーション
            actions = [
                # 基本移動
                (Keys.RIGHT, "右に移動", 0.5),
                (Keys.DOWN, "下に移動", 0.5),
                (Keys.LEFT, "左に移動", 0.5),
                (Keys.UP, "上に移動", 0.5),
                
                # アイテム収集を狙う
                (Keys.RIGHT * 5, "アイテムを探して右へ", 1),
                (Keys.DOWN * 3, "アイテムを探して下へ", 1),
                
                # 敵との戦闘
                (Keys.SPACE, "アクション", 0.5),
                
                # WASDキーテスト
                ("w", "W（上）キー", 0.3),
                ("a", "A（左）キー", 0.3),
                ("s", "S（下）キー", 0.3),
                ("d", "D（右）キー", 0.3),
            ]
            
            for keys, action, wait in actions:
                print(f"[ACTION] {action}")
                body.send_keys(keys)
                time.sleep(wait)
                self.capture_console_logs()
            
            # エラーシナリオを意図的に作成
            print("\n[INFO] デバッグシナリオを実行...")
            self.driver.execute_script("""
                // プレイヤーのHPを減らして危険な状態を作る
                if (window.game) {
                    game.player.hp = 10;
                    console.warn('[RPG TEST] プレイヤーHP低下警告: HP=' + game.player.hp);
                    
                    // 敵を追加生成
                    for(let i = 0; i < 5; i++) {
                        spawnEnemy();
                    }
                    console.log('[RPG TEST] 敵を5体追加生成しました');
                    
                    // アイテムを生成
                    spawnItem();
                    console.log('[RPG TEST] アイテムを追加生成');
                    
                    // ゲーム状態をログ出力
                    console.info('[RPG TEST] 現在のゲーム状態:', {
                        playerPos: {x: game.player.x, y: game.player.y},
                        playerStats: {hp: game.player.hp, level: game.player.level, exp: game.player.exp},
                        enemyCount: game.enemies.length,
                        itemCount: game.items.length
                    });
                    
                    // エラーテスト
                    try {
                        throw new Error('これはテスト用のエラーです');
                    } catch(e) {
                        console.error('[RPG TEST] エラーキャッチテスト:', e.message);
                    }
                }
            """)
            
            # 最後にもう少しプレイ
            time.sleep(2)
            print("[ACTION] 激しい戦闘シミュレーション")
            for _ in range(10):
                body.send_keys(Keys.ARROW_LEFT)
                body.send_keys(Keys.ARROW_RIGHT)
                time.sleep(0.1)
            
            time.sleep(1)
            final_logs = self.capture_console_logs()
            
            # 結果を保存
            self.save_logs()
            
            print(f"\n[SUCCESS] ログ取得完了！")
            print(f"[INFO] 総ログ数: {len(self.logs)}")
            
            # ログの内訳を表示
            log_levels = {}
            rpg_logs = 0
            for log in self.logs:
                level = log['level']
                log_levels[level] = log_levels.get(level, 0) + 1
                if '[RPG]' in log['message']:
                    rpg_logs += 1
            
            print("\n[ログレベル別集計]")
            for level, count in log_levels.items():
                print(f"  {level}: {count}件")
            print(f"  RPG関連: {rpg_logs}件")
            
            # RPG関連のログを抽出して表示
            print("\n[RPG関連ログ（最新10件）]")
            rpg_related = [log for log in self.logs if '[RPG]' in log['message']]
            for log in rpg_related[-10:]:
                msg = log['message'].replace('console-api ', '')
                print(f"  [{log['timestamp']}] {msg[:100]}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] ログ取得中にエラー: {str(e)}")
            return False
    
    def save_logs(self):
        """ログをファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON形式で保存
        json_file = f"rpg_console_logs_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'game': 'Minimal RPG',
                'timestamp': timestamp,
                'total_logs': len(self.logs),
                'logs': self.logs
            }, f, indent=2, ensure_ascii=False)
        
        # 読みやすいテキスト形式でも保存
        txt_file = f"rpg_console_logs_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("=== Minimal RPG F12 Console Logs ===\n")
            f.write(f"取得日時: {timestamp}\n")
            f.write(f"総ログ数: {len(self.logs)}\n")
            f.write("="*50 + "\n\n")
            
            # RPG関連ログを優先表示
            f.write("【RPG関連ログ】\n")
            f.write("-"*30 + "\n")
            for log in self.logs:
                if '[RPG]' in log['message']:
                    f.write(f"[{log['timestamp']}] {log['level']}\n")
                    f.write(f"{log['message']}\n")
                    f.write("-"*30 + "\n")
            
            f.write("\n【その他のログ】\n")
            f.write("-"*30 + "\n")
            for log in self.logs:
                if '[RPG]' not in log['message']:
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
    print("=== Minimal RPG F12コンソールログ取得デモ ===\n")
    
    logger = RPGF12Logger()
    
    try:
        logger.setup_driver()
        success = logger.play_rpg_and_log()
        
        if success:
            print("\n[SUCCESS] F12ログ取得デモ完了！")
            print("[INFO] AIがこれらのログを使ってゲームの動作を理解し、デバッグできます")
            print("\n[TIP] RPGゲームでは以下のようなログが取得できます:")
            print("  - プレイヤーの移動ログ")
            print("  - アイテム取得/敵との戦闘ログ")
            print("  - レベルアップやゲームオーバー")
            print("  - エラーや警告メッセージ")
            input("\n[Enter]キーを押すとブラウザを閉じます...")
        
    except KeyboardInterrupt:
        print("\n[INFO] ユーザーによって中断されました")
    finally:
        logger.cleanup()

if __name__ == "__main__":
    main()