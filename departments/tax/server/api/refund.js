/**
 * 홈택스 환급금 조회 API
 * POST /api/refund
 * Body: { loginType, identity, password }
 *
 * CODEF 홈택스 세금신고납부 환급금 조회
 */
const https = require('https');
const { getToken } = require('../lib/codef-token');

const PUBLIC_KEY = process.env.CODEF_PUBLIC_KEY || 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApnEOQMrzwQSvY/gnIK0qP4w980V1aZyjCQWnRe0YkRrN/Dh68u2UJq4nq4fLzPhoGRhKr7i2o59QvGWu+hUK9uOzfKFOUMs3URgLBA1nwRcfzjSwlTKQ5GnKi7SatNVqn0tvTDCiPAEUtOQTT5PkMCS5si1Lkah6GK+YM37FVyNLCIN99LrzkS9qdC8U8RgVOkidKDvmikFczZxBomDn+GQSmkZ6zfhZwn6zPAskXcmjPd0JxFWLBbkaRUZcylMQQpFN7AMpdDj1Hy2Cr6/bXjwUAcy99zXuoh5A/lL6HvYvyKJG1ApSWR6c8yagXfJ9RNid77LJQE/JGC1+3Rz1AQIDAQAB';

function codefRequest(token, path, body) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(body);
    const options = {
      hostname: 'development.codef.io', // 데모: development, 정식: api
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
          // CODEF 응답은 URL 인코딩된 JSON
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
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const token = await getToken();

    // 홈택스 환급금 조회
    // 데모에서는 고정 응답이 옴
    const body = {
      connectedId: '', // 간편인증 시 발급받는 ID
      organization: '0004', // 국세청
      loginType: '5', // 간편인증
      identity: req.body.identity || '',
      loginTypeLevel: '1',
    };

    const result = await codefRequest(token, '/v1/kr/public/nt/proofissue/refund-check', body);

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
