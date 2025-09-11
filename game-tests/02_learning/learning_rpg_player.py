#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学習型RPGゲームプレイヤー - プレイを重ねるごとに上達していく
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
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Hiragino Sans', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

class LearningRPGPlayer:
    def __init__(self):
        self.driver = None
        self.log_file = "rpg_learning_log.json"
        self.strategy_file = "rpg_strategy.json"
        self.play_history = []
        self.current_strategy = self.load_strategy()
        self.episode = 0
        
    def load_strategy(self):
        """戦略をロード、なければ初期戦略を作成"""
        if os.path.exists(self.strategy_file):
            with open(self.strategy_file, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
                print(f"[INFO] 既存の戦略をロード (エピソード: {strategy['episode']})")
                return strategy
        else:
            # 初期戦略
            return {
                "episode": 0,
                "best_score": 0,
                "attack_frequency": 0.2,  # 攻撃頻度
                "move_frequency": 0.7,     # 移動頻度（生存重視）
                "special_frequency": 0.1,  # 特殊攻撃頻度
                "preferred_distance": 200,  # 敵との好ましい距離
                "dodge_threshold": 100,     # 回避行動を取る距離
                "mp_threshold": 30,         # MP温存の閾値
                "movement_patterns": {
                    "circle": 0.25,
                    "zigzag": 0.25,
                    "random": 0.25,
                    "chase": 0.25
                }
            }
    
    def save_strategy(self):
        """現在の戦略を保存"""
        with open(self.strategy_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_strategy, f, ensure_ascii=False, indent=2)
            
    def load_history(self):
        """過去のプレイ履歴をロード"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        """プレイ履歴を保存"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.play_history, f, ensure_ascii=False, indent=2)
            
    def setup_driver(self):
        """ブラウザ起動"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        
    def get_game_state(self):
        """現在のゲーム状態を取得"""
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
                    maxHp: game.player.maxHp,
                    mp: game.player.mp,
                    maxMp: game.player.maxMp,
                    score: game.player.score,
                    facing: game.player.facing
                },
                enemies: enemies,
                projectiles: game.projectiles.length,
                frameCount: game.frameCount
            };
        """)
        
    def calculate_nearest_enemy(self, player_pos, enemies):
        """最も近い敵を見つける"""
        if not enemies:
            return None, float('inf')
            
        min_dist = float('inf')
        nearest = None
        
        for enemy in enemies:
            dx = enemy['x'] - player_pos['x']
            dy = enemy['y'] - player_pos['y']
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
                
        return nearest, min_dist
        
    def decide_action(self, game_state):
        """ゲーム状態から次の行動を決定"""
        player = game_state['player']
        enemies = game_state['enemies']
        
        nearest_enemy, distance = self.calculate_nearest_enemy(
            {'x': player['x'], 'y': player['y']}, 
            enemies
        )
        
        # 危険度を計算
        danger_level = len(enemies) * 0.1 + (100 - player['hp']) * 0.02
        
        # MP残量を考慮
        mp_ratio = player['mp'] / player['maxMp']
        
        # 行動選択の重み付け
        weights = {
            'move': self.current_strategy['move_frequency'],
            'attack': self.current_strategy['attack_frequency'],
            'special': self.current_strategy['special_frequency'] if mp_ratio > 0.4 else 0
        }
        
        # 距離に基づいて調整
        if distance < self.current_strategy['dodge_threshold']:
            weights['move'] *= 2  # 近すぎる場合は移動を優先
        elif distance > self.current_strategy['preferred_distance']:
            weights['attack'] *= 0.5  # 遠い場合は攻撃を控える
            
        # 重み付き選択
        total = sum(weights.values())
        if total == 0:
            return 'move', None
            
        rand = random.random() * total
        cumsum = 0
        for action, weight in weights.items():
            cumsum += weight
            if rand < cumsum:
                return action, nearest_enemy
                
        return 'move', nearest_enemy
        
    def calculate_move_direction(self, player_pos, nearest_enemy, enemies):
        """移動方向を計算"""
        if not nearest_enemy:
            # 敵がいない場合はランダム移動
            return random.choice(['up', 'down', 'left', 'right'])
            
        dx = nearest_enemy['x'] - player_pos['x']
        dy = nearest_enemy['y'] - player_pos['y']
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 移動パターンを選択
        pattern = random.choices(
            list(self.current_strategy['movement_patterns'].keys()),
            weights=list(self.current_strategy['movement_patterns'].values())
        )[0]
        
        if pattern == 'circle':
            # 円運動
            angle = math.atan2(dy, dx) + math.pi/2
            if abs(math.cos(angle)) > abs(math.sin(angle)):
                return 'right' if math.cos(angle) > 0 else 'left'
            else:
                return 'down' if math.sin(angle) > 0 else 'up'
                
        elif pattern == 'zigzag':
            # ジグザグ移動
            if random.random() < 0.5:
                return 'right' if dx > 0 else 'left'
            else:
                return 'down' if dy > 0 else 'up'
                
        elif pattern == 'chase':
            # 追跡（距離が遠い時）
            if distance > self.current_strategy['preferred_distance']:
                if abs(dx) > abs(dy):
                    return 'right' if dx > 0 else 'left'
                else:
                    return 'down' if dy > 0 else 'up'
            else:
                # 逃走（近すぎる時）
                if abs(dx) > abs(dy):
                    return 'left' if dx > 0 else 'right'
                else:
                    return 'up' if dy > 0 else 'down'
                    
        else:  # random
            return random.choice(['up', 'down', 'left', 'right'])
            
    def execute_action(self, action, direction=None):
        """行動を実行"""
        if action == 'move' and direction:
            key_map = {
                'up': ['w', 'W', 'ArrowUp'],
                'down': ['s', 'S', 'ArrowDown'],
                'left': ['a', 'A', 'ArrowLeft'],
                'right': ['d', 'D', 'ArrowRight']
            }
            keys = key_map[direction]
            for key in keys:
                self.driver.execute_script(f"game.keys['{key}'] = true;")
            time.sleep(0.1)
            for key in keys:
                self.driver.execute_script(f"game.keys['{key}'] = false;")
                
        elif action == 'attack':
            self.driver.execute_script("game.keys[' '] = true;")
            time.sleep(0.05)
            self.driver.execute_script("game.keys[' '] = false;")
            
        elif action == 'special':
            self.driver.execute_script("game.keys['e'] = true; game.keys['E'] = true;")
            time.sleep(0.05)
            self.driver.execute_script("game.keys['e'] = false; game.keys['E'] = false;")
            
    def play_episode(self, duration=60):
        """1エピソードをプレイ"""
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
            
            start_time = time.time()
            action_log = []
            state_history = []
            
            # ゲームプレイ
            while time.time() - start_time < duration:
                # 現在の状態を取得
                game_state = self.get_game_state()
                state_history.append({
                    'time': time.time() - start_time,
                    'hp': game_state['player']['hp'],
                    'mp': game_state['player']['mp'],
                    'score': game_state['player']['score'],
                    'enemies': len(game_state['enemies'])
                })
                
                # HPが0になったら終了
                if game_state['player']['hp'] <= 0:
                    print("  ゲームオーバー！")
                    break
                    
                # 行動を決定
                action, target = self.decide_action(game_state)
                
                # 移動方向を計算
                if action == 'move':
                    direction = self.calculate_move_direction(
                        {'x': game_state['player']['x'], 'y': game_state['player']['y']},
                        target,
                        game_state['enemies']
                    )
                    self.execute_action(action, direction)
                    action_log.append('move')  # シンプルに'move'として記録
                else:
                    self.execute_action(action)
                    action_log.append(action)
                    
                time.sleep(0.1)
                
            # 最終状態を取得
            final_state = self.get_game_state()
            
            # エピソード結果を記録
            episode_result = {
                'episode': self.episode,
                'timestamp': datetime.now().isoformat(),
                'duration': time.time() - start_time,
                'final_score': final_state['player']['score'],
                'final_hp': final_state['player']['hp'],
                'final_mp': final_state['player']['mp'],
                'enemies_remaining': len(final_state['enemies']),
                'actions_taken': len(action_log),
                'action_distribution': {
                    'move': action_log.count('move'),
                    'attack': action_log.count('attack'),
                    'special': action_log.count('special')
                },
                'state_history': state_history
            }
            
            self.play_history.append(episode_result)
            
            print(f"\n=== エピソード {self.episode} 結果 ===")
            print(f"スコア: {episode_result['final_score']}")
            print(f"生存時間: {episode_result['duration']:.1f}秒")
            print(f"行動数: {episode_result['actions_taken']}")
            
            # スクリーンショット
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver.save_screenshot(
                f"C:\\Users\\user\\Desktop\\work\\90_cc\\20250908\\browser-automation-toolkit\\results\\learning_ep{self.episode}_{timestamp}.png"
            )
            
            return episode_result
            
        except Exception as e:
            print(f"[ERROR] エピソード中にエラー: {str(e)}")
            return None
            
    def update_strategy(self):
        """プレイ結果から戦略を更新"""
        if len(self.play_history) < 2:
            return
            
        # 最新の結果を分析
        recent_results = self.play_history[-5:]  # 直近5エピソード
        avg_score = sum(r['final_score'] for r in recent_results) / len(recent_results)
        
        # 最高スコアを更新
        latest = self.play_history[-1]
        if latest['final_score'] > self.current_strategy['best_score']:
            self.current_strategy['best_score'] = latest['final_score']
            print(f"[INFO] 最高スコア更新！ {latest['final_score']}")
            
        # 戦略の調整
        if avg_score < self.current_strategy['best_score'] * 0.7:
            # パフォーマンスが悪い場合は戦略を調整
            print("[INFO] 戦略を調整中...")
            
            # 行動頻度の調整
            if latest['final_hp'] == 0 and latest['duration'] < 30:
                # すぐに死ぬ場合は回避を増やす
                self.current_strategy['move_frequency'] *= 1.1
                self.current_strategy['attack_frequency'] *= 0.9
                self.current_strategy['dodge_threshold'] *= 1.1
                
            if latest['enemies_remaining'] > 15:
                # 敵が多く残る場合は攻撃を増やす
                self.current_strategy['attack_frequency'] *= 1.1
                self.current_strategy['special_frequency'] *= 1.05
                
            # 正規化
            total = (self.current_strategy['move_frequency'] + 
                    self.current_strategy['attack_frequency'] + 
                    self.current_strategy['special_frequency'])
            self.current_strategy['move_frequency'] /= total
            self.current_strategy['attack_frequency'] /= total
            self.current_strategy['special_frequency'] /= total
            
        self.current_strategy['episode'] = self.episode
        
    def visualize_progress(self):
        """学習の進捗を可視化"""
        if len(self.play_history) < 2:
            return
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'RPG学習プレイヤー - エピソード {self.episode}', fontsize=16)
        
        episodes = [h['episode'] for h in self.play_history]
        scores = [h['final_score'] for h in self.play_history]
        durations = [h['duration'] for h in self.play_history]
        
        # スコアの推移
        ax1.plot(episodes, scores, 'b-o', markersize=6)
        ax1.set_xlabel('エピソード')
        ax1.set_ylabel('スコア')
        ax1.set_title('スコアの推移')
        ax1.grid(True, alpha=0.3)
        
        # 生存時間の推移
        ax2.plot(episodes, durations, 'g-o', markersize=6)
        ax2.set_xlabel('エピソード')
        ax2.set_ylabel('生存時間 (秒)')
        ax2.set_title('生存時間の推移')
        ax2.grid(True, alpha=0.3)
        
        # 行動分布（最新エピソード）
        latest = self.play_history[-1]
        actions = ['移動', '攻撃', '特殊']
        counts = [
            latest['action_distribution'].get('move', 0),
            latest['action_distribution'].get('attack', 0),
            latest['action_distribution'].get('special', 0)
        ]
        ax3.pie(counts, labels=actions, autopct='%1.1f%%')
        ax3.set_title('最新エピソードの行動分布')
        
        # スコアのヒストグラム
        ax4.hist(scores, bins=10, color='purple', alpha=0.7)
        ax4.axvline(x=self.current_strategy['best_score'], color='red', 
                   linestyle='--', label=f'最高: {self.current_strategy["best_score"]}')
        ax4.set_xlabel('スコア')
        ax4.set_ylabel('頻度')
        ax4.set_title('スコア分布')
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig(f'rpg_learning_progress_ep{self.episode}.png', dpi=150, bbox_inches='tight')
        print(f"\n[INFO] 進捗グラフを保存: rpg_learning_progress_ep{self.episode}.png")
        
    def cleanup(self):
        """クリーンアップ"""
        if self.driver:
            self.driver.quit()
            
def main():
    print("=== 学習型RPGプレイヤー ===\n")
    print("プレイを重ねるごとに戦略を改善し、スコアを向上させます。\n")
    
    player = LearningRPGPlayer()
    player.play_history = player.load_history()
    
    try:
        # 複数エピソードを実行
        num_episodes = 5
        
        for i in range(num_episodes):
            player.setup_driver()
            
            # 1エピソードプレイ
            result = player.play_episode(duration=45)
            
            if result:
                # 戦略を更新
                player.update_strategy()
                player.save_strategy()
                player.save_history()
                
                # 進捗を可視化
                if (i + 1) % 5 == 0:  # 5エピソードごと
                    player.visualize_progress()
                    
            player.cleanup()
            
            if i < num_episodes - 1:
                print("\n次のエピソードまで3秒待機...")
                time.sleep(3)
                
        # 最終結果を表示
        print("\n=== 学習結果サマリー ===")
        if player.play_history:
            scores = [h['final_score'] for h in player.play_history[-num_episodes:]]
            print(f"直近{num_episodes}エピソードの平均スコア: {sum(scores)/len(scores):.1f}")
            print(f"最高スコア: {max(scores)}")
            print(f"最低スコア: {min(scores)}")
            
            # 最終的な可視化
            player.visualize_progress()
            
    except KeyboardInterrupt:
        print("\n[INFO] 学習を中断しました")
    finally:
        player.cleanup()
        print("\n[INFO] 学習セッション終了")
        
if __name__ == "__main__":
    main()