/**
 * 천명당 VIP 등급 조회 API
 * GET /api/vip-status?email=xxx
 *
 * 등급 기준 (누적 결제 횟수 기반, 환불 제외):
 *   - 일반 (0회): 일반 가격 + LAUNCH2026 쿠폰 사용 가능
 *   - VIP Bronze (1~2회): SAJU5K 쿠폰 (신규 X) + 단골 메일 알림
 *   - VIP Silver (3~5회): VIP3X ₩3,000 쿠폰 자동 노출 + 신년운세 5% 추가 할인
 *   - VIP Gold (6+회): VIP3X + 우선 응답 + 매월 무료 일일 운세 카드 5장
 *
 * Response: { ok, email, paid_count, tier, total_spent, eligible_coupons, perks }
 */
const https = require('https');

function jsonReq(opts) {
  return new Promise((resolve) => {
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
    req.end();
  });
}

async function readGist(gistId, token, filename) {
  if (!token || !gistId) return null;
  const res = await jsonReq({
    hostname: 'api.github.com', port: 443,
    path: `/gists/${gistId}`, method: 'GET',
    headers: { Authorization: `Bearer ${token}`, 'User-Agent': 'cheonmyeongdang-vip' },
  });
  try {
    const file = res.body && res.body.files && res.body.files[filename];
    return file && file.content ? JSON.parse(file.content) : null;
  } catch (e) { return null; }
}

function determineTier(paid_count) {
  if (paid_count >= 6) return { name: 'VIP Gold', level: 3, color: '#e8c97a' };
  if (paid_count >= 3) return { name: 'VIP Silver', level: 2, color: '#c0c0c0' };
  if (paid_count >= 1) return { name: 'VIP Bronze', level: 1, color: '#cd7f32' };
  return { name: '일반', level: 0, color: '#9a9080' };
}

function determineEligibleCoupons(paid_count) {
  const coupons = [];
  // 모두 사용 가능
  coupons.push({ code: 'LAUNCH2026', label: '출시 기념 ₩1,000 할인', valid_until: '2026-06-30' });
  // 신규 가입자 (paid_count === 0)
  if (paid_count === 0) {
    coupons.push({ code: 'SAJU5K', label: '신규 ₩5,000 할인 (사주 정밀/종합 풀이)', valid_until: '2026-06-30' });
  }
  // VIP Silver 이상 (3회 이상)
  if (paid_count >= 3) {
    coupons.push({ code: 'VIP3X', label: 'VIP ₩3,000 할인 (모든 SKU)', valid_until: null });
  }
  return coupons;
}

function determinePerks(paid_count) {
  const perks = ['24시간 환불 보장', '광고 ZERO 결제 시 영구'];
  if (paid_count >= 1) perks.push('단골 고객 ₩2,000 쿠폰 (D+60 메일)');
  if (paid_count >= 3) perks.push('VIP Silver — ₩3,000 자동 할인 쿠폰');
  if (paid_count >= 6) perks.push('VIP Gold — 우선 응답 + 월 무료 일일 운세 카드 5장');
  return perks;
}

module.exports = async (req, res) => {
  try {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') return res.status(204).end();
    if (req.method !== 'GET') return res.status(405).json({ ok: false, error: 'method' });

    // Vercel: req.query is auto-parsed
    const email = String((req.query && req.query.email) || '').trim().toLowerCase();
    if (!email) return res.status(400).json({ ok: false, error: 'no_email' });

    const ghToken = process.env.GITHUB_TOKEN;
    const gistId = process.env.GIST_ID;

    let purchases = [];
    if (ghToken && gistId) {
      try {
        const data = await readGist(gistId, ghToken, 'purchases.json');
        if (data && Array.isArray(data.purchases)) {
          purchases = data.purchases.filter((p) => (p.customerEmail || '').toLowerCase() === email && p.status !== 'refunded');
        }
      } catch (gistErr) {
        // graceful fallback — Gist 못 읽으면 기본값 (paid_count=0)
      }
    }

    const paid_count = purchases.length;
    const total_spent = purchases.reduce((sum, p) => sum + (parseInt(p.amount || 0, 10) || 0), 0);
    const tier = determineTier(paid_count);
    const eligible_coupons = determineEligibleCoupons(paid_count);
    const perks = determinePerks(paid_count);

    return res.status(200).json({ ok: true, email, paid_count, total_spent, tier, eligible_coupons, perks });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'internal', message: String(e && e.message || e).slice(0, 200) });
  }
};

