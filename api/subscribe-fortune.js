/**
 * 천명당 월회원 운세 발송 등록 API
 * POST /api/subscribe-fortune
 *
 * 결제 완료 직후 success.html 또는 pay.html에서 호출.
 * 월회원(subscribe_monthly_9900) 결제 시 생년월일/생시/성별/연락 채널을 받아
 * 일일 운세 발송 대상자 명단에 등록한다.
 *
 * 흐름:
 *   1) Vercel은 파일 시스템에 영구 쓰기 불가 → Telegram 봇으로 신규 가입자 정보를
 *      관리자 chat_id에 전송 (사용자 PC subscribers.json은 별도 sync 스크립트로 채움)
 *   2) 동시에 신규 가입자에게 환영 메시지 + 운세 발송 시간 안내 전송
 *
 * Body: {
 *   orderId, skuId, paymentKey,
 *   name, email, phone,
 *   birth_date, birth_time, birth_calendar, gender,
 *   channel ('telegram'|'kakao'|'email'),
 *   telegram_chat_id (channel=telegram 시 필수)
 * }
 */
const https = require('https');

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
        res.on('end', () => {
          try {
            resolve({ status: res.statusCode, body: JSON.parse(buf) });
          } catch (e) {
            resolve({ status: res.statusCode, body: buf });
          }
        });
      }
    );
    req.on('error', () => resolve({ status: 0, body: null }));
    req.write(data);
    req.end();
  });
}

function addDaysISO(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const adminChat = (process.env.TELEGRAM_CHAT_ID || '').trim();
  if (!tgToken || !adminChat) {
    return res.status(500).json({ success: false, error: '서버 설정 오류 (TELEGRAM 미설정)' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  const {
    orderId, skuId, paymentKey,
    name, email, phone,
    birth_date, birth_time, birth_calendar, gender,
    channel, telegram_chat_id, kakao_id,
  } = body;

  // 필수 검증 — 정기결제 SKU 화이트리스트 (legacy + 신규 2종)
  const ALLOWED_SUBSCRIPTION_SKUS = [
    'subscribe_monthly_9900',
    'subscribe_monthly_29900',
    'subscribe_basic_2900',
  ];
  if (!orderId || !ALLOWED_SUBSCRIPTION_SKUS.includes(skuId)) {
    return res.status(400).json({ success: false, error: '정기결제 SKU만 등록 가능' });
  }
  if (!birth_date || !gender) {
    return res.status(400).json({ success: false, error: '생년월일·성별 필수' });
  }
  const ch = (channel || 'telegram').toLowerCase();
  if (ch === 'telegram' && !telegram_chat_id) {
    return res.status(400).json({ success: false, error: 'Telegram chat_id 필수' });
  }

  const userId = 'cm_' + (orderId || Date.now()) + '_' + Math.random().toString(36).slice(2, 6);
  const paidUntil = addDaysISO(30);

  const record = {
    user_id: userId,
    name: name || '',
    email: email || '',
    phone: phone || '',
    kakao_id: kakao_id || '',
    telegram_chat_id: telegram_chat_id || '',
    channel: ch,
    birth_date,
    birth_time: birth_time || '12:00',
    birth_calendar: birth_calendar || 'solar',
    gender,
    paid_until: paidUntil,
    order_id: orderId,
    sku_id: skuId,
    payment_key: paymentKey || '',
    created_at: new Date().toISOString(),
    last_sent: '',
    active: true,
  };

  // 1) 관리자에게 신규 구독자 정보 전송 (Python sync 스크립트가 이 메시지를 파싱)
  const adminMsg =
    `🪷 <b>천명당 월회원 신규 가입</b>\n` +
    `<pre>${JSON.stringify(record, null, 2)}</pre>\n` +
    `※ daily_fortune_send.py가 이 정보를 받아 매일 08:00 발송`;
  await sendTelegram(tgToken, adminChat, adminMsg);

  // 2) 가입자(텔레그램 채널 시)에게 환영 메시지
  if (ch === 'telegram' && telegram_chat_id) {
    const welcome =
      `🪷 <b>천명당 월회원 가입 완료</b>\n\n` +
      `${name || '회원'}님, 환영합니다.\n\n` +
      `매일 오전 8시, 본인 사주 기반 <b>오늘의 운세</b>를\n` +
      `이 채팅으로 보내드립니다.\n\n` +
      `📅 구독 기간: ~${paidUntil}\n` +
      `🔔 첫 발송: 내일 오전 8시\n` +
      `💌 문의: ghdejr11@gmail.com`;
    await sendTelegram(tgToken, telegram_chat_id, welcome);
  }

  return res.status(200).json({
    success: true,
    user_id: userId,
    paid_until: paidUntil,
    message: '운세 발송 등록 완료. 매일 오전 8시 발송됩니다.',
  });
};
