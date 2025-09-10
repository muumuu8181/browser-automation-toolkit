# Browser Automation & F12 Log Collection Toolkit

包括的なブラウザ自動化とコンソールログ収集ツールキット

## 🎯 主要機能

### 1. Contract Programming (契約プログラミング)
- **Python**: `contract-programming/hello_contract.py`
- **JavaScript**: `contract-programming/hello_contract.js`
- AIコーディング時のバグ防止とデバッグ支援

### 2. F12 Console Log Collection
- **Selenium**: `f12-tools/selenium_f12_tester.py`
- **Puppeteer**: `f12-tools/puppeteer_f12_test.js`
- **Playwright**: `f12-tools/playwright_f12_test.py`

### 3. Web Scraping Tools
- **Yahoo News**: Selenium/Puppeteer/Playwright対応
- **ログイン自動化**: Paters等の認証システム対応
- **Android対応**: Termux環境での実行可能

### 4. Game Automation
- **Action RPG**: 完全自動プレイシステム
- **座標追跡**: リアルタイム位置確認
- **画像背景**: チャット画像の背景適用
- **F12ログ**: ゲーム操作の完全記録

## 🚀 クイックスタート

### Prerequisites
```bash
npm install  # Puppeteer dependencies
pip install selenium playwright requests
```

### F12ログ収集テスト
```bash
# Seleniumでテトリスゲームのログ収集
python f12-tools/tetris_f12_logger.py

# PuppeteerでRPGゲームのログ収集
node f12-tools/puppeteer_f12_test.js

# PlaywrightでF12ログ収集
python f12-tools/playwright_f12_test.py
```

### Web Scraping
```bash
# Yahoo News (3つのツール比較)
python scrapers/selenium_yahoo_news.py
node scrapers/puppeteer_yahoo_news.js  
python scrapers/playwright_yahoo_news.py
```

### Game Automation
```bash
# Action RPGの完全自動プレイ
python game-tests/action_rpg_selenium_fix.py

# 画像背景付きゲーム
python game-tests/action_rpg_with_image_extraction.py
```

## 📁 ディレクトリ構成

```
browser-automation-toolkit/
├── contract-programming/     # 契約プログラミング例
├── f12-tools/               # F12ログ収集ツール
├── scrapers/                # Webスクレイピング
├── game-tests/              # ゲーム自動化
├── results/                 # 実行結果・スクリーンショット
├── docs/                    # 詳細ドキュメント
└── README.md               # このファイル
```

## 🔧 対応プラットフォーム

- **Windows**: 完全対応 (メイン開発環境)
- **macOS**: Selenium/Playwright対応
- **Linux**: 全ツール対応
- **Android**: Termux + Alpine Linux (Pythonのみ)

## 📊 テスト結果

### Yahoo News Scraping
- **Selenium**: 10記事収集
- **Puppeteer**: 10記事収集 (108リンク発見)
- **Playwright**: 8記事収集 (2タイムアウト)

### F12 Log Collection
- **Tetris**: 7コンソールログ収集
- **Action RPG**: 93ゲームイベントログ
- **完全な操作履歴**: キー入力・座標・状態変化

## 🎮 特徴的な機能

### Action RPG自動化
- **移動確認**: 座標表示でキャラクター移動を可視化
- **攻撃システム**: 通常攻撃・特殊攻撃の自動実行
- **JavaScriptインジェクション**: sendKeys問題の解決
- **画像抽出**: Webページから画像を取得して背景に適用

### Contract Programming
- **前提条件**: 入力値の検証
- **事後条件**: 出力値の保証  
- **不変条件**: オブジェクト状態の整合性
- **AIデバッグ**: "3歩進んで2歩下がる"問題の解決

## 📖 詳細ドキュメント

- `docs/README.md`: 全体概要
- `docs/USAGE_MANUAL.md`: 使用方法
- `docs/contract_programming_guide.md`: 契約プログラミング詳解

## 🔗 Related Project

このツールキットは [worktree-template](https://github.com/muumuu8181/worktree-template) から分離されました。

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

このプロジェクトはMITライセンスです。詳細は`LICENSE`ファイルを参照してください。

---

**🚨 重要**: このツールキットはAI開発者向けのデバッグ・自動化支援ツールです。倫理的な使用をお願いします。