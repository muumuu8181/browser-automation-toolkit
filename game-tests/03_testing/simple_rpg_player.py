#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルRPGプレイヤー - 1回プレイしてブラウザを開いたままにする
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
import math

class SimpleRPGPlayer:
    def __init__(self):
        self.driver = None
        self.last_attack_time = 0
        self.attack_cooldown = 0.25
        
    def setup_driver(self):
        """ブラウザ起動"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        
    def play_game(self, duration=45):
        """ゲームをプレイ"""
        # ゲームを開く
        game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
        self.driver.get(f"file:///{game_path}")
        time.sleep(2)
        
        # キャンバスにフォーカス
        canvas = self.driver.find_element(By.ID, "gameCanvas")
        canvas.click()
        
        print("\n=== ゲーム開始 ===")
        print("45秒間自動プレイします...\n")
        
        start_time = time.time()
        kills = 0
        last_score = 0
        
        print("スコア: ", end="", flush=True)
        
        while time.time() - start_time < duration:
            # ゲーム状態を取得
            state = self.driver.execute_script("""
                const enemies = game.enemies.map(e => ({
                    x: e.x + e.width/2,
                    y: e.y + e.height/2
                }));
                
                return {
                    player: {
                        x: game.player.x + 16,
                        y: game.player.y + 16,
                        hp: game.player.hp,
                        mp: game.player.mp,
                        score: game.player.score
                    },
                    enemies: enemies
                };
            """)
            
            player = state['player']
            enemies = state['enemies']
            
            # スコア更新を表示
            if player['score'] > last_score:
                print(f"{player['score']} ", end="", flush=True)
                kills = player['score'] // 10
                last_score = player['score']
            
            # HPが0なら終了
            if player['hp'] <= 0:
                print("\n\nゲームオーバー！")
                break
                
            # 最も近い敵を見つける
            if enemies:
                nearest = min(enemies, key=lambda e: 
                    math.sqrt((e['x']-player['x'])**2 + (e['y']-player['y'])**2))
                dx = nearest['x'] - player['x']
                dy = nearest['y'] - player['y']
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 300:
                    # 敵の方向を向いて攻撃
                    if abs(dx) > abs(dy):
                        direction = 'd' if dx > 0 else 'a'
                    else:
                        direction = 's' if dy > 0 else 'w'
                    
                    # 短く方向転換
                    self.driver.execute_script(f"game.keys['{direction}'] = true;")
                    time.sleep(0.05)
                    self.driver.execute_script(f"game.keys['{direction}'] = false;")
                    
                    # 攻撃
                    if time.time() - self.last_attack_time > self.attack_cooldown:
                        self.driver.execute_script("if(game.player.attackCooldown <= 0) playerAttack();")
                        self.last_attack_time = time.time()
                        
                    # たまに特殊攻撃
                    if player['mp'] >= 30 and len(enemies) >= 3:
                        if random.random() < 0.1:
                            self.driver.execute_script("if(game.player.mp >= 20) specialAttack();")
                            print("*特殊* ", end="", flush=True)
                else:
                    # 敵に接近
                    if abs(dx) > abs(dy):
                        direction = 'd' if dx > 0 else 'a'
                    else:
                        direction = 's' if dy > 0 else 'w'
                    
                    self.driver.execute_script(f"game.keys['{direction}'] = true;")
                    time.sleep(0.2)
                    self.driver.execute_script(f"game.keys['{direction}'] = false;")
            else:
                # 探索
                direction = random.choice(['w', 'a', 's', 'd'])
                self.driver.execute_script(f"game.keys['{direction}'] = true;")
                time.sleep(0.3)
                self.driver.execute_script(f"game.keys['{direction}'] = false;")
                
            time.sleep(0.05)
            
        # 最終結果
        final_state = self.driver.execute_script("return {hp: game.player.hp, mp: game.player.mp, score: game.player.score};")
        
        print(f"\n\n=== ゲーム終了 ===")
        print(f"最終スコア: {final_state['score']}")
        print(f"撃破数: {final_state['score'] // 10} 体")
        print(f"最終HP: {final_state['hp']}/100")
        print(f"最終MP: {final_state['mp']}/50")
        
        return final_state['score']

def main():
    print("=== シンプルRPGプレイヤー ===")
    print("1回プレイしてブラウザを開いたままにします\n")
    
    player = SimpleRPGPlayer()
    
    try:
        player.setup_driver()
        score = player.play_game(duration=45)
        
        print("\n\nブラウザは開いたままです")
        print("画面を確認してください")
        print("\n終了するには Enter キーを押してください...")
        input()
        
    except Exception as e:
        print(f"\nエラー: {e}")
    finally:
        if player.driver:
            player.driver.quit()
            print("ブラウザを閉じました")

if __name__ == "__main__":
    main()