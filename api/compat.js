/**
 * 천명당 궁합(宮合) 분석 API — SKU compat_detail_9900
 * POST /api/compat
 *
 * Body:
 *   {
 *     personA: { year, month, day, hour, gender },
 *     personB: { year, month, day, hour, gender },
 *     // entitlement 검증 옵션 (둘 중 하나):
 *     email: "user@example.com",     // 결제 영수증 ledger(_purchase-store)에서 조회
 *     orderId: "cmd_xxx_yyy",         // 동일 ledger에서 orderId로 직접 조회
 *     // skip 검증 (preview/테스트용 — production에서는 false)
 *     preview: true                   // true면 점수만 반환, 상세 분석은 잠금
 *   }
 *
 * 응답:
 *   200 { ok: true, paid: true, result: {...analyzeCompat 결과...} }
 *   200 { ok: true, paid: false, preview: { overall: 78, headline: "..." } } — preview 모드
 *   402 { ok: false, error: "결제 정보가 없습니다", needsPayment: true, sku: "compat_detail_9900" }
 *   400 { ok: false, error: "..." }
 *
 * 보안:
 *   - SKU 검증: lookupSku('compat_detail_9900') 존재 + email/orderId 매핑 확인
 *   - PII는 응답에 포함하지 않음 (날짜·성별만 echo)
 *   - CORS open (*)
 */
const { lookupSku } = require('./payment-config');
const { listPurchasesByEmail } = require('./_purchase-store');
const { analyzeCompat } = require('./_compat-engine');

// ─── SKU ID (payment-config.js와 동기화) ──────────────────
const COMPAT_SKU = 'compat_detail_9900';
// 월회원권 (잠금 해제 OR 조건)
const MONTHLY_SKUS = ['monthly_premium', 'subscribe_monthly_9900', 'subscribe_monthly_29900'];
// 종합 풀이 (compat 포함)
const COMPREHENSIVE_SKUS = ['comprehensive_15000', 'comprehensive_29900', 'comprehensive_reading'];
// 궁합 단건 SKU 변형 모두 인정
const COMPAT_SKUS = [COMPAT_SKU, 'gunghap'];

function validatePerson(p, label) {
  if (!p) return label + ' 정보가 누락됐습니다';
  var y = Number(p.year), m = Number(p.month), d = Number(p.day);
  if (!y || y < 1920 || y > 2050) return label + '의 출생년도가 유효하지 않습니다 (1920~2050)';
  if (!m || m < 1 || m > 12) return label + '의 월이 유효하지 않습니다 (1~12)';
  if (!d || d < 1 || d > 31) return label + '의 일자가 유효하지 않습니다 (1~31)';
  if (p.hour != null) {
    var h = Number(p.hour);
    if (!isNaN(h) && (h < -1 || h > 23)) return label + '의 시간이 유효하지 않습니다 (0~23, 모르면 -1)';
  }
  return null;
}

function normalizePerson(p) {
  return {
    year: Number(p.year),
    month: Number(p.month),
    day: Number(p.day),
    hour: p.hour == null ? -1 : Number(p.hour),
    gender: (p.gender === 'F' || p.gender === 'M') ? p.gender : 'M',
  };
}

async function checkEntitlement(email, orderId) {
  // entitlement 매트릭스: 궁합 단건 OR 월회원 OR 종합 풀이 (모두 인정)
  if (!email && !orderId) {
    return { paid: false, reason: 'email 또는 orderId가 필요합니다' };
  }

  // GitHub Gist에서 결제 ledger 조회
  if (email) {
    try {
      var result = await listPurchasesByEmail(email);
      if (result.ok) {
        var skuList = (result.records || []).map(function (r) { return r.skuId; }).filter(Boolean);
        // 궁합 / 월회원 / 종합 풀이 중 하나라도 있으면 OK
        var unlocked =
          skuList.some(function (s) { return COMPAT_SKUS.indexOf(s) !== -1; }) ||
          skuList.some(function (s) { return MONTHLY_SKUS.indexOf(s) !== -1; }) ||
          skuList.some(function (s) { return COMPREHENSIVE_SKUS.indexOf(s) !== -1; });
        if (unlocked) {
          return { paid: true, source: 'email_ledger', skus: skuList };
        }
      }
    } catch (e) {
      // ledger 조회 실패해도 orderId fallback 시도
      console.warn('[compat] listPurchasesByEmail 실패:', e.message);
    }
  }

  // orderId 검증 (현재는 prefix CMD/cmd로 형식만 — 실 운영에선 ledger orderId 매칭 필요)
  if (orderId && /^(cmd|CMD)[-_].+/.test(orderId)) {
    // ledger에서 orderId 직접 조회는 추후 listPurchasesByOrderId 추가 시 강화 (현재는 형식만)
    // 본 API는 confirm-payment로 영수증 검증된 orderId만 인정 — preview 모드 권장
    return { paid: false, reason: 'orderId만으로는 검증 불가 — email 함께 전송하세요' };
  }

  return { paid: false, reason: '결제 이력을 찾을 수 없습니다' };
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });

  // body 파싱
  var body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  // 입력 검증
  var errA = validatePerson(body.personA, '본인');
  if (errA) return res.status(400).json({ ok: false, error: errA });
  var errB = validatePerson(body.personB, '상대방');
  if (errB) return res.status(400).json({ ok: false, error: errB });

  var personA = normalizePerson(body.personA);
  var personB = normalizePerson(body.personB);

  // SKU 카탈로그 sanity check (가격/이름 변경 시 알림)
  var sku = lookupSku(COMPAT_SKU);
  if (!sku) {
    return res.status(500).json({ ok: false, error: 'SKU 카탈로그 손상: ' + COMPAT_SKU });
  }

  // 분석 실행 (preview/paid 둘 다 동일하게 계산해야 응답 일관성 보장)
  var compatResult;
  try {
    compatResult = analyzeCompat(personA, personB);
  } catch (e) {
    return res.status(500).json({ ok: false, error: '분석 실패: ' + e.message });
  }

  // ─── preview 모드: 점수 + 헤드라인만 ────────────────────
  if (body.preview === true) {
    return res.status(200).json({
      ok: true,
      paid: false,
      preview: {
        scores: compatResult.scores,
        headline: compatResult.summary.headline,
        ilganHint: {
          A: compatResult.personA.ilgan,
          B: compatResult.personB.ilgan,
        },
      },
      sku: { id: sku.id, name: sku.name, amount: sku.amount },
      payUrl: '/pay.html?sku=' + sku.id,
    });
  }

  // ─── 결제 검증 ──────────────────────────────────────────
  var email = (body.email || '').toString().trim().toLowerCase();
  var orderId = (body.orderId || '').toString().trim();
  var entitled = await checkEntitlement(email, orderId);

  if (!entitled.paid) {
    return res.status(402).json({
      ok: false,
      error: entitled.reason || '궁합 상세 분석은 결제 후 이용 가능합니다',
      needsPayment: true,
      sku: { id: sku.id, name: sku.name, amount: sku.amount },
      payUrl: '/pay.html?sku=' + sku.id,
      preview: {
        scores: compatResult.scores,
        headline: compatResult.summary.headline,
      },
    });
  }

  // ─── 결제 완료 → 풀 결과 반환 ──────────────────────────
  return res.status(200).json({
    ok: true,
    paid: true,
    source: entitled.source,
    sku: { id: sku.id, name: sku.name },
    result: compatResult,
  });
};

// ─── 외부 require용 (테스트/cron) ──────────────────────
module.exports.analyzeCompat = analyzeCompat;
module.exports.checkEntitlement = checkEntitlement;
