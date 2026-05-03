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
    id: 'subscribe_basic_2900',
    name: '베이직 구독 (월)',
    amount: 2900,
    desc: '광고 제거 + 꿈해몽 무제한 + 매일 아침 8시 카톡 운세 + 일일사주 알림 프리미엄. 부담 없는 진입가.',
    type: 'subscription',
  },
  {
    id: 'subscribe_monthly_29900',
    name: '월회원권 (프리미엄)',
    amount: 29900,
    desc: '사주 정밀 + 궁합 무제한 + 매일 아침 8시 카톡 운세 + AI 챗봇 무제한 (종합/신년운세는 별도)',
    type: 'subscription',
  },
  {
    id: 'ai_chatbot_pack_4900',
    name: 'AI 사주 챗봇 30회',
    amount: 4900,
    desc: '천명당 사주 데이터 기반 AI 챗봇과 30회 자유 질의. "오늘 면접 가도 될까요" 등 즉답.',
    type: 'inapp',
  },
  {
    id: 'no_ads_9900',
    name: '광고 없음 (영구)',
    amount: 9900,
    desc: '천명당 모든 무료 콘텐츠에서 광고 영구 제거. 한 번 결제로 평생 사용.',
    type: 'inapp',
  },
  // ─── 5월 시즌: 종소세 환급 ─────────────────────────────────
  // 시즌 한정(2026-05-01~2026-06-01) 종합소득세 신고/환급 조력 SKU.
  // 세무사법 RISK 회피: "신고 대행" 표현 금지 → "체크리스트", "가이드", "AI 챗봇 자료" 톤만 사용.
  // 광고 카피 검수 키워드: "세무사 대체"/"100% 환급"/"절대" 0건.
  {
    id: 'jongsose_checklist_9900',
    name: '종소세 환급 체크리스트 + AI 챗봇 30회',
    amount: 9900,
    desc: '프리랜서·자영업자용 공제 체크리스트 PDF + AI 챗봇 30회 (소득공제·세액공제 자료 안내 한정). 신고 대행 X — 본인 직접 홈택스 입력 보조.',
    type: 'inapp',
  },
  {
    id: 'jongsose_premium_29900',
    name: '종소세 종합 가이드 + 월회원 (1개월)',
    amount: 29900,
    desc: '체크리스트 + 챗봇 무제한(1개월) + 천명당 사주 정밀(직업·재물운 풀이) 1회. 사업자/프리랜서 패키지.',
    type: 'inapp',
  },
  // ─── 5월 시즌: 어버이날 (5/8) ─────────────────────────────────
  // 시즌 한정(2026-05-01~2026-05-15) 부모님 효심 SKU.
  // 광고 카피 검수 키워드: "효도 강요"/"안 사면 불효"/"100%"/"유일" 0건.
  {
    id: 'eobonal_premium_29900',
    name: '어버이날 종합 패키지',
    amount: 29900,
    desc: '부모님 사주 정밀 + 부모-자녀 궁합 + 신년운세 + AI 챗봇 30회 + 카네이션 카드 PDF 5종 + 감사 편지 100선 e-book 묶음. 5월 한정.',
    type: 'inapp',
  },
  // ─── 5월 가정의달 PDF 이북 4종 ─────────────────────────────────
  // KDP 동시 발간 + 천명당 도메인 직접 다운로드. type:'ebook' → success.html에서 다운로드 섹션 분기.
  // pdfPath는 /pdfs/{slug}.pdf — Vercel 정적 호스팅. 결제 후 success.html이 SKU 보고 다운로드 링크 생성.
  // 광고 카피 검수: "100% 환급"/"세무사 대체"/특정 업체·연예인·IP 거론 0건.
  {
    id: 'ebook_eobo_letter_6900',
    name: '어버이날 감사 편지 100선',
    amount: 6900,
    desc: '부모님께 드릴 손편지 100가지 — 막막한 한 줄을 채워드리는 템플릿집 (PDF 79p).',
    type: 'ebook',
    pdfPath: '/pdfs/eobo_letter.pdf',
    pages: 79,
    season: '5/8',
  },
  {
    id: 'ebook_eorin_mission_9900',
    name: '어린이날 가족 미션북',
    amount: 9900,
    desc: '5월 5일, 부모와 아이가 함께 푸는 30일 미션북 (PDF 56p).',
    type: 'ebook',
    pdfPath: '/pdfs/eorin_mission.pdf',
    pages: 56,
    season: '5/5',
  },
  {
    id: 'ebook_family_diary_7900',
    name: '5월 가정의달 다이어리',
    amount: 7900,
    desc: '어버이날·어린이날·가족모임 — 5월 한 달 가족 일정 정리 다이어리 (PDF 39p).',
    type: 'ebook',
    pdfPath: '/pdfs/family_diary.pdf',
    pages: 39,
    season: '5/1~31',
  },
  {
    id: 'ebook_jongsose_guide_12900',
    name: '종소세 셀프 신고 가이드',
    amount: 12900,
    desc: '프리랜서·N잡러 5월 31일 마감 종소세 단계별 가이드 (PDF 28p). 신고 대행 X — 본인 직접 홈택스 입력 보조.',
    type: 'ebook',
    pdfPath: '/pdfs/jongsose_guide.pdf',
    pages: 28,
    season: '5/1~31',
  },
  // ─── K-Saju AI 영문판 (글로벌, USD 표기지만 KRW 환산 결제) ───
  {
    id: 'saju_single_en_999',
    name: 'K-Saju AI — Single Reading (English)',
    amount: 13800, // ~$10 USD @ KRW_PER_USD 1380
    desc: 'Korean four-pillar astrology personalized reading in English. Email delivery within 24 hours. Cultural/entertainment content.',
    type: 'global',
    lang: 'en',
  },
  {
    id: 'saju_premium_en_1900',
    name: 'K-Saju AI — Premium Monthly (English)',
    amount: 26220, // ~$19 USD @ 1380
    desc: 'Unlimited Korean Saju readings + monthly forecasts in English. Cancel anytime. Cultural/entertainment content.',
    type: 'global_subscription',
    lang: 'en',
  },
  // ─── 5/3 자동 생성 디지털 상품 5종 (PDF) — Sprint #1 + #2 ─────────
  // ReportLab 자동 생성. /pdfs/ 정적 호스팅. type:'ebook' → success.html 다운로드 분기.
  // Gumroad cross-listing 자동 (gumroad_api_auto_list.py).
  {
    id: 'ebook_saju_birth_en_9900',
    name: 'Korean Saju Birth Chart Reading (English)',
    amount: 9900,
    desc: 'Korean four-pillar astrology personalized analysis framework in English. 10 stems + 12 branches + 5 elements + career/relationship compatibility. Cultural/entertainment content.',
    type: 'ebook',
    pdfPath: '/pdfs/saju_birth_chart_en.pdf',
    pages: 7,
    lang: 'en',
  },
  {
    id: 'ebook_kwisdom_wallart_12900',
    name: 'Korean Wisdom Wall Art Bundle (12 posters)',
    amount: 12900,
    desc: '12 Korean proverb posters with English translations, A4/Letter printable. Print at home or local shop. Korean tradition wisdom decoded.',
    type: 'ebook',
    pdfPath: '/pdfs/kwisdom_wall_art.pdf',
    pages: 13,
    lang: 'en',
  },
  {
    id: 'ebook_kwisdom_planner_14900',
    name: 'K-Wisdom Daily Planner 2026 (Undated 365-day)',
    amount: 14900,
    desc: 'Korean longevity rituals + Saju daily mood + monthly Korean cultural calendar + weekly reflection (Joseon scholar style). Print and start any month.',
    type: 'ebook',
    pdfPath: '/pdfs/kwisdom_daily_planner_2026.pdf',
    pages: 30,
    lang: 'en',
  },
  {
    id: 'ebook_korean_tax_en_9900',
    name: 'Korean Tax Smart Guide for Foreigners 2026',
    amount: 9900,
    desc: '2026 Korean tax filing guide for foreign residents. Income brackets, foreign engineer deductions, treaty benefits, hometax step-by-step. Information only — not tax representation.',
    type: 'ebook',
    pdfPath: '/pdfs/korean_tax_foreigners.pdf',
    pages: 10,
    lang: 'en',
  },
  {
    id: 'ebook_korean_recipe_7900',
    name: 'Korean Recipe Meal Planner (30 dishes)',
    amount: 7900,
    desc: '30 traditional Korean recipes with English ingredients + weekly meal planner template + banchan diversity tracker. Korean longevity meal philosophy.',
    type: 'ebook',
    pdfPath: '/pdfs/korean_recipe_planner.pdf',
    pages: 4,
    lang: 'en',
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

  // PayPal (글로벌 결제) — PG 라이브키 통과 전 즉시 활성화 가능 채널
  // PAYPAL_CLIENT_ID 환경변수 등록 시 pay.html에 PayPal Smart Buttons 자동 노출
  const paypalClientId = (process.env.PAYPAL_CLIENT_ID || '').trim();
  const paypalEnv = (process.env.PAYPAL_ENV || 'sandbox').trim(); // sandbox or production
  const paypalEnabled = paypalClientId !== '';

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
    // PayPal (글로벌)
    paypalClientId,
    paypalEnv,
    paypalEnabled,
  });
};

// 다른 API에서 SKU 가격 검증 시 import 가능
module.exports.SKU_CATALOG = SKU_CATALOG;
module.exports.lookupSku = function (id) {
  return SKU_CATALOG.find((s) => s.id === id) || null;
};
