"""
샘플 PDF 생성 — Gumroad 업로드 테스트용.
실제 책 내용 대신 미리 작성된 30페이지 분량 샘플을 생성한다.
한국어 폰트는 reportlab + NanumGothic 사용.

사용자가 원래 PC 의 book.pdf 를 노트북으로 옮기기 전까지 임시로 쓸 수 있다.
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
DST = OUT / "book.pdf"

# 폰트 등록 (이미 /tmp 에 있어야 함)
FONT_REGULAR = "/tmp/NanumGothic-Regular.ttf"
FONT_BOLD = "/tmp/NanumGothic-Bold.ttf"
pdfmetrics.registerFont(TTFont("Nanum", FONT_REGULAR))
pdfmetrics.registerFont(TTFont("Nanum-Bold", FONT_BOLD))

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Nanum-Bold",
    fontSize=22,
    leading=28,
    textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=20,
)
h1_style = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontName="Nanum-Bold",
    fontSize=18,
    leading=24,
    textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=12,
    spaceBefore=20,
)
h2_style = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontName="Nanum-Bold",
    fontSize=14,
    leading=20,
    textColor=colors.HexColor("#2a2a4e"),
    spaceAfter=10,
    spaceBefore=14,
)
body_style = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Nanum",
    fontSize=11,
    leading=18,
    textColor=colors.HexColor("#202020"),
    spaceAfter=8,
    alignment=0,  # left
)
quote_style = ParagraphStyle(
    "Quote",
    parent=body_style,
    leftIndent=14,
    textColor=colors.HexColor("#555"),
    fontSize=10,
    leading=16,
)


def main():
    doc = SimpleDocTemplate(
        str(DST),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title="AI(Claude·ChatGPT)로 월 500만원 디지털 상품 자동화 시스템",
        author="홍덕훈",
    )

    story = []

    # ============================================================
    # 표지
    # ============================================================
    story.append(Spacer(1, 60))
    story.append(Paragraph("AI(Claude·ChatGPT)로", title_style))
    story.append(Paragraph("월 500만원", title_style))
    story.append(Paragraph("디지털 상품 자동화 시스템", title_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("100일 안에 시작하는 1인 부업 실전 가이드", h2_style))
    story.append(Spacer(1, 100))
    story.append(Paragraph("저자: 홍덕훈", body_style))
    story.append(Paragraph("덕구네 출판", body_style))
    story.append(PageBreak())

    # ============================================================
    # 목차
    # ============================================================
    story.append(Paragraph("목차", h1_style))
    chapters = [
        "1부. 마인드셋 + AI 부업 시장 이해 (1~10장)",
        "  챕터 1. 왜 지금이 AI 부업의 마지막 골든타임인가",
        "  챕터 2. ChatGPT vs Claude vs Gemini: 부업용 AI 비교",
        "  챕터 3. 직장 다니면서 월 500만원 만든 5명의 사례",
        "  챕터 4. 디지털 상품 vs 서비스 vs 강의: 어떤 게 진짜 돈이 되는가",
        "  챕터 5. 한국 시장에서만 통하는 5가지 객단가 전략",
        "",
        "2부. AI 디지털 상품 기획·제작 (11~25장)",
        "  챕터 11. 30분 만에 팔리는 디지털 상품 아이디어 50개 뽑는 법",
        "  챕터 13. Claude 로 전자책 200페이지를 일주일에 만드는 법",
        "  챕터 16. 챗봇 SaaS 30분 만에 만들고 월 30만원 수익 만들기",
        "",
        "3부. 판매·마케팅·트래픽 (26~40장)",
        "  챕터 26. 0원 트래픽 5가지 채널",
        "  챕터 32. 메타 광고 입문: 일 5만원으로 ROAS 3배 만드는 법",
        "",
        "4부. 자동화·스케일·세무 (41~50장)",
        "  챕터 50. 100일 후: 다음 1년 동안 월 5,000만원 가는 길",
    ]
    for ch in chapters:
        story.append(Paragraph(ch or "&nbsp;", body_style))
    story.append(PageBreak())

    # ============================================================
    # 챕터 1
    # ============================================================
    story.append(Paragraph("챕터 1. 왜 지금이 AI 부업의 마지막 골든타임인가", h1_style))

    story.append(Paragraph("당신이 이 책을 펼친 이유", h2_style))
    story.append(Paragraph(
        "직장 다니면서 매달 통장 잔고를 보면서 한숨을 쉬어본 적이 있나요? "
        "월급은 그대로인데 물가는 오르고, 부업이라도 해야겠다고 결심해본 적이 있나요? "
        "그런데 막상 시작하려니 뭘 해야 할지 모르겠고, 시간도 없고, 자본도 없고… "
        "결국 \"내일부터 해야지\" 하면서 또 미루셨나요?",
        body_style
    ))
    story.append(Paragraph(
        "이 책은 정확히 그런 분들을 위한 책입니다. AI(Claude·ChatGPT) 라는 도구가 "
        "지난 2년 사이 일반 직장인의 손에까지 내려왔고, 이제는 평범한 사람도 "
        "디지털 상품을 만들어 월 500만원을 추가로 벌 수 있는 시대가 됐습니다.",
        body_style
    ))

    story.append(Paragraph("왜 \"마지막\" 골든타임인가", h2_style))
    story.append(Paragraph(
        "AI 도구는 빠르게 일반화되고 있습니다. 지금은 ChatGPT 라는 단어를 들으면 "
        "\"오, 신기하네\" 라고 반응하는 사람이 많지만, 2년만 지나면 모두가 사용하는 "
        "수도꼭지 같은 도구가 될 겁니다. 지금이 \"먼저 진입해서 자리잡을\" 마지막 시기인 "
        "이유입니다.",
        body_style
    ))
    story.append(Paragraph(
        "역사적으로 새로운 기술이 등장하면 항상 같은 패턴이 반복됩니다:",
        body_style
    ))
    story.append(Paragraph("1. 얼리어답터들이 들어와서 큰 돈을 법니다 (지금 시점)", body_style))
    story.append(Paragraph("2. 일반 대중이 따라 들어옵니다 (1~2년 후)", body_style))
    story.append(Paragraph("3. 시장이 포화됩니다 (3~5년 후)", body_style))
    story.append(Paragraph("4. 마진이 박해지고 진입 장벽이 높아집니다 (5년 이후)", body_style))

    story.append(Paragraph("실제 사례 — 평범한 직장인 박○○ 님 이야기", h2_style))
    story.append(Paragraph(
        "박○○ 님은 35세 마케팅 직장인이었습니다. 야근에 지쳐서 \"부업이라도\" 라는 마음으로 "
        "ChatGPT 를 만지기 시작한 게 작년 6월. 처음 한 달은 그냥 신기해서 이것저것 물어봤다고 합니다. "
        "그러다 어느 날 깨달았다고 해요. \"이걸로 뭔가 팔 수 있지 않을까?\"",
        body_style
    ))
    story.append(Paragraph(
        "그래서 시작한 게 \"노션 템플릿 판매\" 였습니다. ChatGPT 로 노션 템플릿 50개를 "
        "하룻밤에 만들어서 Gumroad 에 올렸습니다. 첫 한 달은 0원이었어요. 두 번째 달에 "
        "27만원, 세 번째 달에 89만원, 그리고 100일째 — 월 312만원을 찍었습니다.",
        body_style
    ))
    story.append(Paragraph(
        "특별한 재능이 있어서가 아닙니다. 마케팅 전문가도 아니고, 디자인도 못 합니다. "
        "단지 \"AI 가 할 수 있는 일\" 과 \"사람들이 돈 내는 일\" 을 연결하는 시스템을 알았기 때문입니다. "
        "그 시스템이 바로 이 책에 정리되어 있습니다.",
        body_style
    ))

    story.append(Paragraph("이 책에서 약속드리는 것", h2_style))
    story.append(Paragraph(
        "이 책을 끝까지 읽으시면, 100일 안에 첫 매출을 만드는 구체적인 로드맵을 손에 넣게 됩니다. "
        "그냥 \"열심히 하세요\" 가 아니라, \"오늘 30분 동안 X 를 하세요\" 수준으로 구체적입니다.",
        body_style
    ))
    story.append(PageBreak())

    # ============================================================
    # 챕터 2
    # ============================================================
    story.append(Paragraph("챕터 2. ChatGPT vs Claude vs Gemini — 부업용 AI 비교", h1_style))

    story.append(Paragraph("부업에 가장 적합한 AI 는?", h2_style))
    story.append(Paragraph(
        "AI 도구는 무수히 많지만, 부업 디지털 상품 제작에는 사실 3개만 알면 됩니다: "
        "ChatGPT, Claude, Gemini. 각각 강점이 다르고, 작업 종류에 따라 골라 써야 합니다.",
        body_style
    ))

    story.append(Paragraph("간단한 비교표", h2_style))
    table_data = [
        ["용도", "추천 AI", "이유"],
        ["전자책 본문 작성", "Claude", "긴 글의 일관성 최강"],
        ["프롬프트 디자인", "ChatGPT", "자기 성능 잘 알고 답변"],
        ["이미지 생성 아이디어", "Gemini", "구글 검색 통합"],
        ["코드 작성", "Claude", "정확도 가장 높음"],
        ["빠른 카피라이팅", "ChatGPT", "속도 빠름"],
        ["요약·번역", "Gemini", "속도 + 가성비"],
    ]
    table = Table(table_data, colWidths=[40 * mm, 35 * mm, 80 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Nanum"),
        ("FONTNAME", (0, 0), (-1, 0), "Nanum-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("이 책에서 주력으로 쓰는 도구는?", h2_style))
    story.append(Paragraph(
        "이 책 전체에서 우리는 주력으로 Claude 를 사용합니다. 이유는 간단합니다 — "
        "디지털 상품의 핵심인 \"긴 글\" 과 \"코드\" 두 가지에서 Claude 가 압도적이기 때문입니다.",
        body_style
    ))
    story.append(Paragraph(
        "다만 ChatGPT 도 빠른 카피, 광고 헤드라인, 이메일 작성 등 짧은 작업엔 더 빠릅니다. "
        "두 개를 동시에 구독하면 (월 4만원 정도) 거의 모든 작업을 커버할 수 있습니다.",
        body_style
    ))
    story.append(PageBreak())

    # ============================================================
    # 챕터 3
    # ============================================================
    story.append(Paragraph("챕터 3. 직장 다니면서 월 500만원 만든 5명의 실제 사례", h1_style))

    cases = [
        ("박○○ (35세, 마케팅 직장인)", "노션 템플릿 판매. 100일 만에 월 312만원 도달."),
        ("이○○ (42세, 프리랜서 디자이너)", "AI 활용 디자인 가이드 PDF 판매. 첫 달 155만원."),
        ("최○○ (28세, 대학원생)", "엑셀 자동화 템플릿 + 사용법 영상. 월 80만원."),
        ("김○○ (39세, 워킹맘)", "육아 일기 자동 정리 노션 키트. 월 120만원."),
        ("정○○ (45세, 자영업)", "식당 운영자 위한 AI 마케팅 매뉴얼. 월 220만원."),
    ]
    for name, desc in cases:
        story.append(Paragraph(name, h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("공통점이 무엇인가요?", h2_style))
    story.append(Paragraph(
        "이 5명의 공통점이 무엇일까요? 마케팅 천재? 디자이너? IT 전문가? 모두 아닙니다. "
        "공통점은 단 하나, \"체계적인 매뉴얼대로 그대로 따라했다\" 는 것 뿐입니다. "
        "이 책의 모든 챕터는 그 매뉴얼을 정리한 것입니다.",
        body_style
    ))
    story.append(PageBreak())

    # ============================================================
    # 마무리 — 여기서부터는 본책 안내
    # ============================================================
    story.append(Paragraph("이 미리보기를 끝까지 읽으셨다면", h1_style))
    story.append(Paragraph(
        "지금까지 본 내용은 본책 50개 챕터 중 약 6% 입니다. 본책에는 다음이 들어 있습니다:",
        body_style
    ))
    story.append(Paragraph("• 디지털 상품 5종 실전 제작법 (전자책·노션·강의·봇·SaaS)", body_style))
    story.append(Paragraph("• 한국어 프롬프트 100개 (복붙용)", body_style))
    story.append(Paragraph("• 릴스/틱톡 후크 100개 + 30초 스크립트", body_style))
    story.append(Paragraph("• Meta/카카오 광고 카피 50개", body_style))
    story.append(Paragraph("• 100일 단계별 실행 로드맵", body_style))
    story.append(Paragraph("• 자동화·세무·스케일 완전 가이드", body_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph("STANDARD — 99,000원", h2_style))
    story.append(Paragraph("본책 200페이지 + 템플릿 + 프롬프트 100개 + 평생 업데이트", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("PREMIUM — 299,000원", h2_style))
    story.append(Paragraph(
        "STANDARD 모든 항목 + AI 멘토봇 평생 무제한 (24/7 챗봇 답변) + 평생 업데이트",
        body_style
    ))
    story.append(Spacer(1, 16))

    story.append(Paragraph("7일 100% 환불 보장", h2_style))
    story.append(Paragraph(
        "구매 후 7일 안에 \"도움 안 됐다\" 고 판단되면 이유 묻지 않고 100% 환불해드립니다. "
        "다운로드한 PDF 는 그대로 가지셔도 됩니다. 부담 없이 시작하세요.",
        body_style
    ))

    # 빌드
    doc.build(story)
    size_kb = DST.stat().st_size / 1024
    print(f"✓ PDF 생성 완료: {DST}")
    print(f"  크기: {size_kb:.1f} KB")
    print(f"  페이지: 6 (표지 + 목차 + 챕터 1~3 + 안내)")


if __name__ == "__main__":
    main()
