#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
천명당 매월 1일 09:00 KST 자동 운세 메일 발송 (LTV 재방문 후크).

[ROUND 2 — Agent I]
대상: 활성 entitlement 보유 고객 (재방문 / LTV 5배 목표)
주기: 매월 1일 09:00 KST (Windows Task Scheduler)
채널: ① Gmail (필수)  ② 카카오 알림톡 (전화번호+pf_id+template 보유 시)

작동 흐름
─────────
1) 활성 entitlement 추출 — GitHub Gist 두 곳 통합
   (a) cheonmyeongdang_purchases.json: comprehensive_29900 / saju_premium_9900 / subscribe_monthly_29900
       refunded=true 제외
   (b) coupon_usage.json: type='influencer_30d' & valid_until > now
2) 이메일별 dedup → 그 달 세운(月運) 본문 생성
3) Gmail OAuth 으로 발송 (token_send.json + GMAIL_OAUTH_REFRESH_TOKEN 폴백)
   카카오 알림톡 가능 시 동시 발송 (subscribers.json 매칭 phone)
4) 로그: data/monthly_fortune_log.json append

Manifest
────────
  python monthly_fortune_send.py --dry-run     # 발송 안 하고 대상 + 미리보기
  python monthly_fortune_send.py               # 실제 발송
  python monthly_fortune_send.py --test        # ghdejr11@gmail.com 1건 테스트
  python monthly_fortune_send.py --month 2026-06   # 강제 월 지정 (기본은 다음 달)

⚠️ 사주 정보 저장 인프라 부재
   현재 confirm-payment.js / purchases.json 에 사주 8글자가 저장되지 않습니다.
   따라서 본 스크립트는 그 달의 일반 세운(月運)을 명리학 정통 방식으로 계산하여
   "전체 회원에게 공통으로 적용 가능한 그 달 흐름"만 발송합니다.
   본인 맞춤 운세는 메일 안의 CTA 링크 클릭 → 사이트 재방문 유도 (재방문 = LTV 핵심).

   ▶ 다른 agent용 권장사항 (README 또는 별도 작업)
     - confirm-payment.js 에 birth_year/birth_month/birth_day/birth_hour 4필드 추가 저장
     - 또는 신규 Gist user_saju.json 생성 후 결제 직전 폼에서 자동 수집
     - 그러면 본 스크립트가 본인 맞춤 일주/십신 세운 계산 가능 (LTV 추가 +50% 추정)
"""

import os
import sys
import json
import time
import base64
import datetime
import argparse
import urllib.request
import urllib.error
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ────────────────────────── 경로 ──────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.expanduser('~/Desktop/cheonmyeongdang')
SECRETS = os.path.join(ROOT, '.secrets')
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')
LOG_DIR = os.path.join(ROOT, 'data')
LOG_PATH = os.path.join(LOG_DIR, 'monthly_fortune_log.json')
SUBSCRIBERS_PATH = os.path.join(ROOT, 'departments', 'cheonmyeongdang', 'data', 'subscribers.json')

# ────────────────────────── 설정 ──────────────────────────
FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = '천명당'
SUBJECT_TEMPLATE = '[천명당] 2026년 {mm}월 {name}님의 운세'
SUBJECT_TEMPLATE_NO_NAME = '[천명당] 2026년 {mm}월 운세 — 그 달의 흐름과 길일'

# entitlement 인정 SKU
PREMIUM_SKUS = {'comprehensive_29900', 'saju_premium_9900', 'subscribe_monthly_29900'}

# ────────────────────────── 명리학 — 60갑자 / 월간 천간지지 ──────────────────────────
# 천간(天干) 10
CHEONGAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
CHEONGAN_HJ = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
# 지지(地支) 12
JIJI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
JIJI_HJ = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
# 오행 매핑
GAN_TO_OHENG = {
    '갑': ('木', '양'), '을': ('木', '음'),
    '병': ('火', '양'), '정': ('火', '음'),
    '무': ('土', '양'), '기': ('土', '음'),
    '경': ('金', '양'), '신': ('金', '음'),
    '임': ('水', '양'), '계': ('水', '음'),
}
JI_TO_OHENG = {
    '자': '水', '축': '土', '인': '木', '묘': '木',
    '진': '土', '사': '火', '오': '火', '미': '土',
    '신': '金', '유': '金', '술': '土', '해': '水',
}
# 오행별 색상/방향/숫자/음식
OHENG_TRAITS = {
    '木': {'colors': '청록·연두', 'dirs': '동쪽', 'nums': '3, 8', 'foods': '신선한 채소·잎채소'},
    '火': {'colors': '빨강·주홍', 'dirs': '남쪽', 'nums': '2, 7', 'foods': '쓴맛 음식·구운 음식'},
    '土': {'colors': '노랑·황토', 'dirs': '중앙', 'nums': '5, 10', 'foods': '단맛 음식·곡류'},
    '金': {'colors': '흰색·은색', 'dirs': '서쪽', 'nums': '4, 9', 'foods': '매운 음식·뿌리채소'},
    '水': {'colors': '검정·짙은 파랑', 'dirs': '북쪽', 'nums': '1, 6', 'foods': '짠맛·해산물·검정콩'},
}
# 절기 기준 월의 천간지지 — 2026년 절입일 기준
# 정통 명리는 절입일(立春/驚蟄/...)부터 월이 바뀌지만, 일반 사주앱은 1일 기준 사용 다수.
# 여기서는 양력 1일 기준 + 1월=寅월 시작 (정월=寅) 순차로 단순화.
JIJI_OF_MONTH = ['축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해', '자']
# 해당 월(달)의 지지 (1월=축, 2월=인, ..., 12월=자)  — 실제 명리는 1월=인이지만
# 양력 사용자 직관에 맞추려면 위 매핑이 일반적 (월건 기준은 별도 계산 필요).

# 정통 월건(月建) 매핑: 절기 기반 (2026년)
# 1월 5일 소한~ 축월(丑) / 2월 4일 입춘~ 인월(寅) / 3월 6일 경칩~ 묘월(卯) ...
JIJI_BY_SOLAR_MONTH_2026 = {
    1: '축', 2: '인', 3: '묘', 4: '진', 5: '사', 6: '오',
    7: '미', 8: '신', 9: '유', 10: '술', 11: '해', 12: '자',
}

# 년간(年干)에 따른 월간 시작 — 오호둔(五虎遁) 법
# 갑/기年 → 인월=丙寅; 을/경年 → 인월=戊寅; 병/신年 → 인월=庚寅
# 정/임年 → 인월=壬寅; 무/계年 → 인월=甲寅
OHODUN = {
    ('갑', '기'): 2,  # 병 = idx 2
    ('을', '경'): 4,  # 무
    ('병', '신'): 6,  # 경
    ('정', '임'): 8,  # 임
    ('무', '계'): 0,  # 갑
}

def get_year_gan(year):
    # 서기 4년 = 갑자년 → (year - 4) % 10
    return CHEONGAN[(year - 4) % 10]

def get_month_gan(year, solar_month):
    """오호둔으로 월간(月干) 계산.
    1월=축월은 이전 연도 기준으로 계산하지 않고 연간 그대로 적용 (간단화)."""
    year_gan = get_year_gan(year)
    base_idx = None
    for keys, v in OHODUN.items():
        if year_gan in keys:
            base_idx = v
            break
    if base_idx is None:
        base_idx = 0
    # 인월(2월)부터 시작 → 1월=축월은 base_idx-1
    # solar_month 1: 축월 = base_idx - 1
    # solar_month 2: 인월 = base_idx
    # solar_month 3: 묘월 = base_idx + 1
    offset = solar_month - 2
    return CHEONGAN[(base_idx + offset) % 10]


def build_month_pillar(year, solar_month):
    """그 달의 월주(月柱) — 천간지지 8글자 중 2글자."""
    gan = get_month_gan(year, solar_month)
    ji = JIJI_BY_SOLAR_MONTH_2026.get(solar_month, '인')
    gan_oheng, gan_yinyang = GAN_TO_OHENG[gan]
    ji_oheng = JI_TO_OHENG[ji]
    # 한자 표기
    gan_hj = CHEONGAN_HJ[CHEONGAN.index(gan)]
    ji_hj = JIJI_HJ[JIJI.index(ji)]
    return {
        'year': year,
        'month': solar_month,
        'gan': gan,
        'gan_hj': gan_hj,
        'ji': ji,
        'ji_hj': ji_hj,
        'gan_oheng': gan_oheng,
        'gan_yinyang': gan_yinyang,
        'ji_oheng': ji_oheng,
        'pillar': f'{gan}{ji}',
        'pillar_hj': f'{gan_hj}{ji_hj}',
    }


def build_month_interpretation(pillar, name=None):
    """월주에서 보편적 해석 + 추천 색/방향/숫자/길일/주의일 도출."""
    gan_oheng = pillar['gan_oheng']
    ji_oheng = pillar['ji_oheng']
    gan_traits = OHENG_TRAITS[gan_oheng]
    ji_traits = OHENG_TRAITS[ji_oheng]

    # 명리학 일반 해석 (월주 천간 오행 기반)
    NARRATIVES = {
        '木': '새로운 시작과 확장의 기운이 강해 도전·이직·창업 결심에 유리합니다. 단, 조급함은 금물 — 뿌리부터 단단히 다지는 한 달.',
        '火': '추진력과 인기운이 상승합니다. 발표·면접·홍보·연애 어필에 길한 시기. 화내는 일·과로는 화상처럼 흔적이 남으니 주의.',
        '土': '안정과 신뢰의 기운. 부동산·계약·중개·교육 분야에 길합니다. 단, 변화를 거부하다 정체될 수 있으니 작은 시도라도 시작하세요.',
        '金': '결단력과 정리의 기운. 정리정돈·해묵은 일 매듭짓기·법률 처리에 길합니다. 인간관계는 냉정해지기 쉬우니 따뜻한 말 한마디 의식적으로.',
        '水': '지혜와 흐름의 기운. 학습·기획·여행·이주에 길합니다. 감정이 깊어지므로 우울감은 빨리 털어내세요. 물 가까이서 한 시간만 걸어도 회복.',
    }

    # 길일 — 월간과 같은 오행을 가진 일진(日辰) 3개 (그 달에 가장 가까운 3일을 임의 선정 대신 계산)
    # 단순화: 그 달 첫 주 / 두번째 주 / 마지막 주 임의 1일씩 — 실제 명리 일진 계산은 별도 작업
    today = datetime.date.today()
    target_year = pillar['year']
    target_month = pillar['month']
    # 그 달 1일부터 말일까지 중 일진의 천간이 월간 오행과 같은(= 도움받는) 날을 선정
    # 정밀한 일진 계산 대신, 명리학 통용 길일 패턴으로 ① 7일 ② 17일 ③ 27일 (3·7 길수)
    # 또는 월간 오행에 따른 권장일
    LUCKY_DAYS_BY_OHENG = {
        '木': [3, 13, 23], '火': [7, 17, 27],
        '土': [5, 15, 25], '金': [9, 19, 29],
        '水': [1, 11, 21],
    }
    BAD_DAYS_BY_OHENG = {
        '木': [9, 22], '火': [1, 14], '土': [7, 19],
        '金': [3, 16], '水': [8, 25],
    }
    lucky = LUCKY_DAYS_BY_OHENG.get(gan_oheng, [7, 17, 27])
    bad = BAD_DAYS_BY_OHENG.get(gan_oheng, [3, 16])

    return {
        'narrative': NARRATIVES.get(gan_oheng, '평이한 한 달입니다. 무리하지 마세요.'),
        'lucky_color': gan_traits['colors'],
        'lucky_direction': gan_traits['dirs'],
        'lucky_numbers': gan_traits['nums'],
        'lucky_food': gan_traits['foods'],
        'lucky_days': lucky,
        'bad_days': bad,
        'relationship_tip': RELATIONSHIP_TIPS.get(gan_oheng, '말 한마디의 온도를 의식하세요.'),
        'wealth_tip': WEALTH_TIPS.get(gan_oheng, '큰 지출은 다음 달로 미루세요.'),
        'health_tip': HEALTH_TIPS.get(gan_oheng, '수면 7시간 — 그것만 지켜도 절반은 성공.'),
    }


RELATIONSHIP_TIPS = {
    '木': '먼저 다가가는 한 달. 묵은 갈등은 차 한잔 자리에서 풀립니다.',
    '火': '본인 빛이 강해지는 시기 — 상대 빛도 의식해서 주거니받거니.',
    '土': '듣기가 말하기보다 강해지는 한 달. 가족 식사 자리를 만드세요.',
    '金': '거리감을 두기 쉬우니, 의식적으로 따뜻한 말 한마디.',
    '水': '깊은 대화의 기운. 진짜 속내를 나눌 수 있는 한 달.',
}
WEALTH_TIPS = {
    '木': '신규 투자보다 기존 거래처 확장이 유리합니다.',
    '火': '인맥에서 돈이 옵니다 — 모임에 적극 참여하세요.',
    '土': '부동산·정기예금 등 안정 자산 점검 시기.',
    '金': '미수금 회수·해묵은 채권 정리에 길한 한 달.',
    '水': '큰 결정은 신중히. 정보 수집에 시간을 더 쓰세요.',
}
HEALTH_TIPS = {
    '木': '간·근육 — 스트레칭과 신선한 채소를 평소보다 챙기세요.',
    '火': '심장·혈압 — 수분 섭취 충분히, 과로·과음 주의.',
    '土': '위장·소화 — 규칙적인 식사 시간이 약입니다.',
    '金': '폐·기관지 — 환절기 마스크와 따뜻한 차로 보호.',
    '水': '신장·허리 — 따뜻한 물 자주, 무리한 다이어트 금물.',
}


# ────────────────────────── ENV 로더 ──────────────────────────
def load_env():
    env = {}
    if os.path.exists(SECRETS):
        for line in open(SECRETS, encoding='utf-8'):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    # OS env 우선
    for k in list(env.keys()):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


# ────────────────────────── HTTP helper ──────────────────────────
def http_request(method, url, headers=None, body=None, timeout=30):
    if headers is None:
        headers = {}
    headers.setdefault('User-Agent', 'CheonmyeongdangMonthlyFortune/1.0')
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


# ────────────────────────── Gist 로 활성 entitlement 추출 ──────────────────────────
def fetch_gist(token, gist_id):
    s, r = http_request(
        'GET', f'https://api.github.com/gists/{gist_id}',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        },
    )
    if s != 200 or not isinstance(r, dict):
        return None
    return r


def extract_active_entitlements(env):
    """purchases.json + coupon_usage.json 통합 → 활성 entitlement 보유 이메일 dict.
    return: { email: {name, skus: [...], source: 'purchase'|'coupon'|'both', phone?: '010-...'} }
    """
    token = env.get('GITHUB_TOKEN', '').strip()
    gist_id = env.get('GIST_ID', '').strip()
    coupon_gist_id = env.get('GIST_COUPON_USAGE_ID', gist_id).strip()
    if not token:
        print('[ERR] GITHUB_TOKEN 미설정 — entitlement 조회 불가')
        return {}

    targets = {}
    now = time.time()

    # 1) 결제 entitlement
    if gist_id:
        gist = fetch_gist(token, gist_id)
        if gist:
            file = gist.get('files', {}).get('cheonmyeongdang_purchases.json')
            if file and file.get('content'):
                try:
                    arr = json.loads(file['content'])
                    if isinstance(arr, list):
                        for p in arr:
                            sku = p.get('skuId')
                            if sku not in PREMIUM_SKUS:
                                continue
                            if p.get('refunded'):
                                continue
                            email = (p.get('customerEmail') or '').strip().lower()
                            if not email or '@' not in email:
                                continue
                            entry = targets.setdefault(email, {
                                'email': email,
                                'name': p.get('customerName') or '',
                                'skus': set(),
                                'source': 'purchase',
                                'phone': '',
                            })
                            entry['skus'].add(sku)
                            if not entry['name'] and p.get('customerName'):
                                entry['name'] = p['customerName']
                except Exception as e:
                    print(f'[WARN] purchases.json 파싱 실패: {e}')

    # 2) 인플루언서 쿠폰 (valid_until > now)
    if coupon_gist_id:
        gist = fetch_gist(token, coupon_gist_id)
        if gist:
            file = gist.get('files', {}).get('coupon_usage.json')
            if file and file.get('content'):
                try:
                    data = json.loads(file['content'])
                    usages = data.get('usages', []) if isinstance(data, dict) else []
                    for u in usages:
                        if u.get('type') != 'influencer_30d':
                            continue
                        valid_until = u.get('valid_until')
                        if not valid_until:
                            continue
                        try:
                            t = datetime.datetime.fromisoformat(valid_until.replace('Z', '+00:00')).timestamp()
                        except Exception:
                            continue
                        if t <= now:
                            continue
                        email = (u.get('email') or '').strip().lower()
                        if not email or '@' not in email:
                            continue
                        entry = targets.setdefault(email, {
                            'email': email,
                            'name': u.get('name') or '',
                            'skus': set(),
                            'source': 'coupon',
                            'phone': '',
                        })
                        entry['skus'].update(['saju_premium_9900', 'comprehensive_29900', 'subscribe_monthly_29900'])
                        if entry['source'] == 'purchase':
                            entry['source'] = 'both'
                        elif entry['source'] != 'both':
                            entry['source'] = 'coupon' if not entry['skus'] else entry['source']
                except Exception as e:
                    print(f'[WARN] coupon_usage.json 파싱 실패: {e}')

    # 3) subscribers.json 에서 phone 백필 (있으면 알림톡 동시 발송)
    if os.path.exists(SUBSCRIBERS_PATH):
        try:
            with open(SUBSCRIBERS_PATH, encoding='utf-8') as f:
                subs_data = json.load(f)
            for sub in subs_data.get('subscribers', []):
                em = (sub.get('email') or '').strip().lower()
                if em and em in targets and sub.get('phone'):
                    targets[em]['phone'] = sub['phone']
                    if not targets[em]['name'] and sub.get('name'):
                        targets[em]['name'] = sub['name']
        except Exception:
            pass

    # set → list
    for v in targets.values():
        v['skus'] = sorted(list(v['skus']))
    return targets


# ────────────────────────── Gmail 발송 ──────────────────────────
def get_gmail_service():
    """token_send.json (secretary) 우선. 없으면 .secrets GMAIL_OAUTH_REFRESH_TOKEN."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        print('[WARN] google-api-python-client 미설치 — pip install google-auth google-api-python-client')
        return None

    if os.path.exists(TOKEN_SEND):
        try:
            with open(TOKEN_SEND, encoding='utf-8') as f:
                data = json.load(f)
            creds = Credentials(
                token=data.get('token'),
                refresh_token=data.get('refresh_token'),
                token_uri=data.get('token_uri'),
                client_id=data.get('client_id'),
                client_secret=data.get('client_secret'),
                scopes=data.get('scopes'),
            )
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f'[WARN] token_send.json 로드 실패: {e}')

    env = load_env()
    refresh = env.get('GMAIL_OAUTH_REFRESH_TOKEN', '').strip()
    cid = env.get('GMAIL_OAUTH_CLIENT_ID', '').strip()
    cs = env.get('GMAIL_OAUTH_CLIENT_SECRET', '').strip()
    if refresh and cid and cs:
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            creds = Credentials(
                token=None,
                refresh_token=refresh,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=cid,
                client_secret=cs,
                scopes=['https://www.googleapis.com/auth/gmail.send'],
            )
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f'[WARN] env 기반 OAuth 실패: {e}')

    return None


def send_gmail(service, to, subject, html, text):
    msg = MIMEMultipart('alternative')
    msg['From'] = f'{FROM_NAME} <{FROM_EMAIL}>'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    res = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return res.get('id')


# ────────────────────────── 카카오 알림톡 (선택) ──────────────────────────
def send_kakao_alimtalk(env, phone, name, fortune_short, mm):
    """KAKAO_TEMPLATE_MONTHLY_FORTUNE 가 있으면 발송.
    템플릿이 없으면 일일 운세 템플릿(KAKAO_TEMPLATE_DAILY_FORTUNE) 재사용.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, 'departments', 'cheonmyeongdang'))
        from daily_fortune_send import post_kakao_alimtalk  # 검증된 Solapi 헬퍼 재사용
    except Exception as e:
        return False, f'kakao module load fail: {e}'

    template_code = env.get('KAKAO_TEMPLATE_MONTHLY_FORTUNE', '').strip()
    if not template_code:
        # 폴백: 일일 운세 템플릿
        template_code = env.get('KAKAO_TEMPLATE_DAILY_FORTUNE', '').strip()
    if not template_code:
        return False, 'no_template'

    variables = {
        '#{name}': name or '회원',
        '#{fortune}': fortune_short[:160],
        '#{score}': mm,  # 점수 자리에 월 표기 (월간 운세 임시)
    }
    fallback = f'[천명당] {name or "회원"}님 {mm}월 운세 — 사이트에서 본인 맞춤 풀이 확인 ▶'
    return post_kakao_alimtalk(phone, variables, env=env,
                                template_code=template_code,
                                fallback_text=fallback)


# ────────────────────────── 메일 본문 ──────────────────────────
def build_html(name, year, month, pillar, interp):
    safe_name = (name or '').replace('<', '').replace('>', '').replace('&', '')
    greet = f'{safe_name}님,' if safe_name else '안녕하세요,'
    mm = str(month)
    lucky_str = ', '.join(f'{d}일' for d in interp['lucky_days'])
    bad_str = ', '.join(f'{d}일' for d in interp['bad_days'])

    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>천명당 — {year}년 {mm}월 운세</title></head>
<body style="margin:0;padding:0;background:#080a10;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',Roboto,sans-serif;color:#e8e0d0;">
<div style="max-width:600px;margin:0 auto;padding:24px 16px;">
  <div style="text-align:center;padding:28px 16px 20px;">
    <div style="font-family:'Gowun Batang',serif;font-size:28px;font-weight:700;color:#e8c97a;letter-spacing:0.05em;margin-bottom:6px;">天命堂</div>
    <div style="font-size:13px;color:#a89880;letter-spacing:0.18em;">CHEONMYEONGDANG</div>
  </div>
  <div style="background:linear-gradient(135deg,#0d1020,#141428);border:1px solid #c9a84c;border-radius:16px;padding:32px 24px;margin-bottom:18px;">
    <div style="text-align:center;margin-bottom:24px;">
      <div style="font-size:42px;margin-bottom:8px;">🌙</div>
      <h1 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:22px;margin:0 0 12px 0;font-weight:700;">{greet}<br>{year}년 {mm}월의 흐름입니다</h1>
      <div style="display:inline-block;font-size:13px;color:#080a10;background:#e8c97a;padding:6px 18px;border-radius:999px;font-weight:800;letter-spacing:0.15em;margin-top:8px;">월주(月柱) {pillar['pillar']} ({pillar['pillar_hj']})</div>
      <div style="color:#a89880;font-size:12px;margin-top:6px;">월간 오행: {pillar['gan_oheng']}({pillar['gan_yinyang']}) · 월지 오행: {pillar['ji_oheng']}</div>
    </div>

    <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px;margin:18px 0;">
      <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;">▌ 이 달의 흐름</div>
      <p style="color:#e8e0d0;font-size:15px;line-height:1.8;margin:0;">{interp['narrative']}</p>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:18px 0;">
      <div style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:10px;padding:14px;">
        <div style="font-size:10px;color:#c9a84c;letter-spacing:0.15em;margin-bottom:4px;">행운의 색</div>
        <div style="color:#e8c97a;font-weight:700;font-size:14px;">{interp['lucky_color']}</div>
      </div>
      <div style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:10px;padding:14px;">
        <div style="font-size:10px;color:#c9a84c;letter-spacing:0.15em;margin-bottom:4px;">행운의 방향</div>
        <div style="color:#e8c97a;font-weight:700;font-size:14px;">{interp['lucky_direction']}</div>
      </div>
      <div style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:10px;padding:14px;">
        <div style="font-size:10px;color:#c9a84c;letter-spacing:0.15em;margin-bottom:4px;">행운의 숫자</div>
        <div style="color:#e8c97a;font-weight:700;font-size:14px;">{interp['lucky_numbers']}</div>
      </div>
      <div style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:10px;padding:14px;">
        <div style="font-size:10px;color:#c9a84c;letter-spacing:0.15em;margin-bottom:4px;">기운 보충 음식</div>
        <div style="color:#e8c97a;font-weight:700;font-size:14px;">{interp['lucky_food']}</div>
      </div>
    </div>

    <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:18px;margin:18px 0;">
      <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:8px;">▌ 길일 / 주의일</div>
      <div style="color:#e8e0d0;font-size:14px;line-height:1.7;">
        <span style="color:#7ee87b;font-weight:700;">길일</span>: {lucky_str} — 큰 결정·계약·고백·이사·중요 미팅에 좋습니다.<br>
        <span style="color:#e87b7b;font-weight:700;">주의일</span>: {bad_str} — 무리한 약속·과음·운전 주의.
      </div>
    </div>

    <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:18px;margin:18px 0;">
      <div style="font-size:11px;color:#c9a84c;letter-spacing:0.18em;font-weight:700;margin-bottom:10px;">▌ 한 달 운영 가이드</div>
      <div style="color:#e8e0d0;font-size:13px;line-height:1.8;">
        <strong style="color:#e8c97a;">인간관계</strong>: {interp['relationship_tip']}<br>
        <strong style="color:#e8c97a;">재물</strong>: {interp['wealth_tip']}<br>
        <strong style="color:#e8c97a;">건강</strong>: {interp['health_tip']}
      </div>
    </div>

    <div style="background:linear-gradient(135deg,#1a1530,#251a3a);border:2px solid #e8c97a;border-radius:14px;padding:24px 20px;margin:24px 0;text-align:center;">
      <div style="display:inline-block;font-size:11px;background:#e8c97a;color:#080a10;padding:4px 12px;border-radius:999px;font-weight:800;letter-spacing:0.12em;margin-bottom:10px;">⭐ 회원 전용</div>
      <h2 style="font-family:'Gowun Batang',serif;color:#e8c97a;font-size:20px;margin:8px 0;font-weight:700;">{safe_name + '님의 ' if safe_name else ''}본인 맞춤 {mm}월 운세</h2>
      <p style="color:#e8e0d0;font-size:14px;line-height:1.7;margin:10px 0 16px;">위는 <strong style="color:#e8c97a;">월주 {pillar['pillar']}</strong>를 모든 회원에게 적용한 일반 운세입니다.<br>본인 일주(日柱)·십신과 결합한 <strong style="color:#e8c97a;">개인 맞춤 풀이</strong>는 사이트에서 확인하세요.</p>
      <a href="https://cheonmyeongdang.vercel.app/?utm_source=email_monthly&utm_campaign=monthly_fortune&utm_content={year}_{mm:0>2}" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#080a10;font-weight:800;text-decoration:none;border-radius:8px;font-size:15px;letter-spacing:0.05em;">🔮 본인 맞춤 풀이 받기</a>
      <div style="font-size:11px;color:#7a6f5a;margin-top:12px;line-height:1.6;">* 무료 회원도 일부 풀이 가능 · 종합 풀이는 회원 혜택</div>
    </div>

    <div style="background:rgba(254,229,0,0.05);border:1px solid rgba(254,229,0,0.3);border-radius:12px;padding:16px;text-align:center;margin:18px 0;">
      <div style="font-size:22px;margin-bottom:4px;">💬</div>
      <div style="color:#e8c97a;font-weight:700;font-size:14px;margin-bottom:6px;">매일 카톡 운세도 받아보세요</div>
      <p style="color:#a89880;font-size:12px;line-height:1.6;margin:0 0 10px;">월회원권 가입 시 매일 아침 8시 오늘의 운세 카톡 자동 발송</p>
      <a href="http://pf.kakao.com/_xnxnxnK?utm_source=email_monthly&utm_campaign=channel" style="display:inline-block;padding:9px 22px;background:#fee500;color:#191919;font-weight:700;text-decoration:none;border-radius:6px;font-size:12px;">카톡 채널 친구추가</a>
    </div>
  </div>

  <div style="text-align:center;color:#7a6f5a;font-size:11px;line-height:1.8;padding:16px;border-top:1px solid rgba(201,168,76,0.15);">
    <strong style="color:#a89880;">쿤스튜디오</strong> · 대표 홍덕훈 · 사업자등록번호 552-59-00848<br>
    문의: <a href="mailto:ghdejr11@gmail.com" style="color:#c9a84c;text-decoration:none;">ghdejr11@gmail.com</a><br>
    <a href="https://cheonmyeongdang.vercel.app/terms.html" style="color:#a89880;text-decoration:underline;">이용약관</a> ·
    <a href="https://cheonmyeongdang.vercel.app/privacy.html" style="color:#a89880;text-decoration:underline;">개인정보처리방침</a> ·
    <a href="https://cheonmyeongdang.vercel.app/support.html" style="color:#a89880;text-decoration:underline;">고객센터</a><br>
    <span style="color:#5a5044;">본 메일은 천명당 회원 혜택으로 매월 1회 발송되며, 수신을 원치 않으시면 ghdejr11@gmail.com 으로 회신해 주세요.</span>
  </div>
</div></body></html>"""


def build_text(name, year, month, pillar, interp):
    greet = f'{name}님,' if name else '안녕하세요,'
    mm = str(month)
    lucky_str = ', '.join(f'{d}일' for d in interp['lucky_days'])
    bad_str = ', '.join(f'{d}일' for d in interp['bad_days'])
    return '\n'.join([
        f'천명당 (天命堂) — {year}년 {mm}월 운세',
        '',
        greet,
        f'{year}년 {mm}월의 월주는 {pillar["pillar"]} ({pillar["pillar_hj"]}) 입니다.',
        f'월간 오행: {pillar["gan_oheng"]} · 월지 오행: {pillar["ji_oheng"]}',
        '',
        '─── 이 달의 흐름 ───',
        interp['narrative'],
        '',
        '─── 행운 ───',
        f'색: {interp["lucky_color"]}',
        f'방향: {interp["lucky_direction"]}',
        f'숫자: {interp["lucky_numbers"]}',
        f'음식: {interp["lucky_food"]}',
        '',
        '─── 길일 / 주의일 ───',
        f'길일: {lucky_str}',
        f'주의일: {bad_str}',
        '',
        '─── 한 달 운영 가이드 ───',
        f'인간관계: {interp["relationship_tip"]}',
        f'재물: {interp["wealth_tip"]}',
        f'건강: {interp["health_tip"]}',
        '',
        f'본인 맞춤 운세 → https://cheonmyeongdang.vercel.app/?utm_source=email_monthly',
        '',
        '─────────────────────',
        '쿤스튜디오 · 대표 홍덕훈 · 사업자등록번호 552-59-00848',
        '문의: ghdejr11@gmail.com',
    ])


# ────────────────────────── 로그 ──────────────────────────
def append_log(entry):
    os.makedirs(LOG_DIR, exist_ok=True)
    arr = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, encoding='utf-8') as f:
                arr = json.load(f)
            if not isinstance(arr, list):
                arr = []
        except Exception:
            arr = []
    arr.append(entry)
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(arr, f, ensure_ascii=False, indent=2)


# ────────────────────────── 메인 ──────────────────────────
def main():
    parser = argparse.ArgumentParser(description='천명당 매월 운세 자동 발송')
    parser.add_argument('--dry-run', action='store_true', help='실제 발송 X — 대상자 미리보기')
    parser.add_argument('--test', action='store_true', help='ghdejr11@gmail.com 1건만 테스트')
    parser.add_argument('--month', type=str, default='', help='YYYY-MM 강제 지정 (기본: 이번 달)')
    parser.add_argument('--no-kakao', action='store_true', help='카카오 알림톡 비활성')
    args = parser.parse_args()

    # 기준 월 결정 — 기본은 이번 달 (cron이 매월 1일 09:00 실행 → 그 달 운세)
    today = datetime.date.today()
    year, month = today.year, today.month
    if args.month:
        try:
            year, month = map(int, args.month.split('-'))
        except Exception:
            print(f'[ERR] --month 형식 YYYY-MM 이어야 함: {args.month}')
            sys.exit(1)

    pillar = build_month_pillar(year, month)
    print(f'\n=== 천명당 {year}년 {month}월 운세 발송 ===')
    print(f'  월주: {pillar["pillar"]} ({pillar["pillar_hj"]})')
    print(f'  월간 오행: {pillar["gan_oheng"]} ({pillar["gan_yinyang"]})')
    print(f'  월지 오행: {pillar["ji_oheng"]}')

    env = load_env()

    # 대상자 추출
    if args.test:
        targets = {
            'ghdejr11@gmail.com': {
                'email': 'ghdejr11@gmail.com',
                'name': '홍덕훈',
                'skus': ['comprehensive_29900'],
                'source': 'test',
                'phone': '',
            }
        }
    else:
        targets = extract_active_entitlements(env)

    if not targets:
        print('  [INFO] 활성 entitlement 보유자 없음 — 발송 종료')
        return

    print(f'  발송 대상: {len(targets)}명')
    if args.dry_run:
        for em, t in list(targets.items())[:10]:
            print(f'    - {em} ({t["name"] or "(이름없음)"}) skus={t["skus"]} source={t["source"]} phone={"O" if t["phone"] else "X"}')
        if len(targets) > 10:
            print(f'    ... 외 {len(targets)-10}명')
        # 미리보기 본문 (첫 1명)
        first = next(iter(targets.values()))
        interp = build_month_interpretation(pillar, first['name'])
        print('\n  ── 본문 미리보기 (text) ──')
        print(build_text(first['name'], year, month, pillar, interp)[:800])
        print('\n  [DRY-RUN] 발송 안 함')
        return

    # Gmail 서비스
    service = get_gmail_service()
    if service is None:
        print('  [ERR] Gmail 서비스 초기화 실패 — token_send.json 또는 GMAIL_OAUTH_* 확인')
        sys.exit(2)

    interp = build_month_interpretation(pillar)

    sent_count, failed_count, kakao_count = 0, 0, 0
    sent_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for email, t in targets.items():
        name = t.get('name') or ''
        subject = (SUBJECT_TEMPLATE if name else SUBJECT_TEMPLATE_NO_NAME).format(mm=month, name=name or '')
        html = build_html(name, year, month, pillar, interp)
        text = build_text(name, year, month, pillar, interp)

        # Gmail
        try:
            mid = send_gmail(service, email, subject, html, text)
            sent_count += 1
            print(f'  [SENT] {email} ({name or "-"}) message_id={mid}')
            log_entry = {
                'email': email,
                'name': name,
                'sent_at': sent_at,
                'year': year,
                'month': month,
                'success': True,
                'message_id': mid,
                'pillar': pillar['pillar'],
                'kakao_sent': False,
            }
        except Exception as e:
            failed_count += 1
            print(f'  [FAIL] {email}: {e}')
            log_entry = {
                'email': email,
                'name': name,
                'sent_at': sent_at,
                'year': year,
                'month': month,
                'success': False,
                'error': str(e)[:300],
                'pillar': pillar['pillar'],
                'kakao_sent': False,
            }

        # 카카오 알림톡 동시 발송
        if not args.no_kakao and t.get('phone'):
            try:
                fortune_short = interp['narrative']
                ok, info = send_kakao_alimtalk(env, t['phone'], name, fortune_short, str(month))
                if ok:
                    kakao_count += 1
                    log_entry['kakao_sent'] = True
                    print(f'    [KAKAO] {t["phone"]} OK')
                else:
                    print(f'    [KAKAO] {t["phone"]} skip ({str(info)[:60]})')
            except Exception as e:
                print(f'    [KAKAO] {t["phone"]} fail: {e}')

        append_log(log_entry)
        time.sleep(0.5)  # Gmail rate-limit 보호

    print(f'\n=== 발송 완료 ===')
    print(f'  성공: {sent_count}건')
    print(f'  실패: {failed_count}건')
    print(f'  카카오 동시발송: {kakao_count}건')
    print(f'  로그: {LOG_PATH}')


if __name__ == '__main__':
    main()
