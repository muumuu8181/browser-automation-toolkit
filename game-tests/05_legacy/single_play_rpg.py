#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シングルプレイRPG - 1回だけプレイしてスコアを表示
"""

from score_tracking_rpg_player import ScoreTrackingRPGPlayer

def main():
    print("=== RPG シングルプレイモード ===")
    print("1回だけプレイして終了します\n")
    
    player = ScoreTrackingRPGPlayer()
    
    # 過去のスコアがあれば表示
    if player.score_history:
        player.display_score_board()
        print("\n")
    
    try:
        # 1回だけプレイ
        player.setup_driver()
        score = player.play_game(duration=45)
        
        # ブラウザは開いたままにする
        print("\n\n🎮 ゲーム画面はそのままです")
        print("ブラウザを閉じるには Enter キーを押してください...")
        input()
        
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        player.cleanup()
        print("\n終了しました！")

if __name__ == "__main__":
    main()