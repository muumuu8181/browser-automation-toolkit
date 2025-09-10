#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patersログインページの要素調査スクリプト
実際のログインは行わず、ページ構造を分析します
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

class PatersElementInspector:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """ブラウザドライバーの設定"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        
    def inspect_login_page(self):
        """ログインページの要素を調査"""
        try:
            print("[INFO] Patersログインページにアクセス中...")
            self.driver.get("https://paters.jp/users/sign_in")
            time.sleep(3)
            
            print("[SUCCESS] ページにアクセスしました")
            print(f"[INFO] ページタイトル: {self.driver.title}")
            print(f"[INFO] 現在のURL: {self.driver.current_url}")
            
            # フォーム要素を探す
            print("\n[INFO] フォーム要素を探索中...")
            
            # すべてのフォームを取得
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            print(f"[INFO] 見つかったフォーム数: {len(forms)}")
            
            for i, form in enumerate(forms):
                print(f"\n--- フォーム {i+1} ---")
                try:
                    form_action = form.get_attribute("action")
                    form_method = form.get_attribute("method")
                    print(f"Action: {form_action}")
                    print(f"Method: {form_method}")
                except:
                    pass
            
            # input要素を探す
            print("\n[INFO] input要素を探索中...")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            input_data = []
            for inp in inputs:
                try:
                    input_info = {
                        "type": inp.get_attribute("type"),
                        "name": inp.get_attribute("name"),
                        "id": inp.get_attribute("id"),
                        "placeholder": inp.get_attribute("placeholder"),
                        "value": inp.get_attribute("value"),
                        "class": inp.get_attribute("class")
                    }
                    input_data.append(input_info)
                except:
                    pass
            
            print(f"\n[INFO] 見つかったinput要素:")
            for i, inp in enumerate(input_data):
                print(f"\nInput {i+1}:")
                print(f"  Type: {inp['type']}")
                print(f"  Name: {inp['name']}")
                print(f"  ID: {inp['id']}")
                print(f"  Placeholder: {inp['placeholder']}")
                if inp['type'] == 'submit':
                    print(f"  Value: {inp['value']}")
            
            # ボタン要素を探す
            print("\n[INFO] button要素を探索中...")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"[INFO] 見つかったbutton要素数: {len(buttons)}")
            
            for i, btn in enumerate(buttons):
                try:
                    btn_text = btn.text
                    btn_type = btn.get_attribute("type")
                    print(f"\nButton {i+1}:")
                    print(f"  Text: {btn_text}")
                    print(f"  Type: {btn_type}")
                except:
                    pass
            
            # スクリーンショットを保存
            screenshot_path = "paters_login_page.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"\n[INFO] スクリーンショットを保存しました: {screenshot_path}")
            
            # ページソースの一部を保存（デバッグ用）
            with open("paters_login_structure.txt", "w", encoding="utf-8") as f:
                f.write("=== Patersログインページ構造分析 ===\n\n")
                f.write(f"URL: {self.driver.current_url}\n")
                f.write(f"Title: {self.driver.title}\n\n")
                f.write("Input要素:\n")
                f.write(json.dumps(input_data, indent=2, ensure_ascii=False))
            
            print("[INFO] ページ構造をpaters_login_structure.txtに保存しました")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] ページ調査中にエラーが発生: {str(e)}")
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(3)  # 確認のため少し待機
            self.driver.quit()
            print("[INFO] ブラウザを閉じました")

def main():
    """メイン実行関数"""
    print("=== Patersログインページ要素調査 ===\n")
    print("[NOTE] このスクリプトは実際のログインは行いません")
    print("[NOTE] ページ構造の分析のみを行います\n")
    
    inspector = PatersElementInspector()
    
    try:
        inspector.setup_driver()
        success = inspector.inspect_login_page()
        
        if success:
            print("\n[SUCCESS] ページ調査が完了しました")
            print("[INFO] 分析結果を確認してください:")
            print("  - paters_login_page.png (スクリーンショット)")
            print("  - paters_login_structure.txt (要素情報)")
        
    except KeyboardInterrupt:
        print("\n[INFO] ユーザーによって中断されました")
    finally:
        inspector.cleanup()

if __name__ == "__main__":
    main()