/**
 * 천명당 통합 이벤트 로깅 — Supabase events 테이블에 직접 적재
 * GA4 보완 (서버사이드 SoT). 12-function 한도로 Vercel 프록시 X — anon 키 + 화이트리스트 RPC.
 *
 * 사용:
 *   <script src="/js/cm-events.js"></script>
 *   cm.event('cta_click', {sku: 'jongsose', cta_label: 'pay-button'});
 *   cm.event('pay_success', {sku, amount_krw, gateway, order_id});
 */
(function (window) {
  'use strict';

  var SUPABASE_URL = 'https://hznihnwqgiumxakshtse.supabase.co';
  var ANON_KEY = 'sb_publishable_PlyTpyn4zGe8wqjooIWnSw_g786u-Z_';
  var ALLOWED_EVENTS = [
    'page_view', 'cta_click', 'pay_attempt', 'pay_success', 'pay_fail',
    'refund', 'subscribe', 'signup', 'modal_open', 'video_play'
  ];

  function sessionId() {
    try {
      var k = 'cm_sid';
      var s = sessionStorage.getItem(k);
      if (!s) {
        s = 'sid_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 10);
        sessionStorage.setItem(k, s);
      }
      return s;
    } catch (e) { return null; }
  }

  function userId() {
    try { return localStorage.getItem('cm_uid') || null; } catch (e) { return null; }
  }

  function deviceType() {
    var ua = navigator.userAgent || '';
    if (/Mobi|Android|iPhone/i.test(ua)) return 'mobile';
    if (/iPad|Tablet/i.test(ua)) return 'tablet';
    return 'desktop';
  }

  function getUTM() {
    try {
      var p = new URLSearchParams(location.search);
      return {
        utm_source: p.get('utm_source') || sessionStorage.getItem('cm_utm_source') || '',
        utm_medium: p.get('utm_medium') || sessionStorage.getItem('cm_utm_medium') || '',
        utm_campaign: p.get('utm_campaign') || sessionStorage.getItem('cm_utm_campaign') || '',
      };
    } catch (e) { return {}; }
  }

  function persistUTM() {
    try {
      var p = new URLSearchParams(location.search);
      ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) {
        var v = p.get(k);
        if (v) sessionStorage.setItem('cm_' + k, v);
      });
    } catch (e) {}
  }

  function event(name, props) {
    if (!ALLOWED_EVENTS.includes(name)) return;
    props = props || {};
    var utm = getUTM();
    var payload = {
      p_event_name: name,
      p_session_id: sessionId(),
      p_user_id: userId(),
      p_page_path: location.pathname + location.search,
      p_ref_url: document.referrer || null,
      p_sku: props.sku || null,
      p_amount_krw: props.amount_krw ? parseInt(props.amount_krw, 10) : null,
      p_props: Object.assign({
        device: deviceType(),
        utm_source: utm.utm_source,
        utm_medium: utm.utm_medium,
        utm_campaign: utm.utm_campaign,
      }, props),
    };

    try {
      var body = JSON.stringify(payload);
      // Beacon for unload-safe; fallback to fetch
      var blob = new Blob([body], { type: 'application/json' });
      var sent = false;
      if (navigator.sendBeacon) {
        // Beacon doesn't support custom headers — use fetch with keepalive
      }
      fetch(SUPABASE_URL + '/rest/v1/rpc/log_event', {
        method: 'POST',
        headers: {
          'apikey': ANON_KEY,
          'Authorization': 'Bearer ' + ANON_KEY,
          'Content-Type': 'application/json',
        },
        body: body,
        keepalive: true,
      }).catch(function () {});
    } catch (e) { /* swallow */ }
  }

  // Auto fire page_view + persist UTM on first load
  persistUTM();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { event('page_view'); });
  } else {
    event('page_view');
  }

  window.cm = { event: event, sessionId: sessionId, userId: userId };
})(window);
