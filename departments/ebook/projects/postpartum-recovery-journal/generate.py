"""Postpartum Recovery Journal - 12 Weeks of Healing & Mom Self-Care (6x9, ~120 pages)

A guided 12-week postpartum journal for new mothers.
Each day: mood, sleep, hydration, baby feedings, diapers, physical recovery,
gratitude, self-care win.
Includes weekly reflections, postpartum warning signs reference,
provider contact directory, 6-week & 12-week milestone reflections.
"""
import os
from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

PAGE = (6 * inch, 9 * inch)
W, H = PAGE
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "postpartum_recovery_journal.pdf")

# Warm, gentle palette - dusty rose + sage + cream
DARK = HexColor("#7A4E5F")        # dusty rose plum
ACCENT = HexColor("#C48B9F")      # rose
SOFT = HexColor("#FBE9EC")        # blush
CREAM = HexColor("#F8F1E5")       # cream
SAGE = HexColor("#9CAF88")        # sage green
MID_GRAY = HexColor("#CFCFCF")
LIGHT_GRAY = HexColor("#F4F4F4")

MARGIN = 0.5 * inch
TOTAL_DAYS = 84   # 12 weeks


# ---------- helpers ----------
def footer(c, page_label=""):
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, MARGIN - 14, page_label or "Postpartum Recovery Journal | Deokgu Studio")


def page_break(c, label=""):
    footer(c, label)
    c.showPage()


def wrap_text(c, text, x, y, max_w, font="Helvetica", size=10, leading=14):
    c.setFont(font, size)
    words = text.split()
    line = ""
    for w_ in words:
        test = (line + " " + w_).strip()
        if c.stringWidth(test, font, size) > max_w:
            c.drawString(x, y, line)
            y -= leading
            line = w_
        else:
            line = test
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def hline(c, x1, x2, y, color=MID_GRAY):
    c.setStrokeColor(color)
    c.line(x1, y, x2, y)


def field_lines(c, n, top_y, left, right, leading=18, color=MID_GRAY):
    y = top_y
    for _ in range(n):
        y -= leading
        hline(c, left, right, y, color)
    return y


def section_header(c, text, y):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y, text)
    hline(c, MARGIN, W - MARGIN, y - 4, ACCENT)


def small_label(c, text, x, y, color=ACCENT):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x, y, text.upper())


def checkbox(c, x, y, size=8):
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(0.6)
    c.rect(x, y, size, size, fill=0, stroke=1)


# ---------- pages ----------
def draw_title_page(c):
    c.setFillColor(SOFT)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setFillColor(CREAM)
    c.rect(0, H * 0.40, W, H * 0.22, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W / 2, H * 0.55, "POSTPARTUM")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.49, "RECOVERY")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.43, "JOURNAL")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W / 2, H * 0.33, "12 Weeks of Healing & Mom Self-Care")
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(W / 2, H * 0.29, "A Daily Wellness Companion for New Mothers")

    c.setFillColor(SAGE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, H * 0.10, "DEOKGU STUDIO")

    c.showPage()


def draw_copyright_page(c):
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, H - MARGIN - 12, "Postpartum Recovery Journal")
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, H - MARGIN - 30, "12 Weeks of Healing & Mom Self-Care")

    c.setFont("Helvetica", 8)
    y = H - MARGIN - 60
    text = (
        "Copyright (c) 2026 Deokgu Studio. All rights reserved.",
        "",
        "This journal is intended for personal reflection, daily self-tracking,",
        "and self-care during the postpartum period. It is NOT a substitute for",
        "medical care. Always consult your obstetrician, midwife, pediatrician,",
        "or licensed mental health provider for medical concerns.",
        "",
        "If you experience thoughts of harming yourself or your baby, severe",
        "bleeding, fever, chest pain, or other warning signs listed in this",
        "journal, contact your provider or call 911 / 988 (Suicide & Crisis",
        "Lifeline) immediately.",
        "",
        "No part of this book may be reproduced or distributed without the",
        "prior written permission of the publisher.",
        "",
        "First edition: 2026",
        "Published by Deokgu Studio",
    )
    for line in text:
        c.drawString(MARGIN, y, line)
        y -= 12

    page_break(c, "")


def draw_intro_page(c):
    section_header(c, "Welcome, Mama", H - MARGIN - 14)
    y = H - MARGIN - 40
    paragraphs = [
        "The first 12 weeks after birth are sometimes called the fourth trimester. "
        "Your body is healing, your hormones are recalibrating, and you are getting "
        "to know a tiny new human while also getting to know yourself again.",
        "",
        "This journal is your daily companion for that season. Each page invites you "
        "to slow down for two minutes a day and notice three things: how YOU are "
        "feeling, how baby is doing, and one tiny win.",
        "",
        "There are no rules. Skip days. Write a single word. Use a sticker. The point "
        "is not a perfect journal - it is gentle, repeated attention to your own "
        "recovery.",
        "",
        "Inside you will find:",
    ]
    for p in paragraphs:
        if p == "":
            y -= 6
        else:
            y = wrap_text(c, p, MARGIN, y, W - 2 * MARGIN, size=10, leading=14)
            y -= 4

    bullets = [
        "84 daily check-in pages (12 full weeks)",
        "12 weekly reflections to spot patterns",
        "Postpartum warning signs - know when to call",
        "6-week and 12-week milestone reviews",
        "Provider contact directory",
        "Self-care prompt pages",
    ]
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    for b in bullets:
        c.drawString(MARGIN + 12, y, "- " + b)
        y -= 14

    y -= 8
    c.setFillColor(SAGE)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(MARGIN, y, "You are doing better than you think.")

    page_break(c, "")


def draw_how_to_use(c):
    section_header(c, "How to Use This Journal", H - MARGIN - 14)
    y = H - MARGIN - 40
    items = [
        ("1. Pick a daily anchor.", "Tie your check-in to a feed, nap, or coffee. Two minutes is enough."),
        ("2. Track baby and YOU.", "The left side covers feeds, sleep, diapers. The right side is just for you."),
        ("3. Skip without guilt.", "A blank page is data too. It often shows the hardest days."),
        ("4. Use the weekly review.", "Every 7 days, look back. Patterns reveal themselves quickly."),
        ("5. Bring it to appointments.", "Trends in mood, bleeding, and sleep help your provider help you."),
        ("6. Watch the warning signs.", "If anything on page 8 fits you, please call your provider TODAY."),
    ]
    for title, body in items:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, title)
        y -= 13
        c.setFillColor(black)
        y = wrap_text(c, body, MARGIN + 10, y, W - 2 * MARGIN - 10, size=9.5, leading=13)
        y -= 8

    page_break(c, "")


def draw_warning_signs(c):
    section_header(c, "Postpartum Warning Signs", H - MARGIN - 14)
    y = H - MARGIN - 36
    c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 9.5)
    y = wrap_text(c,
        "If you notice ANY of the following, contact your obstetrician, midwife, "
        "or call 911. These can be signs of postpartum hemorrhage, infection, "
        "preeclampsia, blood clots, or postpartum mood disorders.",
        MARGIN, y, W - 2 * MARGIN, size=9.5, leading=13)
    y -= 8

    sections = [
        ("Physical - call your provider today", [
            "Heavy bleeding (soaking a pad in under an hour)",
            "Passing a clot larger than a golf ball",
            "Fever above 100.4 F (38 C)",
            "Severe headache that does not improve with rest",
            "Vision changes, flashing lights, or blurriness",
            "Chest pain or shortness of breath",
            "Calf pain, redness, or swelling in one leg",
            "Incision (C-section or perineal) red, hot, oozing",
            "Severe pain in your belly",
        ]),
        ("Emotional - call your provider or 988", [
            "Thoughts of harming yourself or your baby",
            "Feeling disconnected from your baby for over 2 weeks",
            "Crying most of the day, every day, after week 2",
            "Severe anxiety or panic that prevents sleep",
            "Hearing or seeing things that are not there",
            "Feeling unable to care for yourself or baby",
        ]),
    ]
    for title, items in sections:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, title)
        y -= 14
        c.setFillColor(black)
        c.setFont("Helvetica", 9.5)
        for it in items:
            c.drawString(MARGIN + 10, y, "- " + it)
            y -= 12
        y -= 6

    c.setFillColor(SAGE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "988 = Suicide & Crisis Lifeline (US)  |  911 = Emergency")
    y -= 12
    c.setFont("Helvetica", 9)
    c.setFillColor(black)
    c.drawString(MARGIN, y, "Postpartum Support International: 1-800-944-4773 (call or text)")

    page_break(c, "")


def draw_provider_directory(c):
    section_header(c, "My Care Team", H - MARGIN - 14)
    y = H - MARGIN - 40
    c.setFillColor(black)
    c.setFont("Helvetica", 9.5)
    c.drawString(MARGIN, y, "Keep contacts handy for the sleepy 3 a.m. moments.")
    y -= 18

    roles = [
        "Obstetrician / Midwife",
        "Pediatrician",
        "Lactation consultant",
        "Mental health therapist",
        "Doula / Postpartum doula",
        "Pelvic floor physical therapist",
        "Pharmacy",
        "Insurance member services",
        "Emergency contact 1",
        "Emergency contact 2",
    ]
    for role in roles:
        small_label(c, role, MARGIN, y)
        y -= 12
        # name line
        hline(c, MARGIN, W - MARGIN, y - 2)
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica", 7)
        c.drawString(MARGIN, y - 11, "Name / Phone / Notes")
        c.setFillColor(black)
        y -= 26

    page_break(c, "")


def draw_baseline_page(c):
    section_header(c, "My Baseline (Week 0)", H - MARGIN - 14)
    y = H - MARGIN - 40
    c.setFillColor(black)
    c.setFont("Helvetica", 9.5)
    y = wrap_text(c,
        "Fill this out within the first 1-2 weeks. Comparing back to today helps "
        "you and your provider see real progress.",
        MARGIN, y, W - 2 * MARGIN, size=9.5, leading=13)
    y -= 10

    fields = [
        ("Birth date",), ("Birth type (vaginal / C-section / VBAC)",),
        ("Hospital / birth location",), ("Baby's name & weight",),
        ("My current weight",), ("Stitches or incision details",),
        ("Medications I am taking",), ("Mood today (1-10)",),
        ("Energy today (1-10)",), ("Pain level (1-10)",),
        ("Sleep last 24h (hours)",), ("Biggest worry right now",),
        ("Biggest hope for these 12 weeks",),
    ]
    for (label,) in fields:
        small_label(c, label, MARGIN, y)
        y -= 10
        hline(c, MARGIN, W - MARGIN, y - 2)
        y -= 18

    page_break(c, "")


def draw_day_page(c, day_num):
    week_num = (day_num - 1) // 7 + 1
    day_in_week = (day_num - 1) % 7 + 1
    days_label = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Top header band
    c.setFillColor(DARK)
    c.rect(0, H - 0.55 * inch, W, 0.55 * inch, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, H - 0.35 * inch, f"Day {day_num}")
    c.setFont("Helvetica", 9)
    c.drawRightString(W - MARGIN, H - 0.35 * inch, f"Week {week_num}  |  Date: ____ / ____ / ____")

    y = H - 0.55 * inch - 14

    # Mood + sleep + pain row
    col_w = (W - 2 * MARGIN) / 3
    small_label(c, "Mood (1-10)", MARGIN, y)
    small_label(c, "Sleep last 24h", MARGIN + col_w, y)
    small_label(c, "Pain (1-10)", MARGIN + 2 * col_w, y)
    y -= 18
    for i in range(3):
        c.setStrokeColor(MID_GRAY)
        c.rect(MARGIN + i * col_w, y - 4, col_w - 12, 22, fill=0, stroke=1)
    y -= 18

    # Hydration & meals & meds
    small_label(c, "Hydration", MARGIN, y)
    for i in range(8):
        c.circle(MARGIN + 50 + i * 15, y + 3, 4, stroke=1, fill=0)
    small_label(c, "Meals", MARGIN + 0.45 * (W - 2 * MARGIN) + 50, y)
    for i in range(3):
        checkbox(c, MARGIN + 0.45 * (W - 2 * MARGIN) + 80 + i * 18, y - 1)
    y -= 22

    # Meds taken
    small_label(c, "Meds taken (yes/no/notes)", MARGIN, y)
    y -= 10
    hline(c, MARGIN, W - MARGIN, y - 2)
    y -= 16

    # ---- Baby section ----
    c.setFillColor(SOFT)
    c.rect(MARGIN - 2, y - 100, (W - 2 * MARGIN), 96, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(MARGIN + 4, y - 12, "BABY")
    c.setFillColor(black)
    c.setFont("Helvetica", 8)

    # Feed times line
    small_label(c, "Feeds (times / sides / oz)", MARGIN + 4, y - 26, color=DARK)
    hline(c, MARGIN + 4, W - MARGIN - 4, y - 38, MID_GRAY)
    hline(c, MARGIN + 4, W - MARGIN - 4, y - 56, MID_GRAY)

    small_label(c, "Diapers - wet", MARGIN + 4, y - 70, color=DARK)
    for i in range(8):
        c.circle(MARGIN + 70 + i * 12, y - 67, 3.5, stroke=1, fill=0)
    small_label(c, "Dirty", MARGIN + 4 + 180, y - 70, color=DARK)
    for i in range(5):
        c.circle(MARGIN + 4 + 180 + 28 + i * 12, y - 67, 3.5, stroke=1, fill=0)

    small_label(c, "Sleep blocks (longest run)", MARGIN + 4, y - 86, color=DARK)
    hline(c, MARGIN + 4 + 130, W - MARGIN - 4, y - 88, MID_GRAY)

    y -= 110

    # Recovery checklist
    section_y = y
    small_label(c, "MY RECOVERY TODAY", MARGIN, section_y, color=DARK)
    y -= 14
    items = [
        "Took a real shower",
        "Stepped outside for fresh air",
        "Ate 3 meals",
        "Drank water with every feed",
        "Took meds / vitamins",
        "Pelvic floor or breathing exercise",
        "Asked for help with one thing",
    ]
    col2_x = MARGIN + (W - 2 * MARGIN) / 2
    for i, it in enumerate(items):
        col_x = MARGIN if i < 4 else col2_x
        row = i if i < 4 else i - 4
        cy = y - row * 13
        checkbox(c, col_x, cy - 6, size=7)
        c.setFillColor(black)
        c.setFont("Helvetica", 8.5)
        c.drawString(col_x + 11, cy - 4, it)
    y -= 13 * 4 + 6

    # Reflection block
    small_label(c, "ONE WIN TODAY", MARGIN, y, color=DARK)
    y -= 12
    hline(c, MARGIN, W - MARGIN, y - 2)
    y -= 18

    small_label(c, "ONE WORRY OR FEELING", MARGIN, y, color=DARK)
    y -= 12
    hline(c, MARGIN, W - MARGIN, y - 2)
    hline(c, MARGIN, W - MARGIN, y - 18)
    y -= 30

    small_label(c, "GRATEFUL FOR", MARGIN, y, color=DARK)
    y -= 12
    hline(c, MARGIN, W - MARGIN, y - 2)
    y -= 14

    page_break(c, f"Day {day_num} of {TOTAL_DAYS}  |  Week {week_num}")


def draw_weekly_review(c, week_num):
    section_header(c, f"Week {week_num} Reflection", H - MARGIN - 14)
    y = H - MARGIN - 40
    c.setFillColor(black)
    c.setFont("Helvetica", 9.5)
    c.drawString(MARGIN, y, f"Date range: ____ / ____  to  ____ / ____")
    y -= 22

    prompts = [
        "Hardest moment this week",
        "Sweetest moment this week",
        "Something my body did that surprised me",
        "Something baby did for the first time",
        "Did I sleep more or less than last week?",
        "Did I cry? When and why?",
        "Did I ask for help? From whom?",
        "What does my body need next week?",
        "What does my heart need next week?",
        "One promise to myself for next week",
    ]
    for p in prompts:
        small_label(c, p, MARGIN, y)
        y -= 10
        hline(c, MARGIN, W - MARGIN, y - 2)
        hline(c, MARGIN, W - MARGIN, y - 18)
        y -= 28

    page_break(c, f"Week {week_num} Reflection")


def draw_milestone_page(c, week_label, milestone_text):
    c.setFillColor(SOFT)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W / 2, H * 0.78, week_label)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(W / 2, H * 0.72, milestone_text)

    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    y = H * 0.62
    prompts = [
        "How is my body different from week 0?",
        "How is my mood different from week 0?",
        "What surprised me most in this stretch?",
        "What am I proud of?",
        "What needs to change for the weeks ahead?",
        "Who has shown up for me? How can I thank them?",
        "What conversation do I need to have with my provider?",
    ]
    for p in prompts:
        small_label(c, p, MARGIN, y, color=DARK)
        y -= 11
        hline(c, MARGIN, W - MARGIN, y - 2)
        hline(c, MARGIN, W - MARGIN, y - 18)
        y -= 30

    page_break(c, week_label)


def draw_self_care_menu(c):
    section_header(c, "5-Minute Self-Care Menu", H - MARGIN - 14)
    y = H - MARGIN - 40
    c.setFillColor(black)
    c.setFont("Helvetica", 9.5)
    y = wrap_text(c,
        "When the day feels long and you are touched out, pick ONE. None of these "
        "require leaving your baby or the couch.",
        MARGIN, y, W - 2 * MARGIN, size=9.5, leading=13)
    y -= 8

    items = [
        "Splash cold water on your face",
        "Drink a tall glass of water with ice",
        "Step outside for 5 deep breaths",
        "Text one friend the truth about today",
        "Change into a clean shirt",
        "Eat a piece of fruit",
        "Stretch your shoulders and neck",
        "Brush your teeth or rinse with mouthwash",
        "Put on lotion that smells nice",
        "Open a window for fresh air",
        "Listen to one favorite song",
        "Cry it out for 3 minutes, set a timer",
        "Walk to the mailbox and back",
        "Hold a warm mug, no agenda",
        "Look at one photo that makes you smile",
        "Say one kind thing to yourself out loud",
    ]
    c.setFillColor(black)
    c.setFont("Helvetica", 9.5)
    col_x = [MARGIN, MARGIN + (W - 2 * MARGIN) / 2 + 6]
    half = (len(items) + 1) // 2
    for i, it in enumerate(items):
        cx = col_x[0] if i < half else col_x[1]
        cy = y - (i if i < half else i - half) * 16
        checkbox(c, cx, cy - 6, size=7)
        c.drawString(cx + 11, cy - 4, it)

    page_break(c, "Self-Care Menu")


def draw_partner_page(c):
    section_header(c, "For My Partner / Support Person", H - MARGIN - 14)
    y = H - MARGIN - 40
    c.setFillColor(black)
    c.setFont("Helvetica", 9.5)
    y = wrap_text(c,
        "If you are reading this, the new mom in your life trusts you. Here is what "
        "actually helps in the postpartum window.",
        MARGIN, y, W - 2 * MARGIN, size=9.5, leading=13)
    y -= 8

    items = [
        ("Watch for warning signs.", "Re-read the warning signs page weekly. Trust changes you see."),
        ("Take a feed or bottle once a day.", "Even one feed gives mom a 2-3 hour sleep block. That is medicine."),
        ("Bring water and snacks every 2 hours.", "Especially while breastfeeding. Do not ask, just bring."),
        ("Handle one full daily task.", "Dishes, laundry, or cooking. Pick one and own it for 12 weeks."),
        ("Field visitors.", "Limit guests, run interference, protect rest."),
        ("Listen without fixing.", "Ask: do you want comfort, advice, or quiet? Then deliver that."),
        ("Notice mood patterns.", "Two weeks of crying, withdrawal, or rage = call her provider with her."),
    ]
    for title, body in items:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, title)
        y -= 13
        c.setFillColor(black)
        y = wrap_text(c, body, MARGIN + 10, y, W - 2 * MARGIN - 10, size=9.5, leading=13)
        y -= 4

    page_break(c, "For My Partner")


def draw_closing(c):
    c.setFillColor(SOFT)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.70, "12 Weeks Done")
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(W / 2, H * 0.64, "You showed up, even when it was hard.")

    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    y = H * 0.54
    prompts = [
        "What am I most proud of?",
        "What do I want my baby to know about these 12 weeks?",
        "What do I want to remember next time the world feels heavy?",
        "Who do I owe a thank-you note?",
        "What is my next chapter, beyond recovery?",
    ]
    for p in prompts:
        small_label(c, p, MARGIN, y, color=DARK)
        y -= 11
        hline(c, MARGIN, W - MARGIN, y - 2)
        hline(c, MARGIN, W - MARGIN, y - 18)
        hline(c, MARGIN, W - MARGIN, y - 34)
        y -= 46

    page_break(c, "Closing Reflection")


# ---------- main ----------
def build():
    c = canvas.Canvas(OUTPUT, pagesize=PAGE)
    c.setTitle("Postpartum Recovery Journal")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_copyright_page(c)
    draw_intro_page(c)
    draw_how_to_use(c)
    draw_warning_signs(c)
    draw_provider_directory(c)
    draw_baseline_page(c)
    draw_self_care_menu(c)

    # 12 weeks: 7 daily pages + weekly reflection
    for week in range(1, 13):
        for d in range(1, 8):
            day_num = (week - 1) * 7 + d
            draw_day_page(c, day_num)
        draw_weekly_review(c, week)
        # Milestones at end of week 6 and week 12
        if week == 6:
            draw_milestone_page(c, "6-Week Milestone", "Halfway through the fourth trimester")
        elif week == 12:
            draw_milestone_page(c, "12-Week Milestone", "End of the fourth trimester")

    draw_partner_page(c)
    draw_closing(c)

    c.save()
    return OUTPUT


if __name__ == "__main__":
    out = build()
    size = os.path.getsize(out) / 1024
    print(f"PDF saved: {out}")
    print(f"Size: {size:.1f} KB")
