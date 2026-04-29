/**
 * 토스페이먼츠 결제 승인 API
 * POST /api/confirm-payment
 * Body: { paymentKey, orderId, amount }
 *
 * 흐름:
 *   1) 클라이언트 위젯 successUrl 콜백 → 이 API 호출
 *   2) 시크릿 키로 https://api.tosspayments.com/v1/payments/confirm 호출
 *   3) 검증 후 영수증 URL + 주문 정보 반환
 *
 * 보안:
 *   - 시크릿 키는 서버에서만 사용 (Basic Auth: base64(secretKey + ":"))
 *   - 금액 검증: 클라이언트가 보낸 amount === TOSS_FIXED_AMOUNT 여부 체크
 */
const https = require('https');

function tossConfirm(secretKey, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const auth = Buffer.from(secretKey + ':').toString('base64');
    const req = https.request({
      hostname: 'api.tosspayments.com',
      port: 443,
      path: '/v1/payments/confirm',
      method: 'POST',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    }, (res) => {
      let buf = '';
      res.on('data', (c) => buf += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(buf);
          resolve({ status: res.statusCode, body: json });
        } catch (e) {
          resolve({ status: res.statusCode, body: { code: 'PARSE_ERROR', message: buf } });
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function sendTelegram(token, chatId, text) {
  return new Promise((resolve) => {
    const data = JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML' });
    const req = https.request({
      hostname: 'api.telegram.org',
      port: 443,
      path: `/bot${token}/sendMessage`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    }, (res) => {
      let buf = '';
      res.on('data', (c) => buf += c);
      res.on('end', () => resolve(buf));
    });
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

  const secretKey = (process.env.TOSS_SECRET_KEY || '').trim();
  const fixedAmount = Number(process.env.TOSS_FIXED_AMOUNT || 9900);
  const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const tgChat = (process.env.TELEGRAM_CHAT_ID || '').trim();

  if (!secretKey) {
    return res.status(500).json({ success: false, error: 'TOSS_SECRET_KEY 미설정' });
  }

  const { paymentKey, orderId, amount } = req.body || {};
  if (!paymentKey || !orderId || amount === undefined) {
    return res.status(400).json({ success: false, error: 'paymentKey, orderId, amount 필수' });
  }

  // 금액 위변조 방지 — 서버에서 정한 금액과 일치해야 함
  if (Number(amount) !== fixedAmount) {
    return res.status(400).json({
      success: false,
      error: `금액 불일치: expected ${fixedAmount}, got ${amount}`,
    });
  }

  try {
    const { status, body } = await tossConfirm(secretKey, {
      paymentKey,
      orderId,
      amount: Number(amount),
    });

    if (status !== 200 || !body || body.status !== 'DONE') {
      return res.status(400).json({
        success: false,
        error: (body && body.message) || '결제 승인 실패',
        code: body && body.code,
        raw: body,
      });
    }

    // 텔레그램 알림 (선택, 실패해도 결제는 성공)
    if (tgToken && tgChat) {
      const txt = `💳 <b>세금N혜택 결제 완료</b>\n`
                + `주문ID: ${orderId}\n`
                + `금액: ${Number(amount).toLocaleString('ko-KR')}원\n`
                + `결제수단: ${body.method || '-'}\n`
                + `이메일: ${(body.customerEmail || '-')}\n`
                + `시각: ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}`;
      sendTelegram(tgToken, tgChat, txt);
    }

    return res.status(200).json({
      success: true,
      orderId: body.orderId,
      orderName: body.orderName,
      amount: body.totalAmount,
      method: body.method,
      receiptUrl: body.receipt && body.receipt.url,
      approvedAt: body.approvedAt,
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
};
