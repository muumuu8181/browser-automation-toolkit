#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アクションRPG戦闘デモ - 攻撃システムを使った激しいバトル
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
from datetime import datetime

class ActionRPGDemo:
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
        print("[INFO] アクションRPGデモ開始！")
        
    def show_battle(self):
        """激しいアクションバトルを実演"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\action_rpg.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(2)
            
            print("\n=== アクションRPGバトル開始！ ===")
            print("[INFO] 攻撃システム搭載 - スペースで撃つ、Eで必殺技！\n")
            
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # バトルパターン1: 基本戦闘
            print("[PHASE 1] 基本戦闘訓練")
            print("  > 上下左右に移動しながら攻撃")
            
            for _ in range(5):
                # 上に移動して撃つ
                body.send_keys(Keys.UP * 3)
                time.sleep(0.2)
                body.send_keys(Keys.SPACE)
                print("  ↑ 上方向に移動＆攻撃！")
                
                # 右に移動して撃つ
                body.send_keys(Keys.RIGHT * 3)
                time.sleep(0.2)
                body.send_keys(Keys.SPACE)
                print("  → 右方向に移動＆攻撃！")
                
                # 下に移動して撃つ
                body.send_keys(Keys.DOWN * 3)
                time.sleep(0.2)
                body.send_keys(Keys.SPACE)
                print("  ↓ 下方向に移動＆攻撃！")
                
                # 左に移動して撃つ
                body.send_keys(Keys.LEFT * 3)
                time.sleep(0.2)
                body.send_keys(Keys.SPACE)
                print("  ← 左方向に移動＆攻撃！")
                
                time.sleep(0.5)
            
            # バトルパターン2: 特殊攻撃
            print("\n[PHASE 2] 特殊攻撃デモ")
            time.sleep(1)
            
            print("  > E キーで全方向攻撃！")
            body.send_keys("E")
            time.sleep(1)
            
            # バトルパターン3: ダッシュ回避
            print("\n[PHASE 3] ダッシュ回避戦術")
            print("  > Shiftでダッシュしながら戦闘")
            
            # Shiftを押しながら移動
            body.send_keys(Keys.SHIFT + Keys.UP * 5)
            print("  ↑ 高速ダッシュ！")
            time.sleep(0.3)
            
            body.send_keys(Keys.SHIFT + Keys.RIGHT * 5)
            print("  → 右へ緊急回避！")
            time.sleep(0.3)
            
            # バトルパターン4: コンボ攻撃
            print("\n[PHASE 4] コンボ攻撃")
            print("  > 連続攻撃でコンボを稼ぐ")
            
            for i in range(10):
                # ランダムな方向に移動
                direction = random.choice([Keys.UP, Keys.DOWN, Keys.LEFT, Keys.RIGHT])
                body.send_keys(direction * 2)
                time.sleep(0.1)
                
                # 攻撃
                body.send_keys(Keys.SPACE)
                print(f"  コンボ {i+1} HIT!")
                time.sleep(0.2)
            
            # バトルパターン5: ボス戦シミュレーション
            print("\n[PHASE 5] ボス戦シミュレーション")
            time.sleep(1)
            
            # 追加の敵を召喚
            self.driver.execute_script("""
                // ボス召喚
                for(let i = 0; i < 5; i++) {
                    spawnEnemy('tank');
                }
                spawnEnemy('shooter');
                spawnEnemy('shooter');
                console.warn('[ACTION RPG] ボス級の敵が大量出現！');
            """)
            
            print("  > ボス級の敵が出現！激しい戦闘開始！")
            
            # 激しい戦闘
            for _ in range(20):
                # ジグザグ移動
                body.send_keys(Keys.UP * 2)
                body.send_keys(Keys.SPACE)
                body.send_keys(Keys.RIGHT * 2)
                body.send_keys(Keys.SPACE)
                body.send_keys(Keys.DOWN * 2)
                body.send_keys(Keys.SPACE)
                body.send_keys(Keys.LEFT * 2)
                body.send_keys(Keys.SPACE)
                time.sleep(0.1)
            
            # 必殺技連発
            print("\n  > MP全開放！必殺技ラッシュ！")
            for _ in range(3):
                body.send_keys("E")
                print("  [!!!] 必殺技発動！")
                time.sleep(1)
            
            # 最終段階
            print("\n[FINAL] 超高速戦闘モード")
            print("  > 全力で動き回りながら攻撃！")
            
            start_time = time.time()
            action_count = 0
            
            while time.time() - start_time < 5:  # 5秒間
                # ランダムアクション
                actions = [
                    (Keys.UP, "↑"),
                    (Keys.DOWN, "↓"),
                    (Keys.LEFT, "←"),
                    (Keys.RIGHT, "→"),
                    (Keys.SPACE, "*"),
                    ("E", "#")
                ]
                
                action, symbol = random.choice(actions)
                body.send_keys(action)
                print(symbol, end="", flush=True)
                action_count += 1
                time.sleep(0.05)
            
            print(f"\n\n[RESULT] {action_count}回のアクションを実行！")
            
            # 戦闘結果を取得
            time.sleep(1)
            result = self.driver.execute_script("""
                return {
                    hp: game.player.hp,
                    mp: game.player.mp,
                    level: game.player.level,
                    score: game.player.score,
                    combo: game.player.combo,
                    enemies: game.enemies.length,
                    projectiles: game.projectiles.length
                };
            """)
            
            print("\n=== 戦闘結果 ===")
            print(f"HP: {result['hp']}/100")
            print(f"MP: {result['mp']}/50") 
            print(f"レベル: {result['level']}")
            print(f"スコア: {result['score']}")
            print(f"最大コンボ: {result['combo']}")
            print(f"残存敵: {result['enemies']}")
            print(f"画面上の弾: {result['projectiles']}")
            
            # スクリーンショット
            self.driver.save_screenshot("action_rpg_battle.png")
            print("\n[INFO] 戦闘スクリーンショット保存: action_rpg_battle.png")
            
            # ログ取得
            logs = self.driver.get_log('browser')
            rpg_logs = [log for log in logs if '[ACTION RPG]' in log['message']]
            print(f"\n[INFO] 戦闘ログ数: {len(rpg_logs)}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] デモ中にエラー: {str(e)}")
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(5)  # 結果を見るため
            self.driver.quit()
            print("[INFO] デモ終了")

def main():
    print("=== アクションRPG戦闘システムデモ ===\n")
    print("特徴:")
    print("- 4方向への移動と攻撃")
    print("- 通常攻撃（スペース）と特殊攻撃（E）")
    print("- ダッシュシステム（Shift）")
    print("- 複数の敵タイプ（通常、高速、タンク、射撃）")
    print("- コンボシステムとスコア")
    print("- アイテムドロップ\n")
    
    demo = ActionRPGDemo()
    
    try:
        demo.setup_driver()
        demo.show_battle()
        
    except KeyboardInterrupt:
        print("\n[INFO] 中断されました")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()