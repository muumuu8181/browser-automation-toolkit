import os
import shutil

# 整理用のフォルダを作成
folders = {
    "01_最新版": ["working_rpg_player.py", "keep_browser_open.py", "score_tracking_rpg_player.py"],
    "02_学習型": ["learning_rpg_player.py", "improved_learning_rpg.py", "reset_and_learn.py"],
    "03_テスト版": ["debug_rpg_player.py", "check_game_start.py", "simple_rpg_player.py"],
    "04_実験版": ["survival_rpg_player.py", "smart_survival_rpg.py", "blitz_rpg_player.py"],
    "05_旧版": ["action_rpg_*.py", "play_custom_bg_rpg*.py", "single_play_rpg.py", "rpg_battle_demo.py"],
    "06_データ": ["*.json", "*.png"]
}

print("=== ファイル整理を開始します ===\n")

# 現在のディレクトリ
current_dir = os.path.dirname(os.path.abspath(__file__))

for folder, patterns in folders.items():
    # フォルダ作成
    folder_path = os.path.join(current_dir, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"フォルダ作成: {folder}")
    
    # ファイル移動
    moved = 0
    for pattern in patterns:
        if "*" in pattern:
            # ワイルドカードパターン
            import glob
            files = glob.glob(os.path.join(current_dir, pattern))
            for file in files:
                if os.path.isfile(file):
                    filename = os.path.basename(file)
                    dest = os.path.join(folder_path, filename)
                    if not os.path.exists(dest):
                        shutil.copy2(file, dest)
                        moved += 1
        else:
            # 特定のファイル
            src = os.path.join(current_dir, pattern)
            if os.path.exists(src) and os.path.isfile(src):
                dest = os.path.join(folder_path, pattern)
                if not os.path.exists(dest):
                    shutil.copy2(src, dest)
                    moved += 1
    
    if moved > 0:
        print(f"  {folder} に {moved} ファイルをコピー")

print("\n=== README作成 ===")

readme_content = """# RPGゲーム自動プレイツール

## フォルダ構成

### 01_最新版
- **working_rpg_player.py** - 動作確認済みの安定版
- **keep_browser_open.py** - ブラウザを開いたままにする版
- **score_tracking_rpg_player.py** - スコア記録機能付き

### 02_学習型
- **learning_rpg_player.py** - 学習して上達するAI
- **improved_learning_rpg.py** - 改良版学習AI

### 03_テスト版
- **debug_rpg_player.py** - デバッグ用
- **check_game_start.py** - ゲーム開始時の状態確認

### 04_実験版
- **survival_rpg_player.py** - サバイバル戦略
- **smart_survival_rpg.py** - 円運動回避戦略
- **blitz_rpg_player.py** - 開幕特殊攻撃戦略

## 使い方

1. 基本的な実行方法：
   ```
   python ファイル名.py
   ```

2. おすすめ：
   - 手動プレイしたい → keep_browser_open.py
   - 自動プレイを見たい → working_rpg_player.py
   - スコアを記録したい → score_tracking_rpg_player.py
"""

with open(os.path.join(current_dir, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

print("README.md を作成しました")
print("\n整理完了！")
print("\n注意: 元のファイルはそのまま残っています。")
print("不要なファイルは手動で削除してください。")