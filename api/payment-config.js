/**
 * 천명당 토스페이먼츠 클라이언트 설정 노출 API
 * GET /api/payment-config
 *
 * 클라이언트 키는 frontend 노출 OK (토스 정책)
 * 시크릿 키는 노출 금지 — 절대 반환하지 않음
 *
 * 응답: { clientKey, env, skus: [{ id, name, amount }, ...] }
 */

// 천명당 SKU 카탈로그 — 가격 정책 확정 (2026-04-30 웹 기준 통일)
// 무료 4종(오늘운세/관상/손금/꿈해몽)은 결제 불필요 → 결제 페이지에 노출 X
//
// 가격 정책 출처: departments/cheonmyeongdang/sku_pricing.md
// CEO 지시 (2026-04-30): 웹 가격 ₩29,900을 정식 가격으로 채택 → 앱 Play Console도 ₩29,900으로 인상 필요
const SKU_CATALOG = [
  {
    id: 'saju_premium_9900',
    name: '사주 정밀 풀이',
    amount: 9900,
    desc: '명리학 기반 정밀 사주 분석 리포트',
    type: 'inapp',
  },
  {
    id: 'compat_detail_9900',
    name: '궁합',
    amount: 9900,
    desc: '두 사주의 합/충/오행 균형 정밀 분석',
    type: 'inapp',
  },
  {
    id: 'comprehensive_29900',
    name: '종합 풀이',
    amount: 29900,
    desc: '사주+궁합+신년운세 통합 심층 리포트 (개별 합산 대비 절약 + 12개월 운세)',
    type: 'inapp',
  },
  {
    id: 'sinnyeon_15000',
    name: '신년운세 (연간)',
    amount: 15000,
    desc: '12개월 월별 운세 + 신살 연간 리포트',
    type: 'inapp',
  },
  {
    id: 'subscribe_monthly_29900',
    name: '월회원권',
    amount: 29900,
    desc: '사주 정밀 + 궁합 무제한 + 매일 아침 8시 카톡 운세 (종합/신년운세는 별도)',
    type: 'subscription',
  },
  {
    id: 'no_ads_9900',
    name: '광고 없음 (영구)',
    amount: 9900,
    desc: '천명당 모든 무료 콘텐츠에서 광고 영구 제거. 한 번 결제로 평생 사용.',
    type: 'inapp',
  },
];

module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

  const clientKey = (process.env.TOSS_CLIENT_KEY || '').trim();
  if (!clientKey) {
    return res.status(500).json({ error: 'Server not configured: TOSS_CLIENT_KEY missing' });
  }

  const env = clientKey.startsWith('live_') ? 'live' : 'test';

  // ─── PG 라우팅 환경변수 ──────────────────────────────────────────
  // CMD_PAYMENT_PROVIDER: 기본 PG. 'toss' | 'portone-kcn' | 'portone-kakaopay' | 'billgate'
  //   미설정 시 'toss' (현재 라이브). 토스 라이브 키 발급 후에도 'toss' 유지 가능.
  //
  // PORTONE_STORE_ID:        포트원 콘솔 → 결제연동 → 상점 ID (store-XXXX)
  // PORTONE_CHANNEL_KEY:     기본 채널 키 (어떤 PG든 단일이면 여기에)
  // PORTONE_CHANNEL_KEY_KCN:      한국결제네트웍스 채널 키
  // PORTONE_CHANNEL_KEY_KAKAOPAY: 카카오페이 채널 키
  //
  // PG 통과 시 vercel env에 4줄(STORE_ID + 3 channel key) 등록만 하면 즉시 가동.
  const provider = (process.env.CMD_PAYMENT_PROVIDER || 'toss').trim();
  const portoneStoreId = (process.env.PORTONE_STORE_ID || 'store-XXXX').trim();
  const portoneChannelKey = (process.env.PORTONE_CHANNEL_KEY || 'channel-key-XXXX').trim();
  const portoneChannelKeys = {
    'portone-kcn': (process.env.PORTONE_CHANNEL_KEY_KCN || portoneChannelKey).trim(),
    'portone-kakaopay': (process.env.PORTONE_CHANNEL_KEY_KAKAOPAY || portoneChannelKey).trim(),
  };

  // SKU별 provider 강제 (예: 월구독은 카카오페이, 단건은 KCN — 환경변수 JSON)
  // CMD_SKU_PROVIDER_OVERRIDE='{"subscribe_monthly_29900":"portone-kakaopay"}'
  let skuProviderOverride = {};
  try {
    if (process.env.CMD_SKU_PROVIDER_OVERRIDE) {
      skuProviderOverride = JSON.parse(process.env.CMD_SKU_PROVIDER_OVERRIDE);
    }
  } catch (e) {
    skuProviderOverride = {};
  }

  return res.status(200).json({
    // 토스 (기존 흐름 유지)
    clientKey,
    env,
    // 공통
    provider,
    skus: SKU_CATALOG,
    // 포트원 V2 (PG 키 미발급 시 placeholder 'store-XXXX' 노출 — pay.html 분기 시 사용 안 함)
    portoneStoreId,
    portoneChannelKey,
    portoneChannelKeys,
    skuProviderOverride,
  });
};

// 다른 API에서 SKU 가격 검증 시 import 가능
module.exports.SKU_CATALOG = SKU_CATALOG;
module.exports.lookupSku = function (id) {
  return SKU_CATALOG.find((s) => s.id === id) || null;
};
