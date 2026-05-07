"""Kakao Ventures Cold Email 재발송 (2026-05-07).

- 발송: ghdejr11@gmail.com → hello@kakao.vc
- BCC : ghdejr11@gmail.com (본인 사본)
- 첨부: kakao_ventures_1pager.pdf
- 본문: v2 hook 강화 (Co-Star $25M / Day 36 / 솔직 ₩0 / $200K seed)
"""
import os
import json
import sys
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_SEND = os.path.join(SCRIPT_DIR, 'token_send.json')

FROM_EMAIL = 'ghdejr11@gmail.com'
FROM_NAME = 'Hong Deokhoon (KunStudio)'
TO_EMAIL = 'hello@kakao.vc'
BCC_EMAIL = 'ghdejr11@gmail.com'

SUBJECT = '[Seed 제안] 천명당 - Co-Star $25M 미국만, 정통 한국 사주 4언어 글로벌 (Day 36 라이브)'

PDF_PATH = r'C:\Users\hdh02\Desktop\cheonmyeongdang\departments\fundraising\kakao_ventures_1pager.pdf'

BODY = """안녕하세요, 카카오벤처스 팀.

쿤스튜디오 홍덕훈입니다.

【3초 요약】
Co-Star는 $25M 모았고 $400K MRR을 찍었습니다. 단, 영어권 서양 점성술만.
한국 사주는 5천년 정통이고 동아시아·디아스포라 SAM이 $5B인데 - 4개 언어로 글로벌 푸는 회사가 한 곳도 없습니다.
저희가 갑니다. Day 36에 한·영·일·중 4개 언어 라이브 + AI Q&A + 글로벌 결제(PayPal) 켰습니다.

【솔직한 현재 (Day 36)】
- 매출 ₩0. 거짓말 안 합니다. 광고비 미집행, organic 단계.
- 인프라는 다 깔렸습니다: 4언어 사이트, PayPal Smart Buttons, Gumroad 18 SKU,
  AppSumo LTD 5/20 출시 예정 ($5K~$15K 30일 자동 매출 예상), Pinterest 4언어 53핀 큐,
  K-Startup AI리그 5/20 마감 (₩5천만~5억 grant 신청 중), 11+ 자동 schtask.
- 한계비용: Claude Haiku Q&A ₩30/쿼리. 사용자가 질문할수록 마진 88% → 92% 올라감.
- Burn ₩28만/월. 1인 운영, 90+ Python 자동화로 10인 팀 경제성.

【왜 카카오벤처스인가】
1. 카카오는 한국 운세 트래픽의 거대 채널 (카톡 운세·다음 운세).
2. 점신·포스텔러(시리즈 B ₩85억) 이후 글로벌 다국어 사주 AI 카테고리 공백.
3. 컨슈머 × AI × K-콘텐츠 - 카벤 포트폴리오 핵심 교집합.

【제안】
- $200K seed (약 ₩2.7억) → 12개월 runway
- 활용: 한국 #3 진입 마케팅 / 4언어 SEO·인플루언서 / 명리학 룰 350→2000 확장 / B2B API GTM
- 12개월 KPI: 첫 ₩1억 MRR, 한국 사주 앱 #3, 영어/일·중화권 #1, 시리즈 A ready

【액션】
30분 화상 데모 가능하시면 5/12(월)~5/16(금) 중 원하시는 시간 알려주세요.
라이브 트래픽(Vercel Analytics) + PayPal 콘솔 + 자동화 demo 직접 보여드립니다.

라이브: https://cheonmyeongdang.vercel.app
첨부: 천명당 1-pager PDF (1장)

감사합니다.
홍덕훈 / 쿤스튜디오 대표
ghdejr11@gmail.com
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
    msg['Bcc'] = BCC_EMAIL
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY, 'plain', 'utf-8'))

    if os.path.isfile(PDF_PATH):
        ctype, _ = mimetypes.guess_type(PDF_PATH)
        if ctype is None:
            ctype = 'application/pdf'
        maintype, subtype = ctype.split('/', 1)
        with open(PDF_PATH, 'rb') as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        fname = 'cheonmyeongdang_1pager.pdf'
        part.add_header(
            'Content-Disposition', 'attachment',
            filename=('utf-8', '', fname),
        )
        msg.attach(part)
        print(f'  [ATTACH] {fname} ({os.path.getsize(PDF_PATH):,} bytes)')
    else:
        print(f'  [WARN] PDF 누락: {PDF_PATH}')
    return msg


def main():
    print('=== Kakao Ventures Cold Email 발송 (재시도, 5/7) ===')
    print(f'  From   : {FROM_NAME} <{FROM_EMAIL}>')
    print(f'  To     : {TO_EMAIL}')
    print(f'  BCC    : {BCC_EMAIL}')
    print(f'  Subject: {SUBJECT}')

    msg = build_message()
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service = load_service()
    res = service.users().messages().send(
        userId='me', body={'raw': raw}
    ).execute()
    message_id = res.get('id')
    thread_id = res.get('threadId')
    print(f'  [SENT] message_id={message_id}')
    print(f'  [SENT] thread_id={thread_id}')
    return message_id


if __name__ == '__main__':
    main()
