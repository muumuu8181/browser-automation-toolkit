from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from collections import deque

def auto_play_maze():
    print("=== 迷路自動プレイデモ ===")
    
    try:
        # ブラウザ起動
        print("ブラウザ起動中...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(800, 800)
        
        # ゲーム読み込み
        game_file = os.path.abspath("maze-game-improved-enemies.html")
        driver.get(f"file:///{game_file}")
        time.sleep(1)
        print("ゲーム開始！")
        
        body = driver.find_element(By.TAG_NAME, "body")
        
        # 30秒間自動プレイ
        start_time = time.time()
        move_count = 0
        
        while time.time() - start_time < 30:  # 30秒間
            # ゲーム状態取得
            state = driver.execute_script("""
                return {
                    player: game.player,
                    goal: game.goal,
                    maze: game.maze,
                    enemies: game.enemies.map(e => ({x: e.x, y: e.y})),
                    health: game.health,
                    steps: game.steps,
                    stage: game.stage
                };
            """)
            
            # 簡易的なBFS経路探索
            path = find_path(state['maze'], 
                           (state['player']['x'], state['player']['y']),
                           (state['goal']['x'], state['goal']['y']))
            
            if path and len(path) > 1:
                # 次の移動先
                next_pos = path[1]
                dx = next_pos[0] - state['player']['x']
                dy = next_pos[1] - state['player']['y']
                
                # 移動
                if dx > 0:
                    body.send_keys(Keys.ARROW_RIGHT)
                elif dx < 0:
                    body.send_keys(Keys.ARROW_LEFT)
                elif dy > 0:
                    body.send_keys(Keys.ARROW_DOWN)
                elif dy < 0:
                    body.send_keys(Keys.ARROW_UP)
                    
                move_count += 1
                
                # 進捗表示（10手ごと）
                if move_count % 10 == 0:
                    print(f"移動: {move_count}回, ステージ: {state['stage']}, " +
                          f"位置: ({state['player']['x']}, {state['player']['y']}), " +
                          f"ライフ: {state['health']}")
            
            # 敵が近い場合は押しのける
            enemies_nearby = sum(1 for e in state['enemies'] 
                               if abs(e['x'] - state['player']['x']) + abs(e['y'] - state['player']['y']) <= 2)
            
            if enemies_nearby >= 2:
                body.send_keys(Keys.SPACE)
                print("敵を押しのけた！")
                time.sleep(0.5)
            
            # アラート処理
            try:
                alert = driver.switch_to.alert
                text = alert.text
                print(f"[アラート] {text}")
                alert.accept()
                time.sleep(1)
            except:
                pass
                
            time.sleep(0.15)  # 少し待機
            
        # 最終結果
        final_state = driver.execute_script("return {stage: game.stage, steps: game.steps, health: game.health};")
        print(f"\n=== 結果 ===")
        print(f"到達ステージ: {final_state['stage']}")
        print(f"総歩数: {final_state['steps']}")
        print(f"残りライフ: {final_state['health']}")
        print(f"総移動回数: {move_count}")
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        
    finally:
        print("\n5秒後にブラウザを閉じます...")
        time.sleep(5)
        if 'driver' in locals():
            driver.quit()
        print("終了")

def find_path(maze, start, goal):
    """簡単なBFS経路探索"""
    queue = deque([(start[0], start[1], [])])
    visited = set()
    
    while queue:
        x, y, path = queue.popleft()
        
        if (x, y) == goal:
            return [(start[0], start[1])] + path + [(x, y)]
            
        if (x, y) in visited:
            continue
            
        visited.add((x, y))
        
        # 4方向探索
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and 
                maze[ny][nx] == 0 and (nx, ny) not in visited):
                
                queue.append((nx, ny, path + [(x, y)]))
    
    return None

if __name__ == "__main__":
    auto_play_maze()