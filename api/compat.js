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
const https = require('https');
const { lookupSku } = require('./payment-config');
const { listPurchasesByEmail } = require('../lib/purchase-store');
const { analyzeCompat } = require('../lib/compat-engine');
const SajuEngine = require('../js/saju-engine.js');

// ────────────────────────────────────────────────────────────
// RapidAPI Saju Reading 모드 (액션 라우팅: ?action=rapidapi-saju)
// rewrite 매핑: /api/saju-rapid → /api/compat?action=rapidapi-saju
// 입력: { birth_year, birth_month, birth_day, birth_hour, gender }
// 응답: { pillars, elements, summary, lucky_color, lucky_direction, advice }
// 인증: X-RapidAPI-Proxy-Secret 헤더 검증 (RapidAPI 표준)
// ────────────────────────────────────────────────────────────

// 오행 → lucky color/direction 매핑
const ELEMENT_TO_COLOR = {
  '목': 'green', '화': 'red', '토': 'yellow',
  '금': 'white', '수': 'black/blue',
};
const ELEMENT_TO_DIRECTION = {
  '목': 'East', '화': 'South', '토': 'Center',
  '금': 'West', '수': 'North',
};

// Claude API 호출 (선택적 — ANTHROPIC_API_KEY 있을 때만)
function callClaude(apiKey, prompt) {
  return new Promise(function (resolve) {
    var data = JSON.stringify({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 1500,
      messages: [{ role: 'user', content: prompt }],
    });
    var req = https.request({
      hostname: 'api.anthropic.com',
      port: 443,
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    }, function (resp) {
      var buf = '';
      resp.on('data', function (c) { buf += c; });
      resp.on('end', function () {
        try {
          var j = JSON.parse(buf);
          if (j && j.content && j.content[0] && j.content[0].text) {
            resolve(j.content[0].text);
          } else {
            resolve(null);
          }
        } catch (e) { resolve(null); }
      });
    });
    req.on('error', function () { resolve(null); });
    // 2.5s timeout — RapidAPI 3s SLA 보장
    req.setTimeout(2500, function () { req.destroy(); resolve(null); });
    req.write(data);
    req.end();
  });
}

// fallback 어드바이스 (Claude 미응답 시) — Korean culture 일반화 (특정 인물/IP 추측 X)
function buildFallbackAdvice(dayElementKr, dominantElementKr) {
  var bridge = {
    '목': 'embrace growth, study, and consistent learning',
    '화': 'channel passion, leadership, and visible action',
    '토': 'cultivate stability, trust, and long-term planning',
    '금': 'pursue precision, discipline, and clear boundaries',
    '수': 'value adaptability, intuition, and quiet observation',
  };
  return 'Your day stem element is ' + dayElementKr + ' and your chart leans toward ' + dominantElementKr + '. To align with your natural flow, ' + (bridge[dayElementKr] || 'follow balanced action') + '. Pay extra attention to relationships that mirror complementary elements rather than opposing ones.';
}

async function handleRapidApiSaju(req, res) {
  // 1) RapidAPI proxy secret 검증
  var expectedSecret = process.env.RAPIDAPI_PROXY_SECRET || '';
  var incomingSecret = req.headers['x-rapidapi-proxy-secret'] || '';
  if (expectedSecret && incomingSecret !== expectedSecret) {
    return res.status(401).json({
      ok: false,
      error: 'Unauthorized — this endpoint is served via RapidAPI only. Subscribe at rapidapi.com',
    });
  }

  // 2) body 파싱
  var body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  var year = Number(body.birth_year);
  var month = Number(body.birth_month);
  var day = Number(body.birth_day);
  var hour = body.birth_hour == null ? -1 : Number(body.birth_hour);
  var gender = (body.gender === 'F' || body.gender === 'M') ? body.gender : 'M';

  if (!year || year < 1920 || year > 2050) {
    return res.status(400).json({ ok: false, error: 'birth_year must be 1920-2050' });
  }
  if (!month || month < 1 || month > 12) {
    return res.status(400).json({ ok: false, error: 'birth_month must be 1-12' });
  }
  if (!day || day < 1 || day > 31) {
    return res.status(400).json({ ok: false, error: 'birth_day must be 1-31' });
  }
  if (hour !== -1 && (hour < 0 || hour > 23)) {
    return res.status(400).json({ ok: false, error: 'birth_hour must be 0-23 or omitted' });
  }

  // 3) 사주 분석 (saju-engine.js)
  var sajuRaw;
  try {
    sajuRaw = SajuEngine.analyzeSaju(year, month, day, hour, gender);
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'Saju calculation failed: ' + e.message });
  }

  // 4) 영문 응답 빌드
  var pillars = [];
  ['년주', '월주', '일주', '시주'].forEach(function (k) {
    var p = sajuRaw[k] || (sajuRaw.사주 && sajuRaw.사주[k]);
    if (!p && sajuRaw.사주) p = sajuRaw.사주[k];
    if (!p) return;
    var stemKr = (SajuEngine.constants.천간 || [])[p.stem] || '';
    var stemHj = (SajuEngine.constants.천간_한자 || [])[p.stem] || '';
    var branchKr = (SajuEngine.constants.지지 || [])[p.branch] || '';
    var branchHj = (SajuEngine.constants.지지_한자 || [])[p.branch] || '';
    var pillarLabel = { '년주': 'year', '월주': 'month', '일주': 'day', '시주': 'hour' }[k];
    pillars.push({
      pillar: pillarLabel,
      stem_kr: stemKr,
      stem_hanja: stemHj,
      branch_kr: branchKr,
      branch_hanja: branchHj,
    });
  });

  // 오행 카운트 추출 (사주 객체 또는 elements 키)
  var elementCount = sajuRaw.오행 || sajuRaw.elements || {};
  var elements = ['목', '화', '토', '금', '수'].map(function (el) {
    return {
      element_kr: el,
      element_en: { '목': 'Wood', '화': 'Fire', '토': 'Earth', '금': 'Metal', '수': 'Water' }[el],
      count: Number(elementCount[el] || 0),
    };
  });

  // dominant element + day stem element
  var sortedEl = elements.slice().sort(function (a, b) { return b.count - a.count; });
  var dominantElementKr = sortedEl[0].element_kr;
  var dayPillar = sajuRaw.사주 && sajuRaw.사주['일주'];
  var dayStemIdx = dayPillar ? dayPillar.stem : 0;
  var STEM_ELEMENT = ['목', '목', '화', '화', '토', '토', '금', '금', '수', '수'];
  var dayElementKr = STEM_ELEMENT[dayStemIdx] || '목';

  var luckyColor = ELEMENT_TO_COLOR[dayElementKr] || 'green';
  var luckyDirection = ELEMENT_TO_DIRECTION[dayElementKr] || 'East';

  // summary 헤드라인 (간단 포맷)
  var summary = 'Day stem ' + (SajuEngine.constants.천간_한자 || [])[dayStemIdx] +
    ' (' + dayElementKr + '/' + ({ '목': 'Wood', '화': 'Fire', '토': 'Earth', '금': 'Metal', '수': 'Water' }[dayElementKr]) + '). ' +
    'Dominant element: ' + dominantElementKr + ' (' + ({ '목': 'Wood', '화': 'Fire', '토': 'Earth', '금': 'Metal', '수': 'Water' }[dominantElementKr]) + ').';

  // 5) Claude AI insight (선택) — 환경변수 있을 때만, fallback 보장
  var advice = buildFallbackAdvice(dayElementKr, dominantElementKr);
  var anthropicKey = process.env.ANTHROPIC_API_KEY || '';
  if (anthropicKey) {
    var prompt = 'You are a Korean Saju (Bazi/Four Pillars) expert. Given a day stem element of ' + dayElementKr +
      ' (' + ({ '목': 'Wood', '화': 'Fire', '토': 'Earth', '금': 'Metal', '수': 'Water' }[dayElementKr]) + ') ' +
      'and a dominant chart element of ' + dominantElementKr + ', write a concise 3-sentence English advice ' +
      'in second person ("you") covering: (1) personality strength, (2) 2026 year theme, (3) one practical action. ' +
      'Use Korean culture references in general terms only. No proper names. Output plain text, no markdown.';
    try {
      var aiText = await callClaude(anthropicKey, prompt);
      if (aiText && typeof aiText === 'string' && aiText.length > 30) {
        advice = aiText.trim();
      }
    } catch (e) { /* fallback advice 사용 */ }
  }

  return res.status(200).json({
    ok: true,
    pillars: pillars,
    elements: elements,
    summary: summary,
    lucky_color: luckyColor,
    lucky_direction: luckyDirection,
    advice: advice,
    meta: {
      day_stem_element: dayElementKr,
      dominant_element: dominantElementKr,
      gender: gender,
      birth: { year: year, month: month, day: day, hour: hour === -1 ? null : hour },
    },
  });
}

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
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-RapidAPI-Proxy-Secret, X-RapidAPI-Key, X-RapidAPI-Host');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });

  // ─── RapidAPI Saju Reading 액션 라우팅 ───
  // /api/saju-rapid → /api/compat?action=rapidapi-saju (vercel.json rewrite)
  var action = (req.query && req.query.action) || '';
  if (action === 'rapidapi-saju') {
    return handleRapidApiSaju(req, res);
  }

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
