/**
 * 천명당 영수증 + 재구매 CTA 자동 이메일 발송
 * POST /api/send-receipt
 * Body: { orderId, amount, skuId, customerEmail, customerName?, paymentKey?, method? }
 *
 * 인증 방식 우선순위:
 *   1) Gmail App Password (GMAIL_APP_PASSWORD + GMAIL_FROM)
 *      → 가장 단순, Vercel Serverless에서 SMTP 발송
 *   2) Gmail API OAuth2 (GMAIL_OAUTH_CLIENT_ID/SECRET/REFRESH_TOKEN)
 *      → secretary 부서 토큰 재인증으로 gmail.send scope 받으면 사용 가능
 *
 * 디자인 원칙:
 *   - 결제 직후 단발성 영수증 → 스팸 우려 없음 (마케팅 동의 불필요)
 *   - 모바일 친화 단일 컬럼 HTML
 *   - 천명당 다크+골드 톤 일관성
 *   - 재구매 CTA(Gumroad 3종)로 LTV +30~50% funnel 형성
 *
 * 실패 정책:
 *   - 이메일 발송 실패해도 success.html은 정상 표시되어야 함 (silent fail)
 *   - 200 OK + { sent: false, reason } 반환하여 클라이언트에서 분기 가능
 */

const https = require('https');
const querystring = require('querystring');
const { lookupSku } = require('./payment-config');
const { appendPurchase } = require('./_purchase-store');

// ─── SKU 메타 (이메일 본문 컨텍스트) ───
const SKU_DELIVERY_NOTE = {
  saju_premium_9900: '사주 정밀 풀이 결과는 앱/웹에서 즉시 확인하실 수 있습니다.',
  compat_detail_9900: '궁합 분석 결과는 앱/웹에서 즉시 확인하실 수 있습니다.',
  comprehensive_29900: '종합 풀이(사주+궁합+신년운세) 리포트는 앱/웹에서 즉시 확인하실 수 있습니다.',
  sinnyeon_15000: '신년운세 12개월 리포트는 앱/웹에서 즉시 확인하실 수 있습니다.',
  subscribe_monthly_29900:
    '월회원권 구독이 시작되었습니다. 내일 오전 8시부터 매일 카카오 알림톡(또는 텔레그램)으로 오늘의 운세를 받으실 수 있습니다.',
};

// ─── HTML 이메일 템플릿 ───
function buildHtml({ orderId, amount, sku, customerName, payDate, method }) {
  const safeName = String(customerName || '').replace(/[<>&"']/g, '');
  const amountFmt = Number(amount).toLocaleString('ko-KR') + '원';
  const deliveryNote =
    SKU_DELIVERY_NOTE[sku.id] ||
    '결과는 24시간 이내 회원 이메일로 발송됩니다.';
  const isSubscription = sku.type === 'subscription';
  const nextRenewal = isSubscription
    ? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString('ko-KR')
    : null;

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>천명당 결제 영수증</title>
</head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">

    <!-- 헤더 -->
    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">
        天命堂
      </div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>

    <!-- 본문 카드 -->
    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:42px;margin-bottom:8px;">${isSubscription ? '🎉' : '✅'}</div>
        <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px 0;font-weight:700;">
          ${isSubscription ? '월회원권 구독이 시작되었습니다' : '주문이 접수되었습니다'}
        </h1>
        <p style="color:#e8e0d0;font-size:15px;line-height:1.7;margin:0;">
          ${safeName ? safeName + '님, ' : ''}소중한 결제 감사드립니다.<br>
          ${deliveryNote.replace(/\n/g, '<br>')}
        </p>
      </div>

      <!-- 영수증 -->
      <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:18px 20px;margin:20px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:12px;">RECEIPT</div>
        <table role="presentation" style="width:100%;border-collapse:collapse;font-size:14px;">
          <tr>
            <td style="padding:6px 0;color:#a89880;border-bottom:1px solid rgba(255,255,255,0.05);">주문번호</td>
            <td style="padding:6px 0;color:#e8c97a;text-align:right;border-bottom:1px solid rgba(255,255,255,0.05);font-family:Menlo,monospace;font-size:12px;">${orderId}</td>
          </tr>
          <tr>
            <td style="padding:6px 0;color:#a89880;border-bottom:1px solid rgba(255,255,255,0.05);">상품명</td>
            <td style="padding:6px 0;color:#e8e0d0;text-align:right;border-bottom:1px solid rgba(255,255,255,0.05);">${sku.name}</td>
          </tr>
          <tr>
            <td style="padding:6px 0;color:#a89880;border-bottom:1px solid rgba(255,255,255,0.05);">결제 금액</td>
            <td style="padding:6px 0;color:#e8c97a;text-align:right;border-bottom:1px solid rgba(255,255,255,0.05);font-weight:700;">${amountFmt}${isSubscription ? ' / 월' : ''}</td>
          </tr>
          <tr>
            <td style="padding:6px 0;color:#a89880;border-bottom:1px solid rgba(255,255,255,0.05);">결제 수단</td>
            <td style="padding:6px 0;color:#e8e0d0;text-align:right;border-bottom:1px solid rgba(255,255,255,0.05);">${method || '토스페이먼츠'}</td>
          </tr>
          <tr>
            <td style="padding:6px 0;color:#a89880;${nextRenewal ? 'border-bottom:1px solid rgba(255,255,255,0.05);' : ''}">결제일</td>
            <td style="padding:6px 0;color:#e8e0d0;text-align:right;${nextRenewal ? 'border-bottom:1px solid rgba(255,255,255,0.05);' : ''}">${payDate}</td>
          </tr>
          ${nextRenewal ? `<tr>
            <td style="padding:6px 0;color:#a89880;">다음 결제일</td>
            <td style="padding:6px 0;color:#e8c97a;text-align:right;font-weight:700;">${nextRenewal}</td>
          </tr>` : ''}
        </table>
      </div>

      <div style="text-align:center;margin:24px 0 8px;">
        <a href="https://cheonmyeongdang.vercel.app/" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:700;text-decoration:none;border-radius:8px;font-size:15px;">
          🏠 천명당으로 돌아가기
        </a>
      </div>
    </div>

    <!-- 재구매 CTA — Gumroad 3종 (LTV funnel) -->
    <div style="background:linear-gradient(135deg,rgba(201,168,76,0.06),rgba(232,201,122,0.02));border:1px solid rgba(232,201,122,0.35);border-radius:16px;padding:24px 20px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:16px;">
        <span style="display:inline-block;font-size:11px;background:#c9a84c;color:#080a10;padding:3px 10px;border-radius:999px;font-weight:800;letter-spacing:0.12em;margin-bottom:8px;">PDF GUIDE</span>
        <div style="font-family:'Gowun Batang',serif;font-size:18px;color:#e8c97a;font-weight:700;margin-top:6px;">함께 보면 좋은 자료</div>
        <p style="color:#a89880;font-size:13px;margin:6px 0 0;line-height:1.6;">결제하신 풀이를 더 깊이 이해할 수 있는 가이드입니다.</p>
      </div>

      <a href="https://ghdejr.gumroad.com/l/saju-intro-kr?utm_source=email_receipt&amp;utm_campaign=postpurchase&amp;utm_content=intro" style="display:block;padding:14px;background:rgba(0,0,0,0.25);border:1px solid rgba(201,168,76,0.2);border-radius:12px;text-decoration:none;color:inherit;margin-bottom:10px;">
        <table role="presentation" style="width:100%;border-collapse:collapse;">
          <tr>
            <td style="width:48px;vertical-align:top;padding-right:12px;">
              <div style="width:48px;height:48px;border-radius:10px;background:linear-gradient(135deg,#c9a84c,#e8c97a);text-align:center;line-height:48px;font-family:'Gowun Batang',serif;font-weight:700;color:#080a10;font-size:14px;">入門</div>
            </td>
            <td style="vertical-align:top;">
              <div style="color:#e8c97a;font-weight:700;font-size:15px;margin-bottom:2px;">사주명리학 입문 가이드 (35p)</div>
              <div style="color:#a89880;font-size:12px;line-height:1.5;">천간·지지·오행·일간 기초 + 천명당 결과 활용 팁</div>
              <div style="font-size:13px;margin-top:4px;"><span style="color:#e8c97a;font-weight:800;">$5</span> <span style="color:#a89880;font-size:11px;">(≈ ₩7,000) 받기 →</span></div>
            </td>
          </tr>
        </table>
      </a>

      <a href="https://ghdejr.gumroad.com/l/2026-zodiac-diary-kr?utm_source=email_receipt&amp;utm_campaign=postpurchase&amp;utm_content=diary" style="display:block;padding:14px;background:rgba(0,0,0,0.25);border:1px solid rgba(201,168,76,0.2);border-radius:12px;text-decoration:none;color:inherit;margin-bottom:10px;">
        <table role="presentation" style="width:100%;border-collapse:collapse;">
          <tr>
            <td style="width:48px;vertical-align:top;padding-right:12px;">
              <div style="width:48px;height:48px;border-radius:10px;background:linear-gradient(135deg,#c9a84c,#e07070);text-align:center;line-height:48px;font-family:'Gowun Batang',serif;font-weight:700;color:#080a10;font-size:14px;">丙午</div>
            </td>
            <td style="vertical-align:top;">
              <div style="color:#e8c97a;font-weight:700;font-size:15px;margin-bottom:2px;">2026 띠별 운세 다이어리 (55p)</div>
              <div style="color:#a89880;font-size:12px;line-height:1.5;">12띠 1년 흐름 + 월별 다이어리 워크시트 12장</div>
              <div style="font-size:13px;margin-top:4px;"><span style="color:#e8c97a;font-weight:800;">$7</span> <span style="color:#a89880;font-size:11px;">(≈ ₩9,800) 받기 →</span></div>
            </td>
          </tr>
        </table>
      </a>

      <a href="https://ghdejr.gumroad.com/l/compatibility-workbook-kr?utm_source=email_receipt&amp;utm_campaign=postpurchase&amp;utm_content=compat" style="display:block;padding:14px;background:rgba(0,0,0,0.25);border:1px solid rgba(201,168,76,0.2);border-radius:12px;text-decoration:none;color:inherit;">
        <table role="presentation" style="width:100%;border-collapse:collapse;">
          <tr>
            <td style="width:48px;vertical-align:top;padding-right:12px;">
              <div style="width:48px;height:48px;border-radius:10px;background:linear-gradient(135deg,#e8c97a,#a89880);text-align:center;line-height:48px;font-family:'Gowun Batang',serif;font-weight:700;color:#080a10;font-size:14px;">合</div>
            </td>
            <td style="vertical-align:top;">
              <div style="color:#e8c97a;font-weight:700;font-size:15px;margin-bottom:2px;">궁합 풀이 워크북 (40p)</div>
              <div style="color:#a89880;font-size:12px;line-height:1.5;">오행 5요소 + 18 일간 케이스 + 갈등 시그널 30 체크</div>
              <div style="font-size:13px;margin-top:4px;"><span style="color:#e8c97a;font-weight:800;">$5</span> <span style="color:#a89880;font-size:11px;">(≈ ₩7,000) 받기 →</span></div>
            </td>
          </tr>
        </table>
      </a>

      <div style="font-size:11px;color:#a89880;margin-top:12px;text-align:center;line-height:1.6;">
        결제는 Gumroad에서 별도로 진행됩니다 · 결제 즉시 이메일로 PDF 발송
      </div>
    </div>

    <!-- 푸터: 사업자 정보 -->
    <div style="text-align:center;color:#7a6f5a;font-size:11px;line-height:1.8;padding:16px;border-top:1px solid rgba(201,168,76,0.15);">
      <strong style="color:#a89880;">쿤스튜디오</strong> · 대표 홍덕훈 · 사업자등록번호 552-59-00848<br>
      문의: <a href="mailto:ghdejr11@gmail.com" style="color:#c9a84c;text-decoration:none;">ghdejr11@gmail.com</a> · 결제대행: 토스페이먼츠<br>
      <a href="https://cheonmyeongdang.vercel.app/terms.html" style="color:#a89880;text-decoration:underline;">이용약관</a> ·
      <a href="https://cheonmyeongdang.vercel.app/privacy.html" style="color:#a89880;text-decoration:underline;">개인정보처리방침</a> ·
      <a href="https://cheonmyeongdang.vercel.app/support.html" style="color:#a89880;text-decoration:underline;">고객센터</a><br>
      <span style="color:#5a5044;">본 메일은 결제 영수증으로 발송되었으며 마케팅 광고가 아닙니다.</span>
    </div>

  </div>
</body>
</html>`;
}

// ─── 텍스트 fallback (HTML 미지원 클라이언트) ───
function buildText({ orderId, amount, sku, customerName, payDate, method }) {
  const amountFmt = Number(amount).toLocaleString('ko-KR') + '원';
  const isSubscription = sku.type === 'subscription';
  return [
    '천명당 (天命堂) — 결제 영수증',
    '',
    `${customerName ? customerName + '님, ' : ''}결제해 주셔서 감사합니다.`,
    '',
    '─── 영수증 ───',
    `주문번호: ${orderId}`,
    `상품명: ${sku.name}`,
    `결제 금액: ${amountFmt}${isSubscription ? ' / 월' : ''}`,
    `결제 수단: ${method || '토스페이먼츠'}`,
    `결제일: ${payDate}`,
    '',
    SKU_DELIVERY_NOTE[sku.id] || '결과는 24시간 이내 발송됩니다.',
    '',
    '─── 함께 보면 좋은 자료 ───',
    '· 사주명리학 입문 가이드 (35p, $5)',
    '  https://ghdejr.gumroad.com/l/saju-intro-kr?utm_source=email_receipt',
    '· 2026 띠별 운세 다이어리 (55p, $7)',
    '  https://ghdejr.gumroad.com/l/2026-zodiac-diary-kr?utm_source=email_receipt',
    '· 궁합 풀이 워크북 (40p, $5)',
    '  https://ghdejr.gumroad.com/l/compatibility-workbook-kr?utm_source=email_receipt',
    '',
    '쿤스튜디오 · 대표 홍덕훈 · 사업자등록번호 552-59-00848',
    '문의: ghdejr11@gmail.com',
  ].join('\n');
}

// ─── Gmail OAuth2 access token 발급 ───
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

// ─── RFC 2822 raw 메일 생성 + base64url 인코딩 ───
function buildRawMessage({ from, to, subject, html, text }) {
  const boundary = '__cmd_boundary_' + Date.now() + '__';
  // Subject UTF-8 base64 인코딩 (한글 안전)
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
  // base64url
  return Buffer.from(raw, 'utf-8')
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

// ─── Gmail API users.messages.send ───
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
              resolve({ id: j.id, raw: j });
            } else {
              reject(new Error('Gmail API 응답 오류 ' + res.statusCode + ': ' + buf));
            }
          } catch (e) {
            reject(new Error('Gmail API 파싱 실패: ' + buf));
          }
        });
      }
    );
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// ─── nodemailer 동적 로드 (App Password 경로) ───
async function sendViaSmtp({ from, to, subject, html, text, user, pass }) {
  let nodemailer;
  try {
    nodemailer = require('nodemailer');
  } catch (e) {
    throw new Error('nodemailer 미설치 — npm install nodemailer 후 재배포 필요');
  }
  const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 465,
    secure: true,
    auth: { user, pass },
  });
  const info = await transporter.sendMail({ from, to, subject, html, text });
  return { id: info.messageId, raw: info };
}

// ─── 메인 핸들러 ───
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  // body 파싱
  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  const {
    orderId,
    amount,
    skuId,
    customerEmail,
    customerName,
    method,
  } = body;

  if (!orderId || !customerEmail || !skuId) {
    return res.status(400).json({
      sent: false,
      reason: 'orderId, customerEmail, skuId 필수',
    });
  }

  // 이메일 형식 가벼운 검증
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(customerEmail))) {
    return res.status(400).json({ sent: false, reason: '이메일 형식 오류' });
  }

  // SKU 검증
  const sku = lookupSku(skuId);
  if (!sku) {
    return res.status(400).json({ sent: false, reason: '유효하지 않은 SKU: ' + skuId });
  }

  // amount는 영수증 표시용 — SKU 가격으로 강제 (위변조 방지)
  const finalAmount = Number(sku.amount);
  const payDate = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

  const html = buildHtml({
    orderId,
    amount: finalAmount,
    sku,
    customerName,
    payDate,
    method,
  });
  const text = buildText({
    orderId,
    amount: finalAmount,
    sku,
    customerName,
    payDate,
    method,
  });
  const subject = `[천명당] 주문 접수 — ${sku.name} (${finalAmount.toLocaleString('ko-KR')}원)`;

  const fromName = '천명당';
  const fromAddr = (process.env.GMAIL_FROM || 'ghdejr11@gmail.com').trim();
  const from = `${fromName} <${fromAddr}>`;
  const to = String(customerEmail).trim();

  // ─── D+3 후속 메일 큐에 저장 (GitHub Gist) ───
  // 영수증 발송 결과와 무관하게 fire-and-forget — 실패해도 영수증은 정상 발송
  // 구독은 별도 알림톡 발송이 있으므로 D+3 업셀 대상에서 제외
  if (sku.type !== 'subscription') {
    appendPurchase({
      orderId,
      customerEmail: to,
      customerName: customerName || '',
      skuId: sku.id,
      skuName: sku.name,
      amount: finalAmount,
      method: method || 'toss',
      paid_at: new Date().toISOString(),
    })
      .then((r) => {
        if (!r.ok) console.error('[send-receipt] purchase store 저장 실패:', r.reason);
        else if (r.gistId) console.log('[send-receipt] purchase stored, gistId=', r.gistId);
      })
      .catch((err) => console.error('[send-receipt] purchase store 예외:', err.message));
  }

  // ─── 인증 경로 1: Gmail App Password (SMTP) ───
  const appPass = (process.env.GMAIL_APP_PASSWORD || '').trim();
  if (appPass) {
    try {
      const r = await sendViaSmtp({
        from,
        to,
        subject,
        html,
        text,
        user: fromAddr,
        pass: appPass,
      });
      return res.status(200).json({
        sent: true,
        method: 'smtp',
        messageId: r.id,
        to,
      });
    } catch (err) {
      console.error('[send-receipt] SMTP 실패, OAuth로 fallback:', err.message);
      // OAuth로 fallback 시도
    }
  }

  // ─── 인증 경로 2: Gmail OAuth2 (refresh token) ───
  const clientId = (process.env.GMAIL_OAUTH_CLIENT_ID || '').trim();
  const clientSecret = (process.env.GMAIL_OAUTH_CLIENT_SECRET || '').trim();
  const refreshToken = (process.env.GMAIL_OAUTH_REFRESH_TOKEN || '').trim();

  if (clientId && clientSecret && refreshToken) {
    try {
      const accessToken = await refreshAccessToken({ clientId, clientSecret, refreshToken });
      const raw = buildRawMessage({ from, to, subject, html, text });
      const r = await sendViaGmailApi({ accessToken, raw });
      return res.status(200).json({
        sent: true,
        method: 'gmail-oauth',
        messageId: r.id,
        to,
      });
    } catch (err) {
      console.error('[send-receipt] OAuth 실패:', err.message);
      // 둘 다 실패 → silent fail (200 OK)
      return res.status(200).json({
        sent: false,
        reason: 'gmail-oauth 발송 실패: ' + err.message,
      });
    }
  }

  // 인증 정보 없음 → silent fail (성공 페이지에 영향 없게)
  return res.status(200).json({
    sent: false,
    reason: 'GMAIL_APP_PASSWORD 또는 GMAIL_OAUTH_* 환경변수 미설정',
  });
};
