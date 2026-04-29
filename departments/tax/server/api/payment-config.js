/**
 * 토스페이먼츠 클라이언트 설정 노출 API
 * GET /api/payment-config
 *
 * 클라이언트 키는 frontend 노출 OK (토스 정책)
 * 시크릿 키는 노출 금지 — 절대 반환하지 않음
 */
module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

  const clientKey = (process.env.TOSS_CLIENT_KEY || '').trim();
  const fixedAmount = Number(process.env.TOSS_FIXED_AMOUNT || 9900);

  if (!clientKey) {
    return res.status(500).json({ error: 'Server not configured: TOSS_CLIENT_KEY missing' });
  }

  // 키 prefix로 환경 추정 (test/live)
  const env = clientKey.startsWith('live_') ? 'live' : 'test';

  return res.status(200).json({
    clientKey,
    fixedAmount,
    env,
    feeRate: 9.9, // 정액 수수료 표시용
  });
};
