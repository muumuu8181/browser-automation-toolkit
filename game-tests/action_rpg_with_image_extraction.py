#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アクションRPG + 画像抽出機能 - チャット画像を背景に設定
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import base64
import requests
import os

class ActionRPGWithImageExtraction:
    def __init__(self):
        self.driver = None
        self.extracted_images = []
        
    def setup_driver(self):
        """ブラウザ起動"""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL'}
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        print("[INFO] アクションRPG + 画像抽出デモ開始！")
        
    def extract_images_from_current_page(self):
        """現在のページから画像を抽出"""
        try:
            print("\n[INFO] 現在のページから画像を抽出中...")
            
            # 全ての画像要素を取得
            images = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"[INFO] {len(images)}個の画像要素を発見")
            
            save_dir = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game"
            extracted_files = []
            
            for i, img in enumerate(images):
                try:
                    src = img.get_attribute('src')
                    if not src:
                        continue
                        
                    print(f"[INFO] 処理中 {i+1}/{len(images)}: {src[:50]}...")
                    
                    if src.startswith('data:'):
                        # Base64画像データ
                        filename = f"extracted_image_{i+1}.png"
                        filepath = os.path.join(save_dir, filename)
                        
                        if self.save_base64_image(src, filepath):
                            extracted_files.append(filename)
                            print(f"[SUCCESS] Base64画像を保存: {filename}")
                    
                    elif src.startswith(('http', 'https')):
                        # URL画像
                        filename = f"extracted_image_{i+1}.jpg"
                        filepath = os.path.join(save_dir, filename)
                        
                        if self.download_image(src, filepath):
                            extracted_files.append(filename)
                            print(f"[SUCCESS] URL画像をダウンロード: {filename}")
                    
                    elif src.startswith('blob:'):
                        # Blob URL - JavaScriptで変換を試みる
                        canvas_data = self.driver.execute_script(f"""
                            return new Promise((resolve) => {{
                                const img = new Image();
                                img.crossOrigin = 'anonymous';
                                img.onload = function() {{
                                    const canvas = document.createElement('canvas');
                                    const ctx = canvas.getContext('2d');
                                    canvas.width = this.width;
                                    canvas.height = this.height;
                                    ctx.drawImage(this, 0, 0);
                                    resolve(canvas.toDataURL('image/png'));
                                }};
                                img.onerror = () => resolve(null);
                                img.src = '{src}';
                            }});
                        """)
                        
                        if canvas_data and canvas_data.startswith('data:'):
                            filename = f"extracted_image_{i+1}.png"
                            filepath = os.path.join(save_dir, filename)
                            
                            if self.save_base64_image(canvas_data, filepath):
                                extracted_files.append(filename)
                                print(f"[SUCCESS] Blob画像を保存: {filename}")
                        else:
                            print(f"[WARNING] Blob画像の変換に失敗")
                
                except Exception as e:
                    print(f"[WARNING] 画像 {i+1} の処理中にエラー: {str(e)}")
                    continue
            
            self.extracted_images = extracted_files
            print(f"\n[SUCCESS] {len(extracted_files)}個の画像を抽出しました:")
            for img in extracted_files:
                print(f"  - {img}")
            
            return extracted_files
            
        except Exception as e:
            print(f"[ERROR] 画像抽出中にエラー: {str(e)}")
            return []
    
    def save_base64_image(self, data_url, filepath):
        """Base64画像データを保存"""
        try:
            # data:image/png;base64, の部分を除去
            header, data = data_url.split(',', 1)
            image_data = base64.b64decode(data)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            return True
        except Exception as e:
            print(f"[ERROR] Base64保存エラー: {str(e)}")
            return False
    
    def download_image(self, url, filepath):
        """URL画像をダウンロード"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"[ERROR] HTTP {response.status_code}: {url}")
                return False
                
        except Exception as e:
            print(f"[ERROR] ダウンロードエラー: {str(e)}")
            return False
    
    def create_custom_bg_game(self, bg_image_filename):
        """抽出した画像を背景に使うゲームを作成"""
        game_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Action RPG - Custom Background</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #1a1a2e;
            font-family: 'Arial', sans-serif;
        }}
        
        .game-container {{
            text-align: center;
            background-color: #16213e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
        }}
        
        canvas {{
            border: 3px solid #0f4c75;
            background-image: url('{bg_image_filename}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            cursor: crosshair;
        }}
        
        .overlay-controls {{
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
        }}
        
        .bg-opacity {{
            margin-top: 10px;
            color: #ecf0f1;
        }}
        
        .bg-opacity input {{
            width: 100px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 10px;
            color: #ecf0f1;
        }}
        
        h1 {{
            color: #e94560;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }}
    </style>
</head>
<body>
    <div class="game-container">
        <h1>Action RPG - カスタム背景版</h1>
        <p style="color: #ecf0f1;">背景画像: {bg_image_filename}</p>
        
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <div class="stats">
            <span>座標: <span id="position" style="color: #f39c12; font-weight: bold;">X:400 Y:300</span></span>
            <span>HP: <span id="hp">100/100</span></span>
            <span>MP: <span id="mp">50/50</span></span>
            <span>スコア: <span id="score">0</span></span>
        </div>
    </div>
    
    <div class="overlay-controls">
        <div>移動: 矢印キー/WASD</div>
        <div>攻撃: スペース</div>
        <div>特殊攻撃: E</div>
        <div class="bg-opacity">
            背景透明度: <br>
            <input type="range" id="opacitySlider" min="0" max="100" value="70">
            <span id="opacityValue">70%</span>
        </div>
    </div>

    <script>
        console.log('[ACTION RPG] カスタム背景版 - ゲーム初期化開始');
        
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // 背景透明度調整
        document.getElementById('opacitySlider').addEventListener('input', function(e) {{
            const opacity = e.target.value / 100;
            document.getElementById('opacityValue').textContent = e.target.value + '%';
            game.bgOverlayOpacity = 1 - opacity;
        }});
        
        // ゲーム状態
        const game = {{
            player: {{
                x: 400, y: 300, width: 32, height: 32,
                speed: 5, hp: 100, maxHp: 100, mp: 50, maxMp: 50,
                score: 0, color: '#e94560', facing: 'right',
                attackCooldown: 0
            }},
            enemies: [],
            projectiles: [],
            particles: [],
            keys: {{}},
            frameCount: 0,
            bgOverlayOpacity: 0.3
        }};
        
        // 弾クラス
        class Projectile {{
            constructor(x, y, dx, dy) {{
                this.x = x; this.y = y;
                this.dx = dx; this.dy = dy;
                this.size = 8; this.color = '#f39c12';
                this.lifetime = 60;
            }}
            
            update() {{
                this.x += this.dx; this.y += this.dy;
                this.lifetime--;
                return this.lifetime > 0 && this.x > 0 && this.x < canvas.width && this.y > 0 && this.y < canvas.height;
            }}
            
            draw() {{
                ctx.shadowBlur = 10; ctx.shadowColor = this.color;
                ctx.fillStyle = this.color;
                ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill(); ctx.shadowBlur = 0;
            }}
        }}
        
        // 敵生成
        function spawnEnemy() {{
            const edge = Math.floor(Math.random() * 4);
            let x, y;
            switch(edge) {{
                case 0: x = Math.random() * canvas.width; y = -30; break;
                case 1: x = canvas.width + 30; y = Math.random() * canvas.height; break;
                case 2: x = Math.random() * canvas.width; y = canvas.height + 30; break;
                case 3: x = -30; y = Math.random() * canvas.height; break;
            }}
            
            game.enemies.push({{
                x: x, y: y, width: 32, height: 32,
                hp: 30, speed: 1 + Math.random() * 2,
                color: '#e74c3c'
            }});
        }}
        
        // 攻撃
        function playerAttack() {{
            if (game.player.attackCooldown > 0) return;
            game.player.attackCooldown = 15;
            const speed = 12;
            
            let dx = 0, dy = 0;
            switch(game.player.facing) {{
                case 'up': dy = -speed; break;
                case 'down': dy = speed; break;
                case 'left': dx = -speed; break;
                case 'right': dx = speed; break;
            }}
            
            game.projectiles.push(new Projectile(
                game.player.x + 16, game.player.y + 16, dx, dy
            ));
        }}
        
        // 特殊攻撃
        function specialAttack() {{
            if (game.player.mp < 20) return;
            game.player.mp -= 20;
            
            for (let angle = 0; angle < Math.PI * 2; angle += Math.PI / 4) {{
                const speed = 8;
                game.projectiles.push(new Projectile(
                    game.player.x + 16, game.player.y + 16,
                    Math.cos(angle) * speed, Math.sin(angle) * speed
                ));
            }}
        }}
        
        // キー入力
        document.addEventListener('keydown', (e) => {{
            game.keys[e.key] = true;
            if (e.key === ' ') {{ e.preventDefault(); playerAttack(); }}
            if (e.key === 'e' || e.key === 'E') {{ e.preventDefault(); specialAttack(); }}
        }});
        document.addEventListener('keyup', (e) => {{ game.keys[e.key] = false; }});
        
        // 更新
        function update() {{
            const speed = game.player.speed;
            
            if (game.keys['ArrowLeft'] || game.keys['a'] || game.keys['A']) {{
                game.player.x = Math.max(0, game.player.x - speed);
                game.player.facing = 'left';
            }}
            if (game.keys['ArrowRight'] || game.keys['d'] || game.keys['D']) {{
                game.player.x = Math.min(canvas.width - 32, game.player.x + speed);
                game.player.facing = 'right';
            }}
            if (game.keys['ArrowUp'] || game.keys['w'] || game.keys['W']) {{
                game.player.y = Math.max(0, game.player.y - speed);
                game.player.facing = 'up';
            }}
            if (game.keys['ArrowDown'] || game.keys['s'] || game.keys['S']) {{
                game.player.y = Math.min(canvas.height - 32, game.player.y + speed);
                game.player.facing = 'down';
            }}
            
            // クールダウン
            if (game.player.attackCooldown > 0) game.player.attackCooldown--;
            if (game.frameCount % 30 === 0 && game.player.mp < game.player.maxMp) game.player.mp++;
            
            // 弾の更新
            game.projectiles = game.projectiles.filter(proj => {{
                if (!proj.update()) return false;
                
                for (let i = game.enemies.length - 1; i >= 0; i--) {{
                    const enemy = game.enemies[i];
                    if (Math.abs(proj.x - (enemy.x + 16)) < 24 && Math.abs(proj.y - (enemy.y + 16)) < 24) {{
                        enemy.hp -= 15;
                        if (enemy.hp <= 0) {{
                            game.enemies.splice(i, 1);
                            game.player.score += 10;
                        }}
                        return false;
                    }}
                }}
                return true;
            }});
            
            // 敵の移動
            game.enemies.forEach(enemy => {{
                const dx = game.player.x - enemy.x;
                const dy = game.player.y - enemy.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist > 0) {{
                    enemy.x += (dx / dist) * enemy.speed;
                    enemy.y += (dy / dist) * enemy.speed;
                }}
                
                // 衝突判定
                if (Math.abs(enemy.x - game.player.x) < 32 && Math.abs(enemy.y - game.player.y) < 32) {{
                    game.player.hp = Math.max(0, game.player.hp - 1);
                }}
            }});
            
            // パーティクル更新
            game.particles = game.particles.filter(p => {{
                p.x += p.dx; p.y += p.dy; p.lifetime--; p.size *= 0.95;
                return p.lifetime > 0;
            }});
            
            // 敵スポーン
            if (game.frameCount % 120 === 0) spawnEnemy();
            
            // UI更新
            document.getElementById('position').textContent = `X:${{Math.round(game.player.x)}} Y:${{Math.round(game.player.y)}}`;
            document.getElementById('hp').textContent = `${{game.player.hp}}/${{game.player.maxHp}}`;
            document.getElementById('mp').textContent = `${{game.player.mp}}/${{game.player.maxMp}}`;
            document.getElementById('score').textContent = game.player.score;
            
            game.frameCount++;
        }}
        
        // 描画
        function render() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 背景オーバーレイ
            ctx.fillStyle = `rgba(15, 52, 96, ${{game.bgOverlayOpacity}})`;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // パーティクル
            game.particles.forEach(p => {{
                ctx.globalAlpha = p.lifetime / 20;
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x - p.size/2, p.y - p.size/2, p.size, p.size);
            }});
            ctx.globalAlpha = 1;
            
            // 弾
            game.projectiles.forEach(proj => proj.draw());
            
            // 敵
            game.enemies.forEach(enemy => {{
                ctx.fillStyle = enemy.color;
                ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
                ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
                ctx.strokeRect(enemy.x, enemy.y, enemy.width, enemy.height);
            }});
            
            // プレイヤー
            ctx.fillStyle = game.player.color;
            ctx.fillRect(game.player.x, game.player.y, game.player.width, game.player.height);
            
            // プレイヤーの向き
            ctx.fillStyle = '#fff';
            switch(game.player.facing) {{
                case 'up': ctx.fillRect(game.player.x + 14, game.player.y, 4, 8); break;
                case 'down': ctx.fillRect(game.player.x + 14, game.player.y + 24, 4, 8); break;
                case 'left': ctx.fillRect(game.player.x, game.player.y + 14, 8, 4); break;
                case 'right': ctx.fillRect(game.player.x + 24, game.player.y + 14, 8, 4); break;
            }}
            
            // プレイヤー輪郭
            ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
            ctx.strokeRect(game.player.x, game.player.y, game.player.width, game.player.height);
        }}
        
        // ゲームループ
        function gameLoop() {{ update(); render(); requestAnimationFrame(gameLoop); }}
        
        // 初期化
        for (let i = 0; i < 3; i++) setTimeout(() => spawnEnemy(), i * 1000);
        gameLoop();
    </script>
</body>
</html>'''
        
        game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
        with open(game_path, 'w', encoding='utf-8') as f:
            f.write(game_html)
        
        return game_path
    
    def run_demo_with_extracted_bg(self):
        """抽出した画像を使ってゲームデモを実行"""
        if not self.extracted_images:
            print("[WARNING] 抽出された画像がありません")
            return
        
        # 最初の抽出画像を使用
        bg_image = self.extracted_images[0]
        print(f"\n[INFO] 背景画像に使用: {bg_image}")
        
        # カスタム背景ゲームを作成
        game_path = self.create_custom_bg_game(bg_image)
        print(f"[SUCCESS] カスタムゲーム作成: {game_path}")
        
        # ゲームを開く
        self.driver.get(f"file:///{game_path}")
        time.sleep(2)
        
        print("\n=== カスタム背景でゲームデモ ===")
        
        # 背景透明度を調整
        self.driver.execute_script("document.getElementById('opacitySlider').value = 50;")
        self.driver.execute_script("document.getElementById('opacitySlider').dispatchEvent(new Event('input'));")
        time.sleep(0.5)
        
        # 操作デモ
        for i in range(10):
            # 移動
            direction = ['ArrowUp', 'ArrowRight', 'ArrowDown', 'ArrowLeft'][i % 4]
            self.driver.execute_script(f"""
                game.keys['{direction}'] = true;
                setTimeout(() => {{
                    game.keys['{direction}'] = false;
                }}, 300);
            """)
            time.sleep(0.5)
            
            # 攻撃
            if i % 3 == 0:
                self.driver.execute_script("""
                    const event = new KeyboardEvent('keydown', {
                        key: ' ', code: 'Space', bubbles: true
                    });
                    document.dispatchEvent(event);
                """)
            
        # 特殊攻撃
        print("\n[DEMO] 特殊攻撃発動！")
        self.driver.execute_script("""
            const event = new KeyboardEvent('keydown', {
                key: 'E', code: 'KeyE', bubbles: true
            });
            document.dispatchEvent(event);
        """)
        
        time.sleep(2)
        
        # 結果確認
        final_status = self.driver.execute_script("""
            return {
                x: Math.round(game.player.x),
                y: Math.round(game.player.y),
                hp: game.player.hp,
                score: game.player.score,
                enemies: game.enemies.length
            };
        """)
        
        print(f"\n=== ゲーム結果 ===")
        print(f"位置: X:{final_status['x']}, Y:{final_status['y']}")
        print(f"HP: {final_status['hp']}/100")
        print(f"スコア: {final_status['score']}")
        print(f"敵の数: {final_status['enemies']}")
        
        # スクリーンショット
        self.driver.save_screenshot(os.path.join(
            r"C:\Users\user\Desktop\work\90_cc\20250908\contract-programming-tutorial\results",
            "custom_bg_game_demo.png"
        ))
        print(f"\n[INFO] スクリーンショット保存完了")
        
        return True
    
    def cleanup(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(3)
            self.driver.quit()
            print("[INFO] デモ終了")

def main():
    print("=== アクションRPG + 画像抽出デモ ===\n")
    print("このツールは:")
    print("1. 現在のページから画像を抽出")
    print("2. 抽出した画像を背景にしたゲームを作成")
    print("3. そのゲームで実際に操作デモを実行\n")
    
    demo = ActionRPGWithImageExtraction()
    
    try:
        demo.setup_driver()
        
        print("[INFO] テスト用の画像サイトにアクセスして画像を抽出します...")
        
        # テスト用の画像サイトにアクセス
        demo.driver.get("https://picsum.photos/")
        time.sleep(3)
        
        print("[INFO] 画像を抽出中...")
        extracted_images = demo.extract_images_from_current_page()
        
        if extracted_images:
            # 抽出した画像を使ってゲームデモ
            demo.run_demo_with_extracted_bg()
        else:
            print("[WARNING] 画像が抽出できませんでした")
        
    except KeyboardInterrupt:
        print("\n[INFO] 中断されました")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()