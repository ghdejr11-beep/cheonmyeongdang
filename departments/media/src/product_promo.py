#!/usr/bin/env python3
"""
쿤스튜디오 미디어부 — 전 제품 자동 홍보
- Gumroad API → 판매 상품 전체 자동 수집
- KDP (향후) → 아마존 책 추가
- Play Store (향후) → 앱 추가
- 텔레그램 / X / Threads(Postiz) 동시 발송
- 하루 2회 자동 스케줄 (도배 방지)
"""
import os, sys, json, random, datetime, argparse
import requests

try:
    import tweepy
except ImportError:
    tweepy = None

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
SECRETS = {}
for line in open(os.path.join(ROOT, '.secrets'), encoding='utf-8'):
    if '=' in line and not line.strip().startswith('#'):
        k, v = line.split('=', 1)
        SECRETS[k.strip()] = v.strip()

GUMROAD_TOKEN = SECRETS.get('GUMROAD_ACCESS_TOKEN', '')
TG_TOKEN = SECRETS.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = SECRETS.get('TELEGRAM_CHAT_ID', '')
POSTIZ_URL = SECRETS.get('POSTIZ_URL', '').rstrip('/')
POSTIZ_KEY = SECRETS.get('POSTIZ_API_KEY', '')
X_API_KEY = SECRETS.get('X_API_KEY', '')
X_API_SECRET = SECRETS.get('X_API_SECRET', '')
X_ACCESS_TOKEN = SECRETS.get('X_ACCESS_TOKEN', '')
X_ACCESS_SECRET = SECRETS.get('X_ACCESS_SECRET', '')
KAKAO_REST = SECRETS.get('KAKAO_REST_API_KEY', '')  # 추가 필요 시

STATE_FILE = os.path.join(os.path.dirname(__file__), 'product_promo_state.json')


def fetch_gumroad_products():
    """판매 중인 Gumroad 상품 전부 가져오기 (공개 + 실물 있는 것만)"""
    r = requests.get('https://api.gumroad.com/v2/products',
                     params={'access_token': GUMROAD_TOKEN}, timeout=15)
    products = r.json().get('products', [])
    active = []
    for p in products:
        if not p.get('published'):
            continue  # 비공개 제외
        active.append({
            'id': p['id'],
            'name': p['name'],
            'url': p['short_url'],
            'price': p.get('formatted_price', ''),
            'description': (p.get('description') or '')[:200],
            'sales_count': p.get('sales_count', 0),
            'thumbnail': p.get('preview_url') or p.get('thumbnail_url') or '',
        })
    return active


def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE, encoding='utf-8'))
    return {'last_promoted': {}, 'rotation_index': 0}


def save_state(state):
    json.dump(state, open(STATE_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


def pick_next_product(products, state):
    """라운드로빈 — 최근 홍보 안 한 상품 우선"""
    now = datetime.datetime.now()
    last = state.get('last_promoted', {})

    def last_hours_ago(pid):
        ts = last.get(pid)
        if not ts:
            return 999
        dt = datetime.datetime.fromisoformat(ts)
        return (now - dt).total_seconds() / 3600

    # 가장 오래 홍보 안 한 상품
    ranked = sorted(products, key=lambda p: -last_hours_ago(p['id']))
    return ranked[0] if ranked else None


def build_telegram_msg(p):
    """텔레그램용 (링크 미리보기 자동, 한국어)"""
    hook = random.choice([
        "오늘은 이것만 정리했어요",
        "지금 가장 많이 팔리는 거",
        "AI 부업 궁금하신 분들",
        "이번 주 신상",
        "이거 하나면 끝",
    ])
    return f"""💡 {hook}

『{p['name']}』
💰 {p['price']}
🔗 {p['url']}

#AI부업 #디지털상품 #쿤스튜디오"""


def build_x_msg(p):
    """X (280자 제한) — 짧게"""
    txt = f"""'{p['name']}'
{p['price']}
{p['url']}
#AI부업 #노션 #클로드"""
    if len(txt) > 270:
        # 이름 자름
        max_name = 60
        name = p['name'][:max_name] + '..'
        txt = f"'{name}'\n{p['price']}\n{p['url']}"
    return txt


def build_threads_msg(p):
    """Threads용 (500자, 해시태그 많이)"""
    return f"""📦 {p['name']}

가격: {p['price']}
주문: {p['url']}

AI 부업, 자동화, 1인 사업 궁금하신 분들 참고하세요.
질문은 편하게 DM 주세요.

#AI부업 #디지털상품 #클로드AI #ChatGPT #노션 #부업추천 #사이드잡 #쿤스튜디오"""


def send_telegram(text):
    if not TG_TOKEN or not TG_CHAT:
        return {'status': 'skip', 'reason': 'no_token'}
    r = requests.post(f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
                      json={'chat_id': TG_CHAT, 'text': text,
                            'disable_web_page_preview': False},
                      timeout=15)
    return {'status': 'ok' if r.ok else 'error', 'body': r.json()}


def send_x(text):
    """X (트위터) 발송 — 기존 tweepy 자격증명 재사용"""
    if not tweepy or not X_API_KEY:
        return {'status': 'skip', 'reason': 'no_token'}
    try:
        client = tweepy.Client(
            consumer_key=X_API_KEY, consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_SECRET,
        )
        resp = client.create_tweet(text=text)
        return {'status': 'ok', 'tweet_id': resp.data['id']}
    except Exception as e:
        return {'status': 'error', 'reason': str(e)[:150]}


def send_postiz(text, providers=None):
    """Postiz로 예약/즉시 발송 (Threads/X/Instagram 등)"""
    if not POSTIZ_URL or not POSTIZ_KEY:
        return {'status': 'skip', 'reason': 'no_postiz'}
    # Postiz API: POST /public/v1/posts
    providers = providers or ['threads']
    payload = {
        'type': 'now',
        'posts': [
            {'integration': {'id': prov}, 'value': [{'content': text}]}
            for prov in providers
        ],
    }
    try:
        r = requests.post(f'{POSTIZ_URL}/public/v1/posts',
                          headers={'Authorization': POSTIZ_KEY,
                                   'Content-Type': 'application/json'},
                          json=payload, timeout=15)
        return {'status': 'ok' if r.ok else 'error', 'code': r.status_code,
                'body': r.text[:200]}
    except Exception as e:
        return {'status': 'error', 'reason': str(e)[:100]}


def promote_once(dry_run=False):
    """한 번 실행 — 다음 타깃 상품 1개 홍보"""
    products = fetch_gumroad_products()
    if not products:
        return {'status': 'no_products'}

    state = load_state()
    target = pick_next_product(products, state)
    if not target:
        return {'status': 'no_target'}

    tg = build_telegram_msg(target)
    x = build_x_msg(target)
    threads = build_threads_msg(target)

    result = {
        'product': target['name'],
        'price': target['price'],
        'url': target['url'],
        'messages': {'tg': tg, 'x': x, 'threads': threads},
    }

    if dry_run:
        result['status'] = 'dry_run'
        return result

    # 실제 발송 — 연결된 모든 채널 동시
    result['telegram'] = send_telegram(tg)
    result['x'] = send_x(x)
    # Postiz — Threads + 연결된 모든 통합 자동 시도
    result['postiz_threads'] = send_postiz(threads, providers=['threads'])
    result['postiz_instagram'] = send_postiz(threads, providers=['instagram'])
    result['postiz_facebook'] = send_postiz(threads, providers=['facebook'])
    result['postiz_linkedin'] = send_postiz(threads, providers=['linkedin'])

    # 상태 업데이트
    state.setdefault('last_promoted', {})[target['id']] = datetime.datetime.now().isoformat()
    save_state(state)
    result['status'] = 'sent'
    return result


def promote_all_dry():
    """전체 상품 미리보기 (발송 X)"""
    products = fetch_gumroad_products()
    print(f"판매 중인 상품: {len(products)}개\n")
    for p in products:
        print(f"=== {p['name']} ===")
        print(f"가격: {p['price']} | 판매: {p['sales_count']}건")
        print(f"URL: {p['url']}")
        print(f"[텔레그램 샘플]\n{build_telegram_msg(p)}")
        print('-' * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry', action='store_true', help='발송 없이 미리보기')
    parser.add_argument('--list', action='store_true', help='상품 전체 샘플 출력')
    parser.add_argument('--now', action='store_true', help='즉시 1건 발송')
    args = parser.parse_args()

    if args.list:
        promote_all_dry()
    elif args.dry:
        print(json.dumps(promote_once(dry_run=True), ensure_ascii=False, indent=2))
    elif args.now:
        print(json.dumps(promote_once(dry_run=False), ensure_ascii=False, indent=2))
    else:
        print("usage: product_promo.py [--dry | --list | --now]")
