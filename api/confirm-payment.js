/**
 * 천명당 토스페이먼츠 결제 승인 API
 * POST /api/confirm-payment
 * Body: { paymentKey, orderId, amount, skuId, customerEmail }
 *
 * 흐름:
 *   1) 클라이언트 위젯 successUrl 콜백 → 이 API 호출
 *   2) skuId로 서버측 가격 검증 (위변조 방지)
 *   3) 시크릿 키로 https://api.tosspayments.com/v1/payments/confirm 호출
 *   4) 검증 후 영수증 URL + 주문 정보 반환
 *   5) 텔레그램 알림 (선택)
 */
const https = require('https');
const { lookupSku } = require('./payment-config');

// 글로벌 in-memory referral cache (invite-link.js / invite-track.js와 공유)
if (!global.__cmdReferralCache) global.__cmdReferralCache = new Map();
if (!global.__cmdVisitorIndex) global.__cmdVisitorIndex = new Map();
const referralCache = global.__cmdReferralCache;
const visitorIndex = global.__cmdVisitorIndex;

function tossConfirm(secretKey, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const auth = Buffer.from(secretKey + ':').toString('base64');
    const req = https.request(
      {
        hostname: 'api.tosspayments.com',
        port: 443,
        path: '/v1/payments/confirm',
        method: 'POST',
        headers: {
          Authorization: `Basic ${auth}`,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(data),
        },
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            const json = JSON.parse(buf);
            resolve({ status: res.statusCode, body: json });
          } catch (e) {
            resolve({ status: res.statusCode, body: { code: 'PARSE_ERROR', message: buf } });
          }
        });
      }
    );
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * 포트원 V2 결제 조회 (서버측 위변조 검증)
 * GET https://api.portone.io/payments/{paymentId}
 * Auth: "PortOne {API_SECRET}"
 *
 * 응답에서 status === 'PAID' && amount.total === 기대금액 인지 확인.
 * Docs: https://developers.portone.io/api/rest-v2/payment
 */
function portoneGetPayment(apiSecret, paymentId) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: 'api.portone.io',
        port: 443,
        path: '/payments/' + encodeURIComponent(paymentId),
        method: 'GET',
        headers: {
          Authorization: 'PortOne ' + apiSecret,
          'Content-Type': 'application/json',
        },
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            const json = JSON.parse(buf);
            resolve({ status: res.statusCode, body: json });
          } catch (e) {
            resolve({ status: res.statusCode, body: { type: 'PARSE_ERROR', message: buf } });
          }
        });
      }
    );
    req.on('error', reject);
    req.end();
  });
}

/**
 * PayPal OAuth2 access token (client_credentials)
 * Docs: https://developer.paypal.com/api/rest/authentication/
 */
function paypalAccessToken(clientId, secret, env) {
  const hostname = env === 'sandbox' ? 'api-m.sandbox.paypal.com' : 'api-m.paypal.com';
  const auth = Buffer.from(clientId + ':' + secret).toString('base64');
  const data = 'grant_type=client_credentials';
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname,
        port: 443,
        path: '/v1/oauth2/token',
        method: 'POST',
        headers: {
          Authorization: 'Basic ' + auth,
          'Content-Type': 'application/x-www-form-urlencoded',
          'Content-Length': Buffer.byteLength(data),
        },
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            const json = JSON.parse(buf);
            resolve({ status: res.statusCode, body: json });
          } catch (e) {
            resolve({ status: res.statusCode, body: { error: 'PARSE_ERROR', raw: buf } });
          }
        });
      }
    );
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * PayPal GET order — capture 후 status === 'COMPLETED' 확인 + amount 검증
 * Docs: https://developer.paypal.com/docs/api/orders/v2/#orders_get
 */
function paypalGetOrder(accessToken, orderId, env) {
  const hostname = env === 'sandbox' ? 'api-m.sandbox.paypal.com' : 'api-m.paypal.com';
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname,
        port: 443,
        path: '/v2/checkout/orders/' + encodeURIComponent(orderId),
        method: 'GET',
        headers: {
          Authorization: 'Bearer ' + accessToken,
          'Content-Type': 'application/json',
        },
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            const json = JSON.parse(buf);
            resolve({ status: res.statusCode, body: json });
          } catch (e) {
            resolve({ status: res.statusCode, body: { error: 'PARSE_ERROR', raw: buf } });
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

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const tgChat = (process.env.TELEGRAM_CHAT_ID || '').trim();

  // body 파싱 (Vercel은 자동 파싱하지만 안전장치)
  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  // provider: 'toss' (기본/현재) | 'portone-kcn' | 'portone-kakaopay' | 'paypal'
  const provider = (body.provider || 'toss').toString();
  const isPortOne = provider === 'portone-kcn' || provider === 'portone-kakaopay' || provider === 'portone';
  const isPaypal = provider === 'paypal';

  const { paymentKey, orderId, amount, skuId, customerEmail, invitedBy_code, visitor_id } = body;
  // 포트원은 paymentId 필드도 허용 (paymentKey가 없을 때)
  const paymentId = body.paymentId || paymentKey;

  if (!paymentId || !orderId || amount === undefined) {
    return res
      .status(400)
      .json({ success: false, error: 'paymentKey/paymentId, orderId, amount 필수' });
  }

  // 서버측 SKU 가격 검증 (위변조 방지)
  const sku = skuId ? lookupSku(skuId) : null;
  if (!sku) {
    return res.status(400).json({ success: false, error: `유효하지 않은 SKU: ${skuId}` });
  }
  if (Number(amount) !== Number(sku.amount)) {
    return res.status(400).json({
      success: false,
      error: `금액 불일치: SKU ${skuId} 정가 ${sku.amount}, 받은 금액 ${amount}`,
    });
  }

  // ─── Provider별 PG 승인/검증 분기 ────────────────────────────
  let normalizedBody;
  let normalizedMethod;
  let normalizedReceiptUrl;
  let normalizedApprovedAt;

  try {
    if (isPaypal) {
      // PayPal Smart Buttons (글로벌) — 클라이언트 capture 후 서버측 위변조 검증
      const paypalClientId = (process.env.PAYPAL_CLIENT_ID || '').trim();
      const paypalSecret = (process.env.PAYPAL_CLIENT_SECRET || '').trim();
      const paypalEnv = (process.env.PAYPAL_ENV || 'production').trim();
      if (!paypalClientId || !paypalSecret) {
        return res
          .status(500)
          .json({ success: false, error: 'PAYPAL_CLIENT_ID/PAYPAL_CLIENT_SECRET 미설정' });
      }
      const tokResp = await paypalAccessToken(paypalClientId, paypalSecret, paypalEnv);
      const accessToken = tokResp.body && tokResp.body.access_token;
      if (tokResp.status !== 200 || !accessToken) {
        return res.status(502).json({
          success: false,
          error: 'PayPal OAuth 실패',
          raw: tokResp.body,
        });
      }
      const ordResp = await paypalGetOrder(accessToken, paymentId, paypalEnv);
      const ord = ordResp.body || {};
      if (ordResp.status !== 200 || ord.status !== 'COMPLETED') {
        return res.status(400).json({
          success: false,
          error: 'PayPal 결제 미완료/검증 실패',
          paypalStatus: ord.status,
          raw: ord,
        });
      }
      // 금액 검증 — PayPal USD vs SKU KRW 환산 (pay.html과 동일 환율 1380)
      const KRW_PER_USD = 1380;
      const expectedUsdRaw = sku.amount / KRW_PER_USD;
      const expectedUsd = Math.max(Number(expectedUsdRaw.toFixed(2)), 0.5);
      const pgUnit = (ord.purchase_units && ord.purchase_units[0]) || {};
      const captures = (pgUnit.payments && pgUnit.payments.captures) || [];
      const cap = captures[0] || {};
      const pgUsd = Number(
        (cap.amount && cap.amount.value) || (pgUnit.amount && pgUnit.amount.value) || 0
      );
      // 환율 변동 5% 허용 — 변동분이 더 크게 떨어진 경우만 거절
      if (pgUsd < expectedUsd * 0.95) {
        return res.status(400).json({
          success: false,
          error: 'PayPal 금액 불일치 (5% 허용범위 초과)',
          expectedUsd,
          paidUsd: pgUsd,
        });
      }
      normalizedBody = ord;
      normalizedMethod = 'paypal';
      const selfLink = ((cap.links || []).find((l) => l && l.rel === 'self') || {}).href;
      normalizedReceiptUrl = selfLink || null;
      normalizedApprovedAt =
        cap.create_time || ord.create_time || new Date().toISOString();
    } else if (isPortOne) {
      // 포트원 V2: 결제 조회로 위변조 검증 (서버 결제승인은 SDK가 PG로 직접 진행)
      const portoneSecret = (process.env.PORTONE_API_SECRET || '').trim();
      if (!portoneSecret) {
        return res.status(500).json({ success: false, error: 'PORTONE_API_SECRET 미설정' });
      }
      const { status, body: pBody } = await portoneGetPayment(portoneSecret, paymentId);
      if (status !== 200 || !pBody || pBody.status !== 'PAID') {
        return res.status(400).json({
          success: false,
          error: (pBody && pBody.message) || '포트원 결제 검증 실패',
          code: pBody && (pBody.code || pBody.type),
          raw: pBody,
        });
      }
      // 금액 재검증 (PG 응답 vs SKU 정가)
      const pgAmount = pBody.amount && (pBody.amount.total != null ? pBody.amount.total : pBody.amount.paid);
      if (Number(pgAmount) !== Number(sku.amount)) {
        return res.status(400).json({
          success: false,
          error: `PG 금액 불일치: SKU ${skuId} 정가 ${sku.amount}, PG 응답 ${pgAmount}`,
        });
      }
      normalizedBody = pBody;
      normalizedMethod = (pBody.method && (pBody.method.type || pBody.method.provider)) || provider;
      normalizedReceiptUrl = pBody.receiptUrl || (pBody.cashReceipt && pBody.cashReceipt.url) || null;
      normalizedApprovedAt = pBody.paidAt || pBody.requestedAt || new Date().toISOString();
    } else {
      // 토스 V2 (기존 흐름 100% 유지)
      const secretKey = (process.env.TOSS_SECRET_KEY || '').trim();
      if (!secretKey) {
        return res.status(500).json({ success: false, error: 'TOSS_SECRET_KEY 미설정' });
      }
      const { status, body: tossBody } = await tossConfirm(secretKey, {
        paymentKey: paymentId,
        orderId,
        amount: Number(amount),
      });
      if (status !== 200 || !tossBody || tossBody.status !== 'DONE') {
        return res.status(400).json({
          success: false,
          error: (tossBody && tossBody.message) || '결제 승인 실패',
          code: tossBody && tossBody.code,
          raw: tossBody,
        });
      }
      normalizedBody = tossBody;
      normalizedMethod = tossBody.method;
      normalizedReceiptUrl = tossBody.receipt && tossBody.receipt.url;
      normalizedApprovedAt = tossBody.approvedAt;
    }

    // 이하 알림/referral/응답 — provider 무관 공통
    const tossBody = normalizedBody; // 토스 응답 필드 호환 (아래 일부 사용)
    const pgCustomerEmail =
      (tossBody && tossBody.customerEmail) ||
      (tossBody && tossBody.customer && tossBody.customer.email) ||
      '';

    // 텔레그램 알림 (선택, 실패해도 결제는 성공)
    if (tgToken && tgChat) {
      const txt =
        `💰 <b>천명당 결제 완료</b>\n` +
        `상품: ${sku.name}\n` +
        `SKU: ${sku.id}\n` +
        `주문ID: ${orderId}\n` +
        `금액: ${Number(amount).toLocaleString('ko-KR')}원\n` +
        `PG: ${provider}\n` +
        `결제수단: ${normalizedMethod || '-'}\n` +
        `이메일: ${customerEmail || pgCustomerEmail || '-'}\n` +
        `시각: ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}`;
      sendTelegram(tgToken, tgChat, txt);
    }

    // === 초대 링크 통한 결제 시 referral 카운트 (중복 체크 포함) ===
    let referralResult = null;
    if (invitedBy_code && /^CMD[A-Z0-9]+$/.test(invitedBy_code)) {
      let record = referralCache.get(invitedBy_code);
      if (!record) {
        record = {
          code: invitedBy_code,
          owner_phone: '',
          owner_email: '',
          created_at: new Date().toISOString(),
          invited: [],
          first_month_free_granted: false,
        };
        referralCache.set(invitedBy_code, record);
      }

      // visitor 매칭: visitor_id 우선, 없으면 customerEmail로 결정성 fallback
      const vidKey = visitor_id || ('email:' + (customerEmail || orderId));
      let entry = (record.invited || []).find(
        (v) => v.visitor_id === vidKey || v.converted_email === customerEmail
      );

      if (!entry) {
        entry = { visitor_id: vidKey, visited_at: new Date().toISOString(), converted: false };
        record.invited.push(entry);
      }

      if (entry.converted) {
        // 이미 카운트 됨 → 무시
        referralResult = { duplicate: true, code: invitedBy_code };
      } else {
        entry.converted = true;
        entry.converted_at = new Date().toISOString();
        entry.converted_email = customerEmail || '';

        const convertedCount = record.invited.filter((v) => v.converted).length;
        referralResult = { duplicate: false, code: invitedBy_code, convertedCount };

        // 10명 도달 → 보상 트리거
        if (convertedCount >= 10 && !record.first_month_free_granted) {
          record.first_month_free_granted = true;
          record.granted_at = new Date().toISOString();

          if (tgToken && tgChat) {
            const reward =
              `🎉 <b>천명당 초대 10명 달성!</b>\n` +
              `code: ${invitedBy_code}\n` +
              `초대자 phone: ${record.owner_phone || '-'}\n` +
              `초대자 email: ${record.owner_email || '-'}\n` +
              `달성 시각: ${record.granted_at}\n\n` +
              `⚙️ 액션: subscribers.json에서 해당 owner의 ` +
              `<code>first_month_free: true</code> 플래그 설정 필요\n` +
              `다음 자동결제 1회 면제 처리`;
            sendTelegram(tgToken, tgChat, reward);
          }
        } else if (tgToken && tgChat) {
          // 일반 conversion 알림
          const msg =
            `✅ <b>천명당 초대 결제 전환</b>\n` +
            `code: ${invitedBy_code}\n` +
            `진행도: ${convertedCount}/10명\n` +
            `결제 이메일: ${customerEmail || '-'}\n` +
            `시각: ${entry.converted_at}`;
          sendTelegram(tgToken, tgChat, msg);
        }
      }
    }

    return res.status(200).json({
      success: true,
      provider: provider,
      orderId: (tossBody && tossBody.orderId) || orderId,
      orderName: (tossBody && tossBody.orderName) || sku.name,
      amount:
        (tossBody && tossBody.totalAmount) ||
        (tossBody && tossBody.amount && (tossBody.amount.total || tossBody.amount.paid)) ||
        Number(amount),
      method: normalizedMethod,
      receiptUrl: normalizedReceiptUrl,
      approvedAt: normalizedApprovedAt,
      sku: { id: sku.id, name: sku.name },
      referral: referralResult,
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
};
