/**
 * 体重記録アプリでの契約プログラミング実装例
 */

class WeightTracker {
    constructor() {
        this.currentDate = new Date();
        this.period = 'week'; // 'day', 'week', 'month'
        this.weights = [];
        this._checkInvariant();
    }

    /**
     * 不変条件：アプリの状態が常に正しいことを保証
     */
    _checkInvariant() {
        // 期間は必ず3つのうちどれか
        const validPeriods = ['day', 'week', 'month'];
        if (!validPeriods.includes(this.period)) {
            throw new Error(`不変条件違反: 無効な期間 '${this.period}'`);
        }
        
        // 現在日付は必ず存在する
        if (!(this.currentDate instanceof Date)) {
            throw new Error('不変条件違反: currentDateが不正');
        }
    }

    /**
     * 期間を変更する
     * 事前条件: 新しい期間は'day', 'week', 'month'のいずれか
     * 事後条件: 期間が正しく変更され、日付は変わらない
     */
    changePeriod(newPeriod) {
        // 事前条件
        const validPeriods = ['day', 'week', 'month'];
        if (!validPeriods.includes(newPeriod)) {
            throw new Error(`事前条件違反: 無効な期間 '${newPeriod}'`);
        }
        
        // 変更前の日付を保存（事後条件チェック用）
        const oldDate = new Date(this.currentDate);
        const oldPeriod = this.period;
        
        // 本処理
        this.period = newPeriod;
        
        // 事後条件
        if (this.currentDate.getTime() !== oldDate.getTime()) {
            throw new Error('事後条件違反: 期間変更で日付が変わってしまった');
        }
        
        if (this.period === oldPeriod) {
            throw new Error('事後条件違反: 期間が変更されていない');
        }
        
        this._checkInvariant();
    }

    /**
     * 前の期間に移動
     * 事前条件: なし
     * 事後条件: 日付が正しい分だけ前に移動している
     */
    moveToPreviousPeriod() {
        const oldDate = new Date(this.currentDate);
        let expectedDate = new Date(oldDate);
        
        // 期間に応じて期待される移動を計算
        switch (this.period) {
            case 'day':
                expectedDate.setDate(expectedDate.getDate() - 1);
                break;
            case 'week':
                expectedDate.setDate(expectedDate.getDate() - 7);
                break;
            case 'month':
                expectedDate.setMonth(expectedDate.getMonth() - 1);
                break;
        }
        
        // 本処理
        switch (this.period) {
            case 'day':
                this.currentDate.setDate(this.currentDate.getDate() - 1);
                break;
            case 'week':
                this.currentDate.setDate(this.currentDate.getDate() - 7);
                break;
            case 'month':
                this.currentDate.setMonth(this.currentDate.getMonth() - 1);
                break;
        }
        
        // 事後条件: 日付が期待通りに変更されている
        if (this.currentDate.getTime() !== expectedDate.getTime()) {
            throw new Error(
                `事後条件違反: 日付が正しく更新されていない\n` +
                `期待: ${expectedDate.toISOString()}\n` +
                `実際: ${this.currentDate.toISOString()}`
            );
        }
        
        this._checkInvariant();
    }

    /**
     * 表示用のデータを取得
     * 事前条件: なし
     * 事後条件: 必ず有効なデータが返される
     */
    getDisplayData() {
        const startDate = this._getStartDate();
        const endDate = this._getEndDate();
        
        // 事後条件: 開始日は終了日より前
        if (startDate >= endDate) {
            throw new Error(
                `事後条件違反: 開始日が終了日より後になっている\n` +
                `開始: ${startDate.toISOString()}\n` +
                `終了: ${endDate.toISOString()}`
            );
        }
        
        // 事後条件: データは必ず配列
        const data = this._filterWeightData(startDate, endDate);
        if (!Array.isArray(data)) {
            throw new Error('事後条件違反: 返されたデータが配列ではない');
        }
        
        return {
            startDate,
            endDate,
            data,
            period: this.period
        };
    }

    _getStartDate() {
        const start = new Date(this.currentDate);
        switch (this.period) {
            case 'day':
                // その日の開始
                start.setHours(0, 0, 0, 0);
                break;
            case 'week':
                // 週の開始（日曜日）
                start.setDate(start.getDate() - start.getDay());
                start.setHours(0, 0, 0, 0);
                break;
            case 'month':
                // 月の開始
                start.setDate(1);
                start.setHours(0, 0, 0, 0);
                break;
        }
        return start;
    }

    _getEndDate() {
        const end = new Date(this.currentDate);
        switch (this.period) {
            case 'day':
                // その日の終了
                end.setHours(23, 59, 59, 999);
                break;
            case 'week':
                // 週の終了（土曜日）
                end.setDate(end.getDate() - end.getDay() + 6);
                end.setHours(23, 59, 59, 999);
                break;
            case 'month':
                // 月の終了
                end.setMonth(end.getMonth() + 1);
                end.setDate(0); // 前月の最終日
                end.setHours(23, 59, 59, 999);
                break;
        }
        return end;
    }

    _filterWeightData(start, end) {
        // ダミー実装
        return this.weights.filter(w => w.date >= start && w.date <= end);
    }
}

// 使用例とテスト
function testWeightTracker() {
    console.log('=== 体重記録アプリの契約プログラミングテスト ===\n');
    
    const tracker = new WeightTracker();
    
    // 1. 正常な期間変更
    console.log('1. 正常な期間変更:');
    try {
        console.log(`  現在の期間: ${tracker.period}`);
        tracker.changePeriod('day');
        console.log(`  変更後の期間: ${tracker.period} ✓`);
    } catch (error) {
        console.log(`  エラー: ${error.message}`);
    }
    
    console.log();
    
    // 2. 無効な期間への変更（バグの原因）
    console.log('2. 無効な期間への変更（よくあるバグ）:');
    try {
        tracker.changePeriod('year'); // 'year'は無効
        console.log('  成功（これはバグ！）');
    } catch (error) {
        console.log(`  エラー検出: ${error.message} ✓`);
    }
    
    console.log();
    
    // 3. 前の期間への移動
    console.log('3. 前の期間への移動:');
    try {
        tracker.period = 'week';
        const before = new Date(tracker.currentDate);
        tracker.moveToPreviousPeriod();
        const after = new Date(tracker.currentDate);
        const diff = (before - after) / (1000 * 60 * 60 * 24);
        console.log(`  ${before.toLocaleDateString()} → ${after.toLocaleDateString()}`);
        console.log(`  ${diff}日前に移動 ✓`);
    } catch (error) {
        console.log(`  エラー: ${error.message}`);
    }
    
    console.log();
    
    // 4. データ取得の整合性チェック
    console.log('4. データ取得の整合性:');
    try {
        const displayData = tracker.getDisplayData();
        console.log(`  期間: ${displayData.period}`);
        console.log(`  開始: ${displayData.startDate.toLocaleDateString()}`);
        console.log(`  終了: ${displayData.endDate.toLocaleDateString()} ✓`);
    } catch (error) {
        console.log(`  エラー: ${error.message}`);
    }
}

// テスト実行
if (require.main === module) {
    testWeightTracker();
}