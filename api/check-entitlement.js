/**
 * 천명당 entitlement 조회 API — 결제 이메일 기반
 *
 * POST /api/check-entitlement
 * body (default mode): { email: "user@example.com" }
 *   → 응답: { ok: true, skus: [...], ... }
 *
 * body (mode='ask_saju'): { mode: 'ask_saju', email, question, saju_data, free_used? }
 *   → entitlement 보유자 또는 무료 시범 1회 사용자에게 Claude API 답변 반환
 *   → 응답: { ok: true, mode: 'ask_saju', answer: "...", remaining_free: 0|1 }
 *           { ok: false, mode: 'ask_saju', reason: 'locked'|'rate_limit'|'api_error' }
 *
 * 클라이언트는 응답의 skus를 localStorage에 저장 후 광고 차단 등에 사용.
 * 비밀번호 0, 회원가입 0, 마찰 최소화.
 */
const https = require('https');
const crypto = require('crypto');
const { listPurchasesByEmail } = require('../lib/purchase-store');

// ─── AI Q&A: 일일 사용량 throttle (in-memory 단순 가드, 서버리스 cold start 시 리셋) ───
const _aiUsageMap = new Map(); // email → { day: 'YYYY-MM-DD', count: N }
const AI_DAILY_LIMIT = 100;

function _aiUsageDayKey() {
  const d = new Date();
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth()+1).padStart(2,'0')}-${String(d.getUTCDate()).padStart(2,'0')}`;
}

function _aiCheckAndIncrement(email) {
  const key = String(email || '').toLowerCase();
  const today = _aiUsageDayKey();
  const cur = _aiUsageMap.get(key);
  if (!cur || cur.day !== today) {
    _aiUsageMap.set(key, { day: today, count: 1 });
    return { ok: true, count: 1 };
  }
  if (cur.count >= AI_DAILY_LIMIT) {
    return { ok: false, count: cur.count };
  }
  cur.count += 1;
  _aiUsageMap.set(key, cur);
  return { ok: true, count: cur.count };
}

// Claude API 호출 (Anthropic Messages API)
function _callClaudeApi({ apiKey, question, sajuData }) {
  return new Promise((resolve, reject) => {
    // 사주 데이터 요약 — 서버에서 안전하게 추출 (클라가 임의 raw 전달해도 길이 캡)
    let sajuSummary = '';
    try {
      if (sajuData && typeof sajuData === 'object') {
        const s = sajuData;
        const parts = [];
        if (s.summary) parts.push(`사주 8자: ${String(s.summary).slice(0, 30)}`);
        if (s.day_stem) parts.push(`일간: ${String(s.day_stem).slice(0, 8)}`);
        if (s.element) parts.push(`일간오행: ${String(s.element).slice(0, 4)}`);
        if (s.yongshin) parts.push(`용신: ${String(s.yongshin).slice(0, 4)}`);
        if (s.gangyak) parts.push(`강약: ${String(s.gangyak).slice(0, 8)}`);
        if (s.daeun) parts.push(`현재대운: ${String(s.daeun).slice(0, 30)}`);
        if (s.gender) parts.push(`성별: ${String(s.gender).slice(0, 4)}`);
        if (Array.isArray(s.sipsin)) parts.push(`십신: ${s.sipsin.slice(0,8).map(x=>String(x).slice(0,8)).join(',')}`);
        sajuSummary = parts.join(' | ').slice(0, 500);
      }
    } catch (e) { sajuSummary = ''; }

    const systemPrompt = '당신은 정통 한국 사주명리학 전문가입니다. 사용자의 사주 데이터(8글자, 십신, 대운, 용신)를 바탕으로 자연어 질문에 답변하세요. 답변 길이: 200~400자. 명리학 용어를 일상어와 함께 사용하세요. 단정적 예언 대신 "~경향이 있습니다", "~시기가 유리합니다" 같은 권유형 어조. 의료/법률/투자 결정은 전문가 상담을 안내하세요.';

    const userMsg = `[내 사주 데이터]\n${sajuSummary || '(사주 분석 결과 일부)'}\n\n[질문]\n${String(question || '').slice(0, 500)}`;

    const body = JSON.stringify({
      model: 'claude-haiku-4-5',
      max_tokens: 500,
      system: systemPrompt,
      messages: [{ role: 'user', content: userMsg }],
    });

    const req = https.request({
      hostname: 'api.anthropic.com', port: 443,
      path: '/v1/messages', method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      timeout: 9000,
    }, (r) => {
      let buf = '';
      r.on('data', (c) => (buf += c));
      r.on('end', () => {
        try {
          const j = JSON.parse(buf);
          if (r.statusCode >= 400) {
            return reject(new Error(`Claude API ${r.statusCode}: ${(j && j.error && j.error.message) || buf.slice(0,200)}`));
          }
          const text = (j && Array.isArray(j.content) && j.content[0] && j.content[0].text) || '';
          resolve(text.trim() || '답변 생성에 실패했습니다.');
        } catch (e) { reject(new Error('Claude 응답 파싱 실패')); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(new Error('Claude API timeout')); });
    req.write(body);
    req.end();
  });
}

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
  let body = {};
  try {
    body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    email = String(body.email || '').trim();
  } catch (e) {
    return res.status(400).json({ ok: false, skus: [], reason: 'Invalid JSON body' });
  }

  const mode = String(body.mode || '').trim();

  // ─── mode='ask_saju': AI 사주 Q&A (Claude Haiku) ───
  if (mode === 'ask_saju') {
    const question = String(body.question || '').trim();
    const sajuData = body.saju_data || null;
    const freeUsed = body.free_used === true || body.free_used === 1 || body.free_used === '1';

    if (!question) {
      return res.status(400).json({ ok: false, mode: 'ask_saju', reason: '질문을 입력해 주세요' });
    }
    if (question.length > 500) {
      return res.status(400).json({ ok: false, mode: 'ask_saju', reason: '질문이 너무 깁니다 (500자 제한)' });
    }

    const apiKey = (process.env.ANTHROPIC_API_KEY || '').trim();
    if (!apiKey) {
      return res.status(500).json({
        ok: false, mode: 'ask_saju', reason: 'AI 서비스 준비 중입니다 (관리자 설정 필요)',
      });
    }

    // entitlement 검증 — 보유자는 무제한, 미보유자는 무료 시범 1회만
    let isPremium = false;
    if (email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      try {
        const result = await listPurchasesByEmail(email);
        if (result && result.ok) {
          const skuSet = new Set((result.records || []).map(r => r.skuId).filter(Boolean));
          const influCoupons = await listInfluencerCouponsByEmail(email);
          if (influCoupons.length > 0) {
            ['saju_premium_9900', 'comprehensive_29900', 'subscribe_monthly_29900'].forEach(s => skuSet.add(s));
          }
          isPremium = skuSet.has('saju_premium_9900') ||
                      skuSet.has('comprehensive_29900') ||
                      skuSet.has('subscribe_monthly_29900');
        }
      } catch (e) { isPremium = false; }
    }

    if (!isPremium && freeUsed) {
      return res.status(402).json({
        ok: false, mode: 'ask_saju', reason: 'locked',
        message: '무료 시범 1회를 사용했습니다. ₩29,900 결제 시 24시간 무제한 Q&A',
      });
    }

    // Throttle: 일일 100회 제한 (이메일 또는 IP fallback)
    const throttleKey = email || (req.headers['x-forwarded-for'] || req.headers['x-real-ip'] || 'anon').split(',')[0].trim();
    const usage = _aiCheckAndIncrement(throttleKey);
    if (!usage.ok) {
      return res.status(429).json({
        ok: false, mode: 'ask_saju', reason: 'rate_limit',
        message: '일일 사용량(100회)을 초과했습니다. 내일 다시 시도해 주세요.',
      });
    }

    // Claude API 호출
    try {
      const answer = await _callClaudeApi({ apiKey, question, sajuData });
      return res.status(200).json({
        ok: true, mode: 'ask_saju',
        answer,
        is_premium: isPremium,
        remaining_free: isPremium ? null : 0, // 시범 사용 직후 0
        daily_used: usage.count,
        daily_limit: AI_DAILY_LIMIT,
      });
    } catch (e) {
      return res.status(502).json({
        ok: false, mode: 'ask_saju', reason: 'api_error',
        message: 'AI 답변 생성에 실패했습니다. 잠시 후 다시 시도해 주세요.',
        detail: String(e.message || e).slice(0, 200),
      });
    }
  }

  // ─── default mode: entitlement 조회 ───
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
