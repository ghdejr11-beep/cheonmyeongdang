/**
 * 천명당 행운패스 등록 API
 * POST /api/lucky-pass
 *
 * 행운패스 = 이메일 OR 카카오 채널 추가 1회로 24h 광고 OFF + 매주 운세 뉴스레터 push
 * 본 endpoint는 이메일 등록 경로만 처리 (카톡 채널 추가는 클라이언트에서 LocalStorage 만 토글).
 *
 * Body: { email, source? ('lucky_pass'), referer? }
 *
 * 흐름:
 *  1) 이메일 형식 검증 (간단)
 *  2) 텔레그램 봇으로 관리자에 신규 구독자 알림 (Vercel은 파일 영구 쓰기 X)
 *  3) GitHub Gist에 누적 (lucky_pass_subscribers.json)
 *  4) JSON 응답 → 클라이언트가 localStorage에 cm_lucky_pass_until = now+24h 저장
 *
 * Env:
 *  - TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
 *  - GITHUB_TOKEN (Gist scope), GIST_ID (선택, 없으면 신규 Gist 생성 시 텔레그램으로 ID 안내)
 */
const https = require('https');

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function jsonReq(opts, body) {
  return new Promise((resolve) => {
    const data = body ? JSON.stringify(body) : null;
    if (data) {
      opts.headers = opts.headers || {};
      opts.headers['Content-Type'] = 'application/json';
      opts.headers['Content-Length'] = Buffer.byteLength(data);
    }
    const req = https.request(opts, (res) => {
      let buf = '';
      res.on('data', (c) => (buf += c));
      res.on('end', () => {
        let parsed = null;
        try { parsed = JSON.parse(buf); } catch (e) {}
        resolve({ ok: res.statusCode >= 200 && res.statusCode < 300, status: res.statusCode, body: parsed, raw: buf });
      });
    });
    req.on('error', () => resolve({ ok: false, status: 0, body: null }));
    if (data) req.write(data);
    req.end();
  });
}

async function notifyTelegram(token, chatId, text) {
  if (!token || !chatId) return;
  return jsonReq(
    {
      hostname: 'api.telegram.org',
      port: 443,
      path: `/bot${token}/sendMessage`,
      method: 'POST',
    },
    { chat_id: chatId, text, parse_mode: 'HTML', disable_web_page_preview: true }
  );
}

async function appendToGist(token, gistId, email, source, referer) {
  if (!token || !gistId) return null;
  // Read current
  const cur = await jsonReq({
    hostname: 'api.github.com',
    port: 443,
    path: `/gists/${gistId}`,
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'User-Agent': 'cheonmyeongdang-lucky-pass',
    },
  });
  let data = { subscribers: [] };
  try {
    const file = cur.body && cur.body.files && cur.body.files['lucky_pass_subscribers.json'];
    if (file && file.content) data = JSON.parse(file.content);
    if (!Array.isArray(data.subscribers)) data.subscribers = [];
  } catch (e) {}
  // De-dup
  const exists = data.subscribers.find((s) => s.email === email);
  if (exists) {
    exists.last_active_at = new Date().toISOString();
    exists.activations = (exists.activations || 1) + 1;
  } else {
    data.subscribers.push({
      email,
      source: source || 'lucky_pass',
      referer: referer || '',
      created_at: new Date().toISOString(),
      last_active_at: new Date().toISOString(),
      activations: 1,
    });
  }
  return jsonReq(
    {
      hostname: 'api.github.com',
      port: 443,
      path: `/gists/${gistId}`,
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'User-Agent': 'cheonmyeongdang-lucky-pass',
      },
    },
    {
      files: {
        'lucky_pass_subscribers.json': { content: JSON.stringify(data, null, 2) },
      },
    }
  );
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method' });

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  const email = String(body.email || '').trim().toLowerCase();
  const source = String(body.source || 'lucky_pass').slice(0, 32);
  const referer = String(req.headers['referer'] || body.referer || '').slice(0, 256);

  if (!EMAIL_RE.test(email) || email.length > 200) {
    return res.status(400).json({ ok: false, error: 'invalid_email' });
  }

  // Persist (best-effort, errors must not fail user response)
  try {
    const tgToken = process.env.TELEGRAM_BOT_TOKEN;
    const tgChat = process.env.TELEGRAM_CHAT_ID;
    const ghToken = process.env.GITHUB_TOKEN;
    const gistId = process.env.GIST_LUCKY_PASS_ID || process.env.GIST_ID;

    const tasks = [];
    if (tgToken && tgChat) {
      tasks.push(
        notifyTelegram(
          tgToken,
          tgChat,
          `🎫 <b>행운패스 신규</b>\n` +
            `email: <code>${email}</code>\n` +
            `source: ${source}\n` +
            `referer: ${referer || '-'}`
        ).catch(() => null)
      );
    }
    if (ghToken && gistId) {
      tasks.push(appendToGist(ghToken, gistId, email, source, referer).catch(() => null));
    }
    if (tasks.length) await Promise.all(tasks);
  } catch (e) {
    // swallow — lucky pass UX must succeed even if persistence fails
  }

  return res.status(200).json({
    ok: true,
    email,
    expires_in_hours: 24,
    next_steps: [
      'localStorage cm_lucky_pass_until = Date.now() + 24*3600*1000',
      'cmLuckyPass.activate(24)',
    ],
  });
};
