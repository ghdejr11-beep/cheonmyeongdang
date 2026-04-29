#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk Manifest Generator — KDP 27권 일괄 manifest.json 생성기
==============================================================
- 폴더명에서 책 제목 자동 추출 (kebab-case → Title Case)
- interior PDF (cover_v_pre_genre.pdf 제외, cover.pdf 제외) 페이지 수 자동 계산
- 폴더명/콘텐츠 기반 language / keywords / categories 추정
- 이미 manifest.json 있는 폴더는 스킵
- 사용자 채울 필드(description, isbn 일부)는 [TODO] 마커

Usage
  python bulk_create_manifests.py
  python bulk_create_manifests.py --projects-dir <path> --dry-run

Author: 쿤스튜디오 (Deokgu Studio) · 2026-04-26
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
    _HAS_PDF = True
except ImportError:
    _HAS_PDF = False

# 사용자 KDP 룰
AUTHOR = "Deokgu Studio"
DEFAULT_PUB_DATE = date.today().isoformat()
DEFAULT_PRICE_USD = 9.99
DEFAULT_TRIM = "6x9"

# 폴더명/키워드 → 카테고리/키워드/언어 휴리스틱
# (폴더명 substring → {keywords, categories, language, trim_size})
HEURISTICS: list[tuple[str, dict[str, Any]]] = [
    ("password-logbook", {
        "keywords": ["password journal", "password keeper", "internet logbook", "password organizer", "login book", "username password", "secure notebook"],
        "categories": ["BISAC: REFERENCE / Personal & Practical Guides", "BISAC: SELF-HELP / Personal Growth"],
        "language": "en",
    }),
    ("airbnb-guestbook", {
        "keywords": ["airbnb guest book", "vacation rental", "vrbo guestbook", "host welcome book", "short term rental", "hospitality journal", "guest log"],
        "categories": ["BISAC: HOUSE & HOME / Reference", "BISAC: BUSINESS & ECONOMICS / Industries / Hospitality"],
        "language": "en",
    }),
    ("blood-pressure-log", {
        "keywords": ["blood pressure log", "hypertension tracker", "bp diary", "health journal", "daily blood pressure", "heart health", "medical record"],
        "categories": ["BISAC: HEALTH & FITNESS / Diseases & Conditions / Cardiovascular", "BISAC: MEDICAL / Reference"],
        "language": "en",
    }),
    ("blood-sugar-tracker", {
        "keywords": ["blood sugar log", "diabetic journal", "glucose tracker", "diabetes log book", "a1c tracker", "insulin journal", "type 2 diabetes"],
        "categories": ["BISAC: HEALTH & FITNESS / Diseases & Conditions / Diabetes", "BISAC: MEDICAL / Endocrinology & Metabolism"],
        "language": "en",
    }),
    ("perimenopause-symptom-tracker", {
        "keywords": ["perimenopause tracker", "menopause journal", "hormone log", "women health", "symptom diary", "hot flash log", "midlife wellness"],
        "categories": ["BISAC: HEALTH & FITNESS / Women's Health", "BISAC: SELF-HELP / Aging"],
        "language": "en",
    }),
    ("sleep-planner", {
        "keywords": ["sleep planner", "sleep tracker", "insomnia journal", "sleep diary", "bedtime routine", "rest log", "circadian planner"],
        "categories": ["BISAC: HEALTH & FITNESS / Sleep", "BISAC: SELF-HELP / Personal Growth"],
        "language": "en",
    }),
    ("yoga-progress-journal", {
        "keywords": ["yoga journal", "yoga progress tracker", "asana log", "yoga practice book", "mindfulness journal", "yoga workbook", "yoga planner"],
        "categories": ["BISAC: HEALTH & FITNESS / Yoga", "BISAC: BODY, MIND & SPIRIT / Mindfulness & Meditation"],
        "language": "en",
    }),
    ("meal-prep-planner", {
        "keywords": ["meal prep planner", "weekly meal planner", "grocery list", "food journal", "meal planning notebook", "kitchen organizer", "diet planner"],
        "categories": ["BISAC: COOKING / Methods / Quick & Easy", "BISAC: HEALTH & FITNESS / Nutrition"],
        "language": "en",
    }),
    ("budget-planner-couples", {
        "keywords": ["budget planner couples", "couples finance", "household budget", "money tracker", "expense journal", "joint finances", "marriage budget"],
        "categories": ["BISAC: BUSINESS & ECONOMICS / Personal Finance / Budgeting", "BISAC: FAMILY & RELATIONSHIPS / Marriage & Long-Term Relationships"],
        "language": "en",
    }),
    ("adhd-planner", {
        "keywords": ["adhd planner", "adhd journal", "executive function", "neurodivergent planner", "focus tracker", "adhd workbook", "adult adhd"],
        "categories": ["BISAC: SELF-HELP / Personal Growth", "BISAC: HEALTH & FITNESS / Diseases & Conditions / Nervous System"],
        "language": "en",
    }),
    ("caregiver-daily-log", {
        "keywords": ["caregiver log", "elderly care journal", "dementia log", "home health journal", "patient daily log", "nursing notebook", "senior care"],
        "categories": ["BISAC: FAMILY & RELATIONSHIPS / Eldercare", "BISAC: MEDICAL / Nursing / Long-Term Care"],
        "language": "en",
    }),
    ("dog-health-training-log", {
        "keywords": ["dog journal", "puppy training log", "dog health record", "pet planner", "dog vaccination", "training notebook", "dog owner"],
        "categories": ["BISAC: PETS / Dogs / General", "BISAC: PETS / Dogs / Training"],
        "language": "en",
    }),
    ("fishing-log-book", {
        "keywords": ["fishing log", "angler journal", "bass fishing", "fishing diary", "tackle box notebook", "fishing trip planner", "fly fishing"],
        "categories": ["BISAC: SPORTS & RECREATION / Fishing", "BISAC: NATURE / Animals / Fish"],
        "language": "en",
    }),
    ("ai-side-hustle-en", {
        "keywords": ["ai side hustle", "make money online", "ai business", "passive income", "ai prompts", "online income", "ai entrepreneur"],
        "categories": ["BISAC: BUSINESS & ECONOMICS / Entrepreneurship", "BISAC: COMPUTERS / Artificial Intelligence / General"],
        "language": "en",
    }),
    ("ai-prompt-workbook", {
        "keywords": ["ai prompt workbook", "chatgpt prompts", "prompt engineering", "ai for beginners", "prompt journal", "generative ai", "llm prompts"],
        "categories": ["BISAC: COMPUTERS / Artificial Intelligence / General", "BISAC: SELF-HELP / Creativity"],
        "language": "en",
    }),
    ("genz-stress", {
        "keywords": ["gen z stress", "anxiety workbook", "young adult mental health", "teen stress", "burnout journal", "self-care workbook", "college stress"],
        "categories": ["BISAC: SELF-HELP / Stress Management", "BISAC: YOUNG ADULT NONFICTION / Health & Daily Living"],
        "language": "en",
    }),
    ("introvert-confidence", {
        "keywords": ["introvert confidence", "shy people", "introvert workbook", "social anxiety", "self-confidence journal", "quiet strength", "introvert power"],
        "categories": ["BISAC: SELF-HELP / Personal Growth", "BISAC: PSYCHOLOGY / Personality"],
        "language": "en",
    }),
    ("mental-reset-journal", {
        "keywords": ["mental reset journal", "mindfulness journal", "anxiety relief", "self-care notebook", "mental health workbook", "guided journal", "wellbeing diary"],
        "categories": ["BISAC: SELF-HELP / Mood Disorders / Depression", "BISAC: BODY, MIND & SPIRIT / Mindfulness & Meditation"],
        "language": "en",
    }),
    ("bold-easy-coloring-animals", {
        "keywords": ["bold coloring book", "easy coloring animals", "seniors coloring", "thick lines coloring", "stress relief", "adult coloring", "low vision coloring"],
        "categories": ["BISAC: GAMES & ACTIVITIES / Coloring Books", "BISAC: SELF-HELP / Aging"],
        "language": "en",
        "trim_size": "8.5x11",
    }),
    ("cottagecore-coloring", {
        "keywords": ["cottagecore coloring", "cozy aesthetic", "countryside coloring", "rustic coloring", "garden coloring", "adult coloring book", "vintage coloring"],
        "categories": ["BISAC: GAMES & ACTIVITIES / Coloring Books", "BISAC: ART / Subjects & Themes / Plants & Animals"],
        "language": "en",
        "trim_size": "8.5x11",
    }),
    ("zodiac-mandala-coloring", {
        "keywords": ["zodiac coloring", "mandala coloring", "astrology coloring", "horoscope coloring", "spiritual coloring", "adult coloring", "stress relief coloring"],
        "categories": ["BISAC: GAMES & ACTIVITIES / Coloring Books", "BISAC: BODY, MIND & SPIRIT / Astrology / General"],
        "language": "en",
        "trim_size": "8.5x11",
    }),
    ("dot-marker-kids", {
        "keywords": ["dot marker activity book", "do a dot", "toddler activity", "preschool dot", "kids dot painting", "bingo dauber book", "dot art kids"],
        "categories": ["BISAC: JUVENILE NONFICTION / Activity Books / Coloring", "BISAC: JUVENILE NONFICTION / Games & Activities / General"],
        "language": "en",
        "trim_size": "8.5x11",
    }),
    ("math-workbook-grade1", {
        "keywords": ["math workbook grade 1", "first grade math", "addition subtraction", "kids math practice", "homeschool math", "elementary math", "math activity book"],
        "categories": ["BISAC: JUVENILE NONFICTION / Mathematics / Arithmetic", "BISAC: EDUCATION / Elementary"],
        "language": "en",
        "trim_size": "8.5x11",
    }),
    ("spot-difference-seniors", {
        "keywords": ["spot the difference seniors", "puzzle book seniors", "large print puzzles", "dementia activity book", "elderly puzzles", "memory activity", "brain games seniors"],
        "categories": ["BISAC: GAMES & ACTIVITIES / Puzzles", "BISAC: SELF-HELP / Aging"],
        "language": "en",
        "trim_size": "8.5x11",
    }),
    ("fortune-notebook", {
        "keywords": ["fortune notebook", "manifestation journal", "luck journal", "lottery log", "gratitude diary", "money mindset", "abundance journal"],
        "categories": ["BISAC: BODY, MIND & SPIRIT / New Thought", "BISAC: SELF-HELP / Personal Growth"],
        "language": "en",
    }),
    ("saju-diary", {
        "keywords": ["사주 다이어리", "사주명리", "운세 노트", "일진 기록", "음양오행", "saju diary", "korean astrology"],
        "categories": ["BISAC: BODY, MIND & SPIRIT / Astrology / General", "BISAC: SELF-HELP / Journaling"],
        "language": "ko",
    }),
]

DEFAULT_RULE = {
    "keywords": ["journal", "planner", "notebook", "logbook", "workbook", "self-help", "productivity"],
    "categories": ["BISAC: SELF-HELP / Personal Growth"],
    "language": "en",
    "trim_size": DEFAULT_TRIM,
}


# ---- Helpers -------------------------------------------------------------
def kebab_to_title(name: str) -> str:
    """password-logbook-premium → Password Logbook Premium"""
    parts = re.split(r"[-_]", name)
    cap = []
    for p in parts:
        if not p:
            continue
        # 두 글자 이하 대문자 처리 (en, ai, kr 등)
        if p.lower() in {"ai", "en", "ko", "us", "uk"}:
            cap.append(p.upper())
        else:
            cap.append(p.capitalize())
    return " ".join(cap)


def detect_language(folder_name: str, override: str | None) -> str:
    if override:
        return override
    if any(k in folder_name for k in ("saju", "kor", "_ko", "-ko")):
        return "ko"
    return "en"


def find_interior_pdf(book_dir: Path) -> Path | None:
    """interior PDF 찾기 — cover/cover_v_pre_genre 제외, 가장 큰 PDF 선택."""
    candidates: list[Path] = []
    for pdf in book_dir.glob("*.pdf"):
        n = pdf.name.lower()
        if n.startswith("cover") or "cover_v_pre_genre" in n or n.endswith("_cover.pdf"):
            continue
        if "kdp_cover" in n:
            continue
        candidates.append(pdf)
    if not candidates:
        return None
    # 가장 큰 파일 = 본문일 가능성 가장 높음
    candidates.sort(key=lambda p: p.stat().st_size, reverse=True)
    return candidates[0]


def get_page_count(pdf_path: Path) -> int:
    if not _HAS_PDF or not pdf_path or not pdf_path.exists():
        return 0
    try:
        doc = fitz.open(pdf_path)
        try:
            return doc.page_count
        finally:
            doc.close()
    except Exception:
        return 0


def get_rule(folder_name: str) -> dict[str, Any]:
    for key, rule in HEURISTICS:
        if key in folder_name:
            return rule
    return DEFAULT_RULE


def make_manifest(book_dir: Path) -> dict[str, Any]:
    folder = book_dir.name
    title = kebab_to_title(folder)
    if len(title) > 200:
        title = title[:200]

    rule = get_rule(folder)
    interior = find_interior_pdf(book_dir)
    page_count = get_page_count(interior) if interior else 0

    manifest = {
        "book_id": folder,
        "title": title,
        "subtitle": "",
        "author": AUTHOR,
        "language": detect_language(folder, rule.get("language")),
        "description": "[TODO: 4000자 이하로 작성. 책 소개·타겟 독자·차별점 포함]",
        "keywords": list(rule.get("keywords", DEFAULT_RULE["keywords"]))[:7],
        "categories": list(rule.get("categories", DEFAULT_RULE["categories"]))[:2],
        "isbn": "",
        "price_usd": DEFAULT_PRICE_USD,
        "page_count": page_count,
        "trim_size": rule.get("trim_size", DEFAULT_TRIM),
        "publication_date": DEFAULT_PUB_DATE,
        "interior_pdf": interior.name if interior else "",
        "cover_pdf": "cover.pdf" if (book_dir / "cover.pdf").exists() else "",
        "low_content": any(k in folder for k in (
            "logbook", "planner", "journal", "tracker", "log", "notebook",
            "coloring", "dot-marker", "spot-difference", "workbook",
        )),
        "published": False,
        "todo": ["description", "isbn", "review_keywords", "review_categories"],
    }
    return manifest


# ---- Driver --------------------------------------------------------------
def run(projects_dir: Path, dry_run: bool = False) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "total": 0,
        "created": [],
        "skipped": [],
        "failed": [],
    }
    folders = sorted([p for p in projects_dir.iterdir()
                      if p.is_dir() and p.name != "__pycache__"])
    summary["total"] = len(folders)

    for book_dir in folders:
        manifest_path = book_dir / "manifest.json"
        if manifest_path.exists():
            summary["skipped"].append(book_dir.name)
            continue
        try:
            manifest = make_manifest(book_dir)
            if dry_run:
                print(f"[DRY] {book_dir.name}: pages={manifest['page_count']} "
                      f"lang={manifest['language']} trim={manifest['trim_size']}")
            else:
                manifest_path.write_text(
                    json.dumps(manifest, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            summary["created"].append({
                "book": book_dir.name,
                "title": manifest["title"],
                "pages": manifest["page_count"],
                "language": manifest["language"],
                "trim_size": manifest["trim_size"],
            })
        except Exception as e:
            summary["failed"].append({"book": book_dir.name, "error": str(e)})
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="KDP 27권 manifest.json 일괄 생성")
    parser.add_argument(
        "--projects-dir",
        type=str,
        default=str(Path(__file__).parent / "projects"),
        help="KDP projects 디렉터리",
    )
    parser.add_argument("--dry-run", action="store_true", help="파일 쓰지 않고 결과만 출력")
    args = parser.parse_args()

    projects_dir = Path(args.projects_dir)
    if not projects_dir.exists():
        print(f"[ERROR] projects-dir 없음: {projects_dir}")
        return 2

    print(f"[INFO] PDF backend: {'PyMuPDF' if _HAS_PDF else 'NONE (page_count=0)'}")
    print(f"[INFO] scanning: {projects_dir}")
    summary = run(projects_dir, dry_run=args.dry_run)

    print("\n=== SUMMARY ===")
    print(f"total folders : {summary['total']}")
    print(f"created       : {len(summary['created'])}")
    print(f"skipped       : {len(summary['skipped'])} (manifest already exists)")
    print(f"failed        : {len(summary['failed'])}")
    if summary["created"]:
        print("\n[CREATED]")
        for c in summary["created"]:
            print(f"  - {c['book']:<32} pages={c['pages']:<4} lang={c['language']} trim={c['trim_size']}")
    if summary["skipped"]:
        print("\n[SKIPPED]")
        for s in summary["skipped"]:
            print(f"  - {s}")
    if summary["failed"]:
        print("\n[FAILED]")
        for f in summary["failed"]:
            print(f"  - {f['book']}: {f['error']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
