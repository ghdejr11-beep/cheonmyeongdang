"""5/7 새벽 받은편지함 24h 스캔 + 우선순위 분류 + 답장 draft 자동 생성.

기능:
1) in:inbox newer_than:1d 메일 전부 list
2) 우선순위 분류 (RED 결제/세무/법무 / ORANGE PG·은행·투자자 / YELLOW 광고·외주제안 / GREEN SNS·뉴스레터·스팸)
3) 답장 가능한 메일 → Gmail draft 작성 (직접 발송 X)
4) 명백한 자동응답 (영수증 ack 등)은 noop — 사용자 검토 후 수동 send
5) 결과 로그 + 보고서 출력 (텔레그램은 quiet, 사용자 자는 중)

토큰: token.json (read+modify), token_send.json (send/draft create)
"""
import os
import sys
import json
import base64
import re
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Windows UTF-8 콘솔
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_READ = os.path.join(SCRIPT_DIR, 'token.json')
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')
LOG_DIR = os.path.join(SCRIPT_DIR, 'logs')
DRAFT_LOG = os.path.join(LOG_DIR, f'inbox_scan_{datetime.date.today().isoformat()}.json')
os.makedirs(LOG_DIR, exist_ok=True)

FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = '쿤스튜디오 홍덕훈'
SIGNATURE = (
    "\n\n감사합니다.\n"
    "쿤스튜디오 홍덕훈\n"
    "사업자등록번호 552-59-00848\n"
    "이메일 ghdejr11@gmail.com\n"
    "(연락처는 회신 메일로 안내드리겠습니다)\n"
)

# ─── 우선순위 분류 키워드 ───
RED_KW = [  # 결제/계약/세무/법무 — 즉시
    '입금', '결제', '환불', '정산', '세무', '세금계산서', '국세', '지방세',
    '법무', '소송', '내용증명', '통보', '청구', '미납',
    'invoice', 'payment failed', 'refund', 'legal notice', 'court', 'overdue',
    '계약', '청구서',
]
ORANGE_KW = [  # PG/은행/투자자 — 오늘
    '포트원', 'tosspayments', '갤럭시아', '카카오페이', '네이버페이',
    'paypal', 'lemonsqueezy', 'stripe',
    '은행', '거래내역', '통장사본',
    '투자', '심사', '실사', 'pitch', 'KoDATA', 'K-Startup', '경북도약',
    '관광AI', 'AI리그',
]
YELLOW_KW = [  # 광고/외주/마케팅 제안
    '제안', '협업', '광고', '마케팅', '외주', '의뢰',
    'collaboration', 'partnership', 'sponsorship', 'sponsored',
]
GREEN_FROM = [  # 자동분류 그린
    'noreply', 'no-reply', 'no_reply', 'newsletter', 'mailer',
    'campaigns', 'broadcast', 'updates@', 'notifications@',
]

# 신뢰 발신 (KORLENS, 천명당, KDP, Toss 등 — 절대 자동 답장 X)
TRUSTED_SYSTEM_FROM = [
    r'@kdp\.amazon\.com', r'@amazon\.com',
    r'@google\.com', r'@accounts\.google\.com',
    r'@toss\.im', r'@tosspayments\.com',
    r'@apple\.com', r'@vercel\.com',
    r'@github\.com',
]


def load_service(token_path, scopes_required=None):
    if not os.path.exists(token_path):
        raise FileNotFoundError(f'토큰 없음: {token_path}')
    with open(token_path, 'r', encoding='utf-8') as f:
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


def fetch_24h_inbox(svc, max_results=100):
    """최근 24시간 받은편지함 메일 리스트."""
    q = 'in:inbox newer_than:1d'
    res = svc.users().messages().list(userId='me', q=q, maxResults=max_results).execute()
    msgs = res.get('messages', [])
    out = []
    for m in msgs:
        try:
            d = svc.users().messages().get(
                userId='me', id=m['id'], format='metadata',
                metadataHeaders=['From', 'Subject', 'Date', 'Message-ID', 'References', 'To'],
            ).execute()
            headers = {h['name']: h['value'] for h in d.get('payload', {}).get('headers', [])}
            from_h = headers.get('From', '')
            mfrom = re.search(r'[\w\.\-+]+@[\w\.\-]+', from_h)
            out.append({
                'id': m['id'],
                'threadId': d['threadId'],
                'from_raw': from_h,
                'from_addr': mfrom.group(0) if mfrom else '',
                'subject': headers.get('Subject', '(제목 없음)'),
                'date': headers.get('Date', ''),
                'message_id': headers.get('Message-ID'),
                'references': headers.get('References'),
                'snippet': d.get('snippet', ''),
                'labelIds': d.get('labelIds', []),
            })
        except Exception as e:
            print(f'[WARN] fetch fail {m["id"]}: {e}')
    return out


def classify_priority(em):
    """RED/ORANGE/YELLOW/GREEN 우선순위 + 자동답장 가능 여부."""
    f = em['from_addr'].lower()
    text = (em['subject'] + ' ' + em['snippet']).lower()

    # GREEN: 발신자 패턴 (뉴스레터/자동알림)
    is_auto = any(g in f for g in GREEN_FROM)

    # 우선순위 키워드
    has_red = any(kw.lower() in text for kw in RED_KW)
    has_orange = any(kw.lower() in text for kw in ORANGE_KW)
    has_yellow = any(kw.lower() in text for kw in YELLOW_KW)

    if has_red:
        priority = 'RED'
    elif has_orange:
        priority = 'ORANGE'
    elif has_yellow:
        priority = 'YELLOW'
    elif is_auto:
        priority = 'GREEN'
    else:
        priority = 'YELLOW'  # 기본 보수적

    # 시스템/신뢰 발신 — 자동 답장 절대 X
    is_system = any(re.search(p, f, re.IGNORECASE) for p in TRUSTED_SYSTEM_FROM)

    # 답장 가능 조건: 사람 보낸 메일 + 시스템 아님 + 자동알림 아님
    repliable = (not is_system) and (not is_auto) and ('@' in em['from_addr'])

    # 비밀번호/인증코드 — 절대 답장 X
    if any(kw in text for kw in ['verification code', 'verify your', '인증번호', 'otp', 'password reset', '비밀번호 재설정']):
        repliable = False

    return priority, repliable, is_auto, is_system


def make_draft_body(em, priority):
    """우선순위에 맞춘 정중한 한국어 답장 본문."""
    subj_lower = em['subject'].lower()
    snippet = em['snippet']

    # 1차 답장 — 영업/협업 제안
    if priority == 'YELLOW' and any(kw in (em['subject'] + ' ' + snippet) for kw in ['제안', '협업', '광고', 'collaboration']):
        body = (
            "안녕하세요, 쿤스튜디오 홍덕훈입니다.\n\n"
            "보내주신 제안 잘 받았습니다.\n"
            "내용을 검토한 뒤 영업일 기준 2~3일 내로 회신드리겠습니다.\n\n"
            "구체적으로 살펴볼 수 있도록, 가능하시다면 아래 정보를 추가로 보내주시면 감사하겠습니다:\n"
            "1) 제안하시는 협업/광고의 범위 및 산출물\n"
            "2) 예산 또는 단가 (있는 경우)\n"
            "3) 일정 (착수 희망일, 마감일)\n"
            "4) 회사/담당자 정보 (사업자등록번호 또는 홈페이지)\n\n"
            "검토 후 진행 여부 및 견적 회신 드리겠습니다.\n"
            "감사합니다."
        )

    # ORANGE — PG/투자자/정부지원
    elif priority == 'ORANGE':
        body = (
            "안녕하세요, 쿤스튜디오 홍덕훈입니다.\n\n"
            "보내주신 메일 확인했습니다.\n"
            "관련 자료 및 추가 정보 정리 후 빠른 시일 내 회신드리겠습니다.\n\n"
            "혹시 추가로 필요하신 자료가 있으시면 본 메일에 회신 부탁드립니다.\n"
            "감사합니다."
        )

    # RED — 결제/세무/법무
    elif priority == 'RED':
        body = (
            "안녕하세요, 쿤스튜디오 홍덕훈입니다.\n\n"
            "보내주신 안내 확인했습니다.\n"
            "관련 사항 확인 후 빠른 시일 내로 처리하여 회신드리겠습니다.\n\n"
            "추가 확인이 필요한 사항이 있으시면 본 메일로 회신 부탁드립니다.\n"
            "감사합니다."
        )

    else:
        body = (
            "안녕하세요, 쿤스튜디오 홍덕훈입니다.\n\n"
            "메일 잘 받았습니다.\n"
            "내용 검토 후 회신드리겠습니다.\n\n"
            "감사합니다."
        )

    return body + SIGNATURE


def create_draft(send_svc, em, body_text):
    """Gmail draft 작성 (발송 X)."""
    msg = MIMEMultipart()
    msg['To'] = em['from_addr']
    msg['From'] = f'"{FROM_NAME}" <{FROM_EMAIL}>'
    subj = em['subject'] or ''
    msg['Subject'] = subj if subj.lower().startswith('re:') else f'Re: {subj}'
    if em.get('message_id'):
        msg['In-Reply-To'] = em['message_id']
        ref = (em.get('references') or '') + (' ' if em.get('references') else '') + em['message_id']
        msg['References'] = ref.strip()
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {'message': {'raw': raw, 'threadId': em['threadId']}}
    return send_svc.users().drafts().create(userId='me', body=body).execute()


def main():
    print('=== 5/7 새벽 받은편지함 24h 스캔 시작 ===')
    read_svc = load_service(TOKEN_READ)
    send_svc = load_service(TOKEN_SEND)

    emails = fetch_24h_inbox(read_svc, max_results=100)
    print(f'\n[총 {len(emails)}개 메일]\n')

    by_priority = {'RED': [], 'ORANGE': [], 'YELLOW': [], 'GREEN': []}
    drafts_created = []
    auto_send_log = []

    for em in emails:
        priority, repliable, is_auto, is_system = classify_priority(em)
        em['priority'] = priority
        em['repliable'] = repliable
        em['is_auto'] = is_auto
        em['is_system'] = is_system
        by_priority[priority].append(em)

    # 답장 draft 작성 — RED/ORANGE/YELLOW 중 repliable
    for p in ['RED', 'ORANGE', 'YELLOW']:
        for em in by_priority[p]:
            if not em['repliable']:
                continue
            try:
                body = make_draft_body(em, p)
                d = create_draft(send_svc, em, body)
                drafts_created.append({
                    'priority': p,
                    'from': em['from_addr'],
                    'subject': em['subject'],
                    'draft_id': d.get('id'),
                })
                print(f"  [DRAFT-{p}] {em['from_addr']} | {em['subject'][:50]}")
            except Exception as e:
                print(f"  [DRAFT FAIL] {em['from_addr']}: {e}")

    # 보고
    print('\n═════════════════════════════')
    print(' 우선순위 요약')
    print('═════════════════════════════')
    for p, label in [('RED', '🔴 결제/세무/법무'),
                     ('ORANGE', '🟠 PG/은행/투자자'),
                     ('YELLOW', '🟡 광고/외주 제안'),
                     ('GREEN', '🟢 SNS/뉴스레터')]:
        items = by_priority[p]
        print(f'\n{label}: {len(items)}건')
        for em in items[:10]:
            print(f"  - {em['from_addr'][:35]:35} | {em['subject'][:55]}")

    print(f'\n📝 작성된 draft: {len(drafts_created)}건')
    print(f'📤 자동 발송: {len(auto_send_log)}건 (없음 — 사용자 검토 후 수동 send)')

    # 로그 저장
    log_data = {
        'date': datetime.datetime.now().isoformat(),
        'total': len(emails),
        'by_priority': {p: len(by_priority[p]) for p in by_priority},
        'drafts_created': drafts_created,
        'all_emails': [
            {k: em[k] for k in ['priority', 'repliable', 'from_addr', 'subject', 'date']}
            for em in emails
        ],
    }
    with open(DRAFT_LOG, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    print(f'\n로그 저장: {DRAFT_LOG}')


if __name__ == '__main__':
    main()
