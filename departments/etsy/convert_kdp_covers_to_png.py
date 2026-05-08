"""KDP cover.pdf → PNG 일괄 변환 (Vela 업로드용).

각 ebook project/cover.pdf를 Etsy listing primary image로 사용하기 위해 PNG로 변환.
출력: departments/etsy/cover_kdp_png/{project_slug}.png
"""
import os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # cheonmyeongdang/departments/
PROJECTS = ROOT / "ebook" / "projects"  # cheonmyeongdang/departments/ebook/projects
OUT_DIR = ROOT / "etsy" / "cover_kdp_png"  # cheonmyeongdang/departments/etsy/cover_kdp_png

if not PROJECTS.exists():
    print(f"[ERR] PROJECTS not found: {PROJECTS}")
    raise SystemExit(1)
print(f"[INFO] PROJECTS = {PROJECTS}")
print(f"[INFO] OUT_DIR = {OUT_DIR}")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# pdftoppm 또는 ImageMagick. Windows에서 ImageMagick magick.exe 사용.
MAGICK_CANDIDATES = [
    r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe",
    r"C:\ProgramData\chocolatey\bin\magick.exe",
    "magick",
]
magick = None
for m in MAGICK_CANDIDATES:
    try:
        r = subprocess.run([m, "-version"], capture_output=True, timeout=5)
        if r.returncode == 0:
            magick = m
            break
    except Exception:
        continue

# fallback: PyMuPDF (fitz) — pure Python PDF rendering
try:
    import fitz  # PyMuPDF
    have_fitz = True
except ImportError:
    have_fitz = False

if not magick and not have_fitz:
    print("[ERR] Neither ImageMagick nor PyMuPDF available. Install: pip install PyMuPDF")
    raise SystemExit(1)

print(f"Using: {magick or 'PyMuPDF/fitz'}")

ok_count = 0
skip_count = 0
fail_count = 0

for proj_dir in sorted(PROJECTS.iterdir()):
    if not proj_dir.is_dir():
        continue
    cover_pdf = proj_dir / "cover.pdf"
    if not cover_pdf.exists():
        continue
    out_png = OUT_DIR / f"{proj_dir.name}.png"
    if out_png.exists() and out_png.stat().st_size > 1000:
        skip_count += 1
        continue
    try:
        if have_fitz:
            doc = fitz.open(str(cover_pdf))
            page = doc[0]  # first page (front cover)
            # 300 DPI for high quality
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x = ~144 dpi
            pix.save(str(out_png))
            doc.close()
        else:
            cmd = [magick, "-density", "150", str(cover_pdf) + "[0]",
                   "-quality", "92", "-resize", "2000x2000>", str(out_png)]
            subprocess.run(cmd, capture_output=True, timeout=30, check=True)
        if out_png.exists() and out_png.stat().st_size > 1000:
            ok_count += 1
            print(f"  [OK] {proj_dir.name}.png ({out_png.stat().st_size//1024}KB)")
        else:
            fail_count += 1
    except Exception as e:
        fail_count += 1
        print(f"  [FAIL] {proj_dir.name}: {e}")

print(f"\n=== Total: OK={ok_count} SKIP={skip_count} FAIL={fail_count} ===")
print(f"Output: {OUT_DIR}")
