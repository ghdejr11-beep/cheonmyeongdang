/**
 * 홈택스 세무관련 증명서 4종 일괄 발급 API
 * POST /api/tax-cert-all
 *
 * Body: { connectedId, identity, codef_token?, biz_no?, year?, types? }
 *  - connectedId : CODEF 간편인증으로 발급받은 connectedId (필수)
 *  - identity    : 주민등록번호 13자리 (선택, CODEF 응답 내 식별용)
 *  - biz_no      : 사업자등록번호 10자리 (사업자등록증명/부가세 과세표준 발급에 사용)
 *  - year        : 조회 기준연도 (default: 직전년도)
 *  - codef_token : 클라이언트가 이미 발급받은 OAuth 토큰 (없으면 서버가 재발급)
 *  - types       : ['businessReg','vat','income','taxPayment'] 중 일부만 발급하고 싶을 때
 *
 * 응답:
 * {
 *   success: true,
 *   data: {
 *     businessReg: { ok, code, message, data? }, // 사업자등록증명
 *     vat:         { ok, code, message, data? }, // 부가가치세 과세표준증명
 *     income:      { ok, code, message, data? }, // 소득금액증명
 *     taxPayment:  { ok, code, message, data? }, // 납세증명서 (tax-cert-all)
 *   }
 * }
 *
 * 한 항목이 실패해도 나머지 항목은 계속 진행하여 partial 결과를 반환합니다.
 */
const { getToken, callApi, setCors } = require('../lib/codef-api');

// CODEF API 경로 (기존 income.js / refund.js 와 동일한 /proofissue/<slug> 패턴)
const ENDPOINTS = {
  businessReg: '/v1/kr/public/nt/proofissue/business-registration-certificate',
  vat:         '/v1/kr/public/nt/proofissue/additional-taxstandard',
  income:      '/v1/kr/public/nt/proofissue/earnings-proof',
  taxPayment:  '/v1/kr/public/nt/proofissue/tax-cert-all',
};

// 이전 연도 (default 조회 기준)
function defaultYear() {
  const now = new Date();
  return String(now.getFullYear() - 1);
}

// 4종 각각의 요청 body 빌더 (CODEF 공통 파라미터 + 항목별 옵션)
function buildBody(kind, { connectedId, identity, biz_no, year }) {
  const base = {
    connectedId,
    organization: '0004', // 국세청
    loginType: '5',       // 간편인증
    loginTypeLevel: '1',
    identity: identity || '',
  };

  switch (kind) {
    case 'businessReg':
      return {
        ...base,
        businessType: '1', // 1:사업자, 2:면세사업자 등
        userName: '',
        businessRegistrationNumber: biz_no || '',
        proofType: '1',    // 1:발급용, 2:열람용
        applicationType: '1',
      };
    case 'vat':
      return {
        ...base,
        businessRegistrationNumber: biz_no || '',
        searchStartYear: year || defaultYear(),
        searchEndYear: year || defaultYear(),
        proofType: '1',
        applicationType: '1',
      };
    case 'income':
      return {
        ...base,
        searchYear: year || defaultYear(),
        incomeType: '1',   // 1:종합소득, 2:근로소득
        proofType: '1',
        applicationType: '1',
      };
    case 'taxPayment':
      return {
        ...base,
        useType: '1',                  // 사용용도 (1:민원/대금수령 등)
        proofType: '1',
        applicationType: '1',
        businessRegistrationNumber: biz_no || '',
      };
    default:
      return base;
  }
}

// 한 항목 호출 — 실패해도 throw 하지 않고 표준화된 객체 반환
async function callOne(token, kind, params) {
  try {
    const result = await callApi(token, ENDPOINTS[kind], buildBody(kind, params));
    const code = result?.result?.code || 'CF-09998';
    const message = result?.result?.message || '';
    return {
      ok: code === 'CF-00000',
      code,
      message,
      data: result?.data || null,
      raw: result,
    };
  } catch (err) {
    return {
      ok: false,
      code: 'CF-EXCEPT',
      message: err.message || String(err),
      data: null,
    };
  }
}

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = req.body || {};
    const { connectedId, identity, biz_no, year, codef_token } = body;

    if (!connectedId) {
      return res.status(400).json({
        success: false,
        error: '먼저 홈택스 연동(간편인증)을 진행해주세요. (connectedId 필요)',
      });
    }

    // 발급할 항목 — types 미지정 시 4종 전부
    const all = ['businessReg', 'vat', 'income', 'taxPayment'];
    const types = Array.isArray(body.types) && body.types.length
      ? body.types.filter((t) => all.includes(t))
      : all;

    // 토큰: 클라이언트가 넘기면 그대로, 아니면 서버가 OAuth 발급
    const token = (codef_token && String(codef_token).trim())
      ? String(codef_token).trim()
      : await getToken();

    const params = { connectedId, identity, biz_no, year };

    // 4종 병렬 호출 (한 건이 실패해도 나머지 진행 — Promise.all + try/catch wrapper)
    const entries = await Promise.all(
      types.map(async (kind) => [kind, await callOne(token, kind, params)])
    );

    const data = Object.fromEntries(entries);
    const anyOk = Object.values(data).some((v) => v && v.ok);

    return res.status(200).json({
      success: anyOk,
      partial: Object.values(data).some((v) => !v.ok),
      data,
    });
  } catch (err) {
    return res.status(500).json({
      success: false,
      error: err.message || String(err),
    });
  }
};
