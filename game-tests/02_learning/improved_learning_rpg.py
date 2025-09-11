#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改良版学習型RPGプレイヤー - より賢く、より強く
"""

import json
import os
import time
import random
import math
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class ImprovedLearningRPG:
    def __init__(self):
        self.driver = None
        self.log_file = "improved_rpg_log.json"
        self.strategy_file = "improved_rpg_strategy.json"
        self.play_history = []
        self.current_strategy = self.load_strategy()
        self.episode = 0
        
    def load_strategy(self):
        """戦略をロード"""
        if os.path.exists(self.strategy_file):
            with open(self.strategy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # より賢い初期戦略
            return {
                "episode": 0,
                "best_score": 0,
                "total_kills": 0,
                "attack_frequency": 0.4,    # 攻撃頻度を上げる
                "move_frequency": 0.5,       # バランス型
                "special_frequency": 0.1,    # 特殊攻撃
                "preferred_distance": 150,   # 中距離戦闘
                "dodge_threshold": 80,       # 回避距離
                "attack_accuracy": 0.7,      # 攻撃精度
                "movement_speed": 0.15,      # 移動時間
                "reaction_time": 0.05        # 反応速度
            }
    
    def setup_driver(self):
        """ブラウザ起動"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        
    def get_game_state(self):
        """ゲーム状態を取得"""
        return self.driver.execute_script("""
            const enemies = game.enemies.map(e => ({
                x: e.x + e.width/2,
                y: e.y + e.height/2,
                hp: e.hp,
                speed: e.speed || 1
            }));
            
            // プレイヤーの向きから攻撃方向を計算
            let aimX = game.player.x + 16;
            let aimY = game.player.y + 16;
            
            switch(game.player.facing) {
                case 'up': aimY -= 100; break;
                case 'down': aimY += 100; break;
                case 'left': aimX -= 100; break;
                case 'right': aimX += 100; break;
            }
            
            return {
                player: {
                    x: game.player.x + 16,
                    y: game.player.y + 16,
                    hp: game.player.hp,
                    maxHp: game.player.maxHp,
                    mp: game.player.mp,
                    maxMp: game.player.maxMp,
                    score: game.player.score,
                    facing: game.player.facing,
                    aimX: aimX,
                    aimY: aimY
                },
                enemies: enemies,
                projectiles: game.projectiles.length,
                frameCount: game.frameCount
            };
        """)
        
    def aim_at_enemy(self, player, enemy):
        """敵の方向を向く"""
        dx = enemy['x'] - player['x']
        dy = enemy['y'] - player['y']
        
        # 方向を決定
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'
            
    def predict_enemy_position(self, enemy, player, time_ahead=0.5):
        """敵の未来位置を予測"""
        dx = player['x'] - enemy['x']
        dy = player['y'] - enemy['y']
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            # 敵の移動ベクトル
            move_x = (dx / dist) * enemy.get('speed', 1) * time_ahead * 60
            move_y = (dy / dist) * enemy.get('speed', 1) * time_ahead * 60
            
            return {
                'x': enemy['x'] + move_x,
                'y': enemy['y'] + move_y
            }
        return enemy
        
    def execute_aimed_attack(self, target_direction):
        """狙いをつけて攻撃"""
        # まず向きを変える
        key_map = {
            'up': ['w', 'W', 'ArrowUp'],
            'down': ['s', 'S', 'ArrowDown'],
            'left': ['a', 'A', 'ArrowLeft'],
            'right': ['d', 'D', 'ArrowRight']
        }
        
        # 短く方向キーを押して向きだけ変える
        keys = key_map[target_direction]
        for key in keys:
            self.driver.execute_script(f"game.keys['{key}'] = true;")
        time.sleep(0.02)
        for key in keys:
            self.driver.execute_script(f"game.keys['{key}'] = false;")
        
        time.sleep(0.02)
        
        # 攻撃
        self.driver.execute_script("game.keys[' '] = true;")
        time.sleep(0.05)
        self.driver.execute_script("game.keys[' '] = false;")
        
    def smart_move(self, direction, duration):
        """賢い移動（壁を避ける）"""
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
            
    def dodge_enemies(self, player, enemies):
        """複数の敵から回避する方向を計算"""
        if not enemies:
            return random.choice(['up', 'down', 'left', 'right'])
            
        # 各方向への危険度を計算
        danger = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        
        for enemy in enemies[:5]:  # 最も近い5体を考慮
            dx = enemy['x'] - player['x']
            dy = enemy['y'] - player['y']
            dist = math.sqrt(dx*dx + dy*dy) + 1
            
            # 距離が近いほど危険度が高い
            threat = 100 / dist
            
            if dx > 0: danger['right'] += threat
            else: danger['left'] += threat
            
            if dy > 0: danger['down'] += threat
            else: danger['up'] += threat
            
        # 最も安全な方向を選択
        safest = min(danger.items(), key=lambda x: x[1])
        return safest[0]
        
    def play_episode(self, duration=60):
        """1エピソードをプレイ（改良版）"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(2)
            
            # キャンバスにフォーカス
            canvas = self.driver.find_element(By.ID, "gameCanvas")
            canvas.click()
            
            self.episode = self.current_strategy['episode'] + 1
            print(f"\n=== エピソード {self.episode} 開始 ===")
            print(f"現在の最高スコア: {self.current_strategy['best_score']}")
            print(f"累計キル数: {self.current_strategy['total_kills']}")
            
            start_time = time.time()
            action_log = []
            state_history = []
            kills = 0
            last_score = 0
            
            # ゲームプレイ
            while time.time() - start_time < duration:
                # 現在の状態を取得
                game_state = self.get_game_state()
                player = game_state['player']
                enemies = game_state['enemies']
                
                # キル数を追跡
                if player['score'] > last_score:
                    kills += (player['score'] - last_score) // 10
                    last_score = player['score']
                    print(f"  敵撃破！ スコア: {player['score']}")
                
                # 状態を記録
                if len(state_history) % 5 == 0:  # 5フレームごとに記録
                    state_history.append({
                        'time': time.time() - start_time,
                        'hp': player['hp'],
                        'mp': player['mp'],
                        'score': player['score'],
                        'enemies': len(enemies),
                        'x': player['x'],
                        'y': player['y']
                    })
                
                # HPが0になったら終了
                if player['hp'] <= 0:
                    print("  ゲームオーバー！")
                    break
                    
                # 最も近い敵を見つける
                if enemies:
                    nearest = min(enemies, key=lambda e: 
                        math.sqrt((e['x']-player['x'])**2 + (e['y']-player['y'])**2))
                    distance = math.sqrt((nearest['x']-player['x'])**2 + 
                                       (nearest['y']-player['y'])**2)
                else:
                    nearest = None
                    distance = float('inf')
                    
                # 行動決定
                if distance < self.current_strategy['dodge_threshold'] and len(enemies) > 3:
                    # 危険！回避行動
                    direction = self.dodge_enemies(player, enemies)
                    self.smart_move(direction, self.current_strategy['movement_speed'])
                    action_log.append('dodge')
                    
                elif distance < self.current_strategy['preferred_distance'] and nearest:
                    # 攻撃範囲内
                    if random.random() < self.current_strategy['attack_accuracy']:
                        # 狙いをつけて攻撃
                        aim_direction = self.aim_at_enemy(player, nearest)
                        self.execute_aimed_attack(aim_direction)
                        action_log.append('attack')
                    else:
                        # 位置調整
                        direction = self.dodge_enemies(player, enemies)
                        self.smart_move(direction, self.current_strategy['movement_speed'] * 0.5)
                        action_log.append('adjust')
                        
                elif nearest:
                    # 敵に接近
                    predicted = self.predict_enemy_position(nearest, player)
                    aim_direction = self.aim_at_enemy(player, predicted)
                    self.smart_move(aim_direction, self.current_strategy['movement_speed'])
                    action_log.append('chase')
                    
                else:
                    # 敵がいない、探索
                    direction = random.choice(['up', 'down', 'left', 'right'])
                    self.smart_move(direction, self.current_strategy['movement_speed'])
                    action_log.append('explore')
                    
                # 特殊攻撃の判断
                if (player['mp'] >= 30 and len(enemies) >= 4 and 
                    random.random() < self.current_strategy['special_frequency']):
                    self.driver.execute_script("game.keys['e'] = true; game.keys['E'] = true;")
                    time.sleep(0.05)
                    self.driver.execute_script("game.keys['e'] = false; game.keys['E'] = false;")
                    action_log.append('special')
                    print("  必殺技発動！")
                    
                time.sleep(self.current_strategy['reaction_time'])
                
            # 最終状態
            final_state = self.get_game_state()
            
            # 結果を記録
            episode_result = {
                'episode': self.episode,
                'timestamp': datetime.now().isoformat(),
                'duration': time.time() - start_time,
                'final_score': final_state['player']['score'],
                'kills': kills,
                'final_hp': final_state['player']['hp'],
                'final_mp': final_state['player']['mp'],
                'enemies_remaining': len(final_state['enemies']),
                'actions_taken': len(action_log),
                'action_breakdown': {
                    'attack': action_log.count('attack'),
                    'dodge': action_log.count('dodge'),
                    'chase': action_log.count('chase'),
                    'explore': action_log.count('explore'),
                    'adjust': action_log.count('adjust'),
                    'special': action_log.count('special')
                }
            }
            
            self.play_history.append(episode_result)
            
            print(f"\n=== エピソード {self.episode} 結果 ===")
            print(f"スコア: {episode_result['final_score']} (キル数: {kills})")
            print(f"生存時間: {episode_result['duration']:.1f}秒")
            print(f"最終HP: {episode_result['final_hp']}")
            print(f"行動内訳: 攻撃{episode_result['action_breakdown']['attack']}回、"
                  f"回避{episode_result['action_breakdown']['dodge']}回、"
                  f"追跡{episode_result['action_breakdown']['chase']}回")
            
            # 学習：戦略を更新
            if episode_result['final_score'] > self.current_strategy['best_score']:
                self.current_strategy['best_score'] = episode_result['final_score']
                print(f"[INFO] 最高スコア更新！")
                
            self.current_strategy['total_kills'] += kills
            self.current_strategy['episode'] = self.episode
            
            # 戦略の微調整
            if kills == 0 and episode_result['duration'] < 20:
                # 攻撃が当たっていない
                self.current_strategy['attack_accuracy'] *= 0.95
                self.current_strategy['preferred_distance'] *= 1.1
                
            if episode_result['final_hp'] == 0 and episode_result['duration'] < 30:
                # 生存時間が短い
                self.current_strategy['dodge_threshold'] *= 1.1
                self.current_strategy['movement_speed'] = min(0.2, 
                    self.current_strategy['movement_speed'] * 1.05)
                    
            # 保存
            with open(self.strategy_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_strategy, f, ensure_ascii=False, indent=2)
                
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.play_history, f, ensure_ascii=False, indent=2)
                
            return episode_result
            
        except Exception as e:
            print(f"[ERROR] エピソード中にエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    def cleanup(self):
        if self.driver:
            self.driver.quit()

def main():
    print("=== 改良版 学習型RPGプレイヤー ===\n")
    print("特徴：")
    print("- 敵の位置を予測して攻撃")
    print("- 複数の敵から賢く回避") 
    print("- 状況に応じた行動選択")
    print("- キル数を追跡\n")
    
    player = ImprovedLearningRPG()
    
    # 履歴をロード
    if os.path.exists(player.log_file):
        with open(player.log_file, 'r', encoding='utf-8') as f:
            player.play_history = json.load(f)
    
    try:
        # 3エピソード実行
        for i in range(3):
            player.setup_driver()
            result = player.play_episode(duration=60)
            player.cleanup()
            
            if i < 2:
                print("\n次のエピソードまで3秒待機...")
                time.sleep(3)
                
        # サマリー表示
        print("\n=== セッションサマリー ===")
        if player.play_history:
            recent = player.play_history[-3:]
            total_score = sum(r['final_score'] for r in recent)
            total_kills = sum(r['kills'] for r in recent)
            avg_duration = sum(r['duration'] for r in recent) / len(recent)
            
            print(f"直近3エピソードの合計スコア: {total_score}")
            print(f"合計キル数: {total_kills}")
            print(f"平均生存時間: {avg_duration:.1f}秒")
            
    except KeyboardInterrupt:
        print("\n[INFO] 学習を中断しました")
    finally:
        player.cleanup()
        
if __name__ == "__main__":
    main()