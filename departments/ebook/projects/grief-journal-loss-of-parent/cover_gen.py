"""Front-cover generator for 'Grief Journal for Loss of a Parent'.

KDP cover wizard expects a single full-bleed cover JPG/PDF; this script
produces a 6.25 x 9.25 in front-only PDF (front + 0.125" bleed each side).
The KDP cover creator can ingest this and add the spine/back automatically,
or the file can be used as-is for sample previews.
"""
import os
import math
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

W = 6.25 * inch
H = 9.25 * inch
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.pdf")

DARK = HexColor("#2F3E54")
ACCENT = HexColor("#7E96B0")
WARM = HexColor("#C8A989")
CREAM = HexColor("#F6F1E8")


def build():
    c = canvas.Canvas(OUTPUT, pagesize=(W, H))

    # background cream
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # top dark band
    c.setFillColor(DARK)
    c.rect(0, H * 0.55, W, H * 0.30, fill=1, stroke=0)

    # main title
    c.setFillColor(CREAM)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W / 2, H * 0.76, "GRIEF")
    c.drawCentredString(W / 2, H * 0.71, "JOURNAL")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.665, "for the")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.61, "LOSS OF A PARENT")

    # subtitle on cream
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(W / 2, H * 0.49, "A Guided Companion for the First Year")
    c.drawCentredString(W / 2, H * 0.46, "After Losing Your Mother or Father")

    # decorative ring
    cx, cy = W / 2, H * 0.30
    c.setFillColor(WARM)
    for i in range(12):
        a = i * (math.pi / 6)
        c.circle(cx + 26 * math.cos(a), cy + 26 * math.sin(a), 3, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.circle(cx, cy, 6, fill=1, stroke=0)

    # bullets band
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9.5)
    bullets = [
        "First-week prompts  -  60 daily check-ins",
        "Weekly reflections  -  1, 3, 6, 12-month milestones",
        "Letter pages  -  memorial lists  -  resources",
    ]
    by = H * 0.18
    for line in bullets:
        c.drawCentredString(W / 2, by, line)
        by -= 14

    # author
    c.setFont("Helvetica", 10)
    c.setFillColor(WARM)
    c.drawCentredString(W / 2, H * 0.06, "DEOKGU STUDIO")

    c.save()
    return OUTPUT


if __name__ == "__main__":
    print("Wrote", build())
