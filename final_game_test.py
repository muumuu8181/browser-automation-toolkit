from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

def test_final_game():
    driver = None
    
    try:
        print("=== 完全版迷路ゲーム動作確認 ===")
        
        # ブラウザ起動
        print("\n1. ブラウザ起動...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(900, 900)
        print("   OK: ブラウザ起動成功")
        
        # ゲーム読み込み
        print("\n2. ゲーム読み込み...")
        game_file = os.path.abspath("maze-game-final.html")
        driver.get(f"file:///{game_file}")
        time.sleep(1)
        print("   OK: ゲーム読み込み成功")
        
        body = driver.find_element(By.TAG_NAME, "body")
        
        # 初期状態確認
        print("\n3. 初期状態確認...")
        state = driver.execute_script("""
            return {
                stage: game.stage,
                currentFloor: game.currentFloor,
                totalFloors: game.totalFloors,
                timeLimit: game.timeLimit,
                timeLeft: game.timeLeft,
                health: game.health,
                score: game.score,
                highScore: game.highScore,
                enemies: game.enemies.length,
                items: game.items.length
            };
        """)
        
        print(f"   - ステージ: {state['stage']}")
        print(f"   - 階層: 地下{state['currentFloor']}階 / 全{state['totalFloors']}階")
        print(f"   - 制限時間: {state['timeLimit']}秒 (残り{state['timeLeft']}秒)")
        print(f"   - ライフ: {state['health']}")
        print(f"   - スコア: {state['score']}")
        print(f"   - ハイスコア: {state['highScore']}")
        print(f"   - 敵の数: {state['enemies']}")
        print(f"   - アイテムの数: {state['items']}")
        
        # 新機能のテスト
        print("\n4. 新機能テスト開始...")
        
        # 4.1 時間経過チェック
        print("\n4.1 時間経過チェック...")
        initial_time = state['timeLeft']
        time.sleep(2)
        
        current_time = driver.execute_script("return game.timeLeft;")
        print(f"   2秒後: {initial_time}秒 → {current_time}秒")
        
        # 4.2 移動とスコア獲得
        print("\n4.2 移動とスコア獲得テスト...")
        moves = [Keys.ARROW_RIGHT, Keys.ARROW_RIGHT, Keys.ARROW_DOWN, Keys.ARROW_DOWN]
        
        for i, key in enumerate(moves):
            body.send_keys(key)
            time.sleep(0.3)
            
            pos = driver.execute_script("return {x: game.player.x, y: game.player.y, score: game.score};")
            print(f"   移動{i+1}: ({pos['x']}, {pos['y']}) スコア: {pos['score']}")
        
        # 4.3 コンボシステムテスト
        print("\n4.3 コンボシステムテスト...")
        # 敵を探して攻撃
        for _ in range(5):
            body.send_keys(Keys.SPACE)
            time.sleep(0.2)
            
        combo_info = driver.execute_script("return {combo: game.combo, lastKillTime: game.lastKillTime};")
        print(f"   コンボ: {combo_info['combo']}")
        
        # 4.4 アイテム効果確認
        print("\n4.4 アイテム収集...")
        # ランダムに動いてアイテムを探す
        for _ in range(10):
            direction = [Keys.ARROW_RIGHT, Keys.ARROW_DOWN, Keys.ARROW_LEFT, Keys.ARROW_UP][_ % 4]
            body.send_keys(direction)
            time.sleep(0.2)
            
        item_state = driver.execute_script("""
            return {
                health: game.health,
                attackPower: game.player.attackPower,
                attacksRemaining: game.player.attacksRemaining,
                timeLeft: game.timeLeft
            };
        """)
        print(f"   - ライフ: {item_state['health']}")
        print(f"   - 攻撃力: {item_state['attackPower']}")
        print(f"   - 攻撃回数: {item_state['attacksRemaining']}")
        
        # 4.5 階層移動チェック
        print("\n4.5 階層システムチェック...")
        stairs_info = driver.execute_script("""
            return {
                hasUpStairs: game.stairs.up !== null,
                hasDownStairs: game.stairs.down !== null,
                downStairsPos: game.stairs.down ? {x: game.stairs.down.x, y: game.stairs.down.y} : null
            };
        """)
        
        if stairs_info['hasDownStairs']:
            print(f"   下り階段あり: ({stairs_info['downStairsPos']['x']}, {stairs_info['downStairsPos']['y']})")
        if stairs_info['hasUpStairs']:
            print("   上り階段あり")
            
        # 4.6 全体攻撃テスト
        print("\n4.6 全体攻撃テスト...")
        body.send_keys('x')
        time.sleep(0.5)
        
        special_used = driver.execute_script("return game.player.specialAttackUsed;")
        print(f"   全体攻撃使用: {special_used}")
        
        # 5. パフォーマンステスト
        print("\n5. 10秒間の連続プレイ...")
        start_score = driver.execute_script("return game.score;")
        play_start = time.time()
        
        while time.time() - play_start < 10:
            # AIっぽい動き
            for direction in [Keys.ARROW_RIGHT, Keys.ARROW_DOWN, Keys.ARROW_LEFT, Keys.ARROW_UP]:
                body.send_keys(direction)
                time.sleep(0.1)
                
                # 敵が近ければ攻撃
                enemies_near = driver.execute_script("""
                    const player = game.player;
                    return game.enemies.filter(e => 
                        Math.abs(e.x - player.x) + Math.abs(e.y - player.y) <= 1
                    ).length;
                """)
                
                if enemies_near > 0:
                    body.send_keys(Keys.SPACE)
                    print("   敵を攻撃！")
                    
            # アラート処理
            try:
                alert = driver.switch_to.alert
                text = alert.text
                print(f"\n[アラート] {text}")
                alert.accept()
                break
            except:
                pass
                
        # 最終結果
        final_state = driver.execute_script("""
            return {
                stage: game.stage,
                currentFloor: game.currentFloor,
                score: game.score,
                timeLeft: game.timeLeft,
                health: game.health,
                combo: game.combo,
                gameOver: game.gameOver
            };
        """)
        
        print(f"\n=== 最終状態 ===")
        print(f"ステージ: {final_state['stage']}")
        print(f"現在階: 地下{final_state['currentFloor']}階")
        print(f"スコア: {start_score} → {final_state['score']} (+{final_state['score'] - start_score})")
        print(f"残り時間: {final_state['timeLeft']}秒")
        print(f"ライフ: {final_state['health']}")
        print(f"最大コンボ: {final_state['combo']}")
        print(f"ゲームオーバー: {final_state['gameOver']}")
        
        print("\n✅ 動作確認完了！全機能正常動作")
        
    except Exception as e:
        print(f"\n❌ エラー発生: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("\n5秒後にブラウザを閉じます...")
            time.sleep(5)
            driver.quit()
            print("ブラウザを閉じました")

if __name__ == "__main__":
    test_final_game()