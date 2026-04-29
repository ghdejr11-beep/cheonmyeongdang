/**
 * 천명당 초대 링크 생성 API
 * POST /api/invite-link
 * Body: { phone, email }
 *
 * 흐름:
 *   1) 사용자 식별자(phone 우선, 없으면 email)로 결정성 코드 생성
 *      - 같은 사용자가 여러 번 호출해도 항상 같은 code 반환 (idempotent)
 *   2) Vercel은 영속 디스크 X → 코드는 hash 기반 결정성 알고리즘으로 생성하고
 *      텔레그램 관리자 채팅에 referrals.json append 요청 메시지 송신
 *   3) 사용자에게 shareUrl + 현재까지 누적된 invited 카운트 응답
 *
 * 영속화:
 *   - 코드 자체는 hash 기반이라 stateless하게 재현 가능
 *   - invited 카운트는 글로벌 in-memory cache (Lambda warm) + 텔레그램 백업
 *   - 추후 Upstash Redis 도입 시 readReferrals/writeReferrals 함수 1곳만 교체
 */
const https = require('https');
const crypto = require('crypto');

// 동일 Lambda 인스턴스 내에서 invited 카운트 메모리 캐시
// (cold start 시 초기화 → 텔레그램 메시지 로그가 fact-of-truth)
if (!global.__cmdReferralCache) global.__cmdReferralCache = new Map();
const cache = global.__cmdReferralCache;

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
        res.on('end', () => resolve({ status: res.statusCode, body: buf }));
      }
    );
    req.on('error', () => resolve({ status: 0 }));
    req.write(data);
    req.end();
  });
}

function genCode(identifier) {
  // 결정성 8자 코드 (같은 phone/email → 같은 code)
  // SHA1 → base36 → 앞 6자 + CMD prefix (총 9자)
  const h = crypto.createHash('sha1').update('cmd-salt-2026:' + identifier).digest('hex');
  const num = parseInt(h.slice(0, 12), 16);
  return 'CMD' + num.toString(36).toUpperCase().slice(0, 6).padStart(6, '0');
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  const phone = (body.phone || '').trim().replace(/[^0-9]/g, '');
  const email = (body.email || '').trim().toLowerCase();
  const identifier = phone || email;

  if (!identifier || (phone && phone.length < 10) || (!phone && !email.includes('@'))) {
    return res.status(400).json({
      success: false,
      error: '휴대폰 번호 또는 이메일이 필요합니다.',
    });
  }

  const code = genCode(identifier);
  const shareUrl = `https://cheonmyeongdang.vercel.app/?ref=${code}`;

  // in-memory 카운트 조회 (없으면 0)
  let record = cache.get(code);
  if (!record) {
    record = {
      code,
      owner_phone: phone || '',
      owner_email: email || '',
      created_at: new Date().toISOString(),
      invited: [],
      first_month_free_granted: false,
    };
    cache.set(code, record);

    // 신규 코드 생성을 텔레그램 관리자에 알림 (영속화 백업)
    const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
    const adminChat = (process.env.TELEGRAM_CHAT_ID || '').trim();
    if (tgToken && adminChat) {
      const msg =
        `🎁 <b>천명당 초대 링크 생성</b>\n` +
        `code: ${code}\n` +
        `phone: ${phone || '-'}\n` +
        `email: ${email || '-'}\n` +
        `shareUrl: ${shareUrl}\n` +
        `created: ${record.created_at}\n` +
        `※ referrals.json에 append 필요 (sync 스크립트)`;
      sendTelegram(tgToken, adminChat, msg);
    }
  }

  return res.status(200).json({
    success: true,
    code,
    shareUrl,
    invitedCount: (record.invited || []).filter((v) => v.converted).length,
    visitedCount: (record.invited || []).length,
    goal: 10,
  });
};
