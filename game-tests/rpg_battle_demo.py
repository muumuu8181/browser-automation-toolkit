#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPGゲーム戦闘デモ - 敵との激しいバトルをF12ログ付きで実演
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
from datetime import datetime

class RPGBattleDemo:
    def __init__(self):
        self.driver = None
        self.logs = []
        
    def setup_driver(self):
        """ブラウザ起動（F12ログ取得モード）"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        print("[INFO] バトルデモ用ブラウザ起動！")
        
    def capture_logs(self):
        """コンソールログを取得"""
        logs = self.driver.get_log('browser')
        for log in logs:
            # RPG関連のログのみ表示
            if '[RPG]' in log['message']:
                timestamp = datetime.fromtimestamp(log['timestamp'] / 1000).strftime('%H:%M:%S')
                message = log['message'].split('"')[-2] if '"' in log['message'] else log['message']
                print(f"[{timestamp}] {message}")
                self.logs.append(log)
    
    def epic_battle(self):
        """エピックバトルシーン"""
        try:
            # RPGを開く
            rpg_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\web_rpg.html"
            self.driver.get(f"file:///{rpg_path}")
            time.sleep(2)
            
            print("\n=== RPG バトルデモ開始！ ===\n")
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # 大量の敵を召喚！
            print("[SCENARIO] 敵の大群を召喚します！")
            self.driver.execute_script("""
                // 敵を10体召喚
                console.log('[RPG] === バトルモード開始！ ===');
                for(let i = 0; i < 10; i++) {
                    spawnEnemy();
                }
                console.warn('[RPG] 警告: 敵が10体出現！逃げろ！');
                
                // プレイヤーを強化
                game.player.speed = 10;
                game.player.hp = 150;
                game.player.maxHp = 150;
                console.log('[RPG] プレイヤー強化: スピード10, HP150');
            """)
            self.capture_logs()
            time.sleep(1)
            
            # 戦闘開始！
            print("\n[BATTLE] 激しい戦闘を開始！")
            
            # 回避行動
            print("[ACTION] 敵の群れを回避！")
            movements = [
                (Keys.LEFT * 5, "左へダッシュ！"),
                (Keys.UP * 3, "上へジャンプ！"),
                (Keys.RIGHT * 5, "右へ回り込む！"),
                (Keys.DOWN * 3, "スライディング！")
            ]
            
            for keys, action in movements:
                print(f"  > {action}")
                body.send_keys(keys)
                time.sleep(0.3)
                self.capture_logs()
            
            # パワーアップアイテムを大量生成
            print("\n[POWER-UP] 救援物資投下！")
            self.driver.execute_script("""
                // アイテムを10個生成
                for(let i = 0; i < 10; i++) {
                    spawnItem();
                }
                console.log('[RPG] 救援物資が10個投下された！');
            """)
            self.capture_logs()
            time.sleep(0.5)
            
            # アイテム収集しながら戦う
            print("\n[ACTION] アイテムを集めながら戦闘！")
            for i in range(20):
                # ジグザグ移動
                if i % 4 == 0:
                    body.send_keys(Keys.UP)
                elif i % 4 == 1:
                    body.send_keys(Keys.RIGHT)
                elif i % 4 == 2:
                    body.send_keys(Keys.DOWN)
                else:
                    body.send_keys(Keys.LEFT)
                
                time.sleep(0.1)
                
                # 5回に1回ログをチェック
                if i % 5 == 0:
                    self.capture_logs()
            
            # 最終決戦！
            print("\n[FINAL BATTLE] 最終決戦！")
            self.driver.execute_script("""
                // ボスを召喚
                const boss = {
                    x: 400,
                    y: 300,
                    width: 64,
                    height: 64,
                    hp: 200,
                    color: '#e74c3c',
                    id: 'BOSS'
                };
                game.enemies.push(boss);
                console.error('[RPG] ボス出現！HP200の強敵だ！');
                
                // 現在の状態を表示
                console.log('[RPG] プレイヤーHP: ' + game.player.hp);
                console.log('[RPG] レベル: ' + game.player.level);
                console.log('[RPG] 敵の数: ' + game.enemies.length);
            """)
            self.capture_logs()
            
            # ボスとの戦い
            print("[ACTION] ボスバトル！")
            for _ in range(30):
                # ランダムに動き回る
                import random
                key = random.choice([Keys.UP, Keys.DOWN, Keys.LEFT, Keys.RIGHT])
                body.send_keys(key)
                time.sleep(0.05)
            
            self.capture_logs()
            
            # 結果確認
            time.sleep(1)
            result = self.driver.execute_script("""
                return {
                    playerHP: game.player.hp,
                    playerLevel: game.player.level,
                    enemyCount: game.enemies.length,
                    itemCount: game.items.length,
                    playerPos: {x: Math.round(game.player.x), y: Math.round(game.player.y)}
                };
            """)
            
            print("\n=== バトル結果 ===")
            print(f"プレイヤーHP: {result['playerHP']}/150")
            print(f"レベル: {result['playerLevel']}")
            print(f"残存敵数: {result['enemyCount']}")
            print(f"アイテム数: {result['itemCount']}")
            print(f"最終位置: ({result['playerPos']['x']}, {result['playerPos']['y']})")
            
            if result['playerHP'] > 0:
                print("\n[VICTORY] 生き残った！勝利！")
                self.driver.execute_script("console.log('[RPG] 勝利！プレイヤーは生き残った！');")
            else:
                print("\n[GAME OVER] 敵が強すぎた...")
                self.driver.execute_script("console.error('[RPG] ゲームオーバー...');")
            
            self.capture_logs()
            
            # スクリーンショット
            self.driver.save_screenshot("rpg_battle_result.png")
            print("\n[INFO] バトルのスクリーンショットを保存: rpg_battle_result.png")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] バトル中にエラー: {str(e)}")
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(3)  # 結果を見るため少し待つ
            self.driver.quit()
            print("[INFO] ブラウザを閉じました")

def main():
    """メイン実行"""
    print("=== RPG エピックバトルデモ ===\n")
    
    demo = RPGBattleDemo()
    
    try:
        demo.setup_driver()
        success = demo.epic_battle()
        
        if success:
            print("\n[SUCCESS] バトルデモ完了！")
            print(f"[INFO] 総ログ数: {len(demo.logs)}")
        
    except KeyboardInterrupt:
        print("\n[INFO] 中断されました")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()