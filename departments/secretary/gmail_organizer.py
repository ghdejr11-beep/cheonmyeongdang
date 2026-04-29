#!/usr/bin/env python3
"""
비서부 — Gmail 자동 정리 시스템

기능:
1. 받은편지함 자동 분류 (5개 라벨 적용)
2. 30일+ 광고/뉴스레터 자동 archive (Inbox에서만 제거, 영구 삭제 X)
3. 정리 결과 텔레그램 보고
4. 사용자 결정 필요 항목 별도 안내 (영구 삭제는 사용자만)

⛔ 절대 금지:
- 메일 영구 삭제 (Trash 이동/Delete) — 사용자 액션만
- 신뢰 발신자(GitHub, 결제, 정부) archive 금지

✅ 허용:
- 라벨 자동 부여
- archive (Inbox 라벨 제거 — 검색으로 복구 가능)
- 텔레그램 보고

CLI:
  python gmail_organizer.py --auth          # 최초 OAuth 1회
  python gmail_organizer.py --classify      # 분류만
  python gmail_organizer.py --archive-old   # 30일+ 광고 archive
  python gmail_organizer.py --report        # 텔레그램 발송
  python gmail_organizer.py --all           # 전체 일일 작업
"""

import argparse
import datetime
import os
import re
import sys

# Windows cp949 콘솔에서도 이모지 print 가능하게
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Gmail API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

# ═══════════════════════════════════════
# 설정
# ═══════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')
LOG_DIR = os.path.join(SCRIPT_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 라벨 + Archive 위해 modify 필요
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
]

# 텔레그램 (secretary.py 와 동일 봇/채팅 사용)
TG_BOT_TOKEN = "8650272218:AAHIYmOVfqzMzr-hcOqWsfW6mftByoEd_SA"
TG_CHAT_ID = "8556067663"
TG_BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

# 자동 적용할 라벨 정의 (Gmail UI에서 보이는 이름)
LABELS = {
    'IMPORTANT_BIZ': '🔴[중요]',
    'NEED_REPLY':    '🟡[답장필요]',
    'PROMO':         '🔵[광고-뉴스레터]',
    'DEV':           '⚪[개발자]',
    'OLD_PROMO':     '⏰[오래된광고]',
}

# ─── 분류 룰 ───
# 🔴 [중요] — 키워드: 입금, 결제, 환불, 정산, 세무, 법무, 통지, 통보, 청구
IMPORTANT_KEYWORDS = [
    '입금', '결제', '환불', '정산', '세무', '법무', '통지', '통보', '청구',
    'invoice', 'payment', 'receipt', 'refund', 'tax', 'legal notice',
    'court', 'paid', 'overdue', '계산서', '세금계산서', '국세', '지방세',
]

# 🟡 [답장필요] — 키워드: 문의, 질문, 요청, ?, 부탁, 회신
REPLY_KEYWORDS = [
    '문의', '질문', '요청', '부탁', '회신', '답변',
    'question', 'inquiry', 'request', 'please reply', 'awaiting',
    'looking forward', '답장', '답신',
]

# 🔵 [광고/뉴스레터] — 발신자: noreply, no-reply, newsletter, promo, marketing, deals
PROMO_FROM_PATTERNS = [
    r'\bnoreply\b', r'\bno-reply\b', r'\bno_reply\b',
    r'newsletter', r'promo', r'marketing', r'deals', r'updates@',
    r'notifications?@', r'mailer@', r'campaigns?@', r'broadcast',
]
PROMO_SUBJECT_PATTERNS = [
    r'\[?광고\]?', r'newsletter', r'unsubscribe', r'할인', r'세일',
    r'sale', r'promotion', r'\d+%\s*off', r'special offer',
    r'이벤트', r'쿠폰', r'적립',
]

# ⚪ [개발자] — 발신자: github, vercel, supabase, anthropic, gumroad, gmail, kakao, naver
DEV_DOMAIN_PATTERNS = [
    r'@github\.com', r'@noreply\.github\.com',
    r'@vercel\.com', r'@supabase\.io', r'@supabase\.com',
    r'@anthropic\.com', r'@gumroad\.com', r'@google\.com',
    r'@googlemail\.com', r'@accounts\.google\.com',
    r'@kakao(?:corp)?\.com', r'@navercorp\.com', r'@naver\.com',
    r'@cloudflare\.com', r'@stripe\.com', r'@paypal\.com',
    r'@npmjs\.com', r'@pypi\.org', r'@discord\.com',
]

# 신뢰 발신자 — archive 금지 (중요 시스템 알림)
NEVER_ARCHIVE_FROM = [
    r'@kdp\.amazon\.com', r'kdp-support', r'kdp-automated',
    r'@amazon\.com',
    r'noreply@google\.com.*play', r'play-console',
    r'@apple\.com', r'developer@apple\.com',
    r'@toss\.im', r'@tosspayments\.com',
    r'@codef\.io', r'@hyphen\.im',
    r'@nts\.go\.kr',  # 국세청
]

# ─── 시간 기준 ───
ARCHIVE_AFTER_DAYS = 30  # 광고 메일 30일+ archive


# ═══════════════════════════════════════
# 인증
# ═══════════════════════════════════════
def authenticate(force_browser: bool = False):
    """OAuth 인증. token.json 있으면 재사용, 없으면 브라우저 OAuth."""
    creds = None
    if os.path.exists(TOKEN_FILE) and not force_browser:
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"[WARN] token.json 읽기 실패: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token and not force_browser:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[WARN] refresh 실패, 브라우저 OAuth 재시도: {e}")
                creds = None
        if not creds or not creds.valid:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json 없음: {CREDENTIALS_FILE}\n"
                    "Google Cloud Console → OAuth 클라이언트 ID(데스크톱) 생성 후 다운로드"
                )
            print("[INFO] 브라우저로 OAuth 동의 진행. '허용' 클릭...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())
        print(f"[OK] token.json 저장: {TOKEN_FILE}")

    return build('gmail', 'v1', credentials=creds)


# ═══════════════════════════════════════
# 라벨 관리
# ═══════════════════════════════════════
def ensure_labels(service):
    """5개 라벨이 없으면 생성. {라벨이름: 라벨ID} 맵 반환."""
    existing = service.users().labels().list(userId='me').execute().get('labels', [])
    name_to_id = {l['name']: l['id'] for l in existing}

    label_ids = {}
    for key, name in LABELS.items():
        if name in name_to_id:
            label_ids[key] = name_to_id[name]
        else:
            body = {
                'name': name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show',
            }
            try:
                created = service.users().labels().create(userId='me', body=body).execute()
                label_ids[key] = created['id']
                print(f"[OK] 라벨 생성: {name}")
            except HttpError as e:
                # 이미 있으면 다시 조회
                if e.resp.status == 409:
                    refreshed = service.users().labels().list(userId='me').execute().get('labels', [])
                    for l in refreshed:
                        if l['name'] == name:
                            label_ids[key] = l['id']
                            break
                else:
                    raise
    return label_ids


# ═══════════════════════════════════════
# 메일 가져오기 (헤더만, 빠르게)
# ═══════════════════════════════════════
def fetch_inbox_metadata(service, max_results=200, days=14):
    """최근 N일 받은편지함 메일을 메타데이터(헤더)만 가져옴."""
    since = datetime.datetime.now() - datetime.timedelta(days=days)
    query = f"in:inbox after:{int(since.timestamp())}"

    messages = []
    next_token = None
    while True:
        params = {
            'userId': 'me',
            'q': query,
            'maxResults': min(100, max_results - len(messages)),
        }
        if next_token:
            params['pageToken'] = next_token
        result = service.users().messages().list(**params).execute()
        messages.extend(result.get('messages', []))
        next_token = result.get('nextPageToken')
        if not next_token or len(messages) >= max_results:
            break

    emails = []
    for m in messages[:max_results]:
        try:
            detail = service.users().messages().get(
                userId='me', id=m['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date'],
            ).execute()
            emails.append(parse_metadata(detail))
        except HttpError as e:
            print(f"[WARN] 메일 가져오기 실패 {m['id']}: {e}")
    return emails


def parse_metadata(msg):
    headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
    return {
        'id': msg['id'],
        'threadId': msg['threadId'],
        'from': headers.get('From', ''),
        'subject': headers.get('Subject', '(제목 없음)'),
        'date': headers.get('Date', ''),
        'internalDate': int(msg.get('internalDate', '0')),  # ms epoch
        'labelIds': msg.get('labelIds', []),
        'snippet': msg.get('snippet', ''),
    }


def fetch_old_promo_messages(service, days=ARCHIVE_AFTER_DAYS, max_results=500):
    """광고/뉴스레터 라벨 + N일 이상 + Inbox 에 있는 메일 ID 반환."""
    promo_label_name = LABELS['PROMO']
    query = (
        f'label:"{promo_label_name}" in:inbox older_than:{days}d'
    )
    ids = []
    next_token = None
    while True:
        params = {'userId': 'me', 'q': query, 'maxResults': 100}
        if next_token:
            params['pageToken'] = next_token
        result = service.users().messages().list(**params).execute()
        for m in result.get('messages', []):
            ids.append(m['id'])
        next_token = result.get('nextPageToken')
        if not next_token or len(ids) >= max_results:
            break
    return ids[:max_results]


# ═══════════════════════════════════════
# 분류
# ═══════════════════════════════════════
def is_never_archive(from_addr: str) -> bool:
    f = from_addr.lower()
    for pat in NEVER_ARCHIVE_FROM:
        if re.search(pat, f, re.IGNORECASE):
            return True
    return False


def classify(email: dict) -> list:
    """이메일을 검사해 적용할 라벨 키 목록 반환 (다중 라벨 가능)."""
    from_addr = (email.get('from') or '').lower()
    subject = (email.get('subject') or '').lower()
    snippet = (email.get('snippet') or '').lower()
    text = subject + ' ' + snippet

    labels = []

    # 🔴 중요 (재정/법무/세무) — 최우선
    for kw in IMPORTANT_KEYWORDS:
        if kw.lower() in text:
            labels.append('IMPORTANT_BIZ')
            break

    # ⚪ 개발자/플랫폼
    for pat in DEV_DOMAIN_PATTERNS:
        if re.search(pat, from_addr, re.IGNORECASE):
            labels.append('DEV')
            break

    # 🔵 광고/뉴스레터 (발신자 OR 제목 패턴)
    is_promo = False
    for pat in PROMO_FROM_PATTERNS:
        if re.search(pat, from_addr, re.IGNORECASE):
            is_promo = True
            break
    if not is_promo:
        for pat in PROMO_SUBJECT_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                is_promo = True
                break
    if is_promo:
        labels.append('PROMO')

    # 🟡 답장 필요 (광고/개발자 알림 아닐 때만 의미 있음)
    if 'PROMO' not in labels and 'DEV' not in labels:
        for kw in REPLY_KEYWORDS:
            if kw.lower() in text:
                labels.append('NEED_REPLY')
                break
        # 제목에 ? 가 있으면 답장 필요로 간주
        if '?' in subject and 'NEED_REPLY' not in labels:
            labels.append('NEED_REPLY')

    return labels


def apply_labels(service, message_id: str, label_ids_to_add: list):
    """메일에 라벨 추가 (이미 있으면 변화 없음)."""
    if not label_ids_to_add:
        return False
    body = {'addLabelIds': label_ids_to_add, 'removeLabelIds': []}
    try:
        service.users().messages().modify(userId='me', id=message_id, body=body).execute()
        return True
    except HttpError as e:
        print(f"[WARN] 라벨 부여 실패 {message_id}: {e}")
        return False


def archive_message(service, message_id: str, old_promo_label_id: str):
    """Inbox 라벨 제거 + ⏰[오래된광고] 라벨 부여 — 영구 삭제 X."""
    body = {
        'removeLabelIds': ['INBOX'],
        'addLabelIds': [old_promo_label_id],
    }
    try:
        service.users().messages().modify(userId='me', id=message_id, body=body).execute()
        return True
    except HttpError as e:
        print(f"[WARN] archive 실패 {message_id}: {e}")
        return False


# ═══════════════════════════════════════
# 명령들
# ═══════════════════════════════════════
def cmd_classify(service, label_ids):
    """받은편지함의 최근 메일을 검사해 라벨 자동 부여."""
    print("[분류] 받은편지함 최근 14일 메일 가져오기...")
    emails = fetch_inbox_metadata(service, max_results=200, days=14)
    print(f"  대상: {len(emails)}개")

    counts = {k: 0 for k in LABELS.keys()}
    counts['UNCATEGORIZED'] = 0
    applied = 0

    for em in emails:
        # 이미 라벨이 충분히 붙어 있으면 건너뜀 (중복 modify 방지)
        existing_label_ids = set(em.get('labelIds', []))

        keys = classify(em)
        if not keys:
            counts['UNCATEGORIZED'] += 1
            continue

        # 추가해야 하는 라벨만 골라내기
        to_add = []
        for k in keys:
            lid = label_ids.get(k)
            if lid and lid not in existing_label_ids:
                to_add.append(lid)
            counts[k] += 1

        if to_add:
            if apply_labels(service, em['id'], to_add):
                applied += 1

    print(f"\n[분류 결과]")
    for k, name in LABELS.items():
        if k in counts:
            print(f"  {name}: {counts[k]}개")
    print(f"  미분류: {counts['UNCATEGORIZED']}개")
    print(f"  실제 라벨 적용된 메일: {applied}개")
    return counts


def cmd_archive_old(service, label_ids):
    """30일+ 광고/뉴스레터 라벨 메일을 Inbox 에서 제거 (archive)."""
    print(f"[archive] 광고/뉴스레터 라벨 + {ARCHIVE_AFTER_DAYS}일 이상 메일 검색...")
    candidates = fetch_old_promo_messages(service, days=ARCHIVE_AFTER_DAYS, max_results=500)
    print(f"  대상: {len(candidates)}개")

    if not candidates:
        return 0, 0

    archived = 0
    skipped = 0
    old_promo_id = label_ids['OLD_PROMO']

    for mid in candidates:
        # NEVER_ARCHIVE 발신자 보호 — 헤더 다시 확인
        try:
            detail = service.users().messages().get(
                userId='me', id=mid, format='metadata',
                metadataHeaders=['From'],
            ).execute()
            headers = {h['name']: h['value'] for h in detail.get('payload', {}).get('headers', [])}
            from_addr = headers.get('From', '')
            if is_never_archive(from_addr):
                skipped += 1
                continue
        except HttpError:
            skipped += 1
            continue

        if archive_message(service, mid, old_promo_id):
            archived += 1

    print(f"  archive 완료: {archived}개")
    print(f"  보호(skip)됨: {skipped}개")
    return archived, skipped


def build_report(counts: dict, archived: int, old_count_estimate: int) -> str:
    """텔레그램 보고 메시지."""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    msg = "📧 <b>비서부 Gmail 정리</b>\n"
    msg += f"<i>{today}</i>\n"
    msg += "─────────────────────────\n"
    msg += f"🔴 중요: {counts.get('IMPORTANT_BIZ', 0)}건 (답장 필요)\n"
    msg += f"🟡 답장필요: {counts.get('NEED_REPLY', 0)}건\n"
    msg += (
        f"🔵 광고/뉴스레터: {counts.get('PROMO', 0)}건"
        f" ({archived}건 archive)\n"
    )
    msg += f"⚪ 개발자: {counts.get('DEV', 0)}건\n"
    msg += "─────────────────────────\n"
    msg += "👀 <b>사용자 결정 필요</b>\n"
    msg += f"- 30일+ 광고 메일 {old_count_estimate}건 (영구 삭제 검토)\n"
    msg += f"- 검색: <code>label:{LABELS['OLD_PROMO']}</code>\n"
    msg += "  또는: <code>label:{0} older_than:30d</code>\n".format(LABELS['PROMO'])
    msg += "\n⛔ AI 는 영구 삭제하지 않습니다 (복구 불가).\n"
    msg += "직접 검색해서 확인 후 휴지통으로 보내세요."
    return msg


def send_telegram(text: str):
    url = f"{TG_BASE_URL}/sendMessage"
    payload = {
        'chat_id': TG_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"[WARN] 텔레그램 전송 실패: {e}")
        return {'ok': False, 'error': str(e)}


def cmd_report(service, label_ids, counts: dict, archived: int):
    """현재 상태 텔레그램 보고."""
    # 30일+ 광고 메일 추정 개수 (archive 후 남아있는 OLD_PROMO 라벨 기준)
    old_count = 0
    try:
        q = f'label:"{LABELS["OLD_PROMO"]}"'
        result = service.users().messages().list(userId='me', q=q, maxResults=500).execute()
        old_count = result.get('resultSizeEstimate', len(result.get('messages', [])))
    except HttpError:
        pass

    text = build_report(counts, archived, old_count)
    print("\n[텔레그램 발송 메시지]")
    print(text.replace('<b>', '').replace('</b>', '')
              .replace('<i>', '').replace('</i>', '')
              .replace('<code>', '').replace('</code>', ''))
    res = send_telegram(text)
    print(f"\n텔레그램 보고: {'✅' if res.get('ok') else '❌'}")
    return res


# ═══════════════════════════════════════
# 메인
# ═══════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="비서부 Gmail 자동 정리")
    parser.add_argument('--auth', action='store_true',
                        help='최초 OAuth 인증 (브라우저 동의 1회)')
    parser.add_argument('--classify', action='store_true',
                        help='받은편지함 분류 (라벨 자동 부여)')
    parser.add_argument('--archive-old', action='store_true',
                        help='30일+ 광고 archive (Inbox 에서 제거)')
    parser.add_argument('--report', action='store_true',
                        help='텔레그램 정리 보고')
    parser.add_argument('--all', action='store_true',
                        help='분류 + archive + 보고 (일일 자동 실행용)')
    parser.add_argument('--dry-run', action='store_true',
                        help='실제 변경 없이 리포트만')
    args = parser.parse_args()

    if not any([args.auth, args.classify, args.archive_old, args.report, args.all]):
        parser.print_help()
        return

    if args.auth:
        # 강제 브라우저 OAuth
        force = not os.path.exists(TOKEN_FILE)
        service = authenticate(force_browser=force)
        # 라벨도 미리 만들어 둠
        ensure_labels(service)
        print("[OK] 인증 완료. token.json 저장됨.")
        return

    service = authenticate()
    label_ids = ensure_labels(service)

    counts = {}
    archived = 0

    if args.classify or args.all:
        counts = cmd_classify(service, label_ids)

    if args.archive_old or args.all:
        archived, _ = cmd_archive_old(service, label_ids)

    if args.report or args.all:
        # counts 비어있으면 미리 한 번 분류 통계만
        if not counts:
            counts = cmd_classify(service, label_ids)
        cmd_report(service, label_ids, counts, archived)


if __name__ == '__main__':
    main()
