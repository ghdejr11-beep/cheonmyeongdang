"""Postpartum Pelvic Floor Recovery Journal - 8.5x11, ~120 pages

For new moms in the first 12 weeks postpartum. Tracks Kegels, leakage,
prolapse symptoms, perineal/c-section incision pain, and pelvic PT visits
so users can recover with data and walk into pelvic-floor PT prepared.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pelvic_floor_recovery_journal.pdf")

DARK = HexColor("#2D5F5D")        # deep teal
ACCENT = HexColor("#5A8F89")      # sage
SOFT = HexColor("#E8F0EE")        # mint cream
MID_GRAY = HexColor("#CCCCCC")
LIGHT_GRAY = HexColor("#F5F5F5")
GREEN = HexColor("#2E7D32")
ORANGE = HexColor("#E65100")
RED = HexColor("#C62828")

MARGIN = 0.75 * inch
WEEKS = 12   # 12 weeks * (7 daily + 1 weekly) = 96 pages of logs
PT_VISITS = 4   # 4 pelvic-PT visit prep pages (every 3 weeks)


# ---------- helpers ----------
def footer(c, title="Postpartum Pelvic Floor Recovery Journal | Deokgu Studio"):
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, MARGIN - 12, title)


def page_break(c):
    footer(c)
    c.showPage()


def underline_field(c, x, y, w, label=None):
    if label:
        c.setFillColor(DARK)
        c.setFont("Helvetica", 10)
        c.drawString(x, y + 4, label)
        c.setStrokeColor(MID_GRAY)
        c.line(x + 130, y, x + 130 + w, y)
    else:
        c.setStrokeColor(MID_GRAY)
        c.line(x, y, x + w, y)


def wrap_para(c, text, x, y, max_w, font="Helvetica", size=11, leading=16):
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


# ---------- pages ----------
def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(MARGIN, MARGIN, W - 2 * MARGIN, H - 2 * MARGIN, fill=1, stroke=0)
    c.setFillColor(SOFT)
    c.rect(MARGIN, H * 0.42, W - 2 * MARGIN, 4, fill=1, stroke=0)
    c.rect(MARGIN, H * 0.62, W - 2 * MARGIN, 4, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W / 2, H * 0.55, "Postpartum")
    c.drawCentredString(W / 2, H * 0.55 - 38, "Pelvic Floor Recovery")

    c.setFont("Helvetica", 13)
    c.drawCentredString(W / 2, H * 0.36, "Kegels  |  Leakage  |  Prolapse  |  Pain  |  PT Visits")
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, H * 0.30, "A 12-Week Daily Journal for New Moms")

    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.14, "Deokgu Studio")
    c.showPage()


def draw_personal_info(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "About Me")

    y = H - 1.7 * inch
    fields = [
        "Name:", "Baby's Name:", "Baby's Birth Date:", "Days Postpartum (today):",
        "Delivery Type (vaginal / C-sec / VBAC):", "Tearing / Episiotomy (degree):",
        "Birth Weight:", "First / Second / Subsequent baby:",
        "OB / Midwife:", "Phone:",
        "Pelvic Floor PT:", "Phone:",
        "Lactation Consultant:", "",
        "Current Medications / Supplements:", "", "",
        "Concerns I want to address in recovery:", "",
    ]
    for f in fields:
        underline_field(c, MARGIN, y, W - 2 * MARGIN - 130, label=f if f else None)
        y -= 26
    page_break(c)


def draw_how_to_use(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "How To Use This Journal")

    y = H - 1.7 * inch
    c.setFillColor(black)
    paragraphs = [
        "The first 12 weeks postpartum (the 'fourth trimester') are when your pelvic floor is most plastic — and when honest tracking changes outcomes. This journal is built to give you data, not pressure.",
        "",
        "1. Each evening, fill in one DAILY page. Rate symptoms 0 (none) - 5 (severe). Log your Kegel sets, even if only one set today.",
        "2. At the end of each week, complete the WEEKLY REVIEW. Watch leakage and pain trend down over time.",
        "3. Every 3 weeks, complete the PELVIC PT VISIT PREP page before your appointment. Bring this book.",
        "4. Don't push: if symptoms worsen (heavy bleeding, fever, foul-smelling discharge, increasing prolapse), call your provider that day.",
        "",
        "This is a personal recovery journal, not medical advice. Always discuss symptoms and exercises with a qualified pelvic-floor physical therapist or your OB.",
    ]
    for p in paragraphs:
        if p == "":
            y -= 10
            continue
        y = wrap_para(c, p, MARGIN, y, W - 2 * MARGIN, size=11, leading=16)
    page_break(c)


def draw_milestones(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "Recovery Milestones (Typical)")

    y = H - 1.6 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Every body is different — these are common ranges, not deadlines.")
    y -= 28

    milestones = [
        ("Week 1-2", [
            "Bleeding (lochia) heavy then tapering. Use pads, not tampons.",
            "Perineum / incision tender. Ice + sitz baths help.",
            "Gentle diaphragmatic breathing only. No Kegels yet if it hurts.",
        ]),
        ("Week 3-6", [
            "Lochia transitions to brown then yellow-white.",
            "Begin gentle Kegels: 5-second holds, 5 reps, 2-3x/day.",
            "Walking is your friend. No running, lifting, or sit-ups.",
        ]),
        ("Week 6 Check-Up", [
            "OB clears (or doesn't clear) you for exercise and intercourse.",
            "ASK for a pelvic-floor PT referral - it is the standard of care.",
            "Diastasis recti and prolapse should be checked at this visit.",
        ]),
        ("Week 7-12", [
            "Pelvic PT typically begins. Internal exam may guide your program.",
            "Build Kegels: 10-second holds, 10 reps, 3x/day. Add quick flicks.",
            "Re-introduce core: bird-dog, dead-bug, glute bridges.",
        ]),
        ("Beyond 12 Weeks", [
            "Most leakage and pain should be improving. Plateau? Get assessed.",
            "Return to running typically week 12+ with PT clearance.",
            "Heavy lifting and high-impact: ease in, not all-or-nothing.",
        ]),
    ]
    c.setFont("Helvetica", 10)
    for label, items in milestones:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN, y, label)
        y -= 16
        c.setFillColor(black)
        c.setFont("Helvetica", 10)
        for it in items:
            c.drawString(MARGIN + 14, y, "- " + it)
            y -= 14
        y -= 6
    page_break(c)


def draw_kegel_reference(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "Kegel & Symptom Reference")

    y = H - 1.7 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "A quick reference - use these terms in your daily and weekly logs.")
    y -= 28

    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "How to Find Your Pelvic Floor")
    y -= 16
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    intro_lines = [
        "Imagine stopping the flow of urine and stopping passing gas at the same time.",
        "That gentle inward-and-upward squeeze is your pelvic floor. Don't clench buttocks,",
        "abs, or thighs. Don't hold your breath. Do not practice on the toilet.",
    ]
    for ln in intro_lines:
        c.drawString(MARGIN + 12, y, ln)
        y -= 14
    y -= 8

    cats = [
        ("Kegel Types", [
            "Long hold: squeeze 5-10 sec, fully relax 10 sec",
            "Quick flick: squeeze + release, 1 second each",
            "Functional: squeeze before you cough, sneeze, lift, stand",
        ]),
        ("Leakage", [
            "Stress: leak with cough / sneeze / laugh / lift",
            "Urge: sudden need, can't make it",
            "Mixed: both stress + urge",
        ]),
        ("Prolapse Sensations", [
            "Heaviness or bulge in vagina / pelvis",
            "'Tampon falling out' feeling",
            "Worse at end of day or with standing",
        ]),
        ("Pain to Track", [
            "Perineum / episiotomy site",
            "C-section incision",
            "Tailbone / coccyx",
            "Pubic bone (symphysis)",
            "Pain with sex (after week 6 clearance)",
        ]),
        ("Red Flags - Call Your Provider", [
            "Soaking a pad in 1 hour",
            "Fever > 100.4 F (38 C)",
            "Foul-smelling discharge",
            "Calf pain or shortness of breath",
            "Worsening prolapse symptoms",
        ]),
    ]
    c.setFont("Helvetica", 10)
    for cat, items in cats:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, cat)
        y -= 14
        c.setFillColor(black)
        c.setFont("Helvetica", 10)
        text = "  -  ".join(items)
        # wrap
        y = wrap_para(c, text, MARGIN + 12, y, W - 2 * MARGIN - 12, size=10, leading=13)
        y -= 6
    page_break(c)


def draw_baseline_assessment(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "Baseline Assessment")

    y = H - 1.6 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Fill this in once, on Day 1. Compare in 12 weeks.")
    y -= 28

    sections = [
        ("Today's date", 1),
        ("Days postpartum", 1),
        ("Hours of sleep last night", 1),
        ("Weight", 1),
        ("Mood (0 low - 10 great)", 1),
        ("Pain level (0-10)", 1),
        ("Leakage frequency: never / rare / daily / many times daily", 1),
        ("Prolapse heaviness (0-10)", 1),
        ("Can I do a Kegel? Yes / not yet / unsure", 1),
        ("Longest Kegel hold (seconds)", 1),
        ("Diastasis (finger gap above navel)", 1),
    ]
    c.setFont("Helvetica", 11)
    for label, _ in sections:
        c.setFillColor(DARK)
        c.drawString(MARGIN, y, label)
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN + 320, y - 2, W - MARGIN, y - 2)
        y -= 26

    y -= 10
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "What does recovery look like to me?")
    y -= 6
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    for _ in range(4):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    page_break(c)


def draw_daily_log(c, week, day):
    top = H - MARGIN
    # Header banner
    c.setFillColor(ACCENT)
    c.rect(MARGIN, top - 28, W - 2 * MARGIN, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 8, top - 20, f"Week {week}  |  Day {day}")
    c.drawRightString(W - MARGIN - 8, top - 20, "Date: ____/____/________   Days PP: ____")

    y = top - 50

    # Sleep / mood / energy row
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Sleep (hrs):  ____")
    c.drawString(MARGIN + 130, y, "Night wakings:  ____")
    c.drawString(MARGIN + 280, y, "Mood (0-10):  ____")
    c.drawString(MARGIN + 410, y, "Energy (0-10):  ____")
    y -= 22

    # Bleeding / discharge
    c.drawString(MARGIN, y, "Bleeding:  none / spot / light / med / heavy   Color:  red / brown / yellow / clear")
    y -= 22

    # Symptom rating table (0-5 scale)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Symptoms today  (circle 0 = none, 5 = severe)")
    y -= 14

    symptoms = [
        "Urinary leakage (count: ____)",
        "Urge / can't make it",
        "Bowel difficulty / pushing",
        "Prolapse / heaviness",
        "Perineum or incision pain",
        "Tailbone / pubic pain",
        "Back pain",
        "Pain with sex (if cleared)",
    ]
    col_w = (W - 2 * MARGIN) / 2 - 6
    col_x = [MARGIN, MARGIN + col_w + 12]
    row_h = 22
    half = (len(symptoms) + 1) // 2

    c.setFont("Helvetica", 10)
    for col_idx in (0, 1):
        cy = y
        for i in range(half):
            idx = col_idx * half + i
            if idx >= len(symptoms):
                break
            cy_row = cy - i * row_h
            c.setFillColor(LIGHT_GRAY if i % 2 == 0 else SOFT)
            c.rect(col_x[col_idx], cy_row - 14, col_w, row_h - 4, fill=1, stroke=0)
            c.setFillColor(DARK)
            c.drawString(col_x[col_idx] + 6, cy_row - 6, symptoms[idx])
            c.setFont("Helvetica", 9)
            for n in range(6):
                cx = col_x[col_idx] + col_w - 90 + n * 14
                c.circle(cx, cy_row - 4, 5, fill=0, stroke=1)
                c.drawCentredString(cx, cy_row - 6, str(n))
            c.setFont("Helvetica", 10)
    y -= half * row_h + 6

    # Kegel log
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Kegels today")
    y -= 20
    c.setFillColor(SOFT)
    c.rect(MARGIN, y - 4, W - 2 * MARGIN, 16, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    headers = ["Set", "Long holds  (sec x reps)", "Quick flicks (reps)", "How it felt"]
    cw = [(W - 2 * MARGIN) * x for x in (0.10, 0.30, 0.25, 0.35)]
    cx = MARGIN
    for i, h in enumerate(headers):
        c.drawString(cx + 6, y, h)
        cx += cw[i]
    y -= 18
    c.setFont("Helvetica", 10)
    c.setStrokeColor(MID_GRAY)
    for i in range(3):
        c.line(MARGIN, y - 4, W - MARGIN, y - 4)
        cx2 = MARGIN
        for ww in cw[:-1]:
            cx2 += ww
            c.line(cx2, y - 4, cx2, y + 18)
        c.setFillColor(DARK)
        c.drawString(MARGIN + 6, y + 4, str(i + 1))
        c.setFillColor(black)
        y -= 22

    # Movement / exercise
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Movement today (walk min, breathing, PT exercises):")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    # Triggers / notes
    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Possible triggers (cough / lift / standing / fatigue):")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "One small win today:")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    page_break(c)


def draw_weekly_review(c, week):
    top = H - MARGIN
    c.setFillColor(ACCENT)
    c.rect(MARGIN, top - 32, W - 2 * MARGIN, 32, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, top - 22, f"Week {week} Review")

    y = top - 56
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "This week's averages:")
    y -= 24
    avgs = [
        "Sleep hours per night:",
        "Leakage episodes total:",
        "Prolapse heaviness (0-5 avg):",
        "Pain level (0-5 avg):",
        "Days I did Kegels:",
        "Longest hold this week (sec):",
        "Days I walked:",
    ]
    c.setFont("Helvetica", 11)
    for a in avgs:
        c.setFillColor(DARK)
        c.drawString(MARGIN + 14, y, a)
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN + 240, y - 2, MARGIN + 380, y - 2)
        y -= 22

    # Trend chart - leakage
    y -= 6
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Leakage Episodes - Daily Trend")
    y -= 8
    gh = 130
    c.setFillColor(SOFT)
    c.setStrokeColor(MID_GRAY)
    c.rect(MARGIN, y - gh, W - 2 * MARGIN, gh, fill=1, stroke=1)
    c.setFont("Helvetica", 8)
    c.setFillColor(DARK)
    for val in [0, 2, 4, 6, 8, 10]:
        yy = y - gh + val * gh / 10
        c.drawRightString(MARGIN - 4, yy - 3, str(val))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    step = (W - 2 * MARGIN) / 7
    for i, d in enumerate(days):
        c.drawCentredString(MARGIN + step * i + step / 2, y - gh - 14, d)

    # Wins / what helped
    y -= gh + 30
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "What got better this week:")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 14
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "What I'm watching:")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    page_break(c)


def draw_pt_visit_prep(c, visit_n):
    top = H - MARGIN
    c.setFillColor(DARK)
    c.rect(MARGIN, top - 36, W - 2 * MARGIN, 36, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, top - 24, f"Pelvic Floor PT Visit Prep  -  #{visit_n}")

    y = top - 60
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, f"Appointment date:  ____ / ____ / ________     PT name: __________________________")
    y -= 26

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Top 3 symptoms affecting my life right now")
    y -= 6
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    for i in range(1, 4):
        y -= 22
        c.drawString(MARGIN, y, f"{i}.")
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN + 18, y - 2, W - MARGIN, y - 2)

    y -= 24
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Leakage / prolapse / pain since last visit (better, same, worse?)")
    y -= 6
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Activities I want to return to (run / lift / sex / sport)")
    y -= 6
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Questions to ask my PT")
    y -= 6
    for _ in range(5):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Home program assigned today")
    y -= 6
    for _ in range(4):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    page_break(c)


def draw_12week_checkpoint(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "12-Week Checkpoint")

    y = H - 1.6 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Compare to your Day 1 baseline. Real progress is rarely linear.")
    y -= 28

    sections = [
        "Today's date",
        "Days postpartum",
        "Hours of sleep last night",
        "Weight",
        "Mood (0 low - 10 great)",
        "Pain level (0-10)",
        "Leakage frequency: never / rare / daily / many times daily",
        "Prolapse heaviness (0-10)",
        "Longest Kegel hold (seconds)",
        "Diastasis (finger gap above navel)",
    ]
    c.setFont("Helvetica", 11)
    for label in sections:
        c.setFillColor(DARK)
        c.drawString(MARGIN, y, label)
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN + 320, y - 2, W - MARGIN, y - 2)
        y -= 24

    y -= 10
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "What changed most?")
    y -= 6
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 14
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "Next 12 weeks goals")
    y -= 6
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    page_break(c)


def draw_closing(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "Strong, Slow, and Steady")

    y = H - 1.8 * inch
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    msg = [
        "Twelve weeks of tracking is real, valuable data - about you, by you.",
        "",
        "Look back through the pages. What patterns surprised you? Which",
        "weeks felt strongest? Which exercises moved the needle most?",
        "",
        "Bring this book to your next pelvic-PT appointment. You have",
        "evidence, not guesswork, to guide your next steps.",
        "",
        "Recovery is not a deadline. It's a direction.",
    ]
    for line in msg:
        c.drawCentredString(W / 2, y, line)
        y -= 18

    page_break(c)


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Postpartum Pelvic Floor Recovery Journal")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_personal_info(c)
    draw_how_to_use(c)
    draw_milestones(c)
    draw_kegel_reference(c)
    draw_baseline_assessment(c)

    # 12 weeks: 7 daily + 1 weekly = 8 pages * 12 = 96
    # PT visit prep at end of weeks 3, 6, 9, 12
    pt_after_weeks = {3, 6, 9, 12}
    visit_n = 0
    for week in range(1, WEEKS + 1):
        for day in range(1, 8):
            draw_daily_log(c, week, day)
        draw_weekly_review(c, week)
        if week in pt_after_weeks:
            visit_n += 1
            draw_pt_visit_prep(c, visit_n)

    draw_12week_checkpoint(c)
    draw_closing(c)
    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
