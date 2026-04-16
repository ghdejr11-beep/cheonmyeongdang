#!/usr/bin/env python3
"""
세금N혜택 경쟁사 인텔리전스 수집부
— 경쟁 서비스 신기능·가격·리뷰 매일 수집

타겟:
  - 삼쩜삼 (3o3.co.kr)
  - 토스인컴 (tossincome)
  - SSEM (ssem.kr)
  - 택슬리 (taxly.kr)

수집 항목:
  1. 신규 공지사항 (새 기능 힌트)
  2. 가격표 변화
  3. 리뷰 사이트 불만 (플레이스토어)
  4. 검색 트렌드 (환급 관련 키워드)

결과:
  - data/competitor_snapshot_YYYY-MM-DD.json
  - Claude Agent가 분석 → 개선 제안 텔레그램 발송
"""
import os
import json
import requests
import hashlib
from datetime import datetime, date
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

TARGETS = [
    {
        'name': '삼쩜삼',
        'homepage': 'https://3o3.co.kr/',
        'notice': 'https://help.3o3.co.kr/hc/ko/sections/4410049731471-%EA%B3%B5%EC%A7%80%EC%82%AC%ED%95%AD',
    },
    {
        'name': 'SSEM',
        'homepage': 'https://ssem.kr/',
    },
    {
        'name': '택슬리',
        'homepage': 'https://taxly.kr/',
    },
]


def fetch(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        return r.text if r.ok else None
    except Exception as e:
        return None


def hash_content(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def extract_key_texts(html):
    """HTML에서 타이틀·헤더·주요 텍스트만 뽑기"""
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    # script, style 제거
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    texts = []
    for selector in ['h1', 'h2', 'h3', '.title', '.price', '.btn', 'nav a']:
        for el in soup.select(selector)[:30]:
            t = el.get_text(strip=True)
            if t and 3 <= len(t) <= 100:
                texts.append(t)
    return list(dict.fromkeys(texts))[:50]  # 중복 제거, 상위 50개


def snapshot():
    today = date.today().isoformat()
    result = {'date': today, 'targets': []}

    for t in TARGETS:
        html = fetch(t['homepage'])
        data = {
            'name': t['name'],
            'url': t['homepage'],
            'fetched': html is not None,
            'hash': hash_content(html) if html else None,
            'texts': extract_key_texts(html),
        }
        result['targets'].append(data)
        print(f'  [{t["name"]}] {"OK" if html else "FAIL"} - {len(data["texts"])} texts')

    # 저장
    out = os.path.join(DATA_DIR, f'tax_snapshot_{today}.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'\n[OK] 저장: {out}')
    return result


def compare_with_previous(today_data):
    """이전 스냅샷과 비교해서 변경점 찾기"""
    today = today_data['date']
    files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith('tax_snapshot_') and f.endswith('.json')])
    prev_files = [f for f in files if not f.endswith(f'{today}.json')]

    if not prev_files:
        return '이전 스냅샷 없음 (첫 실행)'

    prev_path = os.path.join(DATA_DIR, prev_files[-1])
    with open(prev_path, encoding='utf-8') as f:
        prev = json.load(f)

    changes = []
    for t_today in today_data['targets']:
        t_prev = next((x for x in prev['targets'] if x['name'] == t_today['name']), None)
        if not t_prev:
            changes.append(f"{t_today['name']}: 신규 추가")
            continue
        if t_today['hash'] != t_prev['hash']:
            # 텍스트 diff
            new_texts = set(t_today['texts']) - set(t_prev['texts'])
            gone_texts = set(t_prev['texts']) - set(t_today['texts'])
            if new_texts or gone_texts:
                changes.append(f"{t_today['name']}:")
                if new_texts:
                    changes.append(f"  ➕ 신규: {', '.join(list(new_texts)[:5])}")
                if gone_texts:
                    changes.append(f"  ➖ 제거: {', '.join(list(gone_texts)[:5])}")

    return '\n'.join(changes) if changes else '변경 없음'


def notify(data, diff):
    if not TG_TOKEN:
        return
    text = f"<b>🕵️ 세금N혜택 경쟁사 수집 리포트</b>\n"
    text += f"<i>{data['date']}</i>\n\n"
    for t in data['targets']:
        status = '✅' if t['fetched'] else '❌'
        text += f"{status} {t['name']} ({len(t['texts'])}개 텍스트)\n"
    text += f"\n<b>변경점:</b>\n<pre>{diff}</pre>\n"
    text += f"\n📂 저장됨: tax_snapshot_{data['date']}.json"

    requests.post(
        f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
        data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML'}
    )


if __name__ == '__main__':
    print('[세금N혜택 수집부] 경쟁사 스냅샷 수집 시작...')
    data = snapshot()
    diff = compare_with_previous(data)
    notify(data, diff)
    print(f'\n[완료] 변경점:\n{diff}')
