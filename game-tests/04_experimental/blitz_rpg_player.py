#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ブリッツRPGプレイヤー - 開始直後に特殊攻撃で一掃
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
import math

class BlitzRPGPlayer:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        
    def play_game(self):
        # ゲームを開く
        game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
        self.driver.get(f"file:///{game_path}")
        time.sleep(0.5)  # 最小限の待機
        
        print("\n=== ブリッツ作戦開始 ===")
        
        # 即座に特殊攻撃！
        print("開幕特殊攻撃！")
        self.driver.execute_script("""
            // MPを最大にして特殊攻撃
            game.player.mp = game.player.maxMp;
            specialAttack();
        """)
        time.sleep(0.5)
        
        # 状態確認
        state = self.driver.execute_script("""
            return {
                hp: game.player.hp,
                mp: game.player.mp,
                enemies: game.enemies.length,
                projectiles: game.projectiles.length
            };
        """)
        
        print(f"特殊攻撃後: HP={state['hp']}, MP={state['mp']}, 敵={state['enemies']}, 弾={state['projectiles']}")
        
        # 続けて移動しながら戦う
        print("\n通常戦闘開始...")
        start_time = time.time()
        last_score = 0
        
        for _ in range(300):  # 約15秒
            # 状態取得
            state = self.driver.execute_script("""
                const enemies = game.enemies.map(e => ({
                    x: e.x + e.width/2,
                    y: e.y + e.height/2,
                    dist: Math.sqrt(
                        Math.pow(e.x - game.player.x, 2) + 
                        Math.pow(e.y - game.player.y, 2)
                    )
                })).sort((a, b) => a.dist - b.dist);
                
                return {
                    px: game.player.x,
                    py: game.player.y,
                    hp: game.player.hp,
                    mp: game.player.mp,
                    score: game.player.score,
                    enemies: enemies.slice(0, 3),  // 近い3体
                    canAttack: game.player.attackCooldown <= 0
                };
            """)
            
            # スコア更新
            if state['score'] > last_score:
                print(f"スコア: {state['score']}")
                last_score = state['score']
                
            # HP確認
            if state['hp'] <= 0:
                print("ゲームオーバー！")
                break
                
            # 敵がいる場合
            if state['enemies']:
                nearest = state['enemies'][0]
                
                # 移動と攻撃
                dx = nearest['x'] - state['px']
                dy = nearest['y'] - state['py']
                
                if nearest['dist'] < 100:
                    # 近すぎる - 逃げる
                    escape_x = -dx / abs(dx) if dx != 0 else random.choice([-1, 1])
                    escape_y = -dy / abs(dy) if dy != 0 else random.choice([-1, 1])
                    
                    keys = []
                    if escape_x > 0: keys.append('d')
                    else: keys.append('a')
                    if escape_y > 0: keys.append('s')
                    else: keys.append('w')
                    
                    for key in keys:
                        self.driver.execute_script(f"game.keys['{key}'] = true;")
                    time.sleep(0.1)
                    for key in keys:
                        self.driver.execute_script(f"game.keys['{key}'] = false;")
                        
                elif nearest['dist'] < 300:
                    # 攻撃範囲
                    if abs(dx) > abs(dy):
                        facing = 'd' if dx > 0 else 'a'
                    else:
                        facing = 's' if dy > 0 else 'w'
                        
                    # 向きを変えて攻撃
                    self.driver.execute_script(f"game.keys['{facing}'] = true;")
                    time.sleep(0.02)
                    self.driver.execute_script(f"game.keys['{facing}'] = false;")
                    
                    if state['canAttack']:
                        self.driver.execute_script("playerAttack();")
                        
                # MP回復したら特殊攻撃
                if state['mp'] >= 30 and len(state['enemies']) >= 2:
                    self.driver.execute_script("specialAttack();")
                    print("追加特殊攻撃！")
                    
            time.sleep(0.05)
            
        # 最終結果
        final = self.driver.execute_script("""
            return {
                hp: game.player.hp,
                score: game.player.score,
                kills: game.player.score / 10
            };
        """)
        
        print(f"\n=== 最終結果 ===")
        print(f"スコア: {final['score']}")
        print(f"撃破数: {int(final['kills'])}体")
        print(f"HP: {final['hp']}/100")
        print(f"生存時間: {time.time() - start_time:.1f}秒")
        
        return final['score']

def main():
    print("=== ブリッツRPGプレイヤー ===")
    print("開幕特殊攻撃で先制を取ります\n")
    
    player = BlitzRPGPlayer()
    
    try:
        player.setup_driver()
        
        # 3回プレイ
        scores = []
        for i in range(3):
            print(f"\n--- ラウンド {i+1}/3 ---")
            score = player.play_game()
            scores.append(score)
            
            if i < 2:
                print("\n次のラウンドまで3秒...")
                time.sleep(3)
                
        print(f"\n総合結果: {scores}")
        print(f"平均スコア: {sum(scores)/3:.1f}")
        
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        if player.driver:
            player.driver.quit()

if __name__ == "__main__":
    main()