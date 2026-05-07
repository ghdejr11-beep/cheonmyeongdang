"""사업자등록증명 PDF → JPG 변환 (KoDATA 가독성 정정) — 2026-05-07.

배경:
  - 5/5 발송 PDF가 KoDATA 측에서 깨져서 안 보임 (5/7 14:32 통화 안내)
  - JPG/PNG로 변환해서 재발송 권장

전략:
  - PyMuPDF (fitz) 로 1페이지 렌더 (DPI 300)
  - PIL로 JPG 저장 (quality 92, RGB)
  - 가독성 검증 위해 사이즈/dim 출력
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import fitz  # PyMuPDF
from PIL import Image
import io

INPUT_PDF = r'C:\Users\hdh02\Downloads\사업자등록증명서.pdf'
INPUT_PDF_FALLBACK = r'C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\applications\gyeongbuk_doyak\docs\01_사업자등록증명.pdf'
OUTPUT_DIR = r'C:\Users\hdh02\Desktop\cheonmyeongdang\departments\tax\applications\round2_2026_05'
OUTPUT_JPG = os.path.join(OUTPUT_DIR, '사업자등록증_쿤스튜디오_2026-05-07.jpg')
DPI = 300


def main():
    src = INPUT_PDF if os.path.isfile(INPUT_PDF) else INPUT_PDF_FALLBACK
    print(f'[STEP 1] 입력 PDF : {src}')
    print(f'         크기      : {os.path.getsize(src):,} bytes')

    doc = fitz.open(src)
    print(f'         페이지수  : {len(doc)}')

    if len(doc) == 0:
        raise RuntimeError('PDF에 페이지가 없습니다.')

    # 1페이지만 (사업자등록증명서는 보통 1p)
    page = doc[0]
    zoom = DPI / 72.0  # PDF default 72 DPI
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    print(f'[STEP 2] 렌더 완료: {pix.width}x{pix.height} ({DPI} DPI)')

    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img.save(OUTPUT_JPG, 'JPEG', quality=92, optimize=True)
    print(f'[STEP 3] JPG 저장 : {OUTPUT_JPG}')
    print(f'         크기      : {os.path.getsize(OUTPUT_JPG):,} bytes')
    print(f'         DPI       : {DPI}')
    print()
    print('가독성 체크:')
    print(f'  - 가로 {pix.width}px / 세로 {pix.height}px')
    print(f'  - 일반 A4 PDF (595x842 pt) → 300 DPI = ~2480x3508px')
    if pix.width >= 2000 and pix.height >= 2800:
        print('  [OK] 인쇄 품질 (300 DPI). KoDATA 가독성 충분.')
    else:
        print(f'  [WARN] 해상도 낮음. 원본 PDF 페이지가 작을 수 있음.')

    doc.close()
    return OUTPUT_JPG


if __name__ == '__main__':
    out = main()
    print()
    print(f'OUTPUT={out}')
