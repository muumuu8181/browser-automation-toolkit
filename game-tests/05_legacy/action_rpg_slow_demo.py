#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アクションRPG戦闘デモ - ゆっくり確実に動くバージョン
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random

class ActionRPGSlowDemo:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """ブラウザ起動"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        print("[INFO] アクションRPGデモ（ゆっくり版）開始！")
        
    def show_battle(self):
        """確実に動きが見えるバトルデモ"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\action_rpg.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(3)
            
            print("\n=== アクションRPGバトル（動きが見える版）===")
            print("[INFO] ゆっくり確実に操作します\n")
            
            body = self.driver.find_element(By.TAG_NAME, "body")
            canvas = self.driver.find_element(By.TAG_NAME, "canvas")
            
            # ゲーム画面にフォーカス
            canvas.click()
            time.sleep(1)
            
            # デモ1: 四角形移動パターン
            print("[DEMO 1] 四角形に移動しながら攻撃")
            print("大きく四角を描くように移動します")
            time.sleep(1)
            
            # 右上へ
            print("  → 右上へ移動...")
            for _ in range(10):
                body.send_keys(Keys.ARROW_RIGHT)
                time.sleep(0.1)
            for _ in range(8):
                body.send_keys(Keys.ARROW_UP)
                time.sleep(0.1)
            body.send_keys(Keys.SPACE)
            print("     攻撃！")
            time.sleep(0.5)
            
            # 左上へ
            print("  → 左上へ移動...")
            for _ in range(20):
                body.send_keys(Keys.ARROW_LEFT)
                time.sleep(0.1)
            body.send_keys(Keys.SPACE)
            print("     攻撃！")
            time.sleep(0.5)
            
            # 左下へ
            print("  → 左下へ移動...")
            for _ in range(16):
                body.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.1)
            body.send_keys(Keys.SPACE)
            print("     攻撃！")
            time.sleep(0.5)
            
            # 右下へ
            print("  → 右下へ移動...")
            for _ in range(20):
                body.send_keys(Keys.ARROW_RIGHT)
                time.sleep(0.1)
            body.send_keys(Keys.SPACE)
            print("     攻撃！")
            time.sleep(0.5)
            
            # 中央へ戻る
            print("  → 中央へ戻る...")
            for _ in range(10):
                body.send_keys(Keys.ARROW_LEFT)
                time.sleep(0.1)
            for _ in range(8):
                body.send_keys(Keys.ARROW_UP)
                time.sleep(0.1)
            
            # デモ2: 回転攻撃
            print("\n[DEMO 2] 回転しながら連続攻撃")
            time.sleep(1)
            
            directions = [Keys.ARROW_UP, Keys.ARROW_RIGHT, Keys.ARROW_DOWN, Keys.ARROW_LEFT]
            for i in range(3):  # 3周
                print(f"  回転 {i+1}/3")
                for direction in directions:
                    body.send_keys(direction)
                    time.sleep(0.2)
                    body.send_keys(Keys.SPACE)
                    time.sleep(0.2)
            
            # デモ3: 特殊攻撃
            print("\n[DEMO 3] 特殊攻撃デモ")
            print("  → MPを確認して特殊攻撃！")
            time.sleep(1)
            
            # 現在の状態を確認
            status = self.driver.execute_script("""
                return {
                    mp: game.player.mp,
                    hp: game.player.hp,
                    x: Math.round(game.player.x),
                    y: Math.round(game.player.y)
                };
            """)
            print(f"     現在位置: ({status['x']}, {status['y']})")
            print(f"     HP: {status['hp']}, MP: {status['mp']}")
            
            body.send_keys("E")
            print("     特殊攻撃発動！")
            time.sleep(2)
            
            # デモ4: ジグザグ回避
            print("\n[DEMO 4] ジグザグ回避しながら戦闘")
            time.sleep(1)
            
            for i in range(5):
                print(f"  ジグザグ {i+1}/5")
                # 右上
                body.send_keys(Keys.ARROW_RIGHT)
                time.sleep(0.1)
                body.send_keys(Keys.ARROW_UP)
                time.sleep(0.1)
                body.send_keys(Keys.SPACE)
                
                # 右下
                body.send_keys(Keys.ARROW_RIGHT)
                time.sleep(0.1)
                body.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.1)
                body.send_keys(Keys.SPACE)
                time.sleep(0.3)
            
            # デモ5: ダッシュ攻撃
            print("\n[DEMO 5] ダッシュ攻撃")
            print("  → Shiftを押しながら高速移動！")
            time.sleep(1)
            
            # ActionChainsを使用してキーを押し続ける
            actions = ActionChains(self.driver)
            
            # 右にダッシュ
            print("     右へダッシュ！")
            actions.key_down(Keys.SHIFT).send_keys(Keys.ARROW_RIGHT * 5).key_up(Keys.SHIFT).perform()
            time.sleep(0.5)
            body.send_keys(Keys.SPACE)
            
            # 左にダッシュ
            print("     左へダッシュ！")
            actions.key_down(Keys.SHIFT).send_keys(Keys.ARROW_LEFT * 5).key_up(Keys.SHIFT).perform()
            time.sleep(0.5)
            body.send_keys(Keys.SPACE)
            
            # 最終確認
            time.sleep(2)
            final_status = self.driver.execute_script("""
                return {
                    hp: game.player.hp,
                    mp: game.player.mp,
                    level: game.player.level,
                    score: game.player.score,
                    enemies: game.enemies.length,
                    x: Math.round(game.player.x),
                    y: Math.round(game.player.y)
                };
            """)
            
            print("\n=== 戦闘結果 ===")
            print(f"最終位置: ({final_status['x']}, {final_status['y']})")
            print(f"HP: {final_status['hp']}/100")
            print(f"MP: {final_status['mp']}/50")
            print(f"レベル: {final_status['level']}")
            print(f"スコア: {final_status['score']}")
            print(f"残存敵: {final_status['enemies']}")
            
            # 動きを確認するため追加の移動
            print("\n[BONUS] 最後に大きく動いて位置を確認")
            
            # 画面の端まで移動
            print("  → 画面右端へ...")
            for _ in range(30):
                body.send_keys(Keys.ARROW_RIGHT)
                time.sleep(0.05)
            
            print("  → 画面上端へ...")
            for _ in range(20):
                body.send_keys(Keys.ARROW_UP)
                time.sleep(0.05)
                
            print("  → 画面左端へ...")
            for _ in range(30):
                body.send_keys(Keys.ARROW_LEFT)
                time.sleep(0.05)
                
            print("  → 画面下端へ...")
            for _ in range(20):
                body.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.05)
            
            # 最終位置
            final_pos = self.driver.execute_script("""
                return {x: Math.round(game.player.x), y: Math.round(game.player.y)};
            """)
            print(f"\n最終確認位置: ({final_pos['x']}, {final_pos['y']})")
            
            # スクリーンショット
            self.driver.save_screenshot("action_rpg_slow_demo.png")
            print("\n[INFO] スクリーンショット保存: action_rpg_slow_demo.png")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] デモ中にエラー: {str(e)}")
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(5)
            self.driver.quit()
            print("[INFO] デモ終了")

def main():
    print("=== アクションRPG ゆっくり戦闘デモ ===\n")
    print("特徴:")
    print("- 動きが確実に見えるスピード")
    print("- 各アクション間に適切な待機時間")
    print("- 位置情報の確認")
    print("- ActionChainsでキー長押し操作\n")
    
    demo = ActionRPGSlowDemo()
    
    try:
        demo.setup_driver()
        demo.show_battle()
        
    except KeyboardInterrupt:
        print("\n[INFO] 中断されました")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()