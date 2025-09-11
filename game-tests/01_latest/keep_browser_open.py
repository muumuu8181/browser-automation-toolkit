#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ブラウザを開いたままにするRPGプレイヤー
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

def main():
    print("=== RPGゲームを開きます ===\n")
    
    # ブラウザ設定
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'browser': 'ALL'}
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    # デタッチモードで起動（プログラム終了後もブラウザは残る）
    options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(options=options)
    
    # ゲームを開く
    game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
    driver.get(f"file:///{game_path}")
    
    print("ゲームを開きました！")
    print("\n操作方法:")
    print("- 矢印キー/WASD: 移動")
    print("- スペース: 攻撃")
    print("- E: 特殊攻撃")
    print("\nブラウザは開いたままです。")
    print("手動でプレイできます。")
    
    # 初期状態を表示
    time.sleep(2)
    state = driver.execute_script("""
        return {
            hp: game.player.hp,
            mp: game.player.mp,
            enemies: game.enemies.length
        };
    """)
    
    print(f"\n現在の状態:")
    print(f"HP: {state['hp']}/100")
    print(f"MP: {state['mp']}/50")
    print(f"敵の数: {state['enemies']}")
    
    print("\n自動プレイを開始する場合は Enter キーを押してください")
    print("そのまま手動でプレイする場合は、このウィンドウを閉じてください")
    
    try:
        input()
        
        print("\n10秒間の自動プレイを開始します...")
        start_time = time.time()
        
        # 簡単な自動プレイ
        while time.time() - start_time < 10:
            # ランダムに移動
            driver.execute_script("""
                const dirs = ['w', 'a', 's', 'd'];
                const dir = dirs[Math.floor(Math.random() * dirs.length)];
                game.keys[dir] = true;
                setTimeout(() => game.keys[dir] = false, 100);
                
                // たまに攻撃
                if (Math.random() < 0.3 && game.player.attackCooldown <= 0) {
                    playerAttack();
                }
            """)
            time.sleep(0.5)
            
        print("\n自動プレイ終了！")
        print("ブラウザは開いたままです。")
        
    except:
        pass
    
    print("\nプログラムを終了します。")
    print("ブラウザは開いたままなので、手動で閉じてください。")

if __name__ == "__main__":
    main()