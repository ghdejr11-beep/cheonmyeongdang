"""
output/book.md → output/exit_playbook.pdf 변환.
한국어 폰트 자동 다운로드.
"""

import re
import sys
import urllib.request
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether,
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import config

FONTS_DIR = Path(__file__).resolve().parent / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

NANUM_REG = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
NANUM_BOLD = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"


def ensure_fonts():
    reg = FONTS_DIR / "NanumGothic-Regular.ttf"
    bold = FONTS_DIR / "NanumGothic-Bold.ttf"
    if not reg.exists():
        print("  나눔고딕 다운로드 중...")
        urllib.request.urlretrieve(NANUM_REG, reg)
        urllib.request.urlretrieve(NANUM_BOLD, bold)
    return reg, bold


def setup():
    reg, bold = ensure_fonts()
    pdfmetrics.registerFont(TTFont("Nanum", str(reg)))
    pdfmetrics.registerFont(TTFont("Nanum-Bold", str(bold)))
    return {
        "h1": ParagraphStyle("h1", fontName="Nanum-Bold", fontSize=22, leading=30,
                             textColor=colors.HexColor("#1a1a2e"), spaceAfter=14, spaceBefore=10),
        "h2": ParagraphStyle("h2", fontName="Nanum-Bold", fontSize=16, leading=22,
                             textColor=colors.HexColor("#2a4e7a"), spaceAfter=8, spaceBefore=14),
        "h3": ParagraphStyle("h3", fontName="Nanum-Bold", fontSize=12, leading=18,
                             textColor=colors.HexColor("#2a2a4e"), spaceAfter=6),
        "body": ParagraphStyle("body", fontName="Nanum", fontSize=11, leading=18,
                               textColor=colors.HexColor("#202020"), spaceAfter=8),
        "title": ParagraphStyle("title", fontName="Nanum-Bold", fontSize=26, leading=34,
                                textColor=colors.HexColor("#1a1a2e"), alignment=1, spaceAfter=20),
        "sub": ParagraphStyle("sub", fontName="Nanum", fontSize=14, leading=20,
                              textColor=colors.HexColor("#555"), alignment=1, spaceAfter=20),
    }


def esc(s):
    return (str(s) if s else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md_to_story(md: str, styles):
    story = []
    in_box = False
    for raw in md.split("\n"):
        line = raw.rstrip()
        if not line:
            story.append(Spacer(1, 4))
            continue
        if line.startswith("# "):
            story.append(Paragraph(esc(line[2:]), styles["h1"]))
        elif line.startswith("## "):
            story.append(Paragraph(esc(line[3:]), styles["h2"]))
        elif line.startswith("### "):
            story.append(Paragraph(esc(line[4:]), styles["h3"]))
        elif line.startswith("---"):
            story.append(PageBreak())
        elif line.startswith(("- ", "* ")):
            story.append(Paragraph("• " + esc(line[2:]), styles["body"]))
        elif re.match(r"^\d+\.\s", line):
            story.append(Paragraph(esc(line), styles["body"]))
        else:
            text = esc(line).replace("**", "")
            story.append(Paragraph(text, styles["body"]))
    return story


def build_pdf(md_path: Path, out: Path):
    styles = setup()
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=22*mm, bottomMargin=22*mm,
                            title=config.BOOK_TITLE, author=config.AUTHOR)
    md = md_path.read_text(encoding="utf-8")
    story = md_to_story(md, styles)
    doc.build(story)
    print(f"  ✓ PDF: {out} ({out.stat().st_size//1024} KB)")


def main():
    if not config.BOOK_MD_PATH.exists():
        print(f"ERROR: {config.BOOK_MD_PATH} 없음")
        print("       먼저 'python generate_book.py' 실행 (Claude API)")
        print("       또는 'python sample.py' (즉시 사용 가능 샘플)")
        return 1
    build_pdf(config.BOOK_MD_PATH, config.BOOK_PDF_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
