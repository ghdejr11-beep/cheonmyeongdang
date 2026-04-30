/**
 * 천명당 D+3 / D+7 / D+14 후속 메일 자동 발송 (Vercel Cron — 단일 일1회 실행으로 3개 코호트 처리)
 * GET /api/cron-followup                     — 정기 실행 (매일 09:00 KST). D+3, D+7, D+14 모두 처리
 * GET /api/cron-followup?test=1              — 본인 테스트 발송 (D+3 기본)
 * GET /api/cron-followup?test=1&days=7       — D+7 템플릿 테스트
 * GET /api/cron-followup?test=1&days=14      — D+14 템플릿 테스트
 * GET /api/cron-followup?days=7              — D+7 코호트만 cron 처리 (개별 디버그용)
 * GET /api/cron-followup?dry=1               — 발송 안하고 대상자만 미리보기
 *
 * 흐름:
 *   1) GitHub Gist에서 결제 데이터 로드
 *   2) 코호트별 paid_at 윈도우 필터:
 *      - D+3 : "정밀 풀이 활용 5팁 + 월회원권 3일 무료 체험" (LTV +30%)
 *      - D+7 : "활용 1주 — 종합 풀이 ₩29,900 업셀" (LTV +20%)
 *      - D+14: "매일 카톡 운세 — 월회원권 ₩29,900 / 신년운세 ₩15,000" (LTV +15%)
 *   3) 각 코호트마다 followup_sent / followup_d7_sent / followup_d14_sent 별도 마킹
 *   4) refunded=true 항목은 모든 코호트에서 자동 제외 (LTV +5% winback은 refund-confirm에서 처리)
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
const querystring = require('querystring');
const {
  listFollowupTargets,
  markFollowupSent,
} = require('./_purchase-store');

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

// ─── D+30 (한 달 점검) 메일 빌더 ───
function buildD30Html({ customerName, skuName, orderId }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const greet = safeName ? `${safeName}님,` : '안녕하세요,';
  return `<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>천명당 — 한 달 점검</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px;font-weight:700;">${greet}<br>한 달 — 어떻게 지내셨나요?</h1>
      <p style="color:#e8e0d0;font-size:15px;line-height:1.7;">한 달 전 <strong style="color:#e8c97a;">${skuName}</strong>을 받아보셨습니다. 다음 한 달이 어떻게 흐를지 먼저 살펴보세요.</p>
      <div style="background:rgba(0,0,0,0.4);border-radius:10px;padding:18px;margin:18px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;">다음 달 — 미리 알아두면 좋은 3가지</div>
        <ul style="color:#a89880;font-size:14px;line-height:1.8;padding-left:18px;margin:0;">
          <li><strong style="color:#e8c97a;">세운 변동</strong> — 본인 사주 일간과 다음 달 천간의 관계 확인</li>
          <li><strong style="color:#e8c97a;">월운 길흉일</strong> — 중요 결정·계약일은 길일에 맞추기</li>
          <li><strong style="color:#e8c97a;">건강·관계 주의일</strong> — 일주 충·형 일자 미리 메모</li>
        </ul>
      </div>
      <div style="background:linear-gradient(135deg,#1a1530,#251a3a);border:2px solid #e8c97a;border-radius:14px;padding:24px;margin:20px 0;text-align:center;">
        <h2 style="color:#e8c97a;font-size:20px;margin:0 0 8px;">월회원권으로 매일 새 운세 받기</h2>
        <p style="color:#e8e0d0;font-size:14px;line-height:1.7;">월 ₩29,900 — 사주 정밀 + 궁합 + 매일 카톡 운세 무제한.<br>3일 무료 체험 후 결제, 언제든 해지.</p>
        <a href="https://cheonmyeongdang.vercel.app/pay.html?sku=subscribe_monthly_29900&utm_source=email_d30&utm_campaign=upsell_monthly&utm_content=d30" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:8px;font-size:15px;margin-top:8px;">3일 무료 체험 시작</a>
      </div>
      <p style="color:#7a6f5a;font-size:11px;text-align:center;margin-top:16px;">* 본 메일은 한 달 전 결제 고객님께만 발송됩니다 · 주문번호: ${orderId}</p>
    </div>
    <div style="text-align:center;color:#7a6f5a;font-size:11px;line-height:1.6;padding:12px;">쿤스튜디오 · 사업자등록번호 552-59-00848<br><a href="https://cheonmyeongdang.vercel.app" style="color:#7a6f5a;">cheonmyeongdang.vercel.app</a></div>
  </div></body></html>`;
}
function buildD30Text({ customerName, skuName, orderId }) {
  const greet = customerName ? `${customerName}님,` : '안녕하세요,';
  return [
    greet,
    `한 달 전 ${skuName}을 받아보셨습니다. 다음 한 달 흐름을 먼저 살펴보세요.`,
    '',
    '다음 달 — 미리 알아두면 좋은 3가지:',
    '· 세운 변동 (사주 일간 × 다음 달 천간 관계)',
    '· 월운 길흉일 (중요 결정·계약일)',
    '· 건강·관계 주의일 (일주 충·형 일자)',
    '',
    '─── 월회원권 — ₩29,900 / 월 ───',
    '· 사주 정밀 + 궁합 + 매일 카톡 운세 무제한',
    '· 3일 무료 체험 후 결제, 언제든 해지',
    `시작하기: https://cheonmyeongdang.vercel.app/pay.html?sku=subscribe_monthly_29900&utm_source=email_d30&utm_campaign=upsell_monthly`,
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
    storeKey: 'followup_d30_sent',
    storeKeyHook: 'd30',
    subject: ({ customerName }) =>
      `[천명당] ${customerName ? customerName + '님 ' : ''}한 달 점검 — 다음 달 운세 미리보기`,
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
async function sendFollowupEmail({ to, customerName, skuName, orderId, days }) {
  const cohort = COHORTS[days] || COHORTS[3];
  const fromName = '천명당';
  const fromAddr = (process.env.GMAIL_FROM || 'ghdejr11@gmail.com').trim();
  const from = `${fromName} <${fromAddr}>`;

  const subject = cohort.subject({ customerName });
  const html = cohort.html({ customerName, skuName, orderId });
  const text = cohort.text({ customerName, skuName, orderId });

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
    targets = [
      {
        orderId: `cmd_test_d${days}_` + Date.now(),
        customerEmail: 'ghdejr11@gmail.com',
        customerName: '홍덕훈',
        skuId: 'saju_premium_9900',
        skuName: '사주 정밀 풀이 (테스트)',
        paid_at: new Date().toISOString(),
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
        orderId: t.orderId,
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
      explicitDays && COHORTS[explicitDays] ? [explicitDays] : [3, 7, 14];

    const results = [];
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
