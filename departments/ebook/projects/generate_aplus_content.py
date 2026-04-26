"""
Amazon A+ Content 자동 생성기 (Basic A+ 3-module)
=================================================
Amazon A+ Content 표준:
  - Basic A+ → 평균 매출 +8%
  - Premium A+ → 평균 매출 +20%

본 스크립트는 Basic A+ 3-module을 25개 KDP 책 일괄 생성한다:
  Module 1 — From the Author      (970x300 PNG, 좌 30% 로고+저자 / 우 70% why-text)
  Module 2 — What's Inside        (600x300 PNG x4 = first/early/mid/end pages)
  Module 3 — Series Comparison    (1464x600 PNG, 동일 시리즈 비교 차트)

선택사항:
  KDP description HTML 7-section 자동 작성기
  → projects/{book}/kdp_description.html

라이브러리: Pillow + (optional) PyMuPDF (책 본문 PDF → PNG)
  Pillow 미설치 시 즉시 종료
  PyMuPDF 미설치 시 Module 2는 placeholder 처리

금지:
  - 책 본문 PDF 자체 수정 절대 금지 (read-only fitz.open)
  - KDP_RULES.md 규칙 위반 금지

실행:
  python generate_aplus_content.py
"""

from __future__ import annotations

import io
import json
import re
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# -------- 라이브러리 --------
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.stderr.write("Pillow 필요: pip install Pillow\n")
    sys.exit(1)

try:
    import fitz  # PyMuPDF — 본문 PDF 페이지 렌더링 (read-only)
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

# -------- 경로 --------
BASE = Path(__file__).parent.resolve()
GENRE_MAP_PATH = BASE / "genre_color_map.json"

# -------- 색상 / 폰트 기본값 --------
DEFAULT_PRIMARY = "#1E3A5F"
DEFAULT_SECONDARY = "#C9A961"
DEFAULT_BG = "#FAFAFA"
DEFAULT_TEXT = "#1A1A1A"
DEFAULT_MUTED = "#5A5A5A"

# Windows 시스템 폰트 후보 (영문 KDP 책이므로 라틴 폰트 위주)
FONT_CANDIDATES_BOLD = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\impact.ttf",
]
FONT_CANDIDATES_REG = [
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
]


def _find_font(candidates: list[str]) -> Optional[str]:
    for p in candidates:
        if Path(p).exists():
            return p
    return None


FONT_BOLD = _find_font(FONT_CANDIDATES_BOLD)
FONT_REG = _find_font(FONT_CANDIDATES_REG)


def _ttf(size: int, bold: bool = False) -> ImageFont.ImageFont:
    path = FONT_BOLD if bold else FONT_REG
    try:
        if path:
            return ImageFont.truetype(path, size=size)
    except Exception:
        pass
    return ImageFont.load_default()


# -------- KDP_LISTING.md 파서 --------
@dataclass
class BookMeta:
    book_id: str            # 폴더명 (e.g. "budget-planner-couples")
    title: str
    subtitle: str
    author: str
    description: str        # plain-text 압축 (HTML 제거)
    keywords: list[str]
    price: str
    pages: str
    categories: list[str]
    interior_pdf: Optional[Path]
    cover_pdf: Optional[Path]


def _strip_md(s: str) -> str:
    # 코드 펜스, 굵게, 별표, 이모지 마커 제거
    s = re.sub(r"```.*?```", " ", s, flags=re.DOTALL)
    s = re.sub(r"<[^>]+>", " ", s)               # HTML 태그
    s = re.sub(r"[*_`#>]+", "", s)               # MD 강조
    s = re.sub(r"^[\-\d\.★•⚠✨→\s]+", "", s, flags=re.MULTILINE)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _parse_section(md: str, header: str) -> str:
    """## header 다음부터 다음 ## 직전까지 캡처."""
    pat = re.compile(
        rf"^##\s*{re.escape(header)}\s*\n(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    m = pat.search(md)
    return m.group(1).strip() if m else ""


def parse_listing(book_dir: Path) -> Optional[BookMeta]:
    listing_path = book_dir / "KDP_LISTING.md"
    if not listing_path.exists():
        return None
    md = listing_path.read_text(encoding="utf-8", errors="ignore")

    # 제목 — H1 또는 ## Title 또는 - Title:
    title = ""
    m = re.search(r"^#\s+(?:KDP[^:]*:\s*)?(.+?)(?:\s+—.*)?$", md, re.MULTILINE)
    if m:
        title = _strip_md(m.group(1))
    sec_title = _parse_section(md, "Title")
    if sec_title:
        # "Title" section 첫 비어있지 않은 줄
        for line in sec_title.splitlines():
            cleaned = _strip_md(line)
            if cleaned:
                title = cleaned
                break
    # 인라인 "- Title: xxx" 형식
    m_inline = re.search(r"-\s*\*?\*?Title\*?\*?\s*:\s*(.+)", md)
    if m_inline:
        cand = _strip_md(m_inline.group(1))
        if cand and len(cand) > len(title):
            title = cand

    # Subtitle
    subtitle = _strip_md(_parse_section(md, "Subtitle"))
    if not subtitle:
        m_in = re.search(r"-\s*\*?\*?Subtitle\*?\*?\s*:\s*(.+)", md)
        if m_in:
            subtitle = _strip_md(m_in.group(1))

    # Author
    author = _strip_md(_parse_section(md, "Author"))
    if not author or len(author) > 80:
        m_in = re.search(r"-\s*\*?\*?Author\*?\*?\s*:\s*(.+)", md)
        if m_in:
            author = _strip_md(m_in.group(1))
        else:
            m_in2 = re.search(r"##\s*Author\s*:\s*(.+)", md)
            if m_in2:
                author = _strip_md(m_in2.group(1))
    if not author:
        author = "Deokgu Studio"

    # Description — "Description (HTML)" 또는 "설명" 또는 "Description"
    desc_raw = ""
    for h in ["Description (HTML)", "Description", "설명 (Description)", "설명"]:
        cand = _parse_section(md, h)
        if cand:
            desc_raw = cand
            break
    description = _strip_md(desc_raw)

    # Keywords
    kw_raw = _parse_section(md, "Keywords")
    if not kw_raw:
        for h in ["Keywords (7 max)", "키워드 (7개, 쉼표 구분)", "키워드"]:
            cand = _parse_section(md, h)
            if cand:
                kw_raw = cand
                break
    keywords: list[str] = []
    for line in kw_raw.splitlines():
        line = _strip_md(line)
        if not line:
            continue
        if "," in line:
            keywords.extend([k.strip() for k in line.split(",") if k.strip()])
        else:
            keywords.append(line)
    keywords = [k for k in keywords if 2 <= len(k) <= 80][:7]

    # Price
    price_raw = _parse_section(md, "Price") or ""
    price_match = re.search(r"\$\s*[\d.]+", price_raw + " " + md)
    price = price_match.group(0).replace(" ", "") if price_match else "$8.99"

    # Pages — try several layouts
    pages = None
    pages_raw = _parse_section(md, "Pages") or ""
    if pages_raw:
        m = re.search(r"(\d{2,4})", pages_raw)
        if m:
            pages = m.group(1)
    if not pages:
        for pat in [
            r"-\s*\*?\*?Pages?\*?\*?\s*:\s*(\d{2,4})",
            r"##\s*Pages\s*:\s*(\d{2,4})",
            r"Page\s*Count\s*:\s*(\d{2,4})",
            r"-\s*\*?\*?Page\s*Count\*?\*?\s*:\s*(\d{2,4})",
            r"페이지\s*수\s*:\s*\*?\*?\s*(\d{2,4})",
        ]:
            m = re.search(pat, md, re.IGNORECASE)
            if m:
                pages = m.group(1)
                break
    if not pages:
        pages = "120"

    # Categories
    cat_raw = _parse_section(md, "Categories") or _parse_section(md, "카테고리 (2개 선택)") or _parse_section(md, "카테고리")
    categories: list[str] = []
    for line in cat_raw.splitlines():
        cleaned = _strip_md(line)
        if cleaned and len(cleaned) > 3:
            categories.append(cleaned)
    categories = categories[:2]

    # Interior PDF (가장 큰 .pdf 중 cover/cover_verify 제외)
    interior_pdf = None
    pdfs = sorted(
        [p for p in book_dir.glob("*.pdf") if not p.stem.lower().startswith(("cover", "kdp_current"))],
        key=lambda p: p.stat().st_size,
        reverse=True,
    )
    if pdfs:
        interior_pdf = pdfs[0]
    cover_pdf = book_dir / "cover.pdf"
    if not cover_pdf.exists():
        cover_pdf = None

    return BookMeta(
        book_id=book_dir.name,
        title=title or book_dir.name.replace("-", " ").title(),
        subtitle=subtitle,
        author=author,
        description=description,
        keywords=keywords,
        price=price,
        pages=pages,
        categories=categories,
        interior_pdf=interior_pdf,
        cover_pdf=cover_pdf,
    )


# -------- 장르 색상 --------
def load_genre_map() -> dict:
    if not GENRE_MAP_PATH.exists():
        return {"genres": {}}
    return json.loads(GENRE_MAP_PATH.read_text(encoding="utf-8"))


def get_palette(book_id: str, genre_map: dict) -> tuple[str, str, str]:
    """returns (primary, secondary, genre_key)"""
    for gkey, ginfo in genre_map.get("genres", {}).items():
        if book_id in ginfo.get("books", []):
            return ginfo["primary"], ginfo["secondary"], gkey
    return DEFAULT_PRIMARY, DEFAULT_SECONDARY, "default"


# -------- 텍스트 wrap (Pillow textbbox 기반) --------
def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    if not text:
        return []
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        candidate = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_w:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(
    img: Image.Image,
    xy: tuple[int, int],
    text: str,
    font,
    fill: str,
    max_w: int,
    line_h: Optional[int] = None,
    max_lines: Optional[int] = None,
) -> int:
    """returns next-y after the block"""
    draw = ImageDraw.Draw(img)
    lines = wrap_text(draw, text, font, max_w)
    if max_lines:
        lines = lines[:max_lines]
    x, y = xy
    if line_h is None:
        bbox = draw.textbbox((0, 0), "Ay", font=font)
        line_h = (bbox[3] - bbox[1]) + 6
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


# -------- Module 1: From the Author (970x300) --------
def render_module1(meta: BookMeta, primary: str, secondary: str, out_path: Path) -> None:
    W, H = 970, 300
    img = Image.new("RGB", (W, H), DEFAULT_BG)
    draw = ImageDraw.Draw(img)

    # 좌측 30% (0~291) — 로고 + author placeholder
    left_w = int(W * 0.30)
    draw.rectangle([0, 0, left_w, H], fill=primary)

    # Deokgu Studio 로고 (텍스트 마크)
    f_logo_big = _ttf(34, bold=True)
    f_logo_sm = _ttf(15, bold=False)

    logo_y = 60
    draw.text((24, logo_y), "DEOKGU", font=f_logo_big, fill="#FFFFFF")
    draw.text((24, logo_y + 38), "STUDIO", font=f_logo_big, fill=secondary)

    # 저자 사진 placeholder — 원형
    av_cx, av_cy, av_r = left_w // 2, 210, 40
    draw.ellipse([av_cx - av_r, av_cy - av_r, av_cx + av_r, av_cy + av_r],
                 fill="#FFFFFF", outline=secondary, width=3)
    # 머리/몸체 실루엣
    draw.ellipse([av_cx - 18, av_cy - 22, av_cx + 18, av_cy + 14], fill=primary)
    draw.pieslice([av_cx - 30, av_cy + 4, av_cx + 30, av_cy + 60], 180, 360, fill=primary)
    # 캡션
    cap_font = _ttf(11, bold=False)
    draw.text((av_cx - 38, av_cy + av_r + 6), "Indie Publisher", font=cap_font, fill="#FFFFFF")

    # 우측 70% (291~970)
    right_x = left_w + 28
    right_max_w = W - right_x - 28

    # 헤더 라벨
    f_label = _ttf(13, bold=True)
    draw.text((right_x, 28), "FROM THE AUTHOR", font=f_label, fill=secondary)

    # 액센트 라인
    draw.rectangle([right_x, 50, right_x + 60, 53], fill=primary)

    # 메인 헤드라인
    f_head = _ttf(22, bold=True)
    headline_text = f"Why I Wrote {meta.title.split(':')[0].strip()}"
    if len(headline_text) > 70:
        headline_text = headline_text[:67] + "..."
    next_y = draw_text_block(
        img, (right_x, 64), headline_text, f_head, DEFAULT_TEXT,
        right_max_w, line_h=28, max_lines=2,
    )

    # 본문 — description 첫 200자
    body = meta.description.strip() or (
        f"This {meta.pages}-page workbook was crafted to help readers "
        f"organize their lives with clarity and intention. Every page is "
        f"designed for daily use, with thoughtful layouts that turn habits "
        f"into lasting routines."
    )
    body = body[:200].rstrip()
    if len(meta.description) > 200:
        body = body.rsplit(" ", 1)[0] + "..."
    f_body = _ttf(15, bold=False)
    draw_text_block(
        img, (right_x, next_y + 8), body, f_body, DEFAULT_MUTED,
        right_max_w, line_h=22, max_lines=6,
    )

    # 하단 시그니처
    f_sig = _ttf(13, bold=True)
    draw.text((right_x, H - 36), f"— {meta.author}", font=f_sig, fill=primary)

    img.save(out_path, "PNG", optimize=True)


# -------- Module 2: What's Inside (600x300 x 4) --------
def _render_pdf_page_to_pil(pdf_path: Path, page_idx: int, target_w: int, target_h: int) -> Optional[Image.Image]:
    if not HAS_FITZ:
        return None
    try:
        # read-only 모드 (책 본문 절대 수정 금지)
        doc = fitz.open(pdf_path)
        try:
            if page_idx < 0:
                page_idx = max(0, doc.page_count + page_idx)
            page_idx = min(page_idx, doc.page_count - 1)
            page = doc.load_page(page_idx)
            # 약 200dpi 정도로 렌더 후 다운샘플
            zoom = 1.6
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            mode = "RGB" if pix.n < 4 else "RGBA"
            img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
            if mode == "RGBA":
                img = img.convert("RGB")
            # 비율 유지 contain 후 흰 배경 캔버스에 중앙 배치
            img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (target_w, target_h), "#FFFFFF")
            ox = (target_w - img.width) // 2
            oy = (target_h - img.height) // 2
            canvas.paste(img, (ox, oy))
            return canvas
        finally:
            doc.close()
    except Exception:
        return None


def render_module2_panel(
    meta: BookMeta,
    primary: str,
    secondary: str,
    label: str,
    pdf_page_idx: Optional[int],
    out_path: Path,
) -> bool:
    """반환값: 진짜 PDF 페이지 렌더링 성공 여부 (False면 placeholder)"""
    W, H = 600, 300
    img = Image.new("RGB", (W, H), DEFAULT_BG)
    draw = ImageDraw.Draw(img)

    # 상단 헤더 바
    draw.rectangle([0, 0, W, 48], fill=primary)
    f_label = _ttf(16, bold=True)
    draw.text((20, 14), label.upper(), font=f_label, fill="#FFFFFF")
    f_meta = _ttf(11, bold=False)
    draw.text((W - 130, 18), f"{meta.pages} PAGES", font=f_meta, fill=secondary)

    # 미리보기 영역
    preview_box = (24, 64, W - 24, H - 56)
    pw = preview_box[2] - preview_box[0]
    ph = preview_box[3] - preview_box[1]
    draw.rectangle(preview_box, fill="#FFFFFF", outline=secondary, width=2)

    succeeded = False
    rendered = None
    if pdf_page_idx is not None and meta.interior_pdf and meta.interior_pdf.exists():
        rendered = _render_pdf_page_to_pil(meta.interior_pdf, pdf_page_idx, pw - 8, ph - 8)
    if rendered is not None:
        img.paste(rendered, (preview_box[0] + 4, preview_box[1] + 4))
        succeeded = True
    else:
        # placeholder 표시
        f_ph = _ttf(15, bold=True)
        msg = "PREVIEW COMING SOON" if HAS_FITZ else "PYMUPDF NOT AVAILABLE"
        bbox = draw.textbbox((0, 0), msg, font=f_ph)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (preview_box[0] + (pw - tw) // 2, preview_box[1] + (ph - th) // 2),
            msg, font=f_ph, fill=DEFAULT_MUTED,
        )

    # 하단 캡션
    f_cap = _ttf(13, bold=False)
    captions = {
        "first": "Cover Page & Welcome",
        "early": "Quick-Start Sample",
        "mid": "Mid-Book Layout",
        "end": "Notes & Summary Pages",
    }
    cap_text = captions.get(label.lower(), label)
    draw.text((24, H - 32), cap_text, font=f_cap, fill=DEFAULT_TEXT)

    img.save(out_path, "PNG", optimize=True)
    return succeeded


def render_module2(meta: BookMeta, primary: str, secondary: str, out_dir: Path) -> dict:
    """returns {label: success_bool}"""
    results: dict[str, bool] = {}
    page_count = 0
    if HAS_FITZ and meta.interior_pdf and meta.interior_pdf.exists():
        try:
            d = fitz.open(meta.interior_pdf)
            page_count = d.page_count
            d.close()
        except Exception:
            page_count = 0

    plan = [
        ("first", 0 if page_count else None, "module2_a.png"),
        ("early", page_count // 4 if page_count else None, "module2_b.png"),
        ("mid", page_count // 2 if page_count else None, "module2_c.png"),
        ("end", max(0, page_count - 2) if page_count else None, "module2_d.png"),
    ]
    for label, idx, fname in plan:
        ok = render_module2_panel(meta, primary, secondary, label, idx, out_dir / fname)
        results[label] = ok
    return results


# -------- Module 3: Series Comparison (1464x600) --------
SERIES_DEFINITIONS: dict[str, list[str]] = {
    "finance_organize": ["budget-planner-couples", "password-logbook", "password-logbook-premium"],
    "wellness_planners": ["sleep-planner", "yoga-progress-journal", "meal-prep-planner"],
    "health_logs": ["blood-pressure-log", "blood-sugar-tracker", "caregiver-daily-log"],
    "self_help_journals": ["mental-reset-journal", "introvert-confidence", "genz-stress"],
    "kids_activity": ["math-workbook-grade1", "dot-marker-kids", "bold-easy-coloring-animals"],
    "coloring_adult": ["zodiac-mandala-coloring", "cottagecore-coloring", "spot-difference-seniors"],
    "lifestyle_log": ["adhd-planner", "airbnb-guestbook", "fishing-log-book", "dog-health-training-log"],
}


def find_series(book_id: str) -> tuple[str, list[str]]:
    for name, members in SERIES_DEFINITIONS.items():
        if book_id in members:
            return name, members
    # fallback — 본인 1권
    return "standalone", [book_id]


def _key_feature(meta: BookMeta) -> str:
    if meta.subtitle:
        # subtitle 첫 비교적 짧은 구절
        parts = re.split(r"[|—\-]", meta.subtitle)
        for p in parts:
            p = p.strip()
            if 8 <= len(p) <= 38:
                return p
        return meta.subtitle[:38]
    if meta.keywords:
        return meta.keywords[0][:38]
    return f"{meta.pages}-page workbook"


def _audience(meta: BookMeta) -> str:
    """Whole-word matching against book_id (high precision) then text (fallback)."""
    bid = meta.book_id.lower()
    # 1) book_id 기반 — 가장 정확
    id_rules = [
        ("password-logbook-premium", "Seniors & elders"),
        ("password-logbook", "Anyone with online accounts"),
        ("budget-planner-couples", "Couples & partners"),
        ("caregiver-daily-log", "Family caregivers"),
        ("blood-pressure-log", "Hypertension patients"),
        ("blood-sugar-tracker", "Diabetic readers"),
        ("sleep-planner", "Insomniacs"),
        ("yoga-progress-journal", "Yoga practitioners"),
        ("meal-prep-planner", "Meal preppers"),
        ("adhd-planner", "ADHD adults"),
        ("introvert-confidence", "Introverts"),
        ("genz-stress", "Gen-Z & students"),
        ("mental-reset-journal", "Anxiety-prone adults"),
        ("math-workbook-grade1", "1st graders"),
        ("dot-marker-kids", "Toddlers (1-4)"),
        ("bold-easy-coloring-animals", "Young children"),
        ("cottagecore-coloring", "Adult coloring fans"),
        ("zodiac-mandala-coloring", "Astrology & coloring fans"),
        ("spot-difference-seniors", "Seniors & elders"),
        ("dog-health-training-log", "Dog owners"),
        ("fishing-log-book", "Anglers"),
        ("airbnb-guestbook", "Airbnb hosts"),
        ("ai-side-hustle-en", "Aspiring AI freelancers"),
    ]
    for k, v in id_rules:
        if bid == k:
            return v
    # 2) 단어경계 매칭
    text = " " + (meta.description + " " + meta.subtitle + " " + meta.title).lower() + " "
    word_rules = [
        (r"\bseniors?\b", "Seniors & elders"),
        (r"\bgrandparents?\b", "Seniors & elders"),
        (r"\bcouples?\b", "Couples & partners"),
        (r"\bkids?\b", "Children"),
        (r"\btoddlers?\b", "Toddlers (1-4)"),
        (r"\bdogs?\b", "Dog owners"),
        (r"\bcats?\b", "Cat owners"),
        (r"\bairbnb\b", "Airbnb hosts"),
        (r"\bcaregivers?\b", "Family caregivers"),
        (r"\bintroverts?\b", "Introverts"),
        (r"\banxiety\b", "Anxiety-prone adults"),
        (r"\bstress\b", "Stress-prone adults"),
        (r"\byoga\b", "Yoga practitioners"),
        (r"\bsleep\b", "Insomniacs"),
        (r"\bbudget\b", "Budget-conscious"),
        (r"\bfishing\b", "Anglers"),
        (r"\bpasswords?\b", "Anyone with online accounts"),
        (r"\bcoloring\b", "Coloring fans"),
        (r"\bblood pressure\b", "Hypertension patients"),
        (r"\bblood sugar\b", "Diabetic readers"),
        (r"\badhd\b", "ADHD adults"),
    ]
    for pat, label in word_rules:
        if re.search(pat, text):
            return label
    return "Adult readers"


def _draw_thumbnail(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                    primary: str, secondary: str, title: str, *, current: bool = False) -> None:
    x0, y0, x1, y1 = box
    # cover-like rectangle
    draw.rectangle(box, fill=primary, outline=secondary, width=3)
    # decorative diagonal
    draw.polygon([(x0, y0), (x0 + 30, y0), (x0, y0 + 30)], fill=secondary)
    draw.polygon([(x1, y1), (x1 - 30, y1), (x1, y1 - 30)], fill=secondary)
    # title text
    f_t = _ttf(13, bold=True)
    short = title.split(":")[0].strip()
    if len(short) > 30:
        short = short[:30]
    lines = wrap_text(draw, short, f_t, x1 - x0 - 16)[:3]
    ty = y0 + 24
    for line in lines:
        draw.text((x0 + 10, ty), line, font=f_t, fill="#FFFFFF")
        ty += 18
    if current:
        f_b = _ttf(10, bold=True)
        # "THIS BOOK" 뱃지
        bw, bh = 78, 18
        bx = x0 + (x1 - x0 - bw) // 2
        by = y1 - bh - 8
        draw.rectangle([bx, by, bx + bw, by + bh], fill=secondary)
        draw.text((bx + 8, by + 3), "THIS BOOK", font=f_b, fill=primary)


def render_module3(
    current: BookMeta,
    series_members: list[BookMeta],
    primary: str,
    secondary: str,
    out_path: Path,
) -> None:
    W, H = 1464, 600
    img = Image.new("RGB", (W, H), DEFAULT_BG)
    draw = ImageDraw.Draw(img)

    # 상단 헤더
    draw.rectangle([0, 0, W, 70], fill=primary)
    f_title = _ttf(28, bold=True)
    draw.text((40, 18), "COMPARE THE SERIES", font=f_title, fill="#FFFFFF")
    f_sub = _ttf(14, bold=False)
    draw.text((40, 50), "Choose the volume that fits your reader.", font=f_sub, fill=secondary)

    # 표 헤더
    headers = ["Cover", "Pages", "Price", "Key Feature", "Best For"]
    n_cols = len(headers)
    n_rows = max(1, len(series_members))

    table_top = 88
    table_left = 24
    table_right = W - 24
    table_bottom = H - 24
    row_h = (table_bottom - table_top - 40) // n_rows
    col_widths = [
        160,  # cover thumb
        100,
        110,
        420,
        (table_right - table_left) - (160 + 100 + 110 + 420),
    ]

    # 헤더 행
    x = table_left
    for i, h in enumerate(headers):
        cw = col_widths[i]
        draw.rectangle([x, table_top, x + cw, table_top + 36], fill=secondary)
        f_h = _ttf(14, bold=True)
        draw.text((x + 12, table_top + 9), h, font=f_h, fill=primary)
        x += cw

    # 데이터 행
    for ridx, mem in enumerate(series_members):
        row_top = table_top + 36 + ridx * row_h
        is_current = mem.book_id == current.book_id
        bg = "#FFF7E0" if is_current else ("#FFFFFF" if ridx % 2 == 0 else "#F0F0F0")
        draw.rectangle([table_left, row_top, table_right, row_top + row_h], fill=bg)
        # 행 보더
        draw.line([(table_left, row_top + row_h), (table_right, row_top + row_h)],
                  fill="#D0D0D0", width=1)

        # 컬럼별 채우기
        cx = table_left
        # 1. cover thumb
        thumb_pad = 12
        thumb_box = (cx + thumb_pad, row_top + thumb_pad,
                     cx + col_widths[0] - thumb_pad, row_top + row_h - thumb_pad)
        _draw_thumbnail(draw, thumb_box, primary, secondary, mem.title, current=is_current)
        cx += col_widths[0]

        # 2. pages
        f_v = _ttf(20, bold=True)
        draw.text((cx + 14, row_top + row_h // 2 - 12),
                  f"{mem.pages} pp", font=f_v, fill=DEFAULT_TEXT)
        cx += col_widths[1]

        # 3. price
        draw.text((cx + 14, row_top + row_h // 2 - 12),
                  mem.price, font=f_v, fill=primary)
        cx += col_widths[2]

        # 4. key feature
        f_k = _ttf(14, bold=False)
        feat = _key_feature(mem)
        draw_text_block(
            img, (cx + 14, row_top + 14), feat, f_k, DEFAULT_TEXT,
            col_widths[3] - 28, line_h=20, max_lines=4,
        )
        cx += col_widths[3]

        # 5. audience
        aud = _audience(mem)
        f_a = _ttf(14, bold=True)
        draw.text((cx + 14, row_top + row_h // 2 - 10),
                  aud, font=f_a, fill=primary)

    img.save(out_path, "PNG", optimize=True)


# -------- KDP description HTML 7-section 작성기 --------
def build_kdp_description_html(meta: BookMeta) -> str:
    """
    7섹션 구조:
      1. Hook (강조 문장)
      2. Pain point
      3. WHAT'S INSIDE (5+ bullets)
      4. WHY THIS BOOK (3 bullets)
      5. PERFECT FOR (3-4 bullets)
      6. BOOK DETAILS (size/pages/paper/cover)
      7. CTA (gift / buy multiple)
    """
    title_short = meta.title.split(":")[0].strip()
    pages = meta.pages
    desc_seed = meta.description or ""

    def _seed_or(default: str) -> str:
        return (desc_seed[:160] + "...") if len(desc_seed) > 40 else default

    # 키워드 기반 hook
    hook = f"Stay organized. Stay consistent. {title_short} makes it effortless."
    if "couples" in meta.book_id:
        hook = "Build wealth together — without the budget arguments."
    elif "password" in meta.book_id:
        hook = "Never reset another password again. Keep every login in one trusted place."
    elif "sleep" in meta.book_id:
        hook = "Reclaim your nights. Track sleep, spot patterns, wake up refreshed."
    elif "blood-pressure" in meta.book_id:
        hook = "Take control of your numbers. A doctor-friendly log your cardiologist will love."
    elif "blood-sugar" in meta.book_id:
        hook = "Stable glucose starts with simple, daily tracking."
    elif "yoga" in meta.book_id:
        hook = "Watch your practice grow, pose by pose."
    elif "meal-prep" in meta.book_id:
        hook = "Plan once. Eat well all week. Save hours every Sunday."
    elif "caregiver" in meta.book_id:
        hook = "Caring for a loved one is hard enough. Documenting it shouldn't be."
    elif "adhd" in meta.book_id:
        hook = "ADHD-friendly planning that actually sticks."
    elif "introvert" in meta.book_id:
        hook = "Quiet confidence — built one small win at a time."
    elif "genz" in meta.book_id:
        hook = "Stress isn't the enemy. Reacting to it without a plan is."
    elif "mental-reset" in meta.book_id:
        hook = "Reset your mind in 30 days, one journal page at a time."
    elif "math-workbook" in meta.book_id:
        hook = "Build math confidence in 1st graders — one fun page at a time."
    elif "dot-marker" in meta.book_id:
        hook = "Big circles. Bright colors. Hours of focused fun for tiny hands."
    elif "coloring" in meta.book_id:
        hook = "Slow down. Pick a page. Let color do the talking."
    elif "spot-difference" in meta.book_id:
        hook = "Easy on the eyes. Sharp on the mind. Perfect for daily brain training."
    elif "fishing" in meta.book_id:
        hook = "Every cast tells a story. Log it before you forget the one that got away."
    elif "dog-health" in meta.book_id:
        hook = "Healthier dog. Happier vet visits. Train and track in one book."
    elif "airbnb" in meta.book_id:
        hook = "Turn one-time stays into 5-star reviews and lifelong memories."
    elif "zodiac" in meta.book_id:
        hook = "12 zodiac mandalas to color your way to calm."

    inside_items = []
    if "password" in meta.book_id:
        inside_items = [
            "A-Z alphabetical tabs for instant lookup",
            "Hundreds of entries with Website / URL / Username / Password / Email / Notes",
            "Large, easy-to-read print",
            "Wi-Fi & router credential pages",
            "Software license & subscription tracker",
            "Notes pages at the back",
        ]
    elif "budget" in meta.book_id:
        inside_items = [
            "Annual financial overview with goal-setting prompts",
            "Monthly budget sheets — joint + individual columns",
            "Bill tracker, debt payoff log, savings goal pages",
            "Net worth & income/expense summaries",
            "Year-end review pages",
        ]
    elif "sleep" in meta.book_id:
        inside_items = [
            "Daily sleep log with bedtime, wake time & quality scoring",
            "Caffeine, exercise & screen-time trigger trackers",
            "Weekly review with trend graphs",
            "Sleep environment checklist",
            "Notes for your doctor",
        ]
    elif "blood-pressure" in meta.book_id:
        inside_items = [
            "Daily BP log (systolic / diastolic / pulse)",
            "Morning + evening reading slots",
            "Weekly summary with averages",
            "Medication tracker",
            "Doctor visit notes",
        ]
    elif "blood-sugar" in meta.book_id:
        inside_items = [
            "Pre-meal & post-meal glucose readings",
            "Insulin & medication log",
            "Carb count column",
            "Weekly trend pages",
            "A1C tracker",
        ]
    elif "yoga" in meta.book_id:
        inside_items = [
            "Daily session log (style, duration, poses)",
            "Pose progression tracker",
            "Mood & energy ratings",
            "Monthly reflection pages",
            "Goal milestones",
        ]
    elif "meal-prep" in meta.book_id:
        inside_items = [
            "Weekly meal planner pages",
            "Grocery shopping list templates",
            "Pantry inventory pages",
            "Recipe tracker",
            "Macros & calorie log",
        ]
    elif "caregiver" in meta.book_id:
        inside_items = [
            "Daily care log (vitals, meals, medications, mood)",
            "Weekly health-trend summaries",
            "Medication master list",
            "Appointment & emergency-contact pages",
            "Care recipient information page",
        ]
    elif "adhd" in meta.book_id:
        inside_items = [
            "Brain-dump pages",
            "Daily 3-priority planner",
            "Time-block templates",
            "Habit tracker",
            "Win journal",
        ]
    elif "introvert" in meta.book_id:
        inside_items = [
            "30-day confidence challenges",
            "Reflection prompts for social anxiety",
            "Boundary-setting worksheets",
            "Energy management trackers",
            "Win journal",
        ]
    elif "genz" in meta.book_id:
        inside_items = [
            "Stress-trigger trackers",
            "Reframing exercises",
            "Coping-skill checklists",
            "Goal-setting templates",
            "Self-care reminders",
        ]
    elif "mental-reset" in meta.book_id:
        inside_items = [
            "30 daily journal prompts",
            "Mood & gratitude trackers",
            "Cognitive reframing templates",
            "Weekly check-ins",
            "Reset rituals",
        ]
    elif "math-workbook" in meta.book_id:
        inside_items = [
            "Addition & subtraction up to 20",
            "Number-sense games",
            "Word problems with simple visuals",
            "Daily mini-quiz pages",
            "Sticker reward chart",
        ]
    elif "dot-marker" in meta.book_id:
        inside_items = [
            "Bold, easy-to-fill dot patterns",
            "Animals, numbers, alphabet themes",
            "Single-sided pages (no bleed-through)",
            "Big print for tiny hands",
            "Hours of mess-free fun",
        ]
    elif "bold-easy-coloring" in meta.book_id:
        inside_items = [
            "Bold-line designs (no fine detail)",
            "Animals from forest, farm, ocean & jungle",
            "Single-sided pages",
            "Wide margins for cutting & framing",
        ]
    elif "cottagecore-coloring" in meta.book_id:
        inside_items = [
            "Cozy cottage scenes",
            "Floral & garden patterns",
            "Single-sided pages",
            "Calming, slow-living theme",
        ]
    elif "spot-difference-seniors" in meta.book_id:
        inside_items = [
            "Large-print puzzle pages",
            "5-7 differences per puzzle",
            "Easy-to-medium difficulty",
            "Solutions at the back",
            "Memory-friendly design",
        ]
    elif "zodiac" in meta.book_id:
        inside_items = [
            "12 zodiac mandalas",
            "Astrology-themed details",
            "Single-sided print",
            "Calming & meditative",
        ]
    elif "fishing" in meta.book_id:
        inside_items = [
            "Trip log (location / weather / tide)",
            "Catch records (species / size / bait)",
            "Tackle inventory",
            "Best-spot map pages",
        ]
    elif "dog-health" in meta.book_id:
        inside_items = [
            "Vet visit & vaccine log",
            "Medication & supplement tracker",
            "Daily training log",
            "Weight & exercise charts",
            "Emergency-contact page",
        ]
    elif "airbnb" in meta.book_id:
        inside_items = [
            "Guest sign-in pages",
            "Local recommendations",
            "Memorable moments column",
            "Property details page",
        ]
    else:
        inside_items = [
            f"{pages} pages of structured layouts",
            "Daily, weekly, and monthly review templates",
            "Goal & habit trackers",
            "Reflection prompts",
            "Notes & summary pages",
        ]

    why_items = [
        "Designed by an indie publisher who uses it daily",
        "Clean, professional layout — no clutter",
        "Sturdy paperback that lays flat for easy writing",
    ]

    perfect_for: list[str]
    aud = _audience(meta)
    perfect_for = [
        f"{aud} who want a simple, paper-first system",
        "Anyone tired of apps & notifications",
        "A thoughtful, useful gift",
    ]

    details = [
        "Size: 8.5 x 11 inches (US Letter)",
        f"Pages: {pages}",
        "Paper: White, 60lb",
        "Cover: Matte softcover",
        "Print: Black & white interior",
    ]

    cta = (
        "Order yours today — and grab an extra copy for someone you care about."
    )
    if "gift" in (meta.subtitle + meta.description).lower():
        cta = "Add to cart now — perfect for birthdays, holidays, and 'just because' moments."

    li = lambda items: "\n".join(f"  <li>{x}</li>" for x in items)

    html = f"""<p><strong>{hook}</strong></p>

<p>{_seed_or("If you've struggled to stay consistent, you're not alone. This book gives you a simple, paper-first system that works without batteries, apps, or notifications.")}</p>

<p><strong>WHAT'S INSIDE:</strong></p>
<ul>
{li(inside_items)}
</ul>

<p><strong>WHY THIS BOOK:</strong></p>
<ul>
{li(why_items)}
</ul>

<p><strong>PERFECT FOR:</strong></p>
<ul>
{li(perfect_for)}
</ul>

<p><strong>BOOK DETAILS:</strong></p>
<ul>
{li(details)}
</ul>

<p><em>{cta}</em></p>
"""
    return html


# -------- 메인 일괄 실행 --------
def main() -> int:
    genre_map = load_genre_map()

    book_dirs = sorted(
        [d for d in BASE.iterdir() if d.is_dir() and (d / "KDP_LISTING.md").exists()]
    )
    print(f"[i] PyMuPDF available: {HAS_FITZ}")
    print(f"[i] Discovered {len(book_dirs)} books with KDP_LISTING.md")
    if not book_dirs:
        print("[!] No books found.")
        return 1

    # 메타 일괄 파싱 (Module 3 cross-reference 위해)
    metas: dict[str, BookMeta] = {}
    for d in book_dirs:
        m = parse_listing(d)
        if m:
            metas[m.book_id] = m

    total_modules = 0
    total_books_ok = 0
    total_books_fail = 0
    failures: list[tuple[str, str]] = []
    pdf_render_success = 0
    pdf_render_total = 0

    for book_id, meta in metas.items():
        book_dir = BASE / book_id
        out_dir = book_dir / "aplus"
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            primary, secondary, _ = get_palette(book_id, genre_map)

            # Module 1
            render_module1(meta, primary, secondary, out_dir / "module1.png")
            total_modules += 1

            # Module 2 (4 panels)
            m2 = render_module2(meta, primary, secondary, out_dir)
            total_modules += 4
            for label, ok in m2.items():
                pdf_render_total += 1
                if ok:
                    pdf_render_success += 1

            # Module 3 (series comparison)
            series_name, member_ids = find_series(book_id)
            members = [metas[mid] for mid in member_ids if mid in metas]
            if not members:
                members = [meta]
            render_module3(meta, members, primary, secondary, out_dir / "module3.png")
            total_modules += 1

            # KDP description HTML
            html = build_kdp_description_html(meta)
            (book_dir / "kdp_description.html").write_text(html, encoding="utf-8")

            total_books_ok += 1
            print(f"  [OK] {book_id}  (series={series_name}, members={len(members)})")
        except Exception as e:
            total_books_fail += 1
            failures.append((book_id, f"{type(e).__name__}: {e}"))
            print(f"  [FAIL] {book_id}: {e}")
            traceback.print_exc()

    print("\n=== A+ Content Generation Summary ===")
    print(f"  Books OK    : {total_books_ok}")
    print(f"  Books FAIL  : {total_books_fail}")
    print(f"  Modules generated (PNG): {total_modules}")
    print(f"  PDF page renders: {pdf_render_success}/{pdf_render_total} succeeded")
    if failures:
        print("  Failures:")
        for bid, err in failures:
            print(f"    - {bid}: {err}")
    return 0 if total_books_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
