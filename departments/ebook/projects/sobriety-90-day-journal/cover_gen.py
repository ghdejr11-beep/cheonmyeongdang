"""Generate KDP front cover PDF for Sobriety 90-Day Journal.
6x9 trim with 0.125" bleed on all sides => 6.25 x 9.25 in.
Front cover only (KDP also accepts wraparound; we provide the front for upload).
"""
import os, math
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, Color
from reportlab.pdfgen import canvas

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.pdf")

W, H = 6.25 * inch, 9.25 * inch

DARK = HexColor("#1F4E5F")
ACCENT = HexColor("#4A8B9D")
SAND = HexColor("#F5EBD7")
GOLD = HexColor("#C8A24A")
WHITE = white


def main():
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Sobriety Journal Cover")

    # Background full bleed deep teal
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Sand band middle (60% to 75% of height)
    c.setFillColor(SAND)
    c.rect(0, H * 0.55, W, H * 0.13, fill=1, stroke=0)

    # Decorative gold thin lines top and bottom of sand band
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(0.5 * inch, H * 0.55 + 4, W - 0.5 * inch, H * 0.55 + 4)
    c.line(0.5 * inch, H * 0.68 - 4, W - 0.5 * inch, H * 0.68 - 4)

    # Sun/horizon decoration upper area (subtle hope motif)
    c.setStrokeColor(Color(1, 1, 1, alpha=0.18))
    c.setLineWidth(0.6)
    cx, cy, r = W / 2, H * 0.83, 1.0 * inch
    c.circle(cx, cy, r, fill=0)
    c.circle(cx, cy, r * 0.66, fill=0)
    c.circle(cx, cy, r * 0.33, fill=0)

    # Title block
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(W / 2, H * 0.62, "SOBRIETY")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W / 2, H * 0.575, "JOURNAL")

    # Days callout - large gold "90"
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 84)
    c.drawCentredString(W / 2, H * 0.36, "90")
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 14)
    c.drawCentredString(W / 2, H * 0.32, "DAYS TO CLARITY")

    # Subtitle
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, H * 0.24, "A Daily Recovery Companion")
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, H * 0.215, "for Quitting Alcohol & Drugs")

    # Feature bullets
    c.setFillColor(SAND)
    c.setFont("Helvetica", 9)
    feats = [
        "DAILY PROMPTS  -  TRIGGERS  -  GRATITUDE",
        "WEEKLY CHECK-INS  -  EMERGENCY PLAN",
        "30 / 60 / 90 DAY MILESTONE REFLECTIONS",
    ]
    fy = H * 0.16
    for line in feats:
        c.drawCentredString(W / 2, fy, line)
        fy -= 14

    # Author bottom
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, H * 0.07, "DEOKGU STUDIO")

    # Corner accents (small gold dots)
    c.setFillColor(GOLD)
    for x, y in [(0.5 * inch, H - 0.5 * inch), (W - 0.5 * inch, H - 0.5 * inch),
                 (0.5 * inch, 0.5 * inch), (W - 0.5 * inch, 0.5 * inch)]:
        c.circle(x, y, 3, fill=1, stroke=0)

    c.save()
    print(f"Cover: {OUT}  size: {os.path.getsize(OUT)/1024:.1f} KB")


if __name__ == "__main__":
    main()
