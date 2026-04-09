"""
output/book.md → output/book.pdf 변환 (reportlab 기반).
한국어 폰트(나눔고딕)는 처음 1회만 자동 다운로드한다.

v2: reportlab 전환
  이전 fpdf2 기반 버전은 긴 한국어 문장 + 특수문자 조합에서
  "FPDFException: Not enough horizontal space" 에러가 발생.
  reportlab 은 한국어 + 긴 텍스트 처리가 훨씬 안정적.
"""

import re
import sys
import urllib.request
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import config

ROOT = Path(__file__).parent
OUT = ROOT / config.OUTPUT_DIR
FONTS = ROOT / config.FONTS_DIR
FONTS.mkdir(exist_ok=True)

NANUM_REGULAR_URL = (
    "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
)
NANUM_BOLD_URL = (
    "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
)


def ensure_fonts() -> tuple[Path, Path]:
    reg = FONTS / "NanumGothic-Regular.ttf"
    bold = FONTS / "NanumGothic-Bold.ttf"
    if not reg.exists() or reg.stat().st_size < 100_000:
        print("  나눔고딕 Regular 다운로드 중...")
        urllib.request.urlretrieve(NANUM_REGULAR_URL, reg)
    if not bold.exists() or bold.stat().st_size < 100_000:
        print("  나눔고딕 Bold 다운로드 중...")
        urllib.request.urlretrieve(NANUM_BOLD_URL, bold)
    return reg, bold


def setup_styles() -> dict:
    reg, bold = ensure_fonts()
    pdfmetrics.registerFont(TTFont("Nanum", str(reg)))
    pdfmetrics.registerFont(TTFont("Nanum-Bold", str(bold)))

    return {
        "title": ParagraphStyle(
            "title",
            fontName="Nanum-Bold",
            fontSize=28,
            leading=36,
            textColor=colors.HexColor("#1a1a2e"),
            alignment=1,  # center
            spaceAfter=20,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Nanum",
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#555"),
            alignment=1,
            spaceAfter=30,
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName="Nanum-Bold",
            fontSize=22,
            leading=30,
            textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=14,
            spaceBefore=16,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Nanum-Bold",
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#2a4e7a"),
            spaceAfter=8,
            spaceBefore=14,
        ),
        "h3": ParagraphStyle(
            "h3",
            fontName="Nanum-Bold",
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#2a2a4e"),
            spaceAfter=6,
            spaceBefore=10,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Nanum",
            fontSize=11,
            leading=18,
            textColor=colors.HexColor("#202020"),
            spaceAfter=8,
            alignment=0,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Nanum",
            fontSize=11,
            leading=18,
            textColor=colors.HexColor("#202020"),
            spaceAfter=4,
            leftIndent=16,
        ),
        "quote": ParagraphStyle(
            "quote",
            fontName="Nanum",
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#444"),
            backColor=colors.HexColor("#f6f6f8"),
            borderColor=colors.HexColor("#ddd"),
            borderWidth=0.5,
            borderPadding=6,
            leftIndent=6,
            rightIndent=6,
            spaceAfter=8,
        ),
    }


def esc(s: str) -> str:
    """reportlab Paragraph 용 XML 이스케이프."""
    if not s:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def inline_format(text: str) -> str:
    """마크다운 인라인 서식 → reportlab 태그 변환."""
    # 이미 이스케이프된 텍스트 위에서 동작
    # 볼드: **text** → <b>text</b>
    text = re.sub(r"\*\*([^*]+?)\*\*", r"<b>\1</b>", text)
    # 이탤릭: *text* → <i>text</i>
    text = re.sub(r"(?<![*])\*([^*\n]+?)\*(?![*])", r"<i>\1</i>", text)
    return text


def md_to_story(md: str, styles: dict) -> list:
    """마크다운 → reportlab flowables 리스트."""
    story = []
    in_code = False
    code_buffer: list[str] = []

    lines = md.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        i += 1

        # 코드 블록 ``` ~ ```
        if line.startswith("```"):
            if in_code:
                # 종료 → 버퍼 flush
                code_text = esc("\n".join(code_buffer)).replace("\n", "<br/>")
                if code_text:
                    try:
                        story.append(Paragraph(code_text, styles["quote"]))
                    except Exception as e:
                        print(f"    [경고] 코드 블록 렌더 실패: {e}")
                code_buffer = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buffer.append(line)
            continue

        if not line:
            story.append(Spacer(1, 4))
            continue

        # 페이지 나누기 (---)
        if line.startswith("---"):
            story.append(PageBreak())
            continue

        # 헤딩
        if line.startswith("# "):
            story.append(Paragraph(inline_format(esc(line[2:].strip())), styles["h1"]))
            continue
        if line.startswith("## "):
            story.append(Paragraph(inline_format(esc(line[3:].strip())), styles["h2"]))
            continue
        if line.startswith("### "):
            story.append(Paragraph(inline_format(esc(line[4:].strip())), styles["h3"]))
            continue

        # 불릿
        if line.startswith(("- ", "* ")):
            text = "• " + inline_format(esc(line[2:].strip()))
            try:
                story.append(Paragraph(text, styles["bullet"]))
            except Exception as e:
                print(f"    [경고] 불릿 렌더 실패: {line[:50]}... ({e})")
                # 그냥 plain text 로 재시도
                story.append(Paragraph(esc(line[2:].strip()), styles["body"]))
            continue

        # 번호 리스트
        if re.match(r"^\d+\.\s", line):
            text = inline_format(esc(line))
            story.append(Paragraph(text, styles["body"]))
            continue

        # 인용
        if line.startswith("> "):
            story.append(Paragraph(inline_format(esc(line[2:].strip())), styles["quote"]))
            continue

        # 일반 본문
        text = inline_format(esc(line))
        try:
            story.append(Paragraph(text, styles["body"]))
        except Exception as e:
            print(f"    [경고] 본문 렌더 실패: {line[:50]}... ({e})")

    # 닫히지 않은 코드 블록
    if code_buffer:
        code_text = esc("\n".join(code_buffer)).replace("\n", "<br/>")
        story.append(Paragraph(code_text, styles["quote"]))

    return story


def md_to_pdf(md_path: Path, out_path: Path) -> None:
    styles = setup_styles()

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title=getattr(config, "BOOK_TITLE", "전자책"),
        author=getattr(config, "AUTHOR", "덕구네 출판"),
    )

    md = md_path.read_text(encoding="utf-8")
    story = md_to_story(md, styles)
    print(f"  총 {len(story):,}개 블록 처리")
    doc.build(story)

    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"  ✓ PDF 저장: {out_path} ({size_mb:.2f} MB)")


def main() -> int:
    md_path = OUT / "book.md"
    if not md_path.exists():
        print(f"ERROR: {md_path} 없음. 먼저 'python generate_book.py' 실행")
        return 1

    out_path = OUT / "book.pdf"
    print("=" * 60)
    print(f" PDF 변환 (reportlab): {md_path.name} → {out_path.name}")
    print("=" * 60)

    try:
        md_to_pdf(md_path, out_path)
    except ModuleNotFoundError as e:
        print(f"\n❌ reportlab 이 설치되지 않았습니다: {e}")
        print("   python -m pip install reportlab")
        return 1

    print("\n완료. 이 PDF 를 Gumroad/크몽에 업로드하면 됩니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
