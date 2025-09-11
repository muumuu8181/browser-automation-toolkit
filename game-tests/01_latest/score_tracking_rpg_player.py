#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スコア追跡型RPGプレイヤー - プレイごとにスコアを記録・表示
"""

import json
import os
from datetime import datetime
import time
import random
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Hiragino Sans', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

class ScoreTrackingRPGPlayer:
    def __init__(self):
        self.driver = None
        self.score_file = "rpg_score_history.json"
        self.score_history = self.load_score_history()
        self.session_scores = []
        self.last_attack_time = 0
        self.attack_cooldown = 0.25
        
    def load_score_history(self):
        """スコア履歴をロード"""
        if os.path.exists(self.score_file):
            with open(self.score_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
        
    def save_score_history(self):
        """スコア履歴を保存"""
        with open(self.score_file, 'w', encoding='utf-8') as f:
            json.dump(self.score_history, f, ensure_ascii=False, indent=2)
            
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
        """通常攻撃"""
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
            
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
        return self.driver.execute_script("""
            if (game.player.mp >= 20) {
                specialAttack();
                return true;
            }
            return false;
        """)
        
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
                    facing: game.player.facing
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
            
    def display_score_board(self):
        """スコアボードを表示"""
        total_games = len(self.score_history)
        if total_games == 0:
            print("\n📊 まだスコア履歴がありません")
            return
            
        print("\n" + "="*50)
        print("📊 スコアボード")
        print("="*50)
        
        # 全体統計
        all_scores = [h['score'] for h in self.score_history]
        print(f"\n【全体統計】")
        print(f"総プレイ数: {total_games}回")
        print(f"合計スコア: {sum(all_scores):,}")
        print(f"平均スコア: {sum(all_scores)/len(all_scores):.1f}")
        print(f"最高スコア: {max(all_scores)} (プレイ #{self.score_history[all_scores.index(max(all_scores))]['play_number']})")
        
        # 最近10プレイ
        print(f"\n【最近の10プレイ】")
        recent_plays = self.score_history[-10:]
        for play in recent_plays:
            time_str = datetime.fromisoformat(play['timestamp']).strftime("%H:%M:%S")
            bar = "█" * (play['score'] // 10) + "▒" * ((100 - play['score']) // 10)
            print(f"#{play['play_number']:3d} [{time_str}] スコア: {play['score']:3d} |{bar}|")
            
        # 今回のセッション
        if self.session_scores:
            print(f"\n【今回のセッション】")
            print(f"プレイ数: {len(self.session_scores)}回")
            print(f"セッション平均: {sum(self.session_scores)/len(self.session_scores):.1f}")
            print(f"セッション最高: {max(self.session_scores)}")
            
        print("="*50)
        
    def visualize_progress(self):
        """進捗をグラフ化"""
        if len(self.score_history) < 2:
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # スコアの推移
        plays = [h['play_number'] for h in self.score_history[-30:]]
        scores = [h['score'] for h in self.score_history[-30:]]
        
        ax1.plot(plays, scores, 'b-o', markersize=6, linewidth=2)
        ax1.set_xlabel('プレイ番号')
        ax1.set_ylabel('スコア')
        ax1.set_title('スコアの推移（直近30プレイ）')
        ax1.grid(True, alpha=0.3)
        
        # 移動平均を追加
        if len(scores) > 5:
            moving_avg = []
            for i in range(4, len(scores)):
                avg = sum(scores[i-4:i+1]) / 5
                moving_avg.append(avg)
            ax1.plot(plays[4:], moving_avg, 'r--', linewidth=2, label='5プレイ移動平均')
            ax1.legend()
            
        # スコア分布
        all_scores = [h['score'] for h in self.score_history]
        ax2.hist(all_scores, bins=20, color='green', alpha=0.7, edgecolor='black')
        ax2.axvline(x=sum(all_scores)/len(all_scores), color='red', 
                   linestyle='--', label=f'平均: {sum(all_scores)/len(all_scores):.1f}')
        ax2.set_xlabel('スコア')
        ax2.set_ylabel('頻度')
        ax2.set_title('スコア分布')
        ax2.legend()
        
        plt.tight_layout()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(f'rpg_score_progress_{timestamp}.png', dpi=150, bbox_inches='tight')
        print(f"\n📈 グラフを保存: rpg_score_progress_{timestamp}.png")
        
    def play_game(self, duration=45):
        """ゲームをプレイ"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(2)
            
            # キャンバスにフォーカス
            canvas = self.driver.find_element(By.ID, "gameCanvas")
            canvas.click()
            
            play_number = len(self.score_history) + 1
            print(f"\n🎮 プレイ #{play_number} 開始！")
            
            start_time = time.time()
            last_score = 0
            max_score = 0
            
            # リアルタイムスコア表示の準備
            print("スコア: ", end="", flush=True)
            
            while time.time() - start_time < duration:
                # ゲーム状態を取得
                game_state = self.get_game_state()
                player = game_state['player']
                enemies = game_state['enemies']
                
                # スコア更新をリアルタイム表示
                if player['score'] > last_score:
                    print(f"{player['score']} ", end="", flush=True)
                    last_score = player['score']
                    max_score = player['score']
                
                # HPが0なら終了
                if player['hp'] <= 0:
                    print("\n💀 ゲームオーバー！")
                    break
                    
                # 最も近い敵を見つける
                nearest, distance = self.find_nearest_enemy(player, enemies)
                
                if nearest and distance < 300:
                    # 敵の方向を向いて攻撃
                    direction = self.get_direction_to_target(player, nearest)
                    self.move(direction, 0.05)
                    self.attack()
                    
                    # 特殊攻撃の判断
                    if player['mp'] >= 30 and len(enemies) >= 3 and random.random() < 0.15:
                        if self.special_attack():
                            print("💥", end="", flush=True)
                            
                elif nearest:
                    # 敵に接近
                    direction = self.get_direction_to_target(player, nearest)
                    self.move(direction, 0.2)
                    
                else:
                    # 探索
                    direction = random.choice(['up', 'down', 'left', 'right'])
                    self.move(direction, 0.3)
                    
                time.sleep(0.05)
                
            # プレイ結果を記録
            final_state = self.get_game_state()
            play_time = time.time() - start_time
            
            result = {
                'play_number': play_number,
                'timestamp': datetime.now().isoformat(),
                'score': final_state['player']['score'],
                'duration': play_time,
                'final_hp': final_state['player']['hp'],
                'final_mp': final_state['player']['mp'],
                'enemies_killed': final_state['player']['score'] // 10
            }
            
            # 履歴に追加
            self.score_history.append(result)
            self.session_scores.append(result['score'])
            self.save_score_history()
            
            # 結果表示
            print(f"\n\n🏁 プレイ #{play_number} 終了！")
            print(f"最終スコア: {result['score']} (撃破数: {result['enemies_killed']}体)")
            print(f"生存時間: {result['duration']:.1f}秒")
            
            # 特別なメッセージ
            if result['score'] >= 100:
                print("🎉 素晴らしい！100点以上！")
            elif result['score'] >= 50:
                print("👍 良いプレイでした！")
            elif result['score'] == 0:
                print("😢 次はきっと上手くいきます！")
                
            # スコアボードを表示
            self.display_score_board()
            
            # 10プレイごとにグラフを生成
            if play_number % 10 == 0:
                self.visualize_progress()
                
            return result['score']
            
        except Exception as e:
            print(f"\n[ERROR] プレイ中にエラー: {str(e)}")
            return 0
            
    def cleanup(self):
        if self.driver:
            self.driver.quit()

def main():
    print("=== スコア追跡型RPGプレイヤー ===")
    print("毎回のスコアを記録し、進捗を可視化します\n")
    
    player = ScoreTrackingRPGPlayer()
    
    # 初期スコアボード表示
    if player.score_history:
        player.display_score_board()
        print("\n続けてプレイしますか？ (Ctrl+C で終了)")
        time.sleep(2)
    
    try:
        play_count = 0
        
        while True:
            play_count += 1
            print(f"\n--- セッション内プレイ {play_count} ---")
            
            player.setup_driver()
            score = player.play_game(duration=45)
            player.cleanup()
            
            # 次のプレイまでの待機
            print("\n次のプレイまで5秒... (Ctrl+C で終了)")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 セッション終了")
        
        # 最終統計
        if player.session_scores:
            print(f"\n【セッション統計】")
            print(f"プレイ数: {len(player.session_scores)}回")
            print(f"合計スコア: {sum(player.session_scores)}")
            print(f"平均スコア: {sum(player.session_scores)/len(player.session_scores):.1f}")
            print(f"最高スコア: {max(player.session_scores)}")
            
            # 最終グラフ生成
            if len(player.score_history) >= 2:
                player.visualize_progress()
                
        print("\nお疲れ様でした！👋")

if __name__ == "__main__":
    main()