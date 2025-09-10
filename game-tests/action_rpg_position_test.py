#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アクションRPG座標確認デモ - 移動が確実に見えるバージョン
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

class PositionTestDemo:
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
        print("[INFO] 座標確認デモ開始！")
        
    def test_movement(self):
        """移動と座標の確認"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\action_rpg.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(3)
            
            print("\n=== 座標確認テスト ===")
            print("画面上の座標表示を確認してください\n")
            
            canvas = self.driver.find_element(By.TAG_NAME, "canvas")
            body = self.driver.find_element(By.TAG_NAME, "body")
            canvas.click()  # フォーカス
            time.sleep(1)
            
            # 初期座標を取得
            pos = self.driver.execute_script("""
                return {x: game.player.x, y: game.player.y};
            """)
            print(f"初期座標: X:{pos['x']}, Y:{pos['y']}")
            
            # 座標表示要素を取得
            position_elem = self.driver.find_element(By.ID, "position")
            print(f"画面表示: {position_elem.text}\n")
            
            # テスト1: 右に移動
            print("[TEST 1] 右に移動 (→キー10回)")
            for i in range(10):
                body.send_keys(Keys.ARROW_RIGHT)
                time.sleep(0.2)
                if i % 2 == 0:
                    print(f"  {i+1}回目: {position_elem.text}")
            
            pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
            print(f"JavaScript確認: X:{pos['x']}, Y:{pos['y']}\n")
            
            # テスト2: 下に移動
            print("[TEST 2] 下に移動 (↓キー10回)")
            for i in range(10):
                body.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.2)
                if i % 2 == 0:
                    print(f"  {i+1}回目: {position_elem.text}")
            
            pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
            print(f"JavaScript確認: X:{pos['x']}, Y:{pos['y']}\n")
            
            # テスト3: 左に移動
            print("[TEST 3] 左に移動 (←キー10回)")
            for i in range(10):
                body.send_keys(Keys.ARROW_LEFT)
                time.sleep(0.2)
                if i % 2 == 0:
                    print(f"  {i+1}回目: {position_elem.text}")
            
            pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
            print(f"JavaScript確認: X:{pos['x']}, Y:{pos['y']}\n")
            
            # テスト4: 上に移動
            print("[TEST 4] 上に移動 (↑キー10回)")
            for i in range(10):
                body.send_keys(Keys.ARROW_UP)
                time.sleep(0.2)
                if i % 2 == 0:
                    print(f"  {i+1}回目: {position_elem.text}")
            
            pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
            print(f"JavaScript確認: X:{pos['x']}, Y:{pos['y']}\n")
            
            # テスト5: WASDキー
            print("[TEST 5] WASDキーテスト")
            keys = [('W', '上'), ('A', '左'), ('S', '下'), ('D', '右')]
            for key, direction in keys:
                print(f"  {key}キー ({direction})")
                for _ in range(5):
                    body.send_keys(key.lower())
                    time.sleep(0.1)
                print(f"    現在位置: {position_elem.text}")
            
            # デバッグパネルの内容を確認
            debug_panel = self.driver.find_element(By.ID, "debugPanel")
            print(f"\n[デバッグパネル]\n{debug_panel.text}\n")
            
            # コンソールログから移動ログを確認
            logs = self.driver.get_log('browser')
            move_logs = [log for log in logs if '移動:' in log.get('message', '')]
            
            print("[コンソールログの移動記録]")
            for log in move_logs[-10:]:  # 最新10件
                msg = log['message'].split('"')[1] if '"' in log['message'] else log['message']
                print(f"  {msg}")
            
            # 最終確認
            final_pos = self.driver.execute_script("""
                return {
                    x: Math.round(game.player.x),
                    y: Math.round(game.player.y),
                    speed: game.player.speed,
                    facing: game.player.facing
                };
            """)
            
            print(f"\n=== 最終状態 ===")
            print(f"座標: X:{final_pos['x']}, Y:{final_pos['y']}")
            print(f"速度: {final_pos['speed']}")
            print(f"向き: {final_pos['facing']}")
            print(f"画面表示: {position_elem.text}")
            
            # スクリーンショット
            self.driver.save_screenshot("action_rpg_position_test.png")
            print("\n[INFO] スクリーンショット保存: action_rpg_position_test.png")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] テスト中にエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(3)
            self.driver.quit()
            print("[INFO] テスト終了")

def main():
    print("=== アクションRPG 座標確認テスト ===\n")
    print("このテストで確認すること:")
    print("1. 画面上の座標表示が更新されるか")
    print("2. キー入力で実際に移動するか")
    print("3. JavaScriptの座標と画面表示が一致するか\n")
    
    demo = PositionTestDemo()
    
    try:
        demo.setup_driver()
        demo.test_movement()
        
    except KeyboardInterrupt:
        print("\n[INFO] 中断されました")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()