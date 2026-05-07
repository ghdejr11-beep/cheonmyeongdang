"""KoDATA 빈양식 회신 정정 — 작성완료 의뢰서 재발송 (2026-05-07).

KoDATA 회신: "보내주신 의뢰서가 빈양식입니다. 필수기재사항 모두 기재 + 하단 서명 후
다시 메일 보내주세요."

대응:
  1) hwp 직접 편집 불가 (한컴오피스 전용 + LibreOffice 미설치)
  2) docx로 모든 필수기재사항 채워서 재발송
  3) 본문에 빈양식 사과 + 채워진 정보 명시 (수신자가 docx 못 열어도 본문으로 처리 가능)
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
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token.json')

FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = '쿤스튜디오 홍덕훈'
TO_EMAIL = 'find@kodata.co.kr'
CC_EMAIL = 'ghdejr11@gmail.com'
SUBJECT = 'Re: 빈양식 회신 정정 - 기업정보등록-한국관광공사-쿤스튜디오'

ROUND2 = r'C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\applications\round2_2026_05'
DOWNLOADS = r'C:\Users\hdh02\Downloads'

ATTACHMENTS = [
    # 채워진 의뢰서 (docx, 모든 필수기재사항 포함 + 서명)
    os.path.join(ROUND2, '(작성완료)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.docx'),
    # 원본 hwp 양식 (참고용 — 한컴오피스로 다시 열어 변환 가능)
    os.path.join(ROUND2, '(양식)한국관광공사 기업정보 등록의뢰서.hwp'),
    # 사업자등록증명서
    os.path.join(DOWNLOADS, '사업자등록증명_쿤스튜디오.pdf'),
]

BODY = """안녕하십니까,

쿤스튜디오 홍덕훈입니다.

5월 5일 발송드린 「기업정보등록-한국관광공사-쿤스튜디오」 메일에 대한
"빈양식 회신" 안내를 받고 정정 발송드립니다.

원본 hwp 양식이 메일 첨부 과정에서 본문이 비워진 채로 전달되었던 것으로 확인되어
대단히 죄송합니다. 동일한 정보를 채운 의뢰서(docx)와 본문 정보를 함께 보내드립니다.

──────────────────────────────────────────
▶ 입력 대상기업 (필수기재사항)
──────────────────────────────────────────
  - 기업명         : 쿤스튜디오 (KunStudio)
  - 사업자등록번호 : 552-59-00848
  - 대표자         : 홍덕훈
  - 대표자 생년월일: 1985-08-13 (만 41세)
  - 법인등록번호   : 해당없음 (개인사업자)
  - 개업일자       : 2026-04-01
  - 본사 / 사업장 주소
                   : (38204) 경상북도 경주시 외동읍 제내못안길 25-52
  - 업태           : 정보통신업
  - 종목           : 응용 소프트웨어 개발 및 공급업
  - 주요제품       : 천명당(AI 사주 SaaS, 4개국어), 세금N혜택, KORLENS
  - 홈페이지       : https://cheonmyeongdang.com / https://korlens.app
  - 과세유형       : 간이과세자
  - 사업 형태      : 개인사업자 (1인 운영)
  - 상시종업원수   : 1명 (대표자만)

──────────────────────────────────────────
▶ 서류 제출자 / 담당자 정보
──────────────────────────────────────────
  - 담당자         : 홍덕훈 (대표 본인)
  - 담당자 휴대폰  : 010-4244-6992
  - 회사 대표전화  : 070-8018-7832
  - 회사 대표팩스  : 없음 (1인 기업)
  - 문자메시지수신 : 예 (010-4244-6992로 부탁드립니다)
  - 이메일         : ghdejr11@gmail.com

──────────────────────────────────────────
▶ 등록 사유
──────────────────────────────────────────
  한국관광공사 「2026 관광기업 데이터·AI 활용 지원 사업」(KORLENS,
  마감 2026.05.20 18:00) 및 「2026 관광데이터 활용 공모전」 신청 자격
  확보를 위한 한국관광산업포털(투어라즈) 가입.

──────────────────────────────────────────
▶ 신용정보 동의 (모두 동의)
──────────────────────────────────────────
  ☑ 기업(신용)정보 수집·조회 동의 (필수)
  ☑ 개인(신용)정보 수집·활용 동의 (필수)
  ☑ 개인(신용)정보 제공 동의 (필수)
  ☑ 개인(신용)정보 조회 동의 (필수)
  ☑ 고유식별정보 수집·제공 동의 (필수)
  ☑ 개인(신용)정보 수집·활용 동의 (선택)

──────────────────────────────────────────
▶ 서명
──────────────────────────────────────────
  2026년 05월 07일
  기업체명         : 쿤스튜디오 (KunStudio)
  사업자등록번호   : 552-59-00848
  대표자 성명      : 홍덕훈 (전자서명)

  ※ 대표자 주민등록번호 뒷자리는 보안상 본 메일에서 마스킹 처리하였으며,
    필요 시 별도 본인확인 절차를 통해 안전하게 제공드리겠습니다.

──────────────────────────────────────────
▶ 첨부서류
──────────────────────────────────────────
  1. (작성완료) 한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.docx
     ─ 필수기재사항 모두 기재 + 동의항목 체크 + 전자서명 포함
  2. (양식) 한국관광공사 기업정보 등록의뢰서.hwp  *원본 양식 참고용
  3. 사업자등록증명서.pdf

──────────────────────────────────────────
▶ 일정 안내 (긴급)
──────────────────────────────────────────
  한국관광공사 「관광 AI 활용 지원 사업」 신청 마감이 2026-05-20 18:00로
  D-13 남은 상황입니다. 신속한 등록 처리를 부탁드리며, 추가 자료가
  필요하시면 즉시 회신드리겠습니다.

다시 한 번 빈양식 발송 건에 대해 사과드리며, 처리 부탁드립니다.

감사합니다.

──────────────────────────────────────────
쿤스튜디오 대표 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
연락처: 070-****-****
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
    msg['Cc'] = CC_EMAIL
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
    print('=== KoDATA 정정 메일 재발송 (2026-05-07) ===')
    print(f'  From: {FROM_NAME} <{FROM_EMAIL}>')
    print(f'  To  : {TO_EMAIL}')
    print(f'  Cc  : {CC_EMAIL}')
    print(f'  Subj: {SUBJECT}')

    msg = build_message()
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service = load_service()
    res = service.users().messages().send(
        userId='me', body={'raw': raw}
    ).execute()
    print(f'  [SENT] message_id={res.get("id")}')
    print(f'  [SENT] thread_id={res.get("threadId")}')

    # state 기록
    state_file = os.path.join(SCRIPT_DIR, 'kodata_resend_state.json')
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump({
            'sent_at': '2026-05-07',
            'message_id': res.get('id'),
            'thread_id': res.get('threadId'),
            'to': TO_EMAIL,
            'subject': SUBJECT,
            'attachments': [os.path.basename(p) for p in ATTACHMENTS if os.path.isfile(p)],
        }, f, ensure_ascii=False, indent=2)
    print(f'  [STATE] {state_file}')


if __name__ == '__main__':
    main()
