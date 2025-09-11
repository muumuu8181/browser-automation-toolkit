from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
import time
import os
from datetime import datetime

class ImprovedMazeSolver:
    def __init__(self, game_file="maze-game-improved-enemies.html"):
        self.driver = None
        self.game_file = os.path.abspath(game_file)
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def start_browser(self):
        self.log("ブラウザ起動中", "SYSTEM")
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(800, 800)
        self.log("ブラウザ起動完了", "SYSTEM")
        
    def load_game(self):
        self.log(f"ゲームを開く", "GAME")
        self.driver.get(f"file:///{self.game_file}")
        time.sleep(1.5)
        self.log("ゲーム読み込み完了", "GAME")
        
    def get_game_state(self):
        """JavaScriptからゲーム状態を取得"""
        try:
            state = self.driver.execute_script("""
                return {
                    player: game.player,
                    goal: game.goal,
                    enemies: game.enemies.map(e => ({
                        x: e.x, 
                        y: e.y, 
                        type: e.type,
                        stunTime: e.stunTime
                    })),
                    maze: game.maze,
                    stage: game.stage,
                    steps: game.steps,
                    health: game.health,
                    pushCooldown: game.pushCooldown,
                    powerUpTime: game.powerUpTime
                };
            """)
            return state
        except:
            return None
            
    def find_path_bfs(self, state):
        """シンプルなBFS経路探索"""
        maze = state['maze']
        start = (state['player']['x'], state['player']['y'])
        goal = (state['goal']['x'], state['goal']['y'])
        
        from collections import deque
        
        queue = deque([(start, [])])
        visited = set()
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == goal:
                return path
                
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            # 4方向を探索
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and 
                    maze[ny][nx] == 0 and (nx, ny) not in visited):
                    
                    new_path = path + [(nx, ny)]
                    queue.append(((nx, ny), new_path))
        
        return None
        
    def should_push_enemies(self, state):
        """敵を押しのけるべきか判断"""
        if state['pushCooldown'] > 0:
            return False
            
        # 周囲2マス以内の敵をカウント
        enemies_nearby = 0
        for enemy in state['enemies']:
            if enemy['stunTime'] > 0:
                continue
            dist = abs(enemy['x'] - state['player']['x']) + abs(enemy['y'] - state['player']['y'])
            if dist <= 2:
                enemies_nearby += 1
                
        return enemies_nearby >= 2  # 2体以上いたら押しのける
        
    def play_stage(self):
        """1ステージをプレイ"""
        state = self.get_game_state()
        if not state:
            return False
            
        self.log(f"ステージ {state['stage']} 開始", "STAGE")
        self.log(f"敵: {len(state['enemies'])}体, ライフ: {state['health']}", "INFO")
        
        body = self.driver.find_element(By.TAG_NAME, "body")
        
        while True:
            state = self.get_game_state()
            if not state:
                break
                
            # 経路探索
            path = self.find_path_bfs(state)
            if not path:
                self.log("経路が見つかりません", "ERROR")
                break
                
            # 敵を押しのけるべきか判断
            if self.should_push_enemies(state):
                self.log("敵を押しのける！", "ACTION")
                body.send_keys(Keys.SPACE)
                time.sleep(0.5)
                continue
                
            # 次の移動先
            if len(path) > 0:
                next_pos = path[0]
                dx = next_pos[0] - state['player']['x']
                dy = next_pos[1] - state['player']['y']
                
                # キー入力
                if dx > 0:
                    body.send_keys(Keys.ARROW_RIGHT)
                elif dx < 0:
                    body.send_keys(Keys.ARROW_LEFT)
                elif dy > 0:
                    body.send_keys(Keys.ARROW_DOWN)
                elif dy < 0:
                    body.send_keys(Keys.ARROW_UP)
                    
                time.sleep(0.2)  # 敵の動きを見るため
                
            # アラートチェック
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.log(f"アラート: {alert_text}", "ALERT")
                alert.accept()
                
                if "クリア" in alert_text:
                    self.log(f"ステージ {state['stage']} クリア！", "CLEAR")
                    return True
                elif "ゲームオーバー" in alert_text:
                    self.log("ゲームオーバー", "GAMEOVER")
                    return False
            except:
                pass
                
            # 進捗表示
            if state['steps'] % 20 == 0 and state['steps'] > 0:
                self.log(f"進行中: {state['steps']}歩", "PROGRESS")
                
        return False
        
    def run_demo(self, max_stages=3):
        """デモ実行"""
        try:
            self.start_browser()
            self.load_game()
            
            self.log(f"=== 改良版迷路ソルバー デモ ===", "START")
            self.log(f"最大{max_stages}ステージをプレイ", "START")
            
            stages_cleared = 0
            
            for i in range(max_stages):
                if self.play_stage():
                    stages_cleared += 1
                    time.sleep(1)
                else:
                    break
                    
            self.log(f"デモ終了: {stages_cleared}/{max_stages}ステージクリア", "END")
            
        except Exception as e:
            self.log(f"エラー: {str(e)}", "ERROR")
            
        finally:
            if self.driver:
                self.log("10秒後にブラウザを閉じます", "SYSTEM")
                time.sleep(10)
                self.driver.quit()
                self.log("ブラウザを閉じました", "SYSTEM")

if __name__ == "__main__":
    solver = ImprovedMazeSolver()
    solver.run_demo(max_stages=2)  # 2ステージだけデモ