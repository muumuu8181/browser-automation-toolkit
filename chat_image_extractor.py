#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
チャット画像抽出ツール - Seleniumでブラウザから画像を保存
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import requests
import os
from urllib.parse import urlparse

class ChatImageExtractor:
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
        print("[INFO] 画像抽出用ブラウザ起動！")
        
    def extract_chat_images(self, chat_url):
        """チャット画面から画像を抽出"""
        try:
            print(f"[INFO] チャット画面にアクセス: {chat_url}")
            self.driver.get(chat_url)
            time.sleep(3)
            
            # 画像要素を検索
            images = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"[INFO] {len(images)}個の画像を発見")
            
            saved_images = []
            save_dir = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game"
            
            for i, img in enumerate(images):
                try:
                    src = img.get_attribute('src')
                    alt = img.get_attribute('alt') or f"image_{i}"
                    
                    if src and src.startswith(('data:', 'blob:', 'http')):
                        print(f"[INFO] 画像 {i+1}: {alt}")
                        
                        if src.startswith('data:'):
                            # Base64データの場合
                            self.save_base64_image(src, f"{save_dir}/chat_image_{i+1}.png")
                            saved_images.append(f"chat_image_{i+1}.png")
                            
                        elif src.startswith(('http', 'blob:')):
                            # URLまたはBlob URLの場合
                            filename = self.download_image(src, f"{save_dir}/chat_image_{i+1}")
                            if filename:
                                saved_images.append(filename)
                    
                except Exception as e:
                    print(f"[WARNING] 画像 {i+1} の処理中にエラー: {str(e)}")
                    continue
            
            print(f"[SUCCESS] {len(saved_images)}個の画像を保存しました:")
            for img in saved_images:
                print(f"  - {img}")
            
            return saved_images
            
        except Exception as e:
            print(f"[ERROR] 画像抽出中にエラー: {str(e)}")
            return []
    
    def save_base64_image(self, data_url, filepath):
        """Base64画像データを保存"""
        try:
            import base64
            from io import BytesIO
            
            # data:image/png;base64, の部分を除去
            header, data = data_url.split(',', 1)
            image_data = base64.b64decode(data)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
                
            print(f"[SUCCESS] Base64画像を保存: {filepath}")
            return os.path.basename(filepath)
            
        except Exception as e:
            print(f"[ERROR] Base64画像の保存エラー: {str(e)}")
            return None
    
    def download_image(self, url, filepath_base):
        """URLから画像をダウンロード"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Content-Typeから拡張子を推定
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    ext = '.jpg'  # デフォルト
                
                filepath = filepath_base + ext
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"[SUCCESS] 画像をダウンロード: {filepath}")
                return os.path.basename(filepath)
            else:
                print(f"[ERROR] ダウンロード失敗: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[ERROR] ダウンロードエラー: {str(e)}")
            return None
    
    def create_image_game(self, image_filename):
        """抽出した画像を使うゲームを作成"""
        game_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Action RPG - {image_filename}背景版</title>
    <style>
        canvas {{
            border: 3px solid #0f4c75;
            background-image: url('{image_filename}');
            background-size: cover;
            background-position: center;
            cursor: crosshair;
        }}
        body {{
            margin: 0;
            padding: 20px;
            background-color: #1a1a2e;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
        }}
        .overlay {{
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>Action RPG - カスタム背景版</h1>
    <p>背景画像: {image_filename}</p>
    
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    
    <div class="overlay">
        <div>移動: 矢印キー/WASD</div>
        <div>座標: <span id="position">X:400 Y:300</span></div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        const game = {{
            player: {{
                x: 400, y: 300, width: 32, height: 32,
                speed: 5, color: '#e94560', facing: 'right'
            }},
            keys: {{}}
        }};
        
        document.addEventListener('keydown', (e) => {{ game.keys[e.key] = true; }});
        document.addEventListener('keyup', (e) => {{ game.keys[e.key] = false; }});
        
        function update() {{
            const speed = game.player.speed;
            
            if (game.keys['ArrowLeft'] || game.keys['a']) {{
                game.player.x = Math.max(0, game.player.x - speed);
                game.player.facing = 'left';
            }}
            if (game.keys['ArrowRight'] || game.keys['d']) {{
                game.player.x = Math.min(canvas.width - 32, game.player.x + speed);
                game.player.facing = 'right';
            }}
            if (game.keys['ArrowUp'] || game.keys['w']) {{
                game.player.y = Math.max(0, game.player.y - speed);
            }}
            if (game.keys['ArrowDown'] || game.keys['s']) {{
                game.player.y = Math.min(canvas.height - 32, game.player.y + speed);
            }}
            
            document.getElementById('position').textContent = 
                `X:${{Math.round(game.player.x)}} Y:${{Math.round(game.player.y)}}`;
        }}
        
        function render() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 半透明オーバーレイ
            ctx.fillStyle = 'rgba(15, 52, 96, 0.3)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // プレイヤー
            ctx.fillStyle = game.player.color;
            ctx.fillRect(game.player.x, game.player.y, 32, 32);
            
            // 輪郭
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.strokeRect(game.player.x, game.player.y, 32, 32);
        }}
        
        function gameLoop() {{
            update();
            render();
            requestAnimationFrame(gameLoop);
        }}
        
        gameLoop();
    </script>
</body>
</html>"""
        
        game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
        with open(game_path, 'w', encoding='utf-8') as f:
            f.write(game_html)
        
        print(f"[SUCCESS] カスタム背景ゲームを作成: {game_path}")
        return game_path
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            print("[INFO] ブラウザを閉じました")

def main():
    print("=== チャット画像抽出ツール ===\\n")
    
    extractor = ChatImageExtractor()
    
    try:
        extractor.setup_driver()
        
        # チャット画面のURLを取得（現在のブラウザから）
        current_url = input("チャット画面のURLを入力してください（Enterでスキップ）: ").strip()
        
        if not current_url:
            print("[INFO] ブラウザを手動でチャット画面に移動してください...")
            input("準備ができたらEnterを押してください")
            current_url = extractor.driver.current_url
        
        # 画像を抽出
        saved_images = extractor.extract_chat_images(current_url)
        
        if saved_images:
            # 最初の画像でゲームを作成
            game_path = extractor.create_image_game(saved_images[0])
            print(f"\\n[INFO] ゲームファイル: {game_path}")
            
            # ブラウザでゲームを開く
            extractor.driver.get(f"file:///{game_path}")
            input("\\nゲームをお楽しみください！終了するにはEnterを押してください")
        else:
            print("[WARNING] 画像が見つからませんでした")
        
    except KeyboardInterrupt:
        print("\\n[INFO] 中断されました")
    except Exception as e:
        print(f"[ERROR] エラー: {str(e)}")
    finally:
        extractor.cleanup()

if __name__ == "__main__":
    main()