from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import sys

def demo_with_keys():
    driver = None
    try:
        print("=== 鍵とドアシステムデモ ===")
        
        # ブラウザ起動
        print("ブラウザ起動中...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(800, 800)
        
        # ゲーム読み込み
        game_file = os.path.abspath("maze-game-with-keys.html")
        driver.get(f"file:///{game_file}")
        time.sleep(1)
        
        body = driver.find_element(By.TAG_NAME, "body")
        
        # 初期状態
        state = driver.execute_script("""
            return {
                stage: game.stage,
                keys: game.keys.map(k => ({x: k.x, y: k.y, color: k.color, collected: k.collected})),
                doors: game.doors.map(d => ({x: d.x, y: d.y, color: d.color, isOpen: d.isOpen})),
                playerKeys: game.player.keys,
                enemies: game.enemies.length
            };
        """)
        
        print(f"\n初期状態:")
        print(f"- ステージ: {state['stage']}")
        print(f"- 鍵の数: {len(state['keys'])}")
        print(f"- ドアの数: {len(state['doors'])}")
        print(f"- 敵の数: {state['enemies']}")
        
        if state['doors']:
            print("\nドアの情報:")
            for door in state['doors']:
                print(f"  {door['color']}ドア: ({door['x']}, {door['y']})")
                
        if state['keys']:
            print("\n鍵の情報:")
            for key in state['keys']:
                print(f"  {key['color']}鍵: ({key['x']}, {key['y']})")
        
        # 20秒間の自動プレイ
        print("\n20秒間の自動プレイ開始...")
        start_time = time.time()
        move_count = 0
        
        # 基本的な探索パターン
        patterns = [
            [(Keys.ARROW_RIGHT, 3), (Keys.ARROW_DOWN, 3)],
            [(Keys.ARROW_DOWN, 3), (Keys.ARROW_RIGHT, 3)],
            [(Keys.ARROW_LEFT, 2), (Keys.ARROW_DOWN, 2)],
            [(Keys.ARROW_RIGHT, 4), (Keys.ARROW_UP, 2)],
        ]
        pattern_index = 0
        
        while time.time() - start_time < 20:
            # パターンに従って移動
            pattern = patterns[pattern_index % len(patterns)]
            
            for direction, count in pattern:
                for _ in range(count):
                    body.send_keys(direction)
                    move_count += 1
                    time.sleep(0.2)
                    
                    # 状態更新
                    current = driver.execute_script("""
                        return {
                            x: game.player.x,
                            y: game.player.y,
                            playerKeys: game.player.keys,
                            health: game.health,
                            score: game.score
                        };
                    """)
                    
                    # 鍵を取得したか確認
                    if len(current['playerKeys']) > len(state.get('playerKeys', [])):
                        print(f"\n[鍵取得] {current['playerKeys'][-1]}の鍵を入手！")
                        print(f"  現在位置: ({current['x']}, {current['y']})")
                        state['playerKeys'] = current['playerKeys']
                    
                    # 10手ごとに状態表示
                    if move_count % 10 == 0:
                        print(f"\n移動{move_count}回目:")
                        print(f"  位置: ({current['x']}, {current['y']})")
                        print(f"  所持鍵: {current['playerKeys']}")
                        print(f"  スコア: {current['score']}")
            
            # 敵が近い場合は攻撃
            enemies = driver.execute_script("""
                return game.enemies.map(e => ({
                    x: e.x, 
                    y: e.y,
                    dist: Math.abs(e.x - game.player.x) + Math.abs(e.y - game.player.y)
                }));
            """)
            
            close_enemies = [e for e in enemies if e['dist'] <= 1]
            if close_enemies:
                body.send_keys(Keys.SPACE)
                print("  攻撃！")
                
            pattern_index += 1
            
            # アラート処理
            try:
                alert = driver.switch_to.alert
                text = alert.text
                print(f"\n[アラート] {text}")
                alert.accept()
                time.sleep(1)
                break
            except:
                pass
        
        # 最終状態
        final_state = driver.execute_script("""
            return {
                stage: game.stage,
                score: game.score,
                playerKeys: game.player.keys,
                doorsOpened: game.doors.filter(d => d.isOpen).length,
                keysCollected: game.keys.filter(k => k.collected).length
            };
        """)
        
        print(f"\n=== 最終結果 ===")
        print(f"ステージ: {final_state['stage']}")
        print(f"スコア: {final_state['score']}")
        print(f"取得した鍵: {final_state['keysCollected']}個")
        print(f"開けたドア: {final_state['doorsOpened']}個")
        print(f"所持鍵: {final_state['playerKeys']}")
        
    except Exception as e:
        print(f"\nエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("\n5秒後にブラウザを閉じます...")
            time.sleep(5)
            driver.quit()
            print("ブラウザを閉じました")

if __name__ == "__main__":
    demo_with_keys()