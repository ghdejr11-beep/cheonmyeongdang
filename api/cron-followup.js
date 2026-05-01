/**
 * 천명당 D+3 / D+7 / D+14 / D+30 / D+90 후속 메일 자동 발송 (Vercel Cron — 단일 일1회 실행)
 * GET /api/cron-followup                     — 정기 실행 (매일 09:00 KST). 5개 코호트 모두 처리
 * GET /api/cron-followup?test=1              — 본인 테스트 발송 (D+3 기본)
 * GET /api/cron-followup?test=1&days=30      — D+30 winback 템플릿 테스트
 * GET /api/cron-followup?test=1&days=90      — D+90 win-back 템플릿 테스트
 * GET /api/cron-followup?days=30             — D+30 코호트만 cron 처리 (개별 디버그용)
 * GET /api/cron-followup?dry=1               — 발송 안하고 대상자만 미리보기
 * GET /api/cron-followup?test=1&days=30&season=eobonal   — D+30 5월 어버이날 시즌 메일 테스트
 * GET /api/cron-followup?test=1&days=30&season=jongsose  — D+30 5월 종소세 시즌 메일 테스트
 *
 * 5월 시즌 (2026):
 *   - 어버이날 (5/8) — paid_at 5/1~5/7 코호트 D+30 도달 시 어버이날 LP cross-link + 카네이션 카드 5종 + KDP "어버이날 감사 편지 100선"
 *   - 종소세 (5/31) — paid_at 5/1~5/24 코호트 D+30 도달 시 종소세 LP cross-link + 체크리스트 SKU + KDP "종소세 셀프 신고 가이드"
 *   - 두 시즌 동시 매칭 시 어버이날 우선 (D-Day 임박 + 클릭률 우위, getSeasonalCampaign() priority)
 *   - 시즌 외 D+30 코호트는 기존 일반 winback 그대로 유지 (영향 없음)
 *
 * 흐름:
 *   1) GitHub Gist에서 결제 데이터 로드
 *   2) 코호트별 paid_at 윈도우 필터:
 *      - D+3  : "정밀 풀이 활용 5팁 + 월회원권 3일 무료 체험" (LTV +30%)
 *      - D+7  : "활용 1주 — 종합 풀이 ₩29,900 업셀" (LTV +20%)
 *      - D+14 : "매일 카톡 운세 — 월회원권 ₩29,900 / 신년운세 ₩15,000" (LTV +15%)
 *      - D+30 : "윈백 — SKU별 분기 + 30% 할인 쿠폰 (WB30-XXXX, 7일 한정)" (LTV +20-30%)
 *      - D+60 : "재구매 ₩2,000 쿠폰 (WELCOME2K)" (LTV +5%)
 *      - D+90 : "마지막 윈백 — 종합 풀이 50% (WB90-XXXX, 14일 한정)" (LTV +10%)
 *   3) 각 코호트마다 followup_sent / followup_d7_sent / followup_d14_sent / winback_d30_sent / followup_d60_sent / winback_d90_sent 별도 마킹
 *   4) refunded=true 또는 subscription 타입은 모든 코호트에서 자동 제외 (purchase-store.js:213)
 *
 * Vercel Hobby plan: cron 일 1회 한도 → 단일 cron이 3개 코호트 모두 처리
 *   { "path": "/api/cron-followup", "schedule": "0 0 * * *" }   // UTC 00:00 = KST 09:00
 *
 * 보안:
 *   - Vercel Cron 호출 시 Authorization: Bearer $CRON_SECRET 헤더 자동 주입
 *   - 외부 호출 거부 (CRON_SECRET 미일치 + ?test 아닌 경우 403)
 *   - test 모드는 비밀 토큰 (?test=1&key=$FOLLOWUP_TEST_KEY) 또는 본인 IP 검증으로 제한
 */

const https = require('https');
const crypto = require('crypto');
const querystring = require('querystring');
const {
  listFollowupTargets,
  markFollowupSent,
} = require('../lib/purchase-store');

// ─── WB30 Winback 쿠폰 코드 — orderId 기반 결정론적 발급 (서명 검증으로 1회용 보장) ───
// 동일 orderId × 동일 secret → 항상 같은 코드 → coupon-validate가 그대로 검증 가능
// 7일 만료는 발송일 기준으로 고객 안내, 검증은 사용 횟수 1회로 강제 (single_use_per_email)
function genWinbackCoupon(orderId, days = 30) {
  const secret = (process.env.COUPON_SIGNING_SECRET || process.env.CRON_SECRET || 'cmd_wb_default').trim();
  const prefix = days === 30 ? 'WB30' : days === 90 ? 'WB90' : 'WB' + days;
  const h = crypto.createHmac('sha256', secret).update(`${prefix}:${orderId}`).digest('hex').toUpperCase();
  // 4자리 영숫자 코드 (충돌 1/1.6M, 발송 규모 충분)
  return `${prefix}-${h.slice(0, 4)}`;
}
function fmtKstYmd(date) {
  const t = new Date(date);
  // KST = UTC+9
  const kst = new Date(t.getTime() + 9 * 60 * 60 * 1000);
  const y = kst.getUTCFullYear();
  const m = String(kst.getUTCMonth() + 1).padStart(2, '0');
  const d = String(kst.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

// ─── 5월 시즌 캠페인 분기 ───────────────────────────────────────────
// D+30 winback 발송 시점에 가입일 기준 시즌 매칭. 두 시즌 동시 매칭 시 어버이날 우선
// (D-Day 임박 + 클릭률 우위). 시즌 코호트는 일반 winback 분기보다 훨씬 강한 후크.
//
// 어버이날 (5/8) — 5월 1~7일 paid_at: D+30~D+37 도달 시 어버이날 메일
// 종소세  (5/31) — 5월 1~24일 paid_at: D+30~D+미정 도달 시 종소세 메일 (단, 어버이날 미해당분만)
//
// 매년 시즌 갱신: SEASONAL_CAMPAIGNS 배열에 새 객체 추가, 만료 객체는 archived=true 마킹
const SEASONAL_CAMPAIGNS = [
  {
    id: 'eobonal_2026',
    priority: 1, // 낮을수록 우선
    // paid_at 윈도우 (KST 자정 경계 대신 UTC 기준 날짜 — 발송 시점 ±1일 오차 허용)
    paidStart: '2026-05-01',
    paidEnd: '2026-05-07', // inclusive
    eventDate: '2026-05-08', // 어버이날
    archived: false,
  },
  {
    id: 'jongsose_2026',
    priority: 2,
    paidStart: '2026-05-01',
    paidEnd: '2026-05-24', // 종소세 신고 마감 5/31 기준 D-7
    eventDate: '2026-05-31',
    archived: false,
  },
];

function getSeasonalCampaign(signupDate) {
  if (!signupDate) return null;
  const ymd = fmtKstYmd(signupDate);
  const matched = SEASONAL_CAMPAIGNS
    .filter((c) => !c.archived)
    .filter((c) => ymd >= c.paidStart && ymd <= c.paidEnd)
    .sort((a, b) => a.priority - b.priority);
  return matched[0] ? matched[0].id : null;
}

function daysUntil(targetYmd) {
  // 오늘(KST) 대비 남은 일수 — D-Day 음수 시 0 반환 (지난 시즌)
  const now = new Date();
  const todayYmd = fmtKstYmd(now);
  const [y1, m1, d1] = todayYmd.split('-').map(Number);
  const [y2, m2, d2] = targetYmd.split('-').map(Number);
  const t1 = Date.UTC(y1, m1 - 1, d1);
  const t2 = Date.UTC(y2, m2 - 1, d2);
  return Math.max(0, Math.round((t2 - t1) / (24 * 60 * 60 * 1000)));
}

// ─── 공통 푸터 ───
function FOOTER_HTML() {
  return `
    <div style="text-align:center;color:#7a6f5a;font-size:11px;line-height:1.8;padding:16px;border-top:1px solid rgba(201,168,76,0.15);">
      <strong style="color:#a89880;">쿤스튜디오</strong> · 대표 홍덕훈 · 사업자등록번호 552-59-00848<br>
      문의: <a href="mailto:ghdejr11@gmail.com" style="color:#c9a84c;text-decoration:none;">ghdejr11@gmail.com</a><br>
      <a href="https://cheonmyeongdang.vercel.app/terms.html" style="color:#a89880;text-decoration:underline;">이용약관</a> ·
      <a href="https://cheonmyeongdang.vercel.app/privacy.html" style="color:#a89880;text-decoration:underline;">개인정보처리방침</a> ·
      <a href="https://cheonmyeongdang.vercel.app/support.html" style="color:#a89880;text-decoration:underline;">고객센터</a><br>
      <span style="color:#5a5044;">본 메일은 결제 후속 안내로 발송되었으며, 수신을 원치 않으시면 ghdejr11@gmail.com 으로 회신해 주세요.</span>
    </div>`;
}

// ───────────────────────────── D+3 템플릿 ─────────────────────────────
function buildD3Html({ customerName, skuName, orderId }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';

  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>천명당 — 정밀 풀이 활용 가이드</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:42px;margin-bottom:8px;">🌙</div>
        <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px 0;font-weight:700;">${greet}<br>풀이는 잘 받아보셨나요?</h1>
        <p style="color:#e8e0d0;font-size:15px;line-height:1.7;margin:12px 0 0;">3일 전 <strong style="color:#e8c97a;">${skuName}</strong>을 결제해 주셨습니다.<br>오늘은 그 결과를 <strong>5배 더 깊이</strong> 활용하는 방법을 알려드릴게요.</p>
      </div>
      <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px;margin:20px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:14px;">정밀 풀이 활용 5가지 팁</div>
        ${[
          ['1','일주(日柱)부터 다시 보기','일주는 본인의 핵심 성격·연애·결혼관을 결정합니다. 풀이의 일주 해석을 천천히 다시 읽어보세요.'],
          ['2','대운(大運) — 10년 흐름 확인','현재 진행 중인 대운이 인생의 큰 흐름입니다. 길운/흉운 구간을 알면 큰 결정 타이밍을 잡을 수 있습니다.'],
          ['3','세운(歲運) — 올해의 운세 캘린더','올해 어떤 달에 길운이 오는지, 어떤 달을 조심해야 하는지 — 풀이의 세운 표를 캘린더에 표시해 두세요.'],
          ['4','오행 균형 — 부족한 기운 보충','목·화·토·금·수 중 부족한 오행은 색상·방위·음식으로 보충 가능합니다. 풀이의 오행 분석을 일상에 적용해 보세요.'],
          ['5','가족·연인 사주와 비교 (궁합)','본인 사주만 보면 평면적입니다. 가족·연인의 사주와 비교했을 때 진짜 통찰이 나옵니다.'],
        ].map(([n,t,d]) => `
        <div style="display:flex;margin-bottom:14px;">
          <div style="flex-shrink:0;width:28px;height:28px;border-radius:50%;background:#c9a84c;color:#080a10;text-align:center;line-height:28px;font-weight:800;margin-right:12px;">${n}</div>
          <div style="flex:1;">
            <div style="color:#e8c97a;font-weight:700;font-size:14px;margin-bottom:4px;">${t}</div>
            <div style="color:#a89880;font-size:13px;line-height:1.6;">${d}</div>
          </div>
        </div>`).join('')}
      </div>
      <div style="background:linear-gradient(135deg,#1a1530,#251a3a);border:2px solid #e8c97a;border-radius:14px;padding:24px 20px;margin:24px 0;text-align:center;">
        <div style="display:inline-block;font-size:11px;background:#e8c97a;color:#080a10;padding:4px 12px;border-radius:999px;font-weight:800;letter-spacing:0.12em;margin-bottom:10px;">⭐ 한정 혜택</div>
        <h2 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:20px;margin:8px 0;font-weight:700;">월회원권 — 첫 3일 무료 체험</h2>
        <p style="color:#e8e0d0;font-size:14px;line-height:1.7;margin:10px 0 16px;"><strong style="color:#e8c97a;">매일 아침 8시</strong> 오늘의 운세 카톡 발송<br><strong style="color:#e8c97a;">사주·궁합 무제한</strong> 풀이<br>새로운 일·사람·결정마다 그날그날 풀어보기</p>
        <div style="font-size:13px;color:#a89880;margin-bottom:16px;">월 <span style="text-decoration:line-through;">₩9,900</span> → <strong style="color:#e8c97a;font-size:18px;">3일 무료 후 자동결제 (언제든 해지)</strong></div>
        <a href="https://cheonmyeongdang.vercel.app/pay.html?sku=subscribe_monthly_29900&utm_source=email_d3&utm_campaign=upsell_monthly&utm_content=d3" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:8px;font-size:15px;letter-spacing:0.05em;">🎁 무료로 시작하기</a>
        <div style="font-size:11px;color:#7a6f5a;margin-top:12px;line-height:1.6;">* 3일 안에 해지하면 ₩0 · 카드 부담 없습니다</div>
      </div>
      <div style="background:rgba(254,229,0,0.05);border:1px solid rgba(254,229,0,0.3);border-radius:12px;padding:18px;text-align:center;margin:18px 0;">
        <div style="font-size:24px;margin-bottom:6px;">💬</div>
        <div style="color:#e8c97a;font-weight:700;font-size:15px;margin-bottom:6px;">카카오톡 채널 친구추가</div>
        <p style="color:#a89880;font-size:13px;line-height:1.6;margin:0 0 12px;">매일 아침 8시 오늘의 운세 + 신규 풀이 알림을 카톡으로 받아보세요.</p>
        <a href="http://pf.kakao.com/_xnxnxnK?utm_source=email_d3&utm_campaign=channel" style="display:inline-block;padding:10px 24px;background:#fee500;color:#191919;font-weight:700;text-decoration:none;border-radius:6px;font-size:13px;">💬 카톡 채널 친구추가</a>
      </div>
      <div style="font-size:11px;color:#5a5044;text-align:center;margin-top:18px;">결제 주문번호: <span style="font-family:Menlo,monospace;">${orderId}</span></div>
    </div>
    ${FOOTER_HTML()}
  </div>
</body></html>`;
}

function buildD3Text({ customerName, skuName, orderId }) {
  return [
    '천명당 (天命堂) — 정밀 풀이 활용 가이드',
    '',
    `${customerName ? customerName + '님, ' : ''}3일 전 ${skuName}을 결제해 주셨습니다.`,
    '오늘은 그 결과를 더 깊이 활용하는 5가지 팁을 보내드립니다.',
    '',
    '─── 정밀 풀이 활용 5가지 팁 ───',
    '1. 일주(日柱)부터 다시 보기 — 핵심 성격·연애·결혼관',
    '2. 대운(大運) — 10년 흐름 / 길운·흉운 구간 확인',
    '3. 세운(歲運) — 올해의 길운 달을 캘린더에 표시',
    '4. 오행 균형 — 부족한 기운을 색상·방위·음식으로 보충',
    '5. 가족·연인 사주와 비교 (궁합)',
    '',
    '─── 월회원권 — 첫 3일 무료 체험 ───',
    '· 매일 아침 8시 오늘의 운세 카톡 발송',
    '· 사주·궁합 무제한 풀이',
    '· 월 ₩29,900 (3일 안에 해지하면 ₩0)',
    '시작하기: https://cheonmyeongdang.vercel.app/pay.html?sku=subscribe_monthly_29900&utm_source=email_d3&utm_campaign=upsell_monthly',
    '',
    '카카오톡 채널 친구추가: http://pf.kakao.com/_xnxnxnK',
    '',
    `결제 주문번호: ${orderId}`,
    '',
    '쿤스튜디오 · 대표 홍덕훈 · 사업자등록번호 552-59-00848',
    '문의: ghdejr11@gmail.com',
  ].join('\n');
}

// ───────────────────────────── D+7 템플릿 ─────────────────────────────
// 종합 풀이 ₩29,900 업셀 (단건 합산 ₩34,800 → ₩29,900)
function buildD7Html({ customerName, skuName, orderId }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';

  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>천명당 — 1주일 활용 점검 & 종합 풀이</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:42px;margin-bottom:8px;">📜</div>
        <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px 0;font-weight:700;">${greet}<br>결제 1주일 — 어떻게 활용하고 계신가요?</h1>
        <p style="color:#e8e0d0;font-size:15px;line-height:1.7;margin:12px 0 0;">7일 전 <strong style="color:#e8c97a;">${skuName}</strong>을 받아보신 후,<br>풀이를 다시 펼쳐 본 분이 가장 많이 묻는 질문 5가지를 정리했습니다.</p>
      </div>

      <!-- 깊이 활용 5팁 (D+3와 다른 각도) -->
      <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px;margin:20px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:14px;">정밀 풀이 — 1주일 점검 5가지</div>
        ${[
          ['1','내 풀이의 "용신(用神)" 찾기','용신은 내 사주에 가장 도움이 되는 오행입니다. 풀이에서 용신을 확인하고, 색상·방위·직업 선택에 활용하세요.'],
          ['2','지지(地支) 충·합·형·해 점검','일지·월지의 충돌이나 결합은 인간관계·직장 변동의 신호입니다. 올해 세운과 충돌하는 달을 미리 표시해 두세요.'],
          ['3','신살(神殺) — 도화·역마·화개','신살은 인생의 색을 결정합니다. 도화살(인기), 역마살(이동), 화개살(예술/종교) — 본인 신살을 확인하세요.'],
          ['4','격국(格局) — 본인의 사회적 그릇','정관격·식신격·재격 등 격국은 직업적 강점을 보여줍니다. 풀이의 격국을 커리어 결정에 적용하세요.'],
          ['5','대운 전환점 — 인생의 변곡 시기','대운이 바뀌는 시기는 큰 결정의 타이밍입니다. 본인 대운 전환 나이를 메모해 두세요.'],
        ].map(([n,t,d]) => `
        <div style="display:flex;margin-bottom:14px;">
          <div style="flex-shrink:0;width:28px;height:28px;border-radius:50%;background:#c9a84c;color:#080a10;text-align:center;line-height:28px;font-weight:800;margin-right:12px;">${n}</div>
          <div style="flex:1;">
            <div style="color:#e8c97a;font-weight:700;font-size:14px;margin-bottom:4px;">${t}</div>
            <div style="color:#a89880;font-size:13px;line-height:1.6;">${d}</div>
          </div>
        </div>`).join('')}
      </div>

      <!-- 종합 풀이 ₩29,900 업셀 -->
      <div style="background:linear-gradient(135deg,#1a1530,#251a3a);border:2px solid #e8c97a;border-radius:14px;padding:24px 20px;margin:24px 0;text-align:center;">
        <div style="display:inline-block;font-size:11px;background:#e8c97a;color:#080a10;padding:4px 12px;border-radius:999px;font-weight:800;letter-spacing:0.12em;margin-bottom:10px;">📜 통합 리포트</div>
        <h2 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:8px 0;font-weight:700;">종합 풀이 — ₩29,900</h2>
        <p style="color:#e8e0d0;font-size:14px;line-height:1.7;margin:10px 0 14px;">사주 정밀 + 궁합 + 신년운세<br><strong style="color:#e8c97a;">3가지를 한 번에 + 통합 해석 추가</strong></p>

        <div style="background:rgba(0,0,0,0.4);border-radius:8px;padding:14px;margin:14px 0;text-align:left;">
          <div style="display:flex;justify-content:space-between;font-size:13px;color:#a89880;padding:4px 0;">
            <span>· 사주 정밀 풀이</span><span>₩9,900</span>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:13px;color:#a89880;padding:4px 0;">
            <span>· 궁합 정밀 분석</span><span>₩9,900</span>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:13px;color:#a89880;padding:4px 0;border-bottom:1px solid rgba(201,168,76,0.2);">
            <span>· 신년운세 (12개월)</span><span>₩15,000</span>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:14px;color:#7a6f5a;padding:8px 0 4px;">
            <span>단건 합산</span><span style="text-decoration:line-through;">₩34,800</span>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:16px;color:#e8c97a;font-weight:800;padding:4px 0;">
            <span>종합 풀이</span><span>₩29,900</span>
          </div>
          <div style="text-align:center;font-size:12px;color:#c9a84c;margin-top:8px;">→ <strong>₩4,900 절약 (14% off)</strong></div>
        </div>

        <a href="https://cheonmyeongdang.vercel.app/pay.html?sku=comprehensive_29900&utm_source=email_d7&utm_campaign=upsell_comprehensive&utm_content=d7"
           style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:8px;font-size:15px;letter-spacing:0.05em;margin-top:8px;">📜 종합 풀이 보기</a>
        <div style="font-size:11px;color:#7a6f5a;margin-top:12px;line-height:1.6;">* 사주+궁합+신년운세 통합 해석으로 단건보다 깊이 있는 통찰을 드립니다</div>
      </div>

      <!-- 카톡 채널 추가 CTA -->
      <div style="background:rgba(254,229,0,0.05);border:1px solid rgba(254,229,0,0.3);border-radius:12px;padding:18px;text-align:center;margin:18px 0;">
        <div style="font-size:24px;margin-bottom:6px;">💬</div>
        <div style="color:#e8c97a;font-weight:700;font-size:15px;margin-bottom:6px;">카카오톡 채널 친구추가</div>
        <p style="color:#a89880;font-size:13px;line-height:1.6;margin:0 0 12px;">매일 아침 8시 오늘의 운세 + 신규 풀이 알림을 카톡으로 받아보세요.</p>
        <a href="http://pf.kakao.com/_xnxnxnK?utm_source=email_d7&utm_campaign=channel" style="display:inline-block;padding:10px 24px;background:#fee500;color:#191919;font-weight:700;text-decoration:none;border-radius:6px;font-size:13px;">💬 카톡 채널 친구추가</a>
      </div>

      <div style="font-size:11px;color:#5a5044;text-align:center;margin-top:18px;">결제 주문번호: <span style="font-family:Menlo,monospace;">${orderId}</span></div>
    </div>
    ${FOOTER_HTML()}
  </div>
</body></html>`;
}

function buildD7Text({ customerName, skuName, orderId }) {
  return [
    '천명당 (天命堂) — 1주일 활용 점검 & 종합 풀이',
    '',
    `${customerName ? customerName + '님, ' : ''}7일 전 ${skuName}을 결제해 주셨습니다.`,
    '풀이를 다시 펼쳐본 분이 가장 많이 묻는 5가지를 정리했습니다.',
    '',
    '─── 정밀 풀이 1주일 점검 ───',
    '1. 용신(用神) 찾기 — 색상·방위·직업 선택에 활용',
    '2. 지지(地支) 충·합·형·해 점검 — 인간관계·직장 변동 예측',
    '3. 신살(神殺) — 도화·역마·화개 — 인생의 색깔',
    '4. 격국(格局) — 본인의 사회적 그릇',
    '5. 대운 전환점 — 인생의 변곡 시기 메모',
    '',
    '─── 종합 풀이 — ₩29,900 ───',
    '· 사주 정밀(₩9,900) + 궁합(₩9,900) + 신년운세(₩15,000)',
    '· 단건 합산 ₩34,800 → ₩15,000 (₩19,800 절약, 57% off)',
    '· 3가지 통합 해석 — 단건보다 깊이 있는 통찰',
    '바로가기: https://cheonmyeongdang.vercel.app/pay.html?sku=comprehensive_29900&utm_source=email_d7&utm_campaign=upsell_comprehensive',
    '',
    '카카오톡 채널 친구추가: http://pf.kakao.com/_xnxnxnK',
    '',
    `결제 주문번호: ${orderId}`,
    '',
    '쿤스튜디오 · 대표 홍덕훈 · 사업자등록번호 552-59-00848',
    '문의: ghdejr11@gmail.com',
  ].join('\n');
}

// ───────────────────────────── D+14 템플릿 ─────────────────────────────
// 월회원권 ₩29,900 / 신년운세 ₩15,000 시즈널 양자택일
function buildD14Html({ customerName, skuName, orderId }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';

  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>천명당 — 결제 2주일 / 매일 새 운세</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:42px;margin-bottom:8px;">🌅</div>
        <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px 0;font-weight:700;">${greet}<br>결제 2주일 — 매일 새 운세를 받아보세요</h1>
        <p style="color:#e8e0d0;font-size:15px;line-height:1.7;margin:12px 0 0;">한 번의 풀이는 큰 그림을 보여주지만,<br><strong style="color:#e8c97a;">매일의 작은 선택</strong>은 그날의 운세에 따라 달라집니다.<br>오늘은 두 가지 길을 제안드릴게요.</p>
      </div>

      <!-- 양자택일 카드 — 월회원권 -->
      <div style="background:linear-gradient(135deg,#1a1530,#251a3a);border:2px solid #e8c97a;border-radius:14px;padding:22px 18px;margin:18px 0;">
        <div style="text-align:center;">
          <div style="display:inline-block;font-size:11px;background:#e8c97a;color:#080a10;padding:4px 12px;border-radius:999px;font-weight:800;letter-spacing:0.12em;margin-bottom:10px;">⭐ 추천 · 매일 활용형</div>
          <h2 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:20px;margin:6px 0;font-weight:700;">월회원권 — ₩29,900 / 월</h2>
          <p style="color:#e8e0d0;font-size:13px;line-height:1.7;margin:8px 0 14px;">매일 아침 8시 오늘의 운세 카톡<br>사주 정밀 + 궁합 <strong style="color:#e8c97a;">무제한 풀이</strong><br>새로운 사람·결정마다 그날그날 풀어보기</p>
          <a href="https://cheonmyeongdang.vercel.app/pay.html?sku=subscribe_monthly_29900&utm_source=email_d14&utm_campaign=upsell_monthly_or_sinnyeon&utm_content=d14_monthly"
             style="display:inline-block;padding:12px 28px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:8px;font-size:14px;">월회원 시작 (3일 무료)</a>
          <div style="font-size:11px;color:#7a6f5a;margin-top:10px;">* 3일 안에 해지하면 ₩0</div>
        </div>
      </div>

      <!-- OR 구분 -->
      <div style="text-align:center;color:#7a6f5a;font-size:12px;letter-spacing:0.3em;margin:8px 0;">— 또는 —</div>

      <!-- 양자택일 카드 — 신년운세 -->
      <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(201,168,76,0.4);border-radius:14px;padding:22px 18px;margin:18px 0;">
        <div style="text-align:center;">
          <div style="display:inline-block;font-size:11px;background:rgba(201,168,76,0.2);color:#e8c97a;padding:4px 12px;border-radius:999px;font-weight:800;letter-spacing:0.12em;margin-bottom:10px;">📅 1년치 한 번에</div>
          <h2 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:20px;margin:6px 0;font-weight:700;">신년운세 — ₩15,000</h2>
          <p style="color:#e8e0d0;font-size:13px;line-height:1.7;margin:8px 0 14px;">12개월 월별 운세 + 신살 연간 리포트<br>매월 어떤 일이 다가오는지 <strong style="color:#e8c97a;">미리 1년치 캘린더</strong>로 확인<br>큰 결정 전에 한 번 받아두면 든든</p>
          <a href="https://cheonmyeongdang.vercel.app/pay.html?sku=sinnyeon_15000&utm_source=email_d14&utm_campaign=upsell_monthly_or_sinnyeon&utm_content=d14_sinnyeon"
             style="display:inline-block;padding:12px 28px;background:rgba(201,168,76,0.15);color:#e8c97a;border:1px solid #c9a84c;font-weight:800;text-decoration:none;border-radius:8px;font-size:14px;">신년운세 보기</a>
          <div style="font-size:11px;color:#7a6f5a;margin-top:10px;">* 단건 결제 · 자동결제 없음</div>
        </div>
      </div>

      <!-- 미니 활용 가이드 (D+3·D+7과 차별화) -->
      <div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:16px 18px;margin:18px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;">결제 후 2주 — 가장 많이 받은 질문</div>
        <div style="color:#a89880;font-size:13px;line-height:1.8;">
          <strong style="color:#e8c97a;">Q. 풀이 결과가 잘 맞지 않는 것 같아요</strong><br>
          A. 대운(10년 단위)은 시기별로 다르게 작용합니다. 본인 대운 전환 나이 ±2년은 풀이가 지금 모습과 다르게 느껴질 수 있습니다.<br><br>
          <strong style="color:#e8c97a;">Q. 매일 운세는 어디서 보나요?</strong><br>
          A. 월회원권에 포함된 매일 아침 8시 카톡 운세를 권장합니다. 본인 사주에 그날 천간·지지를 대입한 일진(日辰) 기반입니다.<br><br>
          <strong style="color:#e8c97a;">Q. 가족·연인 사주 풀이는?</strong><br>
          A. 궁합(₩9,900) 또는 월회원권 무제한 풀이로 가능합니다.
        </div>
      </div>

      <!-- 카톡 채널 -->
      <div style="background:rgba(254,229,0,0.05);border:1px solid rgba(254,229,0,0.3);border-radius:12px;padding:18px;text-align:center;margin:18px 0;">
        <div style="font-size:24px;margin-bottom:6px;">💬</div>
        <div style="color:#e8c97a;font-weight:700;font-size:15px;margin-bottom:6px;">카카오톡 채널 친구추가</div>
        <p style="color:#a89880;font-size:13px;line-height:1.6;margin:0 0 12px;">매일 아침 8시 오늘의 운세를 카톡으로 받아보세요. (무료 미리보기 제공)</p>
        <a href="http://pf.kakao.com/_xnxnxnK?utm_source=email_d14&utm_campaign=channel" style="display:inline-block;padding:10px 24px;background:#fee500;color:#191919;font-weight:700;text-decoration:none;border-radius:6px;font-size:13px;">💬 카톡 채널 친구추가</a>
      </div>

      <div style="font-size:11px;color:#5a5044;text-align:center;margin-top:18px;">결제 주문번호: <span style="font-family:Menlo,monospace;">${orderId}</span></div>
    </div>
    ${FOOTER_HTML()}
  </div>
</body></html>`;
}

function buildD14Text({ customerName, skuName, orderId }) {
  return [
    '천명당 (天命堂) — 결제 2주일 / 매일 새 운세',
    '',
    `${customerName ? customerName + '님, ' : ''}14일 전 ${skuName}을 결제해 주셨습니다.`,
    '한 번의 풀이는 큰 그림이지만, 매일의 작은 선택은 그날의 운세에 달려있습니다.',
    '',
    '─── 두 가지 길 ───',
    '[1] 월회원권 — ₩29,900 / 월',
    '· 매일 아침 8시 오늘의 운세 카톡',
    '· 사주 정밀 + 궁합 무제한 풀이',
    '· 3일 무료 후 자동결제 (3일 안에 해지하면 ₩0)',
    '시작하기: https://cheonmyeongdang.vercel.app/pay.html?sku=subscribe_monthly_29900&utm_source=email_d14&utm_campaign=upsell_monthly_or_sinnyeon',
    '',
    '[2] 신년운세 — ₩15,000 (단건)',
    '· 12개월 월별 운세 + 신살 연간 리포트',
    '· 매월 어떤 일이 다가오는지 미리 1년치 캘린더',
    '바로가기: https://cheonmyeongdang.vercel.app/pay.html?sku=sinnyeon_15000&utm_source=email_d14&utm_campaign=upsell_monthly_or_sinnyeon',
    '',
    '─── 결제 후 2주 자주 묻는 질문 ───',
    'Q. 풀이가 잘 맞지 않는 것 같아요',
    'A. 대운 전환 나이 ±2년은 풀이와 다르게 느껴질 수 있습니다.',
    'Q. 매일 운세는?',
    'A. 월회원권 카톡 운세 (일진 기반).',
    'Q. 가족·연인 풀이는?',
    'A. 궁합 ₩9,900 또는 월회원권 무제한.',
    '',
    '카카오톡 채널 친구추가: http://pf.kakao.com/_xnxnxnK',
    '',
    `결제 주문번호: ${orderId}`,
    '',
    '쿤스튜디오 · 대표 홍덕훈 · 사업자등록번호 552-59-00848',
    '문의: ghdejr11@gmail.com',
  ].join('\n');
}

// ─── D+30 Winback (SKU별 분기 + 30% 쿠폰) 메일 빌더 ───
//
// 분기 (skuId 기반):
//   saju_premium_9900       → 종합 풀이 (사주+궁합+신년운세) 권유
//   compat_detail_9900      → 종합 풀이 (다른 사람 궁합도 한 번에) 권유
//   comprehensive_29900     → 월회원권 (매월 갱신) 권유
//   sinnyeon_15000          → 월회원권 (월별 자세한 풀이) 권유
//   ai_chatbot_pack_4900    → 월회원권 (AI 챗봇 무제한) 권유
//   no_ads_9900             → 베이직 구독 (광고제거+카톡운세) 권유
//   subscribe_basic_2900    → 월회원권 프리미엄 업그레이드
//   기본값                   → 종합 풀이
//
// 정기결제 자동 갱신자(subscription)는 listFollowupTargets에서 자동 제외됨 (purchase-store.js:213)
//
// 만족도 설문: Tally / Google Forms 무료 양식 (현재 비워둠 — UTM 링크만 살아있으면 OK)
//
// 면책: "재미·교양 목적 / 의료·법률·금융 결정에는 전문가 상담 필요"
const D30_OFFER_MAP = {
  saju_premium_9900: {
    target_sku: 'comprehensive_29900',
    target_name: '종합 풀이',
    target_price: 29900,
    headline: '30일 더 깊은 풀이 — 종합 풀이로 사주·궁합·신년운세 한 번에',
    why: '사주 정밀 풀이를 본 분들이 가장 많이 다음에 찾으시는 것이 <strong>궁합과 1년치 흐름</strong>입니다. 단건 합산 ₩34,800 → ₩29,900.',
    why_text: '사주 정밀 후 다음 단계: 궁합 + 1년치 흐름. 단건 합산 ₩34,800 → 종합 ₩29,900.',
    cta: '종합 풀이 30% 할인 받기',
  },
  compat_detail_9900: {
    target_sku: 'comprehensive_29900',
    target_name: '종합 풀이',
    target_price: 29900,
    headline: '다른 사람과의 궁합도? — 종합 풀이로 사주+궁합+신년운세 한 번에',
    why: '한 사람과의 궁합을 보신 후, 본인의 사주 정밀과 1년 흐름까지 합쳐서 보면 <strong>왜 이 관계가 잘 맞는지</strong> 명확해집니다.',
    why_text: '궁합 1건 본 후 다음 단계: 본인 사주 정밀 + 신년운세 1년치. 단건 합산 ₩34,800 → 종합 ₩29,900.',
    cta: '종합 풀이 30% 할인 받기',
  },
  comprehensive_29900: {
    target_sku: 'subscribe_monthly_29900',
    target_name: '월회원권 (프리미엄)',
    target_price: 29900,
    headline: '월 1회 갱신 — 월회원권으로 매일 새 운세',
    why: '종합 풀이는 한 시점의 큰 그림입니다. <strong>매일의 작은 결정</strong>은 그날그날의 일진이 결정합니다. 월회원권으로 매일 아침 8시 카톡 운세 + 무제한 풀이.',
    why_text: '종합 풀이 = 한 시점의 큰 그림 / 매일의 결정 = 일진. 월회원으로 매일 8시 카톡 + 무제한 풀이.',
    cta: '월회원권 30% 할인 시작',
  },
  sinnyeon_15000: {
    target_sku: 'subscribe_monthly_29900',
    target_name: '월회원권 (프리미엄)',
    target_price: 29900,
    headline: '월별 자세한 풀이 — 월회원권으로 12개월을 12번 다시 보기',
    why: '신년운세는 1년치 큰 흐름입니다. 매월 갱신되는 <strong>그달의 일진·세운·신살</strong>까지 받으시려면 월회원권을 권합니다.',
    why_text: '신년운세 = 연간 흐름 / 매월 일진·세운·신살 = 월회원. 매일 아침 8시 카톡 운세 + 무제한 풀이.',
    cta: '월회원권 30% 할인 시작',
  },
  ai_chatbot_pack_4900: {
    target_sku: 'subscribe_monthly_29900',
    target_name: '월회원권 (프리미엄)',
    target_price: 29900,
    headline: 'AI 챗봇 무제한 — 월회원권으로 모든 질문에 즉답',
    why: '30회 챗봇을 쓰신 분들이 가장 많이 묻는 후속 질문은 "더 자세히 / 다음 결정 / 다른 상황"입니다. 월회원으로 <strong>무제한 + 사주·궁합 풀이까지 포함</strong>.',
    why_text: '챗봇 30회 사용 후 다음 단계: 무제한 + 사주·궁합·매일 운세까지 포함. 월 ₩29,900.',
    cta: '월회원권 30% 할인 시작',
  },
  no_ads_9900: {
    target_sku: 'subscribe_basic_2900',
    target_name: '베이직 구독 (월)',
    target_price: 2900,
    headline: '광고 제거 + 매일 카톡 운세 — 베이직 구독으로 한 단계 더',
    why: '광고 없는 환경에 익숙해지셨다면, 다음은 <strong>매일 아침 8시 카톡 운세 + 꿈해몽 무제한</strong>입니다. 월 ₩2,900으로 가볍게.',
    why_text: '광고 제거 다음 단계: 매일 카톡 운세 + 꿈해몽 무제한. 월 ₩2,900.',
    cta: '베이직 구독 30% 할인 시작',
  },
  subscribe_basic_2900: {
    target_sku: 'subscribe_monthly_29900',
    target_name: '월회원권 (프리미엄)',
    target_price: 29900,
    headline: '베이직 → 프리미엄 — 사주·궁합·AI 챗봇까지',
    why: '베이직(꿈해몽 무제한 + 카톡 운세)에 만족하셨다면, 프리미엄은 <strong>사주 정밀 + 궁합 + AI 챗봇 무제한</strong>까지 추가됩니다.',
    why_text: '베이직 → 프리미엄: 사주·궁합·AI 챗봇 무제한 추가. 월 ₩29,900.',
    cta: '프리미엄 업그레이드 30% 할인',
  },
};

function getD30Offer(skuId) {
  return D30_OFFER_MAP[skuId] || D30_OFFER_MAP.saju_premium_9900;
}

function buildD30Html({ customerName, skuName, skuId, orderId, couponCode, validUntil }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';
  const offer = getD30Offer(skuId);
  const code = couponCode || 'WB30-XXXX';
  const validStr = validUntil || '';
  const discountedPrice = Math.floor(offer.target_price * 0.7);
  const savings = offer.target_price - discountedPrice;
  const payUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=${offer.target_sku}&coupon=${code}&utm_source=email_d30&utm_campaign=winback_d30&utm_content=${skuId || 'unknown'}`;
  const surveyUrl = `https://cheonmyeongdang.vercel.app/support.html?from=winback_d30&order=${encodeURIComponent(orderId)}#feedback`;

  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>천명당 — 30일 윈백 (30% 할인 쿠폰)</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:42px;margin-bottom:8px;">🎁</div>
        <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px;font-weight:700;">${greet}<br>30일 — 어떻게 지내셨나요?</h1>
        <p style="color:#e8e0d0;font-size:15px;line-height:1.7;margin:8px 0 0;">30일 전 <strong style="color:#e8c97a;">${skuName}</strong>을 받아보셨습니다.<br>오늘은 감사의 의미로 <strong style="color:#e8c97a;">30% 할인 쿠폰</strong>을 보내드립니다.</p>
      </div>

      <!-- 30% 쿠폰 박스 -->
      <div style="background:linear-gradient(135deg,#3a1a30,#2a0f25);border:2px dashed #e8c97a;border-radius:14px;padding:22px 18px;margin:18px 0;text-align:center;">
        <div style="font-size:12px;color:#e8c97a;letter-spacing:0.18em;font-weight:800;margin-bottom:6px;">⭐ WINBACK COUPON · 30% OFF</div>
        <h2 style="color:#fff5d9;font-size:32px;margin:8px 0;font-family:'Gowun Batang',serif;font-weight:700;">30% 할인</h2>
        <p style="color:#e8e0d0;font-size:13px;margin:8px 0 14px;line-height:1.6;">${offer.target_name} <span style="text-decoration:line-through;color:#a89880;">₩${offer.target_price.toLocaleString('ko-KR')}</span> → <strong style="color:#e8c97a;font-size:18px;">₩${discountedPrice.toLocaleString('ko-KR')}</strong> <span style="color:#6dbfa8;">(${savings.toLocaleString('ko-KR')}원 절약)</span></p>
        <div style="background:rgba(0,0,0,0.5);padding:12px 20px;border-radius:8px;display:inline-block;font-family:Menlo,monospace;color:#e8c97a;font-size:18px;letter-spacing:0.15em;font-weight:700;">${code}</div>
        <p style="color:#a89880;font-size:11px;margin-top:10px;line-height:1.5;">* 결제 페이지 쿠폰 코드 입력 · 1회용 · ${validStr ? validStr + '까지 유효' : '발급 후 7일 이내 사용'}</p>
      </div>

      <!-- 왜 이 오퍼? -->
      <div style="background:rgba(0,0,0,0.3);border-radius:10px;padding:18px;margin:18px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;">왜 ${offer.target_name}을 권하나요?</div>
        <p style="color:#e8e0d0;font-size:14px;line-height:1.8;margin:0;">${offer.why}</p>
      </div>

      <!-- CTA -->
      <div style="text-align:center;margin:24px 0;">
        <a href="${payUrl}" style="display:inline-block;padding:16px 40px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:10px;font-size:16px;letter-spacing:0.05em;">${offer.cta} →</a>
        <div style="font-size:11px;color:#7a6f5a;margin-top:10px;">* 쿠폰 자동 적용 링크 · 결제 시 ${code} 자동 입력</div>
      </div>

      <!-- Cross-sell: 인스타/유튜브 -->
      <div style="background:rgba(254,229,0,0.05);border:1px solid rgba(201,168,76,0.25);border-radius:10px;padding:16px 18px;margin:18px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;">매일 무료 콘텐츠로 만나요</div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;">
          <a href="https://www.instagram.com/cheonmyeongdang/?utm_source=email_d30" style="flex:1;min-width:140px;padding:10px 16px;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);color:#fff;text-decoration:none;border-radius:8px;font-size:13px;font-weight:700;text-align:center;">📸 인스타그램</a>
          <a href="https://www.youtube.com/@cheonmyeongdang?utm_source=email_d30" style="flex:1;min-width:140px;padding:10px 16px;background:#ff0000;color:#fff;text-decoration:none;border-radius:8px;font-size:13px;font-weight:700;text-align:center;">▶ 유튜브</a>
        </div>
        <p style="color:#a89880;font-size:11px;margin:10px 0 0;text-align:center;line-height:1.5;">매일 오늘의 운세 · 사주 상식 · 신살 해설</p>
      </div>

      <!-- 만족도 설문 -->
      <div style="text-align:center;margin:18px 0 8px;">
        <a href="${surveyUrl}" style="color:#a89880;font-size:12px;text-decoration:underline;">📋 30초 만족도 설문에 참여하시면 추가 혜택</a>
      </div>

      <!-- 면책 -->
      <div style="background:rgba(0,0,0,0.25);border-radius:8px;padding:12px;margin:14px 0;">
        <p style="color:#7a6f5a;font-size:10px;line-height:1.7;margin:0;">⚠ <strong>면책 조항:</strong> 천명당 풀이는 명리학·통계 기반의 <strong>재미·교양 목적</strong> 콘텐츠입니다. 의료·법률·금융 등 중요한 결정은 반드시 해당 분야 전문가와 상담하시기 바랍니다.</p>
      </div>

      <p style="color:#5a5044;font-size:11px;text-align:center;margin-top:14px;">결제 주문번호: <span style="font-family:Menlo,monospace;">${orderId}</span></p>
    </div>
    ${FOOTER_HTML()}
  </div>
</body></html>`;
}

function buildD30Text({ customerName, skuName, skuId, orderId, couponCode, validUntil }) {
  const greet = customerName ? `${customerName}님,` : '안녕하세요,';
  const offer = getD30Offer(skuId);
  const code = couponCode || 'WB30-XXXX';
  const discountedPrice = Math.floor(offer.target_price * 0.7);
  const savings = offer.target_price - discountedPrice;
  const payUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=${offer.target_sku}&coupon=${code}&utm_source=email_d30&utm_campaign=winback_d30&utm_content=${skuId || 'unknown'}`;

  return [
    '천명당 (天命堂) — 30일 윈백 (30% 할인 쿠폰)',
    '',
    `${greet}`,
    `30일 전 ${skuName}을 받아보셨습니다. 감사의 의미로 30% 할인 쿠폰을 보내드립니다.`,
    '',
    '─── ⭐ WINBACK COUPON · 30% OFF ───',
    `· ${offer.target_name}: ₩${offer.target_price.toLocaleString('ko-KR')} → ₩${discountedPrice.toLocaleString('ko-KR')} (${savings.toLocaleString('ko-KR')}원 절약)`,
    `· 쿠폰 코드: ${code}`,
    `· 1회용 · ${validUntil ? validUntil + '까지' : '발급 후 7일 이내'} 사용 가능`,
    '',
    `왜 ${offer.target_name}을 권하나요?`,
    `· ${offer.why_text}`,
    '',
    `${offer.cta}: ${payUrl}`,
    '',
    '─── 매일 무료 콘텐츠 ───',
    '· 인스타: https://www.instagram.com/cheonmyeongdang/?utm_source=email_d30',
    '· 유튜브: https://www.youtube.com/@cheonmyeongdang?utm_source=email_d30',
    '',
    '※ 면책: 천명당 풀이는 명리학·통계 기반 재미·교양 목적 콘텐츠입니다.',
    '   의료·법률·금융 등 중요 결정은 해당 분야 전문가와 상담하세요.',
    '',
    `주문번호: ${orderId}`,
    '쿤스튜디오 · 사업자등록번호 552-59-00848 · ghdejr11@gmail.com',
  ].join('\n');
}

// ─────────────────────────────────────────────────────────────────────────
// ─── 5월 시즌 D+30 메일 — 어버이날 ───
// ─────────────────────────────────────────────────────────────────────────
// 일반 D+30 winback 쿠폰(WB30-XXXX, 30%)은 그대로 유지하고, 본문 상단에 어버이날 시즌 후크
// 추가. 결제 LP는 /eobonal (MD 전용 LP) cross-link, KDP "어버이날 감사 편지 100선" cross-link.
function buildD30EobonalHtml({ customerName, skuName, skuId, orderId, couponCode, validUntil }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';
  const code = couponCode || 'WB30-XXXX';
  const validStr = validUntil || '';
  const offer = getD30Offer(skuId);
  const discountedPrice = Math.floor(offer.target_price * 0.7);
  const savings = offer.target_price - discountedPrice;
  const payUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=${offer.target_sku}&coupon=${code}&utm_source=email_d30&utm_campaign=winback_d30_eobonal&utm_content=${skuId || 'unknown'}`;
  const eobonalLpUrl = `https://cheonmyeongdang.vercel.app/eobonal?utm_source=email_d30&utm_campaign=eobonal_2026`;
  const eobonalSajuUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=saju_premium_9900&utm_source=email_d30&utm_campaign=eobonal_2026&utm_content=parents_saju_free_after_pay`;
  const kdpUrl = `https://www.amazon.com/dp/eobonal-letter-100`;
  const kdpKrUrl = `https://www.amazon.com/dp/eobonal-letter-100?tag=cheonmyeongdang-22&utm_source=email_d30`;
  const dDay = daysUntil('2026-05-08');
  const dDayLabel = dDay === 0 ? '오늘' : `D-${dDay}`;

  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>천명당 — 어버이날 ${dDayLabel} · 부모님 사주 풀이 + 카드 5종</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>

    <!-- 시즌 후크 박스 — 어버이날 -->
    <div style="background:linear-gradient(135deg,#3a1a2e,#2a0f1f);border:2px solid #ff7b9c;border-radius:16px;padding:24px;margin-bottom:18px;text-align:center;">
      <div style="font-size:42px;margin-bottom:6px;">🌷</div>
      <div style="font-size:11px;color:#ff7b9c;letter-spacing:0.18em;font-weight:800;margin-bottom:8px;">어버이날 ${dDayLabel} · 5월 8일</div>
      <h1 style="font-family:'Gowun Batang',serif;color:#ffd6e0;font-size:22px;margin:6px 0 12px;font-weight:700;">${greet}<br>부모님 사주 풀이 + 카네이션 카드 5종</h1>
      <p style="color:#e8e0d0;font-size:14px;line-height:1.7;margin:8px 0 16px;">올해 어버이날, 부모님께 평생 한 번 받아볼<br><strong style="color:#ffd6e0;">사주 정밀 풀이</strong>를 선물로 보내드릴 수 있어요.</p>
      <a href="${eobonalLpUrl}" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#ff7b9c,#ffaec0);color:#080a10;font-weight:800;text-decoration:none;border-radius:10px;font-size:15px;">어버이날 페이지 보기 →</a>
      <p style="color:#a89880;font-size:11px;margin-top:10px;line-height:1.5;">* 결제 후 즉시 PDF 발송 · 부모님 생년월시만 입력</p>
    </div>

    <!-- 카네이션 카드 5종 무료 다운로드 -->
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid rgba(255,123,156,0.3);border-radius:14px;padding:22px;margin-bottom:18px;">
      <div style="font-size:11px;color:#ff7b9c;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;text-align:center;">🎁 무료 선물</div>
      <h2 style="font-family:'Gowun Batang',serif;color:#ffd6e0;font-size:18px;margin:0 0 12px;font-weight:700;text-align:center;">카네이션 카드 PDF 5종</h2>
      <p style="color:#e8e0d0;font-size:13px;line-height:1.7;margin:0 0 14px;text-align:center;">손글씨 폰트 5종 + 인쇄용 A4 / 모바일용 정사각형. 어버이날 LP에서 이메일 입력 시 즉시 다운로드.</p>
      <div style="text-align:center;">
        <a href="${eobonalLpUrl}#freebies" style="display:inline-block;padding:10px 24px;background:transparent;color:#ffd6e0;border:1px solid #ff7b9c;text-decoration:none;border-radius:8px;font-size:13px;font-weight:700;">카드 5종 받기</a>
      </div>
    </div>

    <!-- KDP cross-link -->
    <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(201,168,76,0.2);border-radius:10px;padding:16px 18px;margin-bottom:18px;">
      <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:8px;">📖 함께 읽으면 좋은 책</div>
      <p style="color:#e8e0d0;font-size:13px;line-height:1.7;margin:0 0 8px;"><strong style="color:#e8c97a;">"어버이날 감사 편지 100선"</strong> — 짧은 글이라도 부모님 마음에 와닿는 100가지 표현 모음</p>
      <a href="${kdpUrl}" style="color:#c9a84c;font-size:12px;text-decoration:underline;" target="_blank" rel="noopener">Amazon Kindle (English)</a> ·
      <a href="${kdpKrUrl}" style="color:#c9a84c;font-size:12px;text-decoration:underline;" target="_blank" rel="noopener">Amazon (한국어판)</a>
    </div>

    <!-- 일반 D+30 winback 쿠폰 (그대로 유지) -->
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:28px 22px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:18px;">
        <div style="font-size:32px;margin-bottom:6px;">🎁</div>
        <h2 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:18px;margin:0 0 8px;font-weight:700;">본인용 — 30일 윈백 30% 쿠폰</h2>
        <p style="color:#a89880;font-size:13px;line-height:1.6;margin:0;">30일 전 <strong style="color:#e8c97a;">${skuName}</strong>을 받아보셨습니다. 부모님 선물과 별개로, 본인용 쿠폰도 함께 보내드립니다.</p>
      </div>
      <div style="background:linear-gradient(135deg,#1a3530,#102520);border:2px dashed #e8c97a;border-radius:12px;padding:18px;text-align:center;">
        <div style="font-size:11px;color:#e8c97a;letter-spacing:0.18em;font-weight:800;margin-bottom:4px;">⭐ WINBACK · 30% OFF</div>
        <p style="color:#e8e0d0;font-size:13px;margin:8px 0 12px;">${offer.target_name} <span style="text-decoration:line-through;color:#a89880;">₩${offer.target_price.toLocaleString('ko-KR')}</span> → <strong style="color:#e8c97a;">₩${discountedPrice.toLocaleString('ko-KR')}</strong></p>
        <div style="background:rgba(0,0,0,0.5);padding:10px 18px;border-radius:6px;display:inline-block;font-family:Menlo,monospace;color:#e8c97a;font-size:16px;letter-spacing:0.12em;font-weight:700;">${code}</div>
        <p style="color:#a89880;font-size:11px;margin-top:8px;">${validStr ? validStr + '까지 유효' : '발급 후 7일 이내'}</p>
      </div>
      <div style="text-align:center;margin-top:14px;">
        <a href="${payUrl}" style="display:inline-block;padding:12px 28px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:8px;font-size:14px;">${offer.cta} →</a>
      </div>
    </div>

    <!-- 면책 -->
    <div style="background:rgba(0,0,0,0.25);border-radius:8px;padding:12px;margin:14px 0;">
      <p style="color:#7a6f5a;font-size:10px;line-height:1.7;margin:0;">⚠ <strong>면책:</strong> 천명당 풀이는 명리학·통계 기반의 <strong>재미·교양 목적</strong> 콘텐츠입니다. 의료·법률·금융 결정은 해당 분야 전문가와 상담하세요.</p>
    </div>

    <p style="color:#5a5044;font-size:11px;text-align:center;margin-top:14px;">결제 주문번호: <span style="font-family:Menlo,monospace;">${orderId}</span></p>
    ${FOOTER_HTML()}
  </div>
</body></html>`;
}

function buildD30EobonalText({ customerName, skuName, skuId, orderId, couponCode, validUntil }) {
  const greet = customerName ? `${customerName}님,` : '안녕하세요,';
  const code = couponCode || 'WB30-XXXX';
  const offer = getD30Offer(skuId);
  const discountedPrice = Math.floor(offer.target_price * 0.7);
  const savings = offer.target_price - discountedPrice;
  const payUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=${offer.target_sku}&coupon=${code}&utm_source=email_d30&utm_campaign=winback_d30_eobonal`;
  const eobonalLpUrl = `https://cheonmyeongdang.vercel.app/eobonal?utm_source=email_d30&utm_campaign=eobonal_2026`;
  const dDay = daysUntil('2026-05-08');
  const dDayLabel = dDay === 0 ? '오늘' : `D-${dDay}`;

  return [
    `천명당 (天命堂) — 어버이날 ${dDayLabel} · 부모님 사주 풀이 + 카드 5종`,
    '',
    greet,
    `5월 8일 어버이날까지 ${dDayLabel}. 부모님께 사주 정밀 풀이를 선물로 보낼 수 있는 페이지를 안내드립니다.`,
    '',
    '─── 🌷 어버이날 페이지 ───',
    `· 부모님 사주 풀이 (생년월시만 입력 → PDF 즉시 발송)`,
    `· 카네이션 카드 PDF 5종 무료 다운로드`,
    `· 페이지: ${eobonalLpUrl}`,
    '',
    '─── 📖 함께 읽으면 좋은 책 ───',
    '· "어버이날 감사 편지 100선" (Amazon Kindle / 한국어판)',
    '· https://www.amazon.com/dp/eobonal-letter-100',
    '',
    '─── ⭐ 본인용 — 30일 윈백 30% 쿠폰 ───',
    `· ${offer.target_name}: ₩${offer.target_price.toLocaleString('ko-KR')} → ₩${discountedPrice.toLocaleString('ko-KR')}`,
    `· 쿠폰 코드: ${code} (${validUntil ? validUntil + '까지' : '7일 이내'})`,
    `· 적용 결제: ${payUrl}`,
    '',
    '※ 면책: 천명당 풀이는 명리학·통계 기반 재미·교양 콘텐츠입니다.',
    '   의료·법률·금융 결정은 해당 분야 전문가와 상담하세요.',
    '',
    `주문번호: ${orderId}`,
    '쿤스튜디오 · 사업자등록번호 552-59-00848 · ghdejr11@gmail.com',
  ].join('\n');
}

// ─────────────────────────────────────────────────────────────────────────
// ─── 5월 시즌 D+30 메일 — 종소세 환급 ───
// ─────────────────────────────────────────────────────────────────────────
// 환급 평균액은 국세청 공식 통계 (2024년 종합소득세 신고 환급 평균 약 ₩48만원, 출처: 국세청).
// 광고 카피 "세무사 대체" / "100% 환급" / "강요" 금지 → "참고 자료, 정확한 신고는 홈택스/세무사" 면책.
function buildD30JongsoseHtml({ customerName, skuName, skuId, orderId, couponCode, validUntil }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';
  const code = couponCode || 'WB30-XXXX';
  const validStr = validUntil || '';
  const offer = getD30Offer(skuId);
  const discountedPrice = Math.floor(offer.target_price * 0.7);
  const payUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=${offer.target_sku}&coupon=${code}&utm_source=email_d30&utm_campaign=winback_d30_jongsose&utm_content=${skuId || 'unknown'}`;
  const jongsoseLpUrl = `https://cheonmyeongdang.vercel.app/jongsose?utm_source=email_d30&utm_campaign=jongsose_2026`;
  const jongsoseSkuUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=jongsose_checklist_9900&utm_source=email_d30&utm_campaign=jongsose_2026`;
  const kdpUrl = `https://www.amazon.com/dp/jongsose-self-guide`;
  const dDay = daysUntil('2026-05-31');
  const dDayLabel = dDay === 0 ? '오늘 마감' : `D-${dDay}`;

  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>천명당 — 종소세 ${dDayLabel} · 셀프 신고 12분 가이드</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>

    <!-- 시즌 후크 박스 — 종소세 -->
    <div style="background:linear-gradient(135deg,#1a2e3a,#0f1f2a);border:2px solid #6dbfe8;border-radius:16px;padding:24px;margin-bottom:18px;text-align:center;">
      <div style="font-size:42px;margin-bottom:6px;">📋</div>
      <div style="font-size:11px;color:#6dbfe8;letter-spacing:0.18em;font-weight:800;margin-bottom:8px;">종소세 신고 ${dDayLabel} · 5월 31일 마감</div>
      <h1 style="font-family:'Gowun Batang',serif;color:#d6ecff;font-size:22px;margin:6px 0 12px;font-weight:700;">${greet}<br>종소세 셀프 신고 12분 가이드</h1>
      <p style="color:#e8e0d0;font-size:14px;line-height:1.7;margin:8px 0 8px;">2024년 종합소득세 신고 평균 환급액은 <strong style="color:#d6ecff;">약 ₩48만원</strong> 수준입니다.<br><span style="color:#a89880;font-size:12px;">(출처: 국세청 2024년 종합소득세 신고 통계)</span></p>
      <p style="color:#e8e0d0;font-size:14px;line-height:1.7;margin:14px 0 16px;">홈택스 화면을 따라가는 <strong style="color:#d6ecff;">12분 셀프 신고 체크리스트</strong>로 누락 항목을 점검할 수 있습니다.</p>
      <a href="${jongsoseLpUrl}" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#6dbfe8,#a8d8f0);color:#080a10;font-weight:800;text-decoration:none;border-radius:10px;font-size:15px;">셀프 신고 가이드 보기 →</a>
      <p style="color:#a89880;font-size:11px;margin-top:10px;line-height:1.5;">* 참고 자료 · 정확한 신고는 홈택스 또는 세무사 상담을 권장합니다</p>
    </div>

    <!-- 종소세 SKU 9900 -->
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid rgba(109,191,232,0.3);border-radius:14px;padding:22px;margin-bottom:18px;">
      <div style="font-size:11px;color:#6dbfe8;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;text-align:center;">📋 셀프 신고 체크리스트</div>
      <h2 style="font-family:'Gowun Batang',serif;color:#d6ecff;font-size:18px;margin:0 0 12px;font-weight:700;text-align:center;">종소세 신고 체크리스트 ₩9,900</h2>
      <ul style="color:#e8e0d0;font-size:13px;line-height:1.8;padding-left:20px;margin:0 0 14px;">
        <li>홈택스 화면별 입력 순서 PDF (12장)</li>
        <li>업종별 누락 빈도 TOP 10 항목</li>
        <li>경비 인정 한도표 (프리랜서·사업자별)</li>
        <li>가산세·납부 일정 캘린더</li>
      </ul>
      <div style="text-align:center;">
        <a href="${jongsoseSkuUrl}" style="display:inline-block;padding:10px 24px;background:transparent;color:#d6ecff;border:1px solid #6dbfe8;text-decoration:none;border-radius:8px;font-size:13px;font-weight:700;">체크리스트 받기</a>
      </div>
    </div>

    <!-- KDP cross-link -->
    <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(201,168,76,0.2);border-radius:10px;padding:16px 18px;margin-bottom:18px;">
      <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:8px;">📖 함께 읽으면 좋은 책</div>
      <p style="color:#e8e0d0;font-size:13px;line-height:1.7;margin:0 0 8px;"><strong style="color:#e8c97a;">"종소세 셀프 신고 가이드"</strong> — 프리랜서·1인 사업자가 자주 놓치는 항목 정리</p>
      <a href="${kdpUrl}" style="color:#c9a84c;font-size:12px;text-decoration:underline;" target="_blank" rel="noopener">Amazon Kindle 보기</a>
    </div>

    <!-- 일반 D+30 winback 쿠폰 (그대로 유지) -->
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:28px 22px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:18px;">
        <div style="font-size:32px;margin-bottom:6px;">🎁</div>
        <h2 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:18px;margin:0 0 8px;font-weight:700;">사주 — 30일 윈백 30% 쿠폰</h2>
        <p style="color:#a89880;font-size:13px;line-height:1.6;margin:0;">30일 전 <strong style="color:#e8c97a;">${skuName}</strong>을 받아보셨습니다. 종소세 시즌과 별개로, 사주 풀이 30% 쿠폰도 함께 보내드립니다.</p>
      </div>
      <div style="background:linear-gradient(135deg,#1a3530,#102520);border:2px dashed #e8c97a;border-radius:12px;padding:18px;text-align:center;">
        <div style="font-size:11px;color:#e8c97a;letter-spacing:0.18em;font-weight:800;margin-bottom:4px;">⭐ WINBACK · 30% OFF</div>
        <p style="color:#e8e0d0;font-size:13px;margin:8px 0 12px;">${offer.target_name} <span style="text-decoration:line-through;color:#a89880;">₩${offer.target_price.toLocaleString('ko-KR')}</span> → <strong style="color:#e8c97a;">₩${discountedPrice.toLocaleString('ko-KR')}</strong></p>
        <div style="background:rgba(0,0,0,0.5);padding:10px 18px;border-radius:6px;display:inline-block;font-family:Menlo,monospace;color:#e8c97a;font-size:16px;letter-spacing:0.12em;font-weight:700;">${code}</div>
        <p style="color:#a89880;font-size:11px;margin-top:8px;">${validStr ? validStr + '까지 유효' : '발급 후 7일 이내'}</p>
      </div>
      <div style="text-align:center;margin-top:14px;">
        <a href="${payUrl}" style="display:inline-block;padding:12px 28px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:8px;font-size:14px;">${offer.cta} →</a>
      </div>
    </div>

    <!-- 면책 (세무사법) -->
    <div style="background:rgba(0,0,0,0.25);border-radius:8px;padding:14px;margin:14px 0;">
      <p style="color:#7a6f5a;font-size:10px;line-height:1.7;margin:0;">⚠ <strong>면책:</strong> 본 메일·체크리스트·가이드는 <strong>참고 자료</strong>로 제공되며, 개별 신고에 대한 세무 자문이 아닙니다. 정확한 신고는 <strong>국세청 홈택스</strong> 또는 <strong>세무사</strong> 상담을 권장합니다. 천명당 풀이는 명리학·통계 기반 재미·교양 콘텐츠입니다.</p>
    </div>

    <p style="color:#5a5044;font-size:11px;text-align:center;margin-top:14px;">결제 주문번호: <span style="font-family:Menlo,monospace;">${orderId}</span></p>
    ${FOOTER_HTML()}
  </div>
</body></html>`;
}

function buildD30JongsoseText({ customerName, skuName, skuId, orderId, couponCode, validUntil }) {
  const greet = customerName ? `${customerName}님,` : '안녕하세요,';
  const code = couponCode || 'WB30-XXXX';
  const offer = getD30Offer(skuId);
  const discountedPrice = Math.floor(offer.target_price * 0.7);
  const payUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=${offer.target_sku}&coupon=${code}&utm_source=email_d30&utm_campaign=winback_d30_jongsose`;
  const jongsoseLpUrl = `https://cheonmyeongdang.vercel.app/jongsose?utm_source=email_d30&utm_campaign=jongsose_2026`;
  const dDay = daysUntil('2026-05-31');
  const dDayLabel = dDay === 0 ? '오늘 마감' : `D-${dDay}`;

  return [
    `천명당 (天命堂) — 종소세 ${dDayLabel} · 셀프 신고 12분 가이드`,
    '',
    greet,
    `5월 31일 종합소득세 신고 마감까지 ${dDayLabel}.`,
    '',
    '─── 📋 종소세 시즌 안내 ───',
    '· 2024년 종합소득세 신고 평균 환급액 약 ₩48만원 (출처: 국세청)',
    '· 홈택스 화면별 입력 순서 12분 셀프 신고 체크리스트',
    `· 페이지: ${jongsoseLpUrl}`,
    '',
    '─── 📖 함께 읽으면 좋은 책 ───',
    '· "종소세 셀프 신고 가이드" (Amazon Kindle)',
    '· https://www.amazon.com/dp/jongsose-self-guide',
    '',
    '─── ⭐ 사주 — 30일 윈백 30% 쿠폰 ───',
    `· ${offer.target_name}: ₩${offer.target_price.toLocaleString('ko-KR')} → ₩${discountedPrice.toLocaleString('ko-KR')}`,
    `· 쿠폰 코드: ${code} (${validUntil ? validUntil + '까지' : '7일 이내'})`,
    `· 적용 결제: ${payUrl}`,
    '',
    '※ 면책: 본 메일·가이드는 참고 자료이며, 개별 신고에 대한 세무 자문이 아닙니다.',
    '   정확한 신고는 국세청 홈택스 또는 세무사 상담을 권장합니다.',
    '   천명당 풀이는 명리학·통계 기반 재미·교양 콘텐츠입니다.',
    '',
    `주문번호: ${orderId}`,
    '쿤스튜디오 · 사업자등록번호 552-59-00848 · ghdejr11@gmail.com',
  ].join('\n');
}

// ─── D+90 (장기 휴면 win-back) — 50% 할인 + 마지막 안내 ───
function buildD90Html({ customerName, skuName, orderId, couponCode, validUntil }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';
  const code = couponCode || 'WB90-XXXX';
  const validStr = validUntil || '';
  // D+90은 종합 풀이 50% 고정 (장기 휴면자 강한 후크)
  const target_sku = 'comprehensive_29900';
  const target_name = '종합 풀이';
  const target_price = 29900;
  const discountedPrice = Math.floor(target_price * 0.5);
  const savings = target_price - discountedPrice;
  const payUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=${target_sku}&coupon=${code}&utm_source=email_d90&utm_campaign=winback_d90`;
  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>천명당 — 90일 윈백 (50% 할인)</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:42px;margin-bottom:8px;">💝</div>
        <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px;font-weight:700;">${greet}<br>3개월 — 다시 한 번 인연을 잇고 싶어서</h1>
        <p style="color:#e8e0d0;font-size:15px;line-height:1.7;">3개월 전 <strong style="color:#e8c97a;">${skuName}</strong>을 받아보신 후 발길이 뜸하셨습니다.<br><strong style="color:#e8c97a;">마지막 윈백 쿠폰 — 50% 할인</strong>을 보내드립니다.</p>
      </div>
      <div style="background:linear-gradient(135deg,#3a1a30,#2a0f25);border:2px dashed #e8c97a;border-radius:14px;padding:22px 18px;margin:18px 0;text-align:center;">
        <div style="font-size:12px;color:#e8c97a;letter-spacing:0.18em;font-weight:800;margin-bottom:6px;">💝 90일 윈백 · 50% OFF</div>
        <h2 style="color:#fff5d9;font-size:36px;margin:8px 0;font-family:'Gowun Batang',serif;font-weight:700;">반값 할인</h2>
        <p style="color:#e8e0d0;font-size:13px;margin:8px 0 14px;line-height:1.6;">${target_name} <span style="text-decoration:line-through;color:#a89880;">₩${target_price.toLocaleString('ko-KR')}</span> → <strong style="color:#e8c97a;font-size:20px;">₩${discountedPrice.toLocaleString('ko-KR')}</strong> <span style="color:#6dbfa8;">(${savings.toLocaleString('ko-KR')}원 절약)</span></p>
        <div style="background:rgba(0,0,0,0.5);padding:12px 20px;border-radius:8px;display:inline-block;font-family:Menlo,monospace;color:#e8c97a;font-size:18px;letter-spacing:0.15em;font-weight:700;">${code}</div>
        <p style="color:#a89880;font-size:11px;margin-top:10px;line-height:1.5;">* 1회용 · ${validStr ? validStr + '까지 유효' : '발급 후 14일 이내 사용'} · 마지막 윈백 쿠폰</p>
      </div>
      <div style="background:rgba(0,0,0,0.3);border-radius:10px;padding:18px;margin:18px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;">3개월 동안 천명당이 달라진 것</div>
        <ul style="color:#a89880;font-size:14px;line-height:1.8;padding-left:18px;margin:0;">
          <li>AI 사주 챗봇 — "오늘 면접 가도 될까?" 즉답</li>
          <li>매일 아침 8시 카톡 운세 — 본인 사주 일진 기반</li>
          <li>궁합 정밀 — 가족·연인·동료 사주 비교 무제한</li>
          <li>신년운세 — 12개월 월별 + 신살 연간 리포트</li>
        </ul>
      </div>
      <div style="text-align:center;margin:24px 0;">
        <a href="${payUrl}" style="display:inline-block;padding:16px 40px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:10px;font-size:16px;letter-spacing:0.05em;">종합 풀이 50% 할인 받기 →</a>
      </div>
      <div style="background:rgba(0,0,0,0.25);border-radius:8px;padding:12px;margin:14px 0;">
        <p style="color:#7a6f5a;font-size:10px;line-height:1.7;margin:0;">⚠ 천명당 풀이는 재미·교양 목적입니다. 의료·법률·금융 결정은 전문가와 상담하세요.</p>
      </div>
      <p style="color:#5a5044;font-size:11px;text-align:center;margin-top:14px;">결제 주문번호: <span style="font-family:Menlo,monospace;">${orderId}</span></p>
    </div>
    ${FOOTER_HTML()}
  </div>
</body></html>`;
}

function buildD90Text({ customerName, skuName, orderId, couponCode, validUntil }) {
  const greet = customerName ? `${customerName}님,` : '안녕하세요,';
  const code = couponCode || 'WB90-XXXX';
  const target_price = 29900;
  const discountedPrice = Math.floor(target_price * 0.5);
  const savings = target_price - discountedPrice;
  const payUrl = `https://cheonmyeongdang.vercel.app/pay.html?sku=comprehensive_29900&coupon=${code}&utm_source=email_d90&utm_campaign=winback_d90`;
  return [
    '천명당 (天命堂) — 90일 윈백 (50% 할인)',
    '',
    greet,
    `3개월 전 ${skuName}을 받아보셨습니다. 마지막 윈백 — 50% 할인 쿠폰을 보내드립니다.`,
    '',
    '─── 💝 90일 윈백 · 50% OFF ───',
    `· 종합 풀이: ₩${target_price.toLocaleString('ko-KR')} → ₩${discountedPrice.toLocaleString('ko-KR')} (${savings.toLocaleString('ko-KR')}원 절약)`,
    `· 쿠폰 코드: ${code}`,
    `· 1회용 · ${validUntil ? validUntil + '까지' : '발급 후 14일 이내'} 사용`,
    '',
    '─── 3개월 동안 천명당이 달라진 것 ───',
    '· AI 사주 챗봇 (오늘 면접 가도 될까? 즉답)',
    '· 매일 아침 8시 카톡 운세 (본인 일진 기반)',
    '· 궁합 정밀 (가족·연인·동료 비교 무제한)',
    '· 신년운세 (12개월 + 신살 연간 리포트)',
    '',
    `종합 풀이 50% 할인: ${payUrl}`,
    '',
    '※ 면책: 천명당 풀이는 명리학·통계 기반 재미·교양 목적입니다.',
    '   의료·법률·금융 등 중요 결정은 전문가와 상담하세요.',
    '',
    `주문번호: ${orderId}`,
    '쿤스튜디오 · 사업자등록번호 552-59-00848 · ghdejr11@gmail.com',
  ].join('\n');
}

// ─── D+60 (두 달 — 신년운세 시즌 안내) 메일 빌더 ───
function buildD60Html({ customerName, skuName, orderId }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';
  return `<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>천명당 — 두 달 후</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px;font-weight:700;">${greet}<br>두 달 — 재구매 ₩2,000 할인 쿠폰</h1>
      <p style="color:#e8e0d0;font-size:15px;line-height:1.7;">두 달 전 <strong style="color:#e8c97a;">${skuName}</strong> 받아보신 후 잘 지내고 계신가요? 천명당 단골 고객님께 드리는 감사의 쿠폰입니다.</p>
      <div style="background:linear-gradient(135deg,#1a3530,#102520);border:2px dashed #4a9e8e;border-radius:14px;padding:24px;margin:20px 0;text-align:center;">
        <div style="font-size:12px;color:#4a9e8e;letter-spacing:0.18em;font-weight:800;margin-bottom:8px;">RETURNING CUSTOMER COUPON</div>
        <h2 style="color:#6dbfa8;font-size:24px;margin:6px 0;font-family:'Gowun Batang',serif;">₩2,000 할인</h2>
        <p style="color:#e8e0d0;font-size:13px;margin:8px 0 14px;">신년운세 ₩15,000 → ₩13,000<br>종합 풀이 ₩29,900 → ₩27,900</p>
        <div style="background:rgba(0,0,0,0.4);padding:8px 16px;border-radius:6px;display:inline-block;font-family:monospace;color:#e8c97a;font-size:14px;letter-spacing:0.1em;">코드: WELCOME2K</div>
        <p style="color:#7a6f5a;font-size:11px;margin-top:10px;">* 결제 페이지에서 쿠폰 코드 입력 (적용 30일 이내)</p>
      </div>
      <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:20px 0;">
        <a href="https://cheonmyeongdang.vercel.app/pay.html?sku=sinnyeon_15000&coupon=WELCOME2K&utm_source=email_d60&utm_campaign=returning_coupon" style="padding:12px 24px;background:#c9a84c;color:#080a10;font-weight:700;text-decoration:none;border-radius:8px;font-size:14px;">신년운세 보기</a>
        <a href="https://cheonmyeongdang.vercel.app/pay.html?sku=comprehensive_29900&coupon=WELCOME2K&utm_source=email_d60&utm_campaign=returning_coupon" style="padding:12px 24px;background:#4a9e8e;color:#fff;font-weight:700;text-decoration:none;border-radius:8px;font-size:14px;">종합 풀이 보기</a>
      </div>
      <p style="color:#7a6f5a;font-size:11px;text-align:center;margin-top:16px;">* 두 달 전 결제 고객 한정 · 주문번호: ${orderId}</p>
    </div>
    <div style="text-align:center;color:#7a6f5a;font-size:11px;line-height:1.6;padding:12px;">쿤스튜디오 · 사업자등록번호 552-59-00848<br><a href="https://cheonmyeongdang.vercel.app" style="color:#7a6f5a;">cheonmyeongdang.vercel.app</a></div>
  </div></body></html>`;
}
function buildD60Text({ customerName, skuName, orderId }) {
  const greet = customerName ? `${customerName}님,` : '안녕하세요,';
  return [
    greet,
    `두 달 전 ${skuName} 받아보신 후 잘 지내고 계신가요?`,
    '',
    '단골 고객님 감사 쿠폰: ₩2,000 할인',
    '· 신년운세 ₩15,000 → ₩13,000',
    '· 종합 풀이 ₩29,900 → ₩27,900',
    '쿠폰 코드: WELCOME2K (30일 이내 결제 페이지에서 적용)',
    '',
    `신년운세: https://cheonmyeongdang.vercel.app/pay.html?sku=sinnyeon_15000&coupon=WELCOME2K&utm_source=email_d60`,
    `종합 풀이: https://cheonmyeongdang.vercel.app/pay.html?sku=comprehensive_29900&coupon=WELCOME2K&utm_source=email_d60`,
    '',
    `주문번호: ${orderId}`,
    '쿤스튜디오 · 사업자등록번호 552-59-00848 · ghdejr11@gmail.com',
  ].join('\n');
}

// ─── 코호트별 메일 빌더 매핑 ───
const COHORTS = {
  3: {
    daysAgo: 3,
    storeKey: 'followup_sent', // _purchase-store.js의 기존 필드 (D+3)
    storeKeyHook: 'd3',         // markFollowupSent options 호환용 별칭
    subject: ({ customerName }) =>
      `[천명당] ${customerName ? customerName + '님 ' : ''}풀이 활용 가이드 — 월회원 첫 3일 무료`,
    html: buildD3Html,
    text: buildD3Text,
  },
  7: {
    daysAgo: 7,
    storeKey: 'followup_d7_sent',
    storeKeyHook: 'd7',
    subject: ({ customerName }) =>
      `[천명당] ${customerName ? customerName + '님 ' : ''}1주일 점검 — 종합 풀이 ₩29,900 (₩4,900 절약)`,
    html: buildD7Html,
    text: buildD7Text,
  },
  14: {
    daysAgo: 14,
    storeKey: 'followup_d14_sent',
    storeKeyHook: 'd14',
    subject: ({ customerName }) =>
      `[천명당] ${customerName ? customerName + '님 ' : ''}매일 새 운세 — 월회원 ₩29,900 / 신년운세 ₩15,000`,
    html: buildD14Html,
    text: buildD14Text,
  },
  30: {
    daysAgo: 30,
    storeKey: 'winback_d30_sent', // ⚠ 신규 — 기존 generic D+30 (followup_d30_sent)와 분리
    storeKeyHook: 'winback30',
    subject: ({ customerName }) =>
      `[천명당] ${customerName ? customerName + '님 ' : ''}30일 윈백 — 30% 할인 쿠폰 (7일 한정)`,
    html: buildD30Html,
    text: buildD30Text,
  },
  60: {
    daysAgo: 60,
    storeKey: 'followup_d60_sent',
    storeKeyHook: 'd60',
    subject: ({ customerName }) =>
      `[천명당] ${customerName ? customerName + '님 ' : ''}₩2,000 재구매 쿠폰 (코드: WELCOME2K)`,
    html: buildD60Html,
    text: buildD60Text,
  },
  90: {
    daysAgo: 90,
    storeKey: 'winback_d90_sent',
    storeKeyHook: 'winback90',
    subject: ({ customerName }) =>
      `[천명당] ${customerName ? customerName + '님 ' : ''}마지막 윈백 — 종합 풀이 50% 할인 (14일 한정)`,
    html: buildD90Html,
    text: buildD90Text,
  },
};

// ─── Gmail OAuth refresh + send ───
function refreshAccessToken({ clientId, clientSecret, refreshToken }) {
  return new Promise((resolve, reject) => {
    const data = querystring.stringify({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
    });
    const req = https.request(
      {
        hostname: 'oauth2.googleapis.com',
        port: 443,
        path: '/token',
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Content-Length': Buffer.byteLength(data),
        },
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            const j = JSON.parse(buf);
            if (j.access_token) resolve(j.access_token);
            else reject(new Error('OAuth refresh 실패: ' + buf));
          } catch (e) {
            reject(new Error('OAuth 응답 파싱 실패: ' + buf));
          }
        });
      }
    );
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function buildRawMessage({ from, to, subject, html, text }) {
  const boundary = '__cmd_followup_' + Date.now() + '__';
  const encSubject = '=?UTF-8?B?' + Buffer.from(subject, 'utf-8').toString('base64') + '?=';
  const lines = [
    `From: ${from}`,
    `To: ${to}`,
    `Subject: ${encSubject}`,
    'MIME-Version: 1.0',
    `Content-Type: multipart/alternative; boundary="${boundary}"`,
    '',
    `--${boundary}`,
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 7bit',
    '',
    text || '',
    '',
    `--${boundary}`,
    'Content-Type: text/html; charset=UTF-8',
    'Content-Transfer-Encoding: 7bit',
    '',
    html,
    '',
    `--${boundary}--`,
    '',
  ];
  const raw = lines.join('\r\n');
  return Buffer.from(raw, 'utf-8')
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function sendViaGmailApi({ accessToken, raw }) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ raw });
    const req = https.request(
      {
        hostname: 'gmail.googleapis.com',
        port: 443,
        path: '/gmail/v1/users/me/messages/send',
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(data),
        },
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            const j = JSON.parse(buf);
            if (res.statusCode >= 200 && res.statusCode < 300 && j.id) {
              resolve({ id: j.id });
            } else {
              reject(new Error('Gmail API ' + res.statusCode + ': ' + buf));
            }
          } catch (e) {
            reject(new Error('Gmail 응답 파싱 실패: ' + buf));
          }
        });
      }
    );
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function sendViaSmtp({ from, to, subject, html, text, user, pass }) {
  let nodemailer;
  try {
    nodemailer = require('nodemailer');
  } catch (e) {
    throw new Error('nodemailer 미설치');
  }
  const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 465,
    secure: true,
    auth: { user, pass },
  });
  const info = await transporter.sendMail({ from, to, subject, html, text });
  return { id: info.messageId };
}

// ─── 단일 후속 메일 발송 (코호트 분기) ───
async function sendFollowupEmail({ to, customerName, skuName, skuId, orderId, days, paid_at }) {
  const cohort = COHORTS[days] || COHORTS[3];
  const fromName = '천명당';
  const fromAddr = (process.env.GMAIL_FROM || 'ghdejr11@gmail.com').trim();
  const from = `${fromName} <${fromAddr}>`;

  // Winback 코호트(D+30/D+90)는 1회용 쿠폰 자동 생성 + 유효기간 안내
  let couponCode = null;
  let validUntil = null;
  if (days === 30 || days === 90) {
    couponCode = genWinbackCoupon(orderId, days);
    const validDays = days === 30 ? 7 : 14;
    const exp = new Date(Date.now() + validDays * 24 * 60 * 60 * 1000);
    validUntil = fmtKstYmd(exp);
  }

  const tplArgs = { customerName, skuName, skuId, orderId, couponCode, validUntil };

  // ─── D+30: 5월 시즌 캠페인 매칭 (어버이날 우선 → 종소세) ───
  // 일반 winback 쿠폰(WB30-XXXX, 30%)은 그대로 유지하면서 본문 상단에 시즌 후크 추가
  let subject, html, text;
  const seasonal = days === 30 ? getSeasonalCampaign(paid_at) : null;
  if (seasonal === 'eobonal_2026') {
    const dDay = daysUntil('2026-05-08');
    const dDayLabel = dDay === 0 ? '오늘' : `D-${dDay}`;
    subject = `[천명당] ${customerName ? customerName + '님 ' : ''}부모님 사주 풀이 무료 + 어버이날 카드 5종 (어버이날 ${dDayLabel})`;
    html = buildD30EobonalHtml(tplArgs);
    text = buildD30EobonalText(tplArgs);
  } else if (seasonal === 'jongsose_2026') {
    subject = `[천명당] ${customerName ? customerName + '님 ' : ''}종소세 환급 평균 ₩48만 — 셀프 신고 12분 가이드`;
    html = buildD30JongsoseHtml(tplArgs);
    text = buildD30JongsoseText(tplArgs);
  } else {
    subject = cohort.subject({ customerName });
    html = cohort.html(tplArgs);
    text = cohort.text(tplArgs);
  }

  // 우선순위 1: SMTP App Password
  const appPass = (process.env.GMAIL_APP_PASSWORD || '').trim();
  if (appPass) {
    try {
      const r = await sendViaSmtp({ from, to, subject, html, text, user: fromAddr, pass: appPass });
      return { sent: true, method: 'smtp', messageId: r.id };
    } catch (err) {
      console.error('[cron-followup] SMTP 실패, OAuth로:', err.message);
    }
  }

  // 우선순위 2: Gmail OAuth2
  const clientId = (process.env.GMAIL_OAUTH_CLIENT_ID || '').trim();
  const clientSecret = (process.env.GMAIL_OAUTH_CLIENT_SECRET || '').trim();
  const refreshToken = (process.env.GMAIL_OAUTH_REFRESH_TOKEN || '').trim();
  if (clientId && clientSecret && refreshToken) {
    const accessToken = await refreshAccessToken({ clientId, clientSecret, refreshToken });
    const raw = buildRawMessage({ from, to, subject, html, text });
    const r = await sendViaGmailApi({ accessToken, raw });
    return { sent: true, method: 'gmail-oauth', messageId: r.id };
  }

  return { sent: false, reason: 'GMAIL_APP_PASSWORD 또는 GMAIL_OAUTH_* 미설정' };
}

// ─── 단일 코호트 처리 ───
async function processCohort({ days, isTest, isDryRun, results }) {
  const cohort = COHORTS[days];
  if (!cohort) return;

  let targets = [];
  if (isTest) {
    // 테스트 paid_at — ?season=eobonal|jongsose 시 시즌 윈도우 내 날짜로 강제 (시즌 분기 검증)
    let testPaidAt = new Date().toISOString();
    if (results._seasonOverride === 'eobonal') {
      testPaidAt = new Date('2026-05-03T00:00:00+09:00').toISOString(); // 어버이날 윈도우
    } else if (results._seasonOverride === 'jongsose') {
      testPaidAt = new Date('2026-05-15T00:00:00+09:00').toISOString(); // 종소세 윈도우 (어버이날 X)
    }
    targets = [
      {
        orderId: `cmd_test_d${days}_` + Date.now(),
        customerEmail: 'ghdejr11@gmail.com',
        customerName: '홍덕훈',
        skuId: 'saju_premium_9900',
        skuName: '사주 정밀 풀이 (테스트)',
        paid_at: testPaidAt,
      },
    ];
  } else {
    const r = await listFollowupTargets({
      daysAgo: cohort.daysAgo,
      cohortKey: cohort.storeKey, // _purchase-store.js가 코호트별 마킹 필드 분리 지원
    });
    if (!r.ok) {
      results.push({ days, error: 'store load 실패: ' + r.reason });
      return;
    }
    targets = r.records || [];
  }

  if (isDryRun) {
    results.push({
      days,
      mode: 'dry-run',
      count: targets.length,
      targets: targets.map((t) => ({
        orderId: t.orderId,
        email: (t.customerEmail || '').replace(/^(.{2}).*@/, '$1***@'),
        paid_at: t.paid_at,
      })),
    });
    return;
  }

  if (targets.length === 0) {
    results.push({ days, sent: 0, note: '대상 없음' });
    return;
  }

  const successOrderIds = [];
  const cohortResults = [];
  for (const t of targets) {
    try {
      const r = await sendFollowupEmail({
        to: t.customerEmail,
        customerName: t.customerName,
        skuName: t.skuName,
        skuId: t.skuId,
        orderId: t.orderId,
        paid_at: t.paid_at,
        days,
      });
      cohortResults.push({ orderId: t.orderId, ...r });
      if (r.sent) successOrderIds.push(t.orderId);
    } catch (err) {
      cohortResults.push({ orderId: t.orderId, sent: false, error: err.message });
    }
  }

  if (!isTest && successOrderIds.length > 0) {
    const mark = await markFollowupSent(successOrderIds, { cohortKey: cohort.storeKey });
    if (!mark.ok) console.error(`[cron-followup d${days}] markFollowupSent 실패:`, mark.reason);
  }

  results.push({
    days,
    attempted: targets.length,
    sent: successOrderIds.length,
    results: cohortResults.map((r) => ({
      orderId: r.orderId,
      sent: r.sent,
      method: r.method,
      messageId: r.messageId,
      error: r.error,
      reason: r.reason,
    })),
  });
}

// ─── 메인 핸들러 ───
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');

  const url = req.url || '';
  const isTest = /[?&]test=1/.test(url);
  const isDryRun = /[?&]dry=1/.test(url);
  const seasonMatch = url.match(/[?&]season=([a-z_]+)/);
  const seasonOverride = seasonMatch ? seasonMatch[1] : null; // test 모드 한정 — eobonal | jongsose

  // ?days=3|7|14 → 해당 코호트만 처리. 미지정시 전체 (3, 7, 14)
  const daysMatch = url.match(/[?&]days=(\d+)/);
  const explicitDays = daysMatch ? Number(daysMatch[1]) : null;

  // ─── 인증 ───
  const cronSecret = (process.env.CRON_SECRET || '').trim();
  const testKey = (process.env.FOLLOWUP_TEST_KEY || '').trim();
  const auth = (req.headers && req.headers.authorization) || '';

  let authorized = false;
  if (cronSecret && auth === `Bearer ${cronSecret}`) authorized = true;
  if (isTest && testKey) {
    const m = url.match(/[?&]key=([^&]+)/);
    if (m && decodeURIComponent(m[1]) === testKey) authorized = true;
  }
  if (!cronSecret && !isTest) authorized = true;
  if (!authorized) return res.status(403).json({ error: 'Unauthorized' });

  try {
    const cohortsToRun =
      explicitDays && COHORTS[explicitDays] ? [explicitDays] : [3, 7, 14, 30, 90];

    const results = [];
    // 시즌 오버라이드는 results._seasonOverride로 processCohort에 전달 (test 모드 한정)
    if (isTest && seasonOverride) results._seasonOverride = seasonOverride;
    for (const d of cohortsToRun) {
      await processCohort({ days: d, isTest, isDryRun, results });
    }

    const totalSent = results.reduce((sum, r) => sum + (r.sent || 0), 0);
    const totalAttempted = results.reduce(
      (sum, r) => sum + (r.attempted || (r.count || 0)),
      0
    );

    return res.status(200).json({
      mode: isTest ? 'test' : isDryRun ? 'dry-run' : 'cron',
      cohorts: cohortsToRun,
      total_attempted: totalAttempted,
      total_sent: totalSent,
      details: results,
    });
  } catch (err) {
    console.error('[cron-followup] 오류:', err);
    return res.status(500).json({ error: err.message });
  }
};
