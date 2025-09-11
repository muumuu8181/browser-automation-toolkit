#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動作確認済みRPGプレイヤー - 攻撃クールダウンを考慮
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
import math
from datetime import datetime

class WorkingRPGPlayer:
    def __init__(self):
        self.driver = None
        self.last_attack_time = 0
        self.attack_cooldown = 0.25  # 攻撃間隔（秒）
        
    def setup_driver(self):
        """ブラウザ起動"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        
    def move(self, direction, duration=0.2):
        """移動"""
        key_map = {
            'up': ['w', 'W', 'ArrowUp'],
            'down': ['s', 'S', 'ArrowDown'],
            'left': ['a', 'A', 'ArrowLeft'],
            'right': ['d', 'D', 'ArrowRight']
        }
        
        keys = key_map[direction]
        for key in keys:
            self.driver.execute_script(f"game.keys['{key}'] = true;")
        time.sleep(duration)
        for key in keys:
            self.driver.execute_script(f"game.keys['{key}'] = false;")
            
    def attack(self):
        """通常攻撃（クールダウンを考慮）"""
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
            
        # JavaScriptで直接攻撃関数を呼ぶ
        can_attack = self.driver.execute_script("""
            if (game.player.attackCooldown <= 0) {
                playerAttack();
                return true;
            }
            return false;
        """)
        
        if can_attack:
            self.last_attack_time = current_time
            return True
        return False
        
    def special_attack(self):
        """特殊攻撃"""
        success = self.driver.execute_script("""
            if (game.player.mp >= 20) {
                specialAttack();
                return true;
            }
            return false;
        """)
        return success
        
    def get_game_state(self):
        """ゲーム状態を取得"""
        return self.driver.execute_script("""
            const enemies = game.enemies.map(e => ({
                x: e.x + e.width/2,
                y: e.y + e.height/2,
                hp: e.hp
            }));
            
            return {
                player: {
                    x: game.player.x + 16,
                    y: game.player.y + 16,
                    hp: game.player.hp,
                    mp: game.player.mp,
                    score: game.player.score,
                    facing: game.player.facing,
                    attackCooldown: game.player.attackCooldown
                },
                enemies: enemies,
                projectiles: game.projectiles.length
            };
        """)
        
    def find_nearest_enemy(self, player, enemies):
        """最も近い敵を見つける"""
        if not enemies:
            return None, float('inf')
            
        nearest = None
        min_dist = float('inf')
        
        for enemy in enemies:
            dx = enemy['x'] - player['x']
            dy = enemy['y'] - player['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
                
        return nearest, min_dist
        
    def get_direction_to_target(self, player, target):
        """ターゲットへの方向を計算"""
        dx = target['x'] - player['x']
        dy = target['y'] - player['y']
        
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'
            
    def play_game(self, duration=60):
        """ゲームをプレイ"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(2)
            
            # キャンバスにフォーカス
            canvas = self.driver.find_element(By.ID, "gameCanvas")
            canvas.click()
            
            print("\n=== ゲームプレイ開始 ===")
            
            start_time = time.time()
            kills = 0
            last_score = 0
            actions = 0
            attacks = 0
            hits = 0
            
            while time.time() - start_time < duration:
                # ゲーム状態を取得
                game_state = self.get_game_state()
                player = game_state['player']
                enemies = game_state['enemies']
                
                # スコアからキル数を計算
                if player['score'] > last_score:
                    new_kills = (player['score'] - last_score) // 10
                    kills += new_kills
                    last_score = player['score']
                    hits += new_kills
                    print(f"  敵撃破！ 合計{kills}体 (スコア: {player['score']})")
                
                # HPが0なら終了
                if player['hp'] <= 0:
                    print("  ゲームオーバー！")
                    break
                    
                # 最も近い敵を見つける
                nearest, distance = self.find_nearest_enemy(player, enemies)
                
                if nearest and distance < 300:  # 攻撃範囲内
                    # 敵の方向を向く
                    direction = self.get_direction_to_target(player, nearest)
                    
                    # 短く方向を向く（向きだけ変える）
                    self.move(direction, 0.05)
                    
                    # 攻撃
                    if self.attack():
                        attacks += 1
                        if actions % 10 == 0:
                            print(f"  攻撃！ (合計: {attacks}回)")
                            
                    # たまに特殊攻撃
                    if player['mp'] >= 30 and len(enemies) >= 3 and random.random() < 0.1:
                        if self.special_attack():
                            print(f"  特殊攻撃発動！ (MP: {player['mp']})")
                            
                elif nearest:  # 敵が遠い
                    # 敵に向かって移動
                    direction = self.get_direction_to_target(player, nearest)
                    self.move(direction, 0.2)
                    
                else:  # 敵がいない
                    # ランダムに探索
                    direction = random.choice(['up', 'down', 'left', 'right'])
                    self.move(direction, 0.3)
                    
                actions += 1
                time.sleep(0.05)  # 短い待機
                
            # 結果表示
            final_state = self.get_game_state()
            play_time = time.time() - start_time
            
            print(f"\n=== プレイ結果 ===")
            print(f"プレイ時間: {play_time:.1f}秒")
            print(f"最終スコア: {final_state['player']['score']}")
            print(f"撃破数: {kills}体")
            print(f"最終HP: {final_state['player']['hp']}/100")
            print(f"最終MP: {final_state['player']['mp']}/50")
            print(f"攻撃回数: {attacks}回")
            print(f"命中率: {hits/attacks*100:.1f}%" if attacks > 0 else "命中率: N/A")
            print(f"残存敵数: {len(final_state['enemies'])}")
            
            # スクリーンショット
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver.save_screenshot(
                f"C:\\Users\\user\\Desktop\\work\\90_cc\\20250908\\browser-automation-toolkit\\results\\working_rpg_{timestamp}.png"
            )
            
            return final_state['player']['score']
            
        except Exception as e:
            print(f"[ERROR] プレイ中にエラー: {str(e)}")
            return 0
            
    def cleanup(self):
        if self.driver:
            time.sleep(3)
            self.driver.quit()

def main():
    print("=== 動作確認済みRPGプレイヤー ===")
    print("攻撃クールダウンを考慮した実装\n")
    
    scores = []
    
    for i in range(3):
        print(f"\n--- ラウンド {i+1}/3 ---")
        
        player = WorkingRPGPlayer()
        
        try:
            player.setup_driver()
            score = player.play_game(duration=45)
            scores.append(score)
            
        except KeyboardInterrupt:
            print("\n[INFO] 中断されました")
            break
        finally:
            player.cleanup()
            
        if i < 2:
            print("\n次のラウンドまで3秒待機...")
            time.sleep(3)
            
    # 総合結果
    if scores:
        print(f"\n=== 総合結果 ===")
        print(f"プレイ回数: {len(scores)}回")
        print(f"合計スコア: {sum(scores)}")
        print(f"平均スコア: {sum(scores)/len(scores):.1f}")
        print(f"最高スコア: {max(scores)}")
        print(f"最低スコア: {min(scores)}")

if __name__ == "__main__":
    main()