from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

print("=== 簡易迷路テスト ===")

try:
    # ブラウザ起動
    print("1. ブラウザ起動中...")
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(800, 800)
    print("   OK: ブラウザ起動成功")
    
    # ゲーム読み込み
    print("2. ゲーム読み込み中...")
    game_file = os.path.abspath("maze-game-improved-enemies.html")
    driver.get(f"file:///{game_file}")
    time.sleep(1)
    print("   OK: ゲーム読み込み成功")
    
    # 状態確認
    print("3. ゲーム状態確認...")
    state = driver.execute_script("return {stage: game.stage, health: game.health, enemies: game.enemies.length};")
    print(f"   - ステージ: {state['stage']}")
    print(f"   - ライフ: {state['health']}")
    print(f"   - 敵の数: {state['enemies']}")
    
    # 少し動かす
    print("4. 移動テスト...")
    body = driver.find_element(By.TAG_NAME, "body")
    
    # 右に3回
    for i in range(3):
        body.send_keys(Keys.ARROW_RIGHT)
        time.sleep(0.5)
        pos = driver.execute_script("return {x: game.player.x, y: game.player.y};")
        print(f"   移動{i+1}: 位置({pos['x']}, {pos['y']})")
    
    # スペースキーテスト
    print("5. 押しのけテスト...")
    body.send_keys(Keys.SPACE)
    print("   OK: スペースキー押下")
    time.sleep(0.5)
    
    # 最終状態
    final = driver.execute_script("return {x: game.player.x, y: game.player.y, health: game.health, steps: game.steps};")
    print(f"6. 最終状態: 位置({final['x']}, {final['y']}), ライフ: {final['health']}, 歩数: {final['steps']}")
    
    print("\n[成功] テスト完了！")
    
except Exception as e:
    print(f"\n[エラー] {str(e)}")
    
finally:
    print("\n5秒後にブラウザを閉じます...")
    time.sleep(5)
    if 'driver' in locals():
        driver.quit()
    print("終了しました")