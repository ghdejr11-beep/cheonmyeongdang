/**
 * 홈택스 지급명세서 조회 API (원천징수 내역)
 * POST /api/income
 * Body: { connectedId, identity, startDate?, endDate?, incomeType? }
 */
const { getToken, callApi, setCors } = require('../lib/codef-api');

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const { connectedId, identity, startDate, endDate, incomeType } = req.body || {};

    if (!connectedId) {
      return res.status(400).json({ success: false, error: '먼저 홈택스 연동(간편인증)을 진행해주세요.' });
    }

    const token = await getToken();

    const result = await callApi(token, '/v1/kr/public/nt/proofissue/paystatement', {
      connectedId,
      organization: '0004',
      loginType: '5',
      identity: identity || '',
      loginTypeLevel: '1',
      startDate: startDate || '20210101',
      endDate: endDate || '20261231',
      incomeType: incomeType || '1', // 1: 사업소득, 2: 근로소득
    });

    return res.status(200).json({ success: true, data: result });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
};
