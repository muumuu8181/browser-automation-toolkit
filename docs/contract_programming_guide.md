# 契約プログラミング実践ガイド - 特にAI開発における活用法

## 契約プログラミングとは

契約プログラミング（Design by Contract）は、プログラムの各部分が満たすべき「契約」を明示的に定義し、実行時に検証する手法です。

### 3つの基本要素

1. **事前条件（Precondition）**: 関数実行前に満たすべき条件
2. **事後条件（Postcondition）**: 関数実行後に保証される条件  
3. **不変条件（Invariant）**: オブジェクトが常に保つべき条件

## いつ契約プログラミングを使うべきか

### ✅ 積極的に使うべき場合

#### 1. **AIが開発に関与している場合（最重要）**
```python
def process_user_data(data):
    # AIは型を間違えやすい
    assert isinstance(data, dict), "dataは辞書型である必要があります"
    assert 'user_id' in data, "user_idキーが必要です"
    
    # 処理...
```

**理由**: AIは文脈を忘れる、既存機能を壊しやすい、型を間違える

#### 2. **公開API・ライブラリ開発**
```python
class PublicAPI:
    def authenticate(self, token):
        assert token is not None, "tokenは必須です"
        assert len(token) == 32, "tokenは32文字である必要があります"
```

**理由**: 他者が予期しない使い方をする可能性

#### 3. **金銭・安全性に関わる処理**
```python
def transfer_money(amount, from_account, to_account):
    assert amount > 0, "送金額は正の数"
    assert from_account.balance >= amount, "残高不足"
    
    old_total = from_account.balance + to_account.balance
    # 送金処理...
    
    # 事後条件：総額は変わらない
    assert from_account.balance + to_account.balance == old_total
```

#### 4. **複雑な状態管理**
```javascript
class WeightTracker {
    changePeriod(newPeriod) {
        const oldDate = this.currentDate;
        // 処理...
        
        // 期間変更で日付が変わってはいけない
        assert(this.currentDate === oldDate);
    }
}
```

### ❌ 使わなくてもよい場合

#### 1. **完全に制御下にある内部処理**
```python
def _internal_helper(self):
    # プライベートメソッドで呼び出し元が限定的
    return self.data * 2
```

#### 2. **パフォーマンスがクリティカルな部分**
```python
def game_main_loop():
    # 60FPSを維持する必要がある
    # 契約チェックのオーバーヘッドを避ける
    pass
```

#### 3. **単純すぎる処理**
```python
def get_name(self):
    return self.name  # 単純なgetterには不要
```

## AI開発における契約プログラミングの特別な重要性

### AIとの開発で契約が特に有効な理由

1. **AIの挙動予測が困難**
   - AIは想定外の変更を加えることがある
   - 契約により、変更の影響を即座に検出

2. **「3歩進んで2歩下がる」問題の防止**
   ```python
   # 既存機能に契約を設置
   def existing_feature(self):
       old_state = self.critical_value
       # 処理...
       
       # AIが壊していないかチェック
       assert self.critical_value == old_state, "critical_valueが変更された！"
   ```

3. **AIへの即座のフィードバック**
   - AIが契約違反するコードを実行した瞬間にエラー
   - AIは自分のミスに気づき、修正できる

### 推奨される契約の粒度（AI開発の場合）

```python
# レベル1: 必須 - すべての公開メソッド
def public_method(self, param):
    assert param is not None
    
# レベル2: 強く推奨 - 状態を変更する処理
def update_state(self, new_value):
    old_count = len(self.items)
    # 処理...
    assert len(self.items) >= old_count  # 意図しない削除を防ぐ

# レベル3: 推奨 - 計算処理
def calculate_average(self, numbers):
    assert len(numbers) > 0, "空のリストで平均計算"
    result = sum(numbers) / len(numbers)
    assert not math.isnan(result), "計算結果がNaN"
```

## 実装のベストプラクティス

### 1. 開発環境と本番環境の切り替え

```python
import os

DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

def contract(condition, message):
    if not condition and DEBUG:
        raise AssertionError(f"契約違反: {message}")
    elif not condition:
        # 本番では警告のみ
        logging.warning(f"契約違反: {message}")
```

### 2. ログ記録との併用

```python
def contract_with_log(condition, message, context=None):
    if not condition:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'violation': message,
            'context': context
        }
        
        # ファイルに記録
        with open('contract_violations.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        if DEBUG:
            raise AssertionError(message)
```

## まとめ

### 個人開発での指針

1. **自分だけが使う + 挙動が予測可能** → 最小限の契約でOK
2. **AIが開発に関与** → 積極的に契約を導入
3. **将来の拡張可能性がある** → 主要な部分に契約を設置

### AI開発での鉄則

- **入力/出力の境界には必ず契約**
- **状態変更を伴う処理には契約**
- **「AIがよくやるミス」に対する防御**
  - 型の間違い
  - null/undefined の扱い
  - 配列の破壊的変更
  - 意図しない副作用

### 契約違反時のAIの学習

AIがコードを実行して契約違反が発生した場合：
1. 即座にエラーメッセージが表示される
2. AIは違反内容を理解し、修正できる
3. 同じミスを繰り返しにくくなる

これにより、AIとの共同開発がより効率的かつ安全になります。