"""
전자책 시스템 중앙 설정 파일.
이 파일만 수정하면 책 주제·가격·결제 링크를 모두 바꿀 수 있습니다.
"""

# ============================================================
# 책 정보
# ============================================================
BOOK_TITLE = "AI(Claude·ChatGPT)로 월 500만원 디지털 상품 자동화 시스템"
BOOK_SUBTITLE = "100일 안에 시작하는 1인 부업 실전 가이드"
AUTHOR = "홍덕훈"

TARGET_AUDIENCE = (
    "25~45세 한국 직장인·자영업자. "
    "AI는 들어봤지만 실제로 어떻게 돈으로 만드는지 모르는 사람."
)
PROMISE = (
    "독자가 100일 안에 AI로 디지털 상품(전자책·템플릿·자동화)을 만들고 "
    "월 500만원 부업 수익까지 도달하는 실전 시스템."
)

# 50개 챕터, 각 1500자 → 약 75,000자 / 200~250페이지 PDF
NUM_CHAPTERS = 50
WORDS_PER_CHAPTER = 1500

# ============================================================
# 모델 (Claude API)
# ============================================================
# 기본은 최고 품질 (Opus 4.6). 비용을 줄이려면 sonnet/haiku로 바꿀 수 있음.
MODEL_OUTLINE = "claude-opus-4-6"
MODEL_CHAPTER = "claude-opus-4-6"
MODEL_SHORTS = "claude-opus-4-6"

# ============================================================
# 가격 (KRW)
# ============================================================
PRICE_LITE = 19_900       # 미끼 상품 (PDF 50p)
PRICE_STANDARD = 99_000   # 메인 상품 (PDF 200p + 템플릿)
PRICE_PREMIUM = 299_000   # 프리미엄 (위 + 1:1 카톡 30일 + 평생 업데이트)

# ============================================================
# 판매 링크 (등록 후 채워넣기)
# ============================================================
# 옵션 A: Gumroad (해외 결제, 자동 배송, 가장 쉬움)
GUMROAD_LITE = "https://yourname.gumroad.com/l/lite"
GUMROAD_STANDARD = "https://yourname.gumroad.com/l/standard"
GUMROAD_PREMIUM = "https://yourname.gumroad.com/l/premium"

# 옵션 B: 크몽 (한국 결제, 사업자등록증 불필요, 수수료 20%)
KMONG_URL = "https://kmong.com/gig/your-gig-id"

# 옵션 C: 부크크 (한국 전자책 전용, 인세 70%)
BOOKK_URL = "https://bookk.co.kr/book/view/your-book-id"

# ============================================================
# 출력 폴더
# ============================================================
OUTPUT_DIR = "output"
CHAPTERS_SUBDIR = "chapters"
SHORTS_SUBDIR = "shorts"
FONTS_DIR = "fonts"
