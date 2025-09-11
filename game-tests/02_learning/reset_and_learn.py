import os
import subprocess

# ファイルを削除
files_to_delete = ['rpg_strategy.json', 'rpg_learning_log.json']
for file in files_to_delete:
    if os.path.exists(file):
        os.remove(file)
        print(f"Deleted: {file}")

# 学習プレイヤーを実行
print("\nStarting fresh learning session...\n")
subprocess.run(["python", "learning_rpg_player.py"])