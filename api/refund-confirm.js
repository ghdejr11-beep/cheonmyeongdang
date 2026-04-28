/**
 * 천명당 토스페이먼츠 환불 webhook 자동 응답 (CS 시간 0)
 * POST /api/refund-confirm
 *
 * Toss webhook 등록 (live 키 통과 후 사용자가 콘솔에서 등록):
 *   URL: https://cheonmyeongdang.vercel.app/api/refund-confirm
 *   이벤트: PAYMENT_STATUS_CHANGED  (CANCELED / PARTIAL_CANCELED 포함)
 *
 * 흐름:
 *   1) Toss webhook payload 수신 (PAYMENT_STATUS_CHANGED, status=CANCELED)
 *   2) signature 검증 (TOSS_WEBHOOK_SECRET 있으면) — 우회시 paymentKey로 Toss API 재조회
 *   3) Gist에 markRefunded(orderId) → D+3/D+7/D+14 후속 메일 자동 차단
 *   4) 고객에게 환불 확인 메일 자동 발송:
 *      - 환불 처리 안내 (영업일 3~7일)
 *      - 환불 사유에 따라 톤 조정 (단순 변심 / 결과 미수령 / 기타)
 *      - winback CTA — Gumroad 4종 추천 (utm_source=refund&utm_campaign=winback)
 *   5) 텔레그램 알림 (선택)
 *
 * 보안:
 *   - TOSS_WEBHOOK_SECRET 설정시 HMAC-SHA256 signature 검증
 *     (Toss header: tosspayments-webhook-signature, tosspayments-webhook-transmission-time)
 *   - 미설정시 paymentKey 기반 Toss API 역조회로 검증
 *
 * 수동 테스트:
 *   POST /api/refund-confirm?test=1&key=$FOLLOWUP_TEST_KEY
 *   Body: { orderId, customerEmail, customerName, skuName, refundAmount, cancelReason }
 */

const https = require('https');
const crypto = require('crypto');
const querystring = require('querystring');
const { markRefunded } = require('./_purchase-store');

// ─── Toss API 헬퍼 ───
function tossGetPayment(secretKey, paymentKey) {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(secretKey + ':').toString('base64');
    const req = https.request(
      {
        hostname: 'api.tosspayments.com',
        port: 443,
        path: '/v1/payments/' + encodeURIComponent(paymentKey),
        method: 'GET',
        headers: { Authorization: `Basic ${auth}` },
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            resolve({ status: res.statusCode, body: JSON.parse(buf) });
          } catch (e) {
            resolve({ status: res.statusCode, body: { code: 'PARSE_ERROR', message: buf } });
          }
        });
      }
    );
    req.on('error', reject);
    req.end();
  });
}

function sendTelegram(token, chatId, text) {
  return new Promise((resolve) => {
    const data = JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML' });
    const req = https.request(
      {
        hostname: 'api.telegram.org',
        port: 443,
        path: `/bot${token}/sendMessage`,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(data),
        },
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => resolve(buf));
      }
    );
    req.on('error', () => resolve(null));
    req.write(data);
    req.end();
  });
}

// ─── 환불 사유 톤 분류 ───
function classifyReason(rawReason) {
  const r = String(rawReason || '').toLowerCase();
  if (/(변심|단순|마음|취소)/i.test(rawReason || '')) return 'changed_mind';
  if (/(결과|받지|못받|미수령|안.?받|수신.?실패|메일.?안)/i.test(rawReason || '')) return 'not_received';
  if (/(중복|이중|두번|2번)/i.test(rawReason || '')) return 'duplicate';
  if (/(불만|불량|틀린|오류|에러|작동|버그)/i.test(rawReason || '')) return 'quality';
  return 'other';
}

function reasonOpener(category, customerName) {
  const greet = customerName ? `${customerName}님,` : '안녕하세요,';
  switch (category) {
    case 'changed_mind':
      return `${greet}<br>결제 취소가 정상 접수되었습니다.<br>다음에 다시 만나뵐 수 있길 바랍니다.`;
    case 'not_received':
      return `${greet}<br>결과 메일을 받지 못하셔서 불편을 드려 죄송합니다.<br>환불은 즉시 처리되었으며, 메일 미수령 원인을 점검하여 재발 방지하겠습니다.`;
    case 'duplicate':
      return `${greet}<br>중복 결제가 확인되어 환불 처리되었습니다.<br>실수로 결제되신 점 양해 부탁드리며, 빠르게 입금 환불됩니다.`;
    case 'quality':
      return `${greet}<br>풀이 결과에 만족하지 못하신 점 진심으로 사과드립니다.<br>환불은 즉시 처리되었으며, 의견은 서비스 개선에 반영하겠습니다.`;
    default:
      return `${greet}<br>요청하신 결제 취소가 정상 접수되었습니다.<br>편하게 다시 찾아주시면 감사하겠습니다.`;
  }
}

// ─── 환불 확인 메일 HTML ───
function buildRefundHtml({ customerName, skuName, orderId, refundAmount, category }) {
  const opener = reasonOpener(category, String(customerName || '').replace(/[<>&"']/g, ''));
  const amtStr = `₩${Number(refundAmount || 0).toLocaleString('ko-KR')}`;

  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>천명당 — 환불 처리 안내</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">

    <div style="text-align:center;padding:28px 16px 20px;">
      <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
      <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
    </div>

    <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:42px;margin-bottom:8px;">✅</div>
        <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px 0;font-weight:700;">환불 처리 완료</h1>
        <p style="color:#e8e0d0;font-size:14px;line-height:1.7;margin:12px 0 0;">${opener}</p>
      </div>

      <!-- 환불 상세 -->
      <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px;margin:20px 0;">
        <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:12px;">환불 상세</div>
        <div style="display:flex;justify-content:space-between;font-size:13px;color:#a89880;padding:6px 0;border-bottom:1px solid rgba(201,168,76,0.1);">
          <span>주문번호</span><span style="font-family:Menlo,monospace;color:#e8e0d0;">${orderId}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px;color:#a89880;padding:6px 0;border-bottom:1px solid rgba(201,168,76,0.1);">
          <span>상품</span><span style="color:#e8e0d0;">${skuName || '-'}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px;color:#a89880;padding:6px 0;border-bottom:1px solid rgba(201,168,76,0.1);">
          <span>환불 금액</span><span style="color:#e8c97a;font-weight:700;">${amtStr}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px;color:#a89880;padding:6px 0;">
          <span>입금 예정</span><span style="color:#e8e0d0;">영업일 기준 3~7일 이내</span>
        </div>
      </div>

      <!-- 안내 문구 -->
      <div style="background:rgba(201,168,76,0.05);border-left:3px solid #c9a84c;padding:14px 16px;margin:18px 0;font-size:13px;color:#a89880;line-height:1.7;">
        <strong style="color:#e8c97a;">📌 입금 안내</strong><br>
        결제 수단(카드/계좌)에 따라 입금까지 영업일 기준 <strong style="color:#e8c97a;">3~7일</strong>이 소요됩니다.<br>
        카드 결제는 다음 결제일에 차감되어 표시될 수 있습니다.
      </div>

      <!-- Winback CTA — Gumroad 4종 -->
      <div style="background:linear-gradient(135deg,#1a1530,#251a3a);border:1px solid rgba(201,168,76,0.3);border-radius:14px;padding:22px 18px;margin:24px 0;">
        <div style="text-align:center;margin-bottom:14px;">
          <div style="display:inline-block;font-size:11px;background:rgba(201,168,76,0.2);color:#e8c97a;padding:4px 12px;border-radius:999px;font-weight:800;letter-spacing:0.12em;">언제든 환영합니다</div>
        </div>
        <h2 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:18px;margin:6px 0 10px;font-weight:700;text-align:center;">다른 형태로 만나보세요</h2>
        <p style="color:#a89880;font-size:13px;line-height:1.7;margin:0 0 14px;text-align:center;">결제 부담 없는 e-book 형태로도 천명당의 콘텐츠를 받아보실 수 있습니다.</p>

        <div style="display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;">
          <a href="https://kunstudio.gumroad.com/l/saju_basic?utm_source=refund&utm_campaign=winback&utm_content=ebook_saju" style="flex:1 1 45%;padding:10px;background:rgba(0,0,0,0.4);border:1px solid rgba(201,168,76,0.3);border-radius:8px;text-align:center;text-decoration:none;color:#e8c97a;font-size:13px;font-weight:700;">📜 사주 기초 e-book</a>
          <a href="https://kunstudio.gumroad.com/l/compat_guide?utm_source=refund&utm_campaign=winback&utm_content=ebook_compat" style="flex:1 1 45%;padding:10px;background:rgba(0,0,0,0.4);border:1px solid rgba(201,168,76,0.3);border-radius:8px;text-align:center;text-decoration:none;color:#e8c97a;font-size:13px;font-weight:700;">💞 궁합 가이드</a>
          <a href="https://kunstudio.gumroad.com/l/dream_dictionary?utm_source=refund&utm_campaign=winback&utm_content=ebook_dream" style="flex:1 1 45%;padding:10px;background:rgba(0,0,0,0.4);border:1px solid rgba(201,168,76,0.3);border-radius:8px;text-align:center;text-decoration:none;color:#e8c97a;font-size:13px;font-weight:700;">🌙 꿈해몽 사전</a>
          <a href="https://kunstudio.gumroad.com/l/sinnyeon_yearly?utm_source=refund&utm_campaign=winback&utm_content=ebook_sinnyeon" style="flex:1 1 45%;padding:10px;background:rgba(0,0,0,0.4);border:1px solid rgba(201,168,76,0.3);border-radius:8px;text-align:center;text-decoration:none;color:#e8c97a;font-size:13px;font-weight:700;">📅 신년운세 가이드</a>
        </div>
        <div style="text-align:center;margin-top:14px;">
          <a href="https://kunstudio.gumroad.com?utm_source=refund&utm_campaign=winback" style="display:inline-block;padding:10px 22px;background:rgba(201,168,76,0.15);color:#e8c97a;border:1px solid #c9a84c;font-weight:700;text-decoration:none;border-radius:6px;font-size:13px;">전체 보기</a>
        </div>
      </div>

      <!-- 문의 -->
      <div style="text-align:center;color:#a89880;font-size:12px;line-height:1.7;margin-top:18px;">
        환불 관련 문의: <a href="mailto:ghdejr11@gmail.com?subject=[천명당]%20환불%20문의%20${orderId}" style="color:#c9a84c;text-decoration:none;">ghdejr11@gmail.com</a>
      </div>
    </div>

    <div style="text-align:center;color:#7a6f5a;font-size:11px;line-height:1.8;padding:16px;border-top:1px solid rgba(201,168,76,0.15);">
      <strong style="color:#a89880;">쿤스튜디오</strong> · 대표 홍덕훈 · 사업자등록번호 552-59-00848<br>
      <a href="https://cheonmyeongdang.vercel.app/terms.html" style="color:#a89880;text-decoration:underline;">이용약관</a> ·
      <a href="https://cheonmyeongdang.vercel.app/privacy.html" style="color:#a89880;text-decoration:underline;">개인정보처리방침</a>
    </div>
  </div>
</body></html>`;
}

function buildRefundText({ customerName, skuName, orderId, refundAmount, category }) {
  const greet = customerName ? `${customerName}님,` : '안녕하세요,';
  let opener;
  switch (category) {
    case 'changed_mind':
      opener = `${greet} 결제 취소가 정상 접수되었습니다. 다음에 다시 만나뵐 수 있길 바랍니다.`; break;
    case 'not_received':
      opener = `${greet} 결과 메일을 받지 못하셔서 불편을 드려 죄송합니다. 환불은 즉시 처리되었습니다.`; break;
    case 'duplicate':
      opener = `${greet} 중복 결제가 확인되어 환불 처리되었습니다.`; break;
    case 'quality':
      opener = `${greet} 풀이 결과에 만족하지 못하신 점 진심으로 사과드립니다. 환불 처리되었습니다.`; break;
    default:
      opener = `${greet} 요청하신 결제 취소가 정상 접수되었습니다.`;
  }

  return [
    '천명당 (天命堂) — 환불 처리 완료',
    '',
    opener,
    '',
    '─── 환불 상세 ───',
    `주문번호: ${orderId}`,
    `상품: ${skuName || '-'}`,
    `환불 금액: ₩${Number(refundAmount || 0).toLocaleString('ko-KR')}`,
    '입금 예정: 영업일 기준 3~7일 이내',
    '',
    '※ 결제 수단(카드/계좌)에 따라 입금까지 시간이 다소 걸릴 수 있습니다.',
    '',
    '─── 다른 형태로도 만나보세요 (e-book) ───',
    '· 사주 기초 e-book: https://kunstudio.gumroad.com/l/saju_basic?utm_source=refund&utm_campaign=winback',
    '· 궁합 가이드: https://kunstudio.gumroad.com/l/compat_guide?utm_source=refund&utm_campaign=winback',
    '· 꿈해몽 사전: https://kunstudio.gumroad.com/l/dream_dictionary?utm_source=refund&utm_campaign=winback',
    '· 신년운세 가이드: https://kunstudio.gumroad.com/l/sinnyeon_yearly?utm_source=refund&utm_campaign=winback',
    '',
    '환불 관련 문의: ghdejr11@gmail.com',
    '',
    '쿤스튜디오 · 대표 홍덕훈 · 사업자등록번호 552-59-00848',
  ].join('\n');
}

// ─── Gmail 전송 (cron-followup과 동일 패턴) ───
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
  const boundary = '__cmd_refund_' + Date.now() + '__';
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
  return Buffer.from(lines.join('\r\n'), 'utf-8')
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
            if (res.statusCode >= 200 && res.statusCode < 300 && j.id) resolve({ id: j.id });
            else reject(new Error('Gmail API ' + res.statusCode + ': ' + buf));
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

async function sendRefundEmail({ to, customerName, skuName, orderId, refundAmount, category }) {
  const fromName = '천명당';
  const fromAddr = (process.env.GMAIL_FROM || 'ghdejr11@gmail.com').trim();
  const from = `${fromName} <${fromAddr}>`;
  const subject = `[천명당] ${customerName ? customerName + '님 ' : ''}환불 처리 완료 — 영업일 3~7일 입금`;
  const html = buildRefundHtml({ customerName, skuName, orderId, refundAmount, category });
  const text = buildRefundText({ customerName, skuName, orderId, refundAmount, category });

  const clientId = (process.env.GMAIL_OAUTH_CLIENT_ID || '').trim();
  const clientSecret = (process.env.GMAIL_OAUTH_CLIENT_SECRET || '').trim();
  const refreshToken = (process.env.GMAIL_OAUTH_REFRESH_TOKEN || '').trim();
  if (!clientId || !clientSecret || !refreshToken) {
    return { sent: false, reason: 'GMAIL_OAUTH_* 미설정' };
  }
  const accessToken = await refreshAccessToken({ clientId, clientSecret, refreshToken });
  const raw = buildRawMessage({ from, to, subject, html, text });
  const r = await sendViaGmailApi({ accessToken, raw });
  return { sent: true, method: 'gmail-oauth', messageId: r.id };
}

// ─── HMAC-SHA256 signature 검증 (Toss webhook 표준) ───
// header tosspayments-webhook-signature 형식: "v1:<base64sig>,v1:<base64sig2>"
// payload : `${rawBody}:${transmissionTime}`  → HMAC-SHA256 with secret → base64
function verifyTossSignature({ rawBody, signatureHeader, transmissionTime, secret }) {
  if (!secret) return { ok: true, skipped: true }; // secret 미설정시 skip (paymentKey 역조회로 대체)
  if (!signatureHeader || !transmissionTime) return { ok: false, reason: 'header 없음' };
  try {
    const computed = crypto
      .createHmac('sha256', secret)
      .update(`${rawBody}:${transmissionTime}`)
      .digest('base64');
    const candidates = signatureHeader
      .split(',')
      .map((s) => s.trim().replace(/^v1:/, ''));
    const matched = candidates.some((c) => {
      try {
        const a = Buffer.from(c, 'base64');
        const b = Buffer.from(computed, 'base64');
        return a.length === b.length && crypto.timingSafeEqual(a, b);
      } catch (e) {
        return false;
      }
    });
    return matched ? { ok: true } : { ok: false, reason: 'signature 불일치' };
  } catch (err) {
    return { ok: false, reason: 'signature 검증 오류: ' + err.message };
  }
}

// ─── 메인 핸들러 ───
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, tosspayments-webhook-signature, tosspayments-webhook-transmission-time');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const url = req.url || '';
  const isTest = /[?&]test=1/.test(url);

  // raw body for signature verification
  let rawBody = '';
  let body = req.body;
  if (typeof body === 'string') {
    rawBody = body;
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  } else if (body && typeof body === 'object') {
    rawBody = JSON.stringify(body);
  } else {
    body = {};
  }

  // ─── 인증 ───
  const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const tgChat = (process.env.TELEGRAM_CHAT_ID || '').trim();
  const webhookSecret = (process.env.TOSS_WEBHOOK_SECRET || '').trim();
  const tossSecret = (process.env.TOSS_SECRET_KEY || '').trim();
  const testKey = (process.env.FOLLOWUP_TEST_KEY || '').trim();

  if (isTest) {
    const m = url.match(/[?&]key=([^&]+)/);
    if (!testKey || !m || decodeURIComponent(m[1]) !== testKey) {
      return res.status(403).json({ error: 'Unauthorized (test mode requires correct key)' });
    }
  } else {
    // 실제 webhook — signature 검증 또는 paymentKey 역조회
    const sigHeader = req.headers['tosspayments-webhook-signature'] || '';
    const txTime = req.headers['tosspayments-webhook-transmission-time'] || '';
    const sig = verifyTossSignature({
      rawBody,
      signatureHeader: sigHeader,
      transmissionTime: txTime,
      secret: webhookSecret,
    });
    if (webhookSecret && !sig.ok) {
      console.warn('[refund-confirm] signature 검증 실패:', sig.reason);
      return res.status(401).json({ error: 'Invalid signature: ' + sig.reason });
    }
    // signature 미설정시 → paymentKey로 Toss API 역조회 (아래에서)
  }

  try {
    // Toss webhook payload 구조 추출
    // PAYMENT_STATUS_CHANGED:
    //   { eventType: "PAYMENT_STATUS_CHANGED", createdAt, data: { paymentKey, orderId, status, ... } }
    // 또는 직접 결제 객체가 data로 오는 경우도 있음
    const eventType = body.eventType || '';
    const data = body.data || body;
    const status = data.status || '';
    const paymentKey = data.paymentKey || '';
    const orderId = data.orderId || body.orderId || '';

    let canonical = data; // 기본: webhook의 data 사용
    let trustedFromTossApi = false;

    // signature 미검증 모드 또는 일부 필드 누락 → Toss API 역조회로 신뢰성 확보
    if ((!webhookSecret || !data.totalAmount) && tossSecret && paymentKey) {
      const lookup = await tossGetPayment(tossSecret, paymentKey);
      if (lookup.status === 200 && lookup.body) {
        canonical = lookup.body;
        trustedFromTossApi = true;
      } else {
        console.warn('[refund-confirm] Toss API 역조회 실패:', lookup.status, lookup.body);
      }
    }

    const finalStatus = canonical.status || status;
    const finalOrderId = canonical.orderId || orderId;

    // 테스트 모드는 body 그대로 신뢰
    if (isTest) {
      const t = body || {};
      if (!t.orderId || !t.customerEmail) {
        return res.status(400).json({ error: '테스트 모드: orderId, customerEmail 필수' });
      }
      // 환불 마킹 + 메일 발송 (테스트는 실제 Gist 마킹 X)
      const emailResult = await sendRefundEmail({
        to: t.customerEmail,
        customerName: t.customerName || '',
        skuName: t.skuName || '천명당 결제',
        orderId: t.orderId,
        refundAmount: t.refundAmount || 9900,
        category: classifyReason(t.cancelReason),
      });
      return res.status(200).json({ mode: 'test', emailResult, classified: classifyReason(t.cancelReason) });
    }

    // 환불 이벤트가 아닌 경우 무시 (Toss는 다양한 status 이벤트 보냄 — DONE, IN_PROGRESS 등)
    const isRefund = ['CANCELED', 'PARTIAL_CANCELED', 'CANCELLED'].includes(String(finalStatus).toUpperCase());
    if (!isRefund) {
      return res.status(200).json({ ignored: true, reason: 'not a refund event', status: finalStatus, eventType });
    }
    if (!finalOrderId) {
      return res.status(400).json({ error: 'orderId 누락' });
    }

    // 환불 금액 / 사유 추출
    const cancels = canonical.cancels || [];
    const lastCancel = cancels.length > 0 ? cancels[cancels.length - 1] : null;
    let refundAmount = 0;
    if (lastCancel && lastCancel.cancelAmount) {
      refundAmount = lastCancel.cancelAmount;
    } else if (canonical.balanceAmount === 0 && canonical.totalAmount) {
      // 전체 환불 (잔액 0) → 전체 금액 환불
      refundAmount = canonical.totalAmount;
    } else if (canonical.cancelAmount) {
      refundAmount = canonical.cancelAmount;
    } else if (canonical.totalAmount) {
      refundAmount = canonical.totalAmount;
    }
    const cancelReason = (lastCancel && lastCancel.cancelReason) || canonical.cancelReason || '';
    const customerEmail = canonical.customerEmail || (canonical.metadata && canonical.metadata.customerEmail) || '';
    const customerName = canonical.customerName || (canonical.metadata && canonical.metadata.customerName) || '';
    const skuName = canonical.orderName || (canonical.metadata && canonical.metadata.skuName) || '천명당 결제';
    const category = classifyReason(cancelReason);

    // 1) Gist에 환불 마킹 (D+3/D+7/D+14 후속 메일 자동 차단)
    let markResult;
    try {
      markResult = await markRefunded(finalOrderId);
    } catch (err) {
      markResult = { ok: false, reason: err.message };
    }

    // 2) 텔레그램 알림
    if (tgToken && tgChat) {
      const txt =
        `🔁 <b>천명당 환불 처리</b>\n` +
        `주문ID: ${finalOrderId}\n` +
        `상품: ${skuName}\n` +
        `금액: ₩${Number(refundAmount).toLocaleString('ko-KR')}\n` +
        `사유: ${cancelReason || '-'} (${category})\n` +
        `이메일: ${customerEmail || '-'}\n` +
        `Gist mark: ${markResult.ok ? 'OK' : '실패: ' + markResult.reason}\n` +
        `검증: ${webhookSecret ? 'signature' : trustedFromTossApi ? 'API 역조회' : 'webhook payload'}\n` +
        `시각: ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}`;
      sendTelegram(tgToken, tgChat, txt);
    }

    // 3) 환불 확인 메일 발송 (이메일 있을 때만)
    let emailResult = { sent: false, reason: '고객 이메일 없음' };
    if (customerEmail) {
      try {
        emailResult = await sendRefundEmail({
          to: customerEmail,
          customerName,
          skuName,
          orderId: finalOrderId,
          refundAmount,
          category,
        });
      } catch (err) {
        emailResult = { sent: false, reason: err.message };
      }
    }

    return res.status(200).json({
      ok: true,
      orderId: finalOrderId,
      status: finalStatus,
      refundAmount,
      category,
      markRefunded: markResult,
      email: emailResult,
    });
  } catch (err) {
    console.error('[refund-confirm] 오류:', err);
    return res.status(500).json({ error: err.message });
  }
};
