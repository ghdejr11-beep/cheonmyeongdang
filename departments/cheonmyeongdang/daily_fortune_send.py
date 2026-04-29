#!/usr/bin/env python3
"""
천명당 매일 오전 8시 운세 자동 발송.

발송 우선순위:
  1) 카카오 알림톡 (Solapi 또는 NHN Bizmessage) — 정식 정보성 메시지
  2) 카카오 친구톡 (Solapi CTA, 채널 친구만) — 광고 가능
  3) 텔레그램 (.secrets TELEGRAM_BOT_TOKEN, 폴백)

가입 상태 (2026-04-27 사용자 확인):
  - 카카오 비즈니스 가입 완료 (@cheonmyeongdang, 월렛 ID 908652)
  - 알림톡 템플릿 승인은 별도 (사용자 액션 — 카카오 비즈센터에서 신청)

사용:
    from daily_fortune_send import send_daily_fortune
    ok, channel, info = send_daily_fortune(subscriber, fortune_text, score)
"""
import os
import json
import hmac
import hashlib
import datetime
import urllib.request
import urllib.error
import urllib.parse
import secrets as _secrets

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
SECRETS = os.path.join(ROOT, '.secrets')
SUBSCRIBERS_PATH = os.path.join(ROOT, 'departments', 'cheonmyeongdang', 'data', 'subscribers.json')


# ─────────────────────────── env loader ───────────────────────────
def load_env():
    env = {}
    if os.path.exists(SECRETS):
        for line in open(SECRETS, encoding='utf-8'):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


# ─────────────────────────── HTTP helper ───────────────────────────
def _http(method, url, headers=None, body=None, timeout=20):
    if headers is None:
        headers = {}
    headers.setdefault('User-Agent', 'CheonmyeongdangPoster/1.0')
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode('utf-8')
            headers.setdefault('Content-Type', 'application/json')
        elif isinstance(body, str):
            data = body.encode('utf-8')
        else:
            data = body
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            try:
                return r.status, json.loads(raw.decode('utf-8'))
            except Exception:
                return r.status, raw.decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, str(e)
    except Exception as e:
        return 0, str(e)


# ─────────────────────────── Solapi 카카오 알림톡 ───────────────────────────
def _solapi_auth_header(api_key, api_secret):
    """Solapi HMAC-SHA256 Authorization 헤더 생성.
    포맷: HMAC-SHA256 apiKey=KEY, date=ISO, salt=RANDOM, signature=HMAC
    서명 데이터 = date + salt
    """
    date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    salt = _secrets.token_hex(16)
    sig = hmac.new(api_secret.encode(), (date + salt).encode(), hashlib.sha256).hexdigest()
    return f'HMAC-SHA256 apiKey={api_key}, date={date}, salt={salt}, signature={sig}'


def post_kakao_alimtalk(phone, template_variables, env=None,
                       template_code=None, pf_id=None,
                       fallback_text=None):
    """카카오 알림톡 (Solapi) — 정보성, 템플릿 승인 필수.

    Args:
        phone: 수신자 전화번호 ('010-1234-5678' 또는 '01012345678')
        template_variables: {'#{name}': '홍길동', '#{fortune}': '...', '#{score}': '85'}
        template_code: 알림톡 템플릿 ID (env KAKAO_TEMPLATE_DAILY_FORTUNE 폴백)
        pf_id: 카카오 채널 ID (env KAKAO_PF_ID 폴백, 천명당 월렛 ID = 908652)
        fallback_text: 알림톡 차단/실패 시 SMS 대체 문구

    Returns:
        (success: bool, info: dict|str)
    """
    env = env or load_env()
    api_key = env.get('SOLAPI_API_KEY', '').strip()
    api_secret = env.get('SOLAPI_API_SECRET', '').strip()
    if not api_key or not api_secret:
        return False, 'no SOLAPI_API_KEY/API_SECRET in .secrets'

    template_code = template_code or env.get('KAKAO_TEMPLATE_DAILY_FORTUNE', '').strip()
    pf_id = pf_id or env.get('KAKAO_PF_ID', '').strip()
    if not template_code or not pf_id:
        return False, 'no KAKAO_TEMPLATE_DAILY_FORTUNE / KAKAO_PF_ID'

    # 전화번호 정규화 (하이픈 제거)
    to = phone.replace('-', '').replace(' ', '')

    # Solapi 단일 메시지 API (POST /messages/v4/send)
    body = {
        'message': {
            'to': to,
            'from': env.get('SOLAPI_SENDER_PHONE', '').strip(),  # SMS 폴백용 발신번호
            'kakaoOptions': {
                'pfId': pf_id,
                'templateId': template_code,
                'variables': template_variables,
            },
        }
    }
    if fallback_text:
        # 알림톡 실패 시 자동 SMS 대체
        body['message']['type'] = 'ATA'  # 알림톡 (SMS 폴백 자동 활성화는 채널 정책)
        body['message']['text'] = fallback_text

    auth = _solapi_auth_header(api_key, api_secret)
    s, r = _http('POST', 'https://api.solapi.com/messages/v4/send',
                 headers={'Authorization': auth}, body=body)
    return (s == 200), r


# ─────────────────────────── Solapi 친구톡 (광고 OK) ───────────────────────────
def post_kakao_friendtalk(phone, text, env=None, pf_id=None, image_url=None):
    """카카오 친구톡 — 채널 친구 대상, 광고성 OK, 템플릿 불필요.

    Args:
        phone: 수신자 전화번호
        text: 메시지 본문 (최대 1000자)
        pf_id: 카카오 채널 ID (env KAKAO_PF_ID 폴백)
        image_url: 선택 이미지 URL (CTA 친구톡)
    """
    env = env or load_env()
    api_key = env.get('SOLAPI_API_KEY', '').strip()
    api_secret = env.get('SOLAPI_API_SECRET', '').strip()
    if not api_key or not api_secret:
        return False, 'no SOLAPI_API_KEY/API_SECRET'
    pf_id = pf_id or env.get('KAKAO_PF_ID', '').strip()
    if not pf_id:
        return False, 'no KAKAO_PF_ID'

    to = phone.replace('-', '').replace(' ', '')
    msg = {
        'to': to,
        'kakaoOptions': {
            'pfId': pf_id,
            'variables': {},
        },
        'type': 'CTA' if image_url else 'CTI',
        'text': text[:1000],
    }
    if image_url:
        msg['kakaoOptions']['imageId'] = image_url  # 사전 등록 imageId

    auth = _solapi_auth_header(api_key, api_secret)
    s, r = _http('POST', 'https://api.solapi.com/messages/v4/send',
                 headers={'Authorization': auth}, body={'message': msg})
    return (s == 200), r


# ─────────────────────────── Telegram 폴백 ───────────────────────────
def post_telegram(chat_id, text, env=None):
    """텔레그램 1:1 발송 폴백 (kakao 미연동 구독자용)."""
    env = env or load_env()
    token = env.get('TELEGRAM_BOT_TOKEN', '').strip()
    if not token:
        return False, 'no TELEGRAM_BOT_TOKEN'
    if not chat_id:
        return False, 'no chat_id'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    s, r = _http('POST', url, body={
        'chat_id': str(chat_id),
        'text': text[:4096],
        'parse_mode': 'HTML',
    })
    return (s == 200 and isinstance(r, dict) and r.get('ok') is True), r


# ─────────────────────────── 통합 발송 (우선순위 적용) ───────────────────────────
def send_daily_fortune(subscriber, fortune_text, score=None, env=None):
    """구독자 1명에게 운세 발송. 우선순위: 알림톡 → 친구톡 → 텔레그램.

    Args:
        subscriber: subscribers.json 의 dict 항목
            (필수: phone OR telegram_chat_id, name, 선택: kakao_id, channel)
        fortune_text: 사주 풀이 본문 (200자 이내 권장 — 알림톡 1000byte 제한)
        score: 운세 점수 (1~100)

    Returns:
        (ok: bool, channel: str, info: dict|str)
    """
    env = env or load_env()
    name = subscriber.get('name') or '회원'
    phone = subscriber.get('phone', '').strip()
    chat_id = subscriber.get('telegram_chat_id', '').strip() if isinstance(subscriber.get('telegram_chat_id'), str) else subscriber.get('telegram_chat_id')
    pref = subscriber.get('channel', 'kakao')

    score_str = str(score) if score is not None else '-'
    fortune_short = fortune_text[:160]  # 알림톡 변수 길이 안전 마진

    # 1순위: 카카오 알림톡 (phone + 템플릿 승인 + 채널 가입자)
    if pref in ('kakao', None) and phone:
        variables = {
            '#{name}': name,
            '#{fortune}': fortune_short,
            '#{score}': score_str,
        }
        fallback_sms = f'[천명당] {name}님 오늘의 운세 ({score_str}점) — 앱에서 확인하세요.'
        ok, info = post_kakao_alimtalk(phone, variables, env=env, fallback_text=fallback_sms)
        if ok:
            return True, 'kakao_alimtalk', info

        # 2순위: 친구톡 폴백 (채널 친구인 경우만 도달)
        friendtalk_text = (
            f'🔮 {name}님, 오늘의 운세\n\n'
            f'{fortune_short}\n\n'
            f'운세 점수: {score_str}/100\n'
            f'더 자세한 풀이는 천명당 앱에서 ▶'
        )
        ok2, info2 = post_kakao_friendtalk(phone, friendtalk_text, env=env)
        if ok2:
            return True, 'kakao_friendtalk', info2

        # 3순위: 텔레그램 폴백
        if chat_id:
            ok3, info3 = post_telegram(chat_id, friendtalk_text, env=env)
            if ok3:
                return True, 'telegram', info3

        return False, 'all_failed', {'alimtalk': info, 'friendtalk': info2}

    # 사용자가 텔레그램 선호로 명시한 경우
    if pref == 'telegram' and chat_id:
        text = (
            f'🔮 <b>{name}님 오늘의 운세</b>\n\n'
            f'{fortune_short}\n\n'
            f'운세 점수: <b>{score_str}/100</b>'
        )
        ok, info = post_telegram(chat_id, text, env=env)
        return ok, 'telegram', info

    return False, 'no_channel', f'subscriber {subscriber.get("user_id")} has no phone/chat_id'


# ─────────────────────────── 일괄 발송 (매일 08:00) ───────────────────────────
def run_daily_send(fortune_generator=None, dry_run=False):
    """subscribers.json 의 활성 유료 구독자 전원에게 발송.

    Args:
        fortune_generator: callable(subscriber) -> (text, score)
            None 이면 placeholder 메시지
        dry_run: True 면 실제 발송 X, 시뮬레이션 결과만 반환
    """
    env = load_env()
    if not os.path.exists(SUBSCRIBERS_PATH):
        return {'ok': False, 'reason': f'no subscribers.json at {SUBSCRIBERS_PATH}'}

    with open(SUBSCRIBERS_PATH, encoding='utf-8') as f:
        data = json.load(f)
    subs = data.get('subscribers', [])
    today = datetime.date.today().isoformat()

    sent, skipped, failed = [], [], []
    for sub in subs:
        if not sub.get('active'):
            skipped.append((sub.get('user_id'), 'inactive'))
            continue
        paid_until = sub.get('paid_until', '')
        if paid_until and paid_until < today:
            skipped.append((sub.get('user_id'), f'expired ({paid_until})'))
            continue
        if sub.get('last_sent') == today:
            skipped.append((sub.get('user_id'), 'already_sent_today'))
            continue

        if fortune_generator:
            try:
                text, score = fortune_generator(sub)
            except Exception as e:
                failed.append((sub.get('user_id'), f'generator_error: {e}'))
                continue
        else:
            text = '오늘은 새로운 시작에 좋은 날입니다. 차분히 호흡하고 한 가지에 집중하세요.'
            score = 75

        if dry_run:
            sent.append((sub.get('user_id'), 'dry_run', sub.get('channel', 'kakao')))
            continue

        ok, channel, info = send_daily_fortune(sub, text, score, env=env)
        if ok:
            sent.append((sub.get('user_id'), channel, str(info)[:80]))
            sub['last_sent'] = today
        else:
            failed.append((sub.get('user_id'), channel, str(info)[:200]))

    if not dry_run:
        with open(SUBSCRIBERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        'ok': True,
        'date': today,
        'total': len(subs),
        'sent': len(sent),
        'skipped': len(skipped),
        'failed': len(failed),
        'sent_detail': sent,
        'skipped_detail': skipped,
        'failed_detail': failed,
    }


if __name__ == '__main__':
    import sys
    dry = '--dry-run' in sys.argv
    result = run_daily_send(dry_run=dry)
    print(json.dumps(result, ensure_ascii=False, indent=2))
