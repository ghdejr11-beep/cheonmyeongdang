"""Cover for Pet Loss Memorial Journal (front-only PDF, 6.25 x 9.25 in)
KDP cover wizard handles spine + back during upload."""
import os
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas

PAGE = (6.25 * inch, 9.25 * inch)
W, H = PAGE
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.pdf")

DARK = HexColor("#3F5E48")
CREAM = HexColor("#F7EFE2")
ROSE = HexColor("#D9A6A0")


def main():
    c = canvas.Canvas(OUTPUT, pagesize=PAGE)
    c.setTitle("Pet Loss Memorial Journal Cover")

    # cream background
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # sage band
    c.setFillColor(DARK)
    c.rect(0, H * 0.42, W, H * 0.20, fill=1, stroke=0)

    # title
    c.setFillColor(CREAM)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W / 2, H * 0.55, "PET LOSS")
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W / 2, H * 0.46, "MEMORIAL JOURNAL")

    # subtitle
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(W / 2, H * 0.36, "A Healing Companion Through")
    c.drawCentredString(W / 2, H * 0.33, "the Grief of Losing Your Best Friend")

    # paw print
    cx, cy, r = W / 2, H * 0.22, 6
    c.setFillColor(ROSE)
    for dx, dy in [(-16, 0), (16, 0), (-8, 12), (8, 12)]:
        c.circle(cx + dx, cy + dy, r, fill=1, stroke=0)
    c.circle(cx, cy - 10, 11, fill=1, stroke=0)

    # author
    c.setFillColor(DARK)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, H * 0.07, "Deokgu Studio")

    c.save()
    print(f"Cover: {OUTPUT}  ({os.path.getsize(OUTPUT)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
