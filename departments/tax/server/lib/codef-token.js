/**
 * CODEF 토큰 발급 유틸리티
 */
const https = require('https');

// trim() to remove accidental newlines from env vars (PowerShell echo 이슈 방지)
const CLIENT_ID = (process.env.CODEF_CLIENT_ID || '57d8527e-e2a7-40e1-8bc5-d85ad4df2974').trim();
const CLIENT_SECRET = (process.env.CODEF_CLIENT_SECRET || 'dfc6efea-b57a-4264-b61d-b5450dc36951').trim();

function getToken() {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');
    const postData = 'grant_type=client_credentials&scope=read';

    const options = {
      hostname: 'oauth.codef.io',
      port: 443,
      path: '/oauth/token',
      method: 'POST',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(postData),
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.access_token);
        } catch (e) {
          reject(new Error('Token parse error: ' + data));
        }
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

module.exports = { getToken };
