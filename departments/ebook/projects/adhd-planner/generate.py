"""
📚 ADHD Daily Planner for Adults — Amazon KDP Ready
8.5 x 11 inches, ~150 pages
Designed specifically for ADHD brains: simple, visual, dopamine-friendly
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "ADHD_Planner_Interior.pdf"

W, H = letter
MARGIN = 0.75 * inch

# ADHD-friendly colors (calming but not boring)
BG = HexColor("#ffffff")
PRIMARY = HexColor("#5B6ABF")      # Calm blue-purple
SECONDARY = HexColor("#F0936E")    # Warm coral
ACCENT = HexColor("#4CAF93")       # Teal green
LIGHT_BG = HexColor("#F5F3FF")     # Very light purple
LINE = HexColor("#E0DCF0")
TEXT = HexColor("#2D2D3F")
GRAY = HexColor("#999999")
CHECKBOX = HexColor("#D0CCE0")


def checkbox(c, x, y, size=12):
    c.setStrokeColor(CHECKBOX)
    c.setLineWidth(1.5)
    c.roundRect(x, y - size + 3, size, size, 2)


def draw_title_page(c):
    c.setFillColor(PRIMARY)
    c.rect(MARGIN+5, MARGIN+5, W - 2*MARGIN-10, H - 2*MARGIN-10, fill=1)

    # Brain icon (simple)
    cx, cy = W/2, H*0.62
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 60)
    c.drawCentredString(cx, cy, "ADHD")

    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(cx, cy - 55, "DAILY PLANNER")

    # Decorative line
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(3)
    c.line(cx - 100, cy - 75, cx + 100, cy - 75)

    c.setFont("Helvetica", 18)
    c.drawCentredString(cx, cy - 105, "For Adults Who Think Differently")

    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#ddddff"))
    features = [
        "Simple Daily Pages — No Overwhelm",
        "Brain Dump Spaces — Get It Out of Your Head",
        "Energy Level Tracker — Work WITH Your Brain",
        "Dopamine Menu — Healthy Reward System",
        "Weekly Review — Celebrate Small Wins",
    ]
    y = cy - 160
    for f in features:
        c.drawCentredString(cx, y, f)
        y -= 22

    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#aaaadd"))
    c.drawCentredString(cx, MARGIN + 30, "Designed for ADHD Brains · 150+ Pages · Undated")
    c.showPage()


def draw_how_it_works(c):
    y = H - MARGIN
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(PRIMARY)
    c.drawCentredString(W/2, y, "How This Planner Works")
    y -= 40

    sections = [
        ("Your ADHD Brain is Not Broken",
         "This planner is designed to work WITH how your brain actually functions — not against it. No complicated systems. No guilt. Just simple, flexible pages that help you get things done."),
        ("The Daily Page",
         "Each day has: 3 Must-Do tasks (not 20!), a time-blocking grid, energy level check, brain dump space, and a win tracker. Fill in what works. Skip what doesn't."),
        ("Brain Dump Pages",
         "When your brain is racing at 3am, grab this book. Dump everything out. Sort it later. The act of writing it down frees up mental RAM."),
        ("Weekly Review",
         "Every week, spend 10 minutes looking back. What worked? What didn't? No judgment. Just data. Adjust and keep going."),
        ("The Dopamine Menu",
         "A list of healthy rewards you actually enjoy. Finished your 3 tasks? Pick from YOUR menu. This replaces doom-scrolling with intentional joy."),
    ]

    c.setFont("Helvetica", 11)
    for title, body in sections:
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(MARGIN, y, title)
        y -= 18
        c.setFillColor(TEXT)
        c.setFont("Helvetica", 10)
        # Word wrap
        words = body.split()
        line = ""
        for word in words:
            test = line + " " + word if line else word
            if c.stringWidth(test, "Helvetica", 10) > W - 2*MARGIN - 20:
                c.drawString(MARGIN + 10, y, line)
                y -= 14
                line = word
            else:
                line = test
        if line:
            c.drawString(MARGIN + 10, y, line)
            y -= 20
        y -= 10

    c.showPage()


def draw_daily_page(c, day_num):
    """Core daily planner page — ADHD optimized."""
    y = H - MARGIN

    # Header
    c.setFillColor(LIGHT_BG)
    c.rect(MARGIN, H - MARGIN - 40, W - 2*MARGIN, 40, fill=1)
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN + 5, H - MARGIN - 20, f"Day {day_num}")
    c.setFont("Helvetica", 10)
    c.setFillColor(GRAY)
    c.drawString(MARGIN + 85, H - MARGIN - 20, "Date: _______________")
    c.drawRightString(W - MARGIN - 5, H - MARGIN - 20, "Day of Week: ________")

    y = H - MARGIN - 50

    # === Energy Check ===
    c.setFillColor(SECONDARY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Energy Level Right Now:")
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT)
    levels = ["Low", "Medium", "High", "HYPER"]
    ex = MARGIN + 175
    for lv in levels:
        c.circle(ex, y + 3, 5)
        c.drawString(ex + 8, y, lv)
        ex += 70
    y -= 25

    # === TOP 3 Must-Do (NOT 20!) ===
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "Today's TOP 3 (Only 3!)")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(MARGIN + 180, y + 1, "If you do these 3 things, today is a WIN.")
    y -= 20

    for i in range(3):
        checkbox(c, MARGIN, y, 14)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.setDash(1, 2)
        c.line(MARGIN + 20, y - 8, W - MARGIN, y - 8)
        c.setDash()
        y -= 28

    # === Time Blocks ===
    y -= 5
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Time Blocks")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(MARGIN + 90, y + 1, "(Don't plan every hour. Pick 3-4 blocks max.)")
    y -= 18

    times = ["Morning", "Late Morning", "Afternoon", "Evening"]
    block_h = 22
    for t in times:
        c.setFillColor(LIGHT_BG)
        c.rect(MARGIN, y - block_h + 5, W - 2*MARGIN, block_h, fill=1)
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 5, y - 8, t)
        c.setStrokeColor(LINE)
        c.setDash(1, 2)
        c.line(MARGIN + 90, y - 10, W - MARGIN - 5, y - 10)
        c.setDash()
        y -= block_h + 3

    # === Brain Dump ===
    y -= 8
    c.setFillColor(SECONDARY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Brain Dump")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(MARGIN + 85, y + 1, "(Random thoughts, ideas, worries — get them OUT)")
    y -= 15

    c.setStrokeColor(LINE)
    c.setLineWidth(0.3)
    for _ in range(6):
        c.line(MARGIN, y, W - MARGIN, y)
        y -= 18

    # === Daily Win ===
    y -= 5
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Today's Win")
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(MARGIN + 90, y + 1, "(Even tiny wins count. Write ONE.)")
    y -= 18
    c.setStrokeColor(LINE)
    c.setDash(1, 2)
    c.line(MARGIN, y, W - MARGIN, y)
    c.setDash()

    # === Mood Check ===
    y -= 25
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "End of Day Mood:")
    emojis = ["Rough", "Meh", "OK", "Good", "Great!"]
    ex = MARGIN + 120
    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT)
    for e in emojis:
        c.circle(ex, y + 3, 5)
        c.drawString(ex + 8, y, e)
        ex += 65

    c.showPage()


def draw_brain_dump_page(c, num):
    y = H - MARGIN
    c.setFillColor(SECONDARY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, y, f"Brain Dump #{num}")
    c.setFont("Helvetica", 10)
    c.setFillColor(GRAY)
    c.drawString(MARGIN, y - 18, "Date: ___________  |  Dump everything. Sort later.")
    y -= 45

    c.setStrokeColor(LINE)
    c.setLineWidth(0.3)
    while y > MARGIN + 10:
        c.line(MARGIN, y, W - MARGIN, y)
        y -= 22
    c.showPage()


def draw_weekly_review(c, week_num):
    y = H - MARGIN
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, y, f"Weekly Review — Week {week_num}")
    c.setFont("Helvetica", 10)
    c.setFillColor(GRAY)
    c.drawString(MARGIN, y - 18, "Spend 10 minutes. No judgment. Just data.")
    y -= 50

    questions = [
        ("What went well this week?", 4),
        ("What didn't go as planned?", 3),
        ("What drained my energy?", 3),
        ("What gave me energy?", 3),
        ("Next week I want to:", 3),
        ("One thing I'm proud of:", 2),
    ]

    for q, lines in questions:
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, q)
        y -= 18
        c.setStrokeColor(LINE)
        c.setLineWidth(0.3)
        for _ in range(lines):
            c.line(MARGIN + 10, y, W - MARGIN, y)
            y -= 18
        y -= 10

    c.showPage()


def draw_dopamine_menu(c):
    y = H - MARGIN
    c.setFillColor(SECONDARY)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W/2, y, "My Dopamine Menu")
    y -= 25
    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT)
    c.drawCentredString(W/2, y, "Healthy rewards for when you finish your tasks.")
    c.drawCentredString(W/2, y - 16, "Fill this in. Use it. Update it. No guilt.")
    y -= 55

    categories = [
        ("5-Minute Rewards", 5, ACCENT),
        ("15-Minute Rewards", 5, PRIMARY),
        ("30-Minute Rewards", 4, SECONDARY),
        ("Special Rewards (after a big win)", 3, HexColor("#e91e63")),
    ]

    for cat, count, color in categories:
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN, y, cat)
        y -= 20
        for i in range(count):
            c.setFillColor(TEXT)
            c.setFont("Helvetica", 10)
            c.drawString(MARGIN + 15, y, f"{i+1}.")
            c.setStrokeColor(LINE)
            c.setDash(1, 2)
            c.line(MARGIN + 30, y - 2, W/2 - 10, y - 2)
            c.setDash()
            y -= 20
        y -= 10

    c.showPage()


def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("ADHD Daily Planner for Adults")
    c.setAuthor("Deokgu Studio")

    # Title page
    draw_title_page(c)

    # How it works
    draw_how_it_works(c)

    # Dopamine Menu (put early so they fill it first)
    draw_dopamine_menu(c)

    # 90 daily pages (3 months worth)
    for day in range(1, 91):
        draw_daily_page(c, day)

        # Weekly review every 7 days
        if day % 7 == 0:
            draw_weekly_review(c, day // 7)

        # Brain dump every 5 days
        if day % 5 == 0:
            draw_brain_dump_page(c, day // 5)

    # Extra brain dump pages
    for i in range(5):
        draw_brain_dump_page(c, 19 + i)

    # Final page
    c.setFillColor(PRIMARY)
    c.rect(MARGIN+5, MARGIN+5, W - 2*MARGIN-10, H - 2*MARGIN-10, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W/2, H/2 + 40, "You Made It.")
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H/2, "Your ADHD brain is not a bug.")
    c.drawCentredString(W/2, H/2 - 25, "It's a feature.")
    c.setFont("Helvetica", 11)
    c.setFillColor(SECONDARY)
    c.drawCentredString(W/2, H/2 - 70, "If this planner helped you,")
    c.drawCentredString(W/2, H/2 - 90, "please leave a review on Amazon.")
    c.showPage()

    c.save()
    pages = c.getPageNumber() - 1
    size_kb = os.path.getsize(PDF_PATH) / 1024
    print(f"PDF generated: {PDF_PATH}")
    print(f"Total pages: {pages}")
    print(f"File size: {size_kb:.0f} KB")


if __name__ == "__main__":
    generate()
