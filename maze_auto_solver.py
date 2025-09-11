#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迷路自動クリアプログラム
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from collections import deque

class MazeAutoSolver:
    def __init__(self):
        self.driver = None
        self.maze = []
        self.player_pos = None
        self.goal_pos = None
        self.path = []
        
    def setup_driver(self):
        """ブラウザ起動"""
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        
    def open_game(self):
        """迷路ゲームを開く"""
        game_path = os.path.join(os.path.dirname(__file__), "simple-maze-game.html")
        self.driver.get(f"file:///{game_path}")
        time.sleep(1)
        
    def get_maze_state(self):
        """現在の迷路の状態を取得"""
        state = self.driver.execute_script("""
            return {
                maze: game.maze,
                player: game.player,
                goal: game.goal,
                width: MAZE_WIDTH,
                height: MAZE_HEIGHT,
                steps: game.steps,
                stage: game.stage
            };
        """)
        
        self.maze = state['maze']
        self.player_pos = (state['player']['x'], state['player']['y'])
        self.goal_pos = (state['goal']['x'], state['goal']['y'])
        
        return state
        
    def find_path_bfs(self):
        """幅優先探索で最短経路を見つける"""
        start = self.player_pos
        goal = self.goal_pos
        
        # 訪問済みマップ
        visited = set()
        visited.add(start)
        
        # キュー: (現在位置, 経路)
        queue = deque([(start, [])])
        
        # 4方向の移動
        directions = [
            (0, -1, 'up'),    # 上
            (0, 1, 'down'),   # 下
            (-1, 0, 'left'),  # 左
            (1, 0, 'right')   # 右
        ]
        
        while queue:
            (x, y), path = queue.popleft()
            
            # ゴール到達
            if (x, y) == goal:
                return path
                
            # 4方向を探索
            for dx, dy, direction in directions:
                nx, ny = x + dx, y + dy
                
                # 範囲内かつ通路かつ未訪問
                if (0 <= nx < len(self.maze[0]) and 
                    0 <= ny < len(self.maze) and
                    self.maze[ny][nx] == 0 and
                    (nx, ny) not in visited):
                    
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [direction]))
                    
        return []  # 経路が見つからない
        
    def execute_path(self, path):
        """見つけた経路を実行"""
        print(f"\n経路を実行中... ({len(path)}ステップ)")
        
        # キーマッピング
        key_map = {
            'up': Keys.UP,
            'down': Keys.DOWN,
            'left': Keys.LEFT,
            'right': Keys.RIGHT
        }
        
        body = self.driver.find_element(By.TAG_NAME, "body")
        
        for i, direction in enumerate(path):
            body.send_keys(key_map[direction])
            time.sleep(0.05)  # 少し待機
            
            if i % 10 == 0:
                print(f"  進行状況: {i}/{len(path)}")
                
        print(f"  完了！")
        
    def solve_maze(self):
        """迷路を解く"""
        print("\n=== 迷路自動解析 ===")
        
        # 現在の状態を取得
        state = self.get_maze_state()
        print(f"ステージ: {state['stage']}")
        print(f"プレイヤー位置: {self.player_pos}")
        print(f"ゴール位置: {self.goal_pos}")
        
        # 最短経路を探索
        print("\n最短経路を探索中...")
        path = self.find_path_bfs()
        
        if path:
            print(f"経路発見！ 必要ステップ数: {len(path)}")
            
            # 視覚的に経路を表示（最初の10手）
            print("\n最初の10手: ", end="")
            for direction in path[:10]:
                symbols = {'up': '↑', 'down': '↓', 'left': '←', 'right': '→'}
                print(symbols[direction], end=" ")
            if len(path) > 10:
                print("...")
            else:
                print()
                
            # 経路を実行
            self.execute_path(path)
            
            # 結果を確認（アラートが出る前に少し待つ）
            time.sleep(1)
            
            # アラートの処理
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                print(f"\n{alert_text}")
                alert.accept()  # OKをクリック
                
                # 次のステージの状態を取得
                time.sleep(0.5)
                final_state = self.get_maze_state()
                print(f"次のステージ: {final_state['stage']}")
                return True
            except:
                # アラートがない場合
                final_state = self.get_maze_state()
                print(f"\n結果: ステップ数 = {final_state['steps']}")
                return False
                
        else:
            print("経路が見つかりませんでした")
            
        return False
        
    def auto_play(self, num_stages=3):
        """複数ステージを自動プレイ"""
        print(f"=== {num_stages}ステージ自動プレイ開始 ===\n")
        
        for i in range(num_stages):
            print(f"\n--- ステージ {i+1} ---")
            
            if self.solve_maze():
                print("ステージクリア！")
                time.sleep(1)  # 次のステージの読み込み待ち
            else:
                print("ステージクリア失敗")
                break
                
        print("\n=== 自動プレイ終了 ===")
        
    def cleanup(self):
        """終了処理"""
        if self.driver:
            self.driver.quit()

def main():
    print("=== 迷路自動ソルバー ===")
    print("幅優先探索で最短経路を見つけます\n")
    
    solver = MazeAutoSolver()
    
    try:
        solver.setup_driver()
        solver.open_game()
        
        # 3ステージ自動プレイ
        solver.auto_play(3)
        
        print("\nブラウザを閉じるには Enter を押してください...")
        input()
        
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        solver.cleanup()

if __name__ == "__main__":
    main()