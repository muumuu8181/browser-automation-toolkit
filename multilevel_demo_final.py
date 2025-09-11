from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import signal
import sys

# グローバル変数
driver = None

def cleanup(signum=None, frame=None):
    """確実にブラウザを閉じる"""
    global driver
    print("\nクリーンアップ中...")
    if driver:
        try:
            driver.quit()
            print("ブラウザを正常に閉じました")
        except:
            print("ブラウザは既に閉じられています")
    sys.exit(0)

# シグナルハンドラ設定
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def multilevel_demo():
    global driver
    
    try:
        print("=== 複数階層迷路デモ ===")
        
        # ブラウザ起動
        print("ブラウザ起動中...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(800, 800)
        
        # ゲーム読み込み
        game_file = os.path.abspath("maze-game-multilevel.html")
        driver.get(f"file:///{game_file}")
        time.sleep(1)
        
        body = driver.find_element(By.TAG_NAME, "body")
        
        # 初期状態
        state = driver.execute_script("""
            return {
                currentFloor: game.currentFloor,
                totalFloors: game.totalFloors,
                player: {x: game.player.x, y: game.player.y},
                stairs: game.stairs,
                enemies: game.enemies.length,
                health: game.health
            };
        """)
        
        print(f"\n=== ゲーム情報 ===")
        print(f"現在: 地下{state['currentFloor']}階 / 全{state['totalFloors']}階")
        print(f"プレイヤー位置: ({state['player']['x']}, {state['player']['y']})")
        print(f"敵の数: {state['enemies']}")
        print(f"ライフ: {state['health']}")
        
        if state['stairs']['up']:
            print(f"上り階段: ({state['stairs']['up']['x']}, {state['stairs']['up']['y']})")
        if state['stairs']['down']:
            print(f"下り階段: ({state['stairs']['down']['x']}, {state['stairs']['down']['y']})")
        
        # 15秒間のデモプレイ
        print("\n15秒間のデモプレイ開始...")
        start_time = time.time()
        action_count = 0
        
        # 簡単な探索パターン
        while time.time() - start_time < 15:
            # 右と下を交互に
            for _ in range(3):
                body.send_keys(Keys.ARROW_RIGHT)
                action_count += 1
                time.sleep(0.2)
                
            for _ in range(3):
                body.send_keys(Keys.ARROW_DOWN)
                action_count += 1
                time.sleep(0.2)
                
            # 状態確認
            current = driver.execute_script("""
                return {
                    floor: game.currentFloor,
                    x: game.player.x,
                    y: game.player.y,
                    health: game.health,
                    score: game.score,
                    keys: game.player.keys
                };
            """)
            
            # 階層が変わったか確認
            if current['floor'] != state['currentFloor']:
                print(f"\n[階層移動] 地下{state['currentFloor']}階 → 地下{current['floor']}階")
                state['currentFloor'] = current['floor']
                
                # 新しい階の情報取得
                new_state = driver.execute_script("""
                    return {
                        stairs: game.stairs,
                        enemies: game.enemies.length,
                        goal: game.goal
                    };
                """)
                
                print(f"新しい階の敵: {new_state['enemies']}体")
                if new_state['goal']:
                    print("この階にゴールがあります！")
            
            # 進捗表示
            if action_count % 15 == 0:
                print(f"\n地下{current['floor']}階 - 位置:({current['x']},{current['y']}), " +
                      f"ライフ:{current['health']}, スコア:{current['score']}")
                
            # 敵が近い場合は攻撃
            body.send_keys(Keys.SPACE)
            
            # アラート処理
            try:
                alert = driver.switch_to.alert
                text = alert.text
                print(f"\n[アラート] {text}")
                alert.accept()
                break
            except:
                pass
        
        # 最終状態
        final = driver.execute_script("""
            return {
                stage: game.stage,
                currentFloor: game.currentFloor,
                totalFloors: game.totalFloors,
                score: game.score,
                visitedFloors: Array.from(game.visitedFloors)
            };
        """)
        
        print(f"\n=== 最終結果 ===")
        print(f"ステージ: {final['stage']}")
        print(f"現在の階: 地下{final['currentFloor']}階")
        print(f"訪問した階: {final['visitedFloors']}")
        print(f"スコア: {final['score']}")
        
    except Exception as e:
        print(f"\nエラー: {str(e)}")
    
    finally:
        print("\n5秒後に必ずブラウザを閉じます...")
        time.sleep(5)
        cleanup()

if __name__ == "__main__":
    try:
        multilevel_demo()
    except KeyboardInterrupt:
        print("\n中断されました")
        cleanup()
    except Exception as e:
        print(f"予期しないエラー: {e}")
        cleanup()