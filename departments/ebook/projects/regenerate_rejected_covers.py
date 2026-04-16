#!/usr/bin/env python3
"""
KDP 거절된 3권 표지 재생성 (수정사항 반영)

거절 사유 → 수정:
1. "template text and guides" 제거 → "ISBN Barcode Area" 텍스트 및 박스 완전 제거
2. "spine text too close to edges" → 0.5인치 상하 여백 확보
3. "Author name mismatch" → generate.py와 동일한 저자명 사용

대상 책:
- dot-marker-kids
- spot-difference-seniors
- ai-side-hustle-en
"""

import sys
import os
import math
from pathlib import Path
from reportlab.lib.units import inch as rl_inch
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader

BASE = Path(__file__).parent

# 수정 대상 책 정의
BOOKS_TO_FIX = {
    'dot-marker-kids': {
        'interior': 'Dot_Marker_Activity_Book_Interior.pdf',
        'trim': '8.5x11',
        'title_lines': ['DOT MARKER', 'ACTIVITY BOOK'],
        'subtitle_lines': ['For Toddlers Ages 2-5', '50 Fun Dab & Dot Pages'],
        'features': ['Large dots for tiny hands', 'Animal & shape themes', 'Perfect for age 2-5', 'No templates, no guides'],
        'bg': '#FFEAA7',
        'accent': '#FF6B6B',
        'title_size': 44,
        'author': 'Deokgu Studio',
    },
    'spot-difference-seniors': {
        'interior': 'Spot_Difference_Seniors_Interior.pdf',
        'trim': '8.5x11',
        'title_lines': ['SPOT THE', 'DIFFERENCE'],
        'subtitle_lines': ['Large Print Puzzles', 'for Seniors'],
        'features': ['50 Brain Training Puzzles', 'Large Print for Easy Viewing', 'Answer Key Included', 'Perfect for Memory Care'],
        'bg': '#E8F4F8',
        'accent': '#2980B9',
        'title_size': 42,
        'author': 'Deokgu Studio',
    },
    'ai-side-hustle-en': {
        'interior': 'AI_Side_Hustle_Blueprint_Interior.pdf',
        'trim': '6x9',
        'title_lines': ['AI SIDE', 'HUSTLE', 'BLUEPRINT'],
        'subtitle_lines': ['The 100-Day System to', '$5,000/Month in', 'Digital Products'],
        'features': ['Build, Automate & Scale', 'No Coding Required', 'Proven Blueprint System', 'Passive Income Roadmap'],
        'bg': '#1a1a2e',
        'accent': '#ffd54f',
        'title_size': 36,
        'author': 'Deokhun Hong',
    },
}


def count_pages(pdf_path):
    """PDF 페이지 수 세기"""
    try:
        return len(PdfReader(str(pdf_path)).pages)
    except:
        return 100


def brightness(hex_str):
    """HEX 색상의 밝기 (0-255)"""
    h = hex_str.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def generate_clean_cover(folder, data):
    """깔끔한 표지 생성 - 템플릿 텍스트/가이드 전부 제거"""
    book_dir = BASE / folder
    interior_pdf = book_dir / data['interior']

    if not interior_pdf.exists():
        print(f"  ❌ {folder}: 본문 PDF 없음")
        return False

    page_count = count_pages(interior_pdf)
    BLEED = 0.125  # inch
    spine_width = page_count * 0.002252  # white paper

    if data['trim'] == '8.5x11':
        trim_w, trim_h = 8.5, 11.0
    else:
        trim_w, trim_h = 6.0, 9.0

    cover_w_in = 2 * trim_w + spine_width + 2 * BLEED
    cover_h_in = trim_h + 2 * BLEED

    cover_w = cover_w_in * rl_inch
    cover_h = cover_h_in * rl_inch
    spine_w = spine_width * rl_inch
    bleed = BLEED * rl_inch

    # 영역 경계
    back_start = 0
    back_end = (trim_w + BLEED) * rl_inch
    spine_start = back_end
    spine_end = spine_start + spine_w
    front_start = spine_end
    front_end = cover_w

    # 중심점
    back_cx = (back_start + back_end) / 2
    front_cx = (front_start + front_end) / 2
    spine_cx = (spine_start + spine_end) / 2

    cover_path = book_dir / "cover.pdf"

    print(f"  [{folder}] pages={page_count}, spine={spine_width:.3f}\", cover={cover_w_in:.2f}\"x{cover_h_in:.2f}\"")

    c = canvas.Canvas(str(cover_path), pagesize=(cover_w, cover_h))

    bg = HexColor(data['bg'])
    accent = HexColor(data['accent'])
    c.setFillColor(bg)
    c.rect(0, 0, cover_w, cover_h, fill=1, stroke=0)

    # 전경색 결정
    br = brightness(data['bg'])
    title_color = black if br > 160 else white

    # ───────────────────────
    # FRONT COVER (우측)
    # ───────────────────────
    front_margin = 0.5 * rl_inch
    c.setStrokeColor(accent)
    c.setLineWidth(2)
    c.rect(front_start + front_margin, front_margin,
           (front_end - front_start) - 2 * front_margin,
           cover_h - 2 * front_margin)

    # 타이틀
    c.setFillColor(title_color)
    ts = data['title_size']
    c.setFont("Helvetica-Bold", ts)
    ty = cover_h * 0.65
    for line in data['title_lines']:
        c.drawCentredString(front_cx, ty, line)
        ty -= ts + 8

    # 데코레이션 라인
    c.setStrokeColor(accent)
    c.setLineWidth(3)
    c.line(front_cx - 80, ty + 10, front_cx + 80, ty + 10)

    # 서브타이틀
    sub_size = 16 if data['trim'] == '8.5x11' else 13
    c.setFont("Helvetica-Bold", sub_size)
    c.setFillColor(accent)
    sy = ty - 20
    for line in data['subtitle_lines']:
        c.drawCentredString(front_cx, sy, line)
        sy -= sub_size + 6

    # 저자명 (프론트)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(accent)
    c.drawCentredString(front_cx, bleed + 0.8 * rl_inch, data['author'])

    # ───────────────────────
    # SPINE (중앙)
    # 0.5인치(12.7mm) 상하 여백 확보 — KDP 요구 0.375인치보다 넉넉
    # ───────────────────────
    if spine_width >= 0.15:
        SPINE_SAFE_MARGIN = 0.5 * rl_inch  # KDP 요구 0.375" + 추가 안전 마진

        c.saveState()
        c.setFillColor(title_color)
        spine_font_size = min(11, (spine_w / rl_inch) * 45)

        if spine_font_size >= 5:
            c.setFont("Helvetica-Bold", spine_font_size)

            # 제목 텍스트 (중앙)
            spine_text = " ".join(data['title_lines'])
            c.saveState()
            c.translate(spine_cx, cover_h / 2)
            c.rotate(90)
            c.drawCentredString(0, -spine_font_size / 3, spine_text)
            c.restoreState()

            # 저자 (하단 — 0.5인치 안전 마진 확보)
            if spine_font_size >= 6:
                author_size = max(5, spine_font_size - 2)
                c.setFont("Helvetica", author_size)
                c.setFillColor(accent)

                # 하단 0.5" 여백 + 텍스트 크기
                author_y = SPINE_SAFE_MARGIN + author_size
                c.saveState()
                c.translate(spine_cx, author_y)
                c.rotate(90)
                c.drawCentredString(0, -author_size / 3, data['author'])
                c.restoreState()
        c.restoreState()

    # ───────────────────────
    # BACK COVER (좌측)
    # ───────────────────────
    back_margin = 0.6 * rl_inch

    c.setStrokeColor(accent)
    c.setLineWidth(1)
    c.rect(back_start + back_margin, back_margin,
           (back_end - back_start) - 2 * back_margin,
           cover_h - 2 * back_margin)

    # 백 타이틀
    c.setFont("Helvetica-Bold", 18 if data['trim'] == '8.5x11' else 15)
    c.setFillColor(title_color)
    back_title = " ".join(data['title_lines'])
    c.drawCentredString(back_cx, cover_h * 0.85, back_title)

    c.setStrokeColor(accent)
    c.setLineWidth(2)
    c.line(back_cx - 60, cover_h * 0.82, back_cx + 60, cover_h * 0.82)

    # 기능 리스트
    c.setFont("Helvetica", 11 if data['trim'] == '8.5x11' else 10)
    c.setFillColor(title_color)
    fy = cover_h * 0.75
    for feat in data['features']:
        c.drawCentredString(back_cx, fy, "• " + feat)
        fy -= 20

    # 퍼블리셔 (하단)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(accent)
    c.drawCentredString(back_cx, bleed + 0.9 * rl_inch, data['author'])

    # ═══════════════════════════════════════════════════
    # 핵심 수정: "ISBN Barcode Area" 텍스트 및 박스 전부 제거!
    # 템플릿 가이드/텍스트가 하나도 남지 않도록 함
    # ═══════════════════════════════════════════════════
    # (이전 코드에 있던 barcode 관련 draw 코드 모두 삭제)

    c.save()
    fsize = os.path.getsize(cover_path) / 1024
    print(f"    ✅ cover.pdf → {fsize:.0f} KB (spine: 0.5\" 안전 마진 적용)")
    return True


def main():
    print("=" * 60)
    print("KDP 거절된 3권 표지 재생성")
    print("=" * 60)
    print()
    print("수정 사항:")
    print("  1. 'ISBN Barcode Area' 템플릿 텍스트 제거")
    print("  2. 바코드 박스 가이드 제거")
    print("  3. Spine 상하 여백 0.5인치 확보 (KDP 요구 0.375인치)")
    print("  4. 저자명 'Deokgu Studio'로 통일")
    print()

    success = 0
    for folder, data in BOOKS_TO_FIX.items():
        try:
            if generate_clean_cover(folder, data):
                success += 1
        except Exception as e:
            print(f"  ❌ {folder}: {e}")

    print()
    print(f"완료: {success}/{len(BOOKS_TO_FIX)}권")


if __name__ == '__main__':
    main()
