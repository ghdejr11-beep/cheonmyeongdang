"""
output/prompts.json → output/prompt_pack_1000.pdf 변환.

사용법:
    python make_prompt_pdf.py

reportlab + NanumGothic 사용. 한국어 완벽 지원.
폰트는 /tmp/ 또는 fonts/ 폴더에서 자동 탐색, 없으면 다운로드.
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
    Table, TableStyle, KeepTogether, Preformatted,
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import config

FONTS_DIR = Path(__file__).resolve().parent / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

NANUM_REGULAR_URL = (
    "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
)
NANUM_BOLD_URL = (
    "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
)


def ensure_fonts() -> tuple[Path, Path]:
    reg = FONTS_DIR / "NanumGothic-Regular.ttf"
    bold = FONTS_DIR / "NanumGothic-Bold.ttf"
    if not reg.exists():
        print(f"  나눔고딕 Regular 다운로드 중...")
        urllib.request.urlretrieve(NANUM_REGULAR_URL, reg)
    if not bold.exists():
        print(f"  나눔고딕 Bold 다운로드 중...")
        urllib.request.urlretrieve(NANUM_BOLD_URL, bold)
    return reg, bold


def setup_styles():
    reg, bold = ensure_fonts()
    pdfmetrics.registerFont(TTFont("Nanum", str(reg)))
    pdfmetrics.registerFont(TTFont("Nanum-Bold", str(bold)))

    styles = {}
    styles["cover_title"] = ParagraphStyle(
        "cover_title",
        fontName="Nanum-Bold",
        fontSize=28,
        leading=36,
        textColor=colors.HexColor("#1a1a2e"),
        alignment=1,  # center
        spaceAfter=20,
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub",
        fontName="Nanum",
        fontSize=16,
        leading=22,
        textColor=colors.HexColor("#555"),
        alignment=1,
        spaceAfter=30,
    )
    styles["h1"] = ParagraphStyle(
        "h1",
        fontName="Nanum-Bold",
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=16,
        spaceBefore=10,
    )
    styles["h2"] = ParagraphStyle(
        "h2",
        fontName="Nanum-Bold",
        fontSize=14,
        leading=20,
        textColor=colors.HexColor("#2a4e7a"),
        spaceAfter=6,
        spaceBefore=14,
    )
    styles["h3"] = ParagraphStyle(
        "h3",
        fontName="Nanum-Bold",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#2a2a4e"),
        spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Nanum",
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#202020"),
        spaceAfter=6,
    )
    styles["label"] = ParagraphStyle(
        "label",
        fontName="Nanum-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#707088"),
    )
    styles["prompt"] = ParagraphStyle(
        "prompt",
        fontName="Nanum",
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#1a1a2e"),
        backColor=colors.HexColor("#f5f5f7"),
        borderColor=colors.HexColor("#ddd"),
        borderWidth=0.5,
        borderPadding=8,
        leftIndent=4,
        rightIndent=4,
        spaceAfter=8,
    )
    return styles


def build_pdf(prompts: list, out_path: Path):
    styles = setup_styles()

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=config.PRODUCT_TITLE,
        author=config.AUTHOR,
    )

    story = []

    # ============================================================
    # 표지
    # ============================================================
    story.append(Spacer(1, 80))
    story.append(Paragraph("Claude·ChatGPT", styles["cover_title"]))
    story.append(Paragraph("실전 프롬프트 1,000개", styles["cover_title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("업종별 완전 정복", styles["cover_sub"]))
    story.append(Paragraph("복붙하면 바로 쓰는 한국어 프롬프트 모음집", styles["cover_sub"]))
    story.append(Spacer(1, 80))
    story.append(Paragraph(f"{config.AUTHOR}", styles["body"]))
    story.append(PageBreak())

    # ============================================================
    # 카테고리별 통계
    # ============================================================
    story.append(Paragraph("목차 & 카테고리", styles["h1"]))
    story.append(Spacer(1, 10))

    by_cat = {}
    for p in prompts:
        cid = p.get("category", "unknown")
        by_cat.setdefault(cid, []).append(p)

    table_data = [["#", "카테고리", "프롬프트 수"]]
    for cat in config.CATEGORIES:
        count = len(by_cat.get(cat["id"], []))
        table_data.append([str(cat["num"]), cat["name"], f"{count}개"])
    table_data.append(["", "합계", f"{len(prompts):,}개"])

    table = Table(table_data, colWidths=[12 * mm, 120 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Nanum"),
        ("FONTNAME", (0, 0), (-1, 0), "Nanum-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Nanum-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8e8f0")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#ccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("사용법", styles["h2"]))
    story.append(Paragraph(
        "각 프롬프트는 '상황 → 프롬프트 본문 → 예상 결과' 3단 구조로 되어있습니다. "
        "대괄호 [ ]로 묶인 부분은 여러분의 상황에 맞게 교체하면 됩니다. "
        "예: [제품명] → 나의 실제 제품 이름",
        styles["body"]
    ))
    story.append(Paragraph(
        "복붙한 프롬프트를 ChatGPT 또는 Claude.ai 에 붙여넣기만 하면 됩니다. "
        "모델은 Claude Sonnet 4.5 또는 Opus 4.5 를 추천합니다.",
        styles["body"]
    ))
    story.append(PageBreak())

    # ============================================================
    # 카테고리별 프롬프트 페이지
    # ============================================================
    for cat in config.CATEGORIES:
        cat_prompts = by_cat.get(cat["id"], [])
        if not cat_prompts:
            continue

        # 카테고리 표지
        story.append(Spacer(1, 40))
        story.append(Paragraph(cat["name"], styles["h1"]))
        story.append(Paragraph(cat["description"], styles["body"]))
        story.append(Paragraph(f"총 {len(cat_prompts)}개 프롬프트", styles["label"]))
        story.append(PageBreak())

        # 각 프롬프트
        for p in cat_prompts:
            block = []
            num = p.get("num", "?")
            title = p.get("title", "제목 없음")
            situation = p.get("situation", "")
            prompt_body = p.get("prompt", "")
            expected = p.get("expected", "")

            block.append(Paragraph(f"#{num}. {escape_xml(title)}", styles["h3"]))
            if situation:
                block.append(Paragraph(
                    f"<b>📍 상황:</b> {escape_xml(situation)}",
                    styles["body"]
                ))

            if prompt_body:
                block.append(Paragraph("💬 프롬프트:", styles["label"]))
                # 줄바꿈 보존
                formatted = escape_xml(prompt_body).replace("\n", "<br/>")
                block.append(Paragraph(formatted, styles["prompt"]))

            if expected:
                block.append(Paragraph(
                    f"<b>✅ 기대 결과:</b> {escape_xml(expected)}",
                    styles["body"]
                ))

            block.append(Spacer(1, 8))
            story.append(KeepTogether(block))

        story.append(PageBreak())

    # ============================================================
    # 뒷면
    # ============================================================
    story.append(Paragraph("이 책의 가치", styles["h1"]))
    story.append(Paragraph(
        f"이 PDF 는 한국 AI 활용 실무자를 위해 설계된 {len(prompts):,}개의 프롬프트 "
        f"모음집입니다. 각 프롬프트는 실제 업무 상황에서 검증된 구조로 구성되어 있으며, "
        f"복붙한 후 플레이스홀더만 교체하면 바로 사용 가능합니다.",
        styles["body"]
    ))
    story.append(Paragraph(
        "프롬프트 엔지니어링의 원리, 재사용 가능한 템플릿 구조, 카테고리별 베스트 프랙티스 등을 "
        "한 번에 학습할 수 있어, 단순한 프롬프트 사전을 넘어 'AI 활용의 교과서' 로 사용할 수 있습니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 16))

    story.append(Paragraph("함께 보면 좋은 상품", styles["h2"]))
    story.append(Paragraph(
        "『AI(Claude·ChatGPT)로 월 500만원 디지털 상품 자동화 시스템』 — 이 프롬프트 팩과 함께 "
        "사용하면 시너지가 극대화됩니다. 프롬프트 팩이 '무엇을 입력할 것인가' 를 해결한다면, "
        "본책은 '그 결과물로 어떻게 돈을 벌 것인가' 를 다룹니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 16))

    story.append(Paragraph("7일 100% 환불 보장", styles["h2"]))
    story.append(Paragraph(
        "구매 후 7일 안에 '도움 안 됐다' 고 판단되시면 이유 묻지 않고 100% 환불해드립니다. "
        "다운로드하신 PDF 는 그대로 가지셔도 됩니다.",
        styles["body"]
    ))

    doc.build(story)
    size_kb = out_path.stat().st_size / 1024
    print(f"  ✓ PDF 저장: {out_path} ({size_kb:.1f} KB)")


def escape_xml(text: str) -> str:
    """reportlab Paragraph 는 간단한 HTML/XML 태그를 지원하므로 특수문자 이스케이프."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def main() -> int:
    if not config.PROMPTS_JSON.exists():
        print(f"ERROR: {config.PROMPTS_JSON} 없음")
        print("       먼저 'python generate_prompts.py' 실행")
        return 1

    print("=" * 70)
    print(f" PDF 생성: {config.PRODUCT_TITLE}")
    print("=" * 70)

    data = json.loads(config.PROMPTS_JSON.read_text(encoding="utf-8"))
    prompts = data.get("prompts", [])
    if not prompts:
        print("ERROR: 프롬프트가 비어있습니다")
        return 1

    print(f"불러온 프롬프트: {len(prompts):,}개")
    build_pdf(prompts, config.PROMPTS_PDF)
    return 0


if __name__ == "__main__":
    sys.exit(main())
