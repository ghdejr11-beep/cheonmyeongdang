#!/usr/bin/env python3
"""
Postiz API 래퍼 — 모든 연결된 채널에 동시 게시.

기존 auto_promo.py의 send_telegram()을 이 모듈의 send_all_channels()로
교체하면, Postiz 대시보드에 추가된 모든 채널(텔레그램/IG/YouTube/X 등)에
자동 발행됨. 플랫폼 연결될 때마다 코드 수정 불필요.
"""
import os
import sys
import json
import datetime
import urllib.request
import urllib.error


ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')


def _load_secrets():
    env = {}
    path = os.path.join(ROOT, '.secrets')
    if os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                env[k] = v
    return env


_env = _load_secrets()
POSTIZ_URL = _env.get('POSTIZ_URL', '').rstrip('/')
POSTIZ_API_KEY = _env.get('POSTIZ_API_KEY', '')


def _request(method, path, body=None):
    url = f"{POSTIZ_URL}/api/public/v1{path}"
    headers = {
        'Authorization': POSTIZ_API_KEY,
        'Content-Type': 'application/json',
    }
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, {'error': e.read().decode('utf-8', errors='ignore')}
    except Exception as e:
        return 0, {'error': str(e)}


def list_integrations():
    """현재 연결된 채널(Postiz의 '통합') 목록."""
    status, data = _request('GET', '/integrations')
    return data if status == 200 else []


def send_all_channels(content, include_coupang=True):
    """모든 연결 채널에 즉시 발행. 반환: {integration_name: ok}

    include_coupang=True 이면 5회 포스트당 1회 쿠팡 파트너스 블록 자동 삽입 (공정위 문구 포함)
    """
    if not POSTIZ_URL or not POSTIZ_API_KEY:
        print('[postiz] URL/API 키 미설정 (.secrets 확인)')
        return {}

    # 쿠팡 파트너스 자동 삽입 (5회당 1회)
    if include_coupang:
        try:
            from coupang_rotator import maybe_coupang_block
            coupang_block = maybe_coupang_block('ko')
            if coupang_block:
                content = content + '\n\n' + coupang_block
                print('[postiz] 쿠팡 파트너스 블록 삽입됨')
        except Exception as e:
            print(f'[postiz] 쿠팡 rotator 오류: {e}')

    integrations = list_integrations()
    if not integrations:
        print('[postiz] 연결된 채널 없음')
        return {}

    # 플랫폼별 본문 변환 (Telegram은 HTML 그대로, 나머지는 HTML 태그 제거)
    posts = []
    for intg in integrations:
        platform = intg.get('identifier', '')
        body = content if platform == 'telegram' else _strip_html(content)
        posts.append({
            'integration': {'id': intg['id']},
            'value': [{'content': body, 'image': []}],
            'settings': {'__type': platform},
        })

    now_iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    payload = {
        'type': 'now',
        'date': now_iso,
        'shortLink': False,
        'tags': [],
        'posts': posts,
    }

    status, data = _request('POST', '/posts', payload)
    ok_by_name = {}
    if status in (200, 201):
        for intg in integrations:
            ok_by_name[intg['name'] or intg['identifier']] = True
    else:
        print(f'[postiz] POST 실패 {status}: {data}')
        for intg in integrations:
            ok_by_name[intg['name'] or intg['identifier']] = False
    return ok_by_name


def _strip_html(html):
    """간단한 HTML 태그 제거 — <b>, <i>, <br> 등만 처리."""
    import re
    text = re.sub(r'<br\s*/?>', '\n', html)
    text = re.sub(r'</?[a-zA-Z][^>]*>', '', text)
    return text


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        for intg in list_integrations():
            print(f"{intg['identifier']:12s} {intg['name']:20s} id={intg['id']}")
    elif cmd == 'test':
        msg = ('<b>🔔 Postiz 래퍼 테스트</b>\n\n'
               'auto_promo → Postiz API → 모든 채널 자동 발행 파이프라인 검증.')
        result = send_all_channels(msg)
        for name, ok in result.items():
            print(f"  [{name}] {'OK' if ok else 'FAIL'}")
    else:
        print('사용법: python postiz_poster.py [list|test]')
