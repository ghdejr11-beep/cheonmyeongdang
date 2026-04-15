/**
 * 홈택스 종합소득세 신고결과 조회 API
 * POST /api/tax-report
 *
 * CODEF 홈택스 세금신고결과 조회
 */
const https = require('https');
const { getToken } = require('../lib/codef-token');

function codefRequest(token, path, body) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(body);
    const options = {
      hostname: 'development.codef.io',
      port: 443,
      path: path,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const decoded = decodeURIComponent(data);
          resolve(JSON.parse(decoded));
        } catch (e) {
          resolve({ result: { code: 'CF-09999', message: 'Parse error' }, raw: data });
        }
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const token = await getToken();

    const body = {
      connectedId: '',
      organization: '0004',
      loginType: '5',
      identity: req.body.identity || '',
      loginTypeLevel: '1',
      searchYear: req.body.year || '2025',
    };

    const result = await codefRequest(token, '/v1/kr/public/nt/report/tax-result', body);

    return res.status(200).json({
      success: true,
      data: result,
    });
  } catch (err) {
    return res.status(500).json({
      success: false,
      error: err.message,
    });
  }
};
