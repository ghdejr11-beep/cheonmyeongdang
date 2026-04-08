"""
노션 템플릿 50개 + 제작·판매 완전 가이드 — 중앙 설정.

이 책은 "노션 템플릿 판매로 월 100만원 부업" 을 목표로 하는
디지털 상품 사업가를 위한 200페이지 실전 가이드입니다.
"""

PRODUCT_TITLE = "노션 템플릿 50개 아이디어 + 판매 가이드"
PRODUCT_SUBTITLE = "월 100만원 디지털 상품 부업 실전 매뉴얼"
AUTHOR = "홍덕훈 (덕구네 출판)"

PRICE_KRW = 39_900

# 50개 카테고리 (10개 카테고리 × 5개 템플릿)
CATEGORIES = [
    {"id": "productivity", "name": "📋 생산성·할 일 관리", "count": 5,
     "examples": "Daily Tracker, GTD, Pomodoro, Weekly Review, Task Matrix"},
    {"id": "study", "name": "📚 학습·시험 준비", "count": 5,
     "examples": "스터디 플래너, 단어장, 시험 D-Day, 학습 일지, 노트 정리"},
    {"id": "finance", "name": "💰 가계부·재테크", "count": 5,
     "examples": "월간 가계부, 투자 추적, 부업 수익, 가족 예산, 부동산 분석"},
    {"id": "fitness", "name": "💪 운동·건강 관리", "count": 5,
     "examples": "운동 일지, 식단 트래커, 다이어트, 수면 기록, 건강검진"},
    {"id": "habit", "name": "🎯 습관 형성", "count": 5,
     "examples": "21일 챌린지, 습관 캘린더, 연속 기록, 미라클 모닝, 명상 일지"},
    {"id": "business", "name": "💼 1인 사업·자영업", "count": 5,
     "examples": "고객 CRM, 매출 대시보드, 인보이스, 사업 계획, 경쟁사 분석"},
    {"id": "content", "name": "✏️ 콘텐츠 크리에이터", "count": 5,
     "examples": "콘텐츠 캘린더, 아이디어 뱅크, 스크립트 템플릿, 분석 대시보드"},
    {"id": "wedding", "name": "💍 결혼·가족 이벤트", "count": 5,
     "examples": "결혼 준비, 신혼여행, 출산 준비, 육아 일기, 가족 행사"},
    {"id": "travel", "name": "✈️ 여행·취미", "count": 5,
     "examples": "여행 플래너, 버킷리스트, 독서 기록, 영화 리뷰, 맛집 지도"},
    {"id": "kpop", "name": "🎵 한국 특화", "count": 5,
     "examples": "사주 일지, 띠별 운세, 한국 명절, 축의금 정리, 한국 부동산"},
]

# Claude API 설정
MODEL = "claude-sonnet-4-5"  # 템플릿 설계는 sonnet 권장 (더 구조적)
MAX_TOKENS_PER_TEMPLATE = 4000

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

TEMPLATES_JSON = OUTPUT_DIR / "templates.json"
GUIDE_PDF = OUTPUT_DIR / "notion_templates_50.pdf"
