"""
Claude·ChatGPT 실전 프롬프트 1,000개 팩 — 중앙 설정 파일.
"""

# ============================================================
# 상품 정보
# ============================================================
PRODUCT_TITLE = "Claude·ChatGPT 실전 프롬프트 1,000개 - 업종별 완전 정복"
PRODUCT_SUBTITLE = "복붙하면 바로 쓰는 한국어 프롬프트 모음집"
AUTHOR = "홍덕훈 (덕구네 출판)"

# 가격 (한국 원화)
PRICE_KRW = 29_900

# 번들 할인 (STANDARD 와 함께 사면 할인)
BUNDLE_WITH_STANDARD_PRICE = 99_000  # STANDARD 단독
BUNDLE_PRICE = 119_000  # STANDARD + 프롬프트 팩 = 99,000 + 29,900 - 할인 9,900 = 119,000

# ============================================================
# 10개 카테고리 × 100개 = 1,000개 프롬프트
# ============================================================
CATEGORIES = [
    {
        "id": "email",
        "num": 1,
        "name": "📧 이메일 마케팅 & 세일즈",
        "description": "세일즈 메일, 콜드 아웃리치, 팔로우업, 뉴스레터",
        "count": 100,
    },
    {
        "id": "copywriting",
        "num": 2,
        "name": "✍️ 카피라이팅 & 광고",
        "description": "광고 헤드라인, 상세페이지, 랜딩 카피, 제품 설명",
        "count": 100,
    },
    {
        "id": "sns",
        "num": 3,
        "name": "📱 SNS 콘텐츠 & 바이럴",
        "description": "릴스/틱톡 후크, 인스타 캡션, 트윗, 쓰레드",
        "count": 100,
    },
    {
        "id": "blog",
        "num": 4,
        "name": "📝 블로그 & 콘텐츠 마케팅",
        "description": "SEO 글, 블로그 포스트, 뉴스레터, 매거진",
        "count": 100,
    },
    {
        "id": "youtube",
        "num": 5,
        "name": "🎬 유튜브 & 영상",
        "description": "스크립트, 썸네일 카피, 제목, 설명, 댓글 응대",
        "count": 100,
    },
    {
        "id": "business",
        "num": 6,
        "name": "💼 비즈니스 & 사업 전략",
        "description": "사업계획서, 제안서, 보고서, 회의록, 분석",
        "count": 100,
    },
    {
        "id": "coding",
        "num": 7,
        "name": "💻 코딩 & 개발",
        "description": "코드 리뷰, 디버깅, 리팩토링, 문서화, 알고리즘",
        "count": 100,
    },
    {
        "id": "design",
        "num": 8,
        "name": "🎨 디자인 & 크리에이티브",
        "description": "브랜딩, 로고 컨셉, UI 설명, Midjourney 프롬프트",
        "count": 100,
    },
    {
        "id": "data",
        "num": 9,
        "name": "📊 데이터 & 엑셀 & 분석",
        "description": "엑셀 수식, 데이터 분석, 차트, 리포트, SQL",
        "count": 100,
    },
    {
        "id": "language",
        "num": 10,
        "name": "🌏 번역 & 외국어 & 글쓰기",
        "description": "한영 번역, 맞춤법, 문체 교정, 요약, 리라이트",
        "count": 100,
    },
]

# ============================================================
# Claude API 설정
# ============================================================
MODEL = "claude-haiku-4-5"  # 비용 절감. sonnet 으로 바꾸면 품질 상승
MAX_TOKENS_PER_CATEGORY = 16000  # 100개 × 한국어 ~500자 여유분 포함

# ============================================================
# 경로
# ============================================================
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PROMPTS_JSON = OUTPUT_DIR / "prompts.json"
PROMPTS_PDF = OUTPUT_DIR / "prompt_pack_1000.pdf"
