/* 천명당 Service Worker
 * 캐시 버전: 20260427
 * 전략:
 *  - 정적 자원(이미지/폰트/SVG/MP3): cache-first
 *  - HTML 페이지: network-first (실패 시 캐시)
 *  - API(/api/*) 및 외부 광고/추적: 절대 캐시 X (네트워크 직행)
 */
const CACHE_VERSION = '20260427';
const STATIC_CACHE = 'cmd-static-v' + CACHE_VERSION;
const RUNTIME_CACHE = 'cmd-runtime-v' + CACHE_VERSION;

// 미리 받아둘 핵심 정적 자원 (오프라인 첫 진입 보장)
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/app_icon_512.png',
  '/app_icon_512.webp',
  '/palm-canva.webp',
  '/face-male.webp',
  '/face-female.webp',
  // 별자리 SVG 12종
  '/images/zodiac/00.svg',
  '/images/zodiac/01.svg',
  '/images/zodiac/02.svg',
  '/images/zodiac/03.svg',
  '/images/zodiac/04.svg',
  '/images/zodiac/05.svg',
  '/images/zodiac/06.svg',
  '/images/zodiac/07.svg',
  '/images/zodiac/08.svg',
  '/images/zodiac/09.svg',
  '/images/zodiac/10.svg',
  '/images/zodiac/11.svg'
];

// 캐시 절대 금지 패턴
const NO_CACHE_PATTERNS = [
  /\/api\//,
  /googletagmanager\.com/,
  /google-analytics\.com/,
  /pagead2\.googlesyndication\.com/,
  /googlesyndication\.com/,
  /js\.tosspayments\.com/,
  /\/checkout/,
  /\/payment/
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      // 개별 addAll은 하나만 실패해도 전부 실패하므로 Promise.allSettled
      return Promise.allSettled(
        PRECACHE_URLS.map((url) =>
          cache.add(url).catch((err) => console.warn('[SW] precache miss:', url, err))
        )
      );
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== RUNTIME_CACHE)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

function shouldBypass(url) {
  return NO_CACHE_PATTERNS.some((re) => re.test(url));
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  // GET 외에는 캐시 사용 안 함
  if (req.method !== 'GET') return;

  const url = req.url;
  if (shouldBypass(url)) {
    // 절대 캐시 X — 네트워크 직행
    return;
  }

  const accept = req.headers.get('accept') || '';
  const isHTML = req.mode === 'navigate' || accept.includes('text/html');

  if (isHTML) {
    // network-first
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(RUNTIME_CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() =>
          caches.match(req).then((hit) => hit || caches.match('/index.html'))
        )
    );
    return;
  }

  // 정적 자원: cache-first
  event.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        // 200 응답만 캐시 (opaque 등 제외)
        if (res && res.status === 200 && res.type === 'basic') {
          const copy = res.clone();
          caches.open(RUNTIME_CACHE).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      }).catch(() => hit);
    })
  );
});

// 새 SW 즉시 활성화 메시지
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});
