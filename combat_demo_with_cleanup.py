from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import atexit

# グローバル変数でドライバーを管理
driver = None

def cleanup():
    """確実にブラウザを閉じる"""
    global driver
    if driver:
        try:
            driver.quit()
            print("ブラウザを閉じました")
        except:
            pass

# プログラム終了時に必ず実行
atexit.register(cleanup)

def combat_demo():
    global driver
    print("=== 戦闘システムデモ ===")
    
    try:
        # ブラウザ起動
        print("ブラウザ起動中...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(800, 800)
        
        # ゲーム読み込み
        game_file = os.path.abspath("maze-game-with-combat.html")
        driver.get(f"file:///{game_file}")
        time.sleep(1)
        print("ゲーム開始！")
        
        body = driver.find_element(By.TAG_NAME, "body")
        
        # 初期状態
        state = driver.execute_script("""
            return {
                player: game.player,
                enemies: game.enemies.length,
                items: game.items.length,
                health: game.health,
                attacksRemaining: game.player.attacksRemaining
            };
        """)
        
        print(f"\n初期状態:")
        print(f"- ライフ: {state['health']}")
        print(f"- 攻撃回数: {state['attacksRemaining']}")
        print(f"- 敵の数: {state['enemies']}")
        print(f"- アイテムの数: {state['items']}")
        
        print("\n15秒間のデモプレイ...")
        
        # デモプレイ
        start_time = time.time()
        action_count = 0
        
        while time.time() - start_time < 15:  # 15秒間
            # 右に移動してみる
            body.send_keys(Keys.ARROW_RIGHT)
            action_count += 1
            time.sleep(0.5)
            
            # 下に移動
            body.send_keys(Keys.ARROW_DOWN)
            action_count += 1
            time.sleep(0.5)
            
            # 攻撃！
            body.send_keys(Keys.SPACE)
            print(f"攻撃！ (アクション {action_count})")
            time.sleep(0.5)
            
            # 5秒ごとに全体攻撃
            if int(time.time() - start_time) % 5 == 0:
                body.send_keys('x')
                print("全体攻撃！")
                time.sleep(1)
            
            # 現在の状態確認
            current = driver.execute_script("""
                return {
                    x: game.player.x,
                    y: game.player.y,
                    health: game.health,
                    attacksRemaining: game.player.attacksRemaining,
                    score: game.score,
                    enemies: game.enemies.length
                };
            """)
            
            if action_count % 6 == 0:
                print(f"状態: 位置({current['x']},{current['y']}), " +
                      f"ライフ:{current['health']}, " +
                      f"攻撃回数:{current['attacksRemaining']}, " +
                      f"スコア:{current['score']}, " +
                      f"敵:{current['enemies']}")
                      
            # アラート処理
            try:
                alert = driver.switch_to.alert
                text = alert.text
                print(f"[アラート] {text}")
                alert.accept()
                time.sleep(1)
            except:
                pass
        
        # 最終結果
        final = driver.execute_script("""
            return {
                stage: game.stage,
                score: game.score,
                health: game.health,
                enemies: game.enemies.length
            };
        """)
        
        print(f"\n=== デモ終了 ===")
        print(f"ステージ: {final['stage']}")
        print(f"スコア: {final['score']}")
        print(f"残りライフ: {final['health']}")
        print(f"残り敵数: {final['enemies']}")
        
    except Exception as e:
        print(f"エラー: {str(e)}")
    
    finally:
        print("\n5秒後にブラウザを必ず閉じます...")
        time.sleep(5)

if __name__ == "__main__":
    try:
        combat_demo()
    finally:
        cleanup()  # 確実にクリーンアップ