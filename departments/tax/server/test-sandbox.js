/**
 * CODEF Sandbox 테스트 — 간편인증 connectedId 생성
 * sandbox.codef.io는 고정 응답 반환 (파라미터 형식만 체크)
 */
const { EasyCodef, EasyCodefConstant, EasyCodefUtil } = require('easycodef-node');

const PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApnEOQMrzwQSvY/gnIK0qP4w980V1aZyjCQWnRe0YkRrN/Dh68u2UJq4nq4fLzPhoGRhKr7i2o59QvGWu+hUK9uOzfKFOUMs3URgLBA1nwRcfzjSwlTKQ5GnKi7SatNVqn0tvTDCiPAEUtOQTT5PkMCS5si1Lkah6GK+YM37FVyNLCIN99LrzkS9qdC8U8RgVOkidKDvmikFczZxBomDn+GQSmkZ6zfhZwn6zPAskXcmjPd0JxFWLBbkaRUZcylMQQpFN7AMpdDj1Hy2Cr6/bXjwUAcy99zXuoh5A/lL6HvYvyKJG1ApSWR6c8yagXfJ9RNid77LJQE/JGC1+3Rz1AQIDAQAB';

async function test() {
  const codef = new EasyCodef();
  codef.setPublicKey(PUBLIC_KEY);

  // 샌드박스는 내장 키 자동 사용
  const param = {
    accountList: [{
      countryCode: 'KR',
      businessType: 'NT',
      clientType: 'P',
      organization: '0004',
      loginType: '5',
      loginTypeLevel: '1',
      identity: EasyCodefUtil.encryptRSA(PUBLIC_KEY, '8601011234567'),
      id: '01012345678',
      password: EasyCodefUtil.encryptRSA(PUBLIC_KEY, ''),
      userName: '홍길동',
    }],
  };

  console.log('=== SANDBOX connectedId 생성 테스트 ===');
  console.log('HOST: sandbox.codef.io');
  console.log('파라미터:', JSON.stringify(param, null, 2));
  console.log('---');

  try {
    const result = await codef.createAccount(EasyCodefConstant.SERVICE_TYPE_SANDBOX, param);
    console.log('응답:', result);
  } catch (e) {
    console.error('에러:', e.message);
  }
}

test();
