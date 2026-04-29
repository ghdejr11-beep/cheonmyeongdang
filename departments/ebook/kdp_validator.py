#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDP Validator — Kindle Direct Publishing 거절 방지 자동 검증기
==================================================================
저자: KunStudio (홍덕훈)
규칙 출처: departments/ebook/KDP_RULES.md, MEMORY[KDP 거절 방지]

검증 항목
  1. 표지 PDF (validate_cover)
     - 금지 키워드(template, placeholder, lorem)
     - dimension 6x9 또는 8.5x11 인치
     - 300 DPI 이상 권장
  2. 본문 PDF (validate_interior)
     - 24 ~ 828 페이지
     - spine margin 0.5 인치 이상 (gutter)
  3. 메타데이터 manifest.json (validate_metadata)
     - author == "Deokgu Studio"
     - title 200자 미만
     - description 4000자 미만
     - keywords <= 7
     - categories <= 2
     - ISBN 중복 검사 (published_books.json DB 사용)

CLI
  python kdp_validator.py --book-dir <path> [--strict]
  python kdp_validator.py --self-test

Author: 쿤스튜디오 (Deokgu Studio) · 2026-04-26
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

# ---- PDF backend ---------------------------------------------------------
try:
    import fitz  # PyMuPDF
    _PDF_BACKEND = "pymupdf"
except ImportError:
    try:
        from PyPDF2 import PdfReader  # type: ignore
        _PDF_BACKEND = "pypdf2"
    except ImportError:
        _PDF_BACKEND = None

# ---- Constants -----------------------------------------------------------
REQUIRED_AUTHOR = "Deokgu Studio"
FORBIDDEN_KEYWORDS = ["template", "placeholder", "lorem", "ipsum", "sample text"]
ALLOWED_TRIM_INCHES = [(6.0, 9.0), (8.5, 11.0), (5.0, 8.0), (5.5, 8.5), (7.0, 10.0)]
TARGET_TRIM_INCHES = [(6.0, 9.0), (8.5, 11.0)]  # 우선 권장
PAGE_MIN, PAGE_MAX = 24, 828
SPINE_MARGIN_INCHES = 0.5  # 0.5"
TITLE_MAX = 200
DESC_MAX = 4000
KEYWORDS_MAX = 7
CATEGORIES_MAX = 2
DPI_MIN = 300
TRIM_TOLERANCE = 0.05  # 인치

DB_FILE_DEFAULT = "published_books.json"


# ---- Result types --------------------------------------------------------
@dataclass
class CheckItem:
    name: str
    status: str   # "PASS" | "FAIL" | "WARN" | "SKIP"
    message: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ValidationReport:
    book_dir: str
    timestamp: str
    overall: str = "PASS"   # PASS / FAIL / WARN
    cover: list[CheckItem] = field(default_factory=list)
    interior: list[CheckItem] = field(default_factory=list)
    metadata: list[CheckItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add(self, section: str, item: CheckItem) -> None:
        getattr(self, section).append(item)
        if item.status == "FAIL":
            self.overall = "FAIL"
        elif item.status == "WARN" and self.overall == "PASS":
            self.overall = "WARN"

    def to_dict(self) -> dict:
        return {
            "book_dir": self.book_dir,
            "timestamp": self.timestamp,
            "overall": self.overall,
            "cover": [c.to_dict() for c in self.cover],
            "interior": [c.to_dict() for c in self.interior],
            "metadata": [c.to_dict() for c in self.metadata],
            "errors": self.errors,
        }


# ---- PDF helpers ---------------------------------------------------------
def _pts_to_inches(pts: float) -> float:
    return pts / 72.0


def _read_pdf_info(pdf_path: Path) -> dict:
    """Return {pages, width_in, height_in, text_first_pages, has_images, dpi_estimate}."""
    if _PDF_BACKEND == "pymupdf":
        doc = fitz.open(pdf_path)
        try:
            pages = doc.page_count
            page0 = doc.load_page(0)
            w_in = _pts_to_inches(page0.rect.width)
            h_in = _pts_to_inches(page0.rect.height)
            text_chunks: list[str] = []
            for i in range(min(pages, 5)):
                text_chunks.append(doc.load_page(i).get_text("text") or "")
            # DPI estimate: largest embedded image relative to page size
            dpi_est = 0
            try:
                imgs = page0.get_images(full=True)
                for img in imgs:
                    xref = img[0]
                    info = doc.extract_image(xref)
                    iw, ih = info.get("width", 0), info.get("height", 0)
                    if iw and page0.rect.width:
                        candidate = iw / max(_pts_to_inches(page0.rect.width), 0.01)
                        dpi_est = max(dpi_est, int(candidate))
                    if ih and page0.rect.height:
                        candidate = ih / max(_pts_to_inches(page0.rect.height), 0.01)
                        dpi_est = max(dpi_est, int(candidate))
            except Exception:
                pass
            return {
                "pages": pages,
                "width_in": w_in,
                "height_in": h_in,
                "text": "\n".join(text_chunks),
                "dpi_estimate": dpi_est,
            }
        finally:
            doc.close()
    elif _PDF_BACKEND == "pypdf2":
        reader = PdfReader(str(pdf_path))
        pages = len(reader.pages)
        page0 = reader.pages[0]
        box = page0.mediabox
        w_in = _pts_to_inches(float(box.width))
        h_in = _pts_to_inches(float(box.height))
        text_chunks = []
        for i in range(min(pages, 5)):
            try:
                text_chunks.append(reader.pages[i].extract_text() or "")
            except Exception:
                pass
        return {
            "pages": pages,
            "width_in": w_in,
            "height_in": h_in,
            "text": "\n".join(text_chunks),
            "dpi_estimate": 0,
        }
    raise RuntimeError("PDF backend not installed (need PyMuPDF or PyPDF2).")


def _approx(a: float, b: float, tol: float = TRIM_TOLERANCE) -> bool:
    return abs(a - b) <= tol


def _trim_matches(width_in: float, height_in: float, trims: list[tuple[float, float]]) -> tuple[float, float] | None:
    for w, h in trims:
        if _approx(width_in, w) and _approx(height_in, h):
            return (w, h)
        if _approx(width_in, h) and _approx(height_in, w):  # 가로 표지 등
            return (w, h)
    return None


# ---- Section validators --------------------------------------------------
def validate_cover(pdf_path: Path, report: ValidationReport, strict: bool = False) -> None:
    if not pdf_path.exists():
        report.add("cover", CheckItem("cover.pdf 존재", "FAIL", f"파일 없음: {pdf_path}"))
        return
    try:
        info = _read_pdf_info(pdf_path)
    except Exception as e:
        report.add("cover", CheckItem("cover.pdf 읽기", "FAIL", f"PDF 읽기 실패: {e}"))
        return

    # 1) Forbidden keywords
    text_lc = info["text"].lower()
    hits = [kw for kw in FORBIDDEN_KEYWORDS if kw in text_lc]
    if hits:
        report.add("cover", CheckItem(
            "표지 금지 키워드", "FAIL",
            f"발견된 템플릿 잔재: {', '.join(hits)}",
        ))
    else:
        report.add("cover", CheckItem("표지 금지 키워드", "PASS", "lorem/template/placeholder 없음"))

    # 2) Trim size
    trims = TARGET_TRIM_INCHES if strict else ALLOWED_TRIM_INCHES
    matched = _trim_matches(info["width_in"], info["height_in"], trims)
    if matched:
        report.add("cover", CheckItem(
            "표지 dimension", "PASS",
            f"{info['width_in']:.2f}x{info['height_in']:.2f} in (matched {matched[0]}x{matched[1]})",
        ))
    else:
        sev = "FAIL" if strict else "WARN"
        report.add("cover", CheckItem(
            "표지 dimension", sev,
            f"비표준 trim {info['width_in']:.2f}x{info['height_in']:.2f} in (허용: 6x9, 8.5x11 등)",
        ))

    # 3) DPI estimate
    dpi = info.get("dpi_estimate", 0)
    if dpi >= DPI_MIN:
        report.add("cover", CheckItem("표지 DPI", "PASS", f"~{dpi} DPI"))
    elif dpi == 0:
        report.add("cover", CheckItem(
            "표지 DPI", "WARN",
            "DPI 추정 불가 (이미지 미발견 또는 PyPDF2 백엔드)",
        ))
    else:
        sev = "FAIL" if strict else "WARN"
        report.add("cover", CheckItem(
            "표지 DPI", sev,
            f"~{dpi} DPI (권장 300 미달)",
        ))


def validate_interior(pdf_path: Path, report: ValidationReport, strict: bool = False) -> None:
    if not pdf_path.exists():
        report.add("interior", CheckItem("interior.pdf 존재", "FAIL", f"파일 없음: {pdf_path}"))
        return
    try:
        info = _read_pdf_info(pdf_path)
    except Exception as e:
        report.add("interior", CheckItem("interior.pdf 읽기", "FAIL", f"PDF 읽기 실패: {e}"))
        return

    # 1) Page count
    pages = info["pages"]
    if PAGE_MIN <= pages <= PAGE_MAX:
        report.add("interior", CheckItem("본문 페이지 수", "PASS", f"{pages} pages"))
    else:
        report.add("interior", CheckItem(
            "본문 페이지 수", "FAIL",
            f"{pages} pages (KDP 허용 {PAGE_MIN}~{PAGE_MAX})",
        ))

    # 2) Spine / gutter margin — heuristic via text bbox
    margin_in = _estimate_inner_margin(pdf_path)
    if margin_in is None:
        report.add("interior", CheckItem(
            "spine margin", "WARN",
            "본문 텍스트 bbox 추정 불가 (이미지만 있거나 빈 페이지)",
        ))
    elif margin_in >= SPINE_MARGIN_INCHES - 0.02:
        report.add("interior", CheckItem(
            "spine margin", "PASS",
            f"내측 여백 ~{margin_in:.2f}\" (>= 0.5\")",
        ))
    else:
        sev = "FAIL" if strict else "WARN"
        report.add("interior", CheckItem(
            "spine margin", sev,
            f"내측 여백 ~{margin_in:.2f}\" (KDP 권장 0.5\" 미만)",
        ))


def _estimate_inner_margin(pdf_path: Path) -> float | None:
    """Estimate inner (gutter) margin in inches by inspecting text bboxes on first text-bearing page."""
    if _PDF_BACKEND != "pymupdf":
        return None
    doc = fitz.open(pdf_path)
    try:
        for i in range(min(doc.page_count, 8)):
            page = doc.load_page(i)
            blocks = page.get_text("blocks") or []
            text_blocks = [b for b in blocks if b[4] and b[4].strip()]
            if not text_blocks:
                continue
            page_w = page.rect.width
            min_left = min(b[0] for b in text_blocks)
            max_right = max(b[2] for b in text_blocks)
            # KDP은 홀/짝 페이지 공통이며 spine은 내측이므로 좌·우 중 작은 값을 보수적으로 채택
            left_margin_in = _pts_to_inches(min_left)
            right_margin_in = _pts_to_inches(page_w - max_right)
            return min(left_margin_in, right_margin_in)
        return None
    finally:
        doc.close()


def validate_metadata(manifest_path: Path, report: ValidationReport, db_path: Path | None = None) -> None:
    if not manifest_path.exists():
        report.add("metadata", CheckItem("manifest.json 존재", "FAIL", f"파일 없음: {manifest_path}"))
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        report.add("metadata", CheckItem("manifest.json 파싱", "FAIL", f"JSON 파싱 실패: {e}"))
        return

    # author
    author = manifest.get("author", "").strip()
    if author == REQUIRED_AUTHOR:
        report.add("metadata", CheckItem("저자명", "PASS", f"'{author}'"))
    else:
        report.add("metadata", CheckItem(
            "저자명", "FAIL",
            f"'{author}' (반드시 '{REQUIRED_AUTHOR}')",
        ))

    # title
    title = manifest.get("title", "")
    if 0 < len(title) < TITLE_MAX:
        report.add("metadata", CheckItem("title 길이", "PASS", f"{len(title)} chars"))
    else:
        report.add("metadata", CheckItem(
            "title 길이", "FAIL",
            f"{len(title)} chars (1~{TITLE_MAX-1} 허용)",
        ))

    # description
    desc = manifest.get("description", "")
    if 0 < len(desc) < DESC_MAX:
        report.add("metadata", CheckItem("description 길이", "PASS", f"{len(desc)} chars"))
    else:
        report.add("metadata", CheckItem(
            "description 길이", "FAIL",
            f"{len(desc)} chars (1~{DESC_MAX-1} 허용)",
        ))

    # keywords
    keywords = manifest.get("keywords", []) or []
    if isinstance(keywords, list) and len(keywords) <= KEYWORDS_MAX:
        report.add("metadata", CheckItem("keywords 개수", "PASS", f"{len(keywords)} keywords"))
    else:
        report.add("metadata", CheckItem(
            "keywords 개수", "FAIL",
            f"{len(keywords) if isinstance(keywords, list) else 'invalid'} (max {KEYWORDS_MAX})",
        ))

    # categories
    categories = manifest.get("categories", []) or []
    if isinstance(categories, list) and len(categories) <= CATEGORIES_MAX:
        report.add("metadata", CheckItem("categories 개수", "PASS", f"{len(categories)} categories"))
    else:
        report.add("metadata", CheckItem(
            "categories 개수", "FAIL",
            f"{len(categories) if isinstance(categories, list) else 'invalid'} (max {CATEGORIES_MAX})",
        ))

    # ISBN duplicate check
    isbn = (manifest.get("isbn") or "").strip()
    if not isbn:
        report.add("metadata", CheckItem("ISBN", "WARN", "manifest에 ISBN 없음 (KDP 자동 ASIN이면 무시)"))
    else:
        normalized = re.sub(r"[^0-9Xx]", "", isbn).upper()
        if not (len(normalized) in (10, 13)):
            report.add("metadata", CheckItem("ISBN 형식", "FAIL", f"'{isbn}' (10 or 13자리 필요)"))
        else:
            db_path = db_path or (manifest_path.parent.parent.parent / DB_FILE_DEFAULT)
            existing = _load_db(db_path)
            current_book_id = manifest.get("book_id") or manifest_path.parent.name
            dup = next(
                (e for e in existing if e.get("isbn") == normalized and e.get("book_id") != current_book_id),
                None,
            )
            if dup:
                report.add("metadata", CheckItem(
                    "ISBN 중복", "FAIL",
                    f"이미 등록됨: book_id={dup.get('book_id')} title={dup.get('title')!r}",
                ))
            else:
                report.add("metadata", CheckItem("ISBN 중복", "PASS", f"{normalized} unique"))


def _load_db(db_path: Path) -> list[dict]:
    if not db_path.exists():
        return []
    try:
        data = json.loads(db_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_db(db_path: Path, entries: list[dict]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def register_book(manifest_path: Path, db_path: Path | None = None) -> None:
    """검증 통과 책을 published_books.json DB에 등록 (ISBN 중복 추적)."""
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    isbn = (manifest.get("isbn") or "").strip()
    if not isbn:
        return
    normalized = re.sub(r"[^0-9Xx]", "", isbn).upper()
    db_path = db_path or (manifest_path.parent.parent.parent / DB_FILE_DEFAULT)
    entries = _load_db(db_path)
    book_id = manifest.get("book_id") or manifest_path.parent.name
    if any(e.get("book_id") == book_id for e in entries):
        # update
        for e in entries:
            if e.get("book_id") == book_id:
                e["isbn"] = normalized
                e["title"] = manifest.get("title", "")
                e["registered_at"] = datetime.now().isoformat(timespec="seconds")
    else:
        entries.append({
            "book_id": book_id,
            "isbn": normalized,
            "title": manifest.get("title", ""),
            "author": manifest.get("author", ""),
            "registered_at": datetime.now().isoformat(timespec="seconds"),
        })
    _save_db(db_path, entries)


# ---- Orchestration -------------------------------------------------------
def load_book_dir(book_dir: Path) -> dict:
    """책 디렉터리에서 표지/본문/manifest 경로를 찾아 반환."""
    book_dir = Path(book_dir)
    candidates = {
        "cover": ["cover.pdf", "cover_print.pdf", "cover_kdp.pdf"],
        "interior": [
            "interior.pdf", "interior_print.pdf", "Interior.pdf",
            f"{book_dir.name}_Interior.pdf",
        ],
        "manifest": ["manifest.json", "kdp_manifest.json"],
    }
    found: dict[str, Path | None] = {"cover": None, "interior": None, "manifest": None}
    for kind, names in candidates.items():
        for n in names:
            p = book_dir / n
            if p.exists():
                found[kind] = p
                break
        if found[kind] is None:
            # fallback: 첫 번째 매칭
            if kind == "interior":
                ints = sorted(book_dir.glob("*Interior*.pdf"))
                if ints:
                    found[kind] = ints[0]
            elif kind == "cover":
                covers = sorted(book_dir.glob("cover*.pdf"))
                if covers:
                    found[kind] = covers[0]
    return found


def save_validation_report(report: ValidationReport, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validate_book(book_dir: Path, strict: bool = False, db_path: Path | None = None) -> ValidationReport:
    book_dir = Path(book_dir)
    report = ValidationReport(
        book_dir=str(book_dir.resolve()),
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )
    if not book_dir.exists():
        report.errors.append(f"book_dir 없음: {book_dir}")
        report.overall = "FAIL"
        return report

    paths = load_book_dir(book_dir)

    if paths["cover"]:
        validate_cover(paths["cover"], report, strict=strict)
    else:
        report.add("cover", CheckItem("cover.pdf 존재", "FAIL", "cover*.pdf 미발견"))

    if paths["interior"]:
        validate_interior(paths["interior"], report, strict=strict)
    else:
        report.add("interior", CheckItem("interior.pdf 존재", "FAIL", "*Interior*.pdf 미발견"))

    if paths["manifest"]:
        validate_metadata(paths["manifest"], report, db_path=db_path)
    else:
        report.add("metadata", CheckItem("manifest.json 존재", "FAIL", "manifest.json 미발견"))

    return report


def _pretty_print(report: ValidationReport) -> None:
    icon = {"PASS": "[OK]", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[--]"}
    print(f"\n=== KDP Validation: {report.book_dir} ===")
    print(f"timestamp: {report.timestamp}")
    print(f"OVERALL  : {icon.get(report.overall, '?')} {report.overall}")
    for section in ("cover", "interior", "metadata"):
        items = getattr(report, section)
        if not items:
            continue
        print(f"\n[{section.upper()}]")
        for it in items:
            print(f"  {icon.get(it.status, '?')} {it.name:<24} {it.message}")
    if report.errors:
        print("\n[ERRORS]")
        for e in report.errors:
            print(f"  - {e}")


# ---- Self-test -----------------------------------------------------------
def _make_pdf(path: Path, width_in: float, height_in: float, pages: int,
              text: str = "Body text.", left_margin_in: float = 0.75) -> None:
    """PyMuPDF로 더미 PDF 생성. text는 첫 페이지에 들어감."""
    if _PDF_BACKEND != "pymupdf":
        raise RuntimeError("self-test requires PyMuPDF")
    doc = fitz.open()
    w_pt, h_pt = width_in * 72, height_in * 72
    for i in range(pages):
        page = doc.new_page(width=w_pt, height=h_pt)
        x = left_margin_in * 72
        y = 1.0 * 72
        page.insert_text((x, y), text if i == 0 else f"Page {i+1}", fontsize=11)
    doc.save(str(path))
    doc.close()


def run_self_test() -> bool:
    if _PDF_BACKEND != "pymupdf":
        print("[self-test] PyMuPDF 필요. skip.")
        return False

    tmp = Path(tempfile.mkdtemp(prefix="kdp_validator_test_"))
    db_path = tmp / "published_books.json"
    overall_ok = True
    try:
        # ---- PASS book ----
        good = tmp / "good-book"
        good.mkdir()
        _make_pdf(good / "cover.pdf", 6.0, 9.0, 1, text="Awesome Title by Deokgu Studio")
        _make_pdf(good / "interior.pdf", 6.0, 9.0, 100, text="Chapter 1 — Hello World",
                  left_margin_in=0.75)
        (good / "manifest.json").write_text(json.dumps({
            "book_id": "good-book",
            "title": "Good Book Title",
            "author": "Deokgu Studio",
            "description": "A solid description of the book." * 10,
            "keywords": ["a", "b", "c", "d"],
            "categories": ["Self-Help", "Productivity"],
            "isbn": "9781234567897",
        }, ensure_ascii=False), encoding="utf-8")

        good_report = validate_book(good, strict=False, db_path=db_path)
        _pretty_print(good_report)
        assert good_report.overall in ("PASS", "WARN"), \
            f"good-book should PASS or WARN, got {good_report.overall}"
        register_book(good / "manifest.json", db_path=db_path)
        print(f"[self-test] PASS case overall = {good_report.overall}")

        # ---- FAIL book (template text + bad author + ISBN dup + thin margin + few pages) ----
        bad = tmp / "bad-book"
        bad.mkdir()
        _make_pdf(bad / "cover.pdf", 6.0, 9.0, 1, text="LOREM IPSUM placeholder TEMPLATE")
        _make_pdf(bad / "interior.pdf", 6.0, 9.0, 10, text="Hi",
                  left_margin_in=0.20)  # 0.20" < 0.5"
        (bad / "manifest.json").write_text(json.dumps({
            "book_id": "bad-book",
            "title": "Bad Book",
            "author": "Random Person",  # 잘못된 저자
            "description": "x",
            "keywords": ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8", "k9"],  # 9개
            "categories": ["A", "B", "C"],  # 3개
            "isbn": "9781234567897",  # good-book과 중복
        }, ensure_ascii=False), encoding="utf-8")

        bad_report = validate_book(bad, strict=True, db_path=db_path)
        _pretty_print(bad_report)
        assert bad_report.overall == "FAIL", \
            f"bad-book should FAIL, got {bad_report.overall}"
        # 구체 항목 확인
        all_items = bad_report.cover + bad_report.interior + bad_report.metadata
        names_failed = {it.name for it in all_items if it.status == "FAIL"}
        expected_failures = {
            "표지 금지 키워드", "본문 페이지 수", "spine margin",
            "저자명", "keywords 개수", "categories 개수", "ISBN 중복",
        }
        missing = expected_failures - names_failed
        if missing:
            print(f"[self-test] WARN — 예상 FAIL인데 안 잡힘: {missing}")
            overall_ok = False
        print(f"[self-test] FAIL case overall = {bad_report.overall} "
              f"(failed checks: {len(names_failed)})")

        # ---- save reports ----
        save_validation_report(good_report, tmp / "good_report.json")
        save_validation_report(bad_report, tmp / "bad_report.json")
        print(f"[self-test] reports saved to {tmp}")

        return overall_ok
    finally:
        # 결과 디렉터리는 디버그를 위해 그대로 남김 (필요시 주석 해제)
        # shutil.rmtree(tmp, ignore_errors=True)
        print(f"[self-test] tmp dir kept at: {tmp}")


# ---- CLI -----------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="KDP 거절 방지 자동 검증기")
    parser.add_argument("--book-dir", type=str, help="검증할 책 디렉터리 (cover.pdf, interior.pdf, manifest.json 포함)")
    parser.add_argument("--strict", action="store_true", help="WARN을 FAIL로 격상")
    parser.add_argument("--db", type=str, default=None, help="published_books.json 경로")
    parser.add_argument("--report", type=str, default=None, help="JSON report 출력 경로")
    parser.add_argument("--register", action="store_true", help="검증 통과 시 published_books.json에 등록")
    parser.add_argument("--self-test", action="store_true", help="더미 데이터로 self-test 실행")
    args = parser.parse_args()

    if args.self_test:
        ok = run_self_test()
        return 0 if ok else 1

    if not args.book_dir:
        parser.error("--book-dir 또는 --self-test 필요")

    book_dir = Path(args.book_dir)
    db_path = Path(args.db) if args.db else None

    report = validate_book(book_dir, strict=args.strict, db_path=db_path)
    _pretty_print(report)

    if args.report:
        save_validation_report(report, Path(args.report))
        print(f"\nreport saved → {args.report}")

    if args.register and report.overall != "FAIL":
        manifest = book_dir / "manifest.json"
        if manifest.exists():
            register_book(manifest, db_path=db_path)
            print(f"registered to DB → {db_path or 'default'}")

    return 0 if report.overall != "FAIL" else 2


if __name__ == "__main__":
    sys.exit(main())
