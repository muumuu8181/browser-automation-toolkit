#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迷路自動ソルバー（視覚的パス表示機能付き）
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from datetime import datetime
from collections import deque
import json

class MazeSolverVisual:
    def __init__(self):
        self.driver = None
        self.log_file = "maze_visual_log.txt"
        self.json_log_file = "maze_visual_log.json"
        self.log_entries = []
        
    def write_log(self, message, event_type="INFO"):
        """ログファイルに書き込み"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{event_type}] {message}"
        
        # テキストファイルに追記
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
            
        # JSONログ用のエントリも保存
        self.log_entries.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "message": message,
            "unix_time": time.time()
        })
        
        # コンソールにも出力
        print(log_entry)
        
    def save_json_log(self):
        """JSON形式でログを保存"""
        with open(self.json_log_file, "w", encoding="utf-8") as f:
            json.dump(self.log_entries, f, ensure_ascii=False, indent=2)
            
    def setup_driver(self):
        """ブラウザ起動"""
        self.write_log("ブラウザ起動開始", "SYSTEM")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("detach", True)  # ブラウザを開いたまま
        self.driver = webdriver.Chrome(options=options)
        self.write_log("ブラウザ起動完了", "SYSTEM")
        
    def open_game(self):
        """迷路ゲームを開く"""
        game_path = os.path.join(os.path.dirname(__file__), "simple-maze-game.html")
        self.write_log(f"ゲームファイルを開く: {game_path}", "GAME")
        self.driver.get(f"file:///{game_path}")
        time.sleep(1)
        self.write_log("ゲーム読み込み完了", "GAME")
        
    def inject_visual_functions(self):
        """視覚化用の関数をゲームに注入"""
        self.driver.execute_script("""
            // パスを視覚的に表示する関数
            window.visualizePath = function(path) {
                const canvas = document.getElementById('gameCanvas');
                const ctx = canvas.getContext('2d');
                const CELL_SIZE = 25;
                
                // 現在のプレイヤー位置から開始
                let x = game.player.x;
                let y = game.player.y;
                
                ctx.strokeStyle = 'rgba(0, 255, 255, 0.8)';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(x * CELL_SIZE + CELL_SIZE/2, y * CELL_SIZE + CELL_SIZE/2);
                
                // パスに沿って線を描く
                for (let i = 0; i < path.length; i++) {
                    const direction = path[i];
                    switch(direction) {
                        case 'up': y--; break;
                        case 'down': y++; break;
                        case 'left': x--; break;
                        case 'right': x++; break;
                    }
                    ctx.lineTo(x * CELL_SIZE + CELL_SIZE/2, y * CELL_SIZE + CELL_SIZE/2);
                }
                
                ctx.stroke();
                
                // ゴール地点にマーカー
                ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
                ctx.beginPath();
                ctx.arc(x * CELL_SIZE + CELL_SIZE/2, y * CELL_SIZE + CELL_SIZE/2, 
                       CELL_SIZE/4, 0, Math.PI * 2);
                ctx.fill();
            };
            
            // パス表示をクリアする関数
            window.clearPathVisualization = function() {
                // 再描画を強制
                render();
            };
            
            console.log('視覚化関数を注入しました');
        """)
        self.write_log("視覚化関数を注入", "VISUAL")
        
    def get_maze_state(self):
        """現在の迷路の状態を取得"""
        state = self.driver.execute_script("""
            return {
                maze: game.maze,
                player: game.player,
                goal: game.goal,
                steps: game.steps,
                stage: game.stage
            };
        """)
        return state
        
    def find_path_bfs(self, start, goal, maze):
        """幅優先探索で最短経路を見つける"""
        visited = set()
        visited.add(start)
        queue = deque([(start, [])])
        
        directions = [
            (0, -1, 'up'),
            (0, 1, 'down'),
            (-1, 0, 'left'),
            (1, 0, 'right')
        ]
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == goal:
                return path
                
            for dx, dy, direction in directions:
                nx, ny = x + dx, y + dy
                
                if (0 <= nx < len(maze[0]) and 
                    0 <= ny < len(maze) and
                    maze[ny][nx] == 0 and
                    (nx, ny) not in visited):
                    
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [direction]))
                    
        return []
        
    def visualize_path(self, path):
        """パスを視覚的に表示"""
        path_str = json.dumps(path)
        self.driver.execute_script(f"window.visualizePath({path_str});")
        self.write_log(f"パスを視覚化: {len(path)}ステップ", "VISUAL")
        
    def execute_path_with_visual(self, path):
        """視覚表示付きで経路を実行"""
        key_map = {
            'up': Keys.UP,
            'down': Keys.DOWN,
            'left': Keys.LEFT,
            'right': Keys.RIGHT
        }
        
        body = self.driver.find_element(By.TAG_NAME, "body")
        
        # 実行前に少し待機（視覚効果を見るため）
        time.sleep(1)
        
        start_time = time.time()
        for i, direction in enumerate(path):
            body.send_keys(key_map[direction])
            time.sleep(0.1)  # 各ステップを見やすく
            
            # 進捗をログ
            if i % 5 == 0:
                progress = (i + 1) / len(path) * 100
                self.write_log(f"進捗: {progress:.1f}% ({i+1}/{len(path)}ステップ)", "PROGRESS")
                
        execution_time = time.time() - start_time
        self.write_log(f"経路実行完了: {len(path)}ステップ, 実行時間: {execution_time:.2f}秒", "MOVE")
        
    def solve_stage(self):
        """1ステージを解く（視覚表示付き）"""
        state = self.get_maze_state()
        stage_num = state['stage']
        player_pos = (state['player']['x'], state['player']['y'])
        goal_pos = (state['goal']['x'], state['goal']['y'])
        
        self.write_log(f"ステージ {stage_num} 開始", "STAGE")
        self.write_log(f"プレイヤー位置: {player_pos}, ゴール位置: {goal_pos}", "INFO")
        
        # 経路探索
        path_start_time = time.time()
        path = self.find_path_bfs(player_pos, goal_pos, state['maze'])
        path_time = time.time() - path_start_time
        
        if path:
            self.write_log(f"経路発見: {len(path)}ステップ, 探索時間: {path_time:.3f}秒", "SOLVER")
            
            # パスを視覚化
            self.visualize_path(path)
            
            # 経路実行
            self.execute_path_with_visual(path)
            
            # アラート待機と処理
            time.sleep(1)
            
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                
                # アラート検知をログに記録
                self.write_log(f"アラート検知: '{alert_text}'", "ALERT")
                
                # アラート受諾
                alert.accept()
                self.write_log("アラートを閉じました", "ALERT")
                
                # クリア情報をログ
                self.write_log(f"ステージ {stage_num} クリア！", "CLEAR")
                
                # パス表示をクリア
                self.driver.execute_script("window.clearPathVisualization();")
                
                return True
                
            except:
                self.write_log("アラートが検出されませんでした", "WARNING")
                return False
        else:
            self.write_log("経路が見つかりませんでした", "ERROR")
            return False
            
    def auto_play(self, num_stages=3):
        """複数ステージを自動プレイ（視覚表示付き）"""
        self.write_log(f"視覚表示付き自動プレイ開始: {num_stages}ステージ", "START")
        
        # 視覚化機能を注入
        self.inject_visual_functions()
        
        cleared_stages = 0
        total_steps = 0
        
        for i in range(num_stages):
            if self.solve_stage():
                cleared_stages += 1
                # 現在のステップ数を取得
                state = self.get_maze_state()
                total_steps = state['steps']
                time.sleep(1)  # 次のステージの準備
            else:
                break
                
        self.write_log(f"自動プレイ終了: {cleared_stages}/{num_stages}ステージクリア, 総ステップ数: {total_steps}", "END")
        
    def cleanup(self):
        """終了処理"""
        self.write_log("セッション終了", "SYSTEM")
        # detachオプションを使っているので、ブラウザは閉じない
        # JSON形式でもログを保存
        self.save_json_log()
        self.write_log("ログ保存完了", "SYSTEM")

def main():
    print("=== 迷路自動ソルバー（視覚パス表示版） ===\n")
    
    solver = MazeSolverVisual()
    
    try:
        solver.setup_driver()
        solver.open_game()
        solver.auto_play(3)
        
        print(f"\nログファイル: {solver.log_file}")
        print(f"JSONログ: {solver.json_log_file}")
        print("\nブラウザは開いたままにしています")
        print("パスが水色の線で表示されます")
        
    except Exception as e:
        solver.write_log(f"エラー発生: {str(e)}", "ERROR")
    finally:
        solver.cleanup()

if __name__ == "__main__":
    main()