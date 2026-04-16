"""Yoga Progress Journal - 6x9, 94 pages"""
import os
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = 6*inch, 9*inch
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yoga_progress_journal.pdf")

DARK = HexColor("#4A148C")
ACCENT = HexColor("#7B1FA2")
LIGHT = HexColor("#F3E5F5")
MID_GRAY = HexColor("#CCCCCC")
SAGE = HexColor("#66BB6A")


def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0.75*inch, H*0.46, W - 1.5*inch, 3, fill=1, stroke=0)
    c.rect(0.75*inch, H*0.58, W - 1.5*inch, 3, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W/2, H*0.54, "Yoga Progress")
    c.drawCentredString(W/2, H*0.54 - 34, "Journal")
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H*0.38, "Daily Practice | Pose Checklist | Meditation")
    c.setFont("Helvetica", 10)
    c.drawCentredString(W/2, H*0.10, "Deokgu Studio")
    c.showPage()


def draw_personal_page(c):
    margin = 0.6*inch
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(DARK)
    c.drawCentredString(W/2, H - 0.8*inch, "My Yoga Journey")
    y = H - 1.5*inch
    fields = ["Name:", "Date Started:", "Experience Level:", "Goals:", "", "",
              "Favorite Poses:", "", "Health Notes:", "", "Instructor/Studio:"]
    c.setFont("Helvetica", 10)
    for f in fields:
        if f:
            c.drawString(margin, y + 3, f)
            c.setStrokeColor(MID_GRAY)
            c.line(margin + 120, y, W - margin, y)
        else:
            c.line(margin, y, W - margin, y)
        y -= 24
    c.showPage()


POSES = [
    "Mountain (Tadasana)", "Downward Dog", "Warrior I", "Warrior II",
    "Tree Pose", "Child's Pose", "Cobra", "Cat-Cow",
    "Triangle", "Pigeon", "Bridge", "Savasana",
    "Chair Pose", "Plank", "Seated Forward Fold"
]


def draw_daily_log(c, day_num):
    margin = 0.6*inch
    top = H - margin
    c.setFillColor(ACCENT)
    c.rect(margin, top - 24, W - 2*margin, 24, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 6, top - 18, f"Day {day_num}")
    c.drawRightString(W - margin - 6, top - 18, "Date: ____/____/____")

    y = top - 40
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y, "Duration: _____ min     Type: _______________     Instructor: _______________")

    # Pose checklist
    y -= 22
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y, "Poses Practiced:")
    y -= 6
    c.setFont("Helvetica", 8)
    col_w = (W - 2*margin) / 2
    for i, pose in enumerate(POSES):
        col = i % 2
        row = i // 2
        px = margin + col * col_w + 4
        py = y - row * 14
        # Checkbox
        c.setStrokeColor(MID_GRAY)
        c.rect(px, py - 2, 8, 8, fill=0, stroke=1)
        c.setFillColor(DARK)
        c.drawString(px + 12, py, pose)

    y -= (len(POSES) // 2 + 1) * 14 + 8

    # Flexibility tracker
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y, "Flexibility Check:")
    y -= 16
    flex = ["Forward Fold (fingers to): ___ floor / ___ toes / ___ shins",
            "Seated Straddle: ___ / 10     Backbend: ___ / 10"]
    c.setFont("Helvetica", 8)
    for f in flex:
        c.drawString(margin + 8, y, f)
        y -= 14

    # Mood & energy
    y -= 10
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK)
    c.drawString(margin, y, "Before Practice:")
    c.drawString(margin + (W - 2*margin)/2, y, "After Practice:")
    y -= 14
    c.setFont("Helvetica", 8)
    c.drawString(margin, y, "Energy: 1 2 3 4 5")
    c.drawString(margin + (W - 2*margin)/2, y, "Energy: 1 2 3 4 5")
    y -= 14
    c.drawString(margin, y, "Mood: 1 2 3 4 5")
    c.drawString(margin + (W - 2*margin)/2, y, "Mood: 1 2 3 4 5")
    y -= 14
    c.drawString(margin, y, "Stress: 1 2 3 4 5")
    c.drawString(margin + (W - 2*margin)/2, y, "Stress: 1 2 3 4 5")

    # Meditation
    y -= 20
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK)
    c.drawString(margin, y, "Meditation:  ___ min    Type: _______________")

    # Notes
    y -= 20
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y, "Reflections & Notes:")
    y -= 6
    for _ in range(4):
        y -= 16
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 6)
    c.drawCentredString(W/2, margin - 8, "Yoga Progress Journal | Deokgu Studio")
    c.showPage()


def draw_weekly_review(c, week):
    margin = 0.6*inch
    top = H - margin
    c.setFillColor(SAGE)
    c.rect(margin, top - 28, W - 2*margin, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W/2, top - 20, f"Week {week} Review")

    y = top - 50
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y, "Sessions This Week: ____     Total Minutes: ____")
    y -= 22
    c.drawString(margin, y, "Favorite Practice: ________________________________")
    y -= 22
    c.drawString(margin, y, "New Pose Achieved: _______________________________")
    y -= 22
    c.drawString(margin, y, "Biggest Challenge: ________________________________")
    y -= 28

    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Weekly Intention:")
    y -= 6
    for _ in range(3):
        y -= 16
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    y -= 24
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Gratitude:")
    y -= 6
    for _ in range(3):
        y -= 16
        c.line(margin, y, W - margin, y)

    y -= 24
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Next Week Goals:")
    y -= 6
    for _ in range(3):
        y -= 16
        c.line(margin, y, W - margin, y)

    c.showPage()


def draw_30day_challenge(c):
    margin = 0.6*inch
    top = H - margin
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W/2, top - 25, "30-Day Yoga Challenge")
    y = top - 50
    c.setFont("Helvetica", 8)
    box_w = (W - 2*margin) / 5
    box_h = 40
    for i in range(30):
        col = i % 5
        row = i // 5
        bx = margin + col * box_w
        by = y - row * (box_h + 8)
        c.setStrokeColor(ACCENT)
        c.setFillColor(LIGHT)
        c.rect(bx + 2, by - box_h, box_w - 4, box_h, fill=1, stroke=1)
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(bx + 6, by - 12, f"Day {i+1}")
        c.setFont("Helvetica", 7)
        c.drawString(bx + 6, by - 24, "__ min")
        # Checkbox
        c.setStrokeColor(MID_GRAY)
        c.rect(bx + box_w - 16, by - 14, 8, 8, fill=0, stroke=1)
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=(W, H))
    c.setTitle("Yoga Progress Journal")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_personal_page(c)
    draw_30day_challenge(c)

    # 12 weeks: 7 daily + 1 review = 8 pages per week = 96 content pages
    # + 3 front pages = ~99, but we do ~90 days + reviews
    for week in range(1, 12):
        for day in range(1, 8):
            draw_daily_log(c, (week - 1) * 7 + day)
        draw_weekly_review(c, week)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
