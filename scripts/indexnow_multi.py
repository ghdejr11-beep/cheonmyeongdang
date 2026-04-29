"""IndexNow ping — 세금N혜택 + KORLENS 신규 페이지 일괄 색인 요청."""
import json, urllib.request

ENGINES = [
    'https://api.indexnow.org/indexnow',
    'https://www.bing.com/indexnow',
    'https://yandex.com/indexnow',
    'https://searchadvisor.naver.com/indexnow',
]

# 천명당 키 재사용 (3사이트 모두 같은 운영자)
KEY = "d36c6c00cec20261eabe2e1ea32164e0"

PAYLOADS = [
    {
        'host': 'tax-n-benefit-api.vercel.app',
        'key': KEY,
        'keyLocation': f'https://tax-n-benefit-api.vercel.app/{KEY}.txt',
        'urlList': [
            'https://tax-n-benefit-api.vercel.app/blog/jonghapsodeukse-refund-2026',
            'https://tax-n-benefit-api.vercel.app/blog/hometax-easy-refund',
            'https://tax-n-benefit-api.vercel.app/blog/prepaid-tax-credit',
            'https://tax-n-benefit-api.vercel.app/blog/freelancer-tax-tips',
            'https://tax-n-benefit-api.vercel.app/blog/child-tax-credit',
            'https://tax-n-benefit-api.vercel.app/blog',
            'https://tax-n-benefit-api.vercel.app/support',
        ]
    },
    {
        'host': 'korlens.app',
        'key': KEY,
        'keyLocation': f'https://korlens.app/{KEY}.txt',
        'urlList': [
            'https://korlens.app/blog',
            'https://korlens.app/blog/hidden-restaurants-seoul',
            'https://korlens.app/blog/jeju-itinerary-3days',
            'https://korlens.app/blog/korea-vs-japan-travel',
            'https://korlens.app/blog/korean-bbq-etiquette',
            'https://korlens.app/blog/gyeongju-day-trip',
        ]
    },
]

def ping(endpoint, body):
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode('utf-8'),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'KunStudioIndexNow/1.0',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read(150).decode('utf-8', errors='replace')
    except Exception as e:
        return -1, f'{type(e).__name__}: {e}'

for body in PAYLOADS:
    print(f"\n=== {body['host']} ({len(body['urlList'])} URLs) ===")
    for ep in ENGINES:
        s, m = ping(ep, body)
        print(f'  [{s}] {ep[:50]:50s} → {m[:100]}')
