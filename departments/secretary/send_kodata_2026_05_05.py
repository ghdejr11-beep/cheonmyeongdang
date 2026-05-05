"""KoDATA 기업정보 등록 신청 메일 자동 발송 (2026-05-05).

- 목적: 한국관광산업포털(투어라즈) 가입을 위한 KoDATA 기업정보 사전 등록
- 대회: 2026 관광기업 데이터·AI 활용 지원 사업 (마감 5/20 18:00)
- 발송: ghdejr11@gmail.com → find@kodata.co.kr
- 제목: 기업정보등록-한국관광공사-쿤스튜디오
"""
import os
import json
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token.json')  # gmail.modify scope (send 포함 시도)

FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = '쿤스튜디오 홍덕훈'

TO_EMAIL = 'find@kodata.co.kr'
SUBJECT = '기업정보등록-한국관광공사-쿤스튜디오'

ROUND2 = r'C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\applications\round2_2026_05'
DOWNLOADS = r'C:\Users\hdh02\Downloads'

ATTACHMENTS = [
    # KoDATA 등록의뢰서 양식 (참고용 — 본문에 정보 기재)
    os.path.join(ROUND2, '(양식)한국관광공사 기업정보 등록의뢰서.hwp'),
    # 사업자등록증명서 PDF
    os.path.join(DOWNLOADS, '사업자등록증명_쿤스튜디오.pdf'),
]

BODY = """안녕하십니까,

쿤스튜디오 홍덕훈입니다.

「2026 관광기업 데이터·AI 활용 지원 사업」(한국관광공사, 마감 2026.05.20)에 참여하고자
한국관광산업포털(투어라즈) 가입을 진행 중입니다.
가입 절차상 한국평가데이터(KoDATA)에 기업정보 사전 등록이 필요하여 본 메일로 등록 신청드립니다.

▶ 등록 의뢰 정보 (사업자등록증 기준)

  - 기업명         : 쿤스튜디오 (KunStudio)
  - 대표자         : 홍덕훈
  - 사업자등록번호 : 552-59-00848
  - 개업일자       : 2026-04-01
  - 사업장 주소    : (38204) 경상북도 경주시 외동읍 제내못안길 25-52
  - 업태           : 정보통신업
  - 종목           : 응용 소프트웨어 개발 및 공급업
  - 과세유형       : 간이과세자
  - 연락처(휴대폰) : 010-XXXX-XXXX  *통화 가능 시 회신 부탁드립니다
  - 이메일         : ghdejr11@gmail.com
  - 사업 형태      : 개인사업자 (1인 운영)

▶ 등록 사유
  한국관광공사 「2026 관광기업 데이터·AI 활용 지원 사업」 신청 자격 확보

▶ 첨부
  1. (양식) 한국관광공사 기업정보 등록의뢰서.hwp  *참고용
  2. 사업자등록증명서.pdf

추가 양식 작성이 필요하거나 보완 자료가 필요하시면 회신 부탁드립니다.
빠른 등록 처리 부탁드리겠습니다. 감사합니다.

쿤스튜디오 홍덕훈
사업자번호: 552-59-00848
이메일: ghdejr11@gmail.com
"""


def load_service():
    with open(TOKEN_SEND, 'r', encoding='utf-8') as f:
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


def build_message():
    msg = MIMEMultipart()
    msg['From'] = f'{FROM_NAME} <{FROM_EMAIL}>'
    msg['To'] = TO_EMAIL
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY, 'plain', 'utf-8'))

    for path in ATTACHMENTS:
        if not os.path.isfile(path):
            print(f'  [WARN] 첨부 누락: {path}')
            continue
        ctype, _ = mimetypes.guess_type(path)
        if ctype is None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(path, 'rb') as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        fname = os.path.basename(path)
        part.add_header(
            'Content-Disposition', 'attachment',
            filename=('utf-8', '', fname),
        )
        msg.attach(part)
        print(f'  [ATTACH] {fname} ({os.path.getsize(path):,} bytes)')
    return msg


def main():
    print('=== KoDATA 등록 메일 발송 ===')
    print(f'  From: {FROM_NAME} <{FROM_EMAIL}>')
    print(f'  To  : {TO_EMAIL}')
    print(f'  Subj: {SUBJECT}')

    msg = build_message()
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service = load_service()
    res = service.users().messages().send(
        userId='me', body={'raw': raw}
    ).execute()
    print(f'  [SENT] message_id={res.get("id")}')


if __name__ == '__main__':
    main()
