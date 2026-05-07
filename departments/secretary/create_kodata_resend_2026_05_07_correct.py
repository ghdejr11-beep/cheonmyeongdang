"""KoDATA 정정 메일 RESEND draft (2026-05-07).

5/7 16:34 발송 실패 (codate.co.kr 도메인 오타) → 정정 draft 작성.
- 받는사람: 85343@xn--2n1bp39a0wfq1b.co.kr (= 85343@코데이터.co.kr punycode)
- cc: find@kodata.co.kr (일반 주소도 동시 발송 — 어느쪽이라도 도달 보장)
- 첨부: 기존 19e015c054d7ac79 메시지의 3 첨부를 그대로 가져와 재첨부
"""
import os
import sys
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_READ = os.path.join(SCRIPT_DIR, 'token.json')
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')

ORIGINAL_MSG_ID = '19e015c054d7ac79'  # 5/7 16:34 발송 (bounce)
TO_ADDRESS = '85343@xn--2n1bp39a0wfq1b.co.kr'  # 85343@코데이터.co.kr punycode
CC_ADDRESS = 'find@kodata.co.kr'  # 정상 도달 보장 일반 주소도 cc

BODY_TEXT = """안녕하세요, 한국평가데이터 담당자님.

쿤스튜디오 대표 홍덕훈입니다.

5/7 16:34 발송 메일이 도메인 오타로 반송되어 정정 발송드립니다.

첨부:
1. (작성완료)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.hwp — 모든 필수기재사항 + 서명 + 주민번호 기재
2. 01_사업자등록증명.pdf — 홈택스 발급 정상본
3. 주민등록등본.pdf

확인 후 접수 부탁드립니다. 추가 누락 시 02-3279-6500 또는 회신 주시면 즉시 보완 가능합니다.

감사합니다.

쿤스튜디오 대표 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
"""


def load_read_service():
    with open(TOKEN_READ, 'r', encoding='utf-8') as f:
        data = json.load(f)
    creds = Credentials(
        token=data.get('token'), refresh_token=data.get('refresh_token'),
        token_uri=data.get('token_uri'), client_id=data.get('client_id'),
        client_secret=data.get('client_secret'), scopes=data.get('scopes'),
    )
    return build('gmail', 'v1', credentials=creds)


def load_send_service():
    with open(TOKEN_SEND, 'r', encoding='utf-8') as f:
        data = json.load(f)
    creds = Credentials(
        token=data.get('token'), refresh_token=data.get('refresh_token'),
        token_uri=data.get('token_uri'), client_id=data.get('client_id'),
        client_secret=data.get('client_secret'), scopes=data.get('scopes'),
    )
    return build('gmail', 'v1', credentials=creds)


def fetch_attachments(read_svc, msg_id):
    """원본 메일에서 모든 첨부파일을 (filename, mimeType, bytes)로 추출."""
    full = read_svc.users().messages().get(userId='me', id=msg_id, format='full').execute()
    out = []

    def walk(payload):
        filename = payload.get('filename', '')
        body = payload.get('body', {})
        mt = payload.get('mimeType', '')
        if filename and body.get('attachmentId'):
            att = read_svc.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=body['attachmentId']
            ).execute()
            data = base64.urlsafe_b64decode(att['data'])
            out.append((filename, mt, data))
        for sub in payload.get('parts', []) or []:
            walk(sub)

    walk(full['payload'])
    return out


def main():
    print('[1] 원본 메일 첨부 가져오기...')
    read_svc = load_read_service()
    attachments = fetch_attachments(read_svc, ORIGINAL_MSG_ID)
    print(f'  attachments: {len(attachments)}')
    for fn, mt, data in attachments:
        print(f'    - {fn} ({len(data):,} B, {mt})')

    if len(attachments) != 3:
        print(f'[WARN] 기대한 3 첨부 vs 실제 {len(attachments)}, 계속 진행')

    # MIME 메시지 작성
    msg = MIMEMultipart()
    msg['To'] = TO_ADDRESS
    msg['Cc'] = CC_ADDRESS
    msg['From'] = '"쿤스튜디오 홍덕훈" <ghdejr11@gmail.com>'
    msg['Subject'] = '[정정 발송] 기업정보등록-한국관광공사-쿤스튜디오 (5/7 도메인 반송 보완)'
    msg.attach(MIMEText(BODY_TEXT, 'plain', 'utf-8'))

    for filename, mt, data in attachments:
        # MIME type 분리
        main_type, _, sub_type = mt.partition('/')
        if not sub_type:
            main_type, sub_type = 'application', 'octet-stream'
        part = MIMEBase(main_type, sub_type)
        part.set_payload(data)
        encoders.encode_base64(part)
        # RFC 2231 한글 파일명 지원
        try:
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        except Exception:
            part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    print('[2] Gmail draft 생성...')
    # gmail.modify scope = draft create 포함, gmail.send만으로는 draft 불가
    send_svc = read_svc
    draft = send_svc.users().drafts().create(
        userId='me', body={'message': {'raw': raw}}
    ).execute()
    print(f'  [DRAFT CREATED] id={draft.get("id")}, message_id={draft.get("message", {}).get("id")}')
    print(f'  → https://mail.google.com/mail/u/0/#drafts')
    return draft


if __name__ == '__main__':
    main()
