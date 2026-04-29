"""IndexNow ping — 천명당 신규/업데이트 페이지 일괄 색인 요청.
Bing/Yandex/Naver/Seznam 등 IndexNow 지원 검색엔진 한 번에 등록.
"""
import os, json, urllib.request

KEY = "d36c6c00cec20261eabe2e1ea32164e0"
HOST = "cheonmyeongdang.vercel.app"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"

URLS = [
    f"https://{HOST}/",
    f"https://{HOST}/support",
    f"https://{HOST}/pay",
    f"https://{HOST}/privacy.html",
    f"https://{HOST}/terms.html",
    f"https://{HOST}/sitemap.xml",
    f"https://{HOST}/blog/",
    f"https://{HOST}/blog/2026-zodiac-fortune.html",
    f"https://{HOST}/blog/dream-snake-meaning.html",
    f"https://{HOST}/blog/how-to-check-compatibility.html",
    f"https://{HOST}/blog/gwansang-basics.html",
    f"https://{HOST}/blog/saju-beginner-guide.html",
    f"https://{HOST}/#ddi",
]

def ping(endpoint, body):
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode('utf-8'),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'CheonmyeongdangIndexNow/1.0',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read(200).decode('utf-8', errors='replace')
    except Exception as e:
        return -1, f'{type(e).__name__}: {e}'

body = {
    'host': HOST,
    'key': KEY,
    'keyLocation': KEY_LOCATION,
    'urlList': URLS,
}

for ep in [
    'https://api.indexnow.org/indexnow',
    'https://www.bing.com/indexnow',
    'https://yandex.com/indexnow',
    'https://searchadvisor.naver.com/indexnow',
]:
    status, msg = ping(ep, body)
    print(f'[{status}] {ep} → {msg[:120]}')
