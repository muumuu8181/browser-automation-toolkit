#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スマートサバイバルRPG - 円運動で回避しながら戦う
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
import math

class SmartSurvivalRPG:
    def __init__(self):
        self.driver = None
        self.last_attack_time = 0
        self.attack_cooldown = 0.3
        self.movement_angle = 0  # 円運動用の角度
        
    def setup_driver(self):
        """ブラウザ起動"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        
    def circular_movement(self):
        """円運動で回避"""
        # 中心から一定距離を保ちながら円を描く
        center_x = 400
        center_y = 300
        radius = 200
        
        # 目標位置を計算
        target_x = center_x + radius * math.cos(self.movement_angle)
        target_y = center_y + radius * math.sin(self.movement_angle)
        
        # 現在位置を取得
        current = self.driver.execute_script("""
            return {x: game.player.x + 16, y: game.player.y + 16};
        """)
        
        # 目標への方向を計算
        dx = target_x - current['x']
        dy = target_y - current['y']
        
        # 移動方向を決定
        keys = []
        if abs(dx) > 20:
            if dx > 0:
                keys.extend(['d', 'D', 'ArrowRight'])
            else:
                keys.extend(['a', 'A', 'ArrowLeft'])
                
        if abs(dy) > 20:
            if dy > 0:
                keys.extend(['s', 'S', 'ArrowDown'])
            else:
                keys.extend(['w', 'W', 'ArrowUp'])
        
        # 移動実行
        if keys:
            for key in keys:
                self.driver.execute_script(f"game.keys['{key}'] = true;")
            time.sleep(0.1)
            for key in keys:
                self.driver.execute_script(f"game.keys['{key}'] = false;")
        
        # 角度を更新
        self.movement_angle += 0.1
        if self.movement_angle > 2 * math.pi:
            self.movement_angle -= 2 * math.pi
            
    def smart_attack(self, player, enemies):
        """賢い攻撃 - 移動しながら攻撃"""
        if not enemies or time.time() - self.last_attack_time < self.attack_cooldown:
            return
            
        # 最も近い敵を狙う
        nearest = min(enemies, key=lambda e: e['distance'])
        
        if nearest['distance'] < 250:
            # 敵の方を向く
            dx = nearest['x'] - player['x']
            dy = nearest['y'] - player['y']
            
            if abs(dx) > abs(dy):
                facing = 'right' if dx > 0 else 'left'
            else:
                facing = 'down' if dy > 0 else 'up'
            
            # 現在の向きと違う場合のみ方向転換
            if player.get('facing') != facing:
                key_map = {
                    'up': ['w', 'W', 'ArrowUp'],
                    'down': ['s', 'S', 'ArrowDown'],
                    'left': ['a', 'A', 'ArrowLeft'],
                    'right': ['d', 'D', 'ArrowRight']
                }
                keys = key_map[facing]
                for key in keys:
                    self.driver.execute_script(f"game.keys['{key}'] = true;")
                time.sleep(0.02)
                for key in keys:
                    self.driver.execute_script(f"game.keys['{key}'] = false;")
            
            # 攻撃
            self.driver.execute_script("if(game.player.attackCooldown <= 0) playerAttack();")
            self.last_attack_time = time.time()
            
    def play_game(self, duration=60):
        """ゲームをプレイ"""
        # ゲームを開く
        game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
        self.driver.get(f"file:///{game_path}")
        time.sleep(1)
        
        # キャンバスにフォーカス
        canvas = self.driver.find_element(By.ID, "gameCanvas")
        canvas.click()
        
        print("\n=== スマートサバイバルモード ===")
        print("円運動で回避しながら戦います\n")
        
        start_time = time.time()
        last_score = 0
        last_hp = 100
        phase = "initial"  # initial, combat, survival
        
        print("フェーズ: 初期回避")
        
        while time.time() - start_time < duration:
            # ゲーム状態を取得
            state = self.driver.execute_script("""
                const enemies = game.enemies.map(e => ({
                    x: e.x + e.width/2,
                    y: e.y + e.height/2,
                    distance: Math.sqrt(
                        Math.pow((e.x + e.width/2) - (game.player.x + 16), 2) + 
                        Math.pow((e.y + e.height/2) - (game.player.y + 16), 2)
                    )
                })).sort((a, b) => a.distance - b.distance);
                
                return {
                    player: {
                        x: game.player.x + 16,
                        y: game.player.y + 16,
                        hp: game.player.hp,
                        mp: game.player.mp,
                        score: game.player.score,
                        facing: game.player.facing
                    },
                    enemies: enemies,
                    projectiles: game.projectiles.length
                };
            """)
            
            player = state['player']
            enemies = state['enemies']
            
            # スコア更新
            if player['score'] > last_score:
                kills = (player['score'] - last_score) // 10
                print(f"\n撃破！ +{kills}体 (スコア: {player['score']})")
                last_score = player['score']
            
            # HP変化
            if player['hp'] < last_hp:
                damage = last_hp - player['hp']
                print(f"ダメージ受けた！ -{damage} (HP: {player['hp']})")
                last_hp = player['hp']
            
            # HPが0なら終了
            if player['hp'] <= 0:
                print("\nゲームオーバー！")
                break
                
            # フェーズ管理
            elapsed = time.time() - start_time
            if elapsed < 3:
                # 初期3秒は回避に専念
                self.circular_movement()
                
            elif elapsed < 5 and phase == "initial":
                phase = "combat"
                print("\nフェーズ: 戦闘開始")
                
            # 戦闘フェーズ
            if phase == "combat":
                # 円運動を継続
                self.circular_movement()
                
                # 攻撃
                self.smart_attack(player, enemies)
                
                # 特殊攻撃
                if player['mp'] >= 30 and len(enemies) >= 4:
                    if random.random() < 0.1:
                        self.driver.execute_script("if(game.player.mp >= 20) specialAttack();")
                        print("特殊攻撃発動！")
                        
                # HP危機的状況
                if player['hp'] < 30 and phase != "survival":
                    phase = "survival"
                    print("\nフェーズ: サバイバルモード！")
                    self.movement_angle += math.pi  # 反対側に移動
                    
            time.sleep(0.05)
            
        # 最終結果
        final_state = self.driver.execute_script("""
            return {
                hp: game.player.hp, 
                mp: game.player.mp, 
                score: game.player.score,
                x: game.player.x,
                y: game.player.y,
                enemies: game.enemies.length
            };
        """)
        
        play_time = time.time() - start_time
        
        print(f"\n=== 最終結果 ===")
        print(f"生存時間: {play_time:.1f}秒")
        print(f"最終スコア: {final_state['score']}")
        print(f"撃破数: {final_state['score'] // 10} 体")
        print(f"最終HP: {final_state['hp']}/100")
        print(f"最終MP: {final_state['mp']}/50")
        print(f"残存敵: {final_state['enemies']}体")
        
        # 評価
        if final_state['score'] >= 100:
            print("\n素晴らしい成績です！")
        elif final_state['score'] >= 50:
            print("\n良い成績です！")
        elif play_time >= 30:
            print("\nよく生き延びました！")
            
        return final_state['score']

def main():
    print("=== スマートサバイバルRPG ===")
    print("円運動回避戦術を使用します\n")
    
    player = SmartSurvivalRPG()
    
    try:
        player.setup_driver()
        score = player.play_game(duration=60)
        
        print("\n終了するには Enter キーを押してください...")
        input()
        
    except Exception as e:
        print(f"\nエラー: {e}")
    finally:
        if player.driver:
            player.driver.quit()

if __name__ == "__main__":
    main()