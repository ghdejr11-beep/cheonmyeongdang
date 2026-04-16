/**
 * CODEF 토큰 발급 유틸리티
 */
const https = require('https');

// trim() to remove accidental newlines from env vars (PowerShell echo 이슈 방지)
const CLIENT_ID = (process.env.CODEF_CLIENT_ID || '').trim();
const CLIENT_SECRET = (process.env.CODEF_CLIENT_SECRET || '').trim();

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error('[CODEF] CLIENT_ID 또는 CLIENT_SECRET 환경변수 미설정');
}

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
