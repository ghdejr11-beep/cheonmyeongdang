#!/usr/bin/env python3
"""
서비스 Health Check 에이전트
— 운영중인 모든 Vercel/프로덕션 서비스 5분마다 ping
— 상태 변화(정상→실패 or 실패→정상) 시에만 텔레그램 알림 (스팸 방지)

Usage:
  python health_check.py         # 1회 체크 + 상태 변화 알림
  python health_check.py --once  # 1회만 조용히 체크 (cron용)
  python health_check.py --force # 강제 현재 상태 전체 알림
"""
import os
import sys
import json
import time
import requests
from datetime import datetime

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DATA_DIR = os.path.join(ROOT, 'departments/intelligence/data')
STATE_FILE = os.path.join(DATA_DIR, 'health_state.json')
LOG_FILE = os.path.join(DATA_DIR, 'health_log.txt')
os.makedirs(DATA_DIR, exist_ok=True)

env = {}
secrets_path = os.path.join(ROOT, '.secrets')
if os.path.exists(secrets_path):
    for line in open(secrets_path, encoding='utf-8'):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v
TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')

# 감시 대상 서비스
SERVICES = [
    {
        'name': 'KORLENS',
        'url': 'https://korlens.vercel.app/',
        'emoji': '🔍',
        'timeout': 10,
    },
    {
        'name': 'KORLENS 챗봇 API',
        'url': 'https://korlens.vercel.app/api/chat',
        'method': 'POST',
        'body': {'messages': [{'role': 'user', 'content': 'ping'}]},
        'emoji': '🤖',
        'timeout': 30,
    },
    {
        # 세금N혜택 API — /api/connect는 POST만 허용 (CODEF 인증 트리거).
        # health check은 GET을 지원하는 다른 endpoint 또는 POST 시도.
        'name': '세금N혜택 API',
        'url': 'https://tax-n-benefit-api.vercel.app/',  # 메인 페이지로 변경 (GET 200)
        'emoji': '💰',
        'timeout': 10,
    },
]


def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT:
        print('[TG SKIP]', text[:100])
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML'},
            timeout=10,
        )
    except Exception as e:
        print(f'[TG ERROR] {e}')


def log(msg):
    line = f'[{datetime.now().isoformat(timespec="seconds")}] {msg}'
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode('ascii', 'replace').decode('ascii'))
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def ping(service):
    """
    서버 생존 판단 기준:
    - 2xx/3xx = 정상 UP
    - 4xx (401/403/404/405) = 서버 살아있음, 라우트·인증 문제일 수 있음 → UP 처리
    - 5xx = 서버 장애 DOWN
    - Connection error / Timeout = DOWN
    """
    method = service.get('method', 'GET')
    timeout = service.get('timeout', 10)
    try:
        start = time.time()
        if method == 'POST':
            r = requests.post(service['url'], json=service.get('body'), timeout=timeout)
        else:
            r = requests.get(service['url'], timeout=timeout)
        elapsed = int((time.time() - start) * 1000)
        # 2xx/3xx/4xx = 서버 살아있음. 5xx만 DOWN.
        ok = r.status_code < 500
        return {
            'ok': ok,
            'status': r.status_code,
            'elapsed_ms': elapsed,
            'error': None,
        }
    except Exception as e:
        return {
            'ok': False,
            'status': 0,
            'elapsed_ms': 0,
            'error': str(e)[:200],
        }


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def run(force=False):
    state = load_state()
    changes = []
    results = []

    for svc in SERVICES:
        r = ping(svc)
        result = {'name': svc['name'], 'emoji': svc['emoji'], **r}
        results.append(result)

        prev = state.get(svc['name'], {})
        prev_ok = prev.get('ok', True)

        # 상태 변화 감지
        if prev_ok != r['ok']:
            changes.append(result)

        state[svc['name']] = {
            'ok': r['ok'],
            'status': r['status'],
            'elapsed_ms': r['elapsed_ms'],
            'last_check': datetime.now().isoformat(timespec='seconds'),
        }
        log(f"{svc['emoji']} {svc['name']}: {'UP' if r['ok'] else 'DOWN'} ({r['status']}, {r['elapsed_ms']}ms)")

    save_state(state)

    # 상태 변화 또는 force일 때 알림
    if changes or force:
        lines = []
        if changes:
            downs = [c for c in changes if not c['ok']]
            ups = [c for c in changes if c['ok']]
            if downs:
                lines.append('🚨 <b>서비스 다운</b>')
                for c in downs:
                    err = c.get('error') or f"HTTP {c['status']}"
                    lines.append(f"{c['emoji']} <b>{c['name']}</b> — {err}")
                lines.append('')
            if ups:
                lines.append('✅ <b>서비스 복구</b>')
                for c in ups:
                    lines.append(f"{c['emoji']} <b>{c['name']}</b> — {c['elapsed_ms']}ms")
                lines.append('')
        if force:
            lines.append('📊 <b>전체 Health 상태</b>')
            for r in results:
                mark = '✅' if r['ok'] else '🔴'
                lines.append(f"{mark} {r['emoji']} {r['name']}: HTTP {r['status']} · {r['elapsed_ms']}ms")

        send_telegram('\n'.join(lines))

    return results


if __name__ == '__main__':
    force = '--force' in sys.argv
    results = run(force=force)
    # 간단 요약 출력
    ok_count = sum(1 for r in results if r['ok'])
    print(f'\n{ok_count}/{len(results)} services UP')
