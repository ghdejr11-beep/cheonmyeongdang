/**
 * 천명당 entitlement 조회 API — 결제 이메일 기반
 *
 * POST /api/check-entitlement
 * body: { email: "user@example.com" }
 *
 * 응답:
 *   { ok: true, skus: ["no_ads_9900", "saju_premium_9900"], paid_at: "2026-..." }
 *   { ok: false, skus: [], reason: "..." }
 *
 * 클라이언트는 응답의 skus를 localStorage에 저장 후 광고 차단 등에 사용.
 * 비밀번호 0, 회원가입 0, 마찰 최소화.
 */
const https = require('https');
const { listPurchasesByEmail } = require('../lib/purchase-store');

// 인플루언서 쿠폰 redeem 기록(coupon_usage.json) 조회 — entitlement 백필
async function listInfluencerCouponsByEmail(email) {
  const ghToken = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = ((process.env.GIST_COUPON_USAGE_ID || process.env.GIST_ID) || '').trim();
  if (!ghToken || !gistId) return [];
  return new Promise((resolve) => {
    const req = https.request({
      hostname: 'api.github.com', port: 443,
      path: `/gists/${gistId}`, method: 'GET',
      headers: {
        Authorization: `Bearer ${ghToken}`,
        'User-Agent': 'cheonmyeongdang-entitlement',
        Accept: 'application/vnd.github+json',
      },
    }, (r) => {
      let buf = '';
      r.on('data', (c) => (buf += c));
      r.on('end', () => {
        try {
          const j = JSON.parse(buf);
          const file = j && j.files && j.files['coupon_usage.json'];
          if (!file || !file.content) return resolve([]);
          const data = JSON.parse(file.content);
          if (!data || !Array.isArray(data.usages)) return resolve([]);
          const targetEmail = String(email || '').trim().toLowerCase();
          const now = Date.now();
          const valid = data.usages.filter((u) => {
            if ((u.email || '').toLowerCase() !== targetEmail) return false;
            if (u.type !== 'influencer_30d') return false;
            if (!u.valid_until) return false;
            return Date.parse(u.valid_until) > now;
          });
          resolve(valid);
        } catch (e) { resolve([]); }
      });
    });
    req.on('error', () => resolve([]));
    req.end();
  });
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, skus: [], reason: 'POST only' });
  }

  let email = '';
  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    email = String(body.email || '').trim();
  } catch (e) {
    return res.status(400).json({ ok: false, skus: [], reason: 'Invalid JSON body' });
  }

  // 형식 검증 — 단순 이메일 패턴
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ ok: false, skus: [], reason: '올바른 이메일을 입력해주세요' });
  }

  const result = await listPurchasesByEmail(email);
  if (!result.ok) {
    return res.status(500).json({ ok: false, skus: [], reason: result.reason });
  }

  // SKU 목록 dedup + 정렬 (최신 결제일 기준)
  const records = result.records || [];
  const skuSet = new Set(records.map(r => r.skuId).filter(Boolean));
  const latestArr = records.map(r => r.paid_at).filter(Boolean).sort();
  let latest = latestArr.length ? latestArr[latestArr.length - 1] : null;

  // ─── 인플루언서 쿠폰 백필: purchases에 없어도 coupon_usage.json에 valid 기록 있으면 권한 부여 ───
  const influCoupons = await listInfluencerCouponsByEmail(email);
  if (influCoupons.length > 0) {
    ['saju_premium_9900', 'comprehensive_29900', 'subscribe_monthly_29900'].forEach(s => skuSet.add(s));
    const couponLatest = influCoupons.map(u => u.redeemed_at).filter(Boolean).sort().pop();
    if (couponLatest && (!latest || couponLatest > latest)) latest = couponLatest;
  }

  const skusList = [...skuSet];

  return res.status(200).json({
    ok: true,
    skus: skusList,
    count: skusList.length,
    raw_count: records.length + influCoupons.length,
    latest_paid_at: latest || null,
    has_influencer_coupon: influCoupons.length > 0,
    influencer_valid_until: influCoupons.length ? influCoupons[0].valid_until : null,
    // 토큰: 클라이언트가 localStorage에 저장 (위변조 방지보다는 entitlement 인식용)
    token: skusList.length > 0 ? Buffer.from(`${email.toLowerCase()}|${latest || ''}|${skusList.join(',')}`).toString('base64') : null,
  });
};
