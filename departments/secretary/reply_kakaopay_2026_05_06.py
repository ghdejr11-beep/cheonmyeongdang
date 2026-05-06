"""KakaoPay 김지은 매니저 답장 발송 (5/6 09:10 메일).

요청: 결제경로 작성가이드.pptx 양식 작성하여 전체 답장
현재 상태: KCN 라이브 키 발급 대기 중 → PG 결제창 캡쳐 미가능
대응: 진행 상황 공유 + 라이브 통과 후 PPT 작성/첨부 회신 약속
"""
import os, sys, base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN_SEND = os.path.join(ROOT, "token_send.json")
TOKEN = os.path.join(ROOT, "token.json")

# Reply-to threading
THREAD_MSG_ID = "19dfa9fab66e17f9"  # 5/6 09:10 김지은 답장
ORIG_MSG_ID_HEADER = "<CAG2dC1frneSs2EHzYPwEXuAqpP128+e4k7=o9cK8+saJ5EmeTQ@mail.gmail.com>"
TO = "jella.tto@kakaopaycorp.com"
FROM = "ghdejr11@gmail.com"
SUBJECT = "Re: [카카오페이] 심사관련 보완사항 안내_쿤스튜디오"

BODY = """안녕하세요. 김지은 매니저님.
쿤스튜디오 홍덕훈입니다.

[카카오페이] 심사관련 결제경로 작성가이드.pptx 잘 수령했습니다.
현재 PG 진행상황 공유드립니다.

1) 일반 PG (한국결제네트웍스 KCN) 라이브 키 발급 대기 중
   - 5/4 회신드린 대로 PortOne(아임포트) V2 SDK 통합은 완료된 상태이며,
     KCN 라이브 심사가 진행 중입니다.
   - 라이브 키 발급 즉시 사이트(https://cheonmyeongdang.vercel.app)에서
     일반 PG 결제창이 정상 동작하게 됩니다.
   - 그 시점(이번 주 ~ 다음 주 초 예상)에 가이드 양식 7개 항목을 모두 캡쳐하여
     PPT를 본 메일 전체답장으로 회신드리겠습니다.

2) 갤럭시아머니트리(빌게이트) 백업 PG 채널
   - 계약서 회신 단계이며 KCN 통과가 지연될 경우 백업 라이브로 사용 예정입니다.

3) 가이드 항목별 현재 가능한 사항 안내
   - (1) 메인 화면 URL: https://cheonmyeongdang.vercel.app/
   - (2) 푸터 정보(사업자번호 552-59-00848, 통신판매신고, 개인정보책임자) 포함됨
   - (3) 비회원 구매 가능 → 가이드 3번 항목(로그인 페이지)은 가이드 명시대로 생략
   - (4)(5) 단건결제 상품: 사주명리 정밀 풀이 A4 5장 PDF (₩9,800), 12띠 운세 다이어리 등
   - (7)   정기결제 상품: 월회원 정기결제 (월 1회 사주 풀이 콘텐츠 갱신)
   - (6)(8) PG 결제창: 라이브 키 발급 후 캡쳐 가능

라이브 키 발급은 KCN 측 영업일 기준 처리 후 즉시 회신드리며,
모든 가이드 항목을 충족한 PPT를 첨부하여 본 메일 스레드로 회신드리겠습니다.

확인 및 추가 문의 사항 있으시면 답신 부탁드립니다.
감사합니다.

쿤스튜디오 / 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
사이트: https://cheonmyeongdang.vercel.app
"""


def send():
    # gmail.modify scope token (token.json) is sufficient for sending
    if os.path.exists(TOKEN_SEND):
        creds = Credentials.from_authorized_user_file(TOKEN_SEND)
    else:
        creds = Credentials.from_authorized_user_file(TOKEN)
    service = build("gmail", "v1", credentials=creds)

    msg = EmailMessage()
    msg["To"] = TO
    msg["From"] = FROM
    msg["Subject"] = SUBJECT
    msg["In-Reply-To"] = ORIG_MSG_ID_HEADER
    msg["References"] = ORIG_MSG_ID_HEADER
    msg.set_content(BODY)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    sent = service.users().messages().send(
        userId="me",
        body={"raw": raw, "threadId": THREAD_MSG_ID and None}
    ).execute()
    print(f"sent ok msgId={sent.get('id')}")
    print(f"threadId={sent.get('threadId')}")


if __name__ == "__main__":
    send()
