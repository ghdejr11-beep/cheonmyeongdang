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
    id: 'subscribe_annual_249000',
    name: '연간회원권 (1회 결제, 30% 할인)',
    amount: 249000,
    desc: '월회원권을 1년치 한 번에 결제 — 매월 ₩29,900 × 12 = ₩358,800 → ₩249,000 (30% 절약). 구독 갱신 X, 1년 후 자동 만료. "구독 fatigue" 없는 1회 결제.',
    type: 'inapp',
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
  // ─── 5/3 추가 디지털 상품 5종 (catalog 22 → 27) ─────────────────
  {
    id: 'ebook_kbeauty_skincare_7900',
    name: 'K-Beauty 10-Step Skincare Guide',
    amount: 7900,
    desc: 'Korean 10-step skincare routine decoded by skin type. From oil cleanser to SPF, brand recommendations + customization for oily/dry/sensitive/combination/pigmented skin.',
    type: 'ebook',
    pdfPath: '/pdfs/k_beauty_skincare.pdf',
    pages: 5,
    lang: 'en',
  },
  {
    id: 'ebook_korean_workout_8900',
    name: 'Korean Idol-Inspired Workout (30-day)',
    amount: 8900,
    desc: 'K-pop idol fitness routine — 30 minutes/day, 6 days/week, no equipment except resistance band. Lower body / cardio / upper body rotation + Korean diet companion.',
    type: 'ebook',
    pdfPath: '/pdfs/korean_workout_plan.pdf',
    pages: 5,
    lang: 'en',
  },
  {
    id: 'ebook_coffee_culture_5900',
    name: 'Korean Cafe Culture & Drinks Guide',
    amount: 5900,
    desc: 'Why Korea has 100K+ cafes. 12 essential cafe drinks with Korean pronunciation + cafe etiquette + best chains (Compose Coffee, Mega, Twosome, Starbucks Reserve).',
    type: 'ebook',
    pdfPath: '/pdfs/korean_coffee_culture.pdf',
    pages: 4,
    lang: 'en',
  },
  {
    id: 'ebook_kdrama_saju_9900',
    name: 'K-Drama Character Saju Decoder Vol.1',
    amount: 9900,
    desc: 'Reading the four pillars of K-drama archetypes. 10 Day Master types mapped to common K-drama characters (CEO heir, mentor, detective, healer). Compatibility framework.',
    type: 'ebook',
    pdfPath: '/pdfs/kdrama_saju_decoder.pdf',
    pages: 4,
    lang: 'en',
  },
  {
    id: 'ebook_travel_phrases_4900',
    name: 'Korean Travel Phrases for Tourists',
    amount: 4900,
    desc: '100+ Korean phrases organized by situation — greetings, transit, restaurant, shopping, emergencies, cultural etiquette. Includes pronunciation guide.',
    type: 'ebook',
    pdfPath: '/pdfs/korean_travel_phrases.pdf',
    pages: 5,
    lang: 'en',
  },
  // ─── 5/3 추가 EBOOK 5종 (catalog 27 → 32) ─────────────────
  {
    id: 'ebook_korean_wedding_9900',
    name: 'Korean Wedding Etiquette Guide',
    amount: 9900,
    desc: 'From engagement to wedding ceremony — what foreigners need to know. Saju compatibility check, money gift etiquette, pyebaek bow ceremony, gift exchange timeline.',
    type: 'ebook',
    pdfPath: '/pdfs/korean_wedding_guide.pdf',
    pages: 5,
    lang: 'en',
  },
  {
    id: 'ebook_business_korea_11900',
    name: 'Doing Business in Korea — Etiquette Guide',
    amount: 11900,
    desc: 'Korean business hierarchy, business card exchange, hwesik drinking culture, gift giving, decision making, contract norms. Critical for foreign companies entering Korea.',
    type: 'ebook',
    pdfPath: '/pdfs/korean_business_etiquette.pdf',
    pages: 6,
    lang: 'en',
  },
  {
    id: 'ebook_kpop_saju_vol2_9900',
    name: 'K-Pop Idol Saju Decoder Vol.2',
    amount: 9900,
    desc: 'Reading the four pillars of K-pop archetypes — solo vs group dynamics, 5-element group framework, stage name vs birth name, comeback timing.',
    type: 'ebook',
    pdfPath: '/pdfs/korean_kpop_saju_vol2.pdf',
    pages: 5,
    lang: 'en',
  },
  {
    id: 'ebook_korean_funeral_7900',
    name: 'Korean Funeral & Memorial Etiquette',
    amount: 7900,
    desc: '3-day Korean funeral format, condolence visit protocol, money gift envelope, altar bow ritual (jeoldari), memorial ceremony (jesa).',
    type: 'ebook',
    pdfPath: '/pdfs/korean_funeral_etiquette.pdf',
    pages: 4,
    lang: 'en',
  },
  {
    id: 'ebook_korean_drinking_5900',
    name: 'Korean Drinking Culture & Soju Etiquette',
    amount: 5900,
    desc: 'Survive hwesik (Korean company drinking sessions). Soju basics, pour etiquette (two hands), bomb shots (폭탄주), hangover cure haejang-guk.',
    type: 'ebook',
    pdfPath: '/pdfs/korean_drinking_culture.pdf',
    pages: 5,
    lang: 'en',
  },
  // ─── 5/3 글로벌 mass market 5종 (catalog 32 → 37) ─────────────
  // Korea-specific 제거. 영문권 mass market 검증 niche.
  {
    id: 'ebook_ai_prompts_100_9900',
    name: 'AI Prompts Library: 100 Best Prompts for Solo Entrepreneurs',
    amount: 9900,
    desc: '100 ChatGPT/Claude/Gemini prompts for sales copy, content, customer service, email, product dev, operations. Tested. Copy-paste ready. $1K-5K/month bestseller niche on Amazon KDP.',
    type: 'ebook',
    pdfPath: '/pdfs/ai_prompts_library_100.pdf',
    pages: 4,
    lang: 'en',
  },
  {
    id: 'ebook_time_block_7900',
    name: 'Time Block Mastery: The 21-Day System',
    amount: 7900,
    desc: 'Reclaim 15+ hours/week with the productivity system used by Cal Newport, Elon Musk. 21-day plan with audit, themed days, deep work blocks, common pitfalls.',
    type: 'ebook',
    pdfPath: '/pdfs/time_block_mastery.pdf',
    pages: 5,
    lang: 'en',
  },
  {
    id: 'ebook_solo_entrepreneur_11900',
    name: 'Solo Entrepreneur Stack 2026',
    amount: 11900,
    desc: 'The complete tools, workflows, numbers behind $10K-100K MRR one-person businesses. 36% startups now solo, 77% first-year profitable. Modern AI-powered stack ($50-400/mo).',
    type: 'ebook',
    pdfPath: '/pdfs/solo_entrepreneur_stack_2026.pdf',
    pages: 6,
    lang: 'en',
  },
  {
    id: 'ebook_mindfulness_5min_5900',
    name: 'Mindfulness for Busy People: 5-Minute Daily Practice',
    amount: 5900,
    desc: '5-minute daily practices backed by Stanford and Harvard research. 4-7-8 breathing, body scan, single-tasking, 3 gratitudes. 80% benefit of 30-min sessions.',
    type: 'ebook',
    pdfPath: '/pdfs/mindfulness_5min_daily.pdf',
    pages: 5,
    lang: 'en',
  },
  {
    id: 'ebook_ai_side_hustle_14900',
    name: 'AI Side Hustle Blueprint: $0 → $10K/month',
    amount: 14900,
    desc: '12 proven AI-powered side hustles with real numbers and timelines. Faceless YouTube, Notion templates, AI audiobooks, niche newsletters, productized services. Year 1: $30K, Year 3: $400K math.',
    type: 'ebook',
    pdfPath: '/pdfs/ai_side_hustle_blueprint.pdf',
    pages: 5,
    lang: 'en',
  },
  // ─── 5/3 MEGA BUNDLE — 100일 가속 매출 path ──────────────────
  // 20 PDF + 10 audiobook + 20 SEO blog = catalog 전체 묶음 launch.
  // 정상가 $200+, launch $97 (50% off). Limited time first 100 buyers.
  {
    id: 'bundle_kunstudio_mega_9700',
    name: '🔥 KunStudio Mega Bundle — 20 EBOOKs + Bonuses (LAUNCH)',
    amount: 9700, // ~$70 KRW (~$70 USD with conversion)
    desc: 'ALL 20 KunStudio EBOOKs (AI Prompts, Solo Entrepreneur Stack, Time Block Mastery, Mindfulness, AI Side Hustle, Korean Saju + 15 more). Worth $200+ separately. Launch price $70 first 100 buyers only. Includes audiobook companions when available.',
    type: 'bundle',
    pdfPaths: [
      '/pdfs/ai_prompts_library_100.pdf',
      '/pdfs/time_block_mastery.pdf',
      '/pdfs/solo_entrepreneur_stack_2026.pdf',
      '/pdfs/mindfulness_5min_daily.pdf',
      '/pdfs/ai_side_hustle_blueprint.pdf',
      '/pdfs/saju_birth_chart_en.pdf',
      '/pdfs/kwisdom_wall_art.pdf',
      '/pdfs/kwisdom_daily_planner_2026.pdf',
      '/pdfs/korean_tax_foreigners.pdf',
      '/pdfs/korean_recipe_planner.pdf',
      '/pdfs/k_beauty_skincare.pdf',
      '/pdfs/korean_workout_plan.pdf',
      '/pdfs/korean_coffee_culture.pdf',
      '/pdfs/kdrama_saju_decoder.pdf',
      '/pdfs/korean_travel_phrases.pdf',
      '/pdfs/korean_wedding_guide.pdf',
      '/pdfs/korean_business_etiquette.pdf',
      '/pdfs/korean_kpop_saju_vol2.pdf',
      '/pdfs/korean_funeral_etiquette.pdf',
      '/pdfs/korean_drinking_culture.pdf',
    ],
    pages: 100,
    lang: 'en',
    launch_limit: 100,
    original_price_krw: 200000,
  },
  // ─── 70일 $750K 가속 — Lifetime tier (passive only) ──────────────
  // 2026-05-04: high-touch SKU 4종 (Cohort/SaaS/Audit/WL) 제거 — 사용자 직접 운영 부담 회피.
  // catalog 정책: 일회성 PDF/번들/Lifetime만 유지. 정기결제 + 1:1 응대 + 코호트 운영 X.
  {
    id: 'kunstudio_lifetime_69700',
    name: '🌟 KunStudio Lifetime — All Current + Future EBOOKs Forever',
    amount: 69700, // ~$497 USD
    desc: 'ALL 20 current EBOOKs + every future EBOOK we publish (10+ per month). Audiobook companions included. Priority email support. Best for builders who want lifetime access without recurring fees. Worth $5,000+ over 1 year.',
    type: 'bundle',
    pdfPaths: 'all_current_plus_future',
    lang: 'en',
    tier: 'lifetime',
    launch_limit: 50, // first 50 buyers only at this price
    original_price_krw: 700000,
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
  // 2026-05-04: PortOne 테스트 모드 활성화. STORE_ID + KCN(merchantest9) + KakaoPay(TC0ONETIME) + API Secret 등록 완료.
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

  // PayPal Subscription Plans 제거됨 (2026-05-04): AI Productivity OS SKU 폐기.
  // 정기결제 SaaS는 사용자 직접 운영 부담 — 자율 운영 방향 X.

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
