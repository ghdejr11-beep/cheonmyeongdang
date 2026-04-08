"""
templates.json → notion_templates_50.pdf 변환.
한국어 폰트 자동 다운로드.
"""

import sys
import json
import urllib.request
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether,
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
        "title": ParagraphStyle("title", fontName="Nanum-Bold", fontSize=26, leading=34,
                                textColor=colors.HexColor("#1a1a2e"), alignment=1, spaceAfter=20),
        "sub": ParagraphStyle("sub", fontName="Nanum", fontSize=14, leading=20,
                              textColor=colors.HexColor("#555"), alignment=1, spaceAfter=20),
        "h1": ParagraphStyle("h1", fontName="Nanum-Bold", fontSize=22, leading=28,
                             textColor=colors.HexColor("#1a1a2e"), spaceAfter=14, spaceBefore=10),
        "h2": ParagraphStyle("h2", fontName="Nanum-Bold", fontSize=14, leading=20,
                             textColor=colors.HexColor("#2a4e7a"), spaceAfter=6, spaceBefore=12),
        "h3": ParagraphStyle("h3", fontName="Nanum-Bold", fontSize=12, leading=18,
                             textColor=colors.HexColor("#2a2a4e"), spaceAfter=4),
        "body": ParagraphStyle("body", fontName="Nanum", fontSize=10, leading=16,
                               textColor=colors.HexColor("#202020"), spaceAfter=6),
        "label": ParagraphStyle("label", fontName="Nanum-Bold", fontSize=9, leading=13,
                                textColor=colors.HexColor("#707088")),
        "box": ParagraphStyle("box", fontName="Nanum", fontSize=10, leading=15,
                              backColor=colors.HexColor("#f5f5f7"),
                              borderColor=colors.HexColor("#ddd"), borderWidth=0.5,
                              borderPadding=8, leftIndent=4, rightIndent=4, spaceAfter=6),
    }


def esc(s):
    return (str(s) if s else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_pdf(templates, out):
    s = setup()
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=20*mm, bottomMargin=20*mm,
                            title=config.PRODUCT_TITLE, author=config.AUTHOR)
    story = []

    # 표지
    story.append(Spacer(1, 80))
    story.append(Paragraph("노션 템플릿 50개", s["title"]))
    story.append(Paragraph("아이디어 + 판매 가이드", s["title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(config.PRODUCT_SUBTITLE, s["sub"]))
    story.append(Spacer(1, 80))
    story.append(Paragraph(config.AUTHOR, s["body"]))
    story.append(PageBreak())

    # 목차
    story.append(Paragraph("목차 — 50개 템플릿", s["h1"]))
    by_cat = {}
    for t in templates:
        by_cat.setdefault(t.get("category", "?"), []).append(t)
    rows = [["카테고리", "템플릿 수", "주요 예시"]]
    for cat in config.CATEGORIES:
        ts = by_cat.get(cat["id"], [])
        examples = ", ".join([t.get("name", "") for t in ts[:3]])
        rows.append([cat["name"], f"{len(ts)}개", examples or cat["examples"][:50]])
    table = Table(rows, colWidths=[55*mm, 22*mm, 90*mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Nanum"),
        ("FONTNAME", (0,0), (-1,0), "Nanum-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#ccc")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "각 템플릿마다 <b>이름·타깃·구조·제작법·판매가격·마케팅 카피·예상 매출</b> 까지 정리되어 있어, "
        "이 책 한 권으로 노션 템플릿 부업 사업을 100% 시작할 수 있습니다.",
        s["body"]))
    story.append(PageBreak())

    # 각 템플릿
    for cat in config.CATEGORIES:
        ts = by_cat.get(cat["id"], [])
        if not ts:
            continue
        story.append(Spacer(1, 30))
        story.append(Paragraph(cat["name"], s["h1"]))
        story.append(Paragraph(f"{len(ts)}개 템플릿", s["label"]))
        story.append(PageBreak())

        for t in ts:
            block = []
            block.append(Paragraph(f"#{t.get('num','?')}. {esc(t.get('name','이름 없음'))}", s["h3"]))
            if t.get("tagline"):
                block.append(Paragraph(f"<i>{esc(t['tagline'])}</i>", s["body"]))

            if t.get("target"):
                block.append(Paragraph(f"<b>👤 타깃:</b> {esc(t['target'])}", s["body"]))
            if t.get("scenario"):
                block.append(Paragraph(f"<b>📍 시나리오:</b> {esc(t['scenario'])}", s["body"]))

            if t.get("structure"):
                block.append(Paragraph("🗂️ 핵심 구조:", s["label"]))
                struct = "<br/>".join([f"• {esc(x)}" for x in t["structure"]])
                block.append(Paragraph(struct, s["box"]))

            if t.get("build_steps"):
                block.append(Paragraph("🛠️ 제작 단계:", s["label"]))
                steps = "<br/>".join([esc(x) for x in t["build_steps"]])
                block.append(Paragraph(steps, s["box"]))

            if t.get("price_krw"):
                block.append(Paragraph(
                    f"<b>💰 판매가:</b> {t['price_krw']:,}원 &nbsp;&nbsp; "
                    f"<b>📈 예상 월 매출:</b> {t.get('expected_revenue_monthly_krw', 0):,}원",
                    s["body"]))
            if t.get("marketing_copy"):
                block.append(Paragraph(f"<b>📢 마케팅 카피:</b> {esc(t['marketing_copy'])}", s["body"]))

            block.append(Spacer(1, 8))
            story.append(KeepTogether(block))

        story.append(PageBreak())

    # 마무리
    story.append(Paragraph("판매 시작하는 법", s["h1"]))
    story.append(Paragraph(
        "1. 위 50개 중 본인이 가장 잘 만들 수 있는 1개 선택<br/>"
        "2. 노션에서 해당 템플릿 직접 제작 (1~2시간)<br/>"
        "3. 노션 \"공유\" → \"웹에 게시\" → 복제 가능 링크 생성<br/>"
        "4. Gumroad/크몽에 상품 등록 (PDF + 노션 링크 제공)<br/>"
        "5. 인스타그램·블로그에 마케팅 카피로 홍보<br/>"
        "6. 첫 판매 완료 → 다음 템플릿 제작 → 무한 반복",
        s["body"]))
    story.append(Spacer(1, 16))
    story.append(Paragraph("7일 100% 환불 보장", s["h2"]))
    story.append(Paragraph(
        "구매 후 7일 안에 도움 안 됐다고 판단되면 이유 묻지 않고 100% 환불해드립니다.",
        s["body"]))

    doc.build(story)
    print(f"  ✓ PDF: {out} ({out.stat().st_size//1024:.0f} KB)")


def main():
    if not config.TEMPLATES_JSON.exists():
        print(f"ERROR: {config.TEMPLATES_JSON} 없음. 먼저 'python sample.py' 또는 'python generate_templates.py'")
        return 1
    data = json.loads(config.TEMPLATES_JSON.read_text(encoding="utf-8"))
    templates = data.get("templates", [])
    print(f"불러온 템플릿: {len(templates)}개")
    build_pdf(templates, config.GUIDE_PDF)
    return 0


if __name__ == "__main__":
    sys.exit(main())
