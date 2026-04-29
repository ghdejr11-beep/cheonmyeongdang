"""Sobriety Journal - 90 Days to Clarity (6x9, ~120 pages)

A guided 90-day recovery journal for adults quitting alcohol or drugs.
Each day: cravings, triggers, gratitude, mood, support call, sleep, win.
Includes weekly check-ins, 30/60/90 day milestone reflections,
trigger reference, support contact directory, and emergency plan.
"""
import os
from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

# 6 x 9 inch trim (standard journal size, lower print cost on KDP)
PAGE = (6 * inch, 9 * inch)
W, H = PAGE
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sobriety_90_day_journal.pdf")

# Calm, hopeful palette - deep teal + warm sand
DARK = HexColor("#1F4E5F")        # deep teal
ACCENT = HexColor("#4A8B9D")      # mid teal
SOFT = HexColor("#E8F1F4")        # mist
SAND = HexColor("#F5EBD7")        # warm sand
MID_GRAY = HexColor("#CFCFCF")
LIGHT_GRAY = HexColor("#F4F4F4")
SUCCESS = HexColor("#4F7942")     # forest green

MARGIN = 0.5 * inch  # 6x9 has tight margins, but content stays inside
TOTAL_DAYS = 90


# ---------- helpers ----------
def footer(c, page_label=""):
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, MARGIN - 14, page_label or "Sobriety Journal | Deokgu Studio")


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


# ---------- pages ----------
def draw_title_page(c):
    # Full bleed background
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Sand band middle
    c.setFillColor(SAND)
    c.rect(0, H * 0.40, W, H * 0.20, fill=1, stroke=0)

    # Title
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W / 2, H * 0.52, "SOBRIETY")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.46, "JOURNAL")

    # Subtitle
    c.setFillColor(white)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W / 2, H * 0.34, "90 Days to Clarity")
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(W / 2, H * 0.30, "A Daily Recovery Companion")
    c.drawCentredString(W / 2, H * 0.27, "for Quitting Alcohol & Drugs")

    # Author
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, H * 0.10, "Deokgu Studio")
    c.showPage()


def draw_dedication_page(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 14)
    y = H - 1.2 * inch
    c.drawCentredString(W / 2, y, "This book belongs to")

    y -= 36
    hline(c, MARGIN + 30, W - MARGIN - 30, y)
    c.setFont("Helvetica", 8)
    c.setFillColor(MID_GRAY)
    c.drawCentredString(W / 2, y - 12, "Name")

    y -= 60
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2, y, "My Day One:")
    y -= 24
    hline(c, MARGIN + 60, W - MARGIN - 60, y)
    c.setFont("Helvetica", 8)
    c.setFillColor(MID_GRAY)
    c.drawCentredString(W / 2, y - 12, "Date I chose recovery")

    y -= 70
    c.setFillColor(SAND)
    c.rect(MARGIN, y - 100, W - 2 * MARGIN, 100, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 11)
    quote_lines = [
        '"You do not have to be',
        'good. You do not have to walk',
        'on your knees for a hundred miles',
        'through the desert, repenting.',
        'You only have to let the soft animal',
        'of your body love what it loves."',
    ]
    qy = y - 22
    for line in quote_lines:
        c.drawCentredString(W / 2, qy, line)
        qy -= 14
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, y - 112, "- Mary Oliver")

    # Promise / pledge below
    y -= 140
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, y, "My promise to myself")
    y -= 18
    y = field_lines(c, 4, y, MARGIN + 20, W - MARGIN - 20, leading=20)
    y -= 14
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Signed: ___________________________________")

    page_break(c)


def draw_why_page(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 1 * inch, "Why I'm Doing This")

    y = H - 1.5 * inch
    c.setFillColor(black)
    y = wrap_text(
        c,
        "Read this on hard days. Future-you wrote it for present-you.",
        MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=14,
    )
    y -= 20

    sections = [
        "I'm quitting because:",
        "What I've already lost:",
        "What I want back:",
        "Who I'm doing this for (besides me):",
        "How my life will look 90 days from today:",
    ]
    for s in sections:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, s)
        y -= 6
        y = field_lines(c, 4, y, MARGIN, W - MARGIN)
        y -= 14
    page_break(c)


def draw_how_to_use(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 1 * inch, "How to Use This Journal")

    y = H - 1.5 * inch
    c.setFillColor(black)
    paragraphs = [
        "Ninety days is not magic, but it is enough time for your brain chemistry to start resetting and for new habits to take root. Each day in this book takes 3-5 minutes.",
        "",
        "1. DAILY PAGE - Fill it in once a day, ideally morning or before bed. Even on bad days, especially on bad days. Skipping is not failure; coming back is the work.",
        "",
        "2. WEEKLY CHECK-IN - At the end of each 7-day stretch, look back. Spot triggers, count wins, plan the next week.",
        "",
        "3. MILESTONE PAGES - At Day 30, Day 60, and Day 90, you'll find a longer reflection. These are the receipts of your transformation.",
        "",
        "4. EMERGENCY PLAN - On a craving day, flip to the Emergency Plan in the back. Read it out loud. Then call someone on your support list.",
        "",
        "This is not medical advice. If you are physically dependent on alcohol or benzodiazepines, withdrawal can be life-threatening. Talk to a doctor or call SAMHSA's National Helpline 1-800-662-HELP (4357) before you stop.",
    ]
    for p in paragraphs:
        if p == "":
            y -= 8
            continue
        y = wrap_text(c, p, MARGIN, y, W - 2 * MARGIN, size=10, leading=14)
    page_break(c)


def draw_trigger_reference(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 1 * inch, "Common Triggers")

    y = H - 1.4 * inch
    c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(W / 2, y, "Use these labels in the 'Triggers today' field of your daily page.")
    y -= 22

    cats = [
        ("HALT", ["Hungry", "Angry", "Lonely", "Tired"]),
        ("People", ["Old drinking buddy", "Family conflict", "Toxic coworker", "Breakup"]),
        ("Places", ["Bar", "Restaurant", "Old neighborhood", "Liquor store"]),
        ("Times", ["Friday night", "After work", "Sunday afternoon", "Holidays"]),
        ("Emotions", ["Stress", "Boredom", "Shame", "Anxiety", "Grief", "Joy / celebration"]),
        ("Body", ["Insomnia", "Pain", "PMS", "Hangover memory"]),
        ("Money", ["Payday", "Bills", "Lottery loss", "Bonus"]),
    ]
    for cat, items in cats:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, cat)
        y -= 13
        c.setFillColor(black)
        c.setFont("Helvetica", 9)
        text = "  -  ".join(items)
        # wrap if too long
        if c.stringWidth(text, "Helvetica", 9) > W - 2 * MARGIN - 10:
            y = wrap_text(c, text, MARGIN + 8, y, W - 2 * MARGIN - 8, size=9, leading=12)
        else:
            c.drawString(MARGIN + 8, y, text)
            y -= 14
        y -= 6
    page_break(c)


def draw_support_directory(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 1 * inch, "My Support Team")

    y = H - 1.4 * inch
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Names and numbers I can call at 2am.")
    y -= 22

    c.setFillColor(SAND)
    c.rect(MARGIN, y - 100, W - 2 * MARGIN, 100, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN + 8, y - 14, "Crisis Lines (US)")
    c.setFont("Helvetica", 9)
    c.setFillColor(black)
    cy = y - 30
    crisis = [
        "SAMHSA National Helpline:    1-800-662-HELP (4357)  -  free, 24/7",
        "988 Suicide & Crisis Lifeline:  call or text 988",
        "Alcoholics Anonymous:         aa.org  -  meeting finder",
        "SMART Recovery:               smartrecovery.org",
        "In the Rooms (online mtgs):   intherooms.com",
    ]
    for line in crisis:
        c.drawString(MARGIN + 8, cy, line)
        cy -= 13
    y -= 110

    # personal contacts table
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "My People")
    y -= 14

    headers = ["Name", "Relationship", "Phone"]
    cw = [(W - 2 * MARGIN) * x for x in (0.40, 0.30, 0.30)]

    c.setFillColor(SOFT)
    c.rect(MARGIN, y - 14, W - 2 * MARGIN, 14, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    cx = MARGIN + 4
    for i, h in enumerate(headers):
        c.drawString(cx, y - 10, h)
        cx += cw[i]
    y -= 14

    c.setStrokeColor(MID_GRAY)
    rows = 10
    for _ in range(rows):
        c.line(MARGIN, y, W - MARGIN, y)
        cx = MARGIN
        for i in range(len(headers) + 1):
            c.line(cx, y, cx, y + 18)
            if i < len(headers):
                cx += cw[i]
        y -= 18
    page_break(c)


def draw_daily_page(c, day):
    week = (day - 1) // 7 + 1
    day_in_week = (day - 1) % 7 + 1

    # Header band
    top = H - MARGIN
    c.setFillColor(DARK)
    c.rect(MARGIN, top - 28, W - 2 * MARGIN, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 6, top - 18, f"Day {day}")
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN + 60, top - 18, f"Week {week}, Day {day_in_week}")
    c.drawRightString(W - MARGIN - 6, top - 18, "Date: ___ / ___ / _____")

    y = top - 44

    # Mood + Sleep + Cravings strip
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "Mood (1-5):")
    for n in range(1, 6):
        cx = MARGIN + 64 + (n - 1) * 14
        c.circle(cx, y + 3, 5, fill=0, stroke=1)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx, y + 1, str(n))
        c.setFont("Helvetica-Bold", 9)

    c.drawString(MARGIN + 150, y, "Sleep: ____ hrs")
    c.drawString(MARGIN + 240, y, "Craving (0-10): ____")
    y -= 22

    # Today's intention
    c.setFillColor(SAND)
    c.rect(MARGIN, y - 28, W - 2 * MARGIN, 28, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 6, y - 12, "Today's intention:")
    c.setStrokeColor(MID_GRAY)
    c.line(MARGIN + 100, y - 14, W - MARGIN - 6, y - 14)
    y -= 36

    # 3 gratitudes
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "3 things I'm grateful for")
    y -= 4
    c.setFont("Helvetica", 9)
    c.setFillColor(black)
    for i in range(1, 4):
        y -= 18
        c.drawString(MARGIN, y, f"{i}.")
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN + 14, y - 2, W - MARGIN, y - 2)
    y -= 14

    # Triggers today (3 lines)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Triggers / urges today")
    y -= 4
    y = field_lines(c, 3, y, MARGIN, W - MARGIN, leading=18)
    y -= 10

    # What I did instead (3 lines)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "What I did instead of using")
    y -= 4
    y = field_lines(c, 3, y, MARGIN, W - MARGIN, leading=18)
    y -= 10

    # Connection
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Reached out to:")
    c.setStrokeColor(MID_GRAY)
    c.line(MARGIN + 80, y - 2, MARGIN + 220, y - 2)
    c.drawString(MARGIN + 240, y, "Meeting?  Y / N")
    y -= 16

    # Self-compassion / one small win
    c.setFillColor(SUCCESS)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "One small win today")
    y -= 4
    y = field_lines(c, 2, y, MARGIN, W - MARGIN, leading=18)
    y -= 10

    # Evening reflection
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Evening reflection / Notes")
    y -= 4
    y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=18)

    # Streak banner at bottom
    c.setFillColor(SOFT)
    c.rect(MARGIN, MARGIN + 4, W - 2 * MARGIN, 22, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W / 2, MARGIN + 11, f"Day {day} of 90  -  {TOTAL_DAYS - day} to go")
    page_break(c, f"Day {day}")


def draw_weekly_review(c, week):
    top = H - MARGIN
    c.setFillColor(ACCENT)
    c.rect(MARGIN, top - 30, W - 2 * MARGIN, 30, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, top - 20, f"Week {week} Check-In")

    y = top - 50

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Wins this week:")
    y -= 4
    y = field_lines(c, 5, y, MARGIN, W - MARGIN, leading=20)
    y -= 14

    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Hard moments / closest call:")
    y -= 4
    y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=20)
    y -= 14

    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "What I learned about my triggers:")
    y -= 4
    y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=20)
    y -= 14

    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "One thing I'll change next week:")
    y -= 4
    y = field_lines(c, 3, y, MARGIN, W - MARGIN, leading=20)
    y -= 14

    # Mood / craving averages
    c.setFillColor(SAND)
    c.rect(MARGIN, y - 56, W - 2 * MARGIN, 56, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN + 6, y - 14, "This week's numbers:")
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN + 6, y - 30, "Avg mood:  ____ / 5")
    c.drawString(MARGIN + 130, y - 30, "Avg craving:  ____ / 10")
    c.drawString(MARGIN + 6, y - 46, "Days clean:  ____ / 7")
    c.drawString(MARGIN + 130, y - 46, "Meetings attended:  ____")

    page_break(c, f"Week {week} Review")


def draw_milestone(c, day_marker):
    top = H - MARGIN
    c.setFillColor(DARK)
    c.rect(MARGIN, top - 50, W - 2 * MARGIN, 50, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, top - 26, f"Day {day_marker}")
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, top - 42, "Milestone Reflection")

    y = top - 76
    c.setFillColor(DARK)

    prompts = [
        f"Look back at the last {day_marker} days. What is the biggest shift in how you feel?",
        "What were you most afraid would happen by now? Did it?",
        "Who has shown up for you that surprised you?",
        "What old belief about yourself is starting to crack?",
        "If you wrote a letter to Day 1 you, what would you say?",
        f"What do you need to keep going to Day {min(day_marker + 30, 90) if day_marker < 90 else 'beyond'}?",
    ]
    for p in prompts:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        y = wrap_text(c, p, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Bold", size=10, leading=13)
        y -= 4
        y = field_lines(c, 4, y, MARGIN, W - MARGIN)
        y -= 10

    page_break(c, f"Day {day_marker} Milestone")


def draw_emergency_plan(c):
    top = H - MARGIN
    c.setFillColor(HexColor("#8B0000"))  # deep red
    c.rect(MARGIN, top - 36, W - 2 * MARGIN, 36, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, top - 22, "EMERGENCY PLAN")

    y = top - 52
    c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 9)
    y = wrap_text(c, "Read this OUT LOUD when a craving feels too strong. Then do step 1.",
                  MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=14)
    y -= 12

    steps = [
        ("1.  WAIT 15 MINUTES.", "Cravings peak and pass. Set a timer. Do anything else for 15 minutes."),
        ("2.  CALL ONE PERSON.", "From your support list. Don't text - call. If no one answers, call SAMHSA: 1-800-662-4357."),
        ("3.  CHANGE YOUR LOCATION.", "Walk outside. Drive somewhere safe. Get into a public place. Geography matters."),
        ("4.  DO ONE PHYSICAL THING.", "Push-ups, cold shower, hard walk. Reset the nervous system."),
        ("5.  EAT AND DRINK WATER.", "Hungry + tired = high relapse risk. Eat a real meal."),
        ("6.  REREAD YOUR 'WHY' PAGE.", "Page 4 of this book. Future-you wrote it for this exact moment."),
        ("7.  WRITE IT DOWN.", "Use today's daily page. Naming the urge weakens it."),
    ]
    for title, body in steps:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, title)
        y -= 12
        c.setFillColor(black)
        y = wrap_text(c, body, MARGIN + 14, y, W - 2 * MARGIN - 14, size=9, leading=12)
        y -= 8

    y -= 4
    c.setFillColor(SAND)
    c.rect(MARGIN, y - 40, W - 2 * MARGIN, 40, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN + 6, y - 14, "If you slip:")
    c.setFont("Helvetica", 9)
    c.setFillColor(black)
    y2 = y - 26
    msg = "A slip is data, not a verdict. Open the book. Write what happened. Tomorrow becomes Day 1 again - and Day 1 is brave."
    wrap_text(c, msg, MARGIN + 6, y2, W - 2 * MARGIN - 12, size=9, leading=12)

    page_break(c, "Emergency Plan")


def draw_relapse_log(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, H - 1 * inch, "Slip Log (No Shame)")

    y = H - 1.4 * inch
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(black)
    y = wrap_text(c, "If a slip happens, write it here. Patterns become prevention.",
                  MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=9, leading=12)
    y -= 12

    headers = ["Date", "What happened", "Trigger", "Day count restart"]
    cw = [(W - 2 * MARGIN) * x for x in (0.18, 0.42, 0.22, 0.18)]

    c.setFillColor(SOFT)
    c.rect(MARGIN, y - 14, W - 2 * MARGIN, 14, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 8)
    cx = MARGIN + 3
    for i, h in enumerate(headers):
        c.drawString(cx, y - 10, h)
        cx += cw[i]
    y -= 14

    c.setStrokeColor(MID_GRAY)
    for _ in range(12):
        c.line(MARGIN, y, W - MARGIN, y)
        cx = MARGIN
        for i in range(len(headers) + 1):
            c.line(cx, y, cx, y + 24)
            if i < len(headers):
                cx += cw[i]
        y -= 24
    page_break(c, "Slip Log")


def draw_closing(c):
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setFillColor(SAND)
    c.rect(0, H * 0.45, W, H * 0.10, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.51, "DAY 91")

    c.setFillColor(white)
    c.setFont("Helvetica", 11)
    msg = [
        "You are not the same person",
        "who opened this book on Day 1.",
        "",
        "You proved the thing your fear",
        "told you couldn't be done.",
        "",
        "Recovery isn't a finish line.",
        "It's a direction.",
        "",
        "Keep going. One day at a time.",
    ]
    y = H * 0.40
    for line in msg:
        if line == "":
            y -= 8
            continue
        c.drawCentredString(W / 2, y, line)
        y -= 16

    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(W / 2, H * 0.10, "Deokgu Studio")
    c.showPage()


# ---------- main ----------
def main():
    c = canvas.Canvas(OUTPUT, pagesize=PAGE)
    c.setTitle("Sobriety Journal - 90 Days to Clarity")
    c.setAuthor("Deokgu Studio")
    c.setSubject("Recovery, Sobriety, Addiction")
    c.setKeywords("sobriety, recovery, alcohol, addiction, journal, 90 days")

    draw_title_page(c)
    draw_dedication_page(c)
    draw_why_page(c)
    draw_how_to_use(c)
    draw_trigger_reference(c)
    draw_support_directory(c)
    draw_emergency_plan(c)

    # 90 daily pages with weekly check-ins after every 7 days
    # plus milestone reflections at Day 30, 60, 90
    milestones = {30, 60, 90}
    for day in range(1, TOTAL_DAYS + 1):
        draw_daily_page(c, day)
        if day % 7 == 0:
            draw_weekly_review(c, day // 7)
        if day in milestones:
            draw_milestone(c, day)

    draw_relapse_log(c)
    draw_closing(c)
    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
