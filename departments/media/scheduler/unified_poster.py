#!/usr/bin/env python3
"""
쿤스튜디오 통합 미디어 포스터
— 하나의 큐에서 꺼내 플랫폼별 자동 포스팅 (텔레그램 + X + 인스타 + 카카오 + 라인)

큐 포맷 (posts_unified_queue.json):
[
  {
    "id": "P123",
    "service": "korlens" | "tax" | "cheonmyeongdang" | "hexdrop" | ...,
    "targets": ["telegram", "x", "instagram", "kakao", "line"],
    "title": "코렌즈 출시 안내",
    "body_ko": "한국관광 AI 큐레이션 서비스 KORLENS 출시!...",
    "body_en": "Introducing KORLENS, AI-curated Korean travel...",
    "link": "https://korlens.vercel.app",
    "image_url": "https://.../promo.jpg",
    "scheduled_at": "2026-04-20T09:00:00",  # 이 시간 이후 자동 발송
    "status": "pending" | "sent" | "failed",
    "results": {"telegram": "ok", "x": "ok", ...}
  }
]

Usage:
  python unified_poster.py              # 예약 도달한 포스트 발송
  python unified_poster.py --enqueue    # 대화형 새 포스트 추가
  python unified_poster.py --list       # 큐 현황
  python unified_poster.py --now P123   # 특정 포스트 즉시 발송
"""
import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
DEPT_DIR = os.path.join(ROOT, 'departments/media/scheduler')
QUEUE_FILE = os.path.join(DEPT_DIR, 'posts_unified_queue.json')
LOG_FILE = os.path.join(DEPT_DIR, 'unified_log.txt')

env = {}
secrets_path = os.path.join(ROOT, '.secrets')
if os.path.exists(secrets_path):
    for line in open(secrets_path, encoding='utf-8'):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

# 각 플랫폼 자격증명 (.secrets에서)
TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_CHAT_ID', '')
X_KEY = env.get('X_API_KEY', '')
X_SECRET = env.get('X_API_SECRET', '')
X_TOKEN = env.get('X_ACCESS_TOKEN', '')
X_TOKEN_SECRET = env.get('X_ACCESS_SECRET', '')
KAKAO_TOKEN = env.get('KAKAO_ACCESS_TOKEN', '')
LINE_TOKEN = env.get('LINE_CHANNEL_TOKEN', '')
IG_LONG_TOKEN = env.get('IG_LONG_LIVED_TOKEN', '')
IG_USER_ID = env.get('IG_USER_ID', '')


def log(msg: str):
    line = f'[{datetime.now().isoformat(timespec="seconds")}] {msg}'
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


# ===== 플랫폼별 포스터 =====

def post_telegram(post: dict) -> dict:
    if not TG_TOKEN or not TG_CHAT:
        return {'ok': False, 'error': 'no TG credentials'}
    text = f"<b>{post.get('title', '')}</b>\n\n{post.get('body_ko', '')}"
    if post.get('link'):
        text += f"\n\n👉 {post['link']}"
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'text': text, 'parse_mode': 'HTML',
                  'disable_web_page_preview': 'false'},
            timeout=15,
        )
        return {'ok': r.ok, 'status': r.status_code, 'resp': r.text[:200]}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


def post_x(post: dict) -> dict:
    """X (Twitter) — tweepy 필요"""
    if not all([X_KEY, X_SECRET, X_TOKEN, X_TOKEN_SECRET]):
        return {'ok': False, 'error': 'no X credentials'}
    try:
        import tweepy
    except ImportError:
        return {'ok': False, 'error': 'tweepy not installed'}
    body = post.get('body_en') or post.get('body_ko', '')
    # X 280자 제한
    text = (post.get('title', '') + ' — ' + body)[:260]
    if post.get('link'):
        text = text[:260 - len(post['link']) - 1] + ' ' + post['link']
    try:
        client = tweepy.Client(
            consumer_key=X_KEY, consumer_secret=X_SECRET,
            access_token=X_TOKEN, access_token_secret=X_TOKEN_SECRET,
        )
        r = client.create_tweet(text=text)
        return {'ok': True, 'id': r.data.get('id') if r.data else None}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


def post_instagram(post: dict) -> dict:
    """Instagram Graph API (이미지 게시만)"""
    if not (IG_LONG_TOKEN and IG_USER_ID):
        return {'ok': False, 'error': 'no IG credentials'}
    if not post.get('image_url'):
        return {'ok': False, 'error': 'image_url required for IG'}
    caption = f"{post.get('title', '')}\n\n{post.get('body_ko', '')}\n\n{post.get('link', '')}"
    try:
        # 1) 미디어 컨테이너 생성
        r1 = requests.post(
            f'https://graph.instagram.com/v21.0/{IG_USER_ID}/media',
            data={'image_url': post['image_url'], 'caption': caption[:2200],
                  'access_token': IG_LONG_TOKEN},
            timeout=30,
        )
        d = r1.json()
        container = d.get('id')
        if not container:
            return {'ok': False, 'error': f'container failed: {d}'}
        # 2) publish
        r2 = requests.post(
            f'https://graph.instagram.com/v21.0/{IG_USER_ID}/media_publish',
            data={'creation_id': container, 'access_token': IG_LONG_TOKEN},
            timeout=30,
        )
        return {'ok': r2.ok, 'resp': r2.text[:200]}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


def post_kakao(post: dict) -> dict:
    """카카오톡 나에게 보내기 (개인용) — 채널 메시지는 별도 사업자 인증 필요"""
    if not KAKAO_TOKEN:
        return {'ok': False, 'error': 'no KAKAO token (need OAuth refresh)'}
    try:
        template = {
            'object_type': 'text',
            'text': f"{post.get('title', '')}\n\n{post.get('body_ko', '')}",
            'link': {'web_url': post.get('link', '')},
        }
        r = requests.post(
            'https://kapi.kakao.com/v2/api/talk/memo/default/send',
            headers={'Authorization': f'Bearer {KAKAO_TOKEN}'},
            data={'template_object': json.dumps(template)},
            timeout=15,
        )
        return {'ok': r.ok, 'status': r.status_code, 'resp': r.text[:200]}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


def post_line(post: dict) -> dict:
    """LINE Messaging API (비즈니스 계정)"""
    if not LINE_TOKEN:
        return {'ok': False, 'error': 'no LINE token'}
    text = f"{post.get('title', '')}\n{post.get('body_ko', '')}"
    if post.get('link'):
        text += f"\n{post['link']}"
    try:
        r = requests.post(
            'https://api.line.me/v2/bot/message/broadcast',
            headers={'Authorization': f'Bearer {LINE_TOKEN}',
                     'Content-Type': 'application/json'},
            json={'messages': [{'type': 'text', 'text': text[:5000]}]},
            timeout=15,
        )
        return {'ok': r.ok, 'status': r.status_code, 'resp': r.text[:200]}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:200]}


POSTERS = {
    'telegram': post_telegram,
    'x': post_x,
    'instagram': post_instagram,
    'kakao': post_kakao,
    'line': post_line,
}


# ===== 큐 관리 =====

def load_queue() -> list:
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def save_queue(q: list):
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(q, f, ensure_ascii=False, indent=2)


def dispatch(post: dict) -> dict:
    """포스트를 지정된 플랫폼들에 동시 발송"""
    results = {}
    for target in post.get('targets', []):
        fn = POSTERS.get(target)
        if not fn:
            results[target] = {'ok': False, 'error': 'unknown target'}
            continue
        log(f"→ {target} ({post.get('service', '?')}/{post.get('id', '?')})")
        results[target] = fn(post)
    return results


def is_due(post: dict) -> bool:
    if post.get('status') != 'pending':
        return False
    sch = post.get('scheduled_at')
    if not sch:
        return True
    try:
        dt = datetime.fromisoformat(sch)
        return datetime.now() >= dt
    except Exception:
        return True


def run():
    """예약 도달 포스트 발송"""
    q = load_queue()
    due = [p for p in q if is_due(p)]
    log(f'큐 {len(q)}개, 예약도달 {len(due)}개')
    for p in due:
        results = dispatch(p)
        all_ok = all(r.get('ok') for r in results.values())
        p['status'] = 'sent' if all_ok else 'failed'
        p['results'] = results
        p['sent_at'] = datetime.now().isoformat(timespec='seconds')
        failed = [t for t, r in results.items() if not r.get('ok')]
        if failed:
            log(f'  ⚠️ {p["id"]} 실패: {failed}')
    save_queue(q)
    return due


def enqueue_interactive():
    print('=== 통합 미디어 포스트 추가 ===')
    svc = input('서비스 (korlens/tax/cheonmyeongdang/hexdrop/ebook/etc): ').strip() or 'korlens'
    title = input('제목: ').strip()
    body_ko = input('본문(한국어, 여러 줄 \\n): ').strip().replace('\\n', '\n')
    body_en = input('본문(영어, 옵션): ').strip().replace('\\n', '\n')
    link = input('링크 URL: ').strip()
    img = input('이미지 URL (옵션): ').strip()
    targets_raw = input('타겟 (기본 telegram,x) ["telegram,x,instagram,kakao,line"]: ').strip()
    targets = [t.strip() for t in (targets_raw or 'telegram,x').split(',') if t.strip()]
    when = input('예약 시각 (ISO 또는 Enter=즉시): ').strip()
    q = load_queue()
    post = {
        'id': f'P{int(time.time())}',
        'service': svc,
        'targets': targets,
        'title': title,
        'body_ko': body_ko,
        'body_en': body_en or None,
        'link': link or None,
        'image_url': img or None,
        'scheduled_at': when or None,
        'status': 'pending',
    }
    q.append(post)
    save_queue(q)
    print(f'추가됨: {post["id"]}')


def list_queue():
    q = load_queue()
    print(f'총 {len(q)}개')
    for p in q[-20:]:
        st = p.get('status', '?')
        icon = {'pending': '⏳', 'sent': '✅', 'failed': '❌'}.get(st, '?')
        print(f"  {icon} [{p.get('id')}] {p.get('service')} / {','.join(p.get('targets', []))} / {p.get('title', '')[:50]}")


if __name__ == '__main__':
    if '--enqueue' in sys.argv:
        enqueue_interactive()
    elif '--list' in sys.argv:
        list_queue()
    elif '--now' in sys.argv:
        idx = sys.argv.index('--now')
        pid = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        q = load_queue()
        p = next((x for x in q if x.get('id') == pid), None)
        if not p:
            print(f'id 없음: {pid}')
        else:
            p['results'] = dispatch(p)
            p['status'] = 'sent' if all(r.get('ok') for r in p['results'].values()) else 'failed'
            p['sent_at'] = datetime.now().isoformat(timespec='seconds')
            save_queue(q)
            print(json.dumps(p['results'], ensure_ascii=False, indent=2))
    else:
        run()
