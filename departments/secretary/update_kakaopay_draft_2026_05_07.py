"""5/7 09:19 김지은 매니저 새 답장에 맞춘 강화된 draft 교체.

기존 일반 draft (r-3810309845873979476) 삭제 → 구체적 답변 draft 신규 작성.

매니저 요청 (5/7 09:19):
1. 신용카드 PG 결제창 확인 → 결제경로 PPT 회신
2. 단건결제 추가 신청 후 회신
3. 전체 답장 사용

답변 전략:
- 단건결제 추가 신청 진행 상황 공유
- KCN 라이브 키 발급 대기 → 키 발급 즉시 PPT 첨부 회신 약속
- "이번 주~다음 주 초" 타임라인 제시
- 매니저 신뢰 유지
"""
import os
import sys
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN_SEND = os.path.join(ROOT, "token_send.json")
TOKEN = os.path.join(ROOT, "token.json")

# 5/7 09:19 김지은 매니저 새 답장
TARGET_MSG_ID = "19dffcde861edcae"
THREAD_ID = "19df17c782d108f0"
TO = "jella.tto@kakaopaycorp.com"
FROM = "ghdejr11@gmail.com"
SUBJECT = "Re: [카카오페이] 심사관련 보완사항 안내_쿤스튜디오"

# 기존 약한 draft (5/6 자동 작성)
OLD_DRAFT_ID = "r-3810309845873979476"

BODY = """안녕하세요. 김지은 매니저님.
쿤스튜디오 홍덕훈입니다.

5/7 안내 메일 확인했습니다.
요청 사항 두 가지에 대한 진행 상황 회신드립니다.

1) 신용카드 PG 결제창 확인 (결제경로 PPT)
   - 현재 PortOne V2 SDK 통합은 완료되어 있으며,
     한국결제네트웍스(KCN) 라이브 키 발급 심사가 진행 중입니다.
   - 라이브 키 발급 즉시 사이트(https://cheonmyeongdang.com)에서
     신용카드 PG 결제창이 정상 노출되며,
     첨부주신 결제경로 작성가이드.pptx 양식의 7개 항목을 모두 캡쳐하여
     본 메일 스레드로 전체답장 회신드리겠습니다.
   - 예상 시점: 이번 주 ~ 다음 주 초.
     KCN 측 영업일 처리 완료 즉시 캡쳐+PPT 첨부 회신드리겠습니다.

2) 단건결제 추가 신청
   - 카카오페이 가맹점 어드민에서 단건결제(일반결제) 온라인 추가 신청을
     이번 주 내로 완료한 뒤 본 메일로 신청 완료 회신드리겠습니다.
   - 정기결제와 단건결제 모두 PortOne V2 채널키로 분기되어
     동일 결제경로(PG 결제창 호출 단계까지)를 사용하므로,
     PPT 회신 시 단건/정기 모두 동일한 화면을 사용함을 명시하겠습니다.

3) 현재 가이드 양식 항목별 즉시 확인 가능 사항
   - 메인 화면 URL: https://cheonmyeongdang.com (운영) / https://cheonmyeongdang.vercel.app (백업)
   - 푸터 표기: 사업자번호 552-59-00848, 통신판매신고, 개인정보책임자 모두 표시
   - 상품 결제 페이지: 단건결제(₩9,800 사주 PDF, ₩9,900 프리미엄), 정기결제(₩9,900/월 월회원, ₩29,000/월 프리미엄)
   - PG 결제창 캡쳐: KCN 라이브 키 발급 후 즉시 가능

4) 일정 안내
   - 단건결제 추가 신청 완료: 5/9 (금) 이내 회신
   - KCN 라이브 통과 + PPT 첨부 회신: 5/13 (화) 전후 예상
   - 어느 쪽이든 진행 변경 시 즉시 본 스레드로 공유드리겠습니다.

확인 및 추가 문의 사항 있으시면 답신 부탁드립니다.
감사합니다.

쿤스튜디오 / 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
사이트: https://cheonmyeongdang.com
"""


def get_message_headers(svc, msg_id):
    """대상 메일의 Message-ID 헤더 가져오기 (스레드 잇기용)."""
    msg = svc.users().messages().get(userId="me", id=msg_id, format="metadata",
                                     metadataHeaders=["Message-ID", "References", "Subject"]).execute()
    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
    return headers


def main():
    # token_send.json (drafts/send) 사용
    creds = Credentials.from_authorized_user_file(TOKEN_SEND)
    svc = build("gmail", "v1", credentials=creds)

    # 1) 기존 약한 draft 삭제
    try:
        svc.users().drafts().delete(userId="me", id=OLD_DRAFT_ID).execute()
        print(f"[OK] old draft deleted: {OLD_DRAFT_ID}")
    except Exception as e:
        print(f"[WARN] old draft delete: {e}")

    # 2) target message의 Message-ID 가져오기
    headers = get_message_headers(svc, TARGET_MSG_ID)
    orig_msgid = headers.get("message-id", "")
    refs = headers.get("references", "")
    print(f"[INFO] target Message-ID: {orig_msgid}")
    print(f"[INFO] target References: {refs}")

    # 3) 새 draft 작성
    msg = EmailMessage()
    msg["To"] = TO
    msg["From"] = FROM
    msg["Subject"] = SUBJECT
    if orig_msgid:
        msg["In-Reply-To"] = orig_msgid
        msg["References"] = (refs + " " + orig_msgid).strip() if refs else orig_msgid
    msg.set_content(BODY)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    body_payload = {
        "message": {
            "raw": raw,
            "threadId": THREAD_ID,
        }
    }
    draft = svc.users().drafts().create(userId="me", body=body_payload).execute()
    print(f"[OK] new draft created: id={draft.get('id')}")
    print(f"     threadId={draft.get('message',{}).get('threadId')}")
    print(f"     msgId={draft.get('message',{}).get('id')}")
    return draft


if __name__ == "__main__":
    main()
