"""
apply_genre_colors.py
=====================
장르 색상 매핑(genre_color_map.json) → generate_all_covers.py BOOKS 색상 인자 override
표지를 장르별 색심리학 색상으로 일괄 재생성.

동작:
  1) genre_color_map.json 로드 → folder→(primary, secondary) dict 빌드
  2) generate_all_covers.BOOKS 순회 (튜플 unpack)
  3) 각 책별 cover.pdf 백업 → cover_v_pre_genre.pdf
  4) make_cover() 호출 시 bg_hex/accent_hex 만 genre 색으로 override
  5) 실패 책은 logs/genre_recolor.log 에 기록

옵션:
  --test            : 첫 1권만 dry run (백업 없이 dry_run 폴더로 출력)
  --book=<folder>   : 특정 1권만 처리
  --no-validate     : dual-scale PNG 검증 스킵
  --force           : 이미 백업이 있어도 다시 백업 (기존 백업 보존됨, 새 backup_v2)

산출:
  - {book}/cover.pdf (새 표지)
  - {book}/cover_v_pre_genre.pdf (백업)
  - {book}/_genre_thumb_200x300.png (썸네일 검증, --no-validate 미사용 시)
  - {book}/_genre_full_1600x2400.png (풀사이즈 미리보기, 옵션)
  - logs/genre_recolor.log
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
ROOT = BASE.parent  # departments/ebook
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_PATH = LOG_DIR / "genre_recolor.log"

# generate_all_covers 를 모듈로 import (sibling)
sys.path.insert(0, str(BASE))
import generate_all_covers as gac  # noqa: E402


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_genre_map() -> dict:
    """genre_color_map.json 로드 → folder name → (primary, secondary) dict."""
    path = BASE / "genre_color_map.json"
    if not path.exists():
        raise FileNotFoundError(f"genre_color_map.json missing: {path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    folder_to_colors: dict[str, tuple[str, str, str]] = {}
    for genre_key, genre in data["genres"].items():
        primary = genre["primary"]
        secondary = genre["secondary"]
        for book_folder in genre.get("books", []):
            folder_to_colors[book_folder] = (primary, secondary, genre_key)
    return folder_to_colors


def backup_cover(folder: Path) -> Path | None:
    """기존 cover.pdf 를 cover_v_pre_genre.pdf 로 백업. 이미 있으면 그대로 둠."""
    src = folder / "cover.pdf"
    if not src.exists():
        return None
    dst = folder / "cover_v_pre_genre.pdf"
    if dst.exists():
        # 이미 백업됨 - 보존 (재실행 시 원본 잃지 않음)
        return dst
    shutil.copy2(src, dst)
    return dst


def render_validation_pngs(pdf_path: Path, out_dir: Path) -> tuple[bool, str]:
    """PDF 첫 페이지 → 200x300 thumbnail + 1600x2400 full size PNG.
    PyMuPDF(fitz) 우선 시도, 실패 시 pdf2image fallback.
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(pdf_path))
        page = doc[0]
        # full size (1600x2400 target)
        rect = page.rect
        zoom_x = 1600 / rect.width
        zoom_y = 2400 / rect.height
        zoom = min(zoom_x, zoom_y)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        full_png = out_dir / "_genre_full_1600x2400.png"
        pix.save(str(full_png))

        # thumbnail
        zoom_t = min(200 / rect.width, 300 / rect.height)
        pix_t = page.get_pixmap(matrix=fitz.Matrix(zoom_t, zoom_t), alpha=False)
        thumb_png = out_dir / "_genre_thumb_200x300.png"
        pix_t.save(str(thumb_png))
        doc.close()
        return True, "fitz"
    except Exception as e_fitz:
        try:
            from pdf2image import convert_from_path

            imgs = convert_from_path(str(pdf_path), dpi=150, first_page=1, last_page=1)
            if not imgs:
                return False, f"pdf2image: empty (fitz: {e_fitz})"
            img = imgs[0]
            full = img.resize((1600, 2400))
            full.save(out_dir / "_genre_full_1600x2400.png", "PNG")
            thumb = img.resize((200, 300))
            thumb.save(out_dir / "_genre_thumb_200x300.png", "PNG")
            return True, "pdf2image"
        except Exception as e_p2i:
            return False, f"fitz: {e_fitz} | pdf2image: {e_p2i}"


def process_book(
    book_tuple: tuple,
    folder_to_colors: dict,
    *,
    dry_run: bool = False,
    validate: bool = True,
) -> dict:
    """generate_all_covers.BOOKS 의 한 항목 처리.

    book_tuple: (folder, size, bg_hex, accent_hex, title_lines, subtitle_lines, decor_fn, title_size)
    return: {folder, status, genre, old_bg, new_bg, ...}
    """
    folder, size, bg_hex, accent_hex, titles, subs, decor, tsize = book_tuple
    result: dict = {
        "folder": folder,
        "old_bg": bg_hex,
        "old_accent": accent_hex,
        "status": "pending",
    }

    if folder not in folder_to_colors:
        result["status"] = "skipped_no_genre"
        log(f"  [skip] {folder} - genre map에 없음")
        return result

    new_bg, new_accent, genre_key = folder_to_colors[folder]
    result.update({"new_bg": new_bg, "new_accent": new_accent, "genre": genre_key})

    book_dir = BASE / folder
    if not book_dir.exists():
        result["status"] = "missing_folder"
        log(f"  [FAIL] {folder} - 폴더 없음")
        return result

    target_filename = "cover.pdf"
    out_dir = book_dir
    if dry_run:
        out_dir = book_dir / "_dry_run"
        out_dir.mkdir(exist_ok=True)
        target_filename = "cover_genre_test.pdf"
    else:
        # 백업
        bk = backup_cover(book_dir)
        if bk:
            log(f"  [backup] {folder}/cover.pdf -> {bk.name}")

    try:
        # make_cover 는 BASE / folder / filename 으로 저장하므로 folder 인자에 상대경로 전달
        rel_folder = folder if not dry_run else f"{folder}/_dry_run"
        gac.make_cover(
            rel_folder,
            target_filename,
            size,
            new_bg,
            new_accent,
            titles,
            subs,
            decor,
            tsize,
        )
        produced = book_dir / target_filename if not dry_run else out_dir / target_filename
        result["pdf"] = str(produced)
        result["status"] = "ok"

        if validate and produced.exists():
            ok, engine = render_validation_pngs(produced, out_dir)
            result["validate"] = engine if ok else f"FAIL: {engine}"

        log(f"  [OK]   {folder} ({genre_key}) bg {bg_hex}->{new_bg}, accent {accent_hex}->{new_accent}")
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        log(f"  [FAIL] {folder}: {e}")
        log(traceback.format_exc())

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="장르 색상 일괄 적용 표지 재생성기")
    parser.add_argument("--test", action="store_true", help="첫 1권만 dry run (cover.pdf 건드리지 않음)")
    parser.add_argument("--book", type=str, default=None, help="특정 1권만 처리 (folder 이름)")
    parser.add_argument("--no-validate", action="store_true", help="PNG 검증 스킵")
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="콤마구분 제외 폴더명 (KDP 거절 위험 책 등)",
    )
    args = parser.parse_args()

    log("=" * 60)
    log(f"apply_genre_colors START (test={args.test}, book={args.book})")
    log("=" * 60)

    folder_to_colors = load_genre_map()
    log(f"genre map books: {len(folder_to_colors)}")

    excludes = {x.strip() for x in args.exclude.split(",") if x.strip()}

    targets = []
    for book in gac.BOOKS:
        folder = book[0]
        if args.book and folder != args.book:
            continue
        if folder in excludes:
            log(f"  [exclude] {folder}")
            continue
        targets.append(book)

    if args.test:
        targets = targets[:1]
        log(f"--test: {targets[0][0]} 만 dry run")

    log(f"처리 대상: {len(targets)}권")

    results = []
    for book in targets:
        r = process_book(
            book,
            folder_to_colors,
            dry_run=args.test,
            validate=not args.no_validate,
        )
        results.append(r)

    ok = sum(1 for r in results if r["status"] == "ok")
    skipped = sum(1 for r in results if r["status"] == "skipped_no_genre")
    failed = sum(1 for r in results if r["status"] == "error")
    log("-" * 60)
    log(f"DONE  ok={ok}  skipped(no_genre)={skipped}  failed={failed}  total={len(results)}")
    log("-" * 60)

    summary_path = LOG_DIR / "genre_recolor_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "ts": datetime.now().isoformat(),
                "test": args.test,
                "results": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    log(f"summary -> {summary_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
