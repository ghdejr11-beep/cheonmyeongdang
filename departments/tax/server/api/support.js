/**
 * 고객센터 API — 불만/요청 접수 + Claude 자동 분류
 * POST /api/support
 *
 * Body: { service, category, title, content, email, severity }
 *
 * 분류 로직 (Claude agent가 나중에 재판정):
 *  - auto_fix: 오타/링크깨짐/UI버그 (Claude가 자동 수정 PR)
 *  - needs_approval: 기능 추가/정책 변경 (CEO에게 물어봄)
 *  - reject: 사기/스팸/불법 (자동 거부)
 *  - bug_report: 기능 오류 (로그 확인 후 수정)
 */
const https = require('https');
const fs = require('fs');
const path = require('path');

function sendTelegram(token, chatId, text) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ chat_id: chatId, text, parse_mode: 'HTML', disable_web_page_preview: true });
    const req = https.request({
      hostname: 'api.telegram.org', port: 443,
      path: `/bot${token}/sendMessage`, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) },
    }, (res) => { let b = ''; res.on('data', c => b += c); res.on('end', () => resolve(b)); });
    req.on('error', reject);
    req.write(data); req.end();
  });
}

// 자동 분류 휴리스틱 (Claude가 나중에 재판정)
function preClassify(title, content) {
  const t = (title + ' ' + content).toLowerCase();

  // 스팸/사기 키워드
  const spamWords = ['비트코인', '도박', '성인', '불법', '가격제안', '투자권유', 'viagra', 'casino'];
  if (spamWords.some(w => t.includes(w))) return 'reject';

  // 간단 수정 (오타/링크)
  const simpleFix = ['오타', '깨짐', '링크 안 됨', '이미지 안 보임', '버튼 안 먹힘', '폰트', '색상'];
  if (simpleFix.some(w => t.includes(w))) return 'auto_fix';

  // 새 기능 요청
  const featureWords = ['추가해', '만들어', '있었으면', '바꿔줘', '수정해'];
  if (featureWords.some(w => t.includes(w))) return 'needs_approval';

  // 버그 리포트
  const bugWords = ['안 돼', '작동 안', '에러', '오류', '계산', '틀림', 'error'];
  if (bugWords.some(w => t.includes(w))) return 'bug_report';

  return 'general';
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const token = (process.env.TELEGRAM_BOT_TOKEN || '').trim();
  const chatId = (process.env.TELEGRAM_CHAT_ID || '').trim();
  if (!token || !chatId) return res.status(500).json({ error: 'Server not configured' });

  const body = req.body || {};
  const esc = (s) => String(s || '').replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));

  const service = esc(body.service || '알수없음').slice(0, 50);
  const category = esc(body.category || '일반').slice(0, 50);
  const title = esc(body.title || '').slice(0, 100);
  const content = esc(body.content || '').slice(0, 2000);
  const email = esc(body.email || '').slice(0, 100);

  if (!title || !content) {
    return res.status(400).json({ error: '제목·내용을 입력해주세요.' });
  }

  const classification = preClassify(title, content);
  const badges = {
    auto_fix: '🔧 <b>자동수정 가능</b>',
    needs_approval: '🤔 <b>CEO 판단 필요</b>',
    reject: '🚫 <b>스팸/부적절</b>',
    bug_report: '🐞 <b>버그 리포트</b>',
    general: '💬 <b>일반 문의</b>',
  };

  const text = `${badges[classification]}\n\n`
    + `📍 <b>서비스</b>: ${service}\n`
    + `📂 <b>카테고리</b>: ${category}\n\n`
    + `<b>${title}</b>\n\n`
    + `${content}\n\n`
    + (email ? `✉️ ${email}\n` : '')
    + `⏰ ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}`;

  try {
    await sendTelegram(token, chatId, text);

    // TODO: Claude Agent SDK로 분류 재판정 + auto_fix는 PR 자동 생성
    // 현재는 알림만, 다음 단계에서 자동 처리 로직 추가

    return res.status(200).json({
      success: true,
      classification,
      message: classification === 'reject'
        ? '부적절한 요청으로 분류되어 처리되지 않습니다.'
        : '문의가 접수되었습니다. 24시간 이내 답변드립니다.',
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
};
