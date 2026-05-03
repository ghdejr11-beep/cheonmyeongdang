"""Grief Journal for Loss of a Parent (6x9, ~96 pages).

A guided grief journal for adults mourning the death of a mother or
father. Walks the reader from the raw first week, through 60 daily
check-ins, into long-arc milestones at 1/3/6/12 months. Designed for
both immediate-grief readers and sympathy-gift buyers.
"""
import os
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

PAGE = (6 * inch, 9 * inch)
W, H = PAGE
OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "grief_journal_loss_of_parent.pdf",
)

DARK = HexColor("#2F3E54")        # deep slate blue
ACCENT = HexColor("#7E96B0")      # soft blue-grey
SOFT = HexColor("#E6ECF1")        # mist
WARM = HexColor("#C8A989")        # muted warm beige
CREAM = HexColor("#F6F1E8")
MID_GRAY = HexColor("#CFCFCF")
LIGHT_GRAY = HexColor("#F4F4F4")
GOLD = HexColor("#B98E4D")

MARGIN = 0.75 * inch  # KDP-safe for 24-150 pages on 6x9


def footer(c, page_label=""):
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(
        W / 2,
        MARGIN - 18,
        page_label or "Grief Journal | Loss of a Parent",
    )


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


def section_title(c, text):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 1.0 * inch, text)
    c.setStrokeColor(WARM)
    c.setLineWidth(1.2)
    c.line(W / 2 - 30, H - 1.12 * inch, W / 2 + 30, H - 1.12 * inch)
    c.setLineWidth(1.0)
    return H - 1.5 * inch


# ---------- pages ----------
def draw_title_page(c):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.rect(0, H * 0.42, W, H * 0.20, fill=1, stroke=0)

    c.setFillColor(CREAM)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W / 2, H * 0.55, "GRIEF JOURNAL")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.50, "for the")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.445, "LOSS OF A PARENT")

    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, H * 0.36, "A Guided Companion for the First Year")
    c.drawCentredString(W / 2, H * 0.335, "After Losing Your Mother or Father")

    # decorative dot ring
    cx, cy = W / 2, H * 0.20
    c.setFillColor(WARM)
    for i in range(8):
        import math
        a = i * (3.14159 / 4)
        c.circle(cx + 16 * math.cos(a), cy + 16 * math.sin(a), 2, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.circle(cx, cy, 4, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, H * 0.08, "Deokgu Studio")
    c.showPage()


def draw_copyright_page(c):
    y = H * 0.6
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 9)
    lines = [
        "Grief Journal for the Loss of a Parent",
        "Copyright (c) 2026 Deokgu Studio. All rights reserved.",
        "",
        "This journal is a tool for personal reflection and is not a",
        "substitute for professional grief counseling or medical care.",
        "If you are in crisis, please reach out to the resources listed",
        "at the back of this book.",
        "",
        "First Edition. Printed by Amazon KDP.",
    ]
    for line in lines:
        c.drawCentredString(W / 2, y, line)
        y -= 14
    page_break(c)


def draw_dedication_page(c):
    y = H - 1.5 * inch
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, y, "In loving memory of")

    y -= 50
    hline(c, MARGIN + 30, W - MARGIN - 30, y)
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, y - 12, "Their name")

    y -= 60
    c.setFillColor(DARK)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, y, "________  -  ________")
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, y - 12, "Birth - Passing")

    y -= 80
    c.setFillColor(CREAM)
    c.rect(MARGIN, y - 110, W - 2 * MARGIN, 110, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 11)
    quote_lines = [
        '"What we have once enjoyed deeply',
        'we can never lose. All that we love',
        'deeply becomes a part of us."',
    ]
    qy = y - 28
    for line in quote_lines:
        c.drawCentredString(W / 2, qy, line)
        qy -= 16
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, y - 92, "- Helen Keller")

    page_break(c)


def draw_how_to_use_page(c):
    y = section_title(c, "How to Use This Journal")
    c.setFillColor(DARK)
    intro = (
        "There is no right way to grieve, and there is no right way to use "
        "this book. You can read it cover to cover, or open it on a hard "
        "night and write one line. You can skip pages and come back. You "
        "can leave whole sections blank. The book is yours."
    )
    y = wrap_text(c, intro, MARGIN, y, W - 2 * MARGIN, size=10, leading=14)

    y -= 14
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "WHAT'S INSIDE")
    y -= 18

    items = [
        ("Their Story", "Memorial pages to capture who they were before the world starts to forget."),
        ("First Week", "Seven longer entries for the rawest days, when ordinary time has stopped."),
        ("60 Daily Check-Ins", "A short five-minute rhythm for the hardest two months."),
        ("Weekly Reflections", "Every ten days - a chance to see the small movement you cannot feel."),
        ("Milestones", "One month, three months, six months, one year - the long arc."),
        ("Letter Pages", "Direct space to write to them. As often as you need."),
        ("Memorial Lists", "Protect the details from time."),
        ("Stages of Grief", "A short, compassionate guide so you know nothing you feel is wrong."),
        ("Resources", "Crisis lines, books, and groups - kept short and trustworthy."),
    ]
    for title_, body_ in items:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(DARK)
        c.drawString(MARGIN, y, title_)
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#555555"))
        y = wrap_text(c, body_, MARGIN + 80, y, W - 2 * MARGIN - 80, size=9, leading=12)
        y -= 4

    page_break(c)


def draw_about_my_parent(c):
    y = section_title(c, "About My Mother / Father")

    fields = [
        ("Their full name:", 1),
        ("What I called them:", 1),
        ("Born / passed:", 1),
        ("Where they were born and where they lived:", 2),
        ("Their work, their craft, what they were known for:", 2),
        ("Their voice - how it sounded, what they said often:", 2),
        ("Their hands - what I remember about them:", 2),
        ("Their laugh:", 1),
        ("The thing they always said when I was a child:", 2),
    ]
    for label, lines in fields:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(MARGIN, y, label)
        y -= 6
        y = field_lines(c, lines, y, MARGIN, W - MARGIN, leading=18)
        y -= 12
    page_break(c)


def draw_who_they_were(c):
    y = section_title(c, "Who They Were")

    fields = [
        ("What they loved:", 3),
        ("What annoyed them, what made them laugh:", 3),
        ("Their faith, beliefs, or what gave them peace:", 2),
        ("The hardest thing they ever lived through:", 3),
        ("Their proudest moment (that they told me about):", 2),
        ("Their proudest moment (that they didn't):", 2),
    ]
    for label, lines in fields:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(MARGIN, y, label)
        y -= 6
        y = field_lines(c, lines, y, MARGIN, W - MARGIN, leading=18)
        y -= 10
    page_break(c)


def draw_photo_page(c, title_, prompt_):
    y = section_title(c, title_)
    box_h = 4.0 * inch
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(0.7)
    c.rect(MARGIN, y - box_h, W - 2 * MARGIN, box_h, fill=0, stroke=1)
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(W / 2, y - box_h / 2, "[ photo placeholder - tape or paste here ]")

    y2 = y - box_h - 28
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(MARGIN, y2, prompt_)
    y2 -= 6
    field_lines(c, 6, y2, MARGIN, W - MARGIN, leading=18)
    page_break(c)


def draw_first_week_entry(c, day_label, prompt_text):
    y = section_title(c, day_label)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 10)
    y = wrap_text(c, prompt_text, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=13)
    y -= 10

    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "Today, in three words:")
    y -= 6
    y = field_lines(c, 1, y, MARGIN, W - MARGIN, leading=18)

    y -= 10
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "What I am carrying:")
    y -= 6
    y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=18)

    y -= 8
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "One memory that visited me:")
    y -= 6
    y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=18)

    y -= 8
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "One small thing I will do tonight:")
    y -= 6
    field_lines(c, 2, y, MARGIN, W - MARGIN, leading=18)
    page_break(c)


def draw_daily_checkin_pair(c, day_a, day_b):
    """Two daily check-ins on one page (two per page = compact)."""
    section_title(c, "Daily Check-In")

    def block(top_y, day_n):
        y = top_y
        c.setFillColor(WARM)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, f"Day {day_n}")
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN + 60, y, "date: ____ / ____ / ____")
        y -= 14

        c.setFillColor(DARK)
        c.setFont("Helvetica", 8.5)
        c.drawString(MARGIN, y, "Heaviness today (1 light - 10 crushing):")
        for i in range(1, 11):
            cx = MARGIN + 220 + (i - 1) * 14
            c.circle(cx, y + 3, 4, fill=0, stroke=1)
            c.setFont("Helvetica", 6.5)
            c.drawCentredString(cx, y - 8, str(i))
            c.setFont("Helvetica", 8.5)
        y -= 20

        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(MARGIN, y, "One word for today:")
        y -= 4
        y = field_lines(c, 1, y, MARGIN, W - MARGIN, leading=14)

        y -= 6
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(MARGIN, y, "I missed them most when...")
        y -= 4
        y = field_lines(c, 2, y, MARGIN, W - MARGIN, leading=14)

        y -= 6
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(MARGIN, y, "Something that helped (or did not):")
        y -= 4
        y = field_lines(c, 2, y, MARGIN, W - MARGIN, leading=14)

        y -= 6
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(MARGIN, y, "One small thing for tomorrow:")
        y -= 4
        y = field_lines(c, 1, y, MARGIN, W - MARGIN, leading=14)
        return y

    bottom_after_a = block(H - 1.6 * inch, day_a)

    # divider
    c.setStrokeColor(SOFT)
    c.setLineWidth(0.6)
    c.line(MARGIN, bottom_after_a - 14, W - MARGIN, bottom_after_a - 14)
    c.setLineWidth(1.0)

    block(bottom_after_a - 30, day_b)
    page_break(c)


def draw_weekly_reflection(c, week_n):
    y = section_title(c, f"Weekly Reflection - Week {week_n}")
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 10)
    intro = (
        "Read the past seven days slowly. Notice. Without judgement, write "
        "what is moving and what is still. Healing is not linear - and you "
        "may not feel it - but it is here on these pages."
    )
    y = wrap_text(c, intro, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=13)
    y -= 12

    prompts = [
        ("What was the hardest moment of this week?", 4),
        ("What was a smaller, softer moment - even one?", 4),
        ("Where did I notice their absence most?", 3),
        ("Where did I notice their presence?", 3),
        ("What does my body need next week?", 3),
    ]
    for label, lines in prompts:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(DARK)
        c.drawString(MARGIN, y, label)
        y -= 6
        y = field_lines(c, lines, y, MARGIN, W - MARGIN, leading=16)
        y -= 8
    page_break(c)


def draw_milestone(c, title_, intro_text, prompts):
    y = section_title(c, title_)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 10)
    y = wrap_text(c, intro_text, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=13)
    y -= 12
    for label, lines in prompts:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(DARK)
        c.drawString(MARGIN, y, label)
        y -= 6
        y = field_lines(c, lines, y, MARGIN, W - MARGIN, leading=16)
        y -= 6
    page_break(c)


def draw_letter_page(c, n_total, n_idx):
    y = section_title(c, f"Letter to You ({n_idx} of {n_total})")
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(MARGIN, y, "Date: ____ / ____ / ____")
    y -= 22
    c.setFillColor(DARK)
    c.setFont("Helvetica", 11)
    c.drawString(MARGIN, y, "Dear ____________________,")
    y -= 24
    field_lines(c, 22, y, MARGIN, W - MARGIN, leading=18)
    page_break(c)


def draw_memorial_list(c, title_, prompt_, n_lines=10):
    y = section_title(c, title_)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 10)
    y = wrap_text(c, prompt_, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=13)
    y -= 14
    for i in range(1, n_lines + 1):
        c.setFillColor(WARM)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, f"{i:>2}.")
        c.setFillColor(DARK)
        hline(c, MARGIN + 24, W - MARGIN, y - 2)
        y -= 22
    page_break(c)


def draw_stages_of_grief(c):
    y = section_title(c, "The Stages of Grief")
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 10)
    intro = (
        "These stages are not steps. They are not in order. You may sit in "
        "one for months and visit another for an hour. Nothing you feel is "
        "wrong, and nothing means you are stuck. Grief is the cost of love - "
        "and it is paid slowly, in many small currencies."
    )
    y = wrap_text(c, intro, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=13)
    y -= 14

    stages = [
        ("Denial", "Walking into the room expecting to see them. Reaching for the phone. The mind protects the heart with a small lag in time."),
        ("Anger", "At them, at the doctors, at God, at yourself. Anger is grief asking why - it is love that has nowhere to put itself."),
        ("Bargaining", "If only I had called sooner. If only we had caught it. The mind reviews the tape, looking for an exit that was never there."),
        ("Sadness", "The honest weight of the loss settling in. The empty chair. The first holiday. The phone calls you no longer make."),
        ("Acceptance", "Not 'okay' and never 'over.' A new shape. Carrying them with you, instead of carrying their absence."),
        ("Meaning", "(David Kessler's sixth stage) - what their life keeps giving you, what you do with it, who you become because they lived."),
    ]
    for name, body in stages:
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(WARM)
        c.drawString(MARGIN, y, name)
        c.setFillColor(DARK)
        y -= 14
        y = wrap_text(c, body, MARGIN, y, W - 2 * MARGIN, size=9.5, leading=13)
        y -= 6
    page_break(c)


def draw_resources_page(c):
    y = section_title(c, "Support Resources")
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 10)
    intro = (
        "If you are in crisis, please reach out. Grief is not weakness, and "
        "asking for help is not failure. The phone numbers below are free "
        "and confidential."
    )
    y = wrap_text(c, intro, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=13)
    y -= 14

    items = [
        ("988 Suicide & Crisis Lifeline (US)", "Call or text 988. 24/7 free and confidential support."),
        ("SAMHSA National Helpline", "1-800-662-4357. Free 24/7 treatment referral and information."),
        ("GriefShare", "griefshare.org - in-person and online groups for grieving adults."),
        ("Modern Loss", "modernloss.com - candid grief writing, especially for parental loss."),
        ("The Dinner Party", "thedinnerparty.org - peer groups for adults who have lost someone."),
        ("What's Your Grief", "whatsyourgrief.com - articles and resources from grief educators."),
    ]
    for name, body in items:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(WARM)
        c.drawString(MARGIN, y, name)
        c.setFillColor(DARK)
        y -= 13
        y = wrap_text(c, body, MARGIN + 12, y, W - 2 * MARGIN - 12, size=9.5, leading=13)
        y -= 8

    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Books that have helped many readers")
    y -= 14
    books = [
        '"It\'s OK That You\'re Not OK" - Megan Devine',
        '"The Year of Magical Thinking" - Joan Didion',
        '"H is for Hawk" - Helen Macdonald',
        '"Finding Meaning: The Sixth Stage of Grief" - David Kessler',
        '"Motherless Daughters" - Hope Edelman',
    ]
    c.setFont("Helvetica", 9.5)
    for b in books:
        c.drawString(MARGIN + 12, y, "- " + b)
        y -= 14
    page_break(c)


def draw_closing_page(c):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, H * 0.65, "You carried them here.")
    c.setFont("Helvetica", 11)
    lines = [
        "You will carry them forward.",
        "",
        "Whatever shape your grief takes",
        "in the year ahead -",
        "you are not failing,",
        "you are not behind,",
        "and you are not alone.",
    ]
    y = H * 0.55
    for line in lines:
        c.drawCentredString(W / 2, y, line)
        y -= 16
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(WARM)
    c.drawCentredString(W / 2, H * 0.20, "- Deokgu Studio")
    c.showPage()


# ---------- main ----------
def build():
    c = canvas.Canvas(OUTPUT, pagesize=PAGE)
    c.setTitle("Grief Journal for the Loss of a Parent")
    c.setAuthor("Deokgu Studio")

    # Front matter
    draw_title_page(c)
    draw_copyright_page(c)
    draw_dedication_page(c)
    draw_how_to_use_page(c)

    # THEIR STORY
    draw_about_my_parent(c)
    draw_who_they_were(c)
    draw_photo_page(c, "A Photo of Them", "When I look at this photo, I remember:")
    draw_photo_page(c, "Us, Together", "What was happening the day this was taken:")

    # FIRST WEEK
    first_week = [
        ("Day One - The First Day Without Them",
         "Write what you can. Even if it is one sentence. Even if it is the time of day. The page is patient."),
        ("Day Two - The People Who Showed Up",
         "Who has been there. Who hasn't. The names, the gestures, the silences. There are no wrong feelings to record."),
        ("Day Three - Their Empty Place",
         "The chair, the room, the routine that has stopped. Describe it. Naming the silence is its own form of love."),
        ("Day Four - The Story of Their Last Day",
         "If you are ready. If you are not, fold this page and come back. Telling the story slowly is part of survival."),
        ("Day Five - How My Body Is Taking It",
         "Sleep. Appetite. The physical weight of grief. Write it without trying to fix it. The body is grieving too."),
        ("Day Six - Their Voice in My Head",
         "What you would tell them today. What you imagine they would say back. Both halves of the conversation are real."),
        ("Day Seven - Closing the First Week",
         "What you survived this week. What surprised you. What you are bringing into the next seven days."),
    ]
    for title_, prompt_ in first_week:
        draw_first_week_entry(c, title_, prompt_)

    # 60 DAILY CHECK-INS (2 per page = 30 pages)
    for d in range(1, 61, 2):
        draw_daily_checkin_pair(c, d, d + 1)

    # WEEKLY REFLECTIONS (every ~10 days, but easier as 6 quick checks across the 60-day arc)
    for w in range(1, 7):
        draw_weekly_reflection(c, w)

    # MILESTONES
    draw_milestone(
        c,
        "One Month",
        "It has been a month. The first wave of attention from others has passed and "
        "the world has gone back to noise. This page is just for you.",
        [
            ("What is the hardest part right now?", 4),
            ("What is one thing I have surprised myself by doing?", 3),
            ("What would they say to me today?", 4),
            ("What I want to write to them:", 5),
        ],
    )
    draw_milestone(
        c,
        "Three Months",
        "Three months in. The body remembers anniversaries even when the mind forgets. "
        "Notice what has shifted - in tiny millimeters.",
        [
            ("What can I do today that I could not do in the first week?", 4),
            ("Where am I still stuck?", 4),
            ("What does my grief look like now (compared to month one)?", 4),
            ("Letter to them:", 4),
        ],
    )
    draw_milestone(
        c,
        "Six Months",
        "Six months. The 'firsts' are stacking up - first birthday without them, first "
        "holiday, first big news they did not get to hear. Mark them here.",
        [
            ("The 'firsts' I have carried so far:", 5),
            ("What I have learned about myself:", 4),
            ("Who I am becoming because they lived:", 4),
            ("Letter to them:", 3),
        ],
    )
    draw_milestone(
        c,
        "One Year",
        "A whole year. Not 'over' - never that - but a full circle of seasons carried. "
        "Write to the version of yourself who opened this book on Day One.",
        [
            ("What I want my Day One self to know:", 5),
            ("What I am keeping of them, forever:", 5),
            ("How I will honor them in the year to come:", 4),
            ("Letter to them - one year on:", 4),
        ],
    )

    # LETTER PAGES
    for i in range(1, 6):
        draw_letter_page(c, 5, i)

    # MEMORIAL LISTS
    draw_memorial_list(
        c,
        "Ten Things They Taught Me",
        "Lessons - spoken and unspoken. The ones I carry without thinking about it.",
        n_lines=10,
    )
    draw_memorial_list(
        c,
        "Ten Memories I Never Want to Lose",
        "The small ones, the silly ones, the holy ones. Protect them from time.",
        n_lines=10,
    )
    draw_memorial_list(
        c,
        "Their Sayings, Their Phrases",
        "The words that were theirs. The way they answered the phone. The sign-off on letters. The thing they always said.",
        n_lines=10,
    )
    draw_memorial_list(
        c,
        "Five Traits I Hope I Inherited",
        "What I want to keep of them in the way I move through the world.",
        n_lines=5,
    )

    # STAGES + RESOURCES
    draw_stages_of_grief(c)
    draw_resources_page(c)

    # CLOSING
    draw_closing_page(c)

    c.save()
    return OUTPUT


if __name__ == "__main__":
    out = build()
    print(f"Wrote {out}")
