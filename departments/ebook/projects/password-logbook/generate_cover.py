"""
📚 Password Logbook — KDP Cover Generator
KDP Paperback Cover: Front only (6.14 x 9.21 inches at 300 DPI for 8.5x11 trim)
Actually for 8.5x11 trim, front cover = 8.75 x 11.25 inches (with bleed)
We'll make a simple front cover image. KDP Cover Creator can add spine+back.
"""

from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "Password_Logbook_Cover.pdf"

# 8.5 x 11 front cover with 0.125" bleed each side
W = 8.75 * inch
H = 11.25 * inch
BLEED = 0.125 * inch

DARK = HexColor("#0f0f2e")
ACCENT = HexColor("#4a90d9")
GOLD = HexColor("#d4a843")


def generate_cover():
    c = canvas.Canvas(str(PDF_PATH), pagesize=(W, H))

    # Background
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1)

    # Decorative frame
    margin = 0.5 * inch
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.rect(margin, margin, W - 2*margin, H - 2*margin)
    c.setLineWidth(1)
    c.rect(margin + 8, margin + 8, W - 2*margin - 16, H - 2*margin - 16)

    # Corner decorations
    for x, y in [(margin+20, H-margin-20), (W-margin-20, H-margin-20),
                  (margin+20, margin+20), (W-margin-20, margin+20)]:
        c.setFillColor(GOLD)
        c.circle(x, y, 4, fill=1)

    # Lock icon
    cx, cy = W/2, H * 0.65
    # Lock body
    c.setFillColor(ACCENT)
    c.roundRect(cx-40, cy-50, 80, 60, 8, fill=1)
    # Lock shackle
    c.setStrokeColor(ACCENT)
    c.setLineWidth(8)
    c.arc(cx-25, cy+5, cx+25, cy+55, 0, 180)
    # Keyhole
    c.setFillColor(DARK)
    c.circle(cx, cy-15, 10, fill=1)
    c.rect(cx-4, cy-35, 8, 15, fill=1)

    # Title
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(W/2, H * 0.50, "PASSWORD")
    c.drawCentredString(W/2, H * 0.44, "LOGBOOK")

    # Decorative line
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(W/2 - 80, H*0.42, W/2 + 80, H*0.42)

    # Subtitle
    c.setFont("Helvetica", 16)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, H * 0.37, "Keep Your Internet Passwords")
    c.drawCentredString(W/2, H * 0.34, "Safe & Organized")

    # Features
    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor("#aaaaaa"))
    features = [
        "Alphabetical A-Z Tabs",
        "Large Print for Easy Reading",
        "120+ Pages",
        "Space for Website, URL, Username & Password",
        "Additional Notes Section",
    ]
    y = H * 0.26
    for f in features:
        c.drawCentredString(W/2, y, f"•  {f}")
        y -= 20

    # Bottom
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(GOLD)
    c.drawCentredString(W/2, margin + 40, "Deokgu Studio")

    c.save()
    print(f"Cover PDF generated: {PDF_PATH}")
    print(f"File size: {os.path.getsize(PDF_PATH) / 1024:.0f} KB")


if __name__ == "__main__":
    generate_cover()
