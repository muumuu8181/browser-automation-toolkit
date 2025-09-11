#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
デバッグ版RPGプレイヤー - 何が起きているか詳しく見る
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import math

class DebugRPGPlayer:
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
        print("[INFO] ブラウザ起動完了")
        
    def test_basic_mechanics(self):
        """基本的なゲームメカニクスをテスト"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(2)
            
            # キャンバスにフォーカス
            canvas = self.driver.find_element(By.ID, "gameCanvas")
            canvas.click()
            
            print("\n=== デバッグテスト開始 ===\n")
            
            # 1. 初期状態の確認
            initial_state = self.driver.execute_script("""
                return {
                    player: game.player,
                    enemies: game.enemies.length,
                    projectiles: game.projectiles.length
                };
            """)
            print(f"[初期状態]")
            print(f"  プレイヤー: X={initial_state['player']['x']}, Y={initial_state['player']['y']}")
            print(f"  HP: {initial_state['player']['hp']}/{initial_state['player']['maxHp']}")
            print(f"  MP: {initial_state['player']['mp']}/{initial_state['player']['maxMp']}")
            print(f"  敵の数: {initial_state['enemies']}")
            print(f"  弾の数: {initial_state['projectiles']}\n")
            
            # 2. 移動テスト
            print("[テスト1: 移動]")
            print("  右に移動...")
            self.driver.execute_script("""
                game.keys['d'] = true;
                game.keys['D'] = true;
                game.keys['ArrowRight'] = true;
            """)
            time.sleep(1)
            self.driver.execute_script("""
                game.keys['d'] = false;
                game.keys['D'] = false;
                game.keys['ArrowRight'] = false;
            """)
            
            pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
            print(f"  移動後の位置: X={pos['x']}, Y={pos['y']}")
            print(f"  移動距離: {pos['x'] - initial_state['player']['x']}ピクセル\n")
            
            # 3. 攻撃テスト
            print("[テスト2: 通常攻撃]")
            
            # 攻撃前の状態
            pre_attack = self.driver.execute_script("""
                return {
                    projectiles: game.projectiles.length,
                    facing: game.player.facing,
                    attackCooldown: game.player.attackCooldown
                };
            """)
            print(f"  現在の向き: {pre_attack['facing']}")
            print(f"  攻撃前の弾数: {pre_attack['projectiles']}")
            
            # 攻撃実行
            print("  スペースキーで攻撃...")
            self.driver.execute_script("""
                // 直接攻撃関数を呼ぶ
                playerAttack();
            """)
            time.sleep(0.1)
            
            # 攻撃後の状態
            post_attack = self.driver.execute_script("""
                return {
                    projectiles: game.projectiles.length,
                    lastProjectile: game.projectiles[game.projectiles.length - 1],
                    attackCooldown: game.player.attackCooldown
                };
            """)
            print(f"  攻撃後の弾数: {post_attack['projectiles']}")
            
            if post_attack['projectiles'] > pre_attack['projectiles']:
                proj = post_attack['lastProjectile']
                print(f"  新しい弾: X={proj['x']:.0f}, Y={proj['y']:.0f}, 速度=({proj['dx']:.0f}, {proj['dy']:.0f})")
            else:
                print("  [警告] 弾が発射されませんでした！")
                print(f"  クールダウン: {post_attack['attackCooldown']}")
            
            # 4. 特殊攻撃テスト
            print("\n[テスト3: 特殊攻撃]")
            
            # MP回復
            self.driver.execute_script("game.player.mp = game.player.maxMp;")
            
            pre_special = self.driver.execute_script("""
                return {
                    mp: game.player.mp,
                    projectiles: game.projectiles.length
                };
            """)
            print(f"  MP: {pre_special['mp']}")
            print(f"  特殊攻撃前の弾数: {pre_special['projectiles']}")
            
            # 特殊攻撃
            print("  Eキーで特殊攻撃...")
            self.driver.execute_script("specialAttack();")
            time.sleep(0.1)
            
            post_special = self.driver.execute_script("""
                return {
                    mp: game.player.mp,
                    projectiles: game.projectiles.length
                };
            """)
            print(f"  特殊攻撃後のMP: {post_special['mp']}")
            print(f"  特殊攻撃後の弾数: {post_special['projectiles']}")
            print(f"  発射された弾: {post_special['projectiles'] - pre_special['projectiles']}発\n")
            
            # 5. 敵への攻撃テスト
            print("[テスト4: 敵への攻撃]")
            
            # 敵を近くに配置
            self.driver.execute_script("""
                if (game.enemies.length > 0) {
                    // 最初の敵をプレイヤーの右側に配置
                    game.enemies[0].x = game.player.x + 100;
                    game.enemies[0].y = game.player.y;
                    game.enemies[0].hp = 30;
                }
            """)
            
            # 右を向く
            self.driver.execute_script("""
                game.player.facing = 'right';
            """)
            
            enemy_before = self.driver.execute_script("""
                if (game.enemies.length > 0) {
                    return {
                        exists: true,
                        x: game.enemies[0].x,
                        y: game.enemies[0].y,
                        hp: game.enemies[0].hp
                    };
                }
                return {exists: false};
            """)
            
            if enemy_before['exists']:
                print(f"  敵の位置: X={enemy_before['x']}, Y={enemy_before['y']}")
                print(f"  敵のHP: {enemy_before['hp']}")
                print("  右に向かって攻撃...")
                
                # 複数回攻撃
                for i in range(3):
                    self.driver.execute_script("playerAttack();")
                    time.sleep(0.5)
                    
                    # 弾と敵の状態を確認
                    status = self.driver.execute_script("""
                        const result = {
                            projectiles: game.projectiles.length,
                            enemyCount: game.enemies.length,
                            score: game.player.score
                        };
                        
                        if (game.enemies.length > 0) {
                            result.enemyHp = game.enemies[0].hp;
                            result.enemyX = game.enemies[0].x;
                        }
                        
                        return result;
                    """)
                    
                    print(f"  攻撃{i+1}: 弾数={status['projectiles']}, スコア={status['score']}")
                    if status['enemyCount'] > 0:
                        print(f"    敵HP: {status.get('enemyHp', 'N/A')}")
            
            # 6. ゲームログの確認
            print("\n[テスト5: コンソールログ確認]")
            logs = self.driver.get_log('browser')
            game_logs = [log for log in logs if '[ACTION RPG]' in log['message']]
            print(f"  ゲームログ数: {len(game_logs)}")
            for log in game_logs[-5:]:  # 最新5件
                print(f"  {log['message']}")
                
            # 最終状態
            print("\n[最終状態]")
            final_state = self.driver.execute_script("""
                return {
                    player: {
                        x: game.player.x,
                        y: game.player.y,
                        hp: game.player.hp,
                        mp: game.player.mp,
                        score: game.player.score,
                        facing: game.player.facing
                    },
                    enemies: game.enemies.length,
                    projectiles: game.projectiles.length
                };
            """)
            print(f"  プレイヤー位置: X={final_state['player']['x']}, Y={final_state['player']['y']}")
            print(f"  HP: {final_state['player']['hp']}, MP: {final_state['player']['mp']}")
            print(f"  スコア: {final_state['player']['score']}")
            print(f"  残り敵数: {final_state['enemies']}")
            
        except Exception as e:
            print(f"[ERROR] テスト中にエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def cleanup(self):
        if self.driver:
            time.sleep(5)
            self.driver.quit()

def main():
    print("=== RPGゲーム デバッグテスト ===\n")
    
    player = DebugRPGPlayer()
    
    try:
        player.setup_driver()
        player.test_basic_mechanics()
    finally:
        player.cleanup()

if __name__ == "__main__":
    main()