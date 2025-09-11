#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ゲーム開始時の状況を確認
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

def main():
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'browser': 'ALL'}
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # ゲームを開く
        game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
        driver.get(f"file:///{game_path}")
        time.sleep(2)
        
        print("=== ゲーム開始時チェック ===\n")
        
        # 初期状態を確認
        initial = driver.execute_script("""
            return {
                player: {
                    x: game.player.x,
                    y: game.player.y,
                    hp: game.player.hp,
                    maxHp: game.player.maxHp,
                    speed: game.player.speed
                },
                enemies: game.enemies.map(e => ({
                    x: e.x,
                    y: e.y,
                    hp: e.hp,
                    distance: Math.sqrt(
                        Math.pow(e.x - game.player.x, 2) + 
                        Math.pow(e.y - game.player.y, 2)
                    )
                })),
                frameCount: game.frameCount
            };
        """)
        
        print(f"プレイヤー初期位置: X={initial['player']['x']}, Y={initial['player']['y']}")
        print(f"プレイヤー初期HP: {initial['player']['hp']}/{initial['player']['maxHp']}")
        print(f"プレイヤー速度: {initial['player']['speed']}")
        print(f"\n敵の数: {len(initial['enemies'])}体")
        
        # 近い敵を表示
        close_enemies = [e for e in initial['enemies'] if e['distance'] < 100]
        print(f"100ピクセル以内の敵: {len(close_enemies)}体")
        
        for i, enemy in enumerate(initial['enemies'][:5]):
            print(f"  敵{i+1}: 距離={enemy['distance']:.0f}px, HP={enemy['hp']}")
        
        # 5秒間のダメージを観察
        print("\n--- 5秒間の状態変化 ---")
        
        for second in range(5):
            time.sleep(1)
            
            state = driver.execute_script("""
                return {
                    hp: game.player.hp,
                    x: game.player.x,
                    y: game.player.y,
                    enemyCount: game.enemies.length,
                    closestEnemy: game.enemies.length > 0 ? 
                        Math.min(...game.enemies.map(e => 
                            Math.sqrt(Math.pow(e.x - game.player.x, 2) + 
                                    Math.pow(e.y - game.player.y, 2))
                        )) : 999
                };
            """)
            
            print(f"{second+1}秒後: HP={state['hp']}, 位置=({state['x']}, {state['y']}), "
                  f"敵数={state['enemyCount']}, 最近敵={state['closestEnemy']:.0f}px")
            
            if state['hp'] <= 0:
                print("\nゲームオーバー！")
                break
        
        # 何もしないで生き残れるか確認
        print("\n--- 移動してみる ---")
        
        # 右上に逃げる
        driver.execute_script("""
            game.keys['d'] = true;
            game.keys['w'] = true;
        """)
        time.sleep(1)
        driver.execute_script("""
            game.keys['d'] = false;
            game.keys['w'] = false;
        """)
        
        final = driver.execute_script("""
            return {
                hp: game.player.hp,
                x: game.player.x,
                y: game.player.y,
                score: game.player.score
            };
        """)
        
        print(f"\n移動後: HP={final['hp']}, 位置=({final['x']}, {final['y']})")
        
        print("\nブラウザは開いたままです。")
        print("手動で操作してみてください。")
        print("終了するには Enter キーを押してください...")
        input()
        
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()