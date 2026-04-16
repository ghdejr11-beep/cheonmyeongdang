/**
 * 홈택스 종합소득세 신고결과 조회 API
 * POST /api/tax-report
 * Body: { connectedId, identity, year? }
 */
const { getToken, callApi, setCors } = require('../lib/codef-api');

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const { connectedId, identity, year } = req.body || {};

    if (!connectedId) {
      return res.status(400).json({ success: false, error: '먼저 홈택스 연동(간편인증)을 진행해주세요.' });
    }

    const token = await getToken();

    const result = await callApi(token, '/v1/kr/public/nt/report/tax-result', {
      connectedId,
      organization: '0004',
      loginType: '5',
      identity: identity || '',
      loginTypeLevel: '1',
      searchYear: year || '2025',
    });

    return res.status(200).json({ success: true, data: result });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
};
