#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexNow ping — Bing/Yandex 즉시 색인 요청
4 lang FAQ + sitemap 갱신 후 핵심 URL 일괄 통보
"""
import os
import json
import urllib.request
from datetime import datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
KEY = 'd36c6c00cec20261eabe2e1ea32164e0'
HOST = 'cheonmyeongdang.vercel.app'
KEY_LOC = f'https://{HOST}/{KEY}.txt'
REPORT = os.path.join(ROOT, 'departments', 'intelligence', 'indexnow_ping_report.txt')

URLS = [
    # 4 lang main
    f'https://{HOST}/',
    f'https://{HOST}/en/',
    f'https://{HOST}/ja/',
    f'https://{HOST}/zh/',
    # 4 lang FAQ
    f'https://{HOST}/faq.html',
    f'https://{HOST}/en/faq.html',
    f'https://{HOST}/ja/faq.html',
    f'https://{HOST}/zh/faq.html',
    # sitemap
    f'https://{HOST}/sitemap.xml',
    # ja/zh core
    f'https://{HOST}/ja/pricing.html',
    f'https://{HOST}/ja/four-pillars-jukai.html',
    f'https://{HOST}/ja/jukkan-junishi.html',
    f'https://{HOST}/ja/korean-zodiac-2026-uma.html',
    f'https://{HOST}/ja/saju-aishou-test.html',
    f'https://{HOST}/ja/saju-vs-japanese-shichu-suimei.html',
    f'https://{HOST}/zh/pricing.html',
    f'https://{HOST}/zh/four-pillars-mingli.html',
    f'https://{HOST}/zh/ten-stems-twelve-branches.html',
    f'https://{HOST}/zh/zodiac-2026-red-horse.html',
    f'https://{HOST}/zh/bazi-compatibility-test.html',
    f'https://{HOST}/zh/korean-bazi-vs-chinese-bazi.html',
    # en core
    f'https://{HOST}/en/pricing.html',
    f'https://{HOST}/en/four-pillars-of-destiny.html',
    f'https://{HOST}/en/saju.html',
    f'https://{HOST}/en/saju-compatibility-test.html',
]

ENDPOINTS = [
    'https://api.indexnow.org/IndexNow',
    'https://www.bing.com/IndexNow',
    'https://yandex.com/indexnow',
]


def post_indexnow(endpoint, urls):
    body = json.dumps({
        'host': HOST,
        'key': KEY,
        'keyLocation': KEY_LOC,
        'urlList': urls,
    }).encode('utf-8')
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'CheonmyeongdangIndexNow/1.0'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return {'ok': True, 'status': r.status, 'body': r.read()[:500].decode('utf-8', errors='replace')}
    except Exception as e:
        # IndexNow는 200 / 202를 success로 본다. urllib HTTPError 404는 endpoint 미지원.
        code = getattr(e, 'code', 0)
        return {'ok': code in (200, 202), 'status': code, 'body': str(e)[:500]}


def main():
    lines = [
        f'# IndexNow Ping Report — {datetime.now().isoformat(timespec="seconds")}',
        f'# Host: {HOST}',
        f'# Key: {KEY}',
        f'# URLs: {len(URLS)}',
        '',
    ]
    for ep in ENDPOINTS:
        r = post_indexnow(ep, URLS)
        mark = 'OK' if r['ok'] else 'FAIL'
        lines.append(f'[{mark}] {ep} → HTTP {r["status"]}')
        lines.append(f'      body: {r["body"][:200]}')
    lines.append('')
    lines.append('# URL list submitted:')
    for u in URLS:
        lines.append(f'  - {u}')
    text = '\n'.join(lines)
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(text)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))
    return 0


if __name__ == '__main__':
    main()
