from selenium import webdriver
import os

# ブラウザ設定（プログラム終了後も開いたまま）
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)

# ブラウザを開く
driver = webdriver.Chrome(options=options)

# 迷路ゲームを開く
game_path = os.path.join(os.path.dirname(__file__), "simple-maze-game.html")
driver.get(f"file:///{game_path}")

print("迷路ゲームを開きました！")
print("\n【操作方法】")
print("矢印キー or WASD: 移動")
print("黄色い丸 → 緑の四角を目指そう！")