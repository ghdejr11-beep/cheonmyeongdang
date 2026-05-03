/**
 * 천명당 초대 통합 API (link + track 합본 - Vercel Hobby 12 함수 한계 대응)
 *
 * POST /api/invite?action=link
 *   Body: { phone, email }
 *   → 초대 링크 코드 생성 (idempotent)
 *
 * POST /api/invite?action=track
 *   Body: { ref, vid }
 *   → 초대 방문 추적 (visitor 중복 차단)
 *
 * 또는 body.action 으로도 분기 가능 (호환성).
 */
const https = require('https');
const crypto = require('crypto');

if (!global.__cmdReferralCache) global.__cmdReferralCache = new Map();
if (!global.__cmdVisitorIndex) global.__cmdVisitorIndex = new Map();
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

function genCode(identifier) {
  const h = crypto.createHash('sha1').update('cmd-salt-2026:' + identifier).digest('hex');
  const num = parseInt(h.slice(0, 12), 16);
  return 'CMD' + num.toString(36).toUpperCase().slice(0, 6).padStart(6, '0');
}

function hashVisitor(vid, ip, ua) {
  const raw = `${vid || ''}|${ip || ''}|${(ua || '').slice(0, 80)}`;
  return crypto.createHash('sha256').update(raw).digest('hex').slice(0, 16);
}

// ─── action=link 핸들러 ───
async function handleLink(req, res, body) {
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

    const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
    const adminChat = (process.env.TELEGRAM_CHAT_ID || '').trim();
    if (tgToken && adminChat) {
      const msg =
        `🎁 <b>천명당 초대 링크 생성</b>\n` +
        `code: ${code}\nphone: ${phone || '-'}\nemail: ${email || '-'}\n` +
        `shareUrl: ${shareUrl}\ncreated: ${record.created_at}\n※ referrals.json에 append 필요`;
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
}

// ─── action=track 핸들러 ───
async function handleTrack(req, res, body) {
  const ref = (body.ref || '').trim().toUpperCase();
  const rawVid = (body.vid || '').trim();
  if (!ref || !/^CMD[A-Z0-9]+$/.test(ref)) {
    return res.status(400).json({ success: false, error: 'invalid ref code' });
  }
  if (!rawVid) {
    return res.status(400).json({ success: false, error: 'vid required' });
  }

  const ip =
    (req.headers['x-forwarded-for'] || '').split(',')[0].trim() ||
    req.headers['x-real-ip'] || '';
  const ua = req.headers['user-agent'] || '';

  const visitorId = hashVisitor(rawVid, ip, ua);

  const existingCode = visitorIndex.get(visitorId);
  if (existingCode) {
    return res.status(200).json({
      success: true,
      duplicate: true,
      reason: existingCode === ref ? 'already_tracked_same_code' : 'already_tracked_different_code',
      visitorId,
    });
  }

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

  if ((record.invited || []).some((v) => v.visitor_id === visitorId)) {
    visitorIndex.set(visitorId, ref);
    return res.status(200).json({
      success: true,
      duplicate: true,
      reason: 'already_in_record',
      visitorId,
    });
  }

  const entry = {
    visitor_id: visitorId,
    visited_at: new Date().toISOString(),
    converted: false,
  };
  record.invited.push(entry);
  visitorIndex.set(visitorId, ref);

  const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const adminChat = (process.env.TELEGRAM_CHAT_ID || '').trim();
  if (tgToken && adminChat) {
    const totalVisits = record.invited.length;
    const msg =
      `👀 <b>천명당 초대 방문</b>\n` +
      `code: ${ref}\nvisitor_id: ${visitorId}\nip: ${ip || '-'}\n` +
      `방문 누적: ${totalVisits}명 (결제 전)\n시각: ${entry.visited_at}`;
    sendTelegram(tgToken, adminChat, msg);
  }

  return res.status(200).json({
    success: true,
    duplicate: false,
    visitorId,
    visitedCount: record.invited.length,
    convertedCount: record.invited.filter((v) => v.converted).length,
  });
}

// ─── action=newsletter 핸들러 (K-Wisdom Daily 구독) ───
if (!global.__cmdNewsletterSubs) global.__cmdNewsletterSubs = new Map();
const newsletterSubs = global.__cmdNewsletterSubs;

async function handleNewsletter(req, res, body) {
  const email = (body.email || '').toString().trim().toLowerCase();
  const source = (body.source || 'unknown').toString().slice(0, 60);

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ success: false, error: 'Invalid email' });
  }

  // Idempotent — 중복 구독 방지
  const existing = newsletterSubs.get(email);
  if (existing) {
    return res.status(200).json({
      success: true,
      duplicate: true,
      subscribed_at: existing.subscribed_at,
    });
  }

  const record = {
    email,
    source,
    subscribed_at: new Date().toISOString(),
    confirmed: false,
  };
  newsletterSubs.set(email, record);

  // 텔레그램 알림 (신규 구독자)
  const tgToken = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const adminChat = (process.env.TELEGRAM_CHAT_ID || '').trim();
  if (tgToken && adminChat) {
    const totalSubs = newsletterSubs.size;
    const msg =
      `📬 <b>K-Wisdom Newsletter 신규 구독</b>\n` +
      `email: ${email}\n` +
      `source: ${source}\n` +
      `누적: ${totalSubs}명\n` +
      `시각: ${record.subscribed_at}`;
    sendTelegram(tgToken, adminChat, msg);
  }

  return res.status(200).json({
    success: true,
    duplicate: false,
    subscribed_at: record.subscribed_at,
    total_subs: newsletterSubs.size,
  });
}

// ─── 라우터 ───
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

  // action: 1) query string  2) body.action
  const action = (req.query?.action || body.action || '').toLowerCase();

  if (action === 'link') return handleLink(req, res, body);
  if (action === 'track') return handleTrack(req, res, body);
  if (action === 'newsletter') return handleNewsletter(req, res, body);

  return res.status(400).json({
    success: false,
    error: 'action required (link, track, or newsletter)',
    usage: '/api/invite?action=link  or  /api/invite?action=track',
  });
};
