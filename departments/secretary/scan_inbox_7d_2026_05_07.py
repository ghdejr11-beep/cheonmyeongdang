"""5/7 — 7일 인박스 전수 검사 + 답장 상태 진단 + IGNORED draft 자동 작성.

목적: 사용자 "비서부 왜 있냐" 책임 추궁 — KoDATA 5/7 회신 놓침 사건 대응.

기능:
1) in:inbox after:2026/05/01 — 모든 메일 list (예상 200~500)
2) 각 메일 thread 분석:
   - 답장 발송 여부 (from:me 메시지 존재?)
   - draft 존재 여부 (drafts list 매칭)
3) status 분류:
   - REPLIED: 이미 답장
   - DRAFTED: draft 대기 중
   - IGNORED: 둘 다 X (놓친 메일)
   - AUTO_OK: 답장 불필요 (스팸/뉴스레터/no-reply)
4) IGNORED 중 RED/ORANGE 즉시 draft 자동 작성
5) 7일 통계 + 놓친 RED list + 결과 JSON 보고
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

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_READ = os.path.join(SCRIPT_DIR, 'token.json')
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')
LOG_DIR = os.path.join(SCRIPT_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
TODAY = datetime.date.today().isoformat()
REPORT_JSON = os.path.join(LOG_DIR, f'inbox_7d_audit_{TODAY}.json')
REPORT_MD = os.path.join(LOG_DIR, f'inbox_7d_audit_{TODAY}.md')

ME_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = '쿤스튜디오 홍덕훈'
SIGNATURE = (
    "\n\n감사합니다.\n"
    "쿤스튜디오 홍덕훈\n"
    "사업자등록번호 552-59-00848\n"
    "이메일 ghdejr11@gmail.com\n"
    "(연락처는 회신 메일로 안내드리겠습니다)\n"
)

# ─── 우선순위 키워드 ───
RED_KW = [
    '입금', '결제', '환불', '정산', '세무', '세금계산서', '국세', '지방세',
    '법무', '소송', '내용증명', '통보', '청구', '미납',
    'invoice', 'payment failed', 'refund', 'legal notice', 'court', 'overdue',
    '계약', '청구서',
]
ORANGE_KW = [
    '포트원', 'tosspayments', '갤럭시아', '카카오페이', '네이버페이',
    'paypal', 'lemonsqueezy', 'stripe',
    '은행', '거래내역', '통장사본',
    '투자', '심사', '실사', 'pitch', 'kodata', 'k-startup', '경북도약',
    '관광ai', 'ai리그', '평가데이터', '기업정보', '한국평가',
    '심사역', 'venture', 'capital',
]
YELLOW_KW = [
    '제안', '협업', '광고', '마케팅', '외주', '의뢰',
    'collaboration', 'partnership', 'sponsorship', 'sponsored',
]

NEVER_REPLY_FROM = [
    r'receipts?@', r'receipt[+]', r'invoice[+]', r'invoice[s]?@',
    r'@stripe\.com', r'@stripe-mail\.com',
    r'invoice\+statements@mail\.anthropic\.com',
    r'billing@', r'no[-_.]?reply@',
    r'noreply@', r'donotreply@', r'do_not_reply@',
    r'@mail\.instagram\.com', r'@facebookmail\.com', r'@mail\.facebook\.com',
    r'@x\.com', r'@twitter\.com',
    r'@linkedin\.com', r'@li\.linkedin\.com',
    r'@tiktok\.com',
    r'-recap@', r'-messages@', r'-notifications?@',
    r'stories-recap@', r'unread-messages@',
    r'@cx\.beehiiv\.com', r'@beehiiv\.com',
    r'@e\.heepsy\.com', r'support@heepsy\.com',
    r'@mailchimp\.com', r'@convertkit\.com',
    r'@buttondown\.', r'@substack\.com',
    r'campaigns?@', r'broadcast@', r'updates@',
    r'info@make\.com',
    r'yo@dev\.to', r'@dev\.to',
    r'@quora\.co', r'@reddit\.com', r'@redditmail\.com',
    r'codef\.io\.dev@gmail\.com',
    r'verify@', r'confirm@', r'verification@',
    r'^ghdejr11@gmail\.com$',
]

NEVER_REPLY_KEYWORDS = [
    'verification code', 'verify your', '인증번호', 'otp', 'one-time',
    'password reset', '비밀번호 재설정', 'confirm your', 'unsubscribe',
    'receipt', '영수증', 'newsletter',
    'order confirmation', 'shipping update',
    '스토리', 'unread message', '읽지 않은 메시지',
    '이용기간', '만료', 'expir', 'demo expir',
    '광고', 'sponsored', '할인', 'promotion',
    '프리미엄 구독', '구독 갱신',
]

TRUSTED_SYSTEM_FROM = [
    r'@kdp\.amazon\.com', r'@amazon\.com',
    r'@google\.com', r'@accounts\.google\.com',
    r'@apple\.com', r'@vercel\.com',
    r'@github\.com',
]


def load_service(token_path):
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


def fetch_all_inbox_7d(svc, after='2026/05/01'):
    """7일 받은편지함 전수."""
    q = f'in:inbox after:{after}'
    out = []
    page_token = None
    while True:
        params = {'userId': 'me', 'q': q, 'maxResults': 500}
        if page_token:
            params['pageToken'] = page_token
        res = svc.users().messages().list(**params).execute()
        msgs = res.get('messages', [])
        out.extend(msgs)
        page_token = res.get('nextPageToken')
        if not page_token:
            break
    return out


def fetch_metadata(svc, mid):
    d = svc.users().messages().get(
        userId='me', id=mid, format='metadata',
        metadataHeaders=['From', 'Subject', 'Date', 'Message-ID', 'References', 'To'],
    ).execute()
    headers = {h['name']: h['value'] for h in d.get('payload', {}).get('headers', [])}
    from_h = headers.get('From', '')
    mfrom = re.search(r'[\w\.\-+]+@[\w\.\-]+', from_h)
    return {
        'id': mid,
        'threadId': d['threadId'],
        'from_raw': from_h,
        'from_addr': (mfrom.group(0) if mfrom else '').lower(),
        'subject': headers.get('Subject', '(제목 없음)'),
        'date': headers.get('Date', ''),
        'message_id': headers.get('Message-ID'),
        'references': headers.get('References'),
        'snippet': d.get('snippet', ''),
        'labelIds': d.get('labelIds', []),
    }


def fetch_thread_summary(svc, tid):
    """thread의 모든 메시지 from 수집 — 'from:me' 답장 존재 여부 판단."""
    try:
        t = svc.users().threads().get(userId='me', id=tid, format='metadata',
                                       metadataHeaders=['From']).execute()
    except Exception:
        return {'has_my_reply': False, 'msg_count': 0}
    msgs = t.get('messages', [])
    has_mine = False
    for m in msgs:
        headers = {h['name']: h['value'] for h in m.get('payload', {}).get('headers', [])}
        f = headers.get('From', '').lower()
        if ME_EMAIL in f:
            has_mine = True
            break
    return {'has_my_reply': has_mine, 'msg_count': len(msgs)}


def fetch_all_drafts(svc):
    """모든 draft list — threadId set 반환."""
    drafts = []
    page_token = None
    while True:
        params = {'userId': 'me', 'maxResults': 500}
        if page_token:
            params['pageToken'] = page_token
        res = svc.users().drafts().list(**params).execute()
        ds = res.get('drafts', [])
        drafts.extend(ds)
        page_token = res.get('nextPageToken')
        if not page_token:
            break

    # threadId 매핑
    tid_set = set()
    detail_map = {}
    for d in drafts:
        try:
            full = svc.users().drafts().get(userId='me', id=d['id'], format='metadata').execute()
            tid = full.get('message', {}).get('threadId')
            if tid:
                tid_set.add(tid)
                detail_map[tid] = d['id']
        except Exception:
            pass
    return tid_set, detail_map


def classify_email(em):
    """RED/ORANGE/YELLOW/GREEN + auto_ok 여부."""
    f = em['from_addr']
    text = (em['subject'] + ' ' + em['snippet']).lower()

    is_never_reply = any(re.search(p, f, re.IGNORECASE) for p in NEVER_REPLY_FROM)
    is_system = any(re.search(p, f, re.IGNORECASE) for p in TRUSTED_SYSTEM_FROM)
    has_kw_block = any(kw.lower() in text for kw in NEVER_REPLY_KEYWORDS)

    auto_ok = is_never_reply or is_system or has_kw_block

    has_red = any(kw.lower() in text for kw in RED_KW)
    has_orange = any(kw.lower() in text for kw in ORANGE_KW)
    has_yellow = any(kw.lower() in text for kw in YELLOW_KW)

    if has_red:
        priority = 'RED'
    elif has_orange:
        priority = 'ORANGE'
    elif has_yellow:
        priority = 'YELLOW'
    else:
        priority = 'GREEN'

    return priority, auto_ok


def make_draft_body(em, priority):
    subj_text = em['subject'] + ' ' + em['snippet']

    if priority == 'YELLOW' and any(kw in subj_text for kw in ['제안', '협업', '광고', 'collaboration']):
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
    elif priority == 'ORANGE':
        body = (
            "안녕하세요, 쿤스튜디오 홍덕훈입니다.\n\n"
            "보내주신 메일 확인했습니다.\n"
            "관련 자료 및 추가 정보 정리 후 빠른 시일 내 회신드리겠습니다.\n\n"
            "혹시 추가로 필요하신 자료가 있으시면 본 메일에 회신 부탁드립니다.\n"
            "감사합니다."
        )
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


MIN_BODY_LEN = 250
PLACEHOLDER_TOKENS = ['Lorem ipsum', 'TODO', '{{', 'TBD', '[placeholder]', '[PLACEHOLDER]', 'XXXX', 'FILL_ME', 'XXX_']


def create_draft(send_svc, em, body_text):
    body_clean = (body_text or '').strip()
    if len(body_clean) < MIN_BODY_LEN:
        raise ValueError(f'BODY_TOO_SHORT: len={len(body_clean)}')
    for tok in PLACEHOLDER_TOKENS:
        if tok in body_clean:
            if tok == 'XXXX' and '010-XXXX' in body_clean:
                continue
            raise ValueError(f'PLACEHOLDER: {tok}')
    if not (em.get('subject') or '').strip():
        raise ValueError('EMPTY_SUBJECT')

    msg = MIMEMultipart()
    msg['To'] = em['from_addr']
    msg['From'] = f'"{FROM_NAME}" <{ME_EMAIL}>'
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
    print('=== 5/7 7일 인박스 전수 검사 시작 ===')
    print(f'기준: in:inbox after:2026/05/01\n')

    read_svc = load_service(TOKEN_READ)
    send_svc = load_service(TOKEN_SEND)

    print('[1/4] 인박스 메일 ID 수집...')
    msg_ids = fetch_all_inbox_7d(read_svc)
    print(f'  -> {len(msg_ids)}건 발견\n')

    print('[2/4] draft 목록 수집...')
    draft_tids, draft_map = fetch_all_drafts(send_svc)
    print(f'  -> draft {len(draft_tids)}건 (threadId 단위)\n')

    print('[3/4] 각 메일 메타데이터 + thread 답장 여부 분석...')
    rows = []
    seen_tids = set()
    for i, m in enumerate(msg_ids):
        if (i + 1) % 25 == 0:
            print(f'  ... {i+1}/{len(msg_ids)}')
        try:
            em = fetch_metadata(read_svc, m['id'])
        except Exception as e:
            print(f'  [WARN] meta fail {m["id"]}: {e}')
            continue
        tid = em['threadId']
        # thread 정보는 thread 단위로 1번만 조회
        if tid not in seen_tids:
            seen_tids.add(tid)
            ts = fetch_thread_summary(read_svc, tid)
            em['has_my_reply'] = ts['has_my_reply']
            em['thread_msg_count'] = ts['msg_count']
        else:
            em['has_my_reply'] = True  # 같은 thread 첫번째에서 이미 처리됨
            em['thread_msg_count'] = -1

        em['has_draft'] = (tid in draft_tids)
        priority, auto_ok = classify_email(em)
        em['priority'] = priority
        em['auto_ok'] = auto_ok

        if em['has_my_reply']:
            status = 'REPLIED'
        elif em['has_draft']:
            status = 'DRAFTED'
        elif auto_ok:
            status = 'AUTO_OK'
        else:
            status = 'IGNORED'
        em['status'] = status
        rows.append(em)

    print(f'\n[4/4] IGNORED RED/ORANGE → draft 자동 작성...')
    new_drafts = []
    for em in rows:
        if em['status'] != 'IGNORED':
            continue
        if em['priority'] not in ('RED', 'ORANGE'):
            continue
        # 같은 from에 이미 draft 만들었으면 skip (중복 방지)
        if any(em['from_addr'] == nd['from_addr'] for nd in new_drafts):
            continue
        try:
            body = make_draft_body(em, em['priority'])
            d = create_draft(send_svc, em, body)
            new_drafts.append({
                'from_addr': em['from_addr'],
                'subject': em['subject'],
                'priority': em['priority'],
                'draft_id': d.get('id'),
            })
            print(f"  [DRAFT-{em['priority']}] {em['from_addr']} | {em['subject'][:55]}")
        except Exception as e:
            print(f"  [FAIL] {em['from_addr']}: {e}")

    # ─── 통계 ───
    print('\n═════════════════════════════')
    print(' 7일 메일 통계')
    print('═════════════════════════════')
    by_status = {}
    by_priority = {}
    for em in rows:
        by_status[em['status']] = by_status.get(em['status'], 0) + 1
        by_priority[em['priority']] = by_priority.get(em['priority'], 0) + 1

    print(f"총 메일: {len(rows)}건")
    for s in ('REPLIED', 'DRAFTED', 'IGNORED', 'AUTO_OK'):
        print(f"  {s}: {by_status.get(s, 0)}건")
    print()
    for p in ('RED', 'ORANGE', 'YELLOW', 'GREEN'):
        print(f"  {p}: {by_priority.get(p, 0)}건")

    print('\n═════════════════════════════')
    print(' 🚨 놓친 RED 메일 (IGNORED)')
    print('═════════════════════════════')
    ignored_red = [em for em in rows if em['status'] == 'IGNORED' and em['priority'] == 'RED']
    if not ignored_red:
        print('  없음')
    else:
        for em in ignored_red[:30]:
            print(f"  - {em['date'][:25]} | {em['from_addr'][:40]} | {em['subject'][:60]}")

    print('\n═════════════════════════════')
    print(' 🚨 놓친 ORANGE 메일 (IGNORED)')
    print('═════════════════════════════')
    ignored_or = [em for em in rows if em['status'] == 'IGNORED' and em['priority'] == 'ORANGE']
    if not ignored_or:
        print('  없음')
    else:
        for em in ignored_or[:30]:
            print(f"  - {em['date'][:25]} | {em['from_addr'][:40]} | {em['subject'][:60]}")

    print(f'\n신규 draft 작성: {len(new_drafts)}건')

    # ─── KoDATA 별도 점검 ───
    print('\n═════════════════════════════')
    print(' KoDATA 회신 점검')
    print('═════════════════════════════')
    kodata = [em for em in rows if 'kodata' in em['from_addr'].lower() or '평가데이터' in em['subject'] or '기업정보' in em['subject']]
    for em in kodata:
        print(f"  - {em['date'][:25]} | {em['from_addr']} | {em['subject'][:60]} | status={em['status']}")
    if not kodata:
        print('  KoDATA 관련 메일 없음 (검색 키워드 확인 필요)')

    # ─── 저장 ───
    out = {
        'generated_at': datetime.datetime.now().isoformat(),
        'total': len(rows),
        'by_status': by_status,
        'by_priority': by_priority,
        'new_drafts_today': new_drafts,
        'ignored_red': [{'from': e['from_addr'], 'subject': e['subject'], 'date': e['date']} for e in ignored_red],
        'ignored_orange': [{'from': e['from_addr'], 'subject': e['subject'], 'date': e['date']} for e in ignored_or],
        'kodata_emails': [{'from': e['from_addr'], 'subject': e['subject'], 'date': e['date'], 'status': e['status']} for e in kodata],
        'all_rows': [
            {'date': e['date'], 'from': e['from_addr'], 'subject': e['subject'][:80],
             'priority': e['priority'], 'status': e['status'], 'tid': e['threadId']}
            for e in rows
        ],
    }
    with open(REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\nJSON 저장: {REPORT_JSON}')


if __name__ == '__main__':
    main()
