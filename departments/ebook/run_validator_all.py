#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_validator_all.py — KDP Validator 일괄 실행 + 실패 시 텔레그램 알림

사용법
  python run_validator_all.py                       # projects/ 전체
  python run_validator_all.py --strict              # 엄격 모드
  python run_validator_all.py --root <path>         # 다른 루트
  python run_validator_all.py --no-telegram         # 알림 끔

환경변수 (또는 .secrets 파일)
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib import request, parse

# kdp_validator.py 와 같은 디렉터리에 있다고 가정
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from kdp_validator import (
    validate_book, save_validation_report, _pretty_print,  # type: ignore
)

DEFAULT_ROOT = HERE / "projects"
SECRETS_PATH = HERE.parent.parent / ".secrets"  # cheonmyeongdang/.secrets


def _load_secrets(path: Path) -> dict:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _send_telegram(token: str, chat_id: str, text: str) -> bool:
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = parse.urlencode({
        "chat_id": chat_id,
        "text": text[:4000],
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = request.Request(
        url, data=payload,
        headers={"User-Agent": "kdp-validator/1.0"},
    )
    try:
        with request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[telegram] error: {e}", file=sys.stderr)
        return False


def _book_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    out = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("_") or child.name.startswith("."):
            continue
        # 적어도 PDF 1개는 있어야 책 폴더로 인정
        if any(child.glob("*.pdf")):
            out.append(child)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="KDP Validator 일괄 실행")
    parser.add_argument("--root", type=str, default=str(DEFAULT_ROOT),
                        help="책 디렉터리들을 담은 루트 (기본 projects/)")
    parser.add_argument("--strict", action="store_true", help="WARN을 FAIL로 격상")
    parser.add_argument("--db", type=str, default=None,
                        help="published_books.json 경로 (기본: ebook/published_books.json)")
    parser.add_argument("--reports-dir", type=str, default=str(HERE / "logs" / "kdp_reports"),
                        help="JSON 리포트 저장 디렉터리")
    parser.add_argument("--no-telegram", action="store_true", help="텔레그램 알림 끔")
    args = parser.parse_args()

    root = Path(args.root)
    db_path = Path(args.db) if args.db else (HERE / "published_books.json")
    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    books = _book_dirs(root)
    if not books:
        print(f"[run_all] {root} 에서 책 폴더를 찾지 못함")
        return 0

    summary: list[dict] = []
    failed_books: list[tuple[str, list[str]]] = []
    for book in books:
        report = validate_book(book, strict=args.strict, db_path=db_path)
        _pretty_print(report)
        save_validation_report(report, reports_dir / f"{book.name}.json")
        summary.append({"book": book.name, "overall": report.overall})
        if report.overall == "FAIL":
            fails = [
                f"{it.name}: {it.message}"
                for it in (report.cover + report.interior + report.metadata)
                if it.status == "FAIL"
            ]
            failed_books.append((book.name, fails))

    print("\n" + "=" * 60)
    print("BATCH SUMMARY")
    for s in summary:
        print(f"  {s['overall']:<6} {s['book']}")
    print(f"  total={len(summary)} fail={len(failed_books)}")

    # ---- Telegram alert on any FAIL ----
    if failed_books and not args.no_telegram:
        secrets = {**os.environ, **_load_secrets(SECRETS_PATH)}
        token = secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = secrets.get("TELEGRAM_CHAT_ID", "")
        lines = [f"<b>[KDP Validator] {len(failed_books)} 책 FAIL</b>"]
        for name, fails in failed_books[:10]:
            lines.append(f"\n<b>{name}</b>")
            for f in fails[:6]:
                lines.append(f"  - {f}")
            if len(fails) > 6:
                lines.append(f"  ... +{len(fails)-6} more")
        text = "\n".join(lines)
        sent = _send_telegram(token, chat_id, text)
        print(f"[telegram] sent={sent}")

    return 0 if not failed_books else 2


if __name__ == "__main__":
    sys.exit(main())
