"""5/7 네이버페이 가맹점 가입 4건 보류 fix 완료 안내 draft 생성.

네이버페이 가맹점 심사팀 4건 보류 사유:
1. 통신판매중개구조 명확화 → B2C 직접 판매 명시
2. 충전상품 여부 → 일회성/구독, 충전 X 명시
3. 통신판매업 신고 → 간이과세자 신고 면제 (전자상거래법 제12조 단서) 명시
4. 신용카드 결제수단 노출 → pay.html 결제수단 명시 + 아이콘 추가

본 스크립트는 위 4건 fix 완료를 네이버페이 1:1 문의로 안내하는 메일 draft를
Gmail drafts 폴더에 저장합니다 (자동 발송 X).
"""
import os
import sys
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN_SEND = os.path.join(ROOT, "token_send.json")
TOKEN = os.path.join(ROOT, "token.json")

TO = "smartstore_help@navercorp.com"  # 네이버페이 가맹점 심사팀 (1:1 문의 회신용)
FROM = "ghdejr11@gmail.com"
SUBJECT = "[네이버페이 가맹점] 4건 보류 사유 fix 완료 안내 — 쿤스튜디오 (사업자번호 552-59-00848)"

BODY = """안녕하세요. 네이버페이 가맹점 심사팀.
쿤스튜디오(천명당) 대표 홍덕훈입니다.

가맹점 가입 심사 시 안내하신 4건의 보류 사유에 대한 사이트 보완을 모두 완료하였기에 안내드립니다.

[사이트] https://cheonmyeongdang.com
[신규 안내 페이지] https://cheonmyeongdang.com/business-info.html

────────────────────────────────────────
1) 통신판매중개구조 — 보완 완료
────────────────────────────────────────
- 사이트는 제3자 판매자가 입점하지 않는 B2C 직접 판매 구조입니다.
- 모든 디지털 콘텐츠는 쿤스튜디오가 직접 제작·판매하며, 결제·환불 책임을 단독 부담합니다.
- 신규 페이지 business-info.html 제2항에 결제 흐름 도식
  (고객 → 쿤스튜디오 → 디지털 콘텐츠 즉시 제공)을 명시하였습니다.
- 메인 페이지 푸터에도 "사업 형태: B2C 직접 판매 (중개 X)"를 표기하였습니다.

────────────────────────────────────────
2) 충전상품 여부 — 보완 완료
────────────────────────────────────────
- 본 사이트는 충전형(prepaid charge) 상품을 일체 운영하지 않습니다.
- 포인트·캐시·선불 잔액 적립 및 차감 구조 없음.
- 모든 거래는 단일 SKU 일회성 구매 또는 월·연 단위 구독으로 명확히 구분됩니다.
- 가격대: ₩2,900~₩29,900 / $2.90~$29.90.
- 푸터 및 business-info.html 제3항에 "상품: 디지털 콘텐츠 (충전형 X)"를 명시하였습니다.

────────────────────────────────────────
3) 통신판매업 신고 — 면제 사유 명시 완료
────────────────────────────────────────
- 쿤스튜디오는 부가가치세법 제61조에 따른 간이과세자입니다.
- 「전자상거래 등에서의 소비자보호에 관한 법률」제12조 제1항 단서 및
  공정거래위원회 고시(제2020-11호, 2020.7.29)에 따라
  간이과세자는 통신판매업 신고 의무가 면제됩니다.
- 또한 직전 연도(2026년 4월 1일 개업) 통신판매 거래 횟수 50회 미만으로
  추가 면제 사유에도 해당합니다.
- 향후 일반과세자 전환 또는 연 거래 50회 도달 시 즉시 관할 시·군·구청
  (경상북도 경주시청)에 신고 예정임을 사이트에 명시하였습니다.
- 근거 페이지: https://cheonmyeongdang.com/business-info.html#section6

────────────────────────────────────────
4) 신용카드 결제수단 노출 — 보완 완료
────────────────────────────────────────
- 결제 페이지(https://cheonmyeongdang.com/pay.html) 상단 "3. 결제 수단" 섹션에
  지원 결제수단을 시각적 배지(아이콘)로 명시하였습니다.
  · 신용카드 · 체크카드 · 카카오페이 · 네이버페이 · 토스페이 · PayPal
- "Visa · MasterCard · JCB · Amex 글로벌 카드 모두 지원,
  PCI-DSS 인증 PG 환경에서 안전 결제" 안내 추가.
- 토스페이먼츠 V2 standard 위젯이 정상 로드되어 결제수단 선택 UI가 노출됩니다.
- 푸터에도 "결제수단: 신용카드 · 체크카드 · 카카오페이 · 네이버페이 · 토스페이 · PayPal" 표기.

────────────────────────────────────────
[참고] 사업자 정보
────────────────────────────────────────
- 상호: 쿤스튜디오 (KunStudio)
- 대표자: 홍덕훈
- 사업자등록번호: 552-59-00848 (간이과세자)
- 사업장: 경상북도 경주시 외동읍 제내못안길 25-52
- 개업일: 2026-04-01
- 호스팅: Vercel Inc.
- 개인정보보호책임자: 홍덕훈 (ghdejr11@gmail.com)

────────────────────────────────────────

상기 4건 보완 사항이 심사 기준에 부합하는지 확인 부탁드리며,
추가 보완 필요 사항이 있으시면 본 메일로 회신주시기 바랍니다.

빠른 검토 부탁드리며, 좋은 하루 보내십시오.

감사합니다.

쿤스튜디오 대표 홍덕훈
📧 ghdejr11@gmail.com
☎ 070-****-****
🌐 https://cheonmyeongdang.com
"""


def main():
    token_path = TOKEN_SEND if os.path.exists(TOKEN_SEND) else TOKEN
    if not os.path.exists(token_path):
        print(f"[ERROR] token not found: {token_path}")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(token_path)
    service = build("gmail", "v1", credentials=creds)

    msg = EmailMessage()
    msg["To"] = TO
    msg["From"] = FROM
    msg["Subject"] = SUBJECT
    msg.set_content(BODY)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body = {"message": {"raw": raw}}

    try:
        draft = service.users().drafts().create(userId="me", body=body).execute()
        draft_id = draft.get("id", "")
        msg_id = (draft.get("message") or {}).get("id", "")
        print(f"[OK] Draft created")
        print(f"  draft_id : {draft_id}")
        print(f"  message  : {msg_id}")
        print(f"  to       : {TO}")
        print(f"  subject  : {SUBJECT}")
        print(f"\n  Open in Gmail: https://mail.google.com/mail/u/0/#drafts/{msg_id}")
    except HttpError as e:
        print(f"[ERROR] Gmail API: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
