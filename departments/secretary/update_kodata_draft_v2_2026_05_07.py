"""KoDATA Gmail Draft v2 — 5/7 14:32 통화 핵심 반영 (자동 send X).

5/7 14:32 KoDATA 통화 안내:
  1. 별도 docx 작성 OK (KoDATA 안내 — hwp 양식 강제 X)
  2. 모든 서명란 3곳에 서명 필수
  3. 대표자 주민번호 뒷자리 기재 필수
  4. 사업자등록증 PDF 깨짐 → JPG로 변환 후 재발송
  5. 수신자 변경: 85343@코데이터.CO.KR (담당자 직통, find@ 아님)

작업:
  - 기존 draft 'r-346896956585314531' 삭제
  - 신규 draft 생성 (자동 send 절대 X)
  - 첨부 2: docx v2 + 사업자등록증 JPG
  - 한글 도메인 IDN punycode 변환: 코데이터.co.kr → xn--2n1bp39a0wfq1b.co.kr
"""
import os
import sys
import json
import base64
import mimetypes
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_guard import validate_outbound, validate_attachments, GuardFailure

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(SCRIPT_DIR, 'token.json')

FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = '쿤스튜디오 홍덕훈'

# 한글 도메인 IDN punycode
KODATA_DOMAIN_KOR = '코데이터.co.kr'
KODATA_DOMAIN_PUNY = KODATA_DOMAIN_KOR.encode('idna').decode('ascii')  # xn--2n1bp39a0wfq1b.co.kr
KODATA_LOCAL = '85343'
TO_EMAIL = f'{KODATA_LOCAL}@{KODATA_DOMAIN_PUNY}'
TO_DISPLAY = f'{KODATA_LOCAL}@{KODATA_DOMAIN_KOR}'  # 표시용 (한글)
CC_EMAIL = 'ghdejr11@gmail.com'

# 5/5 발송 스레드 유지 — KoDATA 회신과 동일 스레드
THREAD_ID = '19df70fe428c7e65'
OLD_DRAFT_ID = 'r-346896956585314531'  # 5/7 05:30 자동 발송 직전 draft

SUBJECT = 'Re: 기업정보등록-한국관광공사-쿤스튜디오 (정정 양식 + 사업자등록증 이미지)'

ROUND2_DIR = r'C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\applications\round2_2026_05'
ATTACHMENTS = [
    os.path.join(ROUND2_DIR, '(작성완료_v2)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.docx'),
    os.path.join(ROUND2_DIR, '사업자등록증_쿤스튜디오_2026-05-07.jpg'),
]

BODY = """안녕하세요, 한국평가데이터 담당자님.

오늘(2026-05-07) 14:30경 통화한 쿤스튜디오 대표 홍덕훈입니다.
안내해주신 사항 모두 반영하여 양식 정정 + 사업자등록증 이미지로 변환해서 재발송 드립니다.

──────────────────────────────────────────
▶ 정정 사항 (통화 안내 반영)
──────────────────────────────────────────
  1) 양식 — 별도 워드(docx)로 모든 필수기재사항 작성 (한글 hwp 환경 미보유, KoDATA 측 안내에 따라 docx 진행)
  2) 서명 — 모든 서명란 3곳 표시 (기업명 옆 / 기업개요표 / 정보제공 동의서 하단)
     ※ 자필서명 또는 서명 이미지를 [[XXX 서명]] 위치에 삽입 후 재저장 예정
  3) 대표자 주민번호 — 앞 6자리(850813)는 기재, 뒷 7자리는 [[XXX]] 위치에 직접 기입 후 발송
  4) 사업자등록증 — 기존 PDF 가독성 깨짐 안내 받고 300 DPI JPG로 변환해서 첨부

──────────────────────────────────────────
▶ 기업 정보 (사업자등록증 기준)
──────────────────────────────────────────
  - 기업명         : 쿤스튜디오 (KunStudio)
  - 사업자등록번호 : 552-59-00848
  - 대표자         : 홍덕훈
  - 대표자 생년월일: 1985-08-13
  - 개업일자       : 2026-04-01
  - 사업장 주소    : (38204) 경상북도 경주시 외동읍 제내못안길 25-52
  - 업태/종목      : 정보통신업 / 응용 소프트웨어 개발 및 공급업
  - 과세유형       : 간이과세자 (개인사업자)
  - 주요제품       : 천명당(AI 사주 SaaS, 4개국어), 세금N혜택, KORLENS

──────────────────────────────────────────
▶ 등록 사유
──────────────────────────────────────────
  한국관광공사 「2026 관광기업 데이터·AI 활용 지원 사업」(KORLENS, 마감 2026-05-20 18:00)
  및 「2026 관광데이터 활용 공모전」 신청 자격 확보를 위한 한국관광산업포털(투어라즈) 가입.

──────────────────────────────────────────
▶ 첨부 (2건)
──────────────────────────────────────────
  1. (작성완료_v2)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.docx
     - 모든 필수기재사항 + 서명 위치 표시 + 주민번호 뒷자리 기입란
  2. 사업자등록증_쿤스튜디오_2026-05-07.jpg  (300 DPI, 1.2 MB)
     - 기존 PDF 가독성 정정본

추가 누락 사항 또는 보완 사항 있으시면 회신 또는 02-3279-6500 통화 부탁드립니다.
빠른 등록 처리 부탁드립니다.

감사합니다.

쿤스튜디오 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
휴대폰: 010-4244-6992
주소: (38204) 경상북도 경주시 외동읍 제내못안길 25-52
"""


def load_service():
    with open(TOKEN_PATH, 'r', encoding='utf-8') as f:
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
    msg['From'] = formataddr((FROM_NAME, FROM_EMAIL))
    msg['To'] = TO_EMAIL  # punycode
    msg['Cc'] = CC_EMAIL
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY, 'plain', 'utf-8'))

    for path in ATTACHMENTS:
        if not os.path.isfile(path):
            raise FileNotFoundError(f'첨부 누락: {path}')
        ctype, _ = mimetypes.guess_type(path)
        if ctype is None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(path, 'rb') as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        fname = os.path.basename(path)
        part.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', fname))
        msg.attach(part)
        print(f'  [ATTACH] {fname} ({os.path.getsize(path):,} bytes)')
    return msg


def main():
    print('=== KoDATA Gmail Draft v2 (자동 send X) ===')
    print(f'  TO   : {TO_EMAIL}  (= {TO_DISPLAY})')
    print(f'  CC   : {CC_EMAIL}')
    print(f'  Subj : {SUBJECT}')
    print()

    print('[STEP 1] send_guard validate_outbound')
    try:
        validate_outbound(
            subject=SUBJECT,
            body=BODY,
            recipient=TO_EMAIL,
            attachments=ATTACHMENTS,
        )
        print('  [PASS] body + attachments OK')
    except GuardFailure as e:
        print(f'  [FAIL] {e}')
        sys.exit(1)
    print()

    service = load_service()

    print('[STEP 2] 기존 draft 삭제')
    try:
        service.users().drafts().delete(userId='me', id=OLD_DRAFT_ID).execute()
        print(f'  [DELETED] {OLD_DRAFT_ID}')
    except HttpError as e:
        if e.resp.status == 404:
            print(f'  [SKIP] 기존 draft 없음 (이미 삭제됨)')
        else:
            print(f'  [WARN] {e}')
    print()

    print('[STEP 3] 신규 draft 생성 (send 안함)')
    msg = build_message()
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {'message': {'raw': raw, 'threadId': THREAD_ID}}
    res = service.users().drafts().create(userId='me', body=body).execute()
    draft_id = res.get('id')
    msg_id = res.get('message', {}).get('id')
    print(f'  [DRAFT_CREATED] draft_id = {draft_id}')
    print(f'  [MESSAGE_ID]    {msg_id}')
    print()

    state_file = os.path.join(SCRIPT_DIR, 'kodata_draft_v2_state.json')
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump({
            'draft_id': draft_id,
            'message_id': msg_id,
            'thread_id': THREAD_ID,
            'to': TO_EMAIL,
            'to_display': TO_DISPLAY,
            'subject': SUBJECT,
            'attachments': [os.path.basename(p) for p in ATTACHMENTS],
            'created_at': '2026-05-07',
            'note': '자동 send X — 사용자가 docx에 서명+주민번호 뒷자리 채운 후 임시보관함 → SEND',
        }, f, ensure_ascii=False, indent=2)
    print(f'  [STATE] {state_file}')
    print()

    print('=' * 60)
    print('완료. 사용자 액션 (10초):')
    print('  1. docx v2 열어서 [[XXX]] 위치 3곳 서명 + 주민번호 뒷 7자리 기입')
    print('  2. 저장 후 닫기')
    print('  3. Gmail → 임시보관함 → 새 draft 검토')
    print('  4. (필요 시) docx 재첨부')
    print('  5. 보내기')
    print('=' * 60)


if __name__ == '__main__':
    main()
