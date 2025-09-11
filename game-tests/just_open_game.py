#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ゲームを開くだけ（自動プレイなし）
"""

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# ブラウザ設定
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# 重要：プログラム終了後もブラウザを残す
options.add_experimental_option("detach", True)

# ブラウザを開く
driver = webdriver.Chrome(options=options)

# ゲームを開く
game_path = r"C:\Users\user\Desktop\work\90_cc\20250910\minimal-rpg-game\custom_bg_game.html"
driver.get(f"file:///{game_path}")

print("ゲームを開きました！")
print("\n【操作方法】")
print("矢印キー or WASD: 移動")
print("スペース: 攻撃")
print("E: 特殊攻撃（全方向に弾を発射）")
print("\nブラウザはそのまま残ります。")
print("手動でプレイしてください。")