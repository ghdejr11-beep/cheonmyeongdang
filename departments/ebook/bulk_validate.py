#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk KDP Validator — 27권 일괄 검증 + Telegram 알림
====================================================
- 모든 projects/* 폴더에 kdp_validator.validate_book() 실행
- PASS / FAIL / WARN 카운트 요약
- FAIL이 있으면 Telegram으로 알림 발송 (.secrets에서 TELEGRAM_BOT_TOKEN 로드)
- JSON 결과 보고서 저장: validation_summary.json

Usage
  python bulk_validate.py
  python bulk_validate.py --strict --notify

Author: 쿤스튜디오 (Deokgu Studio) · 2026-04-26
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# kdp_validator 모듈 임포트
THIS_DIR = Path(__file__).parent.resolve()
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from kdp_validator import (  # type: ignore  # noqa: E402
    validate_book,
    ValidationReport,
    validate_cover,
    validate_interior,
    validate_metadata,
    load_book_dir,
    CheckItem,
)


def _find_interior_via_manifest(book_dir: Path) -> Path | None:
    """manifest.json의 interior_pdf 필드 또는 휴리스틱(가장 큰 비표지 PDF)으로 본문 추정."""
    manifest_path = book_dir / "manifest.json"
    if manifest_path.exists():
        try:
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            name = (m.get("interior_pdf") or "").strip()
            if name:
                p = book_dir / name
                if p.exists():
                    return p
        except Exception:
            pass
    # fallback: 가장 큰 비표지 PDF
    candidates = []
    for pdf in book_dir.glob("*.pdf"):
        n = pdf.name.lower()
        if n.startswith("cover") or "kdp_cover" in n:
            continue
        candidates.append(pdf)
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_size, reverse=True)
    return candidates[0]


def _find_cover_via_manifest(book_dir: Path) -> Path | None:
    manifest_path = book_dir / "manifest.json"
    if manifest_path.exists():
        try:
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            name = (m.get("cover_pdf") or "").strip()
            if name:
                p = book_dir / name
                if p.exists():
                    return p
        except Exception:
            pass
    for cand in ("cover.pdf", "cover_print.pdf", "cover_kdp.pdf"):
        p = book_dir / cand
        if p.exists():
            return p
    covers = sorted(book_dir.glob("cover*.pdf"))
    return covers[0] if covers else None


def _validate_book_resolved(book_dir: Path, strict: bool, db_path: Path | None) -> ValidationReport:
    """kdp_validator.validate_book의 manifest 인지(awareness) 래퍼."""
    report = ValidationReport(
        book_dir=str(book_dir.resolve()),
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )
    if not book_dir.exists():
        report.errors.append(f"book_dir 없음: {book_dir}")
        report.overall = "FAIL"
        return report

    cover = _find_cover_via_manifest(book_dir)
    interior = _find_interior_via_manifest(book_dir)
    manifest = book_dir / "manifest.json"

    if cover:
        validate_cover(cover, report, strict=strict)
    else:
        report.add("cover", CheckItem("cover.pdf 존재", "FAIL", "cover*.pdf 미발견"))

    if interior:
        validate_interior(interior, report, strict=strict)
    else:
        report.add("interior", CheckItem("interior.pdf 존재", "FAIL", "interior PDF 미발견"))

    if manifest.exists():
        validate_metadata(manifest, report, db_path=db_path)
    else:
        report.add("metadata", CheckItem("manifest.json 존재", "FAIL", "manifest.json 미발견"))

    return report


SECRETS_CANDIDATES = [
    THIS_DIR / ".secrets",
    THIS_DIR.parent.parent / ".secrets",  # cheonmyeongdang/.secrets
    Path.home() / ".secrets",
]


def load_secrets() -> dict[str, str]:
    """단순 KEY=VALUE 형식 .secrets 파일 로드."""
    for path in SECRETS_CANDIDATES:
        if not path.exists():
            continue
        out: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip().strip('"').strip("'")
        return out
    return {}


def telegram_notify(token: str, chat_id: str, message: str) -> bool:
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": "kunstudio-kdp-validator/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[telegram] FAILED: {e}")
        return False


def collect_failed_items(report: ValidationReport) -> list[str]:
    """FAIL 항목들의 사람 친화적 라벨 리스트."""
    out: list[str] = []
    for section in ("cover", "interior", "metadata"):
        for item in getattr(report, section):
            if item.status == "FAIL":
                out.append(f"{section}.{item.name}: {item.message}")
    return out


def run(projects_dir: Path, strict: bool, notify: bool) -> dict:
    folders = sorted([p for p in projects_dir.iterdir()
                      if p.is_dir() and p.name != "__pycache__"])
    db_path = projects_dir.parent / "published_books.json"

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    detail = []
    fail_books: list[dict] = []

    for book_dir in folders:
        report = _validate_book_resolved(book_dir, strict=strict, db_path=db_path)
        counts[report.overall] = counts.get(report.overall, 0) + 1
        d = {
            "book": book_dir.name,
            "overall": report.overall,
            "cover": [it.to_dict() for it in report.cover],
            "interior": [it.to_dict() for it in report.interior],
            "metadata": [it.to_dict() for it in report.metadata],
        }
        detail.append(d)
        if report.overall == "FAIL":
            fail_books.append({
                "book": book_dir.name,
                "failures": collect_failed_items(report),
            })

    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total": len(folders),
        "counts": counts,
        "fail_books": fail_books,
        "detail": detail,
    }

    # Save report
    report_path = projects_dir.parent / "validation_summary.json"
    report_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Print summary
    print("\n" + "=" * 56)
    print(f"KDP Bulk Validation - {summary['timestamp']}")
    print("=" * 56)
    print(f"total : {summary['total']}")
    print(f"PASS  : {counts['PASS']}")
    print(f"WARN  : {counts['WARN']}")
    print(f"FAIL  : {counts['FAIL']}")
    print(f"report saved → {report_path}")

    if fail_books:
        print(f"\n[FAILED BOOKS] ({len(fail_books)})")
        for fb in fail_books:
            print(f"\n  - {fb['book']}")
            for line in fb["failures"][:6]:
                print(f"      • {line}")
            if len(fb["failures"]) > 6:
                print(f"      … (+{len(fb['failures']) - 6} more)")

    # Telegram notify if FAIL exists
    if notify and fail_books:
        secrets = load_secrets()
        token = secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = secrets.get("TELEGRAM_CHAT_ID", "")
        if token and chat_id:
            lines = [
                "*[KDP Validator] FAIL 발생*",
                f"_{summary['timestamp']}_",
                "",
                f"PASS: {counts['PASS']}  WARN: {counts['WARN']}  *FAIL: {counts['FAIL']}*",
                f"총 {summary['total']}권 중 {len(fail_books)}권 거절 위험",
                "",
                "*FAIL 책 목록:*",
            ]
            for fb in fail_books[:10]:
                lines.append(f"• `{fb['book']}` ({len(fb['failures'])} issues)")
            if len(fail_books) > 10:
                lines.append(f"… 외 {len(fail_books) - 10}권")
            msg = "\n".join(lines)
            ok = telegram_notify(token, chat_id, msg)
            print(f"\n[telegram] notify {'OK' if ok else 'FAILED'}")
        else:
            print("\n[telegram] TELEGRAM_BOT_TOKEN / CHAT_ID 미설정 → 알림 스킵")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="KDP 27권 일괄 검증 + Telegram 알림")
    parser.add_argument(
        "--projects-dir",
        type=str,
        default=str(THIS_DIR / "projects"),
    )
    parser.add_argument("--strict", action="store_true", help="WARN을 FAIL로 격상")
    parser.add_argument("--notify", action="store_true", default=True,
                        help="FAIL 발생 시 Telegram 알림 (기본 ON)")
    parser.add_argument("--no-notify", dest="notify", action="store_false")
    args = parser.parse_args()

    projects_dir = Path(args.projects_dir)
    if not projects_dir.exists():
        print(f"[ERROR] projects-dir 없음: {projects_dir}")
        return 2

    summary = run(projects_dir, strict=args.strict, notify=args.notify)
    return 0 if summary["counts"]["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
