import os
import shutil

print("=== フォルダ整理と英語化 ===\n")

# 現在のディレクトリ
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. まず日本語フォルダを英語にリネーム
rename_map = {
    "01_最新版": "01_latest",
    "02_学習型": "02_learning",
    "03_テスト版": "03_testing",
    "04_実験版": "04_experimental",
    "05_旧版": "05_legacy",
    "06_データ": "06_data"
}

for old_name, new_name in rename_map.items():
    old_path = os.path.join(current_dir, old_name)
    new_path = os.path.join(current_dir, new_name)
    
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)
        print(f"フォルダ名変更: {old_name} → {new_name}")

# 2. 重複ファイルを削除（フォルダに入っているものと同じファイルを削除）
folders = ["01_latest", "02_learning", "03_testing", "04_experimental", "05_legacy", "06_data"]
files_in_folders = set()

# フォルダ内のファイル一覧を取得
for folder in folders:
    folder_path = os.path.join(current_dir, folder)
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, file)):
                files_in_folders.add(file)

print(f"\nフォルダ内のファイル数: {len(files_in_folders)}")

# ルートディレクトリのファイルを確認して削除
deleted_count = 0
for file in os.listdir(current_dir):
    file_path = os.path.join(current_dir, file)
    
    # ファイルかつフォルダ内に同じ名前のファイルがある場合
    if os.path.isfile(file_path) and file in files_in_folders:
        try:
            os.remove(file_path)
            deleted_count += 1
            print(f"削除: {file}")
        except Exception as e:
            print(f"削除失敗: {file} - {e}")

# 3. 必要なファイルだけ残す
keep_files = ["cleanup_and_rename.py", "README.md", "just_open_game.py", "stop_all.bat"]

# 4. 新しいREADMEを作成
readme_content = """# RPG Game Automation Tools

## Folder Structure

### 01_latest/
- **working_rpg_player.py** - Stable version that works
- **keep_browser_open.py** - Keeps browser open after script ends
- **score_tracking_rpg_player.py** - Tracks and visualizes scores

### 02_learning/
- **learning_rpg_player.py** - AI that learns and improves
- **improved_learning_rpg.py** - Enhanced learning AI

### 03_testing/
- **debug_rpg_player.py** - For debugging game mechanics
- **check_game_start.py** - Checks initial game state

### 04_experimental/
- Various experimental strategies

### 05_legacy/
- Old versions and original files

### 06_data/
- JSON files (game logs, strategies)
- PNG files (screenshots, graphs)

## Quick Start

1. Open game without automation:
   ```
   python just_open_game.py
   ```

2. Play with automation:
   ```
   python 01_latest/working_rpg_player.py
   ```

3. Stop all processes:
   ```
   stop_all.bat
   ```
"""

with open(os.path.join(current_dir, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

print(f"\n削除したファイル数: {deleted_count}")
print("\n整理完了！")
print("\n残っているファイル:")
for file in os.listdir(current_dir):
    if os.path.isfile(os.path.join(current_dir, file)):
        print(f"  - {file}")