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
const { listPurchasesByEmail } = require('../lib/purchase-store');

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
  const skuSet = [...new Set(records.map(r => r.skuId).filter(Boolean))];
  const latest = records
    .map(r => r.paid_at)
    .filter(Boolean)
    .sort()
    .pop();

  return res.status(200).json({
    ok: true,
    skus: skuSet,
    count: records.length,
    latest_paid_at: latest || null,
    // 토큰: 클라이언트가 localStorage에 저장 (위변조 방지보다는 entitlement 인식용)
    token: skuSet.length > 0 ? Buffer.from(`${email}|${latest || ''}|${skuSet.join(',')}`).toString('base64') : null,
  });
};
