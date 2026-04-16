/**
 * CODEF API 공통 유틸리티
 * - 토큰 발급 (OAuth)
 * - API 호출 (정식/데모 서버 분기)
 * - connectedId 생성 (간편인증)
 */
const https = require('https');
const crypto = require('crypto');

// 서버 분기
const ENV = (process.env.CODEF_ENV || 'sandbox').trim();
const CODEF_HOST = ENV === 'production' ? 'api.codef.io'
  : ENV === 'sandbox' ? 'sandbox.codef.io'
  : 'development.codef.io';

// sandbox는 전용 내장 키 사용 (CODEF 공식 제공)
const SANDBOX_CLIENT_ID = 'ef27cfaa-10c1-4470-adac-60ba476273f9';
const SANDBOX_CLIENT_SECRET = '83160c33-9045-4915-86d8-809473cdf5c3';

const CLIENT_ID = ENV === 'sandbox' ? SANDBOX_CLIENT_ID : (process.env.CODEF_CLIENT_ID || '').trim();
const CLIENT_SECRET = ENV === 'sandbox' ? SANDBOX_CLIENT_SECRET : (process.env.CODEF_CLIENT_SECRET || '').trim();
const PUBLIC_KEY = (process.env.CODEF_PUBLIC_KEY || '').trim();

function checkEnv() {
  if (!CLIENT_ID || !CLIENT_SECRET) {
    throw new Error('CODEF_CLIENT_ID 또는 CODEF_CLIENT_SECRET 환경변수 미설정');
  }
}

/**
 * OAuth 토큰 발급
 */
function getToken() {
  checkEnv();
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');
    const postData = 'grant_type=client_credentials&scope=read';

    const req = https.request({
      hostname: 'oauth.codef.io',
      port: 443,
      path: '/oauth/token',
      method: 'POST',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(postData),
      },
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.access_token) resolve(json.access_token);
          else reject(new Error('Token error: ' + data));
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

/**
 * CODEF API 호출 공통 함수
 */
function callApi(token, path, body) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(body);
    const req = https.request({
      hostname: CODEF_HOST,
      port: 443,
      path: path,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
      },
    }, (res) => {
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

/**
 * RSA 공개키로 비밀번호 암호화 (CODEF 요구사항)
 */
function encryptRSA(plainText) {
  if (!PUBLIC_KEY) throw new Error('CODEF_PUBLIC_KEY 환경변수 미설정');
  const pemKey = `-----BEGIN PUBLIC KEY-----\n${PUBLIC_KEY}\n-----END PUBLIC KEY-----`;
  const buffer = Buffer.from(plainText, 'utf8');
  const encrypted = crypto.publicEncrypt({
    key: pemKey,
    padding: crypto.constants.RSA_PKCS1_PADDING,
  }, buffer);
  return encrypted.toString('base64');
}

/**
 * connectedId 생성 (간편인증 기반)
 *
 * 1단계: 계정 등록 → 2단계: 간편인증 진행 → connectedId 반환
 *
 * @param {string} token - OAuth 토큰
 * @param {object} params - { identity, userName }
 * @returns {object} - { connectedId, ... }
 */
async function createConnectedId(token, params) {
  // identity + password는 RSA 암호화 필수 (CODEF 요구사항)
  const encIdentity = encryptRSA(params.identity);
  const encPassword = encryptRSA(params.password || '');

  const body = {
    accountList: [{
      countryCode: 'KR',
      businessType: 'NT',       // 국세청
      clientType: 'P',          // 개인
      organization: '0004',     // 국세청
      loginType: '5',           // 간편인증
      loginTypeLevel: params.loginTypeLevel || '1',  // 1:카카오, 5:PASS, 6:네이버, 8:토스
      identity: encIdentity,
      id: params.phone || '',   // 휴대폰 번호 (평문)
      password: encPassword,
      userName: params.userName || '',
    }],
  };

  const result = await callApi(token, '/v1/account/create', body);
  return result;
}

/**
 * 간편인증 2단계 추가인증 (SMS 인증번호 등)
 */
async function addAuthTwoWay(token, params) {
  const body = {
    connectedId: params.connectedId,
    organization: '0004',
    loginType: '5',
    loginTypeLevel: '1',
    identity: params.identity,
    simpleAuth: '1',
    is2Way: true,
    twoWayInfo: {
      jobIndex: params.jobIndex || 0,
      threadIndex: params.threadIndex || 0,
      jti: params.jti || '',
      twoWayTimestamp: params.twoWayTimestamp || 0,
    },
  };

  const result = await callApi(token, '/v1/account/update', body);
  return result;
}

/**
 * CORS 헤더 설정 + preflight 처리
 */
function setCors(res) {
  const allowedOrigins = [
    'https://ghdejr11-beep.github.io',
    'https://tax-n-benefit-api.vercel.app',
    'http://localhost:3000',
    'http://127.0.0.1:5500',
  ];
  res.setHeader('Access-Control-Allow-Origin', '*'); // MVP 단계 — 프로덕션에서 제한
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

module.exports = {
  getToken,
  callApi,
  encryptRSA,
  createConnectedId,
  addAuthTwoWay,
  setCors,
  CODEF_HOST,
};
