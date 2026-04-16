/**
 * CODEF 간편인증 connectedId 생성 API
 * POST /api/connect
 * Body: { identity }  (주민번호 앞 6자리 YYMMDD)
 *
 * 응답: { success, connectedId, twoWayInfo? }
 * - 2way 인증 필요시 twoWayInfo 포함 → 프론트에서 추가인증 UI 표시
 */
const { getToken, createConnectedId, addAuthTwoWay, setCors, encryptRSA } = require('../lib/codef-api');

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const { identity, userName, phone, loginTypeLevel, twoWayInfo } = req.body || {};

    if (!identity || identity.length < 6) {
      return res.status(400).json({ success: false, error: '주민번호를 입력해주세요.' });
    }
    if (!userName) {
      return res.status(400).json({ success: false, error: '이름을 입력해주세요.' });
    }
    if (!phone || phone.length < 10) {
      return res.status(400).json({ success: false, error: '휴대폰 번호를 입력해주세요.' });
    }

    const token = await getToken();

    // 2차 인증 응답인 경우
    if (twoWayInfo && twoWayInfo.jti) {
      const result = await addAuthTwoWay(token, {
        connectedId: twoWayInfo.connectedId,
        identity,
        jobIndex: twoWayInfo.jobIndex,
        threadIndex: twoWayInfo.threadIndex,
        jti: twoWayInfo.jti,
        twoWayTimestamp: twoWayInfo.twoWayTimestamp,
      });

      return res.status(200).json({
        success: true,
        data: result,
      });
    }

    // 최초 connectedId 생성 요청
    const result = await createConnectedId(token, { identity, userName, phone, loginTypeLevel });

    // CODEF 응답 처리
    if (result.result && result.result.code === 'CF-00000') {
      // 성공 — connectedId 발급 완료
      return res.status(200).json({
        success: true,
        connectedId: result.data?.connectedId || '',
        data: result,
      });
    } else if (result.result && result.result.code === 'CF-03002') {
      // 2way 추가인증 필요 (SMS 등)
      return res.status(200).json({
        success: true,
        needTwoWay: true,
        twoWayInfo: result.data || {},
        data: result,
      });
    } else {
      // 기타 에러
      return res.status(200).json({
        success: false,
        error: result.result?.message || 'CODEF 연결 실패',
        data: result,
      });
    }
  } catch (err) {
    return res.status(500).json({
      success: false,
      error: err.message,
    });
  }
};
