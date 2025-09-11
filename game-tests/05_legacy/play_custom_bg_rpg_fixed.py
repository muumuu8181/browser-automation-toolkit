#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カスタム背景RPGゲームを自動プレイ（修正版）
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
        
    def move_player(self, direction, duration=0.5):
        """プレイヤーを移動させる（修正版）"""
        key_map = {
            'up': ['w', 'W', 'ArrowUp'],
            'down': ['s', 'S', 'ArrowDown'],
            'left': ['a', 'A', 'ArrowLeft'],
            'right': ['d', 'D', 'ArrowRight']
        }
        
        keys = key_map.get(direction, [])
        
        # キーを押す
        for key in keys:
            self.driver.execute_script(f"game.keys['{key}'] = true;")
        
        time.sleep(duration)
        
        # キーを離す
        for key in keys:
            self.driver.execute_script(f"game.keys['{key}'] = false;")
            
    def attack(self):
        """通常攻撃"""
        self.driver.execute_script("game.keys[' '] = true;")
        time.sleep(0.1)
        self.driver.execute_script("game.keys[' '] = false;")
        
    def special_attack(self):
        """特殊攻撃"""
        self.driver.execute_script("game.keys['e'] = true; game.keys['E'] = true;")
        time.sleep(0.1)
        self.driver.execute_script("game.keys['e'] = false; game.keys['E'] = false;")
        
    def play_game(self):
        """ゲームを自動プレイ"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(2)
            
            print("\n=== ゲーム開始！ ===")
            print("[操作] 矢印キー/WASD: 移動, スペース: 攻撃, E: 特殊攻撃\n")
            
            # キャンバスにフォーカス
            canvas = self.driver.find_element(By.ID, "gameCanvas")
            canvas.click()
            
            # 初期位置を確認
            initial_state = self.driver.execute_script("""
                return {
                    x: game.player.x,
                    y: game.player.y,
                    hp: game.player.hp,
                    mp: game.player.mp
                };
            """)
            print(f"初期位置: X:{initial_state['x']}, Y:{initial_state['y']}")
            
            print("\n[PHASE 1] 移動テスト")
            
            # 大きく四角形を描くように移動
            movements = [
                ('right', 1.0, '→'),
                ('down', 1.0, '↓'),
                ('left', 1.0, '←'),
                ('up', 1.0, '↑')
            ]
            
            for direction, duration, arrow in movements:
                print(f"  {arrow} 方向へ移動中...")
                self.move_player(direction, duration)
                
                # 移動中に攻撃
                self.attack()
                time.sleep(0.3)
                
                # 現在位置を確認
                pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
                print(f"    現在位置: X:{pos['x']}, Y:{pos['y']}")
            
            print("\n[PHASE 2] 戦闘モード")
            
            # 特殊攻撃
            print("  特殊攻撃発動！")
            self.special_attack()
            time.sleep(1)
            
            # ジグザグ移動しながら戦闘
            print("  ジグザグ移動戦闘開始！")
            for _ in range(5):
                self.move_player('right', 0.3)
                self.attack()
                self.move_player('up', 0.3)
                self.attack()
                self.move_player('left', 0.3)
                self.attack()
                self.move_player('down', 0.3)
                self.attack()
            
            print("\n[PHASE 3] ランダム戦闘（20秒）")
            
            start_time = time.time()
            action_count = 0
            
            while time.time() - start_time < 20:
                action = random.choice(['move', 'attack', 'special'])
                
                if action == 'move':
                    direction = random.choice(['up', 'down', 'left', 'right'])
                    self.move_player(direction, random.uniform(0.2, 0.5))
                    print("移動", end=" ", flush=True)
                elif action == 'attack':
                    self.attack()
                    print("攻撃", end=" ", flush=True)
                else:
                    self.special_attack()
                    print("特殊", end=" ", flush=True)
                
                action_count += 1
                if action_count % 15 == 0:
                    print()  # 改行
                    
                time.sleep(0.1)
            
            print(f"\n\n[結果] {action_count}回の行動を実行！")
            
            # 最終結果を取得
            final_state = self.driver.execute_script("""
                return {
                    player: {
                        x: Math.round(game.player.x),
                        y: Math.round(game.player.y),
                        hp: game.player.hp,
                        mp: game.player.mp,
                        score: game.player.score
                    },
                    enemies: game.enemies.length,
                    projectiles: game.projectiles.length
                };
            """)
            
            print("\n=== 最終結果 ===")
            print(f"移動距離: X:{final_state['player']['x'] - initial_state['x']}, Y:{final_state['player']['y'] - initial_state['y']}")
            print(f"最終位置: X:{final_state['player']['x']}, Y:{final_state['player']['y']}")
            print(f"HP: {final_state['player']['hp']}/100")
            print(f"MP: {final_state['player']['mp']}/50")
            print(f"スコア: {final_state['player']['score']}")
            print(f"画面上の敵: {final_state['enemies']}")
            
            # スクリーンショット保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"C:\\Users\\user\\Desktop\\work\\90_cc\\20250908\\browser-automation-toolkit\\results\\custom_bg_rpg_fixed_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"\n[INFO] スクリーンショット保存: {screenshot_path}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] ゲーム中にエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(5)  # 結果を見るため
            self.driver.quit()
            print("[INFO] ゲーム終了")

def main():
    print("=== カスタム背景RPGゲーム自動プレイ（修正版） ===\n")
    print("修正内容: ゲーム内部のキー状態を直接操作して確実に移動\n")
    
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