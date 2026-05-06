"""KDP wraparound cover for Migraine & Headache Tracker.

Trim: 8.5 x 11 paperback. Bleed: 0.125 in.
Spine: page_count * 0.0025 (white paper) -> 113 * 0.0025 = 0.2825 in.
Wraparound width: 0.125 + 8.5 + 0.2825 + 8.5 + 0.125 = 17.5325 in.
Wraparound height: 0.125 + 11 + 0.125 = 11.25 in.
"""
import os
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas

PAGE_COUNT = 113
SPINE = PAGE_COUNT * 0.0025 * inch
TRIM_W = 8.5 * inch
TRIM_H = 11 * inch
BLEED = 0.125 * inch

W = BLEED + TRIM_W + SPINE + TRIM_W + BLEED
H = BLEED + TRIM_H + BLEED

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.pdf")

DARK = HexColor("#2D1B4E")
ACCENT = HexColor("#6A4FBB")
SOFT = HexColor("#EDE7F6")
LIGHT = HexColor("#F5F0FA")


def draw_cover():
    c = canvas.Canvas(OUTPUT, pagesize=(W, H))
    c.setTitle("Migraine & Headache Tracker - Cover")
    c.setAuthor("Deokgu Studio")

    # Background gradient simulation: solid dark with lighter band at top/bottom
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Soft horizontal accent bands on the front (right side)
    front_x = BLEED + TRIM_W + SPINE
    front_w = TRIM_W

    # Subtle texture stripes
    c.setFillColor(ACCENT)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0)
    band_h = 6
    for i in range(0, int(H), 28):
        c.setFillColor(HexColor("#3E2A66"))
        c.rect(front_x, i, front_w, band_h, fill=1, stroke=0)

    # Title block on front
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 56)
    c.drawCentredString(front_x + front_w / 2, H * 0.70, "Migraine &")
    c.drawCentredString(front_x + front_w / 2, H * 0.70 - 60, "Headache")
    c.drawCentredString(front_x + front_w / 2, H * 0.70 - 120, "Tracker")

    # Soft divider lines
    c.setStrokeColor(SOFT)
    c.setLineWidth(2)
    c.line(front_x + 1.0 * inch, H * 0.58, front_x + front_w - 1.0 * inch, H * 0.58)
    c.line(front_x + 1.0 * inch, H * 0.42, front_x + front_w - 1.0 * inch, H * 0.42)

    # Subtitle / promise
    c.setFillColor(SOFT)
    c.setFont("Helvetica", 16)
    c.drawCentredString(front_x + front_w / 2, H * 0.50, "13-Week Daily Journal")
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(front_x + front_w / 2, H * 0.50 - 22, "Pain  -  Triggers  -  Medication  -  Hormones")

    # Promise badge
    c.setFillColor(ACCENT)
    c.roundRect(front_x + 0.6 * inch, H * 0.30, front_w - 1.2 * inch, 50, 10, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(front_x + front_w / 2, H * 0.30 + 30, "WITH NEUROLOGIST VISIT PREP")
    c.setFont("Helvetica", 11)
    c.drawCentredString(front_x + front_w / 2, H * 0.30 + 14, "120+ pages  -  8.5 x 11  -  Migraine, Tension, Cluster")

    # Author bottom
    c.setFillColor(SOFT)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(front_x + front_w / 2, BLEED + 0.7 * inch, "DEOKGU STUDIO")

    # Spine
    spine_x = BLEED + TRIM_W
    c.saveState()
    c.translate(spine_x + SPINE / 2, H / 2)
    c.rotate(90)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(0, -3, "MIGRAINE & HEADACHE TRACKER  -  DEOKGU STUDIO")
    c.restoreState()

    # Back cover
    back_x = BLEED
    back_w = TRIM_W

    c.setFillColor(SOFT)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(back_x + back_w / 2, H - 1.4 * inch, "Real Data. Better Treatment.")

    c.setFillColor(white)
    c.setFont("Helvetica", 11)
    blurb_lines = [
        "Most patients walk into a neurologist's office trying to remember",
        "the last three months from memory. This 13-week tracker fixes that.",
        "",
        "Each daily page captures peak pain, type and location, aura,",
        "associated symptoms, triggers (food, sleep, hormones, weather,",
        "stress), rescue medications, and what actually relieved the attack.",
        "",
        "Weekly Reviews surface trends. Monthly Neurologist Visit Prep",
        "pages turn raw data into a focused conversation with your doctor.",
    ]
    y = H - 2.2 * inch
    for line in blurb_lines:
        c.drawCentredString(back_x + back_w / 2, y, line)
        y -= 16

    # Bullets
    y -= 14
    c.setFillColor(SOFT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(back_x + 0.7 * inch, y, "What's inside:")
    y -= 18
    c.setFillColor(white)
    c.setFont("Helvetica", 10.5)
    bullets = [
        "13 weeks of daily attack logs (0-10 pain scale, type, location, aura)",
        "13 weekly reviews with daily pain trend chart",
        "3 Neurologist Visit Prep sheets (top triggers, plan, questions)",
        "Trigger reference: food, sleep, hormonal, environment, weather, stress",
        "Preventive & rescue medication log with MOH (overuse) alert",
        "Personal info, medical history, allergies, primary diagnosis",
    ]
    for b in bullets:
        c.drawString(back_x + 0.85 * inch, y, "-  " + b)
        y -= 16

    # Bottom tagline
    c.setFillColor(ACCENT)
    c.roundRect(back_x + 0.7 * inch, BLEED + 1.3 * inch, back_w - 1.4 * inch, 60, 8, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(back_x + back_w / 2, BLEED + 1.3 * inch + 38, "BRING THIS BOOK TO YOUR NEXT")
    c.drawCentredString(back_x + back_w / 2, BLEED + 1.3 * inch + 22, "APPOINTMENT - WITH EVIDENCE.")

    c.setFillColor(SOFT)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(back_x + back_w / 2, BLEED + 0.6 * inch,
                        "This is a personal journal, not medical advice.")

    c.showPage()
    c.save()
    print(f"Cover: {OUTPUT}")
    print(f"Trim: {TRIM_W/inch}x{TRIM_H/inch}  Spine: {SPINE/inch:.4f}\"  Wraparound: {W/inch:.4f}x{H/inch:.4f}\"")


if __name__ == "__main__":
    draw_cover()
