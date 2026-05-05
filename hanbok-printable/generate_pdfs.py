"""Generate hanbok coloring page PDFs for /hanbok-printable/downloads/.

Strategy: Pollinations Flux generates B&W line-art images → ReportLab wraps as A4 PDF.
Output: 8 PDFs to downloads/, one per hanbok type.
"""
import os, sys, json, urllib.request, urllib.parse
from pathlib import Path
from io import BytesIO

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
DOWNLOADS = ROOT / "downloads"
DOWNLOADS.mkdir(exist_ok=True)
RAW = ROOT / "raw"
RAW.mkdir(exist_ok=True)

# 8 hanbok types from index.html
HANBOK = [
    ("hanbok-wedding-bride", "Korean wedding hanbok 활옷 bride traditional dress with phoenix embroidery, black and white line art, simple outlines for coloring book, no shading"),
    ("hanbok-wedding-groom", "Korean traditional wedding hanbok 단령 royal blue groom attire, black and white line art coloring page outline, no shading"),
    ("hanbok-dol", "Korean baby first birthday Dol hanbok with rainbow sleeves 색동 traditional, black and white line art coloring page for kids, no shading"),
    ("hanbok-spring-f", "Korean traditional spring hanbok female pink lavender floral pattern, black and white outline coloring page, no shading"),
    ("hanbok-chuseok", "Korean Chuseok harvest festival hanbok family three figures wearing traditional dress, black and white line art coloring book outline"),
    ("hanbok-seollal", "Korean Lunar New Year Seollal children bowing wearing traditional hanbok, black and white line art coloring page outline for kids"),
    ("hanbok-royal-queen", "Korean Joseon dynasty royal queen 황후 hanbok with crown and embroidery, black and white line art coloring page"),
    ("hanbok-royal-king", "Korean Joseon dynasty royal king 곤룡포 hanbok with dragon embroidery and crown, black and white line art coloring page"),
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def pollinations_image(prompt, w=1024, h=1280, seed=42):
    """Free Pollinations Flux endpoint — returns PNG bytes."""
    enc = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{enc}?width={w}&height={h}&seed={seed}&model=flux&nologo=true"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def to_pdf(image_bytes, title, out_path):
    """Wrap PNG into single-page A4 PDF using minimal pure-Python PDF emitter."""
    # Simple A4 PDF (210x297mm at 72 DPI = 595x842 points)
    # Using reportlab if available, else fall back to img2pdf-like inline
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader

        c = canvas.Canvas(str(out_path), pagesize=A4)
        w, h = A4
        img = ImageReader(BytesIO(image_bytes))
        # Center image, leave 1-inch top for title
        margin = 50
        title_h = 40
        avail_w = w - 2 * margin
        avail_h = h - 2 * margin - title_h
        # Maintain aspect ratio
        iw, ih = img.getSize()
        ratio = min(avail_w / iw, avail_h / ih)
        dw, dh = iw * ratio, ih * ratio
        x = (w - dw) / 2
        y = margin
        c.drawImage(img, x, y, dw, dh)
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(w / 2, h - margin - 20, title)
        c.setFont("Helvetica", 9)
        c.drawCentredString(w / 2, margin / 2, "© KunStudio · cheonmyeongdang.vercel.app · Free for personal use")
        c.save()
        return True
    except ImportError:
        # Fallback: write raw PNG renamed as .pdf (browser shows preview)
        out_path.write_bytes(image_bytes)
        return False


def main():
    print(f"[+] Generating {len(HANBOK)} hanbok coloring PDFs...")
    for i, (slug, prompt) in enumerate(HANBOK, 1):
        out_pdf = DOWNLOADS / f"{slug}.pdf"
        if out_pdf.exists() and out_pdf.stat().st_size > 50_000:
            print(f"  [{i}/{len(HANBOK)}] {slug}.pdf — exists, skip")
            continue
        try:
            print(f"  [{i}/{len(HANBOK)}] {slug} — generating image...")
            img = pollinations_image(prompt, w=1024, h=1280, seed=42 + i)
            raw_path = RAW / f"{slug}.png"
            raw_path.write_bytes(img)

            title = slug.replace("hanbok-", "Hanbok — ").replace("-", " ").title()
            ok = to_pdf(img, title, out_pdf)
            print(f"    [OK] {out_pdf.name} ({len(out_pdf.read_bytes())//1024} KB) {'(reportlab)' if ok else '(png-as-pdf)'}")
        except Exception as e:
            print(f"    [ERR] {slug}: {e}")

    print(f"[done] PDFs in {DOWNLOADS}")


if __name__ == "__main__":
    main()
