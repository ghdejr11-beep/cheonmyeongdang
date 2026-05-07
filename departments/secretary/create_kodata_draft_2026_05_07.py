"""KoDATA 정정 양식 첨부 — Gmail Draft 생성 (자동 send X) — 2026-05-07.

배경:
  - 5/5 16:35 발송: (양식)한국관광공사 기업정보 등록의뢰서.hwp 빈 양식 첨부 → KoDATA 회신 (5/6 09:24)
    "보내주신 의뢰서가 빈양식입니다. 필수기재사항 모두 기재 + 하단 서명 후 재발송"
  - 5/7 05:30 자동 발송 (이전 세션): (작성완료)docx + (양식)빈hwp + PDF 첨부 → 빈 hwp 또 들어감 (RISK)

이번 작업 (사용자 명시 지시):
  - DRAFT만 생성, 자동 send 절대 X
  - 첨부에서 (양식) 빈 hwp 제외
  - (작성완료)docx + 사업자등록증명 PDF 만 첨부
  - send_guard 전체 통과
  - 사용자가 Gmail 임시보관함에서 검토 후 1클릭 발송

수신: find@kodata.co.kr
참조: ghdejr11@gmail.com (본인 cc)
스레드: 19df70fe428c7e65 (KoDATA 회신과 동일 스레드)
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
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 부서 send_guard
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_guard import validate_outbound, validate_attachments, GuardFailure

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(SCRIPT_DIR, 'token.json')

FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = '쿤스튜디오 홍덕훈'
TO_EMAIL = 'find@kodata.co.kr'
CC_EMAIL = 'ghdejr11@gmail.com'
THREAD_ID = '19df70fe428c7e65'  # KoDATA 회신 스레드
SUBJECT = 'Re: 기업정보등록-한국관광공사-쿤스튜디오 (정정 양식 첨부)'

ROUND2_DIR = r'C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\applications\round2_2026_05'
DOWNLOADS = r'C:\Users\hdh02\Downloads'

ATTACHMENTS = [
    os.path.join(ROUND2_DIR, '(작성완료)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.docx'),
    os.path.join(DOWNLOADS, '사업자등록증명_쿤스튜디오.pdf'),
]

BODY = """안녕하십니까,

쿤스튜디오 홍덕훈입니다.

5월 6일 회신 메일(빈양식 안내) 잘 받았습니다.
원본 hwp 양식 편집 환경이 없어 부득이 워드(docx)로 동일 항목을 모두 기재하여 재발송드립니다.
한글(hwp) 형식이 반드시 필요하시면 회신 한 번 주시면 출력·자필 서명 후 우편 또는 팩스로 별도 발송드리겠습니다.

──────────────────────────────────────────
▶ 필수기재사항 (사업자등록증 기준)
──────────────────────────────────────────
  - 기업명         : 쿤스튜디오 (KunStudio)
  - 사업자등록번호 : 552-59-00848
  - 대표자         : 홍덕훈
  - 대표자 생년월일: 1985-08-13 (만 41세)
  - 법인등록번호   : 해당없음 (개인사업자)
  - 개업일자       : 2026-04-01
  - 본사/사업장 주소: (38204) 경상북도 경주시 외동읍 제내못안길 25-52
  - 업태           : 정보통신업
  - 종목           : 응용 소프트웨어 개발 및 공급업
  - 주요제품       : 천명당(AI 사주 SaaS, 4개국어), 세금N혜택, KORLENS
  - 홈페이지       : https://cheonmyeongdang.com / https://korlens.app
  - 과세유형       : 간이과세자
  - 사업 형태      : 개인사업자 (1인 운영)
  - 상시종업원수   : 1명 (대표자만)
  - 자본금         : 해당없음 (개인사업자)
  - 직전년도 매출  : 0원 (2026-04-01 개업, 5/7 시점 매출 없음)

──────────────────────────────────────────
▶ 담당자
──────────────────────────────────────────
  - 담당자         : 홍덕훈 (대표 본인)
  - 휴대폰         : 010-4244-6992
  - 회사 대표전화  : 070-8018-7832
  - 이메일         : ghdejr11@gmail.com
  - 통화 가능 시간 : 평일/주말 09:00-22:00 (KST)

──────────────────────────────────────────
▶ 등록 사유
──────────────────────────────────────────
  한국관광공사 「2026 관광기업 데이터·AI 활용 지원 사업」(KORLENS, 마감 2026.05.20 18:00)
  및 「2026 관광데이터 활용 공모전」 신청 자격 확보를 위한 한국관광산업포털(투어라즈) 가입.

──────────────────────────────────────────
▶ 신용정보 동의
──────────────────────────────────────────
  본 의뢰서 제출로써 다음 사항에 모두 동의합니다.
  · 기업(신용)정보 수집·조회·제공 동의 (필수)
  · 개인(신용)정보 수집·활용·제공 동의 (필수)
  · 한국관광공사 기업정보 등록 목적 활용 동의 (필수)

──────────────────────────────────────────
▶ 첨부
──────────────────────────────────────────
  1. (작성완료)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.docx
     - 모든 필수기재사항 + 하단 서명(전자) 완료
  2. 사업자등록증명_쿤스튜디오.pdf  (사실 확인용, 4/22 발급)

빠른 등록 처리 부탁드립니다.
보완 서류가 필요하시면 위 휴대폰(010-4244-6992) 또는 메일로 연락 주시기 바랍니다.

전자서명: 홍덕훈
작성일자: 2026-05-07

감사합니다.

쿤스튜디오 홍덕훈
사업자번호: 552-59-00848
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
    msg['From'] = f'{FROM_NAME} <{FROM_EMAIL}>'
    msg['To'] = TO_EMAIL
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
    print('=== KoDATA Gmail Draft 생성 (자동 send X) ===')
    print()
    print('[STEP 1] send_guard 검증 (본문 + 첨부)')
    try:
        validate_outbound(
            subject=SUBJECT,
            body=BODY,
            recipient=TO_EMAIL,
            attachments=ATTACHMENTS,
        )
        print('  [PASS] send_guard validate_outbound OK')
    except GuardFailure as e:
        print(f'  [FAIL] {e}')
        sys.exit(1)
    print()

    print('[STEP 2] 메일 빌드')
    print(f'  From   : {FROM_NAME} <{FROM_EMAIL}>')
    print(f'  To     : {TO_EMAIL}')
    print(f'  Cc     : {CC_EMAIL}')
    print(f'  Subj   : {SUBJECT}')
    print(f'  Thread : {THREAD_ID}')
    msg = build_message()
    print()

    print('[STEP 3] Gmail Draft 생성 (send 안함)')
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service = load_service()
    body = {'message': {'raw': raw, 'threadId': THREAD_ID}}
    res = service.users().drafts().create(userId='me', body=body).execute()
    draft_id = res.get('id')
    msg_id = res.get('message', {}).get('id')
    print(f'  [DRAFT_CREATED] draft_id={draft_id}')
    print(f'  [MESSAGE_ID]    {msg_id}')
    print()

    print('=' * 60)
    print('완료. 사용자 액션:')
    print('  Gmail → 임시보관함(Drafts)')
    print('  → "Re: 기업정보등록-한국관광공사-쿤스튜디오 (정정 양식 첨부)"')
    print('  → 첨부 검토')
    print('  → SEND 1클릭')
    print('=' * 60)


if __name__ == '__main__':
    main()
