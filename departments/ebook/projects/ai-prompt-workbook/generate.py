"""
AI 프롬프트 워크북 (AI Prompt Workbook) - 표지 + 본문 PDF 생성기
- 50p 가이드 + 100p 프롬프트 100개 + 6p 부록 = 156p
- 노랑(#F4A261) + 파랑(#1D4ED8)
- 2026 한국 시장 (PromptBase 영어 위주, 한국어 진공)
"""
from __future__ import annotations
import os
import math
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = Path(__file__).parent
PRIMARY = HexColor("#F4A261")  # 노랑
SECONDARY = HexColor("#1D4ED8")  # 파랑
ACCENT_DARK = HexColor("#0E2A6B")
BG = HexColor("#FFF7E8")

W, H = 8.5 * inch, 11 * inch
W_BLEED, H_BLEED = 8.75 * inch, 11.25 * inch


def register_korean_font():
    candidates = [r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\NanumGothic.ttf"]
    for cand in candidates:
        if Path(cand).exists():
            try:
                pdfmetrics.registerFont(TTFont("KR", cand))
                bold = cand.replace(".ttf", "bd.ttf")
                if Path(bold).exists():
                    pdfmetrics.registerFont(TTFont("KR-Bold", bold))
                else:
                    pdfmetrics.registerFont(TTFont("KR-Bold", cand))
                return True
            except Exception:
                continue
    return False


HAS_KR = register_korean_font()
KR = "KR" if HAS_KR else "Helvetica"
KR_B = "KR-Bold" if HAS_KR else "Helvetica-Bold"


def make_cover():
    out = BASE / "cover.pdf"
    c = canvas.Canvas(str(out), pagesize=(W_BLEED, H_BLEED))
    # 파랑 배경
    c.setFillColor(SECONDARY)
    c.rect(0, 0, W_BLEED, H_BLEED, fill=1, stroke=0)
    # 상단 노랑 띠
    c.setFillColor(PRIMARY)
    c.rect(0, H_BLEED*0.7, W_BLEED, H_BLEED*0.3, fill=1, stroke=0)
    # 장식: GPT 아이콘 같은 별 / 다이아몬드 격자
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(1)
    for i in range(5):
        for j in range(5):
            cx = W_BLEED * (0.15 + i * 0.175)
            cy = H_BLEED * (0.32 + j * 0.06)
            c.setFillColor(HexColor("#FFD580"))
            c.circle(cx, cy, 2, fill=1, stroke=0)
    # GPT 마크 (육각형)
    cx, cy = W_BLEED/2, H_BLEED*0.55
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(3)
    p = c.beginPath()
    for k in range(6):
        ang = math.radians(60 * k - 30)
        x = cx + 35 * math.cos(ang)
        y = cy + 35 * math.sin(ang)
        if k == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    # GPT 텍스트
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(cx, cy - 8, "AI")
    # 타이틀
    c.setFillColor(SECONDARY)
    c.setFont(KR_B, 56)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.85, "AI 프롬프트")
    c.drawCentredString(W_BLEED/2, H_BLEED*0.78, "워크북")
    # 부제
    c.setFillColor(white)
    c.setFont(KR, 16)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.42, "200개 ChatGPT 템플릿 + 실습")
    c.setFont(KR, 13)
    c.setFillColor(PRIMARY)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.385, "글쓰기 / 마케팅 / 업무자동화 / 창작")
    # 데코 라인
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(2)
    c.line(W_BLEED*0.25, H_BLEED*0.35, W_BLEED*0.75, H_BLEED*0.35)
    # 배지
    c.setFillColor(PRIMARY)
    c.roundRect(W_BLEED*0.3, H_BLEED*0.22, W_BLEED*0.4, 0.5*inch, 8, fill=1)
    c.setFillColor(SECONDARY)
    c.setFont(KR_B, 14)
    c.drawCentredString(W_BLEED/2, H_BLEED*0.245, "초보 → 중급 한 권으로")
    # 저자명
    c.setFont(KR_B, 13)
    c.setFillColor(PRIMARY)
    c.drawCentredString(W_BLEED/2, 0.65*inch, "Deokgu Studio")
    c.save()
    print(f"  [ai-prompt-workbook] cover.pdf -> {os.path.getsize(out)/1024:.0f} KB")


def page_header(c, title, section=""):
    c.setFillColor(SECONDARY)
    c.rect(0, H - 0.5*inch, W, 0.5*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(KR_B, 14)
    c.drawString(0.85*inch, H - 0.32*inch, title)
    if section:
        c.setFont(KR, 10)
        c.setFillColor(PRIMARY)
        c.drawRightString(W - 0.75*inch, H - 0.32*inch, section)


def body(c, x, y, lines, size=11, leading=18):
    c.setFillColor(black)
    c.setFont(KR, size)
    cy = y
    for line in lines:
        c.drawString(x, cy, line)
        cy -= leading
    return cy


def make_interior():
    out = BASE / "ai_prompt_workbook.pdf"
    c = canvas.Canvas(str(out), pagesize=(W, H))
    M = 0.75 * inch
    M_INNER = 0.85 * inch

    # === 1. Title page ===
    c.setFillColor(SECONDARY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(PRIMARY)
    c.setFont(KR_B, 50)
    c.drawCentredString(W/2, H*0.6, "AI 프롬프트 워크북")
    c.setFont(KR, 18)
    c.setFillColor(white)
    c.drawCentredString(W/2, H*0.53, "200개 ChatGPT 템플릿 + 실습")
    c.setFont(KR, 13)
    c.drawCentredString(W/2, H*0.48, "글쓰기  |  마케팅  |  업무자동화  |  창작")
    c.setFont(KR_B, 14)
    c.setFillColor(PRIMARY)
    c.drawCentredString(W/2, H*0.15, "Deokgu Studio")
    c.showPage()

    # === 2. 목차 (1p) ===
    page_header(c, "목차 Contents")
    toc = [
        ("Part 1", "AI 프롬프트 시작하기", "p. 5"),
        ("Part 2", "프롬프트 엔지니어링 기본 7원칙", "p. 15"),
        ("Part 3", "분야별 프롬프트 200개", "p. 55"),
        ("  3-1", "글쓰기 프롬프트 50개", "p. 56"),
        ("  3-2", "마케팅 프롬프트 50개", "p. 76"),
        ("  3-3", "업무자동화 프롬프트 50개", "p. 96"),
        ("  3-4", "창작/아이디어 프롬프트 50개", "p. 116"),
        ("Part 4", "실습 워크시트", "p. 136"),
        ("부록", "추천 도구 & 다음 단계", "p. 150"),
    ]
    cy = H - 1.5*inch
    for part, title, page in toc:
        c.setFillColor(SECONDARY)
        c.setFont(KR_B, 13)
        c.drawString(M_INNER, cy, part)
        c.setFillColor(black)
        c.setFont(KR, 13)
        c.drawString(M_INNER + 0.7*inch, cy, title)
        c.setFillColor(HexColor("#666"))
        c.drawRightString(W - M, cy, page)
        cy -= 0.4*inch
    c.showPage()

    # === Part 1: AI 시작하기 (10p) ===
    p1_pages = [
        ("AI는 왜 지금 중요한가",
         ["2026년 현재, AI는 검색엔진처럼 일상 도구가 되었습니다.",
          "ChatGPT, Claude, Gemini 등 대형 언어 모델은 글쓰기, 분석, 번역,",
          "코딩, 기획까지 거의 모든 지식 작업의 동반자입니다.",
          "",
          "하지만 같은 AI를 써도 결과는 천차만별입니다.",
          "이유는 단 하나, 바로 '프롬프트(질문)'의 차이입니다.",
          "",
          "이 책은 AI에게 '제대로' 묻는 법을 200개의 실전 템플릿으로 가르쳐 드립니다."]),
        ("이 책의 사용법",
         ["1단계: Part 2를 먼저 읽고, 7원칙을 머리에 새깁니다.",
          "2단계: Part 3에서 자신의 분야를 골라 프롬프트를 그대로 복사해 사용해 봅니다.",
          "3단계: 결과가 나오면, Part 4 워크시트에 '내가 바꾼 부분'을 적습니다.",
          "4단계: 같은 프롬프트로 다른 AI에게도 물어 비교해 봅니다.",
          "",
          "한 권을 끝낼 때면, 자신만의 프롬프트 라이브러리가 만들어집니다."]),
        ("ChatGPT 시작하기 (5분)",
         ["1. chat.openai.com 접속 (또는 모바일 앱)",
          "2. 회원가입 (이메일 또는 구글)",
          "3. 무료 버전으로 시작 (GPT-3.5)",
          "4. 입력창에 프롬프트 복붙 → Enter",
          "5. 결과를 보고, 아쉬우면 '더 짧게', '예시 추가해서' 같이 추가 요청",
          "",
          "TIP: 한국어 프롬프트도 거의 영어와 같은 품질로 작동합니다."]),
        ("Claude 시작하기",
         ["1. claude.ai 접속",
          "2. 구글/이메일 회원가입",
          "3. 무료 버전 - 글쓰기와 분석에 강함",
          "",
          "Claude의 특징:",
          "  - 긴 글 처리 (10만 단어 이상)",
          "  - 안전성 우선",
          "  - 코드 설명이 명료",
          "  - 한국어 자연스러움 우수"]),
        ("Gemini 시작하기",
         ["1. gemini.google.com 접속",
          "2. 구글 계정 로그인",
          "3. 무료 - 검색 결합 강점",
          "",
          "Gemini의 특징:",
          "  - 실시간 웹 검색 결합",
          "  - 구글 워크스페이스 연동",
          "  - 이미지 생성 내장"]),
        ("어떤 AI를 언제 쓸까",
         ["글쓰기 / 보고서 → Claude (긴 글, 한국어 자연스러움)",
          "기획 / 브레인스토밍 → ChatGPT (창의력 강점)",
          "검색 + 요약 → Gemini (실시간 정보)",
          "코딩 → Claude / GPT-4 / GitHub Copilot",
          "이미지 생성 → Midjourney / DALL-E / Gemini",
          "",
          "이 책의 200개 프롬프트는 위 3개 모두에서 작동합니다."]),
        ("AI 사용 시 주의 4가지",
         ["1. 사실 확인 - AI는 종종 그럴듯한 거짓을 만듭니다 (할루시네이션)",
          "2. 개인정보 - 주민번호, 카드번호, 비밀번호 절대 입력 금지",
          "3. 저작권 - 생성물의 상업적 사용 시 약관 확인",
          "4. 의존도 - AI는 동반자이지 대체자가 아닙니다. 비판적 사고 유지."]),
    ]
    for title, lines in p1_pages:
        page_header(c, title, "Part 1")
        body(c, M_INNER, H - 1.5*inch, lines)
        c.showPage()
        # 노트 페이지 (각 챕터당)
        page_header(c, f"{title} - 노트", "Part 1")
        draw_lines_block(c, M_INNER, H - 1.5*inch, M)
        c.showPage()

    # === Part 2: 프롬프트 7원칙 (40p) ===
    principles = [
        ("원칙 1: 역할 부여 (Role)",
         ["AI에게 '당신은 ___ 전문가입니다'라고 시작합니다.",
          "역할이 구체적일수록 답변이 전문적이 됩니다.",
          "",
          "나쁜 예: 마케팅 글 써줘",
          "좋은 예: 당신은 10년차 카피라이터입니다. 30대 여성 대상 화장품 인스타 광고 문구를 5개 작성해 주세요."]),
        ("원칙 2: 맥락 제공 (Context)",
         ["배경 정보를 충분히 알려 주세요.",
          "  - 누가 (대상)",
          "  - 어디서 (플랫폼)",
          "  - 왜 (목적)",
          "  - 언제 (시점)",
          "",
          "맥락이 빠지면 AI는 평균적인 답변만 합니다."]),
        ("원칙 3: 출력 형식 지정 (Format)",
         ["결과의 형태를 명시합니다.",
          "  - '표로'  '5줄로'  '제목 + 본문 + 결론으로'",
          "  - 마크다운 / JSON / 한 줄 요약",
          "",
          "예: 답변을 표로 작성해 주세요. 컬럼은 [기능, 장점, 단점] 입니다."]),
        ("원칙 4: 예시 제공 (Few-shot)",
         ["원하는 결과의 예시를 1-3개 보여 주세요.",
          "AI는 패턴을 학습합니다.",
          "",
          "예: '다음 톤으로 5문장 더 만들어 주세요.\\n",
          "    예시1: 봄이 왔어요. 마음도 살짝 들떴어요.\\n",
          "    예시2: 비가 그치고 햇살이 났어요. 하루가 시작됐어요.'"]),
        ("원칙 5: 단계 분해 (Chain of Thought)",
         ["복잡한 작업은 '단계별로 생각하며' 해 달라고 합니다.",
          "",
          "예: '먼저 핵심 메시지 3개를 정리하고, 각각에 맞는 헤드라인 2개씩,",
          "    마지막에 가장 좋은 1개를 골라 이유를 설명해 주세요.'",
          "",
          "→ AI가 생각의 흐름을 보여 주고, 결과 품질이 크게 올라갑니다."]),
        ("원칙 6: 제약 조건 (Constraints)",
         ["하지 말 것을 명시합니다.",
          "  - '__는 사용하지 마세요'",
          "  - '글자 수 ___자 이내'",
          "  - '전문 용어 없이'",
          "",
          "예: 200자 이내, 외국어 표기 없이, 친근한 반말로 작성해 주세요."]),
        ("원칙 7: 반복 개선 (Iterate)",
         ["한 번에 완벽한 답을 기대하지 말고, 대화로 다듬어 갑니다.",
          "",
          "  '이 부분을 더 짧게'",
          "  '예시 1개 추가해서'",
          "  '20대 톤으로 다시'",
          "  '결론을 더 강하게'",
          "",
          "보통 3-5번 반복하면 만족스러운 결과가 나옵니다."]),
    ]
    for i, (title, lines) in enumerate(principles, 1):
        # 본문
        page_header(c, title, f"Part 2 / 원칙 {i}/7")
        body(c, M_INNER, H - 1.5*inch, lines)
        c.showPage()
        # 워크 페이지 (실습)
        page_header(c, f"실습: 원칙 {i} 적용해 보기", "Part 2")
        c.setFillColor(black)
        c.setFont(KR_B, 12)
        c.setFillColor(SECONDARY)
        c.drawString(M_INNER, H - 1.5*inch, "내가 자주 쓰는 프롬프트:")
        draw_lines_block(c, M_INNER, H - 1.8*inch, M, count=3)
        c.setFillColor(SECONDARY)
        c.setFont(KR_B, 12)
        c.drawString(M_INNER, H - 3.2*inch, f"원칙 {i}을 적용해 다시 쓴다면:")
        draw_lines_block(c, M_INNER, H - 3.5*inch, M, count=8)
        c.showPage()
        # 추가 노트 (원칙당 4p 채우기)
        for _ in range(2):
            page_header(c, f"노트 - 원칙 {i}", "Part 2")
            draw_lines_block(c, M_INNER, H - 1.5*inch, M)
            c.showPage()

    # 7원칙 x 4p = 28p, Part 1 = 14p (7챕터 x 2p), 목차 1p, 타이틀 1p, sub-titles
    # Part 3: 200개 프롬프트 (분야별 50개씩, 페이지당 3개 = 약 67p + 카테고리 표지)

    # === Part 3: 200개 프롬프트 ===
    sections = [
        ("3-1. 글쓰기 프롬프트 50개", "writing", [
            "당신은 베테랑 에디터입니다. 다음 글의 핵심을 3문장으로 요약해 주세요: [글]",
            "당신은 카피라이터입니다. [상품]에 대한 인스타 캡션 5개를 30자 이내로 작성해 주세요.",
            "당신은 신문 칼럼니스트입니다. [주제]에 대한 800자 사설을 써 주세요.",
            "다음 문장을 더 자연스러운 한국어로 다듬어 주세요: [문장]",
            "이 문장의 톤을 [친근함/공식적/유머러스]로 바꿔 주세요: [문장]",
            "당신은 작가입니다. [장르] 단편 소설의 도입부 300자를 써 주세요.",
            "[글]에서 클리셰 표현 5개를 찾아 대안을 제시해 주세요.",
            "다음 글을 [SNS포스팅/블로그/이메일]용으로 재작성해 주세요: [글]",
            "[제품]에 대한 후기 글을 객관적 관점에서 500자로 작성해 주세요.",
            "다음 글의 흐름을 분석하고 개선점 3가지를 제시해 주세요: [글]",
            "[키워드]를 자연스럽게 5번 포함하는 SEO 글을 800자로 작성해 주세요.",
            "당신은 자기계발 작가입니다. [주제]에 대한 영감 메시지 7개를 써 주세요.",
            "다음 메일을 더 정중한 비즈니스 톤으로 다시 써 주세요: [메일]",
            "[책 제목]의 챕터 1을 200자로 요약해 주세요.",
            "[주제]에 대한 토론 찬성/반대 논리를 각 5개씩 정리해 주세요.",
            "내가 쓴 [글]에서 어색한 표현을 찾아 빨간펜 첨삭을 해 주세요.",
            "[키워드] 3개를 사용해 4행시를 지어 주세요.",
            "[상품/서비스] 광고 헤드라인을 임팩트 있게 10개 만들어 주세요.",
            "다음 글의 독자 페르소나를 분석해 주세요: [글]",
            "[주제]에 대한 인터뷰 질문 10개를 깊이 순으로 정렬해 주세요.",
            "당신은 어린이책 작가입니다. 5세용 [주제] 동화를 8문장으로 써 주세요.",
            "이 글을 일본어/영어/중국어 자연스럽게 번역해 주세요: [글]",
            "[주제]에 대한 PPT 슬라이드 10장 구성을 제안해 주세요.",
            "[책]을 100자, 300자, 1000자로 각각 요약해 주세요.",
            "다음 글의 가독성 점수를 매기고 개선점을 알려 주세요: [글]",
            "[감정]을 묘사하는 비유 표현 7가지를 만들어 주세요.",
            "[직업]의 자기소개서 첫 문장 5가지 패턴을 보여 주세요.",
            "[주제]에 대한 트위터/X 실타래 5트윗을 작성해 주세요.",
            "당신은 시인입니다. [감정]을 주제로 자유시 한 편 써 주세요.",
            "이 글에서 결론을 더 강력하게 다시 써 주세요: [글]",
            "[키워드]에 대한 해시태그 30개를 인기 순으로 추천해 주세요.",
            "[독자]가 끝까지 읽고 싶어할 도입부 3개 버전을 작성해 주세요.",
            "다음 글에서 사실, 의견, 추측을 분리해 주세요: [글]",
            "[주제]에 대한 책 목차 12장 구성을 짜 주세요.",
            "이 글의 패러그래프 순서를 논리 순으로 재배열해 주세요: [글]",
            "[행사]의 초청장 문구를 격식 있게 200자로 작성해 주세요.",
            "[제품] 사용 후기 5가지 톤으로 각 100자씩 작성해 주세요. (감동/유머/객관/감사/추천)",
            "[주제]를 5세, 15세, 30세, 60세에게 각각 1문장으로 설명해 주세요.",
            "이 글에서 군더더기 표현을 모두 빼서 절반으로 줄여 주세요: [글]",
            "당신은 라디오 DJ입니다. [주제]에 대한 1분 멘트를 써 주세요.",
            "[책/영화] 리뷰를 별점 + 한 줄 + 본론 300자로 작성해 주세요.",
            "[메뉴]를 매혹적인 카페 메뉴 설명문으로 30자 이내로 써 주세요.",
            "[주제]에 대한 Q&A 10세트를 자주 묻는 순으로 정리해 주세요.",
            "이 글의 어조를 분석하고 비즈니스 메일에 어울리게 고쳐 주세요: [글]",
            "[감정]을 음식, 색깔, 계절, 날씨로 비유한 글 200자를 써 주세요.",
            "[주제]에 대한 TED 스타일 3분 스피치를 작성해 주세요.",
            "이 글의 핵심 주장을 한 문장으로 압축해 주세요: [글]",
            "[브랜드]의 슬로건 후보 10개를 음감 좋은 순으로 정렬해 주세요.",
            "[직업]의 하루 일과를 일기 형식으로 800자에 써 주세요.",
            "다음 후기의 별점을 추정하고 이유 3가지를 들어 주세요: [후기]",
        ]),
        ("3-2. 마케팅 프롬프트 50개", "marketing", [
            "당신은 SNS 매니저입니다. [상품]의 인스타 첫 3초 후크 5개를 만들어 주세요.",
            "[상품]의 타깃 페르소나 3개를 인구통계+심리통계로 작성해 주세요.",
            "[상품]에 어울리는 인플루언서 카테고리 5가지를 추천해 주세요.",
            "다음 광고 카피의 약점 3가지와 개선안을 제시해 주세요: [카피]",
            "[브랜드]의 USP(고유 판매 제안) 3가지를 도출해 주세요.",
            "당신은 그로스 해커입니다. [서비스]의 바이럴 루프를 설계해 주세요.",
            "[제품]의 가격 책정 전략 3가지를 비교해 주세요. (저가/중가/프리미엄)",
            "[상품] 출시 보도자료를 5W1H로 작성해 주세요.",
            "[브랜드]의 브랜드 보이스를 5개 형용사로 정의해 주세요.",
            "유튜브 [주제] 채널의 첫 10개 영상 기획안을 만들어 주세요.",
            "[상품]을 검색할 만한 롱테일 키워드 30개를 뽑아 주세요.",
            "[고객]의 구매 여정 (인지-고려-결정-재구매)을 매핑해 주세요.",
            "[상품]의 A/B 테스트 가설 5개를 우선순위로 정렬해 주세요.",
            "다음 랜딩페이지의 전환율 개선점 5가지를 짚어 주세요: [URL/내용]",
            "[브랜드]의 콘텐츠 캘린더 (1개월) 30개를 만들어 주세요.",
            "당신은 카피라이팅 전문가입니다. PAS, AIDA, 4P 공식으로 [상품] 카피 3개씩 작성해 주세요.",
            "[상품]의 경쟁사 5개를 SWOT으로 비교해 주세요.",
            "[제품] 패키지 디자인 콘셉트 3가지를 글로 묘사해 주세요.",
            "[행사]의 인스타 라이브 스크립트 30분짜리를 작성해 주세요.",
            "[상품]의 추천 후기를 자연스럽게 5가지 톤으로 작성해 주세요.",
            "[브랜드]가 손해 보는 무료 콘텐츠 아이디어 10개를 제시해 주세요.",
            "[제품]의 첫 구매 인센티브 5가지를 효과 순으로 정렬해 주세요.",
            "[키워드]에 대한 메타 디스크립션 (160자) 5가지 버전을 작성해 주세요.",
            "[행사]의 카운트다운 인스타 7일 콘텐츠를 기획해 주세요.",
            "[상품]을 카카오톡, 인스타, 유튜브, 네이버 블로그 4채널로 각각 다르게 광고하는 카피를 작성해 주세요.",
            "[상품] 평균 단가가 [가격]일 때, 신규 고객 1명 획득에 쓸 수 있는 최대 비용을 계산하고 마케팅 채널 추천을 해 주세요.",
            "[브랜드]의 위기 대응 매뉴얼 (불만/오해/경쟁비교)을 단계별로 작성해 주세요.",
            "[직업/타깃]에게 보내는 콜드메일 5가지 시작 문장 패턴을 작성해 주세요.",
            "[행사]의 카카오 채널 친구 모으기 캠페인 5단계를 설계해 주세요.",
            "[상품]의 셀링 포인트를 헤드라인 / 서브 / 본문 / CTA 형식으로 4단 구조로 작성해 주세요.",
            "[고객]이 우리 상품을 안 사는 이유 10가지를 솔직하게 분석해 주세요.",
            "[상품]을 결제까지 끌고 가는 페이스북 광고 카피 (이미지광고/영상광고/캐러셀) 3종을 작성해 주세요.",
            "[브랜드]의 회원가입 환영 메일 시퀀스 5개 (Day 0~7)를 설계해 주세요.",
            "[행사]의 노쇼 방지 리마인더 메시지 3단계를 작성해 주세요.",
            "[상품]을 선물로 추천하는 1분 영상 스크립트를 작성해 주세요.",
            "[키워드]의 구글/네이버 자동완성 추천 검색어 20개를 추측해 주세요.",
            "[브랜드]의 패키지 안에 넣을 손편지 3종 (감사/사과/이벤트)을 작성해 주세요.",
            "[상품]의 시즌별 (봄/여름/가을/겨울) 마케팅 메시지를 각각 작성해 주세요.",
            "[고객]의 이탈 원인을 추측하고 재유치 캠페인 3종을 설계해 주세요.",
            "[브랜드]의 포지셔닝 맵 2x2 (가격 vs 품질) 위에 경쟁사 5개를 배치해 주세요.",
            "[행사]의 사후 후기 부탁 메시지 (자연스러운 톤)를 작성해 주세요.",
            "[상품]에 어울리는 크리에이터 협업 제안서를 200자로 작성해 주세요.",
            "[행사]의 SNS 해시태그 캠페인 (#ㅇㅇㅇ챌린지) 기획안을 만들어 주세요.",
            "[상품]의 크라우드펀딩 스토리텔링 구조 (영웅의 여정 12단계)를 작성해 주세요.",
            "[브랜드]의 NPS(추천 의사) 설문 5문항을 설계해 주세요.",
            "[상품]을 5초 영상, 15초 광고, 60초 인포머셜로 각각 작성해 주세요.",
            "[행사]의 얼리버드 이메일 5개 시퀀스 (D-30, D-14, D-7, D-1, 당일)를 작성해 주세요.",
            "[상품]의 프리미엄 버전 vs 무료 버전 차별화 5가지를 작성해 주세요.",
            "[키워드] 검색 광고 입찰 전략 3단계를 추천해 주세요.",
            "[브랜드]의 1년 후 모습을 비전 보드 형식 글로 200자에 그려 주세요.",
        ]),
        ("3-3. 업무자동화 프롬프트 50개", "automation", [
            "다음 회의록을 [요약/액션아이템/결정사항]으로 정리해 주세요: [회의록]",
            "이 엑셀 표를 분석하고 인사이트 3가지를 도출해 주세요: [데이터]",
            "다음 메일에 정중한 답장 3가지 톤으로 작성해 주세요: [메일]",
            "이 일정에서 우선순위와 시간 블록을 추천해 주세요: [일정]",
            "[작업]을 SOP (표준 업무 절차) 10단계로 문서화해 주세요.",
            "이 보고서를 1페이지 임원용 요약으로 만들어 주세요: [보고서]",
            "다음 데이터를 표로 정리하고 트렌드 3가지를 짚어 주세요: [데이터]",
            "[프로젝트]의 RACI 매트릭스 (책임/실행/협력/통보)를 작성해 주세요.",
            "이 회의를 끝낼 때 마무리 멘트 3개 버전을 추천해 주세요: [회의 주제]",
            "[작업]의 작업분해구조 (WBS) 3레벨까지 작성해 주세요.",
            "이 부서의 KPI 5개를 SMART 기준으로 정의해 주세요: [부서]",
            "다음 슬라이드의 메시지를 강화해 주세요: [슬라이드]",
            "[프로젝트]의 위험 요소 10가지와 대응책을 매트릭스로 작성해 주세요.",
            "이 채용공고를 더 매력적이게 다시 써 주세요: [공고]",
            "[직무]의 면접 질문 10개를 깊이별로 (행동/기술/문화) 분류해 주세요.",
            "다음 코드를 더 읽기 쉽게 리팩토링해 주세요: [코드]",
            "이 SQL 쿼리를 분석하고 성능 개선점을 알려 주세요: [SQL]",
            "[데이터]에서 이상치를 찾고 원인을 추측해 주세요.",
            "이 정책 문서를 사원에게 친근하게 풀어 써 주세요: [정책]",
            "[고객 문의]에 대한 FAQ 답변 10개를 작성해 주세요.",
            "이 회의 안건을 90분 어젠다로 시간 분배해 주세요: [안건]",
            "[프로젝트] 일정의 critical path를 식별하고 위험 시점을 알려 주세요.",
            "이 인터뷰 답변을 키워드 5개로 요약해 주세요: [답변]",
            "[부서]의 1년 OKR (목표/핵심결과)를 5개 작성해 주세요.",
            "다음 결재 문서를 더 간결하게 다시 써 주세요: [문서]",
            "[직무]의 1년차 / 3년차 / 5년차 성장 로드맵을 작성해 주세요.",
            "이 PPT를 텍스트만 보고 30초 발표 스크립트로 변환해 주세요: [PPT 텍스트]",
            "[고객]의 클레임 메일에 사과 + 해결 + 보상 3단 답장을 작성해 주세요.",
            "이 데이터를 시각화한다면 어떤 차트가 적합한지 추천 + 이유: [데이터]",
            "[부서장]에게 보고하는 주간 보고서 템플릿을 만들어 주세요.",
            "다음 컨설팅 제안서를 더 설득력 있게 다시 써 주세요: [제안서]",
            "[작업]의 자동화 가능 여부와 추천 도구를 분석해 주세요.",
            "이 회의를 줄일 수 있는 비대면 대안을 3가지 제시해 주세요: [회의]",
            "[프로젝트]의 이해관계자 맵을 영향력/관심도 매트릭스로 작성해 주세요.",
            "다음 답변을 더 데이터 기반으로 고쳐 주세요: [답변]",
            "[엑셀 함수]가 무엇을 하는지 한 줄로 설명하고 실수 가능 지점을 알려 주세요.",
            "이 메일 흐름을 자동화한다면 어떤 트리거가 적합한지 추천해 주세요: [메일]",
            "[직무] 신입 온보딩 1주일 일정을 시간 단위로 짜 주세요.",
            "이 회사 정책의 빈틈 5가지를 컴플라이언스 관점에서 짚어 주세요: [정책]",
            "[업무]의 단축키 / 자동화 매크로 추천 5가지를 알려 주세요.",
            "이 프레젠테이션의 청중 관심도가 떨어질 수 있는 지점을 짚어 주세요: [PPT]",
            "[부서]의 회의 빈도 진단 (너무 많음/적절/너무 적음) 기준을 만들어 주세요.",
            "이 보고를 1분, 5분, 30분 발표 버전으로 각각 작성해 주세요: [내용]",
            "[프로젝트]의 ROI를 계산하는 공식과 입력값을 정리해 주세요.",
            "다음 매뉴얼을 신입사원도 이해하게 다시 써 주세요: [매뉴얼]",
            "[직무]의 매일 30분 자기개발 루틴을 추천해 주세요.",
            "이 회의록을 회의 5분 후 슬랙에 보낼 한 줄 요약으로 만들어 주세요: [회의록]",
            "[부서]의 비효율 업무 TOP 5를 진단 + 개선안을 작성해 주세요.",
            "이 결재 라인을 단축할 수 있는 대안 흐름을 그려 주세요: [라인]",
            "[직무] 1년차가 흔히 하는 실수 10가지를 정리해 주세요.",
        ]),
        ("3-4. 창작/아이디어 프롬프트 50개", "creative", [
            "당신은 브레인스토밍 코치입니다. [주제]에 대한 100가지 아이디어를 빠르게 던져 주세요.",
            "[일상의 불편]을 해결하는 신제품 아이디어 10개를 추천해 주세요.",
            "[기존 산업]을 AI로 재편하면 어떤 신사업이 가능할지 5개 제안해 주세요.",
            "[키워드]를 결합한 SCAMPER (대체/결합/응용/변형/축소/제거/재배치) 7가지 아이디어를 만들어 주세요.",
            "[직업]을 10년 후에도 살아남게 만들 진화 방향 3가지를 제시해 주세요.",
            "당신은 디자인 씽킹 퍼실리테이터입니다. [문제]에 대한 5단계 (공감-정의-아이디어-프로토타입-테스트)를 진행해 주세요.",
            "[취미]를 부업으로 발전시킬 단계적 로드맵을 작성해 주세요.",
            "[지역]을 주제로 한 새로운 카페 콘셉트 5개를 제안해 주세요.",
            "당신은 SF 작가입니다. [주제]에 대한 30년 후의 모습을 묘사해 주세요.",
            "[감정]에서 영감을 받은 향수 노트를 (탑/미들/베이스) 3단으로 만들어 주세요.",
            "[일상 사물]에 인격을 부여한 짧은 이야기 3편을 써 주세요.",
            "[지역+계절]을 주제로 한 음식 메뉴 7가지를 창작해 주세요.",
            "당신은 보드게임 디자이너입니다. [주제]를 메커니즘으로 한 게임 룰을 작성해 주세요.",
            "[키워드]에서 영감 받은 인테리어 콘셉트 3가지 + 색상 팔레트를 제안해 주세요.",
            "[캐릭터]의 백스토리를 5단계 인생 사건으로 작성해 주세요.",
            "[음식 재료] 3가지로 만들 수 있는 새 요리 레시피를 5개 제안해 주세요.",
            "당신은 광고 크리에이티브 디렉터입니다. [상품]을 주제로 한 30초 광고 콘티 3가지를 묘사해 주세요.",
            "[키워드]를 영화 한 편으로 만든다면 줄거리, 주인공, 클라이맥스를 작성해 주세요.",
            "[일상 문제]를 해결하는 모바일 앱 아이디어 10개를 추천해 주세요.",
            "[감정]을 표현하는 색깔 / 음악 / 동작을 3단으로 시각화해 주세요.",
            "당신은 공간 디자이너입니다. 5평 작업실을 [컨셉]으로 꾸미는 가구 배치도를 글로 그려 주세요.",
            "[취미]를 결합한 클래스 커리큘럼 8주를 설계해 주세요.",
            "[키워드]를 모티프로 한 캐릭터 5명을 외형 + 성격으로 디자인해 주세요.",
            "[지역 특산물]을 활용한 시그니처 디저트 3종을 창작해 주세요.",
            "당신은 시인입니다. [감정 + 계절]을 주제로 단문 시 5편을 써 주세요.",
            "[직업]의 미래 직업 진화 형태 5단계를 그려 주세요.",
            "[일상]을 1분 영상 시리즈 (Vlog 30편) 기획안으로 만들어 주세요.",
            "[키워드]를 장난감으로 만든다면 3-5세, 6-9세, 10-12세용 차별화 디자인을 제안해 주세요.",
            "[일상 도구]를 친환경으로 재디자인한 모델을 묘사해 주세요.",
            "당신은 콘셉트 아티스트입니다. [장면]을 미드저니 프롬프트로 변환해 주세요.",
            "[취미] 커뮤니티의 1년 운영 기획안 (월별 이벤트)을 작성해 주세요.",
            "[일상의 작은 불편]을 모은 후, 가장 사업화 가능성 높은 5가지를 표로 정리해 주세요.",
            "[감정]을 표현하는 무용 동작을 5단계로 묘사해 주세요.",
            "[지역]에서만 가능한 1박2일 여행 코스 5종을 테마별로 작성해 주세요.",
            "당신은 무대 연출가입니다. [주제]의 1시간 공연 흐름을 4막으로 짜 주세요.",
            "[일상의 작은 발견]을 영감 노트로 정리하는 5가지 양식을 제안해 주세요.",
            "[직업]에서 영감 받은 새 직업명 10개를 만들어 주세요.",
            "[키워드 + 색깔]로 한 옷 컬렉션 5룩을 디자인해 주세요.",
            "[감정]을 일러스트 한 장으로 표현한다면 어떤 구도/색/요소가 좋을지 묘사해 주세요.",
            "[관심사] 분야의 책 5권을 읽기 순서대로 추천해 주세요.",
            "당신은 푸드 스타일리스트입니다. [요리]의 플레이팅 5가지 버전을 글로 묘사해 주세요.",
            "[일상]을 만화 4컷으로 그린다면 컷별 대사를 작성해 주세요.",
            "[직업]의 여행지/작업실/카페 3개씩 추천해 주세요. (도시 + 분위기 설명)",
            "[감정]을 단편 영화 5분짜리로 만든다면 시나리오를 써 주세요.",
            "[일상 사물]에 새 용도 5가지를 부여해 주세요.",
            "[키워드]를 향한 마인드맵 3단계 (중심-가지-잎)을 작성해 주세요.",
            "[직업]의 1주일 자기관리 루틴 (운동/독서/창작)을 짜 주세요.",
            "[지역]에 새 카페를 연다면, 입지 / 메뉴 / 가격 / 인테리어 4축으로 기획해 주세요.",
            "[감정]을 책 표지 디자인으로 표현한다면 색/폰트/이미지 콘셉트를 묘사해 주세요.",
            "[취미]를 친구에게 강의한다면 90분 커리큘럼을 짜 주세요.",
        ]),
    ]

    for sec_title, sec_id, prompts in sections:
        # 섹션 표지
        c.setFillColor(SECONDARY)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(PRIMARY)
        c.setFont(KR_B, 38)
        c.drawCentredString(W/2, H*0.55, sec_title)
        c.setFont(KR, 14)
        c.setFillColor(white)
        c.drawCentredString(W/2, H*0.45, "복사해서 바로 쓸 수 있는 50개")
        c.showPage()

        # 프롬프트 페이지: 페이지당 3개 + 실습 칸
        for i in range(0, len(prompts), 3):
            chunk = prompts[i:i+3]
            page_header(c, sec_title, f"Part 3 / {i+1}-{i+len(chunk)}")
            cy = H - 1.4*inch
            for j, p in enumerate(chunk, 1):
                c.setFillColor(SECONDARY)
                c.setFont(KR_B, 11)
                c.drawString(M_INNER, cy, f"[{i+j:03d}]")
                cy -= 0.2*inch
                c.setFillColor(black)
                c.setFont(KR, 10)
                # 텍스트 wrap (한국어 - 글자 단위 wrap)
                wrap_korean(c, p, M_INNER + 0.1*inch, cy, W - M - M_INNER - 0.1*inch)
                # 텍스트 높이 추정 (대략 글자 수 / 50자 per 줄 * 0.2inch)
                est_lines = max(2, len(p) // 45 + 1)
                cy -= est_lines * 0.2*inch + 0.05*inch
                # 실습 칸 1줄
                c.setStrokeColor(HexColor("#CCCCCC"))
                c.setLineWidth(0.4)
                c.setFillColor(HexColor("#888"))
                c.setFont(KR, 9)
                c.drawString(M_INNER + 0.1*inch, cy, "내가 바꾼 부분 / 결과 메모:")
                cy -= 0.2*inch
                c.line(M_INNER + 0.1*inch, cy, W - M, cy)
                cy -= 0.3*inch
                c.line(M_INNER + 0.1*inch, cy, W - M, cy)
                cy -= 0.4*inch
            c.showPage()

    # === Part 4: 워크시트 (10p) ===
    work_pages = [
        ("내 분야의 핵심 작업 정리",
         ["내가 매주 반복하는 작업 10가지를 적어 보세요.",
          "그 중 AI로 자동화 가능한 것을 ★표 해 보세요."]),
        ("내 페르소나 카드",
         ["나의 직업, 주 업무, 자주 쓰는 도구를 정리하세요.",
          "이 정보를 매 프롬프트 시작에 붙이면 답변 품질이 올라갑니다."]),
        ("자주 쓰는 프롬프트 라이브러리 - 글쓰기", []),
        ("자주 쓰는 프롬프트 라이브러리 - 마케팅", []),
        ("자주 쓰는 프롬프트 라이브러리 - 업무", []),
        ("자주 쓰는 프롬프트 라이브러리 - 창작", []),
        ("내가 만든 베스트 프롬프트 10",
         ["나만의 베스트 10을 모으세요. 1년 뒤 라이브러리가 됩니다."]),
        ("AI 사용 일기 - 7일 챌린지", []),
        ("결과 비교 워크시트 (ChatGPT vs Claude)", []),
        ("실패한 프롬프트 / 다시 쓰기", []),
    ]
    for title, intro in work_pages:
        page_header(c, title, "Part 4 / 워크시트")
        c.setFillColor(black)
        cy = H - 1.4*inch
        if intro:
            for line in intro:
                c.setFont(KR, 11)
                c.drawString(M_INNER, cy, line)
                cy -= 0.28*inch
            cy -= 0.2*inch
        draw_lines_block(c, M_INNER, cy, M, count=18)
        c.showPage()

    # === 부록 (6p) ===
    appendix_pages = [
        ("추천 도구 30선",
         ["글쓰기: ChatGPT / Claude / Notion AI / Grammarly",
          "이미지: Midjourney / DALL-E / Stable Diffusion / Leonardo",
          "동영상: Runway / Pika / HeyGen / Synthesia",
          "음성: ElevenLabs / Murf / Suno / Udio",
          "코딩: Cursor / GitHub Copilot / v0.dev / Bolt",
          "업무: Zapier / Make / Notion / Slack AI",
          "디자인: Figma AI / Canva AI / Adobe Firefly",
          "리서치: Perplexity / Phind / SciSpace",
          "한국어 강점: Wrtn / Asktoday / Genie / 뤼튼"]),
        ("AI 윤리 5가지",
         ["1. 사실 확인 - AI 답변은 검증 필요",
          "2. 출처 표기 - AI 사용 사실 공개",
          "3. 개인정보 - 입력하지 마세요",
          "4. 저작권 - 상업 이용 시 약관 확인",
          "5. 책임 - 최종 결정은 사람이"]),
        ("내가 다음에 할 것 (Action Plan)",
         ["이 책에서 가장 도움된 프롬프트 3개:",
          "내가 만들 라이브러리 100개의 카테고리:",
          "다음 1주일 안에 시도할 자동화 1가지:",
          "1년 후 나의 AI 활용 모습:"]),
    ]
    for title, lines in appendix_pages:
        page_header(c, title, "부록")
        c.setFillColor(black)
        cy = H - 1.4*inch
        for line in lines:
            c.setFont(KR, 11)
            c.drawString(M_INNER, cy, line)
            cy -= 0.28*inch
        cy -= 0.2*inch
        draw_lines_block(c, M_INNER, cy, M, count=10)
        c.showPage()

    # 저자 후기 (1p)
    page_header(c, "마치며 - 저자 후기", "")
    c.setFillColor(black)
    cy = H - 1.4*inch
    epilogue = [
        "이 책을 끝까지 읽어 주셔서 감사합니다.",
        "",
        "AI는 마법이 아닙니다. 잘 묻는 사람의 도구입니다.",
        "이 책의 200개 프롬프트는 시작점일 뿐입니다.",
        "",
        "당신만의 1000개 라이브러리가 만들어지는 날,",
        "이 책의 임무는 끝납니다.",
        "",
        "꾸준히 시도하고, 실패하고, 다시 다듬는 매일이",
        "결국 가장 큰 차이를 만듭니다.",
        "",
        "                                    Deokgu Studio",
    ]
    for line in epilogue:
        c.setFont(KR, 12)
        c.drawString(M_INNER, cy, line)
        cy -= 0.32*inch
    c.showPage()

    c.save()
    print(f"  [ai-prompt-workbook] ai_prompt_workbook.pdf -> {os.path.getsize(out)/1024/1024:.1f} MB")


def wrap_korean(c, text, x, y, max_width):
    """한국어 단순 글자단위 wrap. 1줄당 약 45자."""
    char_per_line = 50
    cy = y
    while text:
        line = text[:char_per_line]
        text = text[char_per_line:]
        c.drawString(x, cy, line)
        cy -= 0.2*inch
    return cy


def draw_lines_block(c, x_left, y_top, x_right_margin, count=14):
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.setLineWidth(0.4)
    cy = y_top
    for _ in range(count):
        c.line(x_left, cy, W - x_right_margin, cy)
        cy -= 0.32*inch
    return cy


if __name__ == "__main__":
    print("=" * 50)
    print("Generating ai-prompt-workbook book...")
    print(f"Korean font: {'OK' if HAS_KR else 'FAIL'}")
    print("=" * 50)
    make_cover()
    make_interior()
    print("Done.")
