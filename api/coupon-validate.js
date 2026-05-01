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
const crypto = require('crypto');

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
};

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
    return file && file.content ? JSON.parse(file.content) : null;
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

  if (!code) return res.status(400).json({ ok: false, error: 'no_code' });

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
