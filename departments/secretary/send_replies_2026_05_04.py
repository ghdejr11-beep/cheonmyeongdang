"""2026-05-04 3건 회신 자동 발송 (Gmail API).

1) 카카오페이 [REDACTED] — 심사 보완 안내
2) 부크크 — 사업자등록 PDF 손상 → 재전송 (첨부)
3) 부크크 — ISBN 발급 불가 도서 반려 → 이해 회신

토큰: secretary/token.json (read) + token_send.json (send)
실행: python departments/secretary/send_replies_2026_05_04.py
"""
import os
import json
import base64
import mimetypes
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_READ = os.path.join(SCRIPT_DIR, 'token.json')
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')
PDF_BIZ_REG = r'D:\documents\쿤스튜디오\business_registration_new.pdf'

FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = '쿤스튜디오 홍덕훈'


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


def find_thread(read_svc, query):
    """검색 쿼리로 최신 메일 1통 찾아서 thread + headers 반환."""
    res = read_svc.users().messages().list(userId='me', q=query, maxResults=3).execute()
    msgs = res.get('messages', [])
    if not msgs:
        return None
    full = read_svc.users().messages().get(
        userId='me', id=msgs[0]['id'], format='metadata',
        metadataHeaders=['From', 'Subject', 'Message-ID', 'References', 'To']
    ).execute()
    headers = {h['name']: h['value'] for h in full['payload']['headers']}
    from_h = headers.get('From', '')
    m = re.search(r'[\w\.\-]+@[\w\.\-]+', from_h)
    return {
        'thread_id': full['threadId'],
        'message_id': headers.get('Message-ID'),
        'subject': headers.get('Subject', ''),
        'from_addr': m.group(0) if m else '',
        'references': headers.get('References'),
    }


def make_reply(meta, body_text, attachment_path=None):
    msg = MIMEMultipart()
    msg['To'] = meta['from_addr']
    msg['From'] = f'"{FROM_NAME}" <{FROM_EMAIL}>'
    subj = meta['subject'] or ''
    msg['Subject'] = subj if subj.lower().startswith('re:') else f'Re: {subj}'
    if meta.get('message_id'):
        msg['In-Reply-To'] = meta['message_id']
        ref = (meta.get('references') or '') + (' ' if meta.get('references') else '') + meta['message_id']
        msg['References'] = ref.strip()
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

    if attachment_path and os.path.exists(attachment_path):
        ctype, _ = mimetypes.guess_type(attachment_path)
        ctype = ctype or 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(attachment_path, 'rb') as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment',
                        filename=os.path.basename(attachment_path))
        msg.attach(part)
    return msg


def send_reply(send_svc, msg, thread_id):
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {'raw': raw}
    if thread_id:
        body['threadId'] = thread_id
    return send_svc.users().messages().send(userId='me', body=body).execute()


# ─────────────── 본문 ───────────────
KAKAO_BODY = """안녕하세요, 쿤스튜디오 홍덕훈입니다.
심사 보완사항 회신드립니다.

1) PG 결제창 오류 관련
- 현재 PortOne(구 아임포트) V2 SDK 통합 완료, KCN(한국결제네트웍스) 채널이 라이브 심사 진행 중입니다.
- KCN 라이브 키 발급 즉시 사이트(https://cheonmyeongdang.vercel.app)에서 카드결제창(PG)이 정상 동작 예정이며, 통과 메일 수신 즉시 본 메일로 회신드리겠습니다.
- 갤럭시아머니트리(빌게이트) 채널도 백업으로 신청·계약서 회신 단계에 있습니다 (예비 PG).
- 현재 결제 시도 시 발생한 오류는 KCN/갤럭시아 라이브 미통과 상태에서 테스트 키로 응대된 결과로 추정되며, 라이브 통과 시점에 재현 불가능 상태가 될 예정입니다.

2) 결제 형태
- 정기결제 + 단건결제 두 가지 모두 사용 예정입니다.
- 단건결제(일반결제) 온라인 신청을 추가로 진행하여 본 메일로 회신드리겠습니다.

확인·문의 사항 있으면 답신 부탁드립니다.
감사합니다.

쿤스튜디오 / 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
사이트: https://cheonmyeongdang.vercel.app
"""

BOOKK_FILE_BODY = """안녕하세요, 쿤스튜디오 홍덕훈입니다.
사업자등록 자료 파일 손상 관련 회신드립니다.

이전에 보낸 파일이 손상되어 열람이 안 되었다고 확인했습니다.
재전송드리오니 첨부 파일(business_registration_new.pdf, 1page) 확인 부탁드립니다.

만약 이번에도 열람 불가하시면 본 메일로 알려주시면 PDF 재생성 후 즉시 재전송드리겠습니다.
감사합니다.

쿤스튜디오 / 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
"""

BOOKK_ISBN_BODY = """안녕하세요, 쿤스튜디오 홍덕훈입니다.
ISBN 발급 불가 도서 반려 관련 회신드립니다.

한국문헌번호편람 7판 13페이지 기준으로 다이어리/플래너/캘린더/일기장 등 일회성 자료 형태가 ISBN 발급 대상이 아닌 점 잘 알겠습니다.
해당 도서는 부크크 진행을 중단하고, 디지털 판매(KDP / Gumroad) 채널로 운영하겠습니다.

향후 ISBN 발급이 가능한 형식(시집/소설/인문 서적/자기계발 서술서 등)으로 재신청 시 별도 진행 부탁드립니다.

확인 감사드립니다.

쿤스튜디오 / 홍덕훈
"""


def main():
    read_svc = load_service(TOKEN_READ)
    send_svc = load_service(TOKEN_SEND)

    # 5/4 16:54 1차 실행으로 카카오페이 + ISBN 반려 회신 완료 (idempotent 위해 주석 처리)
    targets = [
        # ('카카오페이', 'from:[REDACTED_PG_CONTACT] newer_than:1d', KAKAO_BODY, None),
        ('부크크 파일 손상', 'from:bookk subject:"사업자 인증 요청" newer_than:1d', BOOKK_FILE_BODY, PDF_BIZ_REG),
        # ('부크크 ISBN 반려', 'from:bookk subject:반려 newer_than:1d', BOOKK_ISBN_BODY, None),
    ]

    print('=' * 70)
    for label, q, body, attach in targets:
        meta = find_thread(read_svc, q)
        if not meta:
            print(f'  [SKIP] {label:25s} not found')
            continue
        msg = make_reply(meta, body, attachment_path=attach)
        try:
            r = send_reply(send_svc, msg, meta['thread_id'])
            print(f'  [SENT] {label:25s} -> {meta["from_addr"]:40s} attach={"Y" if attach else "N"} id={r.get("id")}')
        except Exception as e:
            print(f'  [FAIL] {label:25s} {type(e).__name__}: {str(e)[:80]}')
    print('=' * 70)


if __name__ == '__main__':
    main()
