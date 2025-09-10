#!/usr/bin/env python3
"""
契約プログラミング (Contract Programming) - Python版 Hello World

契約プログラミングの3つの基本要素:
1. 事前条件 (Precondition): 関数が呼ばれる前に満たすべき条件
2. 事後条件 (Postcondition): 関数が終了時に保証すべき条件
3. 不変条件 (Invariant): クラスが常に保つべき条件
"""

class GreetingContract:
    """挨拶を管理するクラス（契約付き）"""
    
    def __init__(self):
        self._greeting_count = 0
        self._check_invariant()
    
    def _check_invariant(self):
        """不変条件: greeting_countは常に0以上"""
        assert self._greeting_count >= 0, "不変条件違反: greeting_countは負の値になってはいけない"
    
    def greet(self, name: str) -> str:
        """
        名前を受け取って挨拶を返す
        
        事前条件:
        - nameは空文字列であってはならない
        - nameは文字列型でなければならない
        
        事後条件:
        - 戻り値は"Hello, {name}!"の形式
        - greeting_countが1増加する
        """
        # 事前条件のチェック
        assert isinstance(name, str), f"事前条件違反: nameは文字列でなければならない (受け取った型: {type(name).__name__})"
        assert len(name.strip()) > 0, "事前条件違反: nameは空文字列であってはならない"
        
        # 事後条件チェックのための初期値を保存
        old_count = self._greeting_count
        
        # 本体の処理
        greeting = f"Hello, {name}!"
        self._greeting_count += 1
        
        # 事後条件のチェック
        assert greeting == f"Hello, {name}!", f"事後条件違反: 期待される形式と異なる"
        assert self._greeting_count == old_count + 1, "事後条件違反: greeting_countが1増加していない"
        
        # 不変条件のチェック
        self._check_invariant()
        
        return greeting
    
    def get_greeting_count(self) -> int:
        """これまでの挨拶回数を返す"""
        self._check_invariant()
        return self._greeting_count


def main():
    """メイン関数"""
    print("=== 契約プログラミング Python版 ===")
    print()
    
    greeter = GreetingContract()
    
    # 正常な使用例
    print("1. 正常な使用例:")
    try:
        result = greeter.greet("World")
        print(f"  結果: {result}")
        print(f"  挨拶回数: {greeter.get_greeting_count()}")
    except AssertionError as e:
        print(f"  エラー: {e}")
    
    print()
    
    # 契約違反の例1: 空文字列
    print("2. 契約違反の例 - 空文字列:")
    try:
        result = greeter.greet("")
        print(f"  結果: {result}")
    except AssertionError as e:
        print(f"  エラー: {e}")
    
    print()
    
    # 契約違反の例2: 型違い
    print("3. 契約違反の例 - 型違い:")
    try:
        result = greeter.greet(123)  # 数値を渡す
        print(f"  結果: {result}")
    except AssertionError as e:
        print(f"  エラー: {e}")
    
    print()
    
    # 複数回の呼び出し
    print("4. 複数回の正常な呼び出し:")
    names = ["Alice", "Bob", "Charlie"]
    for name in names:
        try:
            result = greeter.greet(name)
            print(f"  {result} (合計挨拶回数: {greeter.get_greeting_count()})")
        except AssertionError as e:
            print(f"  エラー: {e}")


if __name__ == "__main__":
    main()