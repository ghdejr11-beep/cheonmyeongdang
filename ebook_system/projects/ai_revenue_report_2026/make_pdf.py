"""
book.md → book.pdf 빌더 (reportlab + NanumGothic).

실행: python make_pdf.py
"""

import re
import sys
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
OUT = ROOT / "output"
FONTS = ROOT / "fonts"


def setup_styles() -> dict:
    reg = FONTS / "NanumGothic-Regular.ttf"
    bold = FONTS / "NanumGothic-Bold.ttf"
    pdfmetrics.registerFont(TTFont("Nanum", str(reg)))
    pdfmetrics.registerFont(TTFont("Nanum-Bold", str(bold)))

    return {
        "title": ParagraphStyle(
            "title", fontName="Nanum-Bold", fontSize=28, leading=36,
            textColor=colors.HexColor("#1a1a2e"), alignment=1, spaceAfter=20,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="Nanum", fontSize=16, leading=22,
            textColor=colors.HexColor("#555"), alignment=1, spaceAfter=30,
        ),
        "h1": ParagraphStyle(
            "h1", fontName="Nanum-Bold", fontSize=22, leading=30,
            textColor=colors.HexColor("#1a1a2e"), spaceAfter=14, spaceBefore=16,
        ),
        "h2": ParagraphStyle(
            "h2", fontName="Nanum-Bold", fontSize=16, leading=22,
            textColor=colors.HexColor("#2a4e7a"), spaceAfter=8, spaceBefore=14,
        ),
        "h3": ParagraphStyle(
            "h3", fontName="Nanum-Bold", fontSize=13, leading=18,
            textColor=colors.HexColor("#2a2a4e"), spaceAfter=6, spaceBefore=10,
        ),
        "body": ParagraphStyle(
            "body", fontName="Nanum", fontSize=11, leading=18,
            textColor=colors.HexColor("#202020"), spaceAfter=8, alignment=0,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Nanum", fontSize=11, leading=18,
            textColor=colors.HexColor("#202020"), spaceAfter=4, leftIndent=16,
        ),
        "quote": ParagraphStyle(
            "quote", fontName="Nanum", fontSize=10, leading=15,
            textColor=colors.HexColor("#444"),
            backColor=colors.HexColor("#f6f6f8"),
            borderColor=colors.HexColor("#ddd"), borderWidth=0.5,
            borderPadding=6, leftIndent=6, rightIndent=6, spaceAfter=8,
        ),
    }


def esc(s: str) -> str:
    if not s:
        return ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_format(text: str) -> str:
    text = re.sub(r"\*\*([^*]+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*])\*([^*\n]+?)\*(?![*])", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+?)`", r'<font face="Courier" color="#a03030">\1</font>', text)
    return text


def md_to_story(md: str, styles: dict) -> list:
    story = []
    in_code = False
    code_buffer: list[str] = []

    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        i += 1

        if line.startswith("```"):
            if in_code:
                code_text = esc("\n".join(code_buffer)).replace("\n", "<br/>")
                if code_text:
                    try:
                        story.append(Paragraph(code_text, styles["quote"]))
                    except Exception as e:
                        print(f"    [경고] 코드 블록 실패: {e}")
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

        if line.startswith("---"):
            story.append(PageBreak())
            continue

        if line.startswith("# "):
            story.append(Paragraph(inline_format(esc(line[2:].strip())), styles["h1"]))
            continue
        if line.startswith("## "):
            story.append(Paragraph(inline_format(esc(line[3:].strip())), styles["h2"]))
            continue
        if line.startswith("### "):
            story.append(Paragraph(inline_format(esc(line[4:].strip())), styles["h3"]))
            continue

        if line.startswith(("- ", "* ")):
            text = "• " + inline_format(esc(line[2:].strip()))
            try:
                story.append(Paragraph(text, styles["bullet"]))
            except Exception as e:
                print(f"    [경고] 불릿 실패: {line[:50]} ({e})")
            continue

        if re.match(r"^\d+\.\s", line):
            story.append(Paragraph(inline_format(esc(line)), styles["body"]))
            continue

        if line.startswith("> "):
            story.append(Paragraph(inline_format(esc(line[2:].strip())), styles["quote"]))
            continue

        try:
            story.append(Paragraph(inline_format(esc(line)), styles["body"]))
        except Exception as e:
            print(f"    [경고] 본문 실패: {line[:50]} ({e})")

    if code_buffer:
        code_text = esc("\n".join(code_buffer)).replace("\n", "<br/>")
        story.append(Paragraph(code_text, styles["quote"]))

    return story


def md_to_pdf(md_path: Path, out_path: Path) -> None:
    styles = setup_styles()
    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm, topMargin=22*mm, bottomMargin=22*mm,
        title=config.BOOK_TITLE, author=config.AUTHOR,
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
        print(f"ERROR: {md_path} 없음")
        return 1
    out_path = OUT / "book.pdf"
    print("=" * 60)
    print(f" PDF 빌드: {config.BOOK_TITLE}")
    print("=" * 60)
    md_to_pdf(md_path, out_path)
    print("완료.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
