# Patersログイン自動化 - Android対応版

## MacroDroid設定手順

### 1. マクロ作成
```
トリガー: 
- 時刻トリガー（毎日指定時刻）
- または手動実行

アクション:
1. Webサイトを開く
   - URL: https://paters.jp/users/sign_in
   
2. 待機（3秒）

3. UI操作
   - クリック（テキスト）: "メールアドレス"フィールド
   - テキスト入力: [email変数]

4. UI操作  
   - クリック（テキスト）: "パスワード"フィールド
   - テキスト入力: [password変数]

5. UI操作
   - クリック（テキスト）: "ログイン"

6. 待機（5秒）

7. HTTP Request（POST）
   - URL: https://your-ai-api.com/webhook
   - ボディ: {"status": "logged_in", "timestamp": [system_time]}
```

### 2. 変数設定
```
ローカル変数:
- email: あなたのメールアドレス
- password: あなたのパスワード
- webhook_url: AI連携用URL
```

### 3. AI連携設定
```
Webhookアクション:
- トリガー: ログイン成功後
- データ送信: JSON形式
- レスポンス処理: 変数に保存
```

## Tasker設定手順

### 1. プロファイル作成
```xml
<TaskerData sr="" dvi="1" tv="5.13.7">
  <Profile sr="prof1" ve="2">
    <cdate>1234567890</cdate>
    <name>Paters Auto Login</name>
    <Event sr="con0" ve="2">
      <code>3000</code>
      <pri>0</pri>
      <App sr="arg0">
        <appClass>com.android.chrome</appClass>
        <appPkg>com.android.chrome</appPkg>
        <label>Chrome</label>
      </App>
    </Event>
  </Profile>
  
  <Task sr="task1">
    <cdate>1234567890</cdate>
    <name>Paters Login Task</name>
    <Action sr="act0" ve="7">
      <code>104</code>
      <Str sr="arg0" ve="3">https://paters.jp/users/sign_in</Str>
    </Action>
    
    <Action sr="act1" ve="7">
      <code>30</code>
      <Int sr="arg0" val="3"/>
    </Action>
    
    <Action sr="act2" ve="7">
      <code>877</code>
      <Str sr="arg0" ve="3">document.querySelector('input[type="email"]').value = '%EMAIL%';</Str>
    </Action>
    
    <Action sr="act3" ve="7">
      <code>877</code>
      <Str sr="arg0" ve="3">document.querySelector('input[type="password"]').value = '%PASSWORD%';</Str>
    </Action>
    
    <Action sr="act4" ve="7">
      <code>877</code>
      <Str sr="arg0" ve="3">document.querySelector('input[type="submit"]').click();</Str>
    </Action>
  </Task>
</TaskerData>
```

### 2. JavaScript実行
```javascript
// Tasker JavaScriptletアクション
var email = global('PATERS_EMAIL');
var password = global('PATERS_PASSWORD');

// Chrome Custom Tabs経由で実行
performTask('Open URL', 1, 'https://paters.jp/users/sign_in');
wait(3000);

// AutoInputプラグイン使用
autoInput('input[type="email"]', email);
autoInput('input[type="password"]', password);
autoInput('click', 'input[type="submit"]');

// 結果をAIに送信
var result = {
  status: 'logged_in',
  timestamp: new Date().toISOString()
};

performTask('HTTP Post', 1, 
  'https://your-ai-api.com/webhook',
  JSON.stringify(result)
);
```

## Automate設定

### フローチャート方式
```yaml
1. Flow Beginning
   ↓
2. App start (Chrome)
   - Package: com.android.chrome
   - Activity: Main
   - Data URI: https://paters.jp/users/sign_in
   ↓
3. Delay (3 seconds)
   ↓
4. Interact (UI element)
   - XPath: //input[@type='email']
   - Action: Set text
   - Text: {email}
   ↓
5. Interact (UI element)  
   - XPath: //input[@type='password']
   - Action: Set text
   - Text: {password}
   ↓
6. Interact (UI element)
   - XPath: //input[@type='submit']
   - Action: Click
   ↓
7. HTTP Request
   - Method: POST
   - URL: https://your-ai-api.com/webhook
   - Content: {"status": "success"}
   ↓
8. Flow End
```

## セキュリティ注意事項

1. **パスワード保護**
   - デバイスの暗号化を有効化
   - アプリ個別のパスワード設定
   - 変数は暗号化して保存

2. **アクセス制限**
   - マクロ実行に指紋認証を要求
   - 特定のWiFi接続時のみ実行

3. **ログ管理**
   - パスワードをログに記録しない
   - 実行履歴を定期的に削除

## トラブルシューティング

### よくある問題
1. **要素が見つからない**
   - 待機時間を増やす
   - XPathセレクタを調整
   - アクセシビリティIDを使用

2. **ログイン失敗**
   - reCAPTCHAの確認
   - 2段階認証の設定確認
   - IPアドレス制限の確認

3. **Android 12以降の制限**
   - アクセシビリティ権限を付与
   - オーバーレイ権限を有効化
   - バッテリー最適化を無効化