#!/usr/bin/env python3
"""
카카오 알림톡 발송 환경 점검 스크립트.

체크 항목:
  1. .secrets 파일 존재 + 5개 키 등록 여부
     - SOLAPI_API_KEY
     - SOLAPI_API_SECRET
     - SOLAPI_SENDER_PHONE
     - KAKAO_PF_ID
     - KAKAO_TEMPLATE_DAILY_FORTUNE
  2. Solapi 잔액 조회 (API 호출, 잔액 5,000원 미만 경고)
  3. Solapi 카카오 채널 연동 상태 (pfId 존재 확인)
  4. Solapi 등록된 템플릿 목록에 KAKAO_TEMPLATE_DAILY_FORTUNE 존재 여부
  5. subscribers.json 활성 회원 수 + 추정 일/월 비용
  6. 테스트 발송 dry-run (실제 발송 X, 변수 치환 시뮬레이션)

사용:
    python scripts/kakao_alimtalk_check.py            # 점검만
    python scripts/kakao_alimtalk_check.py --dry-run  # 점검 + 시뮬레이션
    python scripts/kakao_alimtalk_check.py --send-test 010-1234-5678  # 실제 1건 테스트
"""
import os
import sys
import json
import datetime
import urllib.request
import urllib.error

ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
SECRETS_PATH = os.path.join(ROOT, '.secrets')
SUBSCRIBERS_PATH = os.path.join(ROOT, 'departments', 'cheonmyeongdang', 'data', 'subscribers.json')

# daily_fortune_send 모듈 import 경로 추가
sys.path.insert(0, os.path.join(ROOT, 'departments', 'cheonmyeongdang'))


REQUIRED_KEYS = [
    ('SOLAPI_API_KEY',                'Solapi API Key (Step 3)'),
    ('SOLAPI_API_SECRET',             'Solapi API Secret (Step 3)'),
    ('SOLAPI_SENDER_PHONE',           'Solapi 발신번호 사전등록 (Step 2)'),
    ('KAKAO_PF_ID',                   '카카오 채널 pfId (Step 4) — 천명당 = 908652'),
    ('KAKAO_TEMPLATE_DAILY_FORTUNE',  '카카오 알림톡 템플릿 코드 (Step 8)'),
]

# 평균 단가 (원/건)
ALIMTALK_UNIT_PRICE = 12
WARN_BALANCE_KRW = 5000


def color(s, c):
    """ANSI 색 (Windows cmd 호환)."""
    codes = {'green': '32', 'yellow': '33', 'red': '31', 'cyan': '36', 'gray': '90'}
    return f'\033[{codes.get(c, "0")}m{s}\033[0m' if sys.stdout.isatty() else s


def check_secrets():
    """1. .secrets 파일 + 5개 키 점검."""
    print(color('━' * 60, 'cyan'))
    print(color('1. .secrets 파일 점검', 'cyan'))
    print(color('━' * 60, 'cyan'))

    if not os.path.exists(SECRETS_PATH):
        print(color(f'  [FAIL] .secrets 파일 없음: {SECRETS_PATH}', 'red'))
        print(color('  → docs/KAKAO_ALIMTALK_GUIDE.md 부록 참조해서 생성', 'yellow'))
        return None

    env = {}
    for line in open(SECRETS_PATH, encoding='utf-8'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

    all_ok = True
    for key, desc in REQUIRED_KEYS:
        val = env.get(key, '')
        if val:
            masked = val[:6] + '...' + val[-4:] if len(val) > 12 else val[:4] + '...'
            print(color(f'  [OK]   {key:<30} {masked}', 'green'))
        else:
            print(color(f'  [MISS] {key:<30} ({desc})', 'red'))
            all_ok = False

    if all_ok:
        print(color('  → 모든 키 등록 완료', 'green'))
    else:
        print(color('  → 누락 키 있음. docs/KAKAO_ALIMTALK_GUIDE.md Step 1~8 참조', 'yellow'))

    return env if all_ok else env  # 부분 통과도 env 반환


def _solapi_request(method, path, env, body=None):
    """Solapi 인증 헤더 포함 HTTP 요청."""
    import hmac
    import hashlib
    import secrets as _sec

    api_key = env.get('SOLAPI_API_KEY', '')
    api_secret = env.get('SOLAPI_API_SECRET', '')
    if not api_key or not api_secret:
        return 0, 'no api key'

    date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    salt = _sec.token_hex(16)
    sig = hmac.new(api_secret.encode(), (date + salt).encode(), hashlib.sha256).hexdigest()
    auth = f'HMAC-SHA256 apiKey={api_key}, date={date}, salt={salt}, signature={sig}'

    url = 'https://api.solapi.com' + path
    headers = {
        'Authorization': auth,
        'User-Agent': 'CheonmyeongdangAlimtalkCheck/1.0',
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, str(e)
    except Exception as e:
        return 0, str(e)


def check_solapi_balance(env):
    """2. Solapi 잔액 조회."""
    print()
    print(color('━' * 60, 'cyan'))
    print(color('2. Solapi 잔액 조회', 'cyan'))
    print(color('━' * 60, 'cyan'))

    if not env.get('SOLAPI_API_KEY'):
        print(color('  [SKIP] API Key 없음', 'gray'))
        return None

    s, r = _solapi_request('GET', '/cash/v1/balance', env)
    if s != 200 or not isinstance(r, dict):
        print(color(f'  [FAIL] 잔액 조회 실패 (HTTP {s}): {str(r)[:200]}', 'red'))
        return None

    balance = r.get('balance', 0)
    point = r.get('point', 0)
    total = balance + point

    if total < WARN_BALANCE_KRW:
        print(color(f'  [WARN] 잔액 부족: {total:,}원 (현금 {balance:,}원 + 포인트 {point:,}원)', 'yellow'))
        print(color(f'  → 5,000원 미만. https://console.solapi.com 에서 충전 필요', 'yellow'))
    else:
        print(color(f'  [OK] 잔액: {total:,}원 (현금 {balance:,}원 + 포인트 {point:,}원)', 'green'))

    # 알림톡 발송 가능 건수 추정
    sendable = total // ALIMTALK_UNIT_PRICE
    print(color(f'  → 알림톡 약 {sendable:,}건 발송 가능 (단가 {ALIMTALK_UNIT_PRICE}원 가정)', 'gray'))
    return total


def check_kakao_channel(env):
    """3. Solapi 카카오 채널 연동 상태."""
    print()
    print(color('━' * 60, 'cyan'))
    print(color('3. Solapi 카카오 채널 연동', 'cyan'))
    print(color('━' * 60, 'cyan'))

    pf_id = env.get('KAKAO_PF_ID', '')
    if not pf_id:
        print(color('  [SKIP] KAKAO_PF_ID 없음', 'gray'))
        return False

    s, r = _solapi_request('GET', f'/kakao/v2/channels/{pf_id}', env)
    if s == 200 and isinstance(r, dict):
        name = r.get('searchId') or r.get('name') or 'unknown'
        status = r.get('status', 'unknown')
        if status.lower() in ('active', 'enabled', 'normal'):
            print(color(f'  [OK] 채널 연동됨: {name} (pfId={pf_id}, status={status})', 'green'))
            return True
        else:
            print(color(f'  [WARN] 채널 status={status} — Solapi 콘솔 확인 필요', 'yellow'))
            return False

    print(color(f'  [FAIL] 채널 연동 미확인 (HTTP {s}): {str(r)[:200]}', 'red'))
    print(color('  → docs/KAKAO_ALIMTALK_GUIDE.md Step 4 재실행', 'yellow'))
    return False


def check_template(env):
    """4. 등록 템플릿 확인."""
    print()
    print(color('━' * 60, 'cyan'))
    print(color('4. 알림톡 템플릿 등록 확인', 'cyan'))
    print(color('━' * 60, 'cyan'))

    pf_id = env.get('KAKAO_PF_ID', '')
    template_code = env.get('KAKAO_TEMPLATE_DAILY_FORTUNE', '')
    if not pf_id or not template_code:
        print(color('  [SKIP] KAKAO_PF_ID 또는 KAKAO_TEMPLATE_DAILY_FORTUNE 없음', 'gray'))
        return False

    s, r = _solapi_request('GET', f'/kakao/v2/templates/{template_code}', env)
    if s == 200 and isinstance(r, dict):
        name = r.get('name', '?')
        status = r.get('status', '?')
        inspection = r.get('inspectionStatus', '?')
        if inspection.upper() == 'APPROVED':
            print(color(f'  [OK] 템플릿 승인됨: {name} (code={template_code})', 'green'))
            print(color(f'       status={status}, inspection={inspection}', 'gray'))
            return True
        else:
            print(color(f'  [WAIT] 템플릿 검수 중: {name} (inspection={inspection})', 'yellow'))
            print(color('  → 1~2영업일 소요. 거절 시 docs/KAKAO_ALIMTALK_GUIDE.md 3번 거절사유 참조', 'yellow'))
            return False

    print(color(f'  [FAIL] 템플릿 조회 실패 (HTTP {s}): {str(r)[:200]}', 'red'))
    return False


def estimate_cost():
    """5. subscribers.json 활성 회원 + 비용 추정."""
    print()
    print(color('━' * 60, 'cyan'))
    print(color('5. 회원 수 / 발송 비용 추정', 'cyan'))
    print(color('━' * 60, 'cyan'))

    if not os.path.exists(SUBSCRIBERS_PATH):
        print(color(f'  [INFO] subscribers.json 없음 (아직 회원 0명)', 'gray'))
        return 0

    try:
        with open(SUBSCRIBERS_PATH, encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(color(f'  [FAIL] subscribers.json 파싱 오류: {e}', 'red'))
        return 0

    subs = data.get('subscribers', [])
    today = datetime.date.today().isoformat()
    active = [s for s in subs
              if s.get('active')
              and (not s.get('paid_until') or s.get('paid_until') >= today)]

    n = len(active)
    daily = n * ALIMTALK_UNIT_PRICE
    monthly = daily * 30

    print(color(f'  활성 유료 회원: {n}명', 'green'))
    print(color(f'  일 발송 비용: {daily:,}원 ({n}명 × {ALIMTALK_UNIT_PRICE}원)', 'gray'))
    print(color(f'  월 발송 비용: {monthly:,}원 ({n}명 × 30일 × {ALIMTALK_UNIT_PRICE}원)', 'gray'))
    return n


def dry_run_simulation(env, n_active):
    """6. 발송 시뮬레이션 (실제 발송 X)."""
    print()
    print(color('━' * 60, 'cyan'))
    print(color('6. 발송 시뮬레이션 (dry-run)', 'cyan'))
    print(color('━' * 60, 'cyan'))

    sample_vars = {
        '#{name}':    '홍길동',
        '#{fortune}': '오늘은 새로운 시작에 좋은 날입니다. 차분히 호흡하고 한 가지에 집중하세요.',
        '#{score}':   '85',
    }

    template_body = (
        '[천명당] 오늘의 운세 도착\n\n'
        '#{name}님, 좋은 아침입니다.\n'
        '오늘의 사주 풀이를 전해드립니다.\n\n'
        '#{fortune}\n\n'
        '오늘의 운세 점수: #{score}/100점\n\n'
        '자세한 풀이와 부적은 앱에서 확인하세요.'
    )
    rendered = template_body
    for k, v in sample_vars.items():
        rendered = rendered.replace(k, v)

    print(color('  변수 치환 결과:', 'gray'))
    for line in rendered.split('\n'):
        print(color(f'  │ {line}', 'gray'))

    byte_len = len(rendered.encode('utf-8'))
    if byte_len > 1000:
        print(color(f'  [WARN] 본문 {byte_len}byte — 1000byte 초과! fortune 변수 짧게', 'red'))
    else:
        print(color(f'  [OK] 본문 {byte_len}byte (1000byte 한도 내)', 'green'))

    print(color(f'  활성 회원 {n_active}명 → 예상 비용 {n_active * ALIMTALK_UNIT_PRICE:,}원', 'gray'))
    print(color('  실제 발송: python departments/cheonmyeongdang/daily_fortune_send.py', 'cyan'))


def send_test_one(env, phone):
    """실제 1건 테스트 발송."""
    print()
    print(color('━' * 60, 'cyan'))
    print(color(f'7. 실제 테스트 발송 → {phone}', 'cyan'))
    print(color('━' * 60, 'cyan'))

    try:
        from daily_fortune_send import post_kakao_alimtalk
    except ImportError as e:
        print(color(f'  [FAIL] daily_fortune_send 모듈 import 실패: {e}', 'red'))
        return

    variables = {
        '#{name}':    '테스트',
        '#{fortune}': '점검 스크립트에서 발송된 테스트 메시지입니다. 정상 수신되면 자동 발송 준비 완료입니다.',
        '#{score}':   '100',
    }
    fallback = '[천명당] 알림톡 테스트 발송 (정상 수신되면 자동 발송 준비 완료)'

    ok, info = post_kakao_alimtalk(phone, variables, env=env, fallback_text=fallback)
    if ok:
        print(color(f'  [OK] 발송 성공', 'green'))
        print(color(f'       응답: {str(info)[:300]}', 'gray'))
    else:
        print(color(f'  [FAIL] 발송 실패', 'red'))
        print(color(f'        응답: {str(info)[:500]}', 'yellow'))


def main():
    args = sys.argv[1:]
    do_dry = '--dry-run' in args
    test_phone = None
    if '--send-test' in args:
        idx = args.index('--send-test')
        if idx + 1 < len(args):
            test_phone = args[idx + 1]

    print()
    print(color('╔══════════════════════════════════════════════════════════╗', 'cyan'))
    print(color('║  천명당 카카오 알림톡 발송 환경 점검                     ║', 'cyan'))
    print(color('║  ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').ljust(54) + '║', 'cyan'))
    print(color('╚══════════════════════════════════════════════════════════╝', 'cyan'))

    env = check_secrets()
    if env is None:
        sys.exit(1)

    check_solapi_balance(env)
    check_kakao_channel(env)
    check_template(env)
    n = estimate_cost()

    if do_dry:
        dry_run_simulation(env, n)

    if test_phone:
        send_test_one(env, test_phone)

    print()
    print(color('점검 완료. 누락된 항목은 docs/KAKAO_ALIMTALK_GUIDE.md 참조.', 'cyan'))


if __name__ == '__main__':
    main()
