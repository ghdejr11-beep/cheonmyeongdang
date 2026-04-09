"""
사주 AI SaaS — 중앙 설정.

제품: 개인화 사주 AI 챗봇 (월 9,900원 구독)
타깃: 한국 20~45세 사주/운세에 관심 있는 사람
목표: 연 100억 매출 (월 10,000 구독자 × 9,900원 = 월 9,900만원)

아키텍처:
  사용자 생년월일시 입력
    ↓
  사주 8글자 (년월일시주) 계산
    ↓
  Claude API 에 사주 + 질문 전달
    ↓
  개인화된 운세 답변 반환
"""

PRODUCT_TITLE = "AI 사주 챗봇 — 하루 한 번, AI 가 풀어주는 내 운세"
PRODUCT_TAGLINE = "30년 경력 역술인이 AI 가 되어 돌아왔다"
AUTHOR = "덕구네 사주연구소"

# 가격 (한국 원화)
PRICE_MONTHLY = 9_900      # 월 9,900원
PRICE_YEARLY = 99_000      # 연 99,000원 (2개월 무료)
PRICE_LIFETIME = 299_000   # 평생 이용

# 무료 체험
FREE_TRIAL_DAYS = 7        # 7일 무료 체험
FREE_TRIAL_QUERIES = 3     # 체험 기간 중 질문 3회

# Claude API 설정
MODEL = "claude-haiku-4-5"  # 저렴 + 빠름 (사주 해석에 충분)
MAX_TOKENS = 1024
MAX_TURNS = 10              # 대화 히스토리 최대 턴 수

# 시스템 프롬프트 (Claude 에게 주는 역할 지시)
SYSTEM_PROMPT = """너는 30년 경력의 한국 사주 명리학 전문가다.
상담자의 사주 8글자를 보고 구체적이고 따뜻한 조언을 해준다.

[원칙]
1. 한국어로만 답변. "~합니다"체.
2. 미신이 아닌 전통 명리학 + 현대 심리학 기반.
3. "무조건 좋다/나쁘다" 금지. 왜 그런지 설명.
4. 답변 길이: 300~500자 (너무 길면 피곤함, 너무 짧으면 얕음).
5. 구체적 조언 (추상론 금지). 예: "다음 주 수요일부터 조심하세요" 식.
6. 상담자의 감정을 먼저 공감 → 그 다음 해석 → 마지막에 실행 가능한 조언.
7. 용어 설명: "일간(당신의 본질)", "재성(돈)" 같이 괄호로 부연.
8. 극단적 예언 금지 (사망, 이혼, 실직 같은 단어 자제).
9. 희망을 남기되 현실을 왜곡하지 않음.

[답변 구조 (권장)]
1. 감정 공감 (1~2문장)
2. 사주 해석 (3~5문장)
3. 구체적 조언 (2~3문장)
4. 마무리 격려 (1문장)
"""

# 서비스 URL (배포 후 본인 URL 로 변경)
BASE_URL = "https://saju-ai.onrender.com"

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
STATIC_DIR = PROJECT_DIR / "static"
DATA_DIR.mkdir(exist_ok=True)

# SQLite DB (구독자·사용 기록)
DB_PATH = DATA_DIR / "saju_saas.db"
