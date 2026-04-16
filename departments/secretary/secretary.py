#!/usr/bin/env python3
"""
천명당 비서부 — Gmail 자동 분류 + 요약 시스템

기능:
1. Gmail에서 최근 메일 수집
2. 발신자/제목 기반 분류 (파트너사/광고/개인/KDP거절 등)
3. 텔레그램으로 요약 보고
4. KDP 거절 메일은 편집부로 자동 전달

안전 규칙:
- 삭제/답장은 승인 후에만 실행 (자동 금지)
- 피싱 의심 메일은 별도 표시
"""

import os
import sys
import base64
import re
import json
import datetime
from email import message_from_bytes

# Gmail API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

# ─── 설정 ───
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')

# Gmail API 권한
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',  # 라벨링, 읽음표시
]

# 텔레그램
TG_BOT_TOKEN = "8650272218:AAHIYmOVfqzMzr-hcOqWsfW6mftByoEd_SA"
TG_CHAT_ID = "8556067663"
TG_BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

# 편집부 저장 위치
EDIT_QUEUE_FILE = os.path.join(SCRIPT_DIR, 'edit_queue.json')


# ─── 영→한 번역 사전 (텔레그램 보고용) ───
def translate_subject(subject):
    """영문 제목을 한글로 번역"""
    s = subject
    translations = [
        (r'Attention needed:\s*Please review your title,?\s*', '[수정필요] '),
        (r'\[Action Required\]\s*', '[조치필요] '),
        (r'Your paperback book has been published!?', '페이퍼백 책 출간 완료!'),
        (r'Your identity was successfully verified', '신원인증 완료'),
        (r'Verify your identity on Kindle Direct Publishing by', 'KDP 신원인증 마감:'),
        (r'Your Kindle eBook has been published!?', 'Kindle eBook 출간 완료!'),
        (r'Update on your title', '도서 업데이트 안내'),
        (r'Sales Report', '판매 리포트'),
        (r'Monthly Royalty Report', '월간 로열티 리포트'),
        (r'New pull request', '새 풀 리퀘스트'),
        (r'New comment on', '새 댓글:'),
        (r'New issue', '새 이슈'),
        (r'Deploy ready', '배포 준비됨'),
        (r'Deployment successful', '배포 성공'),
        (r'Build failed', '빌드 실패'),
        (r'Invoice', '인보이스'),
        (r'Receipt', '영수증'),
        (r'Your order has been', '주문 상태:'),
        (r'Welcome to', '환영합니다:'),
    ]
    for pat, rep in translations:
        s = re.sub(pat, rep, s, flags=re.IGNORECASE)
    return s


def translate_category_context(text):
    """카테고리 설명 번역"""
    return text  # 이미 한글


# ─── 발신자 분류 룰 ───
PARTNER_PATTERNS = {
    'KDP (Amazon)': [
        r'kdp-support@amazon\.',
        r'kdp-automated@amazon\.',
        r'kindle-direct-publishing',
        r'no-reply@kindle\.',
        r'@amazon\.com',
    ],
    'Google Play': [
        r'googleplay-.*@google\.com',
        r'play-console-noreply@google\.com',
        r'noreply@google\.com.*play',
    ],
    'Apple': [
        r'no_reply@email\.apple\.com',
        r'developer@apple\.com',
    ],
    'Meta Developer': [
        r'noreply@facebookmail\.com',
        r'notification\+.*@facebookmail\.com',
        r'developers@facebook\.com',
    ],
    '카카오': [
        r'@kakaocorp\.com',
        r'noreply@kakao',
        r'kakaobusiness',
    ],
    '토스': [
        r'@toss\.im',
        r'noreply@toss',
    ],
    '네이버': [
        r'@navercorp\.com',
        r'noreply@naver\.com',
    ],
    'CODEF': [
        r'@codef\.io',
    ],
    '크티': [
        r'@ctee\.kr',
    ],
    'Vercel': [
        r'@vercel\.com',
        r'noreply@vercel',
    ],
    'X / Twitter': [
        r'@x\.com',
        r'@twitter\.com',
    ],
    'GitHub': [
        r'@github\.com',
    ],
}

# KDP 거절/수정 요청 키워드 (제목 기준이 더 정확)
KDP_REJECTION_KEYWORDS = [
    'attention needed', 'please review your title', 'action required',
    'not approved', 'rejected', 'needs changes', 'content issue',
    'metadata issue', 'cover issue', 'unable to publish',
    '승인되지', '거절', '수정 필요', '불가', '반려',
    'manuscript', 'please revise', 'changes required',
]

# 스팸/광고 패턴
SPAM_PATTERNS = [
    r'unsubscribe', r'광고', r'이벤트', r'할인', r'sale',
    r'promotion', r'newsletter', r'\[광고\]',
]

# ═══════════════════════════════════════
# 바이러스/피싱 검사 패턴
# ═══════════════════════════════════════

# 피싱/악성 URL 패턴 (위험 도메인, 단축 URL 변형 등)
PHISHING_URL_PATTERNS = [
    # 단축 URL (원래 URL을 숨기므로 위험)
    r'bit\.ly/', r'tinyurl\.com/', r'goo\.gl/', r't\.co/', r'ow\.ly/',
    r'is\.gd/', r'buff\.ly/', r'rebrand\.ly/',
    # 의심스러운 TLD (최근 피싱에 자주 쓰임)
    r'\.tk/', r'\.ml/', r'\.ga/', r'\.cf/', r'\.gq/',
    # IP 주소 직접 사용 (정상 사이트는 도메인 사용)
    r'https?://\d+\.\d+\.\d+\.\d+',
    # 유명 브랜드 사칭 (오타 도메인)
    r'amaz[o0]n[-.]', r'payp[a4]l[-.]', r'g[o0]{2}gle[-.]',
    r'mlcrosoft', r'appIe\.', r'netfllx',
]

# 위험 파일 확장자 (첨부파일)
DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jar', '.msi',
    '.com', '.pif', '.hta', '.ps1', '.wsf', '.lnk', '.dll',
    '.zip.exe', '.pdf.exe', '.docx.exe',  # 이중 확장자
]

# 피싱 키워드 (사회공학적 공격 패턴)
PHISHING_KEYWORDS = [
    # 긴급성 조장
    '계정이 잠겼', '계정 정지', '즉시 확인', '긴급', 'verify immediately',
    'account suspended', 'account locked', 'urgent action required',
    # 금전 유혹
    '당첨', '상금', 'you have won', 'claim your prize', 'lottery',
    '환급금', '세금 환급', 'tax refund',
    # 로그인 정보 요구
    '비밀번호 확인', 'verify your password', 'confirm credentials',
    '본인 인증', '재로그인',
    # 배송/택배 사칭
    '배송 실패', 'delivery failed', 'package held', '송장번호 미확인',
]

# 정상으로 간주할 발신자 (화이트리스트)
TRUSTED_SENDERS = [
    r'@amazon\.com$', r'@kindle\.com$',
    r'@google\.com$', r'@googlemail\.com$',
    r'@apple\.com$', r'@email\.apple\.com$',
    r'@facebook\.com$', r'@facebookmail\.com$',
    r'@kakaocorp\.com$', r'@kakao\.com$',
    r'@naver\.com$', r'@navercorp\.com$',
    r'@toss\.im$',
    r'@github\.com$', r'@github\.io$',
    r'@codef\.io$',
    r'@vercel\.com$',
    r'@ctee\.kr$',
    r'@hyphen\.im$',
]


def scan_virus_and_phishing(email):
    """
    메일을 읽기 전 바이러스/피싱 검사
    반환: {'safe': bool, 'threats': [list of threat descriptions], 'risk_level': 'safe'|'low'|'medium'|'high'}
    """
    threats = []
    risk_score = 0

    from_addr = email.get('from', '').lower()
    subject = email.get('subject', '').lower()
    body = email.get('body', '').lower()
    snippet = email.get('snippet', '').lower()

    # 1. 신뢰 발신자 화이트리스트 체크
    is_trusted = False
    for pattern in TRUSTED_SENDERS:
        if re.search(pattern, from_addr):
            is_trusted = True
            break

    # 2. 피싱 URL 검사 (본문 + 제목)
    combined_text = subject + ' ' + body + ' ' + snippet
    for pattern in PHISHING_URL_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            threats.append(f'의심스러운 URL 패턴 감지: {pattern}')
            risk_score += 30
            break  # 하나만 기록 (중복 방지)

    # 3. 위험 파일 확장자 검사
    for ext in DANGEROUS_EXTENSIONS:
        # 본문에 파일명 언급 or 첨부 표시
        if ext in combined_text:
            threats.append(f'위험 파일 확장자 감지: {ext}')
            risk_score += 40

    # 4. 피싱 키워드 검사
    phishing_kw_count = 0
    for kw in PHISHING_KEYWORDS:
        if kw.lower() in combined_text:
            phishing_kw_count += 1
    if phishing_kw_count >= 2:
        threats.append(f'피싱 의심 키워드 {phishing_kw_count}개 감지')
        risk_score += 25

    # 5. 발신자 스푸핑 검사 (표시 이름과 실제 주소 불일치)
    display_match = re.search(r'^([^<]+)<([^>]+)>', email.get('from', ''))
    if display_match:
        display_name = display_match.group(1).strip().lower()
        actual_email = display_match.group(2).strip().lower()
        # 유명 브랜드가 표시 이름에 있는데 실제 도메인이 다른 경우
        brand_mismatch = False
        for brand in ['amazon', 'google', 'apple', 'kakao', 'naver', 'toss', 'samsung', 'kb', 'hyundai']:
            if brand in display_name:
                brand_domain_ok = False
                for trusted in TRUSTED_SENDERS:
                    if brand in trusted.lower() and re.search(trusted, actual_email):
                        brand_domain_ok = True
                        break
                if not brand_domain_ok:
                    brand_mismatch = True
                    threats.append(f'발신자 스푸핑 의심: 표시명에 "{brand}" 있으나 실제 주소 불일치')
                    risk_score += 50
                    break

    # 6. 신뢰 발신자면 위험도 감소
    if is_trusted:
        risk_score = max(0, risk_score - 20)

    # 위험도 판정
    if risk_score >= 60:
        risk_level = 'high'
    elif risk_score >= 30:
        risk_level = 'medium'
    elif risk_score >= 10:
        risk_level = 'low'
    else:
        risk_level = 'safe'

    return {
        'safe': risk_score < 30,
        'threats': threats,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'is_trusted_sender': is_trusted,
    }


# ═══════════════════════════════════════
# Gmail 인증
# ═══════════════════════════════════════
def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# ═══════════════════════════════════════
# 메일 가져오기 & 파싱
# ═══════════════════════════════════════
def fetch_recent_emails(service, hours=24, max_results=50):
    """최근 N시간 내 받은 메일 목록"""
    since = datetime.datetime.now() - datetime.timedelta(hours=hours)
    query = f"after:{int(since.timestamp())} -in:sent -in:draft"

    result = service.users().messages().list(
        userId='me', q=query, maxResults=max_results
    ).execute()

    messages = result.get('messages', [])
    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()
        emails.append(parse_email(detail))

    return emails


def parse_email(msg):
    """Gmail 메시지 파싱"""
    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
    body = extract_body(msg['payload'])
    return {
        'id': msg['id'],
        'threadId': msg['threadId'],
        'from': headers.get('From', ''),
        'to': headers.get('To', ''),
        'subject': headers.get('Subject', '(제목 없음)'),
        'date': headers.get('Date', ''),
        'body': body[:3000],  # 최대 3000자
        'labels': msg.get('labelIds', []),
        'snippet': msg.get('snippet', ''),
    }


def extract_body(payload):
    """본문 추출 (text/plain 우선, 없으면 HTML 태그 제거)"""
    # 1순위: text/plain
    text_body = _find_body(payload, 'text/plain')
    if text_body:
        return text_body
    # 2순위: text/html → 태그 제거
    html_body = _find_body(payload, 'text/html')
    if html_body:
        # 간단한 HTML 태그 제거
        cleaned = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<script[^>]*>.*?</script>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        cleaned = re.sub(r'&nbsp;', ' ', cleaned)
        cleaned = re.sub(r'&amp;', '&', cleaned)
        cleaned = re.sub(r'&lt;', '<', cleaned)
        cleaned = re.sub(r'&gt;', '>', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    return ''


def _find_body(payload, mime_type):
    """재귀적으로 특정 mime type 본문 찾기"""
    if payload.get('mimeType') == mime_type:
        data = payload.get('body', {}).get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
    if 'parts' in payload:
        for part in payload['parts']:
            result = _find_body(part, mime_type)
            if result:
                return result
    return ''


# ═══════════════════════════════════════
# 분류
# ═══════════════════════════════════════
def classify_email(email):
    """메일 분류 (바이러스/피싱 검사 먼저 수행)"""
    # 0. 먼저 바이러스/피싱 검사 수행 (메일 내용 상세 분석 전)
    security = scan_virus_and_phishing(email)
    email['_security'] = security  # 결과를 email 객체에 저장

    from_addr = email['from'].lower()
    subject = email['subject'].lower()
    body = email['body'].lower()

    # 1. 파트너사 확인
    partner = None
    for name, patterns in PARTNER_PATTERNS.items():
        for p in patterns:
            if re.search(p, from_addr):
                partner = name
                break
        if partner:
            break

    # 2. KDP 거절 여부 (제목 우선 체크)
    is_kdp_rejection = False
    if partner == 'KDP (Amazon)':
        # 성공 메일은 제외
        if 'published' in subject or 'verified' in subject:
            is_kdp_rejection = False
        else:
            combined = subject + ' ' + body
            for kw in KDP_REJECTION_KEYWORDS:
                if kw.lower() in combined:
                    is_kdp_rejection = True
                    break

    # 3. 스팸/광고
    is_spam = False
    for p in SPAM_PATTERNS:
        if re.search(p, subject, re.IGNORECASE):
            is_spam = True
            break

    # 4. 카테고리 결정 (보안 위협 최우선)
    if security['risk_level'] == 'high':
        category = '🛑 피싱/악성 의심 (높음)'
        priority = 11  # 최우선 (사용자 즉시 경고)
    elif security['risk_level'] == 'medium':
        category = '⚠️ 피싱/악성 의심 (중간)'
        priority = 9
    elif is_kdp_rejection:
        category = '🚨 KDP 거절/수정 요청'
        priority = 10
    elif partner:
        category = f'🏢 파트너사 ({partner})'
        priority = 8
    elif is_spam:
        category = '🗑 광고/스팸'
        priority = 1
    else:
        category = '📧 일반'
        priority = 5

    return {
        'category': category,
        'partner': partner,
        'is_kdp_rejection': is_kdp_rejection,
        'is_spam': is_spam,
        'priority': priority,
    }


# ═══════════════════════════════════════
# KDP 거절 파싱 (편집부로 전달)
# ═══════════════════════════════════════
def parse_kdp_rejection(email):
    """KDP 거절 메일에서 책 제목, 거절 사유 추출"""
    body = email['body']
    subject = email['subject']

    # 책 제목 추출 시도
    book_title = ''
    title_patterns = [
        r'ASIN:\s*([A-Z0-9]+)',
        r'title[:\s]+([^\n]+)',
        r'book[:\s]+([^\n]+)',
        r'"([^"]+)"',
    ]
    for p in title_patterns:
        m = re.search(p, body, re.IGNORECASE)
        if m:
            book_title = m.group(1).strip()
            break

    # 거절 사유 (본문에서 키워드 주변 추출)
    reason = ''
    for kw in KDP_REJECTION_KEYWORDS:
        idx = body.lower().find(kw.lower())
        if idx >= 0:
            start = max(0, idx - 200)
            end = min(len(body), idx + 500)
            reason = body[start:end].strip()
            break

    return {
        'email_id': email['id'],
        'subject': subject,
        'book_title': book_title,
        'reason': reason or body[:800],
        'received_at': email['date'],
        'status': 'pending_edit',  # pending_edit → drafted → approved → sent
    }


def add_to_edit_queue(rejection):
    """편집부 대기열에 추가"""
    queue = []
    if os.path.exists(EDIT_QUEUE_FILE):
        try:
            with open(EDIT_QUEUE_FILE, 'r', encoding='utf-8') as f:
                queue = json.load(f)
        except:
            queue = []

    # 중복 체크
    if not any(item['email_id'] == rejection['email_id'] for item in queue):
        queue.append(rejection)
        with open(EDIT_QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        return True
    return False


# ═══════════════════════════════════════
# 요약 보고
# ═══════════════════════════════════════
def build_summary(emails_classified):
    """텔레그램 요약 메시지 (보안 경고 우선 표시)"""
    by_category = {}
    threats_detected = []

    for email, meta in emails_classified:
        cat = meta['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append((email, meta))

        # 위험 메일 별도 수집
        sec = email.get('_security', {})
        if sec.get('risk_level') in ('medium', 'high'):
            threats_detected.append((email, sec))

    # 우선순위 순 정렬
    ordered = sorted(by_category.items(), key=lambda x: -x[1][0][1]['priority'])

    msg = "📮 <b>비서부 메일 보고</b>\n"
    msg += f"<i>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</i>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"

    total = sum(len(v) for v in by_category.values())
    msg += f"📬 총 {total}개의 새 메일"

    # 보안 검사 결과 표시
    safe_count = total - len(threats_detected)
    msg += f"\n🔒 바이러스/피싱 검사 완료: {safe_count}개 안전"
    if threats_detected:
        msg += f", <b>{len(threats_detected)}개 위험</b>"
    msg += "\n\n"

    # 위험 메일 먼저 상세 표시
    if threats_detected:
        msg += "🛑 <b>위험 메일 경고</b>\n"
        msg += "<i>※ 클릭 전 반드시 확인하세요</i>\n\n"
        for email, sec in threats_detected[:5]:
            subject_kr = translate_subject(email['subject'])[:60]
            from_name = email['from'].split('<')[0].strip().strip('"')[:25]
            icon = '🛑' if sec['risk_level'] == 'high' else '⚠️'
            msg += f"{icon} <b>[{from_name}]</b>\n"
            msg += f"   {subject_kr}\n"
            msg += f"   위협: {sec['threats'][0][:60]}\n" if sec['threats'] else ""
            msg += f"   위험도: {sec['risk_score']}점\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"

    # 나머지 카테고리
    for cat, items in ordered:
        # 위험 카테고리는 이미 위에서 처리
        if '🛑' in cat or '⚠️' in cat:
            continue
        msg += f"<b>{cat}</b> ({len(items)}개)\n"
        for email, meta in items[:5]:
            subject_kr = translate_subject(email['subject'])[:70]
            from_name = email['from'].split('<')[0].strip().strip('"')[:20]
            msg += f"  • [{from_name}] {subject_kr}\n"
        if len(items) > 5:
            msg += f"  ... 외 {len(items)-5}개\n"
        msg += "\n"

    return msg


def send_telegram(text):
    url = f"{TG_BASE_URL}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json()


# ═══════════════════════════════════════
# 메인 실행
# ═══════════════════════════════════════
def run(hours=24, dry_run=False):
    print(f"[비서부] 최근 {hours}시간 메일 분석 시작...")

    service = authenticate()
    emails = fetch_recent_emails(service, hours=hours, max_results=50)
    print(f"  수신 메일 {len(emails)}개 가져옴")

    classified = []
    kdp_rejections = []

    for email in emails:
        meta = classify_email(email)
        classified.append((email, meta))

        if meta['is_kdp_rejection']:
            rejection = parse_kdp_rejection(email)
            if add_to_edit_queue(rejection):
                kdp_rejections.append(rejection)

    # 카테고리별 집계
    categories = {}
    for email, meta in classified:
        cat = meta['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("\n분류 결과:")
    for cat, cnt in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}개")

    if kdp_rejections:
        print(f"\n🚨 KDP 거절 {len(kdp_rejections)}건 → 편집부 대기열 추가됨")

    # 텔레그램 전송
    if not dry_run:
        summary = build_summary(classified)
        if kdp_rejections:
            summary += f"\n🚨 <b>KDP 거절 {len(kdp_rejections)}건 편집부로 전달됨</b>\n"
            for r in kdp_rejections[:3]:
                summary += f"  • {r['subject'][:60]}\n"
        result = send_telegram(summary)
        print(f"\n텔레그램 보고: {'✅' if result.get('ok') else '❌'}")

    return classified, kdp_rejections


if __name__ == '__main__':
    hours = 24
    dry_run = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'preview':
            dry_run = True
        else:
            try:
                hours = int(sys.argv[1])
            except:
                pass

    run(hours=hours, dry_run=dry_run)
