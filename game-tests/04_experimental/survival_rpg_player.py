#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サバイバルRPGプレイヤー - 開始直後から回避行動を取る
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
import math

class SurvivalRPGPlayer:
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
        
    def emergency_escape(self):
        """緊急回避 - 開始直後に実行"""
        print("緊急回避開始！")
        
        # 右上に全力で逃げる
        self.driver.execute_script("""
            game.keys['d'] = true;
            game.keys['D'] = true;
            game.keys['ArrowRight'] = true;
            game.keys['w'] = true;
            game.keys['W'] = true;
            game.keys['ArrowUp'] = true;
        """)
        
        time.sleep(1.5)  # 1.5秒間逃げる
        
        # キーを離す
        self.driver.execute_script("""
            game.keys['d'] = false;
            game.keys['D'] = false;
            game.keys['ArrowRight'] = false;
            game.keys['w'] = false;
            game.keys['W'] = false;
            game.keys['ArrowUp'] = false;
        """)
        
        print("緊急回避完了！")
        
    def find_safe_direction(self, player, enemies):
        """最も安全な方向を見つける"""
        if not enemies:
            return random.choice(['w', 'a', 's', 'd'])
            
        # 各方向の危険度を計算
        directions = {
            'w': {'x': 0, 'y': -1, 'danger': 0},  # 上
            's': {'x': 0, 'y': 1, 'danger': 0},   # 下
            'a': {'x': -1, 'y': 0, 'danger': 0},  # 左
            'd': {'x': 1, 'y': 0, 'danger': 0}    # 右
        }
        
        # 各敵からの脅威を計算
        for enemy in enemies:
            dx = enemy['x'] - player['x']
            dy = enemy['y'] - player['y']
            distance = math.sqrt(dx*dx + dy*dy) + 1
            
            # 近い敵ほど危険
            threat = 1000 / distance
            
            # 各方向への危険度を加算
            if dx > 0:  # 敵が右にいる
                directions['d']['danger'] += threat
                directions['a']['danger'] -= threat * 0.5  # 左は安全
            else:  # 敵が左にいる
                directions['a']['danger'] += threat
                directions['d']['danger'] -= threat * 0.5  # 右は安全
                
            if dy > 0:  # 敵が下にいる
                directions['s']['danger'] += threat
                directions['w']['danger'] -= threat * 0.5  # 上は安全
            else:  # 敵が上にいる
                directions['w']['danger'] += threat
                directions['s']['danger'] -= threat * 0.5  # 下は安全
        
        # 最も安全な方向を選択
        safest = min(directions.items(), key=lambda x: x[1]['danger'])
        return safest[0]
        
    def play_game(self, duration=45):
        """ゲームをプレイ"""
        # ゲームを開く
        game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
        self.driver.get(f"file:///{game_path}")
        time.sleep(1)  # 読み込み待機を短縮
        
        # キャンバスにフォーカス
        canvas = self.driver.find_element(By.ID, "gameCanvas")
        canvas.click()
        
        print("\n=== サバイバルモード開始 ===")
        
        # 即座に緊急回避！
        self.emergency_escape()
        
        # 現在の状態を確認
        state = self.driver.execute_script("""
            return {
                hp: game.player.hp,
                x: game.player.x,
                y: game.player.y
            };
        """)
        print(f"回避後の状態: HP={state['hp']}, 位置=({state['x']}, {state['y']})")
        
        if state['hp'] <= 0:
            print("緊急回避が間に合いませんでした...")
            return 0
            
        # 通常のゲームプレイ
        print("\n通常プレイ開始...")
        start_time = time.time()
        last_score = 0
        
        print("スコア: ", end="", flush=True)
        
        while time.time() - start_time < duration:
            # ゲーム状態を取得
            state = self.driver.execute_script("""
                const enemies = game.enemies.map(e => ({
                    x: e.x + e.width/2,
                    y: e.y + e.height/2,
                    distance: Math.sqrt(
                        Math.pow(e.x - game.player.x, 2) + 
                        Math.pow(e.y - game.player.y, 2)
                    )
                })).sort((a, b) => a.distance - b.distance);
                
                return {
                    player: {
                        x: game.player.x + 16,
                        y: game.player.y + 16,
                        hp: game.player.hp,
                        mp: game.player.mp,
                        score: game.player.score
                    },
                    enemies: enemies,
                    nearestDistance: enemies.length > 0 ? enemies[0].distance : 999
                };
            """)
            
            player = state['player']
            enemies = state['enemies']
            
            # スコア更新
            if player['score'] > last_score:
                print(f"{player['score']} ", end="", flush=True)
                last_score = player['score']
            
            # HPが0なら終了
            if player['hp'] <= 0:
                print("\n\nゲームオーバー！")
                break
                
            # 危機的状況の判定
            if state['nearestDistance'] < 50:
                # 超近距離！回避優先
                safe_dir = self.find_safe_direction(player, enemies)
                self.driver.execute_script(f"""
                    game.keys['{safe_dir}'] = true;
                """)
                time.sleep(0.1)
                self.driver.execute_script(f"""
                    game.keys['{safe_dir}'] = false;
                """)
                
            elif state['nearestDistance'] < 200:
                # 攻撃可能距離
                if enemies:
                    nearest = enemies[0]
                    dx = nearest['x'] - player['x']
                    dy = nearest['y'] - player['y']
                    
                    # 敵の方を向く
                    if abs(dx) > abs(dy):
                        direction = 'd' if dx > 0 else 'a'
                    else:
                        direction = 's' if dy > 0 else 'w'
                    
                    # 方向転換
                    self.driver.execute_script(f"game.keys['{direction}'] = true;")
                    time.sleep(0.03)
                    self.driver.execute_script(f"game.keys['{direction}'] = false;")
                    
                    # 攻撃
                    if time.time() - self.last_attack_time > self.attack_cooldown:
                        self.driver.execute_script("if(game.player.attackCooldown <= 0) playerAttack();")
                        self.last_attack_time = time.time()
                        
                    # HP低下時は回避も混ぜる
                    if player['hp'] < 50:
                        safe_dir = self.find_safe_direction(player, enemies)
                        self.driver.execute_script(f"game.keys['{safe_dir}'] = true;")
                        time.sleep(0.05)
                        self.driver.execute_script(f"game.keys['{safe_dir}'] = false;")
                        
            else:
                # 敵が遠い - 探索
                direction = random.choice(['w', 'a', 's', 'd'])
                self.driver.execute_script(f"game.keys['{direction}'] = true;")
                time.sleep(0.2)
                self.driver.execute_script(f"game.keys['{direction}'] = false;")
                
            # 特殊攻撃
            if player['mp'] >= 30 and len(enemies) >= 3:
                if random.random() < 0.15:
                    self.driver.execute_script("if(game.player.mp >= 20) specialAttack();")
                    print("*特殊* ", end="", flush=True)
                    
            time.sleep(0.05)
            
        # 最終結果
        final_state = self.driver.execute_script("""
            return {
                hp: game.player.hp, 
                mp: game.player.mp, 
                score: game.player.score,
                x: game.player.x,
                y: game.player.y
            };
        """)
        
        print(f"\n\n=== ゲーム終了 ===")
        print(f"最終スコア: {final_state['score']}")
        print(f"撃破数: {final_state['score'] // 10} 体")
        print(f"最終HP: {final_state['hp']}/100")
        print(f"最終位置: ({final_state['x']}, {final_state['y']})")
        print(f"生存時間: {time.time() - start_time:.1f}秒")
        
        return final_state['score']

def main():
    print("=== サバイバルRPGプレイヤー ===")
    print("開始直後の危険を回避します\n")
    
    player = SurvivalRPGPlayer()
    
    try:
        player.setup_driver()
        score = player.play_game(duration=45)
        
        print("\nブラウザは開いたままです")
        print("終了するには Enter キーを押してください...")
        input()
        
    except Exception as e:
        print(f"\nエラー: {e}")
    finally:
        if player.driver:
            player.driver.quit()

if __name__ == "__main__":
    main()