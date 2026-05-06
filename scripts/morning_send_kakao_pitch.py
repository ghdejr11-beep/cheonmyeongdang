#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
morning_send_kakao_pitch.py
2026-05-07 09:00 KST 자동 발송 — Kakao Ventures cold email pitch.

목적:
  - hello@kakao.vc 로 천명당 시드 제안 메일 발송 (홍덕훈 / 쿤스튜디오)
  - 본문: departments/fundraising/kakao_ventures_cold_email.md (코드 블록 추출)
  - 첨부: departments/fundraising/kakao_ventures_1pager.md (PDF 변환 시도)
  - 발송 후 logs/kakao_pitch_sent_2026_05_07.json 기록

사용법:
  python scripts/morning_send_kakao_pitch.py --dry-run   # 미리보기 (발송 X)
  python scripts/morning_send_kakao_pitch.py             # 실 발송

schtask 등록 (Windows):
  schtasks /Create /SC ONCE /SD 2026/05/07 /ST 09:00 ^
    /TN "KunStudio_KakaoVC_PitchSend" ^
    /TR "python C:\\Users\\hdh02\\Desktop\\cheonmyeongdang\\scripts\\morning_send_kakao_pitch.py" /F
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import mimetypes
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Force UTF-8 stdout (Windows cp949 fix)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SECRETS = ROOT / ".secrets"
SECRETARY = ROOT / "departments" / "secretary"
TOKEN_SEND = SECRETARY / "token_send.json"
TOKEN_FALLBACK = SECRETARY / "token.json"  # gmail.modify (send 포함)

EMAIL_MD = ROOT / "departments" / "fundraising" / "kakao_ventures_cold_email.md"
ONEPAGER_MD = ROOT / "departments" / "fundraising" / "kakao_ventures_1pager.md"

LOGS_DIR = ROOT / "logs"
LOG_FILE = LOGS_DIR / "kakao_pitch_sent_2026_05_07.json"

FROM_EMAIL = "ghdejr11@gmail.com"
FROM_NAME = "쿤스튜디오 홍덕훈"
TO_EMAIL = "hello@kakao.vc"
SUBJECT = "[Seed 제안] 천명당 — 4언어 한국 사주 AI SaaS, Day 36 라이브 (홍덕훈 / 쿤스튜디오)"


def load_secrets() -> dict[str, str]:
    out: dict[str, str] = {}
    if not SECRETS.exists():
        return out
    with open(SECRETS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def telegram_alert(msg: str) -> None:
    """텔레그램 알림 (실패 시 silent)."""
    creds = load_secrets()
    token = creds.get("TELEGRAM_BOT_TOKEN")
    chat = creds.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    try:
        data = urllib.parse.urlencode(
            {"chat_id": chat, "text": msg, "disable_web_page_preview": "true"}
        ).encode()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        req = urllib.request.Request(url, data=data, method="POST")
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        pass


def extract_email_body(md_path: Path) -> str:
    """`kakao_ventures_cold_email.md` 의 ``` 코드 블록(본문) 추출."""
    text = md_path.read_text(encoding="utf-8")
    # ```...``` 블록 찾기 (가장 큰 것)
    blocks = re.findall(r"```(?:\w*\n)?(.*?)```", text, flags=re.DOTALL)
    if blocks:
        # 가장 긴 블록 = 본문
        return max(blocks, key=len).strip() + "\n"
    # fallback: 전체 텍스트 (markdown formatting 제거 정도)
    return text.strip() + "\n"


def try_md_to_pdf(md_path: Path) -> Path | None:
    """1-pager md → PDF 변환 시도. 실패 시 None."""
    pdf_path = md_path.with_suffix(".pdf")
    # 1) reportlab 사용 (간단 변환)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        )
        from reportlab.lib import colors

        # 한글 폰트 등록 (CID — Adobe 내장, 추가 다운로드 X)
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
            font_name = "HYSMyeongJo-Medium"
        except Exception:
            font_name = "Helvetica"

        text = md_path.read_text(encoding="utf-8")
        lines = text.splitlines()

        styles = getSampleStyleSheet()
        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"], fontName=font_name,
            fontSize=9, leading=12,
        )
        h1 = ParagraphStyle(
            "H1", parent=styles["Heading1"], fontName=font_name,
            fontSize=16, leading=20, textColor=colors.HexColor("#222"),
        )
        h2 = ParagraphStyle(
            "H2", parent=styles["Heading2"], fontName=font_name,
            fontSize=12, leading=16, textColor=colors.HexColor("#444"),
        )

        story = []
        for line in lines:
            s = line.rstrip()
            if not s:
                story.append(Spacer(1, 4))
                continue
            if s.startswith("# "):
                story.append(Paragraph(s[2:].strip(), h1))
            elif s.startswith("## "):
                story.append(Paragraph(s[3:].strip(), h2))
            elif s.startswith("---"):
                story.append(Spacer(1, 6))
            elif s.startswith("|"):
                # 표는 단순 텍스트로
                story.append(Paragraph(s.replace("|", " | "), body_style))
            else:
                # markdown bold/italic 간단 처리
                cleaned = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
                cleaned = re.sub(r"\*(.+?)\*", r"<i>\1</i>", cleaned)
                story.append(Paragraph(cleaned, body_style))

        doc = SimpleDocTemplate(
            str(pdf_path), pagesize=A4,
            leftMargin=15*mm, rightMargin=15*mm,
            topMargin=15*mm, bottomMargin=15*mm,
        )
        doc.build(story)
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            print(f"  [PDF] reportlab 변환 성공: {pdf_path.name} "
                  f"({pdf_path.stat().st_size:,} bytes)")
            return pdf_path
    except Exception as e:
        print(f"  [WARN] reportlab PDF 변환 실패: {e}")

    return None


def build_message(body_text: str, attachments: list[Path]) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = TO_EMAIL
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    for path in attachments:
        if not path or not path.is_file():
            print(f"  [WARN] 첨부 누락: {path}")
            continue
        ctype, _ = mimetypes.guess_type(str(path))
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", "attachment",
            filename=("utf-8", "", path.name),
        )
        msg.attach(part)
        print(f"  [ATTACH] {path.name} ({path.stat().st_size:,} bytes)")
    return msg


def load_gmail_service():
    """token_send.json 우선, fallback token.json."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    token_path = TOKEN_SEND if TOKEN_SEND.exists() else TOKEN_FALLBACK
    if not token_path.exists():
        raise RuntimeError(f"Gmail token not found: {TOKEN_SEND} or {TOKEN_FALLBACK}")
    with open(token_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
    )
    print(f"  [TOKEN] using {token_path.name} (scopes={data.get('scopes')})")
    return build("gmail", "v1", credentials=creds)


def write_log(payload: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  [LOG] {LOG_FILE}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="발송하지 않고 본문/첨부 미리보기")
    args = ap.parse_args()

    print("=" * 60)
    print("Kakao Ventures cold email — 자동 발송")
    print(f"  From: {FROM_NAME} <{FROM_EMAIL}>")
    print(f"  To  : {TO_EMAIL}")
    print(f"  Subj: {SUBJECT}")
    print(f"  Time: {datetime.now().isoformat()}")
    print("=" * 60)

    # 1) 본문 추출
    if not EMAIL_MD.exists():
        print(f"[FAIL] 메일 본문 파일 없음: {EMAIL_MD}")
        telegram_alert(f"[Kakao VC] 발송 실패 — 본문 파일 없음: {EMAIL_MD.name}")
        return 1
    body = extract_email_body(EMAIL_MD)
    print(f"\n[BODY] {len(body)} chars from {EMAIL_MD.name}")
    if args.dry_run:
        preview = body[:1500] + ("\n... (truncated)" if len(body) > 1500 else "")
        print("-" * 60)
        print(preview)
        print("-" * 60)

    # 2) 첨부 준비 (PDF 시도, 실패 시 md)
    attachments: list[Path] = []
    if ONEPAGER_MD.exists():
        pdf = try_md_to_pdf(ONEPAGER_MD)
        attachments.append(pdf if pdf else ONEPAGER_MD)
    else:
        print(f"  [WARN] 1-pager 없음: {ONEPAGER_MD}")

    if args.dry_run:
        print(f"\n[DRY-RUN] 첨부 후보: {[p.name for p in attachments]}")
        print("[DRY-RUN] 실 발송 X. 종료.")
        return 0

    # 3) 메시지 빌드 + 발송
    try:
        msg = build_message(body, attachments)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service = load_gmail_service()
        res = service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        msg_id = res.get("id")
        print(f"\n  [SENT] message_id={msg_id}")
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        print(f"\n[FAIL] {err}")
        telegram_alert(
            f"[Kakao VC 발송 실패]\n{err}\n\n수동 발송 필요: hello@kakao.vc"
        )
        # 실패 로그도 남김
        write_log({
            "ok": False,
            "error": err,
            "to": TO_EMAIL,
            "subject": SUBJECT,
            "attempted_at": datetime.now().isoformat(),
        })
        return 2

    # 4) 성공 로그
    write_log({
        "ok": True,
        "msg_id": msg_id,
        "to": TO_EMAIL,
        "subject": SUBJECT,
        "from": FROM_EMAIL,
        "sent_at": datetime.now().isoformat(),
        "attachments": [p.name for p in attachments if p.is_file()],
        "body_chars": len(body),
        "body_source": EMAIL_MD.name,
    })

    telegram_alert(
        f"[Kakao VC 발송 완료]\nmsg_id={msg_id}\nto={TO_EMAIL}\n"
        f"첨부: {', '.join(p.name for p in attachments if p.is_file())}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
