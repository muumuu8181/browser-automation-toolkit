#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アクションRPG操作デモ - Selenium修正版
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

class ActionRPGSeleniumFix:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """ブラウザ起動"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        print("[INFO] アクションRPG操作デモ（修正版）開始！")
        
    def show_movement(self):
        """JavaScriptとActionChainsを組み合わせて確実に動かす"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\action_rpg.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(3)
            
            print("\n=== 確実に動く操作デモ ===\n")
            
            # canvasとbodyを取得
            canvas = self.driver.find_element(By.TAG_NAME, "canvas")
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # canvasをクリックしてフォーカス
            canvas.click()
            time.sleep(1)
            
            # 初期位置
            pos = self.driver.execute_script("return {x: Math.round(game.player.x), y: Math.round(game.player.y)};")
            print(f"初期位置: X:{pos['x']}, Y:{pos['y']}")
            
            # デモ1: JavaScriptでキー入力をシミュレート
            print("\n[DEMO 1] JavaScript制御による移動")
            
            # 右に移動
            print("  → 右に移動中...")
            self.driver.execute_script("""
                // キーを押す
                game.keys['ArrowRight'] = true;
                // 1秒後に離す
                setTimeout(() => {
                    game.keys['ArrowRight'] = false;
                }, 1000);
            """)
            time.sleep(1.5)
            
            pos = self.driver.execute_script("return {x: Math.round(game.player.x), y: Math.round(game.player.y)};")
            print(f"     現在位置: X:{pos['x']}, Y:{pos['y']}")
            
            # 下に移動
            print("  ↓ 下に移動中...")
            self.driver.execute_script("""
                game.keys['ArrowDown'] = true;
                setTimeout(() => {
                    game.keys['ArrowDown'] = false;
                }, 1000);
            """)
            time.sleep(1.5)
            
            pos = self.driver.execute_script("return {x: Math.round(game.player.x), y: Math.round(game.player.y)};")
            print(f"     現在位置: X:{pos['x']}, Y:{pos['y']}")
            
            # デモ2: 攻撃しながら移動
            print("\n[DEMO 2] 攻撃しながら移動")
            
            for i in range(5):
                print(f"  攻撃 {i+1}/5")
                # 移動
                direction = ['ArrowUp', 'ArrowRight', 'ArrowDown', 'ArrowLeft'][i % 4]
                self.driver.execute_script(f"""
                    game.keys['{direction}'] = true;
                    setTimeout(() => {{
                        game.keys['{direction}'] = false;
                        // 攻撃
                        const event = new KeyboardEvent('keydown', {{
                            key: ' ',
                            code: 'Space',
                            bubbles: true
                        }});
                        document.dispatchEvent(event);
                    }}, 300);
                """)
                time.sleep(0.5)
            
            pos = self.driver.execute_script("return {x: Math.round(game.player.x), y: Math.round(game.player.y)};")
            print(f"  最終位置: X:{pos['x']}, Y:{pos['y']}")
            
            # デモ3: 特殊攻撃
            print("\n[DEMO 3] 特殊攻撃デモ")
            
            # MP確認
            mp = self.driver.execute_script("return game.player.mp;")
            print(f"  現在のMP: {mp}")
            
            if mp >= 20:
                print("  特殊攻撃発動！")
                self.driver.execute_script("""
                    const event = new KeyboardEvent('keydown', {
                        key: 'E',
                        code: 'KeyE',
                        bubbles: true
                    });
                    document.dispatchEvent(event);
                """)
                time.sleep(2)
                
                mp_after = self.driver.execute_script("return game.player.mp;")
                print(f"  攻撃後のMP: {mp_after}")
            
            # デモ4: 複雑な動き
            print("\n[DEMO 4] 複雑な動きのパターン")
            
            # 円を描くように移動
            print("  円を描くように移動")
            movements = [
                ('ArrowRight', 'ArrowUp'),
                ('ArrowRight', 'ArrowDown'),
                ('ArrowLeft', 'ArrowDown'),
                ('ArrowLeft', 'ArrowUp')
            ]
            
            for keys in movements:
                self.driver.execute_script(f"""
                    game.keys['{keys[0]}'] = true;
                    game.keys['{keys[1]}'] = true;
                    setTimeout(() => {{
                        game.keys['{keys[0]}'] = false;
                        game.keys['{keys[1]}'] = false;
                    }}, 500);
                """)
                time.sleep(0.7)
            
            # デモ5: WASDキー
            print("\n[DEMO 5] WASDキーでの操作")
            
            wasd_keys = [
                ('w', '上'),
                ('d', '右'),
                ('s', '下'),
                ('a', '左')
            ]
            
            for key, direction in wasd_keys:
                print(f"  {key.upper()}キー: {direction}へ移動")
                self.driver.execute_script(f"""
                    game.keys['{key}'] = true;
                    setTimeout(() => {{
                        game.keys['{key}'] = false;
                    }}, 500);
                """)
                time.sleep(0.7)
                
                pos = self.driver.execute_script("return {x: Math.round(game.player.x), y: Math.round(game.player.y)};")
                print(f"    位置: X:{pos['x']}, Y:{pos['y']}")
            
            # 最終状態確認
            print("\n=== 最終状態 ===")
            
            final_status = self.driver.execute_script("""
                return {
                    x: Math.round(game.player.x),
                    y: Math.round(game.player.y),
                    hp: game.player.hp,
                    mp: game.player.mp,
                    level: game.player.level,
                    score: game.player.score,
                    enemyCount: game.enemies.length,
                    facing: game.player.facing
                };
            """)
            
            print(f"位置: X:{final_status['x']}, Y:{final_status['y']}")
            print(f"HP: {final_status['hp']}/100")
            print(f"MP: {final_status['mp']}/50")
            print(f"レベル: {final_status['level']}")
            print(f"スコア: {final_status['score']}")
            print(f"敵の数: {final_status['enemyCount']}")
            print(f"向き: {final_status['facing']}")
            
            # 画面表示確認
            position_elem = self.driver.find_element(By.ID, "position")
            print(f"\n画面の座標表示: {position_elem.text}")
            
            # スクリーンショット
            self.driver.save_screenshot("action_rpg_selenium_fix.png")
            print("\n[INFO] スクリーンショット保存: action_rpg_selenium_fix.png")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] デモ中にエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(3)
            self.driver.quit()
            print("[INFO] デモ終了")

def main():
    print("=== アクションRPG Selenium修正版デモ ===\n")
    print("特徴:")
    print("- JavaScriptでgame.keysを直接操作")
    print("- キーイベントの確実な発火")
    print("- 座標の変化を確認")
    print("- 攻撃システムも含めたデモ\n")
    
    demo = ActionRPGSeleniumFix()
    
    try:
        demo.setup_driver()
        demo.show_movement()
        
    except KeyboardInterrupt:
        print("\n[INFO] 中断されました")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()