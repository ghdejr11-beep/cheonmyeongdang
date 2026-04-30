"""Pet Loss Memorial Journal - A Healing Companion (6x9, ~120 pages)

A guided grief journal for adults mourning the loss of a beloved pet
(dog, cat, or any companion animal). Each section walks the reader from
the raw first days through the long arc of healing - while preserving
their pet's memory in dedicated memorial pages.
"""
import os
from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

PAGE = (6 * inch, 9 * inch)
W, H = PAGE
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pet_loss_memorial_journal.pdf")

# Soft healing palette - sage + dusty rose + cream
DARK = HexColor("#3F5E48")        # deep sage
ACCENT = HexColor("#8DA290")      # mid sage
SOFT = HexColor("#EAEFE7")        # mist sage
ROSE = HexColor("#D9A6A0")        # dusty rose
CREAM = HexColor("#F7EFE2")       # warm cream
MID_GRAY = HexColor("#CFCFCF")
LIGHT_GRAY = HexColor("#F4F4F4")
GOLD = HexColor("#B98E4D")        # warm gold

MARGIN = 0.75 * inch  # KDP-safe for 100+ pages on 6x9


# ---------- helpers ----------
def footer(c, page_label=""):
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, MARGIN - 18, page_label or "Pet Loss Memorial Journal | Deokgu Studio")


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
    # decorative rule
    c.setStrokeColor(ROSE)
    c.setLineWidth(1.2)
    c.line(W / 2 - 30, H - 1.12 * inch, W / 2 + 30, H - 1.12 * inch)
    c.setLineWidth(1.0)
    return H - 1.5 * inch


# ---------- pages ----------
def draw_title_page(c):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # sage band
    c.setFillColor(DARK)
    c.rect(0, H * 0.42, W, H * 0.20, fill=1, stroke=0)

    # title
    c.setFillColor(CREAM)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W / 2, H * 0.54, "PET LOSS")
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W / 2, H * 0.46, "MEMORIAL JOURNAL")

    # subtitle
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(W / 2, H * 0.36, "A Healing Companion Through")
    c.drawCentredString(W / 2, H * 0.33, "the Grief of Losing Your Best Friend")

    # paw-print accent (drawn as soft circle cluster)
    cx, cy, r = W / 2, H * 0.22, 5
    c.setFillColor(ROSE)
    for dx, dy in [(-14, 0), (14, 0), (-7, 10), (7, 10)]:
        c.circle(cx + dx, cy + dy, r, fill=1, stroke=0)
    c.circle(cx, cy - 8, 9, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, H * 0.08, "Deokgu Studio")
    c.showPage()


def draw_dedication_page(c):
    y = H - 1.4 * inch
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, y, "In loving memory of")

    y -= 36
    hline(c, MARGIN + 30, W - MARGIN - 30, y)
    c.setFont("Helvetica", 8)
    c.setFillColor(MID_GRAY)
    c.drawCentredString(W / 2, y - 12, "Their name")

    y -= 60
    c.setFillColor(DARK)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, y, "Forever in my heart")

    y -= 30
    c.drawCentredString(W / 2, y, "________ - ________")
    c.setFont("Helvetica", 8)
    c.setFillColor(MID_GRAY)
    c.drawCentredString(W / 2, y - 12, "Years of love")

    y -= 70
    c.setFillColor(CREAM)
    c.rect(MARGIN, y - 110, W - 2 * MARGIN, 110, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 11)
    quote_lines = [
        '"Until one has loved an animal,',
        'a part of one\'s soul remains',
        'unawakened."',
    ]
    qy = y - 30
    for line in quote_lines:
        c.drawCentredString(W / 2, qy, line)
        qy -= 16
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, y - 90, "- Anatole France")

    page_break(c)


def draw_about_my_pet_page(c):
    y = section_title(c, "About My Best Friend")

    fields = [
        ("Their full name:", 1),
        ("Nicknames I called them:", 2),
        ("Species / breed:", 1),
        ("Birthday (or adoption day):", 1),
        ("The day they joined our family:", 1),
        ("Their color, markings, weight:", 2),
        ("Their eyes (and the look I will never forget):", 2),
    ]
    for label, lines in fields:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, label)
        y -= 6
        y = field_lines(c, lines, y, MARGIN, W - MARGIN, leading=18)
        y -= 12

    page_break(c)


def draw_how_we_met_page(c):
    y = section_title(c, "How We Found Each Other")

    prompts = [
        "Where I first saw them:",
        "What I remember about that first moment:",
        "Why I chose them - or how they chose me:",
        "What our first day at home was like:",
    ]
    for p in prompts:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, p)
        y -= 6
        y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=18)
        y -= 12
    page_break(c)


def draw_their_personality_page(c):
    y = section_title(c, "Who They Were")

    sections = [
        ("Their personality in one sentence:", 2),
        ("Things they loved (foods, places, people, toys):", 4),
        ("Things they hated:", 3),
        ("Funny habits and quirks only they had:", 4),
        ("The sound they made when they were happy:", 2),
    ]
    for label, lines in sections:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, label)
        y -= 6
        y = field_lines(c, lines, y, MARGIN, W - MARGIN, leading=16)
        y -= 8

    page_break(c)


def draw_photo_memorial_page(c, label):
    y = section_title(c, label)

    # large photo box
    box_h = 3.0 * inch
    c.setStrokeColor(ACCENT)
    c.setFillColor(SOFT)
    c.rect(MARGIN, y - box_h, W - 2 * MARGIN, box_h, fill=1, stroke=1)

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(W / 2, y - box_h / 2, "tape or paste a favorite photo here")

    y -= box_h + 18

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "When this was taken:")
    c.setStrokeColor(MID_GRAY)
    c.line(MARGIN + 130, y - 2, W - MARGIN, y - 2)

    y -= 22
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "What I remember about this moment:")
    y -= 6
    y = field_lines(c, 5, y, MARGIN, W - MARGIN, leading=18)

    page_break(c, label)


def draw_how_to_use(c):
    y = section_title(c, "How to Use This Journal")

    paragraphs = [
        "Grief has no schedule. This journal does not push you forward; it walks beside you. Use it on the days you can. Skip the days you cannot. Both are part of healing.",
        "",
        "1. THEIR STORY  -  The first pages are a place to remember who they were while the details are sharp. Writing them down protects them from time.",
        "",
        "2. FIRST WEEK PAGES  -  Seven longer entries for the rawest days. Prompts that meet you where you are: the empty bowl, the silent house, the first night.",
        "",
        "3. DAILY GRIEF PAGES  -  Sixty short check-ins. Three to five minutes a day. Track what hurts, what helped, what you noticed.",
        "",
        "4. WEEKLY REFLECTIONS  -  Brief look-backs every seventh day to see your own progress, even when you can't feel it.",
        "",
        "5. MILESTONE PAGES  -  At one month, three months, six months, and one year, longer reflections to honor where you are.",
        "",
        "6. LETTERS, MEMORIES, PHOTOS  -  Memorial pages throughout to write to them, hold their stories, and keep their face close.",
        "",
        "7. RESOURCES  -  Pet loss support lines, books, and grief stages information at the back.",
        "",
        "There is no wrong way to do this. If you cry on the page, let it warp the paper. The book is meant for that.",
    ]
    for p in paragraphs:
        if p == "":
            y -= 8
            continue
        y = wrap_text(c, p, MARGIN, y, W - 2 * MARGIN, size=10, leading=14)
    page_break(c)


def draw_stages_of_grief(c):
    y = section_title(c, "The Stages of Pet Grief")

    c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 9)
    y = wrap_text(c,
                  "Grief is not a line. You will move through these in your own order, more than once.",
                  MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=14)
    y -= 14

    stages = [
        ("DENIAL & SHOCK",
         "The house feels wrong. You hear them. You forget for a second, then remember. This is your nervous system protecting you while the news lands."),
        ("GUILT & 'WHAT IF'",
         "Almost every grieving pet owner replays the last days. Did I miss something? Should I have known? This is love looking for somewhere to go - not evidence of failure."),
        ("ANGER",
         "At the vet. At yourself. At people who 'don't get it.' Anger is grief with armor on. Let it out somewhere safe; do not let it sit on someone you love."),
        ("DEEP SADNESS",
         "The wave that takes the air out. It is also the one that lets the love through. Sit on the floor and cry on this book if you need to."),
        ("BARGAINING WITH MEMORY",
         "Looking at photos, replaying their best day. This is how the bond moves from body to memory."),
        ("MEANING & ACCEPTANCE",
         "Not 'getting over' - getting through. You start carrying them differently. The love stays. The sharpest pain quiets."),
    ]
    for name, desc in stages:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, name)
        y -= 12
        c.setFillColor(black)
        y = wrap_text(c, desc, MARGIN + 10, y, W - 2 * MARGIN - 10, size=9, leading=12)
        y -= 8

    page_break(c)


# ----- First-week deep daily pages -----
def draw_first_week_day(c, day_num, prompt_title, prompts):
    # header band
    top = H - MARGIN
    c.setFillColor(DARK)
    c.rect(MARGIN, top - 32, W - 2 * MARGIN, 32, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN + 8, top - 14, f"First Week  -  Day {day_num}")
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN + 8, top - 26, prompt_title)
    c.setFont("Helvetica", 8)
    c.drawRightString(W - MARGIN - 8, top - 22, "Date: ___ / ___ / _____")

    y = top - 50

    # mood + tear count strip
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "Today's heaviness (1-10): ____")
    c.drawString(MARGIN + 200, y, "Slept: ____ hrs")
    y -= 16
    c.drawString(MARGIN, y, "I ate today:  Y / N")
    c.drawString(MARGIN + 110, y, "Talked to someone:  Y / N")
    c.drawString(MARGIN + 260, y, "Outside:  Y / N")
    y -= 16

    for p in prompts:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, p)
        y -= 4
        y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=16)
        y -= 8

    page_break(c, f"First Week  -  Day {day_num}")


# ----- Compact daily journal page (60 days) -----
def draw_daily_compact(c, day):
    top = H - MARGIN

    # Soft header
    c.setFillColor(SOFT)
    c.rect(MARGIN, top - 26, W - 2 * MARGIN, 26, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 6, top - 15, f"Day {day}")
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN + 60, top - 15, "of grief")
    c.setFont("Helvetica", 8)
    c.drawRightString(W - MARGIN - 6, top - 17, "Date: ___ / ___ / _____")

    y = top - 44

    # heaviness scale (1-10)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "Heaviness today (1-10):")
    c.setFont("Helvetica", 9)
    for n in range(1, 11):
        cx = MARGIN + 130 + (n - 1) * 14
        c.circle(cx, y + 3, 5, fill=0, stroke=1)
        c.setFont("Helvetica", 6)
        c.drawCentredString(cx, y + 1, str(n))
        c.setFont("Helvetica", 9)
    y -= 22

    # one feeling word + how I slept
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "One word for today:")
    c.setStrokeColor(MID_GRAY)
    c.line(MARGIN + 120, y - 2, W - MARGIN, y - 2)
    y -= 22

    # I missed them most when...
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "I missed them most when...")
    y -= 4
    y = field_lines(c, 3, y, MARGIN, W - MARGIN, leading=16)
    y -= 10

    # something that helped today
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Something that helped today (even a little)")
    y -= 4
    y = field_lines(c, 3, y, MARGIN, W - MARGIN, leading=16)
    y -= 10

    # a memory that came up
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "A memory of them I want to keep")
    y -= 4
    c.setFillColor(black)
    y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=16)
    y -= 10

    # one thing I'll do tomorrow
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "One small thing I'll do tomorrow")
    y -= 4
    y = field_lines(c, 2, y, MARGIN, W - MARGIN, leading=16)

    page_break(c, f"Day {day}")


# ----- Weekly reflection -----
def draw_weekly_reflection(c, week):
    top = H - MARGIN
    c.setFillColor(ACCENT)
    c.rect(MARGIN, top - 30, W - 2 * MARGIN, 30, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, top - 20, f"Week {week} Reflection")

    y = top - 50

    sections = [
        ("How my body felt this week (sleep, appetite, tiredness):", 4),
        ("Moments I felt the loss most sharply:", 4),
        ("Anything that brought a tiny bit of relief:", 4),
        ("A memory that visited me this week:", 4),
        ("What I want to give myself permission to do next week:", 3),
    ]
    for label, lines in sections:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, label)
        y -= 4
        y = field_lines(c, lines, y, MARGIN, W - MARGIN, leading=16)
        y -= 6

    page_break(c, f"Week {week} Reflection")


# ----- Monthly milestone -----
def draw_milestone(c, label, sublabel, prompts):
    top = H - MARGIN
    c.setFillColor(DARK)
    c.rect(MARGIN, top - 56, W - 2 * MARGIN, 56, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, top - 30, label)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, top - 46, sublabel)

    y = top - 84

    for p in prompts:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        y = wrap_text(c, p, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Bold", size=10, leading=13)
        y -= 4
        y = field_lines(c, 4, y, MARGIN, W - MARGIN, leading=16)
        y -= 10

    page_break(c, label)


# ----- Letter pages -----
def draw_letter_page(c, prompt):
    y = section_title(c, "A Letter to You")
    c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 10)
    y = wrap_text(c, prompt, MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=13)
    y -= 14

    # letter lines
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Dear  ____________________ ,")
    y -= 18

    c.setStrokeColor(MID_GRAY)
    while y > MARGIN + 60:
        c.line(MARGIN, y, W - MARGIN, y)
        y -= 18

    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 10)
    c.drawRightString(W - MARGIN, MARGIN + 40, "Always yours,")
    c.line(W - MARGIN - 140, MARGIN + 26, W - MARGIN, MARGIN + 26)
    page_break(c, "Letter")


# ----- Memory list pages -----
def draw_memory_list(c, title, items):
    y = section_title(c, title)
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(MARGIN, y, "Fill these in over time. Some will come back to you on a walk, in a song.")
    y -= 24

    for n, prompt in enumerate(items, 1):
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y, f"{n}.  {prompt}")
        y -= 4
        y = field_lines(c, 2, y, MARGIN + 14, W - MARGIN, leading=14)
        y -= 6
    page_break(c, title)


# ----- Resources page -----
def draw_resources(c):
    y = section_title(c, "Pet Loss Support")

    c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 9)
    y = wrap_text(c,
                  "Talking to someone who understands pet loss is not weakness. It is the same wisdom you used to take them to the vet.",
                  MARGIN, y, W - 2 * MARGIN, font="Helvetica-Oblique", size=10, leading=14)
    y -= 14

    c.setFillColor(CREAM)
    c.rect(MARGIN, y - 130, W - 2 * MARGIN, 130, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN + 8, y - 16, "Pet Loss Hotlines (US)")
    c.setFont("Helvetica", 9)
    c.setFillColor(black)
    cy = y - 32
    lines = [
        "ASPCA Pet Loss Hotline:        1-877-474-3310",
        "Cornell Univ. Pet Loss Line:   607-218-7457  (Tue/Thu evenings)",
        "Tufts Pet Loss Support:        508-839-7966  (Mon-Fri)",
        "Lap of Love Pet Loss Support:  lapoflove.com/pet-loss-support",
        "Rainbows Bridge community:     rainbowsbridge.com",
        "988 Suicide & Crisis Lifeline: call or text 988  (if you need a person)",
    ]
    for line in lines:
        c.drawString(MARGIN + 8, cy, line)
        cy -= 13
    y -= 140

    # Books / reading
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Books that have helped grieving pet families")
    y -= 14
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    books = [
        "  -  'The Loss of a Pet'  -  Wallace Sife",
        "  -  'Goodbye, Friend'  -  Gary Kowalski",
        "  -  'When Your Pet Dies: A Guide to Mourning'  -  Alan Wolfelt",
        "  -  'Saying Goodbye to the Pet You Love'  -  Lorri Greene",
    ]
    for b in books:
        c.drawString(MARGIN, y, b)
        y -= 13

    page_break(c, "Resources")


# ----- Closing pages -----
def draw_carrying_them_forward(c):
    y = section_title(c, "Carrying Them Forward")

    c.setFillColor(black)
    paragraphs = [
        "There is no point at which the love ends. It just learns to live in a different shape.",
        "",
        "Some grieving pet owners keep an empty leash. Some plant a tree. Some donate to a shelter every year on the anniversary. Some adopt again, when ready - not as a replacement, but because the love has somewhere to go.",
        "",
        "On the next page, write what you want to do to keep them with you. There is no right answer.",
    ]
    for p in paragraphs:
        if p == "":
            y -= 8
            continue
        y = wrap_text(c, p, MARGIN, y, W - 2 * MARGIN, size=10, leading=14)
    y -= 12

    sections = [
        ("How I'll honor their memory each year:", 3),
        ("A small ritual just for me and them:", 3),
        ("What I learned about love by loving them:", 4),
    ]
    for label, lines in sections:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, label)
        y -= 4
        y = field_lines(c, lines, y, MARGIN, W - MARGIN, leading=16)
        y -= 8

    page_break(c, "Carrying Them Forward")


def draw_closing(c):
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setFillColor(CREAM)
    c.rect(0, H * 0.42, W, H * 0.16, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.50, "STILL WITH ME")

    c.setFillColor(white)
    c.setFont("Helvetica", 11)
    msg = [
        "What we have once enjoyed",
        "deeply we can never lose.",
        "",
        "All that we love deeply",
        "becomes a part of us.",
        "",
        "- Helen Keller",
    ]
    y = H * 0.34
    for line in msg:
        if line == "":
            y -= 8
            continue
        c.drawCentredString(W / 2, y, line)
        y -= 16

    # paw print
    cx, cy, r = W / 2, H * 0.18, 5
    c.setFillColor(ROSE)
    for dx, dy in [(-14, 0), (14, 0), (-7, 10), (7, 10)]:
        c.circle(cx + dx, cy + dy, r, fill=1, stroke=0)
    c.circle(cx, cy - 8, 9, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(W / 2, H * 0.07, "Deokgu Studio")
    c.showPage()


# ---------- main ----------
def main():
    c = canvas.Canvas(OUTPUT, pagesize=PAGE)
    c.setTitle("Pet Loss Memorial Journal - A Healing Companion")
    c.setAuthor("Deokgu Studio")
    c.setSubject("Pet Loss, Grief, Memorial")
    c.setKeywords("pet loss, dog grief, cat grief, memorial journal, pet memorial, healing")

    # Front matter (~10 pages)
    draw_title_page(c)
    draw_dedication_page(c)
    draw_about_my_pet_page(c)
    draw_how_we_met_page(c)
    draw_their_personality_page(c)
    draw_photo_memorial_page(c, "A Favorite Photo")
    draw_how_to_use(c)
    draw_stages_of_grief(c)

    # First Week - 7 deep daily pages
    first_week = [
        ("The first day without them",
         ["What today felt like the moment I woke up:",
          "What I keep expecting to see or hear:",
          "Something I want to say to them right now:"]),
        ("Their empty space",
         ["The places in my home that feel different:",
          "The objects I cannot put away yet:",
          "What I want to do with their things, eventually:"]),
        ("How my body is taking it",
         ["My sleep, eating, and energy today:",
          "Where I feel grief in my body:",
          "One small kindness I can give my body tomorrow:"]),
        ("The story of our last day",
         ["What I want to remember about our last hours together:",
          "What I want to forgive myself for:",
          "What they would tell me if they could:"]),
        ("Who has shown up - and who hasn't",
         ["People who have understood the size of this:",
          "People who said the wrong thing (it's okay):",
          "Who I can ask for support tomorrow:"]),
        ("Their voice in my head",
         ["The sound of them I do not want to forget:",
          "What they 'said' to me without words:",
          "When I most expect to hear them today:"]),
        ("Closing the first week",
         ["What this week took from me:",
          "What this week taught me about my love for them:",
          "What I need to ask for in the days ahead:"]),
    ]
    for i, (ttl, prompts) in enumerate(first_week, 1):
        draw_first_week_day(c, i, ttl, prompts)

    # 60 daily compact pages with weekly reflections
    # Plus milestone reflections at Day 30 and Day 60
    DAYS = 60
    milestone_days = {30, 60}
    for d in range(1, DAYS + 1):
        draw_daily_compact(c, d)
        if d % 10 == 0:
            draw_weekly_reflection(c, d // 10)

    # Memorial / letter pages interspersed at the end
    draw_letter_page(c, "If I could write them one letter, this is what I would say.")
    draw_photo_memorial_page(c, "Their Best Day")
    draw_memory_list(c, "Ten Memories I Never Want to Lose",
                     ["The first time I knew I loved them",
                      "The funniest thing they ever did",
                      "Their favorite walk / spot / corner",
                      "The trick or sound that was theirs alone",
                      "A vacation or trip we took together",
                      "How they greeted me when I came home",
                      "A time they made me laugh through tears",
                      "Their quiet way of telling me they loved me",
                      "A photo I will keep forever",
                      "Their last gift to me"])
    draw_letter_page(c, "Tell them about who you've become because of them.")
    draw_photo_memorial_page(c, "Just Their Eyes")
    draw_memory_list(c, "Their Daily Rituals",
                     ["Their morning routine",
                      "How they ate / drank",
                      "Their sleeping place",
                      "Their afternoon habits",
                      "Their welcome-home moment",
                      "Their evening / bedtime ritual",
                      "Sounds I'll always associate with them",
                      "Their funny demands (the ones I never refused)"])

    # Long-arc milestones
    draw_milestone(c, "ONE MONTH",
                   "What the first month gave - and took",
                   ["Look back at the past month. What surprised you about your grief?",
                    "What is harder than you expected? What is a little easier?",
                    "Who or what has gotten you through?",
                    "What do you want to say to the version of you on Day 1?"])

    draw_milestone(c, "THREE MONTHS",
                   "Carrying it differently",
                   ["What does grief feel like now versus the first weeks?",
                    "Are there moments you feel guilty for laughing? You don't have to.",
                    "Who or what has unexpectedly comforted you?",
                    "What about them is becoming clearer with time?"])

    draw_milestone(c, "SIX MONTHS",
                   "The slow softening",
                   ["What do you notice you are no longer afraid of?",
                    "What part of your daily life still has their shape?",
                    "If you've thought about adopting again, what feels true?",
                    "What does loving them now ask of you?"])

    draw_milestone(c, "ONE YEAR",
                   "A whole year of carrying you",
                   ["The first year is hard - all of it. What did you survive that you didn't think you could?",
                    "What rituals or habits do you want to keep doing every year?",
                    "If you could tell other people one thing about pet grief, what would it be?",
                    "How will you mark today, every year, going forward?"])

    draw_letter_page(c, "Tell them you are okay - or that you are not - and that you carry them.")
    draw_carrying_them_forward(c)
    draw_resources(c)
    draw_closing(c)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
