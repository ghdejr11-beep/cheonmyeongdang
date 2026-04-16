/**
 * 텔레그램 알림 프록시 API
 * POST /api/notify
 *
 * 클라이언트 → 서버 → 텔레그램 (봇 토큰 서버에만 존재)
 */
const https = require('https');

function sendTelegram(token, chatId, text) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ chat_id: chatId, text: text, parse_mode: 'HTML' });
    const options = {
      hostname: 'api.telegram.org',
      port: 443,
      path: `/bot${token}/sendMessage`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    };
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (c) => body += c);
      res.on('end', () => resolve(body));
    });
    req.on('error', reject);
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

  const token = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const chatId = (process.env.TELEGRAM_CHAT_ID || '').trim();

  if (!token || !chatId) {
    return res.status(500).json({ error: 'Server not configured' });
  }

  const body = req.body || {};
  let text = '';

  // 입력 검증 + HTML 이스케이프
  const esc = (s) => String(s || '').replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));

  if (body.type === 'preregister') {
    const email = esc(body.email).slice(0, 100);
    const phone = esc(body.phone || '').slice(0, 30);
    const job = esc(body.job || '').slice(0, 30);
    if (!email || email.indexOf('@') === -1) {
      return res.status(400).json({ error: 'Invalid email' });
    }
    // 부서 수익 집계 채널에도 동시 발송 (매 사전예약 = 미래 매출 1건)
    const jobLabels = {
      freelancer: '💼 프리랜서', shop: '🏪 자영업자', creator: '🎬 크리에이터',
      worker: '🛵 플랫폼노동자', employee: '💻 직장인부업', insurance: '🛡️ 보험설계사',
    };
    const jobTxt = jobLabels[job] || job || '-';
    text = `🎯 <b>세금N혜택 사전예약</b>\n`
         + `이메일: ${email}\n`
         + (phone ? `전화: ${phone}\n` : '')
         + `직종: ${jobTxt}\n`
         + `시간: ${new Date().toLocaleString('ko-KR', {timeZone: 'Asia/Seoul'})}\n\n`
         + `💰 <i>환급 서비스 오픈 시 인당 ~15,000원 수익 예상</i>`;
  } else if (body.type === 'consultation') {
    const name = esc(body.name).slice(0, 50);
    const phone = esc(body.phone).slice(0, 30);
    if (!name || !phone) {
      return res.status(400).json({ error: 'Missing fields' });
    }
    text = `📞 <b>세무사 상담 신청</b>\n성함: ${name}\n연락처: ${phone}\n시간: ${new Date().toLocaleString('ko-KR')}`;
  } else {
    return res.status(400).json({ error: 'Invalid type' });
  }

  try {
    await sendTelegram(token, chatId, text);
    return res.status(200).json({ success: true });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
};
