/**
 * 천명당 결제 데이터 영구 저장소 (GitHub Gist 기반)
 *
 * 왜 Gist?
 *   - Vercel KV/Upstash는 무료 티어 제한 + 별도 가입
 *   - DB는 사용자 환경 작업 필요
 *   - Gist는 GitHub 토큰(repo scope) 1개만 있으면 됨, 비용 0원
 *   - private gist → 외부 노출 X (PII 보호)
 *
 * 데이터 형식 (purchases.json):
 *   [
 *     {
 *       orderId: "cmd_xxx",
 *       paymentKey: "tps_xxx",
 *       customerEmail: "user@example.com",
 *       customerName: "홍길동",
 *       skuId: "saju_premium_9900",
 *       skuName: "사주 정밀 풀이",
 *       amount: 9900,
 *       method: "카드",
 *       paid_at: "2026-04-28T10:30:00Z",
 *       followup_sent: false,
 *       refunded: false
 *     }, ...
 *   ]
 *
 * 환경변수:
 *   GITHUB_TOKEN — Personal Access Token (gist scope)
 *   GIST_ID      — purchases.json을 담은 Gist의 ID (없으면 첫 호출 시 자동 생성 후 로그)
 */

const https = require('https');

const GIST_FILENAME = 'cheonmyeongdang_purchases.json';
const USER_AGENT = 'cheonmyeongdang-followup/1.0';

function ghRequest({ method, path, token, body }) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const headers = {
      'User-Agent': USER_AGENT,
      Accept: 'application/vnd.github+json',
      Authorization: `Bearer ${token}`,
      'X-GitHub-Api-Version': '2022-11-28',
    };
    if (data) {
      headers['Content-Type'] = 'application/json';
      headers['Content-Length'] = Buffer.byteLength(data);
    }
    const req = https.request(
      {
        hostname: 'api.github.com',
        port: 443,
        path,
        method,
        headers,
      },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => {
          try {
            const j = buf ? JSON.parse(buf) : null;
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(j);
            } else {
              reject(
                new Error(
                  `GitHub API ${res.statusCode}: ${j && j.message ? j.message : buf}`
                )
              );
            }
          } catch (e) {
            reject(new Error('GitHub 응답 파싱 실패: ' + buf));
          }
        });
      }
    );
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function getGist({ token, gistId }) {
  return ghRequest({
    method: 'GET',
    path: `/gists/${gistId}`,
    token,
  });
}

async function patchGist({ token, gistId, content }) {
  return ghRequest({
    method: 'PATCH',
    path: `/gists/${gistId}`,
    token,
    body: {
      files: {
        [GIST_FILENAME]: { content },
      },
    },
  });
}

async function createGist({ token }) {
  return ghRequest({
    method: 'POST',
    path: '/gists',
    token,
    body: {
      description: '[private] cheonmyeongdang purchase ledger — D+3 followup queue',
      public: false,
      files: {
        [GIST_FILENAME]: { content: '[]' },
      },
    },
  });
}

/**
 * 결제 데이터 1건 추가 (append).
 * @returns {Promise<{ok: boolean, reason?: string, gistId?: string}>}
 */
async function appendPurchase(record) {
  const token = (process.env.GITHUB_TOKEN || '').trim();
  if (!token) return { ok: false, reason: 'GITHUB_TOKEN 미설정' };

  let gistId = (process.env.GIST_ID || '').trim();

  try {
    if (!gistId) {
      // 최초 1회 — Gist 자동 생성
      const created = await createGist({ token });
      gistId = created.id;
      console.log(`[purchase-store] 새 Gist 생성됨: ${gistId} — Vercel env GIST_ID에 추가하세요`);
    }

    const gist = await getGist({ token, gistId });
    const file = gist.files && gist.files[GIST_FILENAME];
    let arr = [];
    if (file && file.content) {
      try {
        arr = JSON.parse(file.content);
        if (!Array.isArray(arr)) arr = [];
      } catch (e) {
        arr = [];
      }
    }

    // orderId 중복 방지
    if (arr.some((p) => p.orderId === record.orderId)) {
      return { ok: true, gistId, reason: 'duplicate orderId — skipped' };
    }

    arr.push({
      ...record,
      followup_sent: false,
      refunded: false,
    });

    // 보관 기간: 60일 이상 + followup_sent=true 인 것만 자동 정리 (PII 최소화)
    const cutoff = Date.now() - 60 * 24 * 60 * 60 * 1000;
    arr = arr.filter((p) => {
      const t = new Date(p.paid_at).getTime();
      if (isNaN(t)) return true;
      if (t < cutoff && p.followup_sent) return false;
      return true;
    });

    await patchGist({ token, gistId, content: JSON.stringify(arr, null, 2) });
    return { ok: true, gistId };
  } catch (err) {
    return { ok: false, reason: err.message };
  }
}

/**
 * 코호트별 후속 메일 대상 결제 조회.
 * cohortKey: 'followup_sent' (D+3) | 'followup_d7_sent' (D+7) | 'followup_d14_sent' (D+14)
 * 해당 코호트가 false 이고 refunded=false 이고 paid_at이 정확히 daysAgo일 전(±24h 윈도우) 인 항목.
 * subscription 타입은 후속 메일에서 제외 (이미 활성 구독자).
 * @returns {Promise<{ok:boolean, records:Array, gistId?:string, reason?:string}>}
 */
async function listFollowupTargets({ daysAgo = 3, cohortKey = 'followup_sent' } = {}) {
  const token = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = (process.env.GIST_ID || '').trim();
  if (!token || !gistId) {
    return { ok: false, records: [], reason: 'GITHUB_TOKEN/GIST_ID 미설정' };
  }

  try {
    const gist = await getGist({ token, gistId });
    const file = gist.files && gist.files[GIST_FILENAME];
    let arr = [];
    if (file && file.content) {
      try {
        arr = JSON.parse(file.content);
        if (!Array.isArray(arr)) arr = [];
      } catch (e) {
        arr = [];
      }
    }

    const now = Date.now();
    // 정확히 D+N (오차 24시간 윈도우)
    const targetMin = now - (daysAgo + 1) * 24 * 60 * 60 * 1000;
    const targetMax = now - daysAgo * 24 * 60 * 60 * 1000;

    const records = arr.filter((p) => {
      if (p[cohortKey]) return false; // 이 코호트 메일 이미 발송됨
      if (p.refunded) return false;
      if (p.skuType === 'subscription' || p.type === 'subscription') return false;
      if (!p.paid_at) return false;
      const t = new Date(p.paid_at).getTime();
      if (isNaN(t)) return false;
      return t >= targetMin && t <= targetMax;
    });

    return { ok: true, records, gistId, total: arr.length };
  } catch (err) {
    return { ok: false, records: [], reason: err.message };
  }
}

/**
 * 후속 메일 발송 후 코호트별 sent 필드 마킹.
 * options.cohortKey: 'followup_sent' (D+3, 기본) | 'followup_d7_sent' | 'followup_d14_sent'
 */
async function markFollowupSent(orderIds, options = {}) {
  const cohortKey = options.cohortKey || 'followup_sent';
  const sentAtKey = cohortKey + '_at';
  const token = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = (process.env.GIST_ID || '').trim();
  if (!token || !gistId) return { ok: false, reason: 'GITHUB_TOKEN/GIST_ID 미설정' };

  try {
    const gist = await getGist({ token, gistId });
    const file = gist.files && gist.files[GIST_FILENAME];
    let arr = [];
    if (file && file.content) {
      arr = JSON.parse(file.content);
      if (!Array.isArray(arr)) arr = [];
    }
    const idSet = new Set(orderIds);
    let touched = 0;
    arr = arr.map((p) => {
      if (idSet.has(p.orderId) && !p[cohortKey]) {
        touched++;
        return { ...p, [cohortKey]: true, [sentAtKey]: new Date().toISOString() };
      }
      return p;
    });
    await patchGist({ token, gistId, content: JSON.stringify(arr, null, 2) });
    return { ok: true, touched };
  } catch (err) {
    return { ok: false, reason: err.message };
  }
}

/**
 * 환불된 주문 마킹 (수동 또는 환불 webhook에서 호출).
 */
async function markRefunded(orderId) {
  const token = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = (process.env.GIST_ID || '').trim();
  if (!token || !gistId) return { ok: false, reason: 'GITHUB_TOKEN/GIST_ID 미설정' };

  try {
    const gist = await getGist({ token, gistId });
    const file = gist.files && gist.files[GIST_FILENAME];
    let arr = JSON.parse((file && file.content) || '[]');
    if (!Array.isArray(arr)) arr = [];
    arr = arr.map((p) =>
      p.orderId === orderId ? { ...p, refunded: true, refunded_at: new Date().toISOString() } : p
    );
    await patchGist({ token, gistId, content: JSON.stringify(arr, null, 2) });
    return { ok: true };
  } catch (err) {
    return { ok: false, reason: err.message };
  }
}

/**
 * 특정 이메일의 비환불 결제 SKU 목록 반환 — entitlement 검증용
 * @param {string} email
 * @returns {Promise<{ok:boolean, records:Array, reason?:string}>}
 */
async function listPurchasesByEmail(email) {
  if (!email) return { ok: false, records: [], reason: 'email 미지정' };
  const target = String(email).trim().toLowerCase();
  const token = (process.env.GITHUB_TOKEN || '').trim();
  const gistId = (process.env.GIST_ID || '').trim();
  if (!token || !gistId) {
    return { ok: false, records: [], reason: 'GITHUB_TOKEN/GIST_ID 미설정' };
  }
  try {
    const gist = await getGist({ token, gistId });
    const file = gist.files && gist.files[GIST_FILENAME];
    let arr = [];
    if (file && file.content) {
      try {
        arr = JSON.parse(file.content);
        if (!Array.isArray(arr)) arr = [];
      } catch (e) { arr = []; }
    }
    const records = arr
      .filter(p => (p.customerEmail || '').trim().toLowerCase() === target)
      .filter(p => !p.refunded)
      .map(p => ({ skuId: p.skuId, paid_at: p.paid_at, orderId: p.orderId, skuName: p.skuName }));
    return { ok: true, records };
  } catch (err) {
    return { ok: false, records: [], reason: err.message };
  }
}

module.exports = {
  appendPurchase,
  listFollowupTargets,
  markFollowupSent,
  markRefunded,
  listPurchasesByEmail,
};
