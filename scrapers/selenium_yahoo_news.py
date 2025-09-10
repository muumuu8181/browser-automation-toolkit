#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium でYahooニュースデータを収集（学習・研究目的）
"""

import requests
import zipfile
import os
import tempfile
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import re

def get_chrome_version():
    """Chromeバージョン取得"""
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        result = subprocess.run([chrome_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            return version
    except:
        pass
    return "139.0.7258.155"

def download_chromedriver():
    """ChromeDriverをダウンロード"""
    chrome_version = get_chrome_version()
    major_version = chrome_version.split('.')[0]
    
    try:
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        for version_info in data['versions']:
            if version_info['version'].startswith(f"{major_version}."):
                if 'chromedriver' in version_info['downloads']:
                    for download in version_info['downloads']['chromedriver']:
                        if download['platform'] == 'win64':
                            temp_dir = tempfile.mkdtemp()
                            zip_path = os.path.join(temp_dir, 'chromedriver.zip')
                            
                            with requests.get(download['url'], stream=True, timeout=30) as r:
                                r.raise_for_status()
                                with open(zip_path, 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                            
                            extract_path = os.path.join(temp_dir, 'extracted')
                            os.makedirs(extract_path, exist_ok=True)
                            
                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                zip_ref.extractall(extract_path)
                            
                            for root, dirs, files in os.walk(extract_path):
                                for file in files:
                                    if file == 'chromedriver.exe':
                                        return os.path.join(root, file)
                            break
                    break
    except Exception as e:
        print(f"[ERROR] ChromeDriverダウンロード失敗: {e}")
    return None

class SeleniumYahooNewsScraper:
    def __init__(self):
        self.driver = None
        self.news_data = []
        
    def setup_browser(self):
        """ブラウザセットアップ"""
        print("[INFO] Seleniumでブラウザを起動...")
        
        driver_path = download_chromedriver()
        if not driver_path:
            print("[ERROR] ChromeDriverが取得できません")
            return False
        
        options = Options()
        options.add_argument('--headless')  # バックグラウンド実行
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            print("[SUCCESS] ブラウザ起動成功")
            return True
        except Exception as e:
            print(f"[ERROR] ブラウザ起動エラー: {e}")
            return False
    
    def scrape_yahoo_news(self):
        """Yahooニュースをスクレイピング"""
        print("\n=== Selenium Yahooニュース収集 ===")
        
        if not self.setup_browser():
            return False
        
        try:
            url = "https://news.yahoo.co.jp/"
            print(f"[INFO] アクセス: {url}")
            
            self.driver.get(url)
            time.sleep(3)  # ページ読み込み待機
            
            print("[INFO] ニュース記事を検索中...")
            
            # ニュース記事のリンクを取得
            news_links = []
            
            # 複数のセレクターを試す
            selectors = [
                'a[href*="/articles/"]',  # Yahoo記事リンク
                'div[class*="newsList"] a',
                'div[class*="topicsListItem"] a',
                'article a',
                '.newsFeed a'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements[:20]:  # 最初の20件
                        href = element.get_attribute('href')
                        text = element.get_attribute('textContent') or element.text
                        if href and 'yahoo.co.jp' in href and text.strip():
                            news_links.append({
                                'url': href,
                                'title': text.strip(),
                                'selector': selector
                            })
                except Exception as e:
                    continue
            
            print(f"[INFO] {len(news_links)}件のニュースリンクを発見")
            
            # 重複を除去
            unique_links = []
            seen_urls = set()
            for link in news_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            print(f"[INFO] 重複除去後: {len(unique_links)}件")
            
            # 詳細情報を取得（最初の10件）
            for i, link in enumerate(unique_links[:10]):
                try:
                    print(f"[INFO] 記事 {i+1}/{min(10, len(unique_links))} を処理中...")
                    
                    # 記事ページにアクセス
                    self.driver.get(link['url'])
                    time.sleep(2)
                    
                    # 記事の詳細情報を取得
                    article_data = {
                        'url': link['url'],
                        'title': link['title'],
                        'content': '',
                        'timestamp': '',
                        'category': '',
                        'source': 'yahoo_news',
                        'scraped_at': time.time()
                    }
                    
                    # 記事本文を取得
                    content_selectors = [
                        'div[class*="articleBody"] p',
                        'div[class*="article"] p',
                        '.article-body p',
                        'article p'
                    ]
                    
                    for selector in content_selectors:
                        try:
                            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if paragraphs:
                                content_parts = [p.text.strip() for p in paragraphs if p.text.strip()]
                                if content_parts:
                                    article_data['content'] = '\n'.join(content_parts)
                                    break
                        except:
                            continue
                    
                    # タイムスタンプを取得
                    time_selectors = [
                        'time',
                        '.article-date',
                        '.timestamp',
                        '[class*="time"]'
                    ]
                    
                    for selector in time_selectors:
                        try:
                            time_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            article_data['timestamp'] = time_element.text.strip()
                            break
                        except:
                            continue
                    
                    self.news_data.append(article_data)
                    print(f"[SUCCESS] 記事収集完了: {article_data['title'][:50]}...")
                    
                except Exception as e:
                    print(f"[WARN] 記事処理エラー: {e}")
                    continue
            
            # 結果をファイルに保存
            result = {
                'tool': 'selenium',
                'success': len(self.news_data) > 0,
                'timestamp': time.time(),
                'total_articles': len(self.news_data),
                'articles': self.news_data,
                'source_url': url
            }
            
            output_file = 'selenium_yahoo_news.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n[SUMMARY] Selenium収集結果:")
            print(f"  - 総記事数: {len(self.news_data)}")
            print(f"  - 保存ファイル: {output_file}")
            
            for i, article in enumerate(self.news_data[:5]):
                print(f"  [{i+1}] {article['title'][:60]}...")
            
            self.driver.quit()
            
            if len(self.news_data) > 0:
                print(f"\n[SUCCESS] Seleniumによるニュース収集が成功しました！")
                return True
            else:
                print(f"\n[ERROR] ニュースが1件も収集できませんでした")
                return False
                
        except Exception as e:
            print(f"[ERROR] スクレイピングエラー: {e}")
            if self.driver:
                self.driver.quit()
            return False

def main():
    print("Selenium Yahoo!ニュース収集を開始します...\n")
    scraper = SeleniumYahooNewsScraper()
    success = scraper.scrape_yahoo_news()
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] Seleniumでニュース収集完了！")
        print("="*60)
    else:
        print("\n[ERROR] ニュース収集に失敗しました")

if __name__ == "__main__":
    main()