/**
 * ============================================================================
 * 천명당 Supabase 경량 클라이언트 (index.html 용)
 * ============================================================================
 *
 * 정상 제출 전용 경량 래퍼. Supabase JS SDK 를 로드하지 않고 fetch 로 직접
 * PostgREST 엔드포인트를 호출합니다 (메인 페이지 로딩 가벼움).
 *
 * admin.html 은 이 파일을 쓰지 않고 Supabase JS SDK 를 별도로 로드합니다
 * (Auth · SELECT · UPDATE · DELETE 가 필요하므로).
 * ============================================================================
 */
(function () {
  'use strict';

  function isEnabled() {
    const cfg = window.SUPABASE_CONFIG;
    if (!cfg) return false;
    if (!cfg.enabled) return false;
    if (!cfg.url || !cfg.anonKey) return false;
    if (cfg.url.indexOf('YOUR_') === 0) return false;
    if (cfg.anonKey.indexOf('YOUR_') === 0) return false;
    return true;
  }

  /**
   * 불만 1건을 Supabase complaints 테이블에 INSERT
   * @returns {Promise<{ok: boolean, reason?: string, detail?: string}>}
   */
  function saveComplaint(complaint) {
    if (!isEnabled()) {
      return Promise.resolve({ ok: false, reason: 'not_configured' });
    }

    const cfg = window.SUPABASE_CONFIG;
    const row = {
      id: complaint.id,
      name: complaint.name || null,
      tel: complaint.tel || null,
      email: complaint.email || null,
      type: complaint.type || null,
      detail: complaint.detail,
      rating: complaint.rating || 0,
      analysis: complaint.analysis || null,
      submitted_at: complaint.timestamp || new Date().toISOString()
    };

    return fetch(cfg.url + '/rest/v1/complaints', {
      method: 'POST',
      headers: {
        'apikey': cfg.anonKey,
        'Authorization': 'Bearer ' + cfg.anonKey,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify(row)
    })
    .then(function (res) {
      if (res.ok) return { ok: true };
      return res.text().then(function (text) {
        return { ok: false, reason: 'http_' + res.status, detail: text };
      });
    })
    .catch(function (err) {
      return { ok: false, reason: 'network', detail: String(err) };
    });
  }

  window.SupabaseComplaint = {
    isEnabled: isEnabled,
    saveComplaint: saveComplaint
  };
})();
