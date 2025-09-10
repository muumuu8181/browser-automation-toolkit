#!/usr/bin/env node
/**
 * Patersログイン自動化スクリプト（Puppeteer版）
 */

const puppeteer = require('puppeteer-core');
const readline = require('readline');
require('dotenv').config();

class PatersLoginAutomation {
    constructor() {
        this.browser = null;
        this.page = null;
    }

    async setupBrowser() {
        console.log('[INFO] ブラウザを起動中...');
        
        try {
            const chromePath = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
            
            this.browser = await puppeteer.launch({
                executablePath: chromePath,
                headless: false, // 動作確認のため表示モード
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled'
                ],
                defaultViewport: {
                    width: 1280,
                    height: 720
                }
            });
            
            this.page = await this.browser.newPage();
            
            // 自動化検出を回避
            await this.page.evaluateOnNewDocument(() => {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            });
            
            // User-Agent設定
            await this.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
            
            console.log('[SUCCESS] ブラウザ起動成功！');
            return true;
            
        } catch (error) {
            console.log(`[ERROR] ブラウザ起動エラー: ${error.message}`);
            return false;
        }
    }

    async login(email, password) {
        try {
            console.log('[INFO] Patersログインページにアクセス中...');
            await this.page.goto('https://paters.jp/users/sign_in', {
                waitUntil: 'networkidle2',
                timeout: 30000
            });
            
            console.log('[INFO] ページ読み込み完了');
            
            // メールアドレス入力
            console.log('[INFO] メールアドレスを入力...');
            const emailSelectors = [
                'input[type="email"]',
                'input[name="user[email]"]',
                'input[id*="email"]',
                '#user_email',
                '.email-input',
                'input[placeholder*="メール"]'
            ];
            
            let emailField = null;
            for (const selector of emailSelectors) {
                try {
                    emailField = await this.page.$(selector);
                    if (emailField) break;
                } catch (e) {}
            }
            
            if (emailField) {
                await emailField.click({ clickCount: 3 }); // 全選択
                await emailField.type(email);
                console.log('[SUCCESS] メールアドレス入力完了');
            } else {
                console.log('[ERROR] メールアドレスフィールドが見つかりません');
                return false;
            }
            
            // パスワード入力
            console.log('[INFO] パスワードを入力...');
            const passwordSelectors = [
                'input[type="password"]',
                'input[name="user[password]"]',
                'input[id*="password"]',
                '#user_password',
                '.password-input'
            ];
            
            let passwordField = null;
            for (const selector of passwordSelectors) {
                try {
                    passwordField = await this.page.$(selector);
                    if (passwordField) break;
                } catch (e) {}
            }
            
            if (passwordField) {
                await passwordField.click({ clickCount: 3 });
                await passwordField.type(password);
                console.log('[SUCCESS] パスワード入力完了');
            } else {
                console.log('[ERROR] パスワードフィールドが見つかりません');
                return false;
            }
            
            // ログインボタンをクリック
            console.log('[INFO] ログインボタンを探しています...');
            const loginButtonSelectors = [
                'input[type="submit"][value*="ログイン"]',
                'button[type="submit"]',
                'input[name="commit"]',
                '.login-button',
                'button'
            ];
            
            let loginButton = null;
            for (const selector of loginButtonSelectors) {
                try {
                    const buttons = await this.page.$$(selector);
                    for (const button of buttons) {
                        const text = await this.page.evaluate(el => el.textContent || el.value || '', button);
                        if (text.includes('ログイン')) {
                            loginButton = button;
                            break;
                        }
                    }
                    if (loginButton) break;
                } catch (e) {}
            }
            
            if (loginButton) {
                console.log('[INFO] ログインボタンをクリック...');
                await Promise.all([
                    this.page.waitForNavigation({ waitUntil: 'networkidle2' }),
                    loginButton.click()
                ]);
                
                // ログイン結果の確認
                const currentUrl = this.page.url();
                
                if (!currentUrl.includes('sign_in')) {
                    console.log(`[SUCCESS] ログイン成功！現在のURL: ${currentUrl}`);
                    
                    // ログイン後の情報を取得
                    const pageTitle = await this.page.title();
                    console.log(`[INFO] ページタイトル: ${pageTitle}`);
                    
                    return true;
                } else {
                    console.log('[WARN] ログインに失敗した可能性があります');
                    
                    // エラーメッセージを探す
                    const errorSelectors = ['.alert', '.error', '.flash', '[class*="error"]'];
                    for (const selector of errorSelectors) {
                        try {
                            const errorElement = await this.page.$(selector);
                            if (errorElement) {
                                const errorText = await this.page.evaluate(el => el.textContent, errorElement);
                                console.log(`[ERROR] エラーメッセージ: ${errorText.trim()}`);
                            }
                        } catch (e) {}
                    }
                    
                    return false;
                }
            } else {
                console.log('[ERROR] ログインボタンが見つかりません');
                
                // デバッグ用：ページ内のフォーム要素を表示
                const forms = await this.page.$$eval('form', forms => 
                    forms.map(form => ({
                        action: form.action,
                        method: form.method,
                        inputs: Array.from(form.querySelectorAll('input')).map(input => ({
                            type: input.type,
                            name: input.name,
                            value: input.value
                        }))
                    }))
                );
                console.log('[DEBUG] フォーム情報:', JSON.stringify(forms, null, 2));
                
                return false;
            }
            
        } catch (error) {
            console.log(`[ERROR] ログイン処理中にエラーが発生: ${error.message}`);
            
            // スクリーンショットを保存（デバッグ用）
            try {
                await this.page.screenshot({ path: 'login_error.png' });
                console.log('[INFO] エラー時のスクリーンショットを保存: login_error.png');
            } catch (e) {}
            
            return false;
        }
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
            console.log('[INFO] ブラウザを閉じました');
        }
    }
}

// 入力を取得する関数
function askQuestion(question) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            rl.close();
            resolve(answer);
        });
    });
}

// メイン実行
async function main() {
    console.log('=== Patersログイン自動化 (Puppeteer版) ===\n');

    // 環境変数から認証情報を取得
    let email = process.env.PATERS_EMAIL;
    let password = process.env.PATERS_PASSWORD;

    if (!email || !password) {
        console.log('[WARN] 環境変数が設定されていません。手動入力モードに切り替えます。');
        email = await askQuestion('メールアドレス: ');
        password = await askQuestion('パスワード: ');
    }

    const automation = new PatersLoginAutomation();

    try {
        const browserReady = await automation.setupBrowser();
        if (!browserReady) {
            return;
        }

        const success = await automation.login(email, password);

        if (success) {
            console.log('\n[INFO] ログイン後の処理を実行できます');
            await askQuestion('Enterキーを押すとブラウザを閉じます...');
        }

    } catch (error) {
        console.log(`\n[ERROR] 実行エラー: ${error.message}`);
    } finally {
        await automation.cleanup();
    }
}

// エラーハンドリング
process.on('unhandledRejection', (reason, promise) => {
    console.log('[ERROR] Unhandled Rejection:', reason);
});

if (require.main === module) {
    main();
}