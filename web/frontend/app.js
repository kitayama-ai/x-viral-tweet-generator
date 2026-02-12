// API Endpoint (開発環境では localhost、本番環境では実際のURL)
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://x-viral-tweet-api-172353178391.us-central1.run.app';

// DOM要素
const generateBtn = document.getElementById('generate-btn');
const statusSection = document.getElementById('status-section');
const statusText = document.getElementById('status-text');
const resultsSection = document.getElementById('results-section');
const resultsContainer = document.getElementById('results-container');

// フォーム要素
const accountsTextarea = document.getElementById('accounts');
const tweetsToAnalyzeInput = document.getElementById('tweets-to-analyze');
const tweetsToRewriteInput = document.getElementById('tweets-to-rewrite');
const minLikesInput = document.getElementById('min-likes');
const minRetweetsInput = document.getElementById('min-retweets');

// 生成ボタンのイベントリスナー
generateBtn.addEventListener('click', handleGenerate);

async function handleGenerate() {
    // 入力値を取得
    const accounts = accountsTextarea.value
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
    
    if (accounts.length === 0) {
        showToast('アカウントを1つ以上入力してください', 'error');
        return;
    }
    
    const settings = {
        tweets_to_analyze: parseInt(tweetsToAnalyzeInput.value),
        tweets_to_rewrite: parseInt(tweetsToRewriteInput.value),
        min_likes: parseInt(minLikesInput.value),
        min_retweets: parseInt(minRetweetsInput.value)
    };
    
    // UIを更新
    generateBtn.disabled = true;
    resultsSection.style.display = 'none';
    statusSection.style.display = 'block';
    statusText.textContent = '処理中... ツイートを収集しています';
    
    try {
        // バックエンドAPIを呼び出し
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                accounts: accounts,
                settings: settings
            })
        });
        
        if (!response.ok) {
            let detail = `HTTP ${response.status}`;
            try {
                const errData = await response.json();
                if (errData.detail) detail = errData.detail;
            } catch (e) {}
            throw new Error(detail);
        }
        
        const data = await response.json();
        
        // 結果を表示
        displayResults(data.results);
        
        showToast('生成が完了しました！', 'success');
        
    } catch (error) {
        console.error('Error:', error);

        // エラー詳細を取得
        let errorDetail = error.message || 'Unknown error';
        if (error.message && error.message.includes('API Error')) {
            try {
                // レスポンスボディからエラー詳細を取得
                errorDetail = error.message;
            } catch (e) {}
        }

        showToast(`エラー: ${errorDetail}`, 'error');
        statusText.textContent = `エラーが発生しました: ${errorDetail}`;
        statusSection.style.display = 'block';
    } finally {
        generateBtn.disabled = false;
        statusSection.style.display = 'none';
    }
}

function displayResults(results) {
    resultsContainer.innerHTML = '';
    
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">結果がありません</p>';
        resultsSection.style.display = 'block';
        return;
    }
    
    results.forEach((result, index) => {
        const card = createResultCard(result, index);
        resultsContainer.appendChild(card);
    });
    
    resultsSection.style.display = 'block';
}

function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    card.innerHTML = `
        <div class="result-header">
            <span class="result-category">${result.category || 'AI×副業'}</span>
            <div class="result-metrics">
                <span class="metric">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                    </svg>
                    ${formatNumber(result.original_likes)}
                </span>
                <span class="metric">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M7 7h10v2l2 2-2 2v2H7v-2L5 11l2-2V7z"/>
                    </svg>
                    ${formatNumber(result.original_retweets)}
                </span>
                <span class="metric">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                    </svg>
                    ${formatNumber(result.original_replies)}
                </span>
            </div>
        </div>
        
        <div class="result-original">
            <div class="result-label">元ツイート</div>
            <div class="result-text">${escapeHtml(result.original_text)}</div>
        </div>
        
        <div class="result-rewritten">
            <div class="result-label">リライト（X公式アルゴリズム最適化）</div>
            <div class="result-text">${escapeHtml(result.rewritten_text)}</div>
        </div>
        
        ${result.thread && result.thread.length > 0 ? `
        <div class="result-thread">
            <div class="result-label">スレッド</div>
            ${result.thread.map(tweet => `<div class="result-text" style="margin-bottom: 8px; padding-left: 12px; border-left: 2px solid var(--accent-blue);">${escapeHtml(tweet)}</div>`).join('')}
        </div>
        ` : ''}
        
        <div class="result-scores">
            <div class="score-item">
                <div class="score-label">P(dwell)</div>
                <div class="score-value">${result.scores.dwell_potential}/10</div>
            </div>
            <div class="score-item">
                <div class="score-label">P(reply)</div>
                <div class="score-value">${result.scores.reply_potential}/10</div>
            </div>
            <div class="score-item">
                <div class="score-label">Virality</div>
                <div class="score-value">${result.scores.virality}/10</div>
            </div>
        </div>
        
        ${result.call_to_action ? `
        <div class="result-cta">
            <div class="result-label">リプライ誘発</div>
            <div class="result-text">${escapeHtml(result.call_to_action)}</div>
        </div>
        ` : ''}
        
        ${result.image_url ? `
        <div class="result-image">
            <div class="result-label">図解画像</div>
            <img src="${result.image_url}" alt="Generated infographic" loading="lazy">
        </div>
        ` : ''}
    `;
    
    return card;
}

function displayMockResults() {
    const mockResults = [
        {
            category: 'AI×副業',
            original_text: '2026年、最も稼げるAI副業スキル TOP5\n\n1位: プロンプトエンジニアリング\n2位: AIツール導入コンサル\n3位: AI生成コンテンツの編集\n4位: データラベリング（高品質）\n5位: AI倫理監査\n\n意外と「AIを使う」より「AIを正しく使わせる」スキルが高単価。',
            original_likes: 2100,
            original_retweets: 580,
            original_replies: 142,
            rewritten_text: '2026年、AIで副業する人の9割が知らない「3つの致命的ミス」\n\n1. ツールに丸投げ → 品質が低下\n2. 差別化ゼロ → 価格競争に巻き込まれる\n3. 学習を怠る → すぐに時代遅れに\n\n成功者は「AI×自分の専門性」を武器にしてる。\n\nあなたの専門性、言語化できてる？',
            thread: [
                '特に重要なのが「2. 差別化」。\n\nAIツールは誰でも使える時代だから、「何を」作るかより「誰のために」作るかが勝負。\n\nニッチな専門知識 × AI = 高単価案件',
                '実例：医療ライター×ChatGPT\n→ 一般ライターの3倍の単価\n\n理由：専門用語の正確性と、患者目線の表現をAIだけでは出せない。\n\n「あなただけの掛け算」を見つけよう。'
            ],
            call_to_action: 'あなたの専門性は何ですか？AIとどう掛け算しますか？',
            scores: {
                dwell_potential: 9,
                reply_potential: 8,
                virality: 9
            },
            image_url: 'https://via.placeholder.com/600x338/1d9bf0/ffffff?text=AI+x+副業スキル'
        },
        {
            category: 'AI技術',
            original_text: 'ChatGPTで副業始めて3ヶ月の収益報告\n\n月5万→月18万に成長\n\n✓ ブログ記事執筆代行\n✓ SNS投稿テンプレート販売\n✓ プロンプト設計サポート\n\nコツは「自分の経験×AI」を掛け算すること。AIだけじゃ差別化できない時代。\n\nあなたの強みは何？',
            original_likes: 1680,
            original_retweets: 450,
            original_replies: 103,
            rewritten_text: 'ChatGPT副業で月10万稼ぐロードマップ（実証済み）\n\n【1-2ヶ月目】\n✓ プロンプト100本ノック\n✓ ポートフォリオ5本作成\n\n【3-4ヶ月目】\n✓ クラウドソーシングで実績\n✓ 低単価でも評価を集める\n\n【5-6ヶ月目】\n✓ 単価交渉＆リピーター獲得\n✓ 月10万達成\n\nこの順番、間違えると挫折する。\n\n今どのステップにいる？',
            thread: [
                '多くの人が失敗するのは「いきなり高単価を狙う」こと。\n\n実績ゼロで単価交渉は無理。まずは低単価でも「5つ星評価10件」を目指す。\n\nこれが次の単価アップの武器になる。'
            ],
            call_to_action: '今どのステップにいますか？次に何をしますか？',
            scores: {
                dwell_potential: 9,
                reply_potential: 9,
                virality: 8
            },
            image_url: 'https://via.placeholder.com/600x338/1d9bf0/ffffff?text=ChatGPT副業ロードマップ'
        }
    ];
    
    displayResults(mockResults);
}

function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-text">${message}</span>`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', () => {
    console.log('X バズ投稿生成AI - Ready');
    console.log('API Base URL:', API_BASE_URL);
});
