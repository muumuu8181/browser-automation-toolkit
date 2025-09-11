#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カスタム背景RPGゲームを自動プレイ
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
from datetime import datetime

class CustomBgRPGPlayer:
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
        print("[INFO] カスタム背景RPGゲーム起動！")
        
    def play_game(self):
        """ゲームを自動プレイ"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(2)
            
            print("\n=== ゲーム開始！ ===")
            print("[操作] 矢印キー/WASD: 移動, スペース: 攻撃, E: 特殊攻撃\n")
            
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # ゲームプレイ開始
            print("[PHASE 1] 移動と攻撃の基本操作")
            
            # 四方向に移動して攻撃
            directions = [
                (Keys.UP, "↑"),
                (Keys.RIGHT, "→"),
                (Keys.DOWN, "↓"),
                (Keys.LEFT, "←")
            ]
            
            for _ in range(3):
                for key, arrow in directions:
                    # より長く押し続ける
                    for _ in range(10):
                        body.send_keys(key)
                        time.sleep(0.05)
                    time.sleep(0.3)
                    body.send_keys(Keys.SPACE)
                    print(f"  {arrow} 移動して攻撃！")
                    time.sleep(0.5)
            
            print("\n[PHASE 2] 特殊攻撃でMP消費")
            time.sleep(1)
            
            # 特殊攻撃を使用
            for i in range(2):
                print(f"  特殊攻撃 {i+1} 発動！")
                body.send_keys("E")
                time.sleep(2)
            
            print("\n[PHASE 3] ランダム戦闘モード")
            
            # 30秒間ランダムに戦闘
            start_time = time.time()
            action_count = 0
            
            while time.time() - start_time < 30:
                # ランダムな行動を選択
                action_type = random.choice(["move", "attack", "special"])
                
                if action_type == "move":
                    # 移動（WASDキーを使用）
                    direction = random.choice([
                        ("w", "↑"),
                        ("s", "↓"),
                        ("a", "←"),
                        ("d", "→")
                    ])
                    # 複数回キーを送信して確実に移動
                    for _ in range(5):
                        body.send_keys(direction[0])
                        time.sleep(0.02)
                    print(f"  {direction[1]}移動!", end=" ", flush=True)
                    
                elif action_type == "attack":
                    body.send_keys(Keys.SPACE)
                    print(f"  攻撃!", end=" ", flush=True)
                    
                else:  # special
                    body.send_keys("e")
                    print(f"  特殊!", end=" ", flush=True)
                
                action_count += 1
                
                if action_count % 10 == 0:
                    print()  # 改行
                
                time.sleep(random.uniform(0.1, 0.3))
            
            print(f"\n\n[結果] {action_count}回の行動を実行！")
            
            # ゲーム状態を取得
            time.sleep(1)
            game_state = self.driver.execute_script("""
                return {
                    player: {
                        x: game.player.x,
                        y: game.player.y,
                        hp: game.player.hp,
                        mp: game.player.mp,
                        score: game.player.score
                    },
                    enemies: game.enemies.length,
                    projectiles: game.projectiles.length
                };
            """)
            
            print("\n=== 最終結果 ===")
            print(f"プレイヤー位置: X:{game_state['player']['x']}, Y:{game_state['player']['y']}")
            print(f"HP: {game_state['player']['hp']}/100")
            print(f"MP: {game_state['player']['mp']}/50")
            print(f"スコア: {game_state['player']['score']}")
            print(f"画面上の敵: {game_state['enemies']}")
            print(f"画面上の弾: {game_state['projectiles']}")
            
            # スクリーンショット保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"C:\\Users\\user\\Desktop\\work\\90_cc\\20250908\\browser-automation-toolkit\\results\\custom_bg_rpg_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"\n[INFO] スクリーンショット保存: {screenshot_path}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] ゲーム中にエラー: {str(e)}")
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(5)  # 結果を見るため
            self.driver.quit()
            print("[INFO] ゲーム終了")

def main():
    print("=== カスタム背景RPGゲーム自動プレイ ===\n")
    
    player = CustomBgRPGPlayer()
    
    try:
        player.setup_driver()
        player.play_game()
        
    except KeyboardInterrupt:
        print("\n[INFO] 中断されました")
    finally:
        player.cleanup()

if __name__ == "__main__":
    main()