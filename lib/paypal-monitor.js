/**
 * 천명당 PayPal 일일 매출 모니터 — Vercel Cron (매일 00:00 UTC = 09:00 KST).
 *
 * 기존 paypal_daily_monitor.py (로컬 schtask)의 Vercel 이전판.
 * - 로컬 PC OFF 상태에서도 24/7 동작
 * - PayPal env vars (PAYPAL_CLIENT_ID/SECRET/ENV)는 Vercel env에 이미 등록됨
 *
 * 인증:
 *   - Vercel Cron 호출: Authorization: Bearer ${CRON_SECRET}
 *   - 수동 테스트: GET /api/paypal-daily-cron?test=1&key=${FOLLOWUP_TEST_KEY}
 *
 * 데이터 저장: GitHub Gist (GIST_ID + GITHUB_TOKEN — 이미 cheonmyeongdang에서 사용 중)
 *   - paypal_state.json = { seen_ids: [...], daily: {YYYY-MM-DD: {tx_count, total_value, ...}} }
 *
 * 텔레그램 push: TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
 *   - 신규 거래 있으면: "💰 PayPal 신규 N건 / 합계 $X" 알림
 *   - 신규 0건이면: 조용히 통과 (스팸 방지)
 */
const https = require('https');

const PP_BASE_LIVE = 'https://api-m.paypal.com';
const PP_BASE_SANDBOX = 'https://api-m.sandbox.paypal.com';

function jsonReq(opts, body) {
  return new Promise((resolve) => {
    const data = body ? (typeof body === 'string' ? body : JSON.stringify(body)) : null;
    if (data) {
      opts.headers = opts.headers || {};
      if (!opts.headers['Content-Type']) opts.headers['Content-Type'] = 'application/json';
      opts.headers['Content-Length'] = Buffer.byteLength(data);
    }
    const req = https.request(opts, (res) => {
      let buf = '';
      res.on('data', (c) => (buf += c));
      res.on('end', () => {
        let parsed = null;
        try { parsed = JSON.parse(buf); } catch (e) {}
        resolve({ ok: res.statusCode >= 200 && res.statusCode < 300, status: res.statusCode, body: parsed, raw: buf });
      });
    });
    req.on('error', (e) => resolve({ ok: false, status: 0, body: null, error: String(e) }));
    if (data) req.write(data);
    req.end();
  });
}

async function getPayPalToken() {
  const clientId = (process.env.PAYPAL_CLIENT_ID || '').trim();
  const secret = (process.env.PAYPAL_CLIENT_SECRET || '').trim();
  if (!clientId || !secret) throw new Error('PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET missing');
  const ppEnv = (process.env.PAYPAL_ENV || 'live').toLowerCase();
  const base = ppEnv === 'sandbox' ? PP_BASE_SANDBOX : PP_BASE_LIVE;
  const auth = Buffer.from(`${clientId}:${secret}`).toString('base64');
  const r = await jsonReq({
    hostname: base.replace('https://', ''),
    port: 443,
    path: '/v1/oauth2/token',
    method: 'POST',
    headers: {
      Authorization: `Basic ${auth}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  }, 'grant_type=client_credentials');
  if (!r.ok || !r.body || !r.body.access_token) throw new Error('PayPal token failed: ' + (r.raw || '').slice(0, 200));
  return { token: r.body.access_token, base };
}

async function fetchTransactions(token, base, days = 2) {
  const end = new Date();
  const start = new Date(end.getTime() - days * 86400 * 1000);
  const fmt = (d) => d.toISOString().slice(0, 19) + '-0000';
  const params = new URLSearchParams({
    start_date: fmt(start),
    end_date: fmt(end),
    fields: 'transaction_info,payer_info',
    page_size: '100',
  }).toString();
  const r = await jsonReq({
    hostname: base.replace('https://', ''),
    port: 443,
    path: `/v1/reporting/transactions?${params}`,
    method: 'GET',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new Error('PayPal fetch failed: ' + (r.raw || '').slice(0, 200));
  return (r.body && r.body.transaction_details) || [];
}

// ─── GitHub Gist storage ───
const GIST_FILE = 'paypal_state.json';

async function readGistState() {
  const ghToken = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = ((process.env.GIST_PAYPAL_ID || process.env.GIST_ID) || '').trim();
  if (!ghToken || !gistId) return { seen_ids: [], daily: {} };
  const r = await jsonReq({
    hostname: 'api.github.com', port: 443,
    path: `/gists/${gistId}`, method: 'GET',
    headers: {
      Authorization: `Bearer ${ghToken}`,
      'User-Agent': 'cheonmyeongdang-paypal-cron',
      Accept: 'application/vnd.github+json',
    },
  });
  if (!r.ok || !r.body) return { seen_ids: [], daily: {} };
  const file = r.body.files && r.body.files[GIST_FILE];
  if (!file || !file.content) return { seen_ids: [], daily: {} };
  try {
    const parsed = JSON.parse(file.content);
    return {
      seen_ids: Array.isArray(parsed.seen_ids) ? parsed.seen_ids : [],
      daily: parsed.daily && typeof parsed.daily === 'object' ? parsed.daily : {},
    };
  } catch (e) { return { seen_ids: [], daily: {} }; }
}

async function writeGistState(state) {
  const ghToken = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = ((process.env.GIST_PAYPAL_ID || process.env.GIST_ID) || '').trim();
  if (!ghToken || !gistId) return { ok: false, reason: 'missing_credentials' };
  const r = await jsonReq({
    hostname: 'api.github.com', port: 443,
    path: `/gists/${gistId}`, method: 'PATCH',
    headers: {
      Authorization: `Bearer ${ghToken}`,
      'User-Agent': 'cheonmyeongdang-paypal-cron',
      Accept: 'application/vnd.github+json',
    },
  }, {
    files: {
      [GIST_FILE]: {
        content: JSON.stringify({
          seen_ids: state.seen_ids.slice(-5000), // 최근 5000건만 보관 (Gist 1MB 한도)
          daily: state.daily,
          updated_at: new Date().toISOString(),
        }, null, 2),
      },
    },
  });
  return { ok: r.ok, status: r.status };
}

// ─── Telegram push ───
async function pushTelegram(text) {
  const token = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const chatId = (process.env.TELEGRAM_CHAT_ID || '').trim();
  if (!token || !chatId) return { ok: false, reason: 'missing_telegram_credentials' };
  const data = new URLSearchParams({
    chat_id: chatId,
    text: text,
    parse_mode: 'HTML',
    disable_web_page_preview: 'true',
  }).toString();
  const r = await jsonReq({
    hostname: 'api.telegram.org', port: 443,
    path: `/bot${token}/sendMessage`, method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  }, data);
  return { ok: r.ok, status: r.status };
}

/**
 * PayPal 일일 매출 monitor — cron-followup.js에서 호출.
 * 인증·라우팅은 caller(cron-followup)가 처리. 이 함수는 순수 monitor 로직만.
 *
 * 반환: { ok, today_kst, total_tx_fetched, new_tx_count, today_count, today_total, currencies, gist_saved, telegram_pushed }
 */
async function runPayPalMonitor() {
  try {
    // 1. PayPal token
    const { token, base } = await getPayPalToken();

    // 2. 최근 2일치 거래 fetch
    const txs = await fetchTransactions(token, base, 2);

    // 3. Gist에서 이전 state 읽기
    const state = await readGistState();
    const seen = new Set(state.seen_ids);

    // 4. 신규 거래 detect + 일일 통계 계산
    const todayKST = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
    const newTxs = [];
    let todayCount = 0;
    let todayTotal = 0;
    const currencies = {};

    for (const t of txs) {
      const info = (t && t.transaction_info) || {};
      const tid = info.transaction_id || '';
      if (!tid) continue;
      if (!seen.has(tid)) {
        newTxs.push(t);
        seen.add(tid);
      }
      const dateKST = (info.transaction_initiation_date || '').slice(0, 10); // KST 변환은 PayPal 응답이 UTC이지만 단순 비교
      if (dateKST === todayKST) {
        todayCount += 1;
        const amount = (info.transaction_amount && info.transaction_amount.value) || '0';
        const currency = (info.transaction_amount && info.transaction_amount.currency_code) || 'USD';
        try {
          todayTotal += parseFloat(amount) || 0;
          currencies[currency] = (currencies[currency] || 0) + (parseFloat(amount) || 0);
        } catch (e) {}
      }
    }

    // 5. 일일 통계 갱신
    state.seen_ids = Array.from(seen);
    state.daily = state.daily || {};
    state.daily[todayKST] = {
      date: todayKST,
      tx_count: todayCount,
      total_value: Math.round(todayTotal * 100) / 100,
      currencies,
      checked_at: new Date().toISOString(),
    };

    // 6. Gist 저장
    const gistResult = await writeGistState(state);

    // 7. 텔레그램 push (신규 거래 있을 때만)
    let telegramResult = null;
    if (newTxs.length > 0) {
      const lines = [`💰 <b>PayPal 신규 거래 ${newTxs.length}건</b>`, `📅 ${todayKST}`];
      for (const t of newTxs.slice(0, 10)) {
        const info = (t && t.transaction_info) || {};
        const payer = (t && t.payer_info) || {};
        const amt = info.transaction_amount || {};
        const email = (payer.email_address || '?').toString();
        const edom = email.includes('@') ? email.split('@')[1] : '?';
        const datetime = (info.transaction_initiation_date || '?').slice(0, 19).replace('T', ' ');
        lines.push(`  ${datetime} | ${amt.value || '0'} ${amt.currency_code || '?'} | @${edom}`);
      }
      if (newTxs.length > 10) lines.push(`  ... 외 ${newTxs.length - 10}건`);
      lines.push('');
      lines.push(`📊 오늘 합계: ${todayCount}건 / $${(todayTotal).toFixed(2)}`);
      telegramResult = await pushTelegram(lines.join('\n'));
    }

    return {
      ok: true,
      checked_at: new Date().toISOString(),
      today_kst: todayKST,
      total_tx_fetched: txs.length,
      new_tx_count: newTxs.length,
      today_count: todayCount,
      today_total: Math.round(todayTotal * 100) / 100,
      currencies,
      gist_saved: gistResult.ok,
      telegram_pushed: telegramResult ? telegramResult.ok : 'no_new_tx_skipped',
    };
  } catch (e) {
    console.error('paypal-monitor error:', e);
    // 에러 시 텔레그램으로 알림
    try { await pushTelegram(`🚨 <b>PayPal cron 실패</b>\n${(e && e.message) || e}`); } catch (te) {}
    return { ok: false, error: (e && e.message) || String(e) };
  }
}

module.exports = { runPayPalMonitor };
