// API Endpoint
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://x-viral-tweet-api-172353178391.us-central1.run.app';

// DOM
const generateBtn = document.getElementById('generate-btn');
const statusSection = document.getElementById('status-section');
const statusText = document.getElementById('status-text');
const resultsSection = document.getElementById('results-section');
const resultsContainer = document.getElementById('results-container');
const resultsCount = document.getElementById('results-count');
const emptyState = document.getElementById('empty-state');
const summaryPanel = document.getElementById('summary-panel');

// Form
const accountsTextarea = document.getElementById('accounts');
const tweetsToAnalyzeInput = document.getElementById('tweets-to-analyze');
const tweetsToRewriteInput = document.getElementById('tweets-to-rewrite');
const minLikesInput = document.getElementById('min-likes');
const minRetweetsInput = document.getElementById('min-retweets');

generateBtn.addEventListener('click', handleGenerate);

async function handleGenerate() {
    const accounts = accountsTextarea.value
        .split('\n')
        .map(l => l.trim().replace(/^@/, ''))
        .filter(l => l.length > 0);

    if (accounts.length === 0) {
        showToast('アカウントを1つ以上入力してください', 'error');
        return;
    }

    const settings = {
        tweets_to_analyze: parseInt(tweetsToAnalyzeInput.value),
        tweets_to_rewrite: parseInt(tweetsToRewriteInput.value),
        min_likes: parseInt(minLikesInput.value),
        min_retweets: parseInt(minRetweetsInput.value),
        generate_images: false  // 画像生成はデフォルトOFF
    };

    // UI
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;"></div> 生成中...';
    emptyState.style.display = 'none';
    resultsSection.style.display = 'none';
    summaryPanel.style.display = 'none';
    statusSection.style.display = 'block';
    statusText.textContent = 'ツイートを収集中...';

    const startTime = Date.now();

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ accounts, settings })
        });

        if (!response.ok) {
            let detail = `HTTP ${response.status}`;
            try {
                const err = await response.json();
                if (err.detail) detail = err.detail;
            } catch (e) {}
            throw new Error(detail);
        }

        const data = await response.json();
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

        // 結果表示
        displayResults(data.results);
        displaySummary(data.summary, elapsed);

        statusSection.style.display = 'none';
        showToast(`${data.results.length}件のリライトを生成しました（${elapsed}秒）`, 'success');

    } catch (error) {
        console.error('Error:', error);
        statusText.textContent = `エラー: ${error.message}`;
        showToast(`エラー: ${error.message}`, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg> バズ投稿を生成';
    }
}

function displaySummary(summary, elapsed) {
    summaryPanel.style.display = 'block';
    document.getElementById('stat-collected').textContent = summary.total_collected;
    document.getElementById('stat-filtered').textContent = summary.total_filtered;
    document.getElementById('stat-analyzed').textContent = summary.total_analyzed;
    document.getElementById('stat-rewritten').textContent = summary.total_rewritten;

    if (summary.cost) {
        document.getElementById('cost-x-lookups').textContent = summary.cost.x_api_user_lookups || 0;
        document.getElementById('cost-x-reads').textContent = summary.cost.x_api_tweets_read || 0;
        document.getElementById('cost-x-usd').textContent = `$${(summary.cost.x_api_cost_usd || 0).toFixed(4)}`;
        document.getElementById('cost-analysis-calls').textContent = summary.cost.gemini_analysis_calls;
        document.getElementById('cost-rewrite-calls').textContent = summary.cost.gemini_rewrite_calls;
        document.getElementById('cost-gemini-usd').textContent = `$${(summary.cost.gemini_cost_usd || 0).toFixed(4)}`;
        document.getElementById('cost-jpy').textContent = `¥${summary.cost.estimated_cost_jpy.toFixed(2)}`;
        document.getElementById('cost-usd').textContent = `($${summary.cost.estimated_cost_usd.toFixed(4)})`;
    }
}

function displayResults(results) {
    resultsContainer.innerHTML = '';

    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:40px;">結果がありません</p>';
        resultsSection.style.display = 'block';
        return;
    }

    resultsCount.textContent = `${results.length}件`;

    results.forEach((result, index) => {
        resultsContainer.appendChild(createResultCard(result, index));
    });

    resultsSection.style.display = 'block';
}

function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';

    const scores = result.scores || {};
    const dwell = scores.dwell_potential || '-';
    const reply = scores.reply_potential || '-';
    const viral = scores.virality || '-';

    card.innerHTML = `
        <div class="result-card-inner">
            <div class="result-header">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span class="result-number">${index + 1}</span>
                    <span style="font-size:13px;color:var(--text-secondary);">${esc(result.original_url || '')}</span>
                </div>
                <div class="result-metrics">
                    <span class="metric"><svg width="14" height="14" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg> ${fmtNum(result.original_likes)}</span>
                    <span class="metric"><svg width="14" height="14" viewBox="0 0 24 24"><path d="M7 7h10v2l2 2-2 2v2H7v-2L5 11l2-2V7z"/></svg> ${fmtNum(result.original_retweets)}</span>
                    <span class="metric"><svg width="14" height="14" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg> ${fmtNum(result.original_replies)}</span>
                </div>
            </div>

            <div class="result-compare">
                <div class="result-col original">
                    <div class="result-label"><span class="label-dot original"></span> 元ツイート</div>
                    <div class="result-text">${esc(result.original_text)}</div>
                </div>
                <div class="result-col rewrite">
                    <div class="result-label"><span class="label-dot rewrite"></span> リライト</div>
                    <div class="result-text">${esc(result.rewritten_text)}</div>
                </div>
            </div>

            <div class="result-footer">
                <span class="score-badge">Dwell <span class="score-num">${dwell}</span></span>
                <span class="score-badge">Reply <span class="score-num">${reply}</span></span>
                <span class="score-badge">Viral <span class="score-num">${viral}</span></span>
                <button class="btn-copy" onclick="copyText(this, ${index})">コピー</button>
            </div>

            ${result.call_to_action ? `<div class="result-cta">${esc(result.call_to_action)}</div>` : ''}
        </div>
    `;

    // Store rewrite text for copy
    card.dataset.rewrite = result.rewritten_text + (result.call_to_action ? '\n\n' + result.call_to_action : '');

    return card;
}

function copyText(btn, index) {
    const card = btn.closest('.result-card');
    const text = card.dataset.rewrite || '';
    navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied!';
        btn.style.color = 'var(--accent-green)';
        btn.style.borderColor = 'var(--accent-green)';
        setTimeout(() => {
            btn.textContent = 'コピー';
            btn.style.color = '';
            btn.style.borderColor = '';
        }, 2000);
    });
}

function fmtNum(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return String(n);
}

function esc(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-text">${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('X バズ投稿生成AI - Ready');
    console.log('API:', API_BASE_URL);
});
