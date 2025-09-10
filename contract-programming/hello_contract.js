#!/usr/bin/env node
/**
 * 契約プログラミング (Contract Programming) - JavaScript版 Hello World
 * 
 * 契約プログラミングの3つの基本要素:
 * 1. 事前条件 (Precondition): 関数が呼ばれる前に満たすべき条件
 * 2. 事後条件 (Postcondition): 関数が終了時に保証すべき条件
 * 3. 不変条件 (Invariant): クラスが常に保つべき条件
 */

class ContractError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ContractError';
    }
}

class GreetingContract {
    constructor() {
        this._greetingCount = 0;
        this._checkInvariant();
    }

    /**
     * 不変条件: greetingCountは常に0以上
     */
    _checkInvariant() {
        if (this._greetingCount < 0) {
            throw new ContractError(
                `不変条件違反: greetingCountは負の値になってはいけない (現在値: ${this._greetingCount})`
            );
        }
    }

    /**
     * 名前を受け取って挨拶を返す
     * 
     * @param {string} name - 挨拶する相手の名前
     * @returns {string} 挨拶メッセージ
     * 
     * 事前条件:
     * - nameは空文字列であってはならない
     * - nameは文字列型でなければならない
     * 
     * 事後条件:
     * - 戻り値は"Hello, {name}!"の形式
     * - greetingCountが1増加する
     */
    greet(name) {
        // 事前条件のチェック
        if (typeof name !== 'string') {
            throw new ContractError(
                `事前条件違反: nameは文字列でなければならない (受け取った型: ${typeof name})`
            );
        }
        if (name.trim().length === 0) {
            throw new ContractError(
                '事前条件違反: nameは空文字列であってはならない'
            );
        }

        // 事後条件チェックのための初期値を保存
        const oldCount = this._greetingCount;

        // 本体の処理
        const greeting = `Hello, ${name}!`;
        this._greetingCount += 1;

        // 事後条件のチェック
        if (greeting !== `Hello, ${name}!`) {
            throw new ContractError(
                `事後条件違反: 期待される形式と異なる (実際: ${greeting})`
            );
        }
        if (this._greetingCount !== oldCount + 1) {
            throw new ContractError(
                `事後条件違反: greetingCountが1増加していない (期待値: ${oldCount + 1}, 実際: ${this._greetingCount})`
            );
        }

        // 不変条件のチェック
        this._checkInvariant();

        return greeting;
    }

    /**
     * これまでの挨拶回数を返す
     * @returns {number} 挨拶回数
     */
    getGreetingCount() {
        this._checkInvariant();
        return this._greetingCount;
    }
}

function main() {
    console.log('=== 契約プログラミング JavaScript版 ===');
    console.log();

    const greeter = new GreetingContract();

    // 正常な使用例
    console.log('1. 正常な使用例:');
    try {
        const result = greeter.greet('World');
        console.log(`  結果: ${result}`);
        console.log(`  挨拶回数: ${greeter.getGreetingCount()}`);
    } catch (error) {
        console.log(`  エラー: ${error.message}`);
    }

    console.log();

    // 契約違反の例1: 空文字列
    console.log('2. 契約違反の例 - 空文字列:');
    try {
        const result = greeter.greet('');
        console.log(`  結果: ${result}`);
    } catch (error) {
        console.log(`  エラー: ${error.message}`);
    }

    console.log();

    // 契約違反の例2: 型違い
    console.log('3. 契約違反の例 - 型違い:');
    try {
        const result = greeter.greet(123); // 数値を渡す
        console.log(`  結果: ${result}`);
    } catch (error) {
        console.log(`  エラー: ${error.message}`);
    }

    console.log();

    // 契約違反の例3: null
    console.log('4. 契約違反の例 - null:');
    try {
        const result = greeter.greet(null);
        console.log(`  結果: ${result}`);
    } catch (error) {
        console.log(`  エラー: ${error.message}`);
    }

    console.log();

    // 複数回の呼び出し
    console.log('5. 複数回の正常な呼び出し:');
    const names = ['Alice', 'Bob', 'Charlie'];
    for (const name of names) {
        try {
            const result = greeter.greet(name);
            console.log(`  ${result} (合計挨拶回数: ${greeter.getGreetingCount()})`);
        } catch (error) {
            console.log(`  エラー: ${error.message}`);
        }
    }
}

// メイン関数を実行
if (require.main === module) {
    main();
}