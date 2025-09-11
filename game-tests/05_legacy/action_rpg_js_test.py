#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アクションRPG座標確認 - JavaScript直接実行版
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

class PositionTestJSDemo:
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
        print("[INFO] JavaScript座標確認デモ開始！")
        
    def test_movement(self):
        """JavaScriptで直接移動を確認"""
        try:
            # ゲームを開く
            game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\action_rpg.html"
            self.driver.get(f"file:///{game_path}")
            time.sleep(3)
            
            print("\n=== JavaScript直接操作テスト ===")
            print("JavaScriptから直接ゲーム変数を操作します\n")
            
            # 初期状態確認
            status = self.driver.execute_script("""
                return {
                    x: game.player.x,
                    y: game.player.y,
                    speed: game.player.speed,
                    keys: Object.keys(game.keys).filter(k => game.keys[k])
                };
            """)
            print(f"初期状態:")
            print(f"  座標: X:{status['x']}, Y:{status['y']}")
            print(f"  速度: {status['speed']}")
            print(f"  押されているキー: {status['keys']}\n")
            
            # テスト1: JavaScriptで直接プレイヤーを動かす
            print("[TEST 1] JavaScriptで直接移動")
            
            # 右に移動
            self.driver.execute_script("game.player.x += 100;")
            pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
            print(f"  右に100移動後: X:{pos['x']}, Y:{pos['y']}")
            
            # 下に移動
            self.driver.execute_script("game.player.y += 100;")
            pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
            print(f"  下に100移動後: X:{pos['x']}, Y:{pos['y']}")
            
            time.sleep(1)
            
            # テスト2: キー押下をシミュレート
            print("\n[TEST 2] キー押下シミュレーション")
            
            # ArrowRightキーを押した状態にする
            self.driver.execute_script("game.keys['ArrowRight'] = true;")
            print("  ArrowRightキーを押下状態に設定")
            
            # 0.5秒待機（ゲームループで移動が処理される）
            time.sleep(0.5)
            
            # キーを離す
            self.driver.execute_script("game.keys['ArrowRight'] = false;")
            pos = self.driver.execute_script("return {x: Math.round(game.player.x), y: Math.round(game.player.y)};")
            print(f"  0.5秒後の位置: X:{pos['x']}, Y:{pos['y']}")
            
            # テスト3: イベントディスパッチ
            print("\n[TEST 3] KeyboardEventディスパッチ")
            
            # 初期位置を記録
            initial_pos = self.driver.execute_script("return {x: game.player.x, y: game.player.y};")
            
            # KeyboardEventを作成して送信
            self.driver.execute_script("""
                // キーダウンイベント
                const downEvent = new KeyboardEvent('keydown', {
                    key: 'ArrowLeft',
                    code: 'ArrowLeft',
                    keyCode: 37,
                    bubbles: true
                });
                document.dispatchEvent(downEvent);
                
                // 一定時間押し続ける
                setTimeout(() => {
                    const upEvent = new KeyboardEvent('keyup', {
                        key: 'ArrowLeft',
                        code: 'ArrowLeft',
                        keyCode: 37,
                        bubbles: true
                    });
                    document.dispatchEvent(upEvent);
                }, 500);
            """)
            
            time.sleep(1)
            
            final_pos = self.driver.execute_script("return {x: Math.round(game.player.x), y: Math.round(game.player.y)};")
            print(f"  ArrowLeftイベント後: X:{final_pos['x']}, Y:{final_pos['y']}")
            print(f"  移動距離: X:{final_pos['x'] - initial_pos['x']}")
            
            # テスト4: 複数方向同時押し
            print("\n[TEST 4] 複数キー同時押し")
            
            self.driver.execute_script("""
                // 右下に移動
                game.keys['ArrowRight'] = true;
                game.keys['ArrowDown'] = true;
            """)
            
            time.sleep(1)
            
            self.driver.execute_script("""
                game.keys['ArrowRight'] = false;
                game.keys['ArrowDown'] = false;
            """)
            
            pos = self.driver.execute_script("return {x: Math.round(game.player.x), y: Math.round(game.player.y)};")
            print(f"  右下移動後: X:{pos['x']}, Y:{pos['y']}")
            
            # 画面表示の確認
            position_elem = self.driver.find_element(By.ID, "position")
            print(f"  画面表示: {position_elem.text}")
            
            # テスト5: ゲームループの確認
            print("\n[TEST 5] ゲームループ状態確認")
            
            loop_info = self.driver.execute_script("""
                // フレームカウントを記録
                const startFrame = game.frameCount;
                
                // 1秒後のフレーム数を確認
                return new Promise((resolve) => {
                    setTimeout(() => {
                        resolve({
                            startFrame: startFrame,
                            endFrame: game.frameCount,
                            fps: game.frameCount - startFrame,
                            updateFunctionExists: typeof update === 'function',
                            renderFunctionExists: typeof render === 'function'
                        });
                    }, 1000);
                });
            """)
            
            print(f"  ゲームループ状態:")
            print(f"    FPS: {loop_info['fps']}")
            print(f"    update関数: {'存在' if loop_info['updateFunctionExists'] else '存在しない'}")
            print(f"    render関数: {'存在' if loop_info['renderFunctionExists'] else '存在しない'}")
            
            # デバッグパネル確認
            debug_panel = self.driver.find_element(By.ID, "debugPanel")
            print(f"\n[デバッグパネル最新ログ]")
            logs = debug_panel.text.split('\n')[-5:]  # 最新5行
            for log in logs:
                if log and log != 'Battle Log':
                    print(f"  {log}")
            
            # スクリーンショット
            self.driver.save_screenshot("action_rpg_js_test.png")
            print("\n[INFO] スクリーンショット保存: action_rpg_js_test.png")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] テスト中にエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(3)
            self.driver.quit()
            print("[INFO] テスト終了")

def main():
    print("=== アクションRPG JavaScript座標確認テスト ===\n")
    print("このテストで確認すること:")
    print("1. JavaScriptから直接座標を変更できるか")
    print("2. game.keysの操作で移動するか")
    print("3. KeyboardEventで移動するか")
    print("4. ゲームループが正常に動作しているか\n")
    
    demo = PositionTestJSDemo()
    
    try:
        demo.setup_driver()
        demo.test_movement()
        
    except KeyboardInterrupt:
        print("\n[INFO] 中断されました")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()