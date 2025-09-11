from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from collections import deque
import time
import json
import os
from datetime import datetime

class MazeSolverWithEnemies:
    def __init__(self, game_file="maze-game-with-enemies.html"):
        self.driver = None
        self.game_file = os.path.abspath(game_file)
        self.logs = []
        self.game_data = {
            "sessions": [],
            "total_stages": 0,
            "total_steps": 0,
            "enemy_collisions": 0,
            "stage_attempts": []
        }
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.logs.append(log_entry)
        
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
        self.log(f"ゲームファイルを開く: {self.game_file}", "GAME")
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
                    enemies: game.enemies.map(e => ({x: e.x, y: e.y, type: e.type})),
                    maze: game.maze,
                    stage: game.stage,
                    steps: game.steps,
                    health: game.health,
                    gameOver: game.gameOver
                };
            """)
            return state
        except:
            return None
            
    def find_safe_path(self, state, avoid_enemies=True):
        """敵を避けながら最短経路を探索（A*アルゴリズム）"""
        maze = state['maze']
        start = (state['player']['x'], state['player']['y'])
        goal = (state['goal']['x'], state['goal']['y'])
        enemies = [(e['x'], e['y']) for e in state['enemies']] if avoid_enemies else []
        
        # ヒューリスティック関数（マンハッタン距離）
        def heuristic(pos):
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
        # 敵からの距離を計算
        def enemy_danger(pos):
            if not avoid_enemies:
                return 0
            min_dist = float('inf')
            for enemy_pos in enemies:
                dist = abs(pos[0] - enemy_pos[0]) + abs(pos[1] - enemy_pos[1])
                min_dist = min(min_dist, dist)
            # 距離が近いほど危険度が高い
            return max(0, 3 - min_dist) * 5
        
        # 優先度付きキュー（手動実装）
        open_set = [(0, start, [])]
        visited = set()
        
        while open_set:
            # 最小コストのノードを取得
            open_set.sort(key=lambda x: x[0])
            f_score, current, path = open_set.pop(0)
            
            if current == goal:
                return path
                
            if current in visited:
                continue
                
            visited.add(current)
            
            # 4方向を探索
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                
                # 範囲チェックと壁チェック
                if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and 
                    maze[ny][nx] == 0 and (nx, ny) not in visited):
                    
                    # 新しいパス
                    new_path = path + [(nx, ny)]
                    
                    # コスト計算
                    g_score = len(new_path)
                    h_score = heuristic((nx, ny))
                    danger = enemy_danger((nx, ny))
                    f_score = g_score + h_score + danger
                    
                    open_set.append((f_score, (nx, ny), new_path))
        
        # 敵を避けて経路が見つからない場合は、敵を無視して再探索
        if avoid_enemies:
            self.log("安全な経路が見つかりません。敵を無視して探索", "SOLVER")
            return self.find_safe_path(state, avoid_enemies=False)
            
        return None
        
    def visualize_path(self, path):
        """パスを視覚的に表示"""
        if not path:
            return
            
        script = """
            const path = arguments[0];
            const ctx = document.getElementById('gameCanvas').getContext('2d');
            const CELL_SIZE = 25;
            
            // パスを描画
            ctx.strokeStyle = '#0ff';
            ctx.lineWidth = 3;
            ctx.globalAlpha = 0.5;
            
            ctx.beginPath();
            for (let i = 0; i < path.length; i++) {
                const x = path[i][0] * CELL_SIZE + CELL_SIZE/2;
                const y = path[i][1] * CELL_SIZE + CELL_SIZE/2;
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
            ctx.globalAlpha = 1.0;
        """
        
        self.driver.execute_script(script, path)
        
    def move_along_path(self, path):
        """パスに沿って移動（敵の動きを考慮）"""
        # canvasではなくbodyにキー送信
        body = self.driver.find_element(By.TAG_NAME, "body")
        moves = 0
        
        for i, (x, y) in enumerate(path):
            # 現在の状態を取得
            state = self.get_game_state()
            if not state or state['gameOver']:
                break
                
            current = (state['player']['x'], state['player']['y'])
            
            # すでに目標地点にいる場合はスキップ
            if current == (x, y):
                continue
                
            # 敵が近くにいるかチェック
            enemies_nearby = False
            for enemy in state['enemies']:
                dist = abs(enemy['x'] - current[0]) + abs(enemy['y'] - current[1])
                if dist <= 2:
                    enemies_nearby = True
                    self.log(f"敵が接近中！距離: {dist}", "WARNING")
                    break
            
            # 敵が近い場合は再経路探索
            if enemies_nearby and i > 5:
                self.log("敵が近いため再経路探索", "SOLVER")
                new_path = self.find_safe_path(state)
                if new_path:
                    self.visualize_path(new_path)
                    return moves + self.move_along_path(new_path)
            
            # 移動方向を決定
            dx = x - current[0]
            dy = y - current[1]
            
            # キー入力
            if dx > 0:
                body.send_keys(Keys.ARROW_RIGHT)
            elif dx < 0:
                body.send_keys(Keys.ARROW_LEFT)
            elif dy > 0:
                body.send_keys(Keys.ARROW_DOWN)
            elif dy < 0:
                body.send_keys(Keys.ARROW_UP)
                
            moves += 1
            time.sleep(0.15)  # 敵の動きを見るために少し遅く
            
            # 進捗表示
            if moves % 10 == 0:
                progress = (i / len(path)) * 100
                self.log(f"進捗: {progress:.1f}% ({i}/{len(path)}ステップ)", "PROGRESS")
                
        return moves
        
    def handle_alert(self):
        """アラート処理"""
        try:
            wait = WebDriverWait(self.driver, 0.5)
            alert = wait.until(EC.alert_is_present())
            alert_text = alert.text
            self.log(f"アラート検知: '{alert_text}'", "ALERT")
            alert.accept()
            self.log("アラート処理完了", "ALERT")
            return alert_text
        except TimeoutException:
            return None
            
    def play_stage(self):
        """1ステージをプレイ"""
        state = self.get_game_state()
        if not state:
            return False
            
        self.log(f"ステージ {state['stage']} 開始", "STAGE")
        self.log(f"プレイヤー位置: ({state['player']['x']}, {state['player']['y']}), " +
                f"ゴール位置: ({state['goal']['x']}, {state['goal']['y']})", "INFO")
        self.log(f"敵の数: {len(state['enemies'])}, ライフ: {state['health']}", "INFO")
        
        attempts = 0
        stage_data = {
            "stage": state['stage'],
            "attempts": 0,
            "enemy_collisions": 0,
            "total_steps": 0
        }
        
        while attempts < 5:  # 最大5回まで挑戦
            attempts += 1
            stage_data["attempts"] = attempts
            
            # 経路探索
            start_time = time.time()
            path = self.find_safe_path(state)
            search_time = time.time() - start_time
            
            if not path:
                self.log("経路が見つかりません", "ERROR")
                return False
                
            self.log(f"経路発見: {len(path)}ステップ, 探索時間: {search_time:.3f}秒", "SOLVER")
            
            # パスを表示
            self.visualize_path(path)
            self.log(f"パス描画完了: {len(path)}ステップ", "VISUAL")
            
            # 移動実行
            start_time = time.time()
            moves = self.move_along_path(path)
            move_time = time.time() - start_time
            stage_data["total_steps"] += moves
            
            self.log(f"移動実行完了: {moves}ステップ, 実行時間: {move_time:.2f}秒", "MOVE")
            
            # アラートチェック
            time.sleep(0.5)
            alert_text = self.handle_alert()
            
            if alert_text and "クリア" in alert_text:
                self.log(f"ステージ {state['stage']} クリア！", "CLEAR")
                self.game_data["stage_attempts"].append(stage_data)
                return True
            elif alert_text and "ゲームオーバー" in alert_text:
                self.log("ゲームオーバー！", "GAMEOVER")
                self.game_data["enemy_collisions"] += 1
                stage_data["enemy_collisions"] += 1
                time.sleep(1)
                # ゲームがリセットされるので再挑戦
                state = self.get_game_state()
                if state:
                    self.log(f"再挑戦 {attempts+1}/5", "RETRY")
            else:
                # 敵との衝突をチェック
                new_state = self.get_game_state()
                if new_state and new_state['health'] < state['health']:
                    self.log("敵と衝突！初期位置に戻されました", "COLLISION")
                    self.game_data["enemy_collisions"] += 1
                    stage_data["enemy_collisions"] += 1
                    state = new_state
                    time.sleep(0.5)
                else:
                    break
                    
        return False
        
    def play_game(self, max_stages=5):
        """ゲームを自動プレイ"""
        self.log(f"=== 敵対応迷路ソルバー ===", "START")
        self.log(f"自動プレイ開始: 最大{max_stages}ステージ", "START")
        
        session_start = time.time()
        stages_cleared = 0
        
        try:
            for i in range(max_stages):
                if self.play_stage():
                    stages_cleared += 1
                    self.game_data["total_stages"] = stages_cleared
                    time.sleep(1)
                else:
                    self.log("ステージクリア失敗", "ERROR")
                    break
                    
        except Exception as e:
            self.log(f"エラー発生: {str(e)}", "ERROR")
            
        session_time = time.time() - session_start
        self.log(f"自動プレイ終了: {stages_cleared}/{max_stages}ステージクリア, " +
                f"合計敵衝突: {self.game_data['enemy_collisions']}回", "END")
        
        # セッションデータを保存
        self.game_data["sessions"].append({
            "timestamp": datetime.now().isoformat(),
            "stages_cleared": stages_cleared,
            "total_time": session_time,
            "enemy_collisions": self.game_data["enemy_collisions"]
        })
        
    def save_logs(self):
        """ログを保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # テキストログ
        log_file = f"maze_enemies_log_{timestamp}.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.logs))
            
        # JSONログ
        json_file = f"maze_enemies_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.game_data, f, ensure_ascii=False, indent=2)
            
        print(f"\nログファイル: {log_file}")
        print(f"データファイル: {json_file}")
        
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.log("セッション終了", "SYSTEM")
            time.sleep(2)
            self.driver.quit()
            self.log("ブラウザを閉じました", "SYSTEM")
            
    def run(self):
        """メイン実行"""
        try:
            self.start_browser()
            self.load_game()
            self.play_game(max_stages=3)
        finally:
            self.save_logs()
            # inputを使わずに少し待機
            time.sleep(3)
            self.close()

if __name__ == "__main__":
    print("=== 敵対応迷路ソルバー ===\n")
    
    solver = MazeSolverWithEnemies()
    solver.run()