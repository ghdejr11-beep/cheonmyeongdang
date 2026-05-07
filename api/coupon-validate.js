/**
 * 천명당 쿠폰 검증 API
 * POST /api/coupon-validate
 *
 * 정적 쿠폰:
 *   - WELCOME2K     : ₩2,000 할인 (D+60 후속 메일 자동 발급)
 *   - VIP3X         : ₩3,000 할인 (3회 이상 결제자 자동 노출)
 *   - LAUNCH2026    : ₩1,000 할인 (출시 기념, 모두 사용 가능, ~2026-06-30)
 *   - SAJU5K        : ₩5,000 할인 (사주 정밀 풀이 한정, 신규 가입자 1회)
 *
 * 동적 윈백 쿠폰 (cron-followup이 결제 orderId 기반으로 발급):
 *   - WB30-XXXX     : 30% 할인 (D+30 윈백, 7일 유효, 1회용 per email)
 *   - WB90-XXXX     : 50% 할인 (D+90 윈백, 14일 유효, 1회용 per email)
 *   ※ XXXX는 HMAC-SHA256(orderId, COUPON_SIGNING_SECRET)의 첫 4자리 (서명 검증으로 위조 차단)
 *
 * Body: { code, email?, sku?, amount? }
 * Response:
 *   ok=true:  { ok, code, discount_amount, discount_pct, original, final, valid_until, restriction }
 *   ok=false: { ok: false, error }
 *
 * 보안:
 *   - 정적 쿠폰: 코드 상수
 *   - 동적 쿠폰: HMAC 서명 검증 (위조 불가) + Gist usage 카운트 (1회용 강제)
 *   - PG 결제 시 amount는 클라이언트에서 받지 말고 server-side에서 SKU price - coupon discount로 재계산
 */
const https = require('https');
const querystring = require('querystring');
const crypto = require('crypto');
const { appendPurchase } = require('../lib/purchase-store');

// ─── Magic-link redeem 토큰 (인플루언서 쿠폰 이메일 검증용) ───
// 토큰 = HMAC-SHA256(`${email}|${code}|${ts}`, INFLU_COUPON_SECRET).hex.slice(0,16)
// 유효시간: 30분 (ts 검증)
const MAGIC_LINK_TTL_MS = 30 * 60 * 1000;
const MAGIC_LINK_BASE = 'https://cheonmyeongdang.vercel.app/?coupon_redeem=true';

function buildMagicLinkToken(email, code, ts, secret) {
  const payload = `${String(email || '').toLowerCase()}|${String(code || '').toUpperCase()}|${ts}`;
  return crypto.createHmac('sha256', secret).update(payload).digest('hex').slice(0, 16);
}

function verifyMagicLinkToken(email, code, ts, token, secret) {
  if (!secret || !token || !ts) return { ok: false, reason: 'missing_params' };
  const tsNum = parseInt(ts, 10);
  if (!Number.isFinite(tsNum)) return { ok: false, reason: 'invalid_ts' };
  if (Date.now() - tsNum > MAGIC_LINK_TTL_MS) return { ok: false, reason: 'expired' };
  if (Date.now() - tsNum < -60 * 1000) return { ok: false, reason: 'future_ts' }; // clock skew 1min
  const expected = buildMagicLinkToken(email, code, tsNum, secret);
  // timing-safe compare
  const a = Buffer.from(expected);
  const b = Buffer.from(String(token));
  if (a.length !== b.length) return { ok: false, reason: 'bad_token' };
  if (!crypto.timingSafeEqual(a, b)) return { ok: false, reason: 'bad_token' };
  return { ok: true };
}

// ─── 매직링크 메일 발송 (Gmail SMTP App Password 또는 OAuth2 fallback — send-receipt.js와 동일 인프라) ───
function _refreshGmailAccessToken({ clientId, clientSecret, refreshToken }) {
  return new Promise((resolve, reject) => {
    const data = querystring.stringify({
      client_id: clientId, client_secret: clientSecret,
      refresh_token: refreshToken, grant_type: 'refresh_token',
    });
    const req = https.request({
      hostname: 'oauth2.googleapis.com', port: 443, path: '/token', method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(data),
      },
    }, (res) => {
      let buf = ''; res.on('data', (c) => (buf += c));
      res.on('end', () => {
        try {
          const j = JSON.parse(buf);
          if (j.access_token) resolve(j.access_token);
          else reject(new Error('OAuth refresh 실패: ' + buf));
        } catch (e) { reject(new Error('OAuth 응답 파싱 실패')); }
      });
    });
    req.on('error', reject); req.write(data); req.end();
  });
}

function _buildRawMessage({ from, to, subject, html, text }) {
  const boundary = '__cmd_magiclink_' + Date.now() + '__';
  const encSubject = '=?UTF-8?B?' + Buffer.from(subject, 'utf-8').toString('base64') + '?=';
  const lines = [
    `From: ${from}`,
    `To: ${to}`,
    `Subject: ${encSubject}`,
    'MIME-Version: 1.0',
    `Content-Type: multipart/alternative; boundary="${boundary}"`,
    '',
    `--${boundary}`,
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 7bit',
    '',
    text || '',
    '',
    `--${boundary}`,
    'Content-Type: text/html; charset=UTF-8',
    'Content-Transfer-Encoding: 7bit',
    '',
    html,
    '',
    `--${boundary}--`,
    '',
  ];
  return Buffer.from(lines.join('\r\n'), 'utf-8')
    .toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function _sendViaGmailApi({ accessToken, raw }) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ raw });
    const req = https.request({
      hostname: 'gmail.googleapis.com', port: 443,
      path: '/gmail/v1/users/me/messages/send', method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    }, (res) => {
      let buf = ''; res.on('data', (c) => (buf += c));
      res.on('end', () => {
        try {
          const j = JSON.parse(buf);
          if (res.statusCode >= 200 && res.statusCode < 300 && j.id) resolve({ id: j.id });
          else reject(new Error('Gmail API ' + res.statusCode + ': ' + buf.slice(0, 200)));
        } catch (e) { reject(new Error('Gmail API 파싱 실패')); }
      });
    });
    req.on('error', reject); req.write(data); req.end();
  });
}

async function _sendViaSmtp({ from, to, subject, html, text, user, pass }) {
  let nodemailer;
  try { nodemailer = require('nodemailer'); }
  catch (e) { throw new Error('nodemailer_unavailable'); }
  const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com', port: 465, secure: true,
    auth: { user, pass },
  });
  const info = await transporter.sendMail({ from, to, subject, html, text });
  return { id: info.messageId };
}

async function sendMagicLinkEmail(toEmail, magicUrl, code) {
  const fromAddr = (process.env.GMAIL_FROM || 'ghdejr11@gmail.com').trim();
  const from = `천명당 <${fromAddr}>`;
  const subject = '[천명당] 인플루언서 쿠폰 활성화 링크';
  const safeUrl = String(magicUrl).replace(/[<>&"']/g, '');
  const html = `<!DOCTYPE html><html><body style="margin:0;background:#080a10;font-family:-apple-system,'Noto Sans KR',sans-serif;color:#e8e0d0;">
<div style="max-width:560px;margin:0 auto;padding:32px 16px;">
  <div style="text-align:center;padding:20px 0;">
    <div style="font-family:'Gowun Batang',serif;font-size:26px;color:#e8c97a;letter-spacing:0.05em;">天命堂</div>
  </div>
  <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;">
    <h1 style="color:#e8c97a;font-size:20px;margin:0 0 16px;">쿠폰 활성화 링크</h1>
    <p style="color:#e8e0d0;font-size:14px;line-height:1.7;margin:0 0 18px;">
      안녕하세요. 인플루언서 쿠폰 <strong style="color:#e8c97a;">${String(code).replace(/[<>&"']/g,'')}</strong> 적용을 위해 본인 이메일 인증이 필요합니다.<br>
      아래 버튼을 클릭하여 30일 무료 구독을 활성화해 주세요. (30분 이내 유효)
    </p>
    <div style="text-align:center;margin:24px 0;">
      <a href="${safeUrl}" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:700;text-decoration:none;border-radius:8px;font-size:15px;">쿠폰 활성화 →</a>
    </div>
    <p style="color:#a89880;font-size:11px;line-height:1.6;margin:16px 0 0;">
      본인이 요청하지 않았다면 이 메일을 무시하세요. 링크는 30분 후 자동 만료됩니다.
    </p>
  </div>
  <div style="text-align:center;color:#7a6f5a;font-size:11px;line-height:1.8;padding:16px;">
    쿤스튜디오 · 사업자 552-59-00848 · ghdejr11@gmail.com
  </div>
</div></body></html>`;
  const text = `천명당 — 쿠폰 활성화 링크\n\n쿠폰 ${code} 적용을 위해 아래 링크를 클릭해 주세요 (30분 유효):\n\n${magicUrl}\n\n본인이 요청하지 않았다면 무시하세요.`;

  // 1) SMTP App Password 우선
  const appPass = (process.env.GMAIL_APP_PASSWORD || '').trim();
  let smtpError = null;
  if (appPass) {
    try {
      const r = await _sendViaSmtp({ from, to: toEmail, subject, html, text, user: fromAddr, pass: appPass });
      return { ok: true, method: 'smtp', messageId: r.id };
    } catch (err) {
      smtpError = err.message || String(err);
      console.error('[magic-link] SMTP 실패, OAuth2로 fallback:', smtpError);
    }
  } else {
    smtpError = 'GMAIL_APP_PASSWORD env not set';
  }
  // 2) OAuth2
  const clientId = (process.env.GMAIL_OAUTH_CLIENT_ID || '').trim();
  const clientSecret = (process.env.GMAIL_OAUTH_CLIENT_SECRET || '').trim();
  const refreshToken = (process.env.GMAIL_OAUTH_REFRESH_TOKEN || '').trim();
  if (clientId && clientSecret && refreshToken) {
    try {
      const accessToken = await _refreshGmailAccessToken({ clientId, clientSecret, refreshToken });
      const raw = _buildRawMessage({ from, to: toEmail, subject, html, text });
      const r = await _sendViaGmailApi({ accessToken, raw });
      return { ok: true, method: 'gmail-oauth', messageId: r.id };
    } catch (err) {
      return { ok: false, reason: 'oauth_send_failed: ' + err.message + ' | smtp_error: ' + (smtpError || 'no_smtp_attempted') };
    }
  }
  return { ok: false, reason: 'no_gmail_credentials | smtp_error: ' + (smtpError || 'unknown') };
}

// ─── 쿠폰 정의 ───
// expires는 ISO 날짜, null이면 무제한
const COUPONS = {
  WELCOME2K: {
    discount_amount: 2000,
    discount_pct: null,
    restriction: { min_amount: 9900, sku_in: null, single_use_per_email: true },
    valid_until: null,
    description: '돌아오신 고객 ₩2,000 할인',
  },
  VIP3X: {
    discount_amount: 3000,
    discount_pct: null,
    restriction: { min_amount: 9900, sku_in: null, single_use_per_email: true, requires_vip: true },
    valid_until: null,
    description: 'VIP 등급(3회 이상 결제) ₩3,000 할인',
  },
  LAUNCH2026: {
    discount_amount: 1000,
    discount_pct: null,
    restriction: { min_amount: 9900, sku_in: null, single_use_per_email: false },
    valid_until: '2026-06-30T23:59:59+09:00',
    description: '출시 기념 ₩1,000 할인',
  },
  SAJU5K: {
    discount_amount: 5000,
    discount_pct: null,
    restriction: { min_amount: 14900, sku_in: ['saju_premium_9900', 'comprehensive_29900'], single_use_per_email: true, new_customer_only: true },
    valid_until: '2026-06-30T23:59:59+09:00',
    description: '사주 정밀/종합 풀이 신규 가입자 ₩5,000 할인',
  },
  // ─── 대표자 친구 10명 무료 (5/7 발급, 100% 할인 = ₩0 결제) ───
  SAJUF001: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 1' },
  SAJUF002: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 2' },
  SAJUF003: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 3' },
  SAJUF004: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 4' },
  SAJUF005: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 5' },
  SAJUF006: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 6' },
  SAJUF007: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 7' },
  SAJUF008: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 8' },
  SAJUF009: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 9' },
  SAJUF010: { discount_amount: 9900, discount_pct: null, restriction: { sku_in: ['saju_premium_9900'], single_use_per_email: true }, valid_until: '2026-08-07T23:59:59+09:00', description: '친구 무료 (정밀 풀이) 10' },
};

// ─── 인플루언서 쿠폰 (KSAJU-NNNNN-XXXXXX) — HMAC 검증, 1코드 1사용, 30일 무료 ───
// 형식: KSAJU-{seed:5digits}-{hmac6}
// hmac6 = HMAC-SHA256(INFLU_COUPON_SECRET, seed_str).b32encode()[:6] (위·아래 영문 + 23456789)
// seed range: 00001..20000 (2만 unique codes)
// 검증: 서버에서 동일 HMAC 계산 후 매칭 → DB 없이 무한 확장
// 단일 사용 강제: Gist coupon_usage.json (코드 단위 dedup)
const INFLU_ALPHA = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
const INFLU_SEED_MIN = 1;
const INFLU_SEED_MAX = 20000;

function isValidInfluCode(code) {
  const m = String(code || '').match(/^KSAJU-(\d{5})-([A-Z0-9]{6})$/);
  if (!m) return null;
  const seed = parseInt(m[1], 10);
  if (seed < INFLU_SEED_MIN || seed > INFLU_SEED_MAX) return null;
  const secret = (process.env.INFLU_COUPON_SECRET || '').trim();
  if (!secret) return null;
  const seedStr = String(seed).padStart(5, '0');
  const h = crypto.createHmac('sha256', secret).update(seedStr).digest();
  // base32 (RFC 4648) — node 18+ supports buf.toString('base64') but not base32 directly. Implement.
  let b32 = '';
  let bits = 0, value = 0;
  for (let i = 0; i < h.length && b32.length < 6; i++) {
    value = (value << 8) | h[i];
    bits += 8;
    while (bits >= 5 && b32.length < 6) {
      b32 += INFLU_ALPHA[(value >>> (bits - 5)) & 31];
      bits -= 5;
    }
  }
  return b32 === m[2] ? { seed, code } : null;
}

// ─── 동적 윈백 쿠폰 검증 (WB30-XXXX / WB90-XXXX) ───
// cron-followup.js의 genWinbackCoupon과 동일 로직: 4자리 영숫자 = HMAC(prefix:orderId, secret).slice(0,4).upper
// orderId는 쿠폰 코드만으로는 알 수 없으므로, 본 검증은 "이 코드가 우리가 발급한 형식인지"만 확인.
// 실제 사용 횟수 제한은 single_use_per_email로 강제 (Gist usage 누적).
//
// 발급 후 7일/14일 유효는 결제 시점이 아니라 메일 발송 시점 기준 — 클라이언트 안내용.
// 검증은 사용 횟수 1회만 강제하고 정확한 시점 추적은 하지 않음(서버리스 환경에서 Gist round-trip 비용 고려).
function isValidWinbackCode(code) {
  const m = String(code || '').match(/^(WB30|WB90)-([0-9A-F]{4})$/);
  if (!m) return null;
  const prefix = m[1];
  return {
    prefix,
    discount_pct: prefix === 'WB30' ? 30 : 50,
    description: prefix === 'WB30' ? 'D+30 윈백 30% 할인' : 'D+90 윈백 50% 할인',
    target_skus:
      prefix === 'WB30'
        ? ['comprehensive_29900', 'subscribe_monthly_29900', 'subscribe_basic_2900', 'sinnyeon_15000']
        : ['comprehensive_29900'],
    valid_days: prefix === 'WB30' ? 7 : 14,
  };
}

function jsonReq(opts, body) {
  return new Promise((resolve) => {
    const data = body ? JSON.stringify(body) : null;
    if (data) {
      opts.headers = opts.headers || {};
      opts.headers['Content-Type'] = 'application/json';
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
    req.on('error', () => resolve({ ok: false, status: 0, body: null }));
    if (data) req.write(data);
    req.end();
  });
}

async function readGist(gistId, token, filename) {
  if (!token || !gistId) return null;
  const res = await jsonReq({
    hostname: 'api.github.com', port: 443,
    path: `/gists/${gistId}`, method: 'GET',
    headers: { Authorization: `Bearer ${token}`, 'User-Agent': 'cheonmyeongdang-coupon' },
  });
  try {
    const file = res.body && res.body.files && res.body.files[filename];
    const parsed = file && file.content ? JSON.parse(file.content) : null;
    if (parsed && typeof parsed === 'object') {
      // race-condition 검증용 메타데이터 — etag/updated_at 보존 (Gist API 응답 기반)
      Object.defineProperty(parsed, '__etag', { value: res.body && res.body.history && res.body.history[0] && res.body.history[0].version || null, enumerable: false });
      Object.defineProperty(parsed, '__updated_at', { value: res.body && res.body.updated_at || null, enumerable: false });
    }
    return parsed;
  } catch (e) { return null; }
}

async function getCustomerStats(email) {
  const ghToken = process.env.GITHUB_TOKEN;
  const gistId = process.env.GIST_ID;
  if (!ghToken || !gistId || !email) return { paid_count: 0, vip: false, is_new: true };
  const data = await readGist(gistId, ghToken, 'purchases.json');
  if (!data || !Array.isArray(data.purchases)) return { paid_count: 0, vip: false, is_new: true };
  const myPurchases = data.purchases.filter((p) => (p.customerEmail || '').toLowerCase() === email.toLowerCase() && p.status !== 'refunded');
  const paid_count = myPurchases.length;
  return {
    paid_count,
    vip: paid_count >= 3,
    is_new: paid_count === 0,
  };
}

async function getCouponUsageCount(code, email) {
  const ghToken = process.env.GITHUB_TOKEN;
  const gistId = process.env.GIST_COUPON_USAGE_ID || process.env.GIST_ID;
  if (!ghToken || !gistId) return 0;
  const data = await readGist(gistId, ghToken, 'coupon_usage.json');
  if (!data || !Array.isArray(data.usages)) return 0;
  return data.usages.filter((u) => u.code === code && (u.email || '').toLowerCase() === (email || '').toLowerCase()).length;
}

// ─── INFLU: 코드 단독 사용 검증 (이메일 무관, 코드 1회 = 글로벌 dead) ───
async function getCouponUsageByCodeOnly(code) {
  const ghToken = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = ((process.env.GIST_COUPON_USAGE_ID || process.env.GIST_ID) || '').trim();
  if (!ghToken || !gistId) return null;
  const data = await readGist(gistId, ghToken, 'coupon_usage.json');
  if (!data || !Array.isArray(data.usages)) return null;
  return data.usages.find((u) => u.code === code) || null;
}

async function recordCouponUsage(code, email, type, validUntil) {
  const ghToken = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = ((process.env.GIST_COUPON_USAGE_ID || process.env.GIST_ID) || '').trim();
  if (!ghToken || !gistId) return { ok: false, error: 'no_token_or_gist' };

  // ─── Race-condition 방어 (옵션 B) ───
  // 1) 0~150ms 랜덤 지연 → 동시 도달 요청 분산
  // 2) 첫 readGist에 이미 동일 code 존재 시 → 즉시 false (이미 사용됨)
  // 3) PATCH 완료 후 200ms 대기 → 재read하여 race 검증
  // 4) 같은 code의 record가 2개 이상이면 → redeemed_at 가장 빠른 것이 winner
  //    - 자신이 winner 아니면 → 자신의 record 제거(PATCH) + already_used 반환
  const myRedeemedAt = new Date().toISOString();
  const myRecord = {
    code,
    email: (email || '').toLowerCase(),
    type,
    valid_until: validUntil || null,
    redeemed_at: myRedeemedAt,
  };

  // (1) jitter
  await new Promise((r) => setTimeout(r, Math.floor(Math.random() * 150)));

  // (2) pre-check: 첫 readGist
  const existing = (await readGist(gistId, ghToken, 'coupon_usage.json')) || { usages: [] };
  if (!Array.isArray(existing.usages)) existing.usages = [];
  const alreadyUsed = existing.usages.find((u) => u && u.code === code);
  if (alreadyUsed) {
    return {
      ok: false,
      status: 409,
      error: 'already_used',
      body_excerpt: `pre-check: code ${code} already used by ${alreadyUsed.email || 'unknown'} at ${alreadyUsed.redeemed_at || 'unknown'}`,
      already_used: true,
      existing_record: alreadyUsed,
    };
  }

  // (3) PATCH (push my record)
  existing.usages.push(myRecord);
  const patch = await jsonReq({
    hostname: 'api.github.com', port: 443,
    path: `/gists/${gistId}`, method: 'PATCH',
    headers: { Authorization: `Bearer ${ghToken}`, 'User-Agent': 'cheonmyeongdang-coupon', 'Accept': 'application/vnd.github+json' },
  }, {
    files: { 'coupon_usage.json': { content: JSON.stringify(existing, null, 2) } },
  });
  if (!patch.ok) {
    return { ok: false, status: patch.status, body_excerpt: patch.body ? JSON.stringify(patch.body).slice(0, 200) : (patch.raw || '').slice(0, 200) };
  }

  // (4) Double-check after PATCH: 200ms wait + re-read
  // GitHub Gist PATCH semantics: "last-writer-wins" — 전체 파일 content를 replace.
  // 다중 동시 PATCH 시 각 writer가 비어있는 existing 보고 push → 마지막 PATCH가
  // 이전 PATCH 모두 덮어씀 → 마지막 writer 1명만 store에 남는다.
  // 따라서 verify-after-PATCH에서 "내 record가 살아남았는가"로 winner 판정.
  await new Promise((r) => setTimeout(r, 200));
  const verify = (await readGist(gistId, ghToken, 'coupon_usage.json')) || { usages: [] };
  if (!Array.isArray(verify.usages)) verify.usages = [];
  const sameCodeRecords = verify.usages.filter((u) => u && u.code === code);

  const myRecordExists = sameCodeRecords.some(
    (u) => u.redeemed_at === myRedeemedAt && (u.email || '') === (email || '').toLowerCase()
  );

  if (!myRecordExists) {
    // 내 PATCH가 다른 writer의 PATCH로 덮어씀 ("last-writer-wins" overwrite)
    // 같은 code의 다른 record가 살아있으면 → race lost (이미 사용됨)
    // 같은 code 없이 다른 code들만 살아있으면 → 다른 code redeem이 내 PATCH 덮은 것 → retry
    if (sameCodeRecords.length > 0) {
      const survivor = sameCodeRecords[0];
      return {
        ok: false,
        status: 409,
        error: 'already_used',
        race_detected: true,
        i_am_loser: true,
        body_excerpt: `race lost: my record overwritten by same-code winner. survivor=${survivor.email} at ${survivor.redeemed_at}`,
        existing_record: survivor,
      };
    }
    // 같은 code가 store에 없음 = 다른 코드 redeem 또는 외부 작업이 내 PATCH를 덮음
    // → retry: verify에 내 record 추가하고 한 번 더 PATCH
    verify.usages.push(myRecord);
    const retryPatch = await jsonReq({
      hostname: 'api.github.com', port: 443,
      path: `/gists/${gistId}`, method: 'PATCH',
      headers: { Authorization: `Bearer ${ghToken}`, 'User-Agent': 'cheonmyeongdang-coupon', 'Accept': 'application/vnd.github+json' },
    }, {
      files: { 'coupon_usage.json': { content: JSON.stringify(verify, null, 2) } },
    });
    if (!retryPatch.ok) {
      return { ok: false, status: retryPatch.status, body_excerpt: 'retry PATCH failed: ' + ((retryPatch.body ? JSON.stringify(retryPatch.body).slice(0, 200) : (retryPatch.raw || '').slice(0, 200))) };
    }
    // retry 후 재검증
    await new Promise((r) => setTimeout(r, 200));
    const reverify = (await readGist(gistId, ghToken, 'coupon_usage.json')) || { usages: [] };
    if (!Array.isArray(reverify.usages)) reverify.usages = [];
    const reSameCode = reverify.usages.filter((u) => u && u.code === code);
    const reMyExists = reSameCode.some(
      (u) => u.redeemed_at === myRedeemedAt && (u.email || '') === (email || '').toLowerCase()
    );
    if (reMyExists && reSameCode.length === 1) {
      return { ok: true, status: retryPatch.status, retried: true, body_excerpt: 'retry success' };
    }
    if (!reMyExists && reSameCode.length > 0) {
      // 재시도 중에도 동일 코드 다른 record가 들어옴 → loser
      return {
        ok: false,
        status: 409,
        error: 'already_used',
        race_detected: true,
        i_am_loser: true,
        retried: true,
        body_excerpt: 'race lost on retry',
        existing_record: reSameCode[0],
      };
    }
    // 알 수 없는 상태 — 보수적으로 ok 반환 (내 record가 살아있음)
    return { ok: true, status: retryPatch.status, retried: true, body_excerpt: 'retry uncertain but myRecord present' };
  }

  // 내 record가 살아남음.
  // (이론상 거의 발생하지 않지만) 같은 code의 다른 record가 함께 살아있으면(서로 다른 위치 push) cleanup.
  if (sameCodeRecords.length > 1) {
    // tie-breaker: redeemed_at 가장 빠른 것이 winner
    const sorted = sameCodeRecords.slice().sort((a, b) => {
      const ta = a.redeemed_at || '';
      const tb = b.redeemed_at || '';
      if (ta !== tb) return ta < tb ? -1 : 1;
      return (a.email || '').localeCompare(b.email || '');
    });
    const winner = sorted[0];
    const iAmWinner = winner.redeemed_at === myRedeemedAt && (winner.email || '') === (email || '').toLowerCase();

    if (iAmWinner) {
      const cleaned = verify.usages.filter((u) => {
        if (!u || u.code !== code) return true;
        return u.redeemed_at === winner.redeemed_at && (u.email || '') === (winner.email || '');
      });
      verify.usages = cleaned;
      const cleanupPatch = await jsonReq({
        hostname: 'api.github.com', port: 443,
        path: `/gists/${gistId}`, method: 'PATCH',
        headers: { Authorization: `Bearer ${ghToken}`, 'User-Agent': 'cheonmyeongdang-coupon', 'Accept': 'application/vnd.github+json' },
      }, {
        files: { 'coupon_usage.json': { content: JSON.stringify(verify, null, 2) } },
      });
      return {
        ok: true,
        status: patch.status,
        race_detected: true,
        cleanup_ok: cleanupPatch.ok,
        losers_removed: sameCodeRecords.length - 1,
        body_excerpt: `race winner=${email}, removed ${sameCodeRecords.length - 1} losers (cleanup ${cleanupPatch.ok ? 'ok' : 'failed'})`,
      };
    } else {
      const cleaned = verify.usages.filter((u) => {
        if (!u || u.code !== code) return true;
        return !(u.redeemed_at === myRedeemedAt && (u.email || '') === (email || '').toLowerCase());
      });
      verify.usages = cleaned;
      await jsonReq({
        hostname: 'api.github.com', port: 443,
        path: `/gists/${gistId}`, method: 'PATCH',
        headers: { Authorization: `Bearer ${ghToken}`, 'User-Agent': 'cheonmyeongdang-coupon', 'Accept': 'application/vnd.github+json' },
      }, {
        files: { 'coupon_usage.json': { content: JSON.stringify(verify, null, 2) } },
      });
      return {
        ok: false,
        status: 409,
        error: 'already_used',
        race_detected: true,
        i_am_loser: true,
        body_excerpt: `race lost: winner=${winner.email} at ${winner.redeemed_at}, my=${email} at ${myRedeemedAt}`,
        existing_record: winner,
      };
    }
  }

  // 정상 케이스: 내 record만 살아있음
  return { ok: true, status: patch.status, body_excerpt: patch.body ? JSON.stringify(patch.body).slice(0, 200) : (patch.raw || '').slice(0, 200) };
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method' });

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  const code = String(body.code || '').trim().toUpperCase();
  const email = String(body.email || '').trim().toLowerCase();
  const sku = String(body.sku || '').trim();
  const amount = parseInt(body.amount || '0', 10) || 0;
  const mode = String(body.mode || 'validate').trim().toLowerCase(); // 'validate' | 'redeem'

  if (!code) return res.status(400).json({ ok: false, error: 'no_code' });

  // ─── 인플루언서 쿠폰 (KSAJU-NNNNN-XXXXXX) — HMAC 검증, 1코드 1사용, 30일 무료 ───
  const influ = isValidInfluCode(code);
  if (influ) {
    try {
      let used = null;
      try { used = await getCouponUsageByCodeOnly(code); } catch (e) { used = null; }
      if (used) {
        return res.status(409).json({
          ok: false, error: 'already_used',
          message: '이미 사용된 쿠폰입니다.',
          redeemed_at: used.redeemed_at,
        });
      }
      // ─── mode='redeem_request': 이메일 받음 → magic-link 토큰 생성 → 메일 발송 (entitlement 부여 X) ───
      if (mode === 'redeem_request') {
        if (!email) return res.status(400).json({ ok: false, error: 'email_required_for_redeem' });
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          return res.status(400).json({ ok: false, error: 'invalid_email_format' });
        }
        const secret = (process.env.INFLU_COUPON_SECRET || '').trim();
        if (!secret) return res.status(500).json({ ok: false, error: 'server_misconfigured' });
        const ts = Date.now();
        const token = buildMagicLinkToken(email, code, ts, secret);
        const magicUrl = `${MAGIC_LINK_BASE}&code=${encodeURIComponent(code)}&email=${encodeURIComponent(email)}&token=${token}&ts=${ts}`;
        const sendResult = await sendMagicLinkEmail(email, magicUrl, code);
        if (!sendResult.ok) {
          return res.status(500).json({
            ok: false, error: 'email_send_failed',
            message: '이메일 발송 실패. 잠시 후 다시 시도해 주세요.',
            debug: { reason: sendResult.reason },
          });
        }
        return res.status(200).json({
          ok: true, sent: true, mode: 'redeem_request',
          message: `${email}로 쿠폰 활성화 링크를 발송했습니다. 메일함을 확인해 주세요. (30분 유효)`,
          method: sendResult.method,
        });
      }

      // ─── mode='redeem_confirm' (또는 legacy 'redeem' + token): 토큰 검증 후 entitlement 부여 ───
      if (mode === 'redeem_confirm' || (mode === 'redeem' && body.token)) {
        if (!email) return res.status(400).json({ ok: false, error: 'email_required_for_redeem' });
        const secret = (process.env.INFLU_COUPON_SECRET || '').trim();
        if (!secret) return res.status(500).json({ ok: false, error: 'server_misconfigured' });
        const token = String(body.token || '').trim();
        const ts = body.ts || body.timestamp;
        const verify = verifyMagicLinkToken(email, code, ts, token, secret);
        if (!verify.ok) {
          return res.status(401).json({
            ok: false, error: 'invalid_token',
            reason: verify.reason,
            message: verify.reason === 'expired'
              ? '활성화 링크가 만료되었습니다 (30분 초과). 쿠폰 입력 → 이메일 재요청해 주세요.'
              : '잘못된 활성화 링크입니다.',
          });
        }
        const validUntil = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();
        let recordResult = { ok: false };
        try { recordResult = await recordCouponUsage(code, email, 'influencer_30d', validUntil); } catch (e) { recordResult = { ok: false, error: String(e && e.message || e) }; }
        if (!recordResult.ok) {
          return res.status(500).json({
            ok: false, error: 'recording_failed',
            message: '저장 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.',
            debug: { status: recordResult.status, body: recordResult.body_excerpt, err: recordResult.error },
          });
        }
        const orderId = `infl_${code}_${Date.now()}`;
        const grantedSkus = ['saju_premium_9900', 'comprehensive_29900', 'subscribe_monthly_29900'];
        let purchaseResults = [];
        for (const skuItem of grantedSkus) {
          try {
            const r = await appendPurchase({
              orderId: `${orderId}_${skuItem}`,
              paymentKey: `coupon_${code}`,
              customerEmail: email,
              customerName: '[인플루언서 무료]',
              skuId: skuItem,
              skuName: `[인플루언서 30일 무료] ${skuItem}`,
              amount: 0,
              method: '쿠폰',
              paid_at: new Date().toISOString(),
              valid_until: validUntil,
              followup_sent: true,
              refunded: false,
              source: 'influencer_coupon',
              coupon_code: code,
            });
            purchaseResults.push({ sku: skuItem, ok: r.ok, reason: r.reason || null });
          } catch (e) {
            purchaseResults.push({ sku: skuItem, ok: false, reason: String(e && e.message || e) });
          }
        }
        const entitlement_ok = purchaseResults.every(p => p.ok);
        return res.status(200).json({
          ok: true, code, mode: 'redeemed',
          coupon_type: 'influencer_30d',
          description: '인플루언서 30일 무료 구독권',
          granted_email: email,
          granted_skus: grantedSkus,
          valid_until: validUntil,
          entitlement_ok,
          entitlement_debug: entitlement_ok ? null : purchaseResults,
          message: entitlement_ok
            ? '쿠폰 적용 완료. 30일 무료 구독이 활성화되었습니다.'
            : '쿠폰은 적용되었으나 일부 권한 등록에 실패했습니다. 고객센터로 문의해주세요.',
        });
      }

      // ─── 레거시 mode='redeem' (token 없음) — 보안상 차단, redeem_request로 유도 ───
      if (mode === 'redeem') {
        return res.status(400).json({
          ok: false,
          error: 'redeem_requires_email_verification',
          message: '쿠폰 적용을 위해 이메일 인증이 필요합니다. 먼저 mode=redeem_request로 활성화 링크를 받아주세요.',
        });
      }
      // validate 모드 (preview): 사용 가능 여부만 반환
      return res.status(200).json({
        ok: true, code, mode: 'preview',
        coupon_type: 'influencer_30d',
        description: '인플루언서 30일 무료 구독권 (사용 시 즉시 활성화)',
        restriction: { single_use_per_code: true, free_subscription_days: 30 },
      });
    } catch (err) {
      return res.status(500).json({ ok: false, error: 'influ_branch_error', message: String(err && err.message || err) });
    }
  }

  // ─── 동적 윈백 쿠폰 (WB30-XXXX / WB90-XXXX) 우선 처리 ───
  const wb = isValidWinbackCode(code);
  if (wb) {
    // 1회용 per email 강제 (single_use_per_email)
    if (email) {
      const count = await getCouponUsageCount(code, email);
      if (count >= 1) return res.status(409).json({ ok: false, error: 'already_used' });
    }
    // 적용 가능 SKU 검증
    if (sku && !wb.target_skus.includes(sku)) {
      return res.status(400).json({ ok: false, error: 'sku_not_eligible', allowed_skus: wb.target_skus });
    }
    const discount_amount = amount ? Math.floor((amount * wb.discount_pct) / 100) : 0;
    const final_amount = amount ? Math.max(0, amount - discount_amount) : null;
    return res.status(200).json({
      ok: true,
      code,
      discount_amount,
      discount_pct: wb.discount_pct,
      description: wb.description,
      original: amount || null,
      final: final_amount,
      valid_until: null, // 발송 시점 기반 클라이언트 안내 — 검증은 1회용 per email로 강제
      restriction: { single_use_per_email: true, sku_in: wb.target_skus },
      coupon_type: 'winback_dynamic',
    });
  }

  const coupon = COUPONS[code];
  if (!coupon) return res.status(404).json({ ok: false, error: 'invalid_code' });

  // 만료 검증
  if (coupon.valid_until) {
    const now = Date.now();
    const expires = Date.parse(coupon.valid_until);
    if (now > expires) return res.status(410).json({ ok: false, error: 'expired', valid_until: coupon.valid_until });
  }

  const r = coupon.restriction || {};

  // 최소 금액 검증
  if (r.min_amount && amount && amount < r.min_amount) {
    return res.status(400).json({ ok: false, error: 'amount_too_low', min_amount: r.min_amount });
  }

  // SKU 제약
  if (r.sku_in && sku && !r.sku_in.includes(sku)) {
    return res.status(400).json({ ok: false, error: 'sku_not_eligible', allowed_skus: r.sku_in });
  }

  // 1인 1회 / VIP / 신규 가입자 검증 (email 있을 때만)
  if (email) {
    if (r.single_use_per_email) {
      const count = await getCouponUsageCount(code, email);
      if (count >= 1) return res.status(409).json({ ok: false, error: 'already_used' });
    }
    if (r.requires_vip || r.new_customer_only) {
      const stats = await getCustomerStats(email);
      if (r.requires_vip && !stats.vip) return res.status(403).json({ ok: false, error: 'not_vip', paid_count: stats.paid_count });
      if (r.new_customer_only && !stats.is_new) return res.status(403).json({ ok: false, error: 'not_new_customer' });
    }
  }

  // 할인 계산
  let discount_amount = 0;
  if (coupon.discount_amount) discount_amount = coupon.discount_amount;
  if (coupon.discount_pct && amount) discount_amount = Math.floor(amount * coupon.discount_pct / 100);
  const final_amount = amount ? Math.max(0, amount - discount_amount) : null;

  return res.status(200).json({
    ok: true,
    code,
    discount_amount,
    discount_pct: coupon.discount_pct,
    description: coupon.description,
    original: amount || null,
    final: final_amount,
    valid_until: coupon.valid_until,
    restriction: r,
  });
};
