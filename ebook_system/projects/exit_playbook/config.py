"""
퇴사 후 1인 사업 플레이북 — 중앙 설정.

타깃: 30~45세 직장인. 퇴사 고민 중이거나 이미 퇴사한 1인 사업 준비자.
가격: 99,000원 (메인 상품) 또는 49,900원 (얼리버드)
포지셔닝: 감정 트리거 + 실전 가이드
"""

BOOK_TITLE = "퇴사 후 1인 사업 플레이북 — AI 시대의 1년 생존 매뉴얼"
BOOK_SUBTITLE = "직장 그만둔 첫 1년, 어떻게 살아남을 것인가"
AUTHOR = "홍덕훈 (덕구네 출판)"

TARGET_AUDIENCE = (
    "30~45세 직장인. 매일 출근이 지옥인데 그만두긴 무섭고, "
    "1인 사업은 동경하지만 무엇부터 해야 할지 모르는 사람."
)
PROMISE = (
    "퇴사 D-Day 부터 1년 후 월 500만원 안정 수익까지 "
    "12개월 단계별 매뉴얼. 감정·실전·세무·법무 전부 포함."
)

NUM_CHAPTERS = 50
WORDS_PER_CHAPTER = 1500

PRICE_KRW = 99_000
EARLY_BIRD_PRICE_KRW = 49_900

MODEL_OUTLINE = "claude-opus-4-6"
MODEL_CHAPTER = "claude-opus-4-6"

OUTPUT_DIR = "output"
CHAPTERS_SUBDIR = "chapters"

# 4부 구성 (직장인 → 1인 사업가 12개월 여정)
PART_STRUCTURE = """
제1부 (1~10장): 퇴사 결정 — D-30 부터 D-Day 까지
  - 진짜로 그만둬도 되는가? 자가진단
  - 퇴사 전 마지막 30일 체크리스트
  - 통장에 얼마 있어야 안전한가
  - 회사에 어떻게 말할 것인가
  - 인수인계의 기술

제2부 (11~25장): 첫 90일 — 정체성 재구축 + 첫 매출
  - 퇴사 후 한 달의 함정 (잉여 인간 증후군)
  - 첫 30일 루틴 만들기
  - "내가 팔 수 있는 것" 발견하기 (Skills Audit)
  - 첫 1,000원 매출 만드는 5가지 길
  - 1인 사업 첫 번째 상품 출시 가이드

제3부 (26~40장): D+90 ~ D+180 — 매출 시스템 구축
  - 첫 고객 10명 만드는 법
  - 가격 책정의 심리학 (1만원 → 10만원)
  - 자동화 시스템 첫 단계
  - SNS·블로그·이메일 마케팅 입문
  - 첫 100만원 → 첫 500만원

제4부 (41~50장): D+180 ~ D+365 — 안정 + 확장
  - 월 500만원 도달 후의 함정
  - 외주화 + 시스템화 (혼자 일하지 않기)
  - 세무·건강보험·국민연금
  - 법인 전환 타이밍
  - 1년 후 회고 + 다음 1년 계획
"""

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR_PATH = PROJECT_DIR / OUTPUT_DIR
OUTPUT_DIR_PATH.mkdir(exist_ok=True)
CHAPTERS_PATH = OUTPUT_DIR_PATH / CHAPTERS_SUBDIR
CHAPTERS_PATH.mkdir(exist_ok=True)

OUTLINE_PATH = OUTPUT_DIR_PATH / "outline.json"
BOOK_MD_PATH = OUTPUT_DIR_PATH / "book.md"
BOOK_PDF_PATH = OUTPUT_DIR_PATH / "book.pdf"
