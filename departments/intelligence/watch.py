#!/usr/bin/env python3
"""
통합 경쟁사 인텔리전스 수집부 — 모든 부서 지원
 Usage:
   python watch.py tax         # 세금N혜택 수집
   python watch.py saju        # 천명당 수집
   python watch.py insurance   # 보험다보여 수집
   python watch.py prompts     # 크티 프롬프트 수집
   python watch.py kdp         # KDP 전자책 수집
   python watch.py all         # 전부
"""
import os
import sys
import json
import requests
import hashlib
from datetime import date
from bs4 import BeautifulSoup

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DATA_DIR = os.path.join(ROOT, 'departments/intelligence/data')
os.makedirs(DATA_DIR, exist_ok=True)

env = {}
for line in open(os.path.join(ROOT, '.secrets'), encoding='utf-8'):
    if '=' in line:
        k, v = line.strip().split('=', 1)
        env[k] = v

TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')

# 부서별 타겟 정의
DEPT_TARGETS = {
    'tax': {
        'label': '💰 세금N혜택',
        'targets': [
            {'name': '삼쩜삼', 'url': 'https://3o3.co.kr/'},
            {'name': 'SSEM', 'url': 'https://ssem.kr/'},
            {'name': '택슬리', 'url': 'https://taxly.kr/'},
        ],
    },
    'saju': {
        'label': '🔮 천명당 (사주)',
        'targets': [
            {'name': '점신', 'url': 'https://www.jeomsin.co.kr/'},
            {'name': '포스텔러', 'url': 'https://www.posteller.com/'},
            {'name': '헬로우봇', 'url': 'https://hellobot.co/'},
        ],
    },
    'insurance': {
        'label': '🛡️ 보험다보여',
        'targets': [
            {'name': '보맵', 'url': 'https://bomapp.com/'},
            {'name': '굿리치', 'url': 'https://www.goodrich.co.kr/'},
            {'name': '레몬클립', 'url': 'https://www.lemonclip.com/'},
        ],
    },
    'prompts': {
        'label': '📝 크티 프롬프트',
        'targets': [
            {'name': 'PromptBase', 'url': 'https://promptbase.com/'},
            {'name': '크티', 'url': 'https://ctee.kr/'},
            {'name': 'PromptHero', 'url': 'https://prompthero.com/'},
        ],
    },
    'kdp': {
        'label': '📖 KDP 전자책',
        'targets': [
            {'name': 'Amazon 베스트셀러 로코믹', 'url': 'https://www.amazon.com/Best-Sellers-Books-Low-Content-Books/zgbs/books/14111361011'},
            {'name': 'Amazon 베스트셀러 저널', 'url': 'https://www.amazon.com/Best-Sellers-Books-Journals/zgbs/books/10807'},
        ],
    },
    'korlens': {
        'label': '🔍 KORLENS (관광 큐레이션)',
        'targets': [
            {'name': '대한민국 구석구석 (공식)', 'url': 'https://korean.visitkorea.or.kr/'},
            {'name': '트리플', 'url': 'https://triple.guide/intro'},
            {'name': '마이리얼트립', 'url': 'https://www.myrealtrip.com/'},
            {'name': '트립닷컴 국내여행', 'url': 'https://kr.trip.com/'},
            {'name': 'Mindtrip AI', 'url': 'https://mindtrip.ai/'},
            {'name': 'Layla AI', 'url': 'https://layla.ai/'},
        ],
    },
}


def fetch(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        return r.text if r.ok else None
    except Exception:
        return None


def hash_content(t):
    return hashlib.sha256((t or '').encode()).hexdigest()[:16]


def extract(html):
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    texts = []
    for selector in ['h1', 'h2', 'h3', '.title', '.price', '.btn', 'nav a', '[class*="title"]', '[class*="price"]']:
        for el in soup.select(selector)[:30]:
            t = el.get_text(strip=True)
            if t and 3 <= len(t) <= 100:
                texts.append(t)
    return list(dict.fromkeys(texts))[:50]


def snapshot_dept(dept_key):
    dept = DEPT_TARGETS[dept_key]
    today = date.today().isoformat()
    result = {'dept': dept_key, 'label': dept['label'], 'date': today, 'targets': []}

    for t in dept['targets']:
        html = fetch(t['url'])
        data = {
            'name': t['name'], 'url': t['url'],
            'fetched': html is not None,
            'hash': hash_content(html) if html else None,
            'texts': extract(html),
        }
        result['targets'].append(data)
        ok = '✅' if html else '❌'
        print(f'  [{dept_key}/{t["name"]}] {ok} {len(data["texts"])} texts')

    out = os.path.join(DATA_DIR, f'{dept_key}_snapshot_{today}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def diff_with_previous(dept_key, today_data):
    files = sorted([f for f in os.listdir(DATA_DIR)
                    if f.startswith(f'{dept_key}_snapshot_') and f.endswith('.json')])
    today_file = f'{dept_key}_snapshot_{today_data["date"]}.json'
    prev_files = [f for f in files if f != today_file]

    if not prev_files:
        return '(이전 스냅샷 없음)'

    with open(os.path.join(DATA_DIR, prev_files[-1]), encoding='utf-8') as f:
        prev = json.load(f)

    changes = []
    for t_today in today_data['targets']:
        t_prev = next((x for x in prev['targets'] if x['name'] == t_today['name']), None)
        if not t_prev:
            changes.append(f"➕ {t_today['name']} 추가")
            continue
        if t_today['hash'] != t_prev['hash']:
            new = set(t_today['texts']) - set(t_prev['texts'])
            gone = set(t_prev['texts']) - set(t_today['texts'])
            if new:
                changes.append(f"{t_today['name']}:")
                changes.append(f"  ➕ {', '.join(list(new)[:3])}")
            if gone:
                changes.append(f"  ➖ {', '.join(list(gone)[:3])}")
    return '\n'.join(changes) if changes else '변경 없음'


def notify(results):
    if not TG_TOKEN:
        return
    lines = [f"<b>🕵️ 경쟁사 수집 리포트</b>", f"<i>{date.today().isoformat()}</i>", ""]
    for r in results:
        lines.append(f"<b>{r['data']['label']}</b>")
        for t in r['data']['targets']:
            s = '✅' if t['fetched'] else '❌'
            lines.append(f"  {s} {t['name']} ({len(t['texts'])})")
        lines.append(f"  <i>diff:</i> {r['diff'][:200]}")
        lines.append("")

    text = '\n'.join(lines)
    requests.post(
        f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
        data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML'}
    )


def run(dept_keys):
    results = []
    for key in dept_keys:
        if key not in DEPT_TARGETS:
            print(f'[SKIP] 알 수 없는 부서: {key}')
            continue
        print(f'\n[{DEPT_TARGETS[key]["label"]}] 스냅샷 시작')
        data = snapshot_dept(key)
        diff = diff_with_previous(key, data)
        print(f'  diff: {diff[:150]}')
        results.append({'dept': key, 'data': data, 'diff': diff})
    if results:
        notify(results)
        print(f'\n[완료] 텔레그램 리포트 발송')


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'all':
        run(list(DEPT_TARGETS.keys()))
    else:
        run([sys.argv[1]])
