/**
 * 천명당 통합 분석 부트스트랩 — Microsoft Clarity + Vercel Analytics
 * GA4 (G-90Y8GPVX1F) 는 각 페이지 head에 직접 로드 (먼저).
 * 이 스니펫은 GA4 와 별도로 Clarity / Vercel Analytics / 표준 GA4 funnel 이벤트 발사를 담당.
 *
 * 사용:
 *   <script src="/js/cm-analytics.js" defer></script>
 *
 * NOTE: CLARITY_PROJECT_ID 는 사용자가 https://clarity.microsoft.com 에서 프로젝트 생성 후
 *       1줄만 교체. 비어있어도 다른 부분은 정상 동작.
 */
(function (window, document) {
  'use strict';

  // ─────────────────────────────────────────────────────────────
  // 1) Microsoft Clarity (placeholder — 사용자가 ID 1줄만 교체)
  //    https://clarity.microsoft.com → New Project → ID 복사 후 아래 교체
  // ─────────────────────────────────────────────────────────────
  var CLARITY_PROJECT_ID = ''; // ← e.g. 'r6n5x9abcd'

  if (CLARITY_PROJECT_ID) {
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r);
      t.async = 1;
      t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0];
      y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CLARITY_PROJECT_ID);
  }

  // ─────────────────────────────────────────────────────────────
  // 2) Vercel Web Analytics (production-only no-op outside vercel.app)
  //    공식 스니펫 (자동 SPA route tracking 포함)
  //    https://vercel.com/docs/analytics/quickstart#with-script
  // ─────────────────────────────────────────────────────────────
  try {
    window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    var vs = document.createElement('script');
    vs.defer = true;
    vs.src = '/_vercel/insights/script.js';
    vs.setAttribute('data-mode', 'auto');
    document.head.appendChild(vs);
  } catch (e) { /* ignore */ }

  // ─────────────────────────────────────────────────────────────
  // 3) GA4 표준 funnel 이벤트 — view_landing / click_buy / start_checkout
  //    purchase / begin_checkout / view_item 은 이미 페이지별로 발사됨
  // ─────────────────────────────────────────────────────────────
  function safeGtag(name, params) {
    try { if (window.gtag) window.gtag('event', name, params || {}); } catch (e) { /* ignore */ }
    // cm-events.js (Supabase) 보완 발사
    try { if (window.cm && typeof window.cm.event === 'function') window.cm.event(name, params || {}); } catch (e) { /* ignore */ }
  }

  // view_landing — 페이지가 / 또는 /en/ 등 landing 일 때만
  function isLanding() {
    var p = (location.pathname || '/').replace(/\/+$/, '/') || '/';
    return p === '/' || p === '/en/' || p === '/index.html' || p === '/en/index.html';
  }

  function init() {
    if (isLanding()) {
      safeGtag('view_landing', {
        page_location: location.href,
        page_path: location.pathname,
        language: (document.documentElement.lang || 'ko')
      });
    }

    // 모든 buy/CTA 버튼 위임 클릭 → click_buy
    document.addEventListener('click', function (ev) {
      var t = ev.target;
      if (!t) return;
      // 가장 가까운 anchor / button
      var el = t.closest && t.closest('a,button');
      if (!el) return;
      var label = (el.getAttribute('data-cta') || el.getAttribute('aria-label') || el.textContent || '').trim().slice(0, 60);
      var href = el.getAttribute && el.getAttribute('href') || '';
      var isBuy = /pay|buy|결제|구매|checkout|order|주문/i.test(label + ' ' + href) ||
                  el.classList && (el.classList.contains('btn-buy') || el.classList.contains('btn-pay') || el.classList.contains('cta-buy'));
      if (isBuy) {
        safeGtag('click_buy', { cta_label: label, href: href, page_path: location.pathname });
      }
    }, { passive: true });

    // PayPal SDK popup 열림 → start_checkout (event-listener 패치)
    // PayPal Smart Buttons는 onClick 콜백으로 추적 가능. 글로벌 hook 노출.
    window.cmTrackStartCheckout = function (sku, amount, gateway) {
      safeGtag('start_checkout', { sku: sku || null, value: amount || null, currency: 'KRW', gateway: gateway || 'unknown' });
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})(window, document);
