from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
import time
import os
from datetime import datetime

def demo_enemy_maze():
    """敵キャラクター版迷路の短いデモ"""
    driver = None
    
    try:
        print("=== 敵キャラクター版迷路デモ ===")
        print("[開始] ブラウザを起動します...")
        
        # ブラウザ起動
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(800, 800)
        print("[OK] ブラウザ起動完了")
        
        # ゲーム読み込み
        game_file = os.path.abspath("maze-game-with-enemies.html")
        driver.get(f"file:///{game_file}")
        time.sleep(1.5)
        print("[OK] ゲーム読み込み完了")
        
        # ゲーム状態を取得
        state = driver.execute_script("""
            return {
                player: game.player,
                goal: game.goal,
                enemies: game.enemies.length,
                stage: game.stage,
                health: game.health
            };
        """)
        
        print(f"\n[情報] ゲーム状態:")
        print(f"  - ステージ: {state['stage']}")
        print(f"  - プレイヤー位置: ({state['player']['x']}, {state['player']['y']})")
        print(f"  - ゴール位置: ({state['goal']['x']}, {state['goal']['y']})")
        print(f"  - 敵の数: {state['enemies']}")
        print(f"  - ライフ: {state['health']}")
        
        # 少し動かしてみる
        body = driver.find_element(By.TAG_NAME, "body")
        print("\n[デモ] 少し動かしてみます...")
        
        moves = [
            (Keys.ARROW_RIGHT, "右"),
            (Keys.ARROW_RIGHT, "右"),
            (Keys.ARROW_DOWN, "下"),
            (Keys.ARROW_DOWN, "下"),
            (Keys.ARROW_RIGHT, "右"),
            (Keys.ARROW_RIGHT, "右"),
            (Keys.ARROW_DOWN, "下"),
            (Keys.ARROW_DOWN, "下")
        ]
        
        for key, direction in moves:
            body.send_keys(key)
            print(f"  移動: {direction}")
            time.sleep(0.3)
            
            # 現在の状態を確認
            current = driver.execute_script("return {x: game.player.x, y: game.player.y, health: game.health};")
            
            # 敵の位置も確認
            enemies = driver.execute_script("return game.enemies.map(e => ({x: e.x, y: e.y, type: e.type}));")
            print(f"    位置: ({current['x']}, {current['y']}), ライフ: {current['health']}")
            
            # 近くに敵がいるか確認
            for enemy in enemies:
                dist = abs(enemy['x'] - current['x']) + abs(enemy['y'] - current['y'])
                if dist <= 2:
                    print(f"    ⚠️ 敵が近い！ 距離: {dist}, タイプ: {enemy['type']}")
        
        print("\n[デモ] 10秒間敵の動きを観察...")
        for i in range(10):
            time.sleep(1)
            enemies = driver.execute_script("return game.enemies.map(e => ({x: e.x, y: e.y, type: e.type}));")
            print(f"  {i+1}秒後 - 敵の位置: ", end="")
            for j, enemy in enumerate(enemies):
                print(f"敵{j+1}({enemy['x']},{enemy['y']})", end=" ")
            print()
            
        print("\n[完了] デモ終了")
        
    except Exception as e:
        print(f"\n[エラー] {str(e)}")
        
    finally:
        if driver:
            print("\n[終了] 5秒後にブラウザを閉じます...")
            time.sleep(5)
            driver.quit()
            print("[OK] ブラウザを閉じました")

if __name__ == "__main__":
    demo_enemy_maze()