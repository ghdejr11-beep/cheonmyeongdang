#!/usr/bin/env python3
"""AI Side Hustle 전용 표지 재생성 (브랜드명 제거 버전)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from regenerate_rejected_covers import generate_clean_cover, BOOKS_TO_FIX

folder = 'ai-side-hustle-en'
data = BOOKS_TO_FIX[folder]
print("=" * 60)
print("AI Side Hustle 표지 재생성 (v2 - 브랜드명 제거)")
print("=" * 60)
print()
print(f"새 부제: {' / '.join(data['subtitle_lines'])}")
print(f"저자: {data['author']}")
print()
generate_clean_cover(folder, data)
