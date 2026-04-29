/**
 * 천명당 초대 방문 추적 API
 * POST /api/invite-track
 * Body: { ref, vid }
 *
 * 핵심: **중복 체크**
 *   - 같은 visitor_id(브라우저 UUID + IP/UA hash)가 이미 invited 배열에 있으면 무시
 *   - 한 visitor는 글로벌(모든 코드)에서 한 번만 카운트
 *   - 초대자 본인 visitor가 자기 코드 클릭 시에도 무시 (selfRef)
 *
 * 영속화: in-memory cache + 텔레그램 백업 (관리자 메시지로 데이터 보존)
 */
const https = require('https');
const crypto = require('crypto');

if (!global.__cmdReferralCache) global.__cmdReferralCache = new Map();
if (!global.__cmdVisitorIndex) global.__cmdVisitorIndex = new Map(); // visitor_id → code (글로벌 중복 차단)
const cache = global.__cmdReferralCache;
const visitorIndex = global.__cmdVisitorIndex;

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

function hashVisitor(vid, ip, ua) {
  // visitor_id 정규화: 브라우저 UUID + IP + UA 결합 SHA256 앞 16자
  // 같은 사람이 ref 파라미터 바꿔도 동일 visitor로 인식되도록
  const raw = `${vid || ''}|${ip || ''}|${(ua || '').slice(0, 80)}`;
  return crypto.createHash('sha256').update(raw).digest('hex').slice(0, 16);
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

  const ref = (body.ref || '').trim().toUpperCase();
  const rawVid = (body.vid || '').trim();
  if (!ref || !/^CMD[A-Z0-9]+$/.test(ref)) {
    return res.status(400).json({ success: false, error: 'invalid ref code' });
  }
  if (!rawVid) {
    return res.status(400).json({ success: false, error: 'vid required' });
  }

  // 클라이언트 IP + UA 추출 (Vercel 헤더)
  const ip =
    (req.headers['x-forwarded-for'] || '').split(',')[0].trim() ||
    req.headers['x-real-ip'] ||
    '';
  const ua = req.headers['user-agent'] || '';

  const visitorId = hashVisitor(rawVid, ip, ua);

  // === 글로벌 중복 체크 (visitor 1명 = 1코드만 카운트) ===
  const existingCode = visitorIndex.get(visitorId);
  if (existingCode) {
    // 이미 다른 코드로 카운트된 visitor → 무시 (첫 번째 ref만 유효)
    return res.status(200).json({
      success: true,
      duplicate: true,
      reason: existingCode === ref ? 'already_tracked_same_code' : 'already_tracked_different_code',
      visitorId,
    });
  }

  // referral 레코드 조회/생성
  let record = cache.get(ref);
  if (!record) {
    record = {
      code: ref,
      owner_phone: '',
      owner_email: '',
      created_at: new Date().toISOString(),
      invited: [],
      first_month_free_granted: false,
    };
    cache.set(ref, record);
  }

  // 한 번 더 안전: 이 코드 내에서 같은 visitor가 있는지 (cache가 다른 인스턴스에서 채워졌을 가능성)
  if ((record.invited || []).some((v) => v.visitor_id === visitorId)) {
    visitorIndex.set(visitorId, ref);
    return res.status(200).json({
      success: true,
      duplicate: true,
      reason: 'already_in_record',
      visitorId,
    });
  }

  // 신규 visitor 등록
  const entry = {
    visitor_id: visitorId,
    visited_at: new Date().toISOString(),
    converted: false,
  };
  record.invited.push(entry);
  visitorIndex.set(visitorId, ref);

  // 텔레그램 백업 (영속화 fallback)
  const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const adminChat = (process.env.TELEGRAM_CHAT_ID || '').trim();
  if (tgToken && adminChat) {
    const totalVisits = record.invited.length;
    const msg =
      `👀 <b>천명당 초대 방문</b>\n` +
      `code: ${ref}\n` +
      `visitor_id: ${visitorId}\n` +
      `ip: ${ip || '-'}\n` +
      `방문 누적: ${totalVisits}명 (결제 전)\n` +
      `시각: ${entry.visited_at}`;
    sendTelegram(tgToken, adminChat, msg);
  }

  return res.status(200).json({
    success: true,
    duplicate: false,
    visitorId,
    visitedCount: record.invited.length,
    convertedCount: record.invited.filter((v) => v.converted).length,
  });
};
