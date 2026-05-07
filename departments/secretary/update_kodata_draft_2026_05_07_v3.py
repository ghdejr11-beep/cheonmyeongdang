"""KoDATA 정정 메일 draft v3 — 사용자 작성 hwp + 신규 PDF 2개 첨부.

5/7 14:32 통화 + 사용자 작성 hwp + 16:25 주민등록등본 발급 반영.

수신: 85343@xn--2n1bp39a0wfq1b.co.kr (= 85343@코데이터.co.kr)
참조: ghdejr11@gmail.com

첨부 3개:
  1. (작성완료)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.hwp (188KB)
  2. 사업자등록증명_쿤스튜디오 (1).pdf (23KB, 5/7 14:38 신규 발급)
  3. 주민등록등본.pdf (1MB, 5/7 16:25 발급)

자동 send X — drafts에 저장만.
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import formataddr
from email.header import Header
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 기존 fix_kodata_2026_05_07.py 또는 secretary token 로직 재사용
SCRIPT = Path(__file__).resolve().parent
TOKEN_FILE = SCRIPT / "token_send.json"
SEND_TOKEN = SCRIPT / "token_send.json"
RECIPIENT = "85343@xn--2n1bp39a0wfq1b.co.kr"  # 85343@코데이터.co.kr IDN
CC = "ghdejr11@gmail.com"
THREAD_ID = "19df70fe428c7e65"  # 기존 KoDATA thread

ATTACHMENTS = [
    r"C:\Users\hdh02\Downloads\(작성완료)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.hwp",
    r"C:\Users\hdh02\Downloads\사업자등록증명_쿤스튜디오 (1).pdf",
    r"C:\Users\hdh02\Downloads\주민등록등본.pdf",
]

SUBJECT = "Re: [정정] 기업정보등록-한국관광공사-쿤스튜디오 (양식 작성완료 + 사업자등록증 + 주민등록등본)"

BODY = """안녕하세요, 한국평가데이터 담당자님.

오늘(2026-05-07) 14:30경 통화한 쿤스튜디오 대표 홍덕훈입니다.

안내해주신 대로 양식 정정 + 추가 서류 첨부해서 다시 보냅니다.

1) 한국관광공사 기업정보 등록의뢰서: 모든 필수기재사항 + 서명(자필) + 대표자 주민등록번호 기재 완료
2) 사업자등록증명: 신규 발급분 첨부 (이전 PDF 깨짐 안내 받고 새로 발급)
3) 주민등록등본: 추가 첨부

확인 후 접수 부탁드립니다.

추가 누락 사항 있으면 02-3279-6500 통화 또는 회신 주세요.

감사합니다.

쿤스튜디오 대표 홍덕훈
사업자등록번호: 552-59-00848
이메일: ghdejr11@gmail.com
"""


def get_access_token() -> str:
    tok = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    data = urllib.parse.urlencode({
        "client_id": tok["client_id"],
        "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(tok["token_uri"], data=data)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())["access_token"]


def build_mime() -> bytes:
    msg = MIMEMultipart()
    msg["From"] = "ghdejr11@gmail.com"
    msg["To"] = RECIPIENT
    msg["Cc"] = CC
    msg["Subject"] = str(Header(SUBJECT, "utf-8"))
    msg.attach(MIMEText(BODY, "plain", "utf-8"))

    for path in ATTACHMENTS:
        with open(path, "rb") as f:
            data = f.read()
        fname = os.path.basename(path)
        ext = path.lower().rsplit(".", 1)[-1]
        if ext == "pdf":
            part = MIMEApplication(data, _subtype="pdf")
        elif ext == "hwp":
            part = MIMEApplication(data, _subtype="x-hwp")
        else:
            part = MIMEApplication(data)
        # filename UTF-8 encoding (RFC 2231)
        part.add_header(
            "Content-Disposition",
            "attachment",
            filename=("utf-8", "", fname),
        )
        msg.attach(part)
    return msg.as_bytes()


def list_existing_drafts(token: str) -> list:
    url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts?q=subject:기업정보등록-한국관광공사"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get("drafts", [])
    except Exception as e:
        print(f"[WARN] list drafts: {e}")
        return []


def delete_draft(token: str, draft_id: str) -> None:
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/drafts/{draft_id}"
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        urllib.request.urlopen(req, timeout=10)
        print(f"  [DELETED] draft {draft_id}")
    except Exception as e:
        print(f"  [WARN] delete {draft_id}: {e}")


def create_draft(token: str, mime_bytes: bytes, thread_id: str | None = None) -> dict:
    raw = base64.urlsafe_b64encode(mime_bytes).decode()
    body = {"message": {"raw": raw}}
    if thread_id:
        body["message"]["threadId"] = thread_id
    url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main() -> None:
    print("=== KoDATA draft v3 갱신 ===")
    token = get_access_token()
    print("[OK] gmail token")

    # 기존 KoDATA draft 모두 삭제
    drafts = list_existing_drafts(token)
    print(f"  기존 KoDATA drafts: {len(drafts)}건")
    for d in drafts:
        delete_draft(token, d["id"])

    # 새 draft 생성
    print("[BUILD] MIME 작성 중...")
    mime = build_mime()
    print(f"[BUILD] 총 {len(mime):,} bytes")

    print("[CREATE] draft 생성...")
    res = create_draft(token, mime, thread_id=THREAD_ID)
    print(f"[OK] draft_id: {res['id']}")
    print(f"[OK] message_id: {res['message']['id']}")
    print(f"[OK] threadId: {res['message']['threadId']}")
    print()
    print("✅ Gmail 임시보관함 → 'Re: [정정] 기업정보등록...' 검토 후 SEND 1클릭")
    print(f"   수신: {RECIPIENT} (= 85343@코데이터.co.kr)")
    print(f"   첨부: 의뢰서 hwp + 사업자등록증 + 주민등록등본")
    print(f"   자동 send X")


if __name__ == "__main__":
    main()
