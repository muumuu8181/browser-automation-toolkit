#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patersログイン自動化スクリプト（Selenium版）
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from dotenv import load_dotenv

class PatersLoginAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """ブラウザドライバーの設定"""
        options = Options()
        # ヘッドレスモードを無効にして動作確認
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        
    def login(self, email, password):
        """ログイン処理"""
        try:
            print("[INFO] Patersログインページにアクセス中...")
            self.driver.get("https://paters.jp/users/sign_in")
            time.sleep(3)  # ページ読み込み待機
            
            print("[INFO] メールアドレスを入力...")
            # メールアドレス入力フィールドを探す（実際のIDはmail）
            email_selectors = [
                "#mail",
                "input[name='user[login]']",
                "input[placeholder*='電話番号またはメールアドレス']",
                "input[type='text'][name*='login']"
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if email_field:
                email_field.clear()
                email_field.send_keys(email)
                print("[SUCCESS] メールアドレス入力完了")
            else:
                print("[ERROR] メールアドレスフィールドが見つかりません")
                return False
            
            print("[INFO] パスワードを入力...")
            # パスワード入力フィールドを探す（実際のIDはpassword）
            password_selectors = [
                "#password",
                "input[name='user[password]']",
                "input[type='password']",
                "input[placeholder*='パスワード']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if password_field:
                password_field.clear()
                password_field.send_keys(password)
                print("[SUCCESS] パスワード入力完了")
            else:
                print("[ERROR] パスワードフィールドが見つかりません")
                return False
            
            print("[INFO] ログインボタンを探しています...")
            # ログインボタンを探す（実際はinput[type='submit']）
            login_button_selectors = [
                "input[type='submit'][value='ログイン']",
                "input[name='commit']",
                "input[type='submit']"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    if selector.startswith("button:contains"):
                        # XPathで部分一致検索
                        login_button = self.driver.find_element(
                            By.XPATH, "//button[contains(text(), 'ログイン')]"
                        )
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_button.is_displayed() and login_button.is_enabled():
                        break
                except:
                    continue
            
            if login_button:
                print("[INFO] ログインボタンをクリック...")
                login_button.click()
                
                # ログイン後の確認
                time.sleep(5)
                current_url = self.driver.current_url
                
                if "sign_in" not in current_url:
                    print(f"[SUCCESS] ログイン成功！現在のURL: {current_url}")
                    return True
                else:
                    print("[WARN] ログインに失敗した可能性があります")
                    # エラーメッセージを探す
                    error_selectors = [".alert", ".error", ".flash", "*[class*='error']"]
                    for selector in error_selectors:
                        try:
                            error_msg = self.driver.find_element(By.CSS_SELECTOR, selector)
                            print(f"[ERROR] エラーメッセージ: {error_msg.text}")
                        except:
                            pass
                    return False
            else:
                print("[ERROR] ログインボタンが見つかりません")
                return False
                
        except Exception as e:
            print(f"[ERROR] ログイン処理中にエラーが発生: {str(e)}")
            return False
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            print("[INFO] ブラウザを閉じました")

def main():
    """メイン実行関数"""
    print("=== Patersログイン自動化 ===\n")
    
    # 環境変数から認証情報を取得（.envファイル使用推奨）
    load_dotenv()
    email = os.getenv("PATERS_EMAIL")
    password = os.getenv("PATERS_PASSWORD")
    
    if not email or not password:
        print("[WARN] 環境変数が設定されていません。手動入力モードに切り替えます。")
        email = input("メールアドレス: ")
        password = input("パスワード: ")
    
    automation = PatersLoginAutomation()
    
    try:
        automation.setup_driver()
        success = automation.login(email, password)
        
        if success:
            print("\n[INFO] ログイン後の処理を実行できます")
            input("Enterキーを押すとブラウザを閉じます...")
        
    except KeyboardInterrupt:
        print("\n[INFO] ユーザーによって中断されました")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main()