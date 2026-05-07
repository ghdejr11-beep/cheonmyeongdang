"""KoDATA 정정 메일 draft v4 — 모든 기존 KoDATA draft 삭제 + 깔끔하게 다시 작성.

사용자 16:34 발송 메일이 도메인 오타(codate.co.kr)로 bounce.
v3 정정 draft는 IDN punycode 정확하지만 사용자가 "새로보내" 요청.

v4 변경:
- 모든 KoDATA 관련 draft 전수 삭제 후 1개만 깔끔히 새로
- 수신: 85343@xn--2n1bp39a0wfq1b.co.kr (= 85343@코데이터.co.kr) — 정확
- 참조: find@kodata.co.kr (백업 도달 보장)
- 첨부 3개: 의뢰서 hwp + 사업자등록증 + 주민등록등본
- 본문: 명확한 통화 인사 + 첨부 list + bounce 사과

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
from email.header import Header
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPT = Path(__file__).resolve().parent
TOKEN_FILE = SCRIPT / "token_send.json"

RECIPIENT_PUNY = "85343@xn--2n1bp39a0wfq1b.co.kr"  # = 85343@코데이터.co.kr
CC = "find@kodata.co.kr,ghdejr11@gmail.com"  # find 백업 + 본인 사본
THREAD_ID = "19df70fe428c7e65"

ATTACHMENTS = [
    r"C:\Users\hdh02\Downloads\(작성완료)한국관광공사_기업정보_등록의뢰서_쿤스튜디오_2026-05-07.hwp",
    r"C:\Users\hdh02\Downloads\사업자등록증명_쿤스튜디오 (1).pdf",
    r"C:\Users\hdh02\Downloads\주민등록등본.pdf",
]

SUBJECT = "Re: [재발송] 기업정보등록-한국관광공사-쿤스튜디오 (양식 작성완료 + 사업자등록증 + 주민등록등본)"

BODY = """안녕하세요, 한국평가데이터 담당자님.

오늘(2026-05-07) 14:30경 통화한 쿤스튜디오 대표 홍덕훈입니다.

직전 16:34에 보낸 메일이 수신 도메인 표기 오류로 도달하지 않은 것 같아서 다시 보내드립니다.
받는 메일주소를 정확히 확인해서 재발송했습니다.

안내해주신 대로 양식 정정 + 추가 서류 모두 첨부합니다.

1) 한국관광공사 기업정보 등록의뢰서: 모든 필수기재사항 + 자필 서명 + 대표자 주민등록번호 기재 완료
2) 사업자등록증명: 신규 발급분 (이전 PDF 깨짐 안내 받고 새로 발급)
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


def gmail_api(token: str, path: str, method: str = "GET", body=None):
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def list_kodata_drafts(token: str) -> list:
    """기업정보등록 / 한국관광공사 / KoDATA 관련 drafts 모두."""
    out = []
    for q in ["기업정보등록", "한국관광공사", "kodata"]:
        try:
            res = gmail_api(token, f"drafts?q={urllib.parse.quote('subject:' + q)}")
            out.extend(res.get("drafts", []))
        except Exception as e:
            print(f"[WARN] list q={q}: {e}")
    # dedup
    seen = set()
    uniq = []
    for d in out:
        if d["id"] not in seen:
            seen.add(d["id"])
            uniq.append(d)
    return uniq


def delete_draft(token: str, draft_id: str) -> None:
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/drafts/{draft_id}"
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        urllib.request.urlopen(req, timeout=10)
        print(f"  [DEL] {draft_id}")
    except Exception as e:
        print(f"  [WARN] del {draft_id}: {e}")


def build_mime() -> bytes:
    msg = MIMEMultipart()
    msg["From"] = "ghdejr11@gmail.com"
    msg["To"] = RECIPIENT_PUNY
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
        part.add_header("Content-Disposition", "attachment",
                        filename=("utf-8", "", fname))
        msg.attach(part)
    return msg.as_bytes()


def create_draft(token: str, mime_bytes: bytes) -> dict:
    raw = base64.urlsafe_b64encode(mime_bytes).decode()
    body = {"message": {"raw": raw, "threadId": THREAD_ID}}
    return gmail_api(token, "drafts", method="POST", body=body)


def main() -> None:
    print("=== KoDATA draft v4 (재발송) ===")
    token = get_access_token()

    # 모든 KoDATA 관련 draft 삭제
    drafts = list_kodata_drafts(token)
    print(f"[CLEAN] 기존 KoDATA drafts: {len(drafts)}건 삭제")
    for d in drafts:
        delete_draft(token, d["id"])

    # 새 draft 생성
    print("[BUILD] MIME 작성")
    mime = build_mime()
    print(f"[BUILD] {len(mime):,} bytes")

    print("[CREATE] draft 생성")
    res = create_draft(token, mime)
    print(f"[OK] draft_id: {res['id']}")
    print(f"[OK] message_id: {res['message']['id']}")
    print()
    print("✅ 새 draft 생성 완료")
    print(f"   수신: {RECIPIENT_PUNY}")
    print(f"      = 85343@코데이터.co.kr (정확한 IDN punycode)")
    print(f"   참조: {CC}")
    print(f"   첨부: 의뢰서 hwp + 사업자등록증 + 주민등록등본")
    print(f"   thread: {THREAD_ID}")
    print()
    print("👤 Gmail 임시보관함 → 가장 위 draft → SEND 1클릭")


if __name__ == "__main__":
    main()
