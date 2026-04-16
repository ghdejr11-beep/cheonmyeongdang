"""
📚 Sleep Improvement Planner — Amazon KDP Ready
8.5 x 11 inches, ~100 pages
90-night sleep tracker + wind-down routines + sleep hygiene tips
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "Sleep_Planner_Interior.pdf"
W, H = letter
M = 0.75 * inch

NAVY = HexColor("#1B2838")
MOON = HexColor("#F5E6CA")
STAR = HexColor("#FFD700")
PURPLE = HexColor("#6C5B9E")
SKY = HexColor("#2D4059")
LINE = HexColor("#D5D0E0")
LIGHT = HexColor("#F0EDF5")
TEXT = HexColor("#333344")


def draw_title_page(c):
    c.setFillColor(NAVY)
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
    cx = W/2

    # Stars (inside margins only)
    import random
    random.seed(42)
    c.setFillColor(STAR)
    for _ in range(40):
        sx = random.randint(int(M)+10, int(W-M)-10)
        sy = random.randint(int(M)+10, int(H-M)-10)
        c.circle(sx, sy, random.choice([1,1.5,2]), fill=1)

    # Moon (inside margins)
    c.setFillColor(MOON)
    c.circle(cx+60, H*0.72, 30, fill=1)
    c.setFillColor(NAVY)
    c.circle(cx+72, H*0.74, 25, fill=1)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(cx, H*0.52, "SLEEP")
    c.drawCentredString(cx, H*0.46, "IMPROVEMENT")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(MOON)
    c.drawCentredString(cx, H*0.40, "PLANNER")

    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#aaaacc"))
    c.drawCentredString(cx, H*0.32, "90-Night Sleep Tracker")
    c.drawCentredString(cx, H*0.29, "Wind-Down Routines & Sleep Hygiene Guide")

    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#666688"))
    c.drawCentredString(cx, M+20, "Track · Improve · Rest Better  |  100+ Pages")
    c.showPage()


def draw_sleep_tips(c):
    y = H - M
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(PURPLE)
    c.drawCentredString(W/2, y, "Sleep Hygiene Essentials")
    y -= 35

    tips = [
        ("Same Time Every Day", "Go to bed and wake up at the same time — even weekends. Your body clock needs consistency."),
        ("Screen Curfew", "No screens 60 minutes before bed. Blue light suppresses melatonin. Read a book instead."),
        ("Cool & Dark Room", "Ideal temperature: 65-68°F (18-20°C). Use blackout curtains. Your brain sleeps better in the dark."),
        ("No Caffeine After 2pm", "Caffeine has a 6-hour half-life. That 3pm coffee is still in your system at 9pm."),
        ("Wind-Down Ritual", "Create a 30-min routine: dim lights → warm drink → journal → breathing. Signal your brain it's time."),
        ("Bed = Sleep Only", "Don't work, scroll, or worry in bed. Train your brain: bed means sleep."),
        ("Dump Your Worries", "Racing thoughts? Write them in this planner. Getting them out of your head is the first step."),
        ("Move Your Body", "Exercise helps sleep — but finish at least 3 hours before bed."),
    ]

    for title, desc in tips:
        c.setFillColor(PURPLE)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(M, y, f"• {title}")
        y -= 16
        c.setFillColor(TEXT)
        c.setFont("Helvetica", 9.5)
        words = desc.split()
        line = ""
        for w in words:
            test = line + " " + w if line else w
            if c.stringWidth(test, "Helvetica", 9.5) > W - 2*M - 30:
                c.drawString(M+15, y, line)
                y -= 13
                line = w
            else:
                line = test
        if line:
            c.drawString(M+15, y, line)
            y -= 13
        y -= 8
    c.showPage()


def draw_nightly_page(c, night):
    y = H - M

    # Header (inside margins)
    c.setFillColor(LIGHT)
    c.rect(M+5, H-M-40, W-2*M-10, 38, fill=1)
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(M+10, H-M-25, f"Night {night}")
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 10)
    c.drawRightString(W-M-5, H-M-25, "Date: _______________")
    y = H - M - 50

    # Pre-sleep checklist
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M, y, "Pre-Sleep Checklist")
    y -= 18
    checks = ["No caffeine after 2pm", "Screens off 60min before bed",
              "Room cool & dark", "Wind-down routine done"]
    for ch in checks:
        c.setStrokeColor(LINE)
        c.setLineWidth(1.2)
        c.roundRect(M+5, y-9, 11, 11, 2)
        c.setFillColor(TEXT)
        c.setFont("Helvetica", 9)
        c.drawString(M+22, y-6, ch)
        y -= 18

    # Sleep data
    y -= 10
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M, y, "Sleep Data")
    y -= 20

    fields = [
        ("Bedtime:", "___:___ PM/AM"),
        ("Wake time:", "___:___ AM"),
        ("Hours slept:", "_____ hours"),
        ("Time to fall asleep:", "_____ min"),
        ("Night wakings:", "_____ times"),
    ]
    for label, placeholder in fields:
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(M+10, y, label)
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#999999"))
        c.drawString(M+120, y, placeholder)
        y -= 18

    # Sleep quality
    y -= 8
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M, y, "Sleep Quality:")
    qualities = ["Terrible", "Poor", "OK", "Good", "Amazing"]
    ex = M + 110
    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT)
    for q in qualities:
        c.circle(ex, y+3, 5)
        c.drawString(ex+8, y, q)
        ex += 70
    y -= 25

    # Energy next morning
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M, y, "Morning Energy:")
    levels = ["Exhausted", "Low", "Medium", "High", "Refreshed"]
    ex = M + 120
    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT)
    for lv in levels:
        c.circle(ex, y+3, 5)
        c.drawString(ex+8, y, lv)
        ex += 70
    y -= 30

    # What helped / what hurt
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(M, y, "What helped me sleep:")
    y -= 16
    c.setStrokeColor(LINE)
    c.setLineWidth(0.3)
    for _ in range(2):
        c.line(M+10, y, W-M, y)
        y -= 18

    y -= 5
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(M, y, "What hurt my sleep:")
    y -= 16
    for _ in range(2):
        c.line(M+10, y, W-M, y)
        y -= 18

    # Dream journal
    y -= 5
    c.setFillColor(MOON)
    c.roundRect(M, y-70, W-2*M, 75, 8, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(M+10, y-10, "Dream Journal (optional)")
    c.setStrokeColor(HexColor("#CCBFA0"))
    c.setLineWidth(0.3)
    for i in range(3):
        c.line(M+10, y-28-i*18, W-M-10, y-28-i*18)

    c.showPage()


def draw_weekly_sleep_review(c, week):
    y = H - M
    c.setFillColor(PURPLE)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W/2, y, f"Week {week} Sleep Review")
    y -= 35

    qs = [
        ("Average hours slept this week:", 1),
        ("Best night this week — what was different?", 3),
        ("Worst night — what went wrong?", 3),
        ("Pattern I noticed:", 3),
        ("One thing I'll try next week:", 2),
        ("Overall sleep rating (1-10):", 1),
    ]
    for q, lines in qs:
        c.setFillColor(PURPLE)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(M, y, q)
        y -= 18
        c.setStrokeColor(LINE)
        c.setLineWidth(0.3)
        for _ in range(lines):
            c.line(M+10, y, W-M, y)
            y -= 18
        y -= 10
    c.showPage()


def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("Sleep Improvement Planner")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_sleep_tips(c)

    for night in range(1, 91):
        draw_nightly_page(c, night)
        if night % 7 == 0:
            draw_weekly_sleep_review(c, night // 7)

    # Final page
    c.setFillColor(NAVY)
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
    c.setFillColor(MOON)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W/2, H/2+20, "Sweet Dreams.")
    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor("#ffffff"))
    c.drawCentredString(W/2, H/2-15, "90 nights of tracking. Real data. Better sleep.")
    c.setFillColor(STAR)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H/2-55, "Please leave a review on Amazon!")
    c.showPage()

    c.save()
    print(f"PDF: {PDF_PATH}")
    print(f"Pages: {c.getPageNumber()-1}")
    print(f"Size: {os.path.getsize(PDF_PATH)/1024:.0f} KB")

if __name__ == "__main__":
    generate()
