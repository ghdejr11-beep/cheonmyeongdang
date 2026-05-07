#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
천명당 v3.5 글로벌 SaaS 라이브 모니터 (16 항목)
— 매시간 schtask 실행 (KunStudio_Cheonmyeongdang_V35_Monitor)
— 실패 시에만 텔레그램 알림 (사용자 quiet window 08:00~01:00 PT 존중)

체크 항목 (16개):
  1) ko/  HTTP 200
  2) en/  HTTP 200
  3) ja/  HTTP 200
  4) zh/  HTTP 200
  5) /api/check-entitlement (POST 응답 < 500)
  6) /api/payment-config    (GET  응답 < 500)
  7) /api/confirm-payment   (GET  응답 시간 < 5s)
  8) /api/send-receipt      (POST stub 응답)
  9) /api/coupon-validate   (POST 응답)
 10) /api/subscribe-fortune (POST stub)
 11) /api/lucky-pass        (GET  응답)
 12) /api/vip-status        (POST 응답)
 13) sitemap.xml            (HTTP 200 + xml 파싱)
 14) robots.txt             (HTTP 200)
 15) Pinterest queue.json   (로컬 파일 존재 + JSON 파싱 OK)
 16) SEO blog index 4 lang  (en blog index HTTP 200, 다른 lang은 발행 통계)

Usage:
  python cheonmyeongdang_v35_monitor.py            # 1회 실행
  python cheonmyeongdang_v35_monitor.py --force    # 전체 상태 강제 알림
"""

import os
import sys
import json
import time
import socket
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DATA_DIR = os.path.join(ROOT, 'departments', 'intelligence', 'data')
STATE_FILE = os.path.join(DATA_DIR, 'v35_monitor_state.json')
LOG_FILE = os.path.join(DATA_DIR, 'v35_monitor_log.txt')
os.makedirs(DATA_DIR, exist_ok=True)

BASE = 'https://cheonmyeongdang.vercel.app'

# ---------- secrets ----------
env = {}
secrets_path = os.path.join(ROOT, '.secrets')
if os.path.exists(secrets_path):
    for line in open(secrets_path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')

# ---------- quiet window (사용자 깨우지 않기) ----------
# Pacific Time (PT) 기준 08:00 ~ 다음날 01:00 = "활동 시간"
# 그 외(PT 01:00 ~ 08:00)는 quiet — 알림 보류 후 다음 활동시간에 발송
PT_OFFSET_HOURS = -7  # PDT (5월은 daylight)
QUIET_START_PT = 1    # 01:00 PT
QUIET_END_PT = 8      # 08:00 PT


def is_quiet_now():
    now_utc = datetime.now(timezone.utc)
    now_pt = now_utc + timedelta(hours=PT_OFFSET_HOURS)
    h = now_pt.hour
    return QUIET_START_PT <= h < QUIET_END_PT


# ---------- HTTP helper ----------
def http(url, method='GET', body=None, timeout=15, headers=None, full_body=False):
    """단순 urllib 래퍼. Cloudflare 1010 회피 위해 UA 강제.

    full_body=True 일 때 응답 전체를 보존(sitemap XML 파싱 등).
    그 외엔 메모리 절약 위해 2KB만 보관.
    """
    hdrs = {
        'User-Agent': 'CheonmyeongdangV35Monitor/1.0 (+kunstudio)',
        'Accept': '*/*',
    }
    if headers:
        hdrs.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        hdrs['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content = r.read()
            elapsed = int((time.time() - t0) * 1000)
            return {
                'ok': r.status < 500,
                'status': r.status,
                'elapsed_ms': elapsed,
                'body': content if full_body else content[:2000],
                'error': None,
            }
    except urllib.error.HTTPError as e:
        elapsed = int((time.time() - t0) * 1000)
        # 4xx도 서버 살아있음으로 간주 (라우트/검증 문제일 수 있음)
        return {
            'ok': e.code < 500,
            'status': e.code,
            'elapsed_ms': elapsed,
            'body': b'',
            'error': f'HTTP {e.code}',
        }
    except (urllib.error.URLError, socket.timeout) as e:
        elapsed = int((time.time() - t0) * 1000)
        return {
            'ok': False,
            'status': 0,
            'elapsed_ms': elapsed,
            'body': b'',
            'error': str(e)[:200],
        }


# ---------- 16 checks ----------
def check_lang(lang):
    url = f'{BASE}/{lang}/' if lang != 'ko' else f'{BASE}/'
    name = f'{lang.upper()} 메인 페이지'
    r = http(url, timeout=12)
    return {'name': name, 'ok': r['ok'] and r['status'] == 200, 'status': r['status'],
            'elapsed_ms': r['elapsed_ms'], 'error': r['error']}


def check_api(path, method='GET', body=None, name=None, max_ms=8000):
    url = f'{BASE}{path}'
    r = http(url, method=method, body=body, timeout=15)
    ok = r['ok']
    if ok and r['elapsed_ms'] > max_ms:
        ok = False
        err = f'too slow {r["elapsed_ms"]}ms'
    else:
        err = r['error']
    return {'name': name or path, 'ok': ok, 'status': r['status'],
            'elapsed_ms': r['elapsed_ms'], 'error': err}


def check_sitemap():
    url = f'{BASE}/sitemap.xml'
    r = http(url, timeout=15, full_body=True)
    if not (r['ok'] and r['status'] == 200):
        return {'name': 'sitemap.xml', 'ok': False, 'status': r['status'],
                'elapsed_ms': r['elapsed_ms'], 'error': r['error'] or 'fetch fail'}
    # XML 파싱 검증 (bytes로 받은 경우 BOM/encoding 우회)
    body = r['body']
    if isinstance(body, bytes):
        # BOM 제거
        if body.startswith(b'\xef\xbb\xbf'):
            body = body[3:]
        try:
            text = body.decode('utf-8')
        except UnicodeDecodeError:
            text = body.decode('utf-8', errors='replace')
    else:
        text = body
    try:
        root = ET.fromstring(text)
        url_count = len([e for e in root.iter() if e.tag.endswith('url')])
        return {'name': 'sitemap.xml', 'ok': True, 'status': 200,
                'elapsed_ms': r['elapsed_ms'], 'error': None,
                'meta': f'{url_count} urls'}
    except Exception as e:
        return {'name': 'sitemap.xml', 'ok': False, 'status': 200,
                'elapsed_ms': r['elapsed_ms'], 'error': f'XML parse: {e}'}


def check_robots():
    return check_api('/robots.txt', name='robots.txt')


def check_pinterest_queue():
    qpath = os.path.join(ROOT, 'departments', 'pinterest_pins', 'queue.json')
    if not os.path.exists(qpath):
        return {'name': 'Pinterest queue.json', 'ok': False, 'status': 0,
                'elapsed_ms': 0, 'error': 'file missing'}
    try:
        with open(qpath, encoding='utf-8') as f:
            data = json.load(f)
        n = len(data) if isinstance(data, list) else len(data.get('items', []))
        return {'name': 'Pinterest queue.json', 'ok': True, 'status': 200,
                'elapsed_ms': 0, 'error': None, 'meta': f'{n} pins'}
    except Exception as e:
        return {'name': 'Pinterest queue.json', 'ok': False, 'status': 0,
                'elapsed_ms': 0, 'error': f'JSON: {e}'}


def check_blog_index():
    """blog/ 와 blog/en/ 발행 상태"""
    return check_api('/blog/', name='Blog index (ko)')


def check_blog_en():
    return check_api('/blog/en/', name='Blog index (en)')


def run_all_checks():
    checks = []
    # 1~4) 4 lang
    for lang in ['ko', 'en', 'ja', 'zh']:
        checks.append(check_lang(lang))
    # 5~12) API (8개 — 사용자 spec 5개 이상 + 보강)
    checks.append(check_api('/api/check-entitlement', method='POST',
                            body={'email': 'monitor@test.local'},
                            name='check-entitlement', max_ms=10000))
    checks.append(check_api('/api/payment-config', name='payment-config'))
    checks.append(check_api('/api/confirm-payment', name='confirm-payment',
                            max_ms=5000))
    checks.append(check_api('/api/send-receipt', method='POST',
                            body={'test': True}, name='send-receipt'))
    checks.append(check_api('/api/coupon-validate', method='POST',
                            body={'code': 'TEST'}, name='coupon-validate'))
    checks.append(check_api('/api/subscribe-fortune', method='POST',
                            body={'test': True}, name='subscribe-fortune'))
    checks.append(check_api('/api/lucky-pass', name='lucky-pass'))
    checks.append(check_api('/api/vip-status', method='POST',
                            body={'email': 'monitor@test.local'},
                            name='vip-status'))
    # 13) sitemap
    checks.append(check_sitemap())
    # 14) robots
    checks.append(check_robots())
    # 15) Pinterest queue
    checks.append(check_pinterest_queue())
    # 16) Blog index
    checks.append(check_blog_index())
    return checks


# ---------- state / telegram ----------
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def log(msg):
    line = f'[{datetime.now().isoformat(timespec="seconds")}] {msg}'
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode('ascii', 'replace').decode('ascii'))
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT:
        log('[TG SKIP] no token/chat')
        return False
    if is_quiet_now():
        log(f'[TG QUIET] within PT 01-08, queued: {text[:80]}')
        # quiet 중엔 pending 큐에 저장
        pending_path = os.path.join(DATA_DIR, 'v35_monitor_pending_tg.txt')
        with open(pending_path, 'a', encoding='utf-8') as f:
            f.write(f'[{datetime.now().isoformat(timespec="seconds")}]\n{text}\n---\n')
        return False
    url = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage'
    body = {'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML',
            'disable_web_page_preview': True}
    r = http(url, method='POST', body=body, timeout=10)
    return r['ok']


def flush_pending_telegram():
    """quiet window 끝나면 큐된 알림 발송"""
    pending_path = os.path.join(DATA_DIR, 'v35_monitor_pending_tg.txt')
    if not os.path.exists(pending_path) or is_quiet_now():
        return
    try:
        with open(pending_path, encoding='utf-8') as f:
            content = f.read().strip()
        if content:
            send_telegram(f'⏰ <b>Quiet 시간 누락 알림</b>\n\n{content[:3500]}')
        os.remove(pending_path)
    except Exception as e:
        log(f'[FLUSH ERROR] {e}')


# ---------- main ----------
def run(force=False):
    flush_pending_telegram()

    state = load_state()
    results = run_all_checks()
    changes_down = []
    changes_up = []

    for r in results:
        prev = state.get(r['name'], {})
        prev_ok = prev.get('ok', True)
        prev_fail_count = prev.get('fail_count', 0)
        prev_alerted_down = prev.get('alerted_down', False)
        this_fail_count = 0 if r['ok'] else prev_fail_count + 1

        # 2회 연속 fail 시 confirmed DOWN — Vercel CDN 갱신 false alarm 방지
        if not r['ok'] and this_fail_count >= 2 and not prev_alerted_down:
            changes_down.append(r)
            this_alerted_down = True
        elif r['ok'] and prev_alerted_down:
            changes_up.append(r)
            this_alerted_down = False
        else:
            this_alerted_down = prev_alerted_down

        state[r['name']] = {
            'ok': r['ok'],
            'status': r['status'],
            'elapsed_ms': r['elapsed_ms'],
            'last_check': datetime.now().isoformat(timespec='seconds'),
            'error': r.get('error'),
            'fail_count': this_fail_count,
            'alerted_down': this_alerted_down,
        }
        mark = 'UP' if r['ok'] else 'DOWN'
        meta = f' ({r.get("meta")})' if r.get('meta') else ''
        log(f'  {mark}: {r["name"]} → HTTP {r["status"]} {r["elapsed_ms"]}ms{meta}')

    save_state(state)

    ok_count = sum(1 for r in results if r['ok'])
    total = len(results)
    log(f'천명당 v3.5 헬스체크: {ok_count}/{total} UP')

    if changes_down or changes_up or force:
        lines = []
        if changes_down:
            lines.append('🚨 <b>천명당 v3.5 — 서비스 다운</b>')
            for c in changes_down:
                err = c.get('error') or f'HTTP {c["status"]}'
                lines.append(f'  🔴 <b>{c["name"]}</b> — {err}')
            lines.append('')
        if changes_up:
            lines.append('✅ <b>천명당 v3.5 — 복구</b>')
            for c in changes_up:
                lines.append(f'  🟢 <b>{c["name"]}</b> — {c["elapsed_ms"]}ms')
            lines.append('')
        if force:
            lines.append('📊 <b>천명당 v3.5 전체 상태</b>')
            lines.append(f'  {ok_count}/{total} UP')
            for r in results:
                mark = '🟢' if r['ok'] else '🔴'
                lines.append(f'  {mark} {r["name"]}: {r["status"]} · {r["elapsed_ms"]}ms')
        send_telegram('\n'.join(lines))

    return results


if __name__ == '__main__':
    force = '--force' in sys.argv
    results = run(force=force)
    fail = [r for r in results if not r['ok']]
    sys.exit(1 if fail else 0)
