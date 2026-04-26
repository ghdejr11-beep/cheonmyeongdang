"""Perimenopause Symptom Tracker & HRT Logbook - 8.5x11, ~120 pages

For women 35-55 navigating perimenopause. Tracks daily hot flashes, mood,
sleep, energy, cycle, HRT/supplements, and includes monthly Doctor Visit Prep
sheets so users can bring real data to their gynecologist.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perimenopause_symptom_tracker.pdf")

DARK = HexColor("#5E2750")        # plum
ACCENT = HexColor("#A0457A")      # mauve
SOFT = HexColor("#F4E4EE")        # blush
MID_GRAY = HexColor("#CCCCCC")
LIGHT_GRAY = HexColor("#F5F5F5")
GREEN = HexColor("#2E7D32")
ORANGE = HexColor("#E65100")
RED = HexColor("#C62828")

MARGIN = 0.75 * inch
WEEKS = 14   # 14 weeks * (7 daily + 1 weekly) = 112 pages of logs
MONTHS = 3   # 3 monthly doctor-visit prep pages


# ---------- helpers ----------
def footer(c, title="Perimenopause Symptom Tracker | Deokgu Studio"):
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
        c.line(x + 110, y, x + 110 + w, y)
    else:
        c.setStrokeColor(MID_GRAY)
        c.line(x, y, x + w, y)


# ---------- pages ----------
def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(MARGIN, MARGIN, W - 2 * MARGIN, H - 2 * MARGIN, fill=1, stroke=0)
    c.setFillColor(SOFT)
    c.rect(MARGIN, H * 0.42, W - 2 * MARGIN, 4, fill=1, stroke=0)
    c.rect(MARGIN, H * 0.62, W - 2 * MARGIN, 4, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(W / 2, H * 0.55, "Perimenopause")
    c.drawCentredString(W / 2, H * 0.55 - 38, "Symptom Tracker")

    c.setFont("Helvetica", 13)
    c.drawCentredString(W / 2, H * 0.36, "Hot Flashes  |  Mood  |  Sleep  |  Cycle  |  HRT")
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, H * 0.30, "A 14-Week Daily Journal with Doctor Visit Prep")

    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.14, "Deokgu Studio")
    c.showPage()


def draw_personal_info(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "About Me")

    y = H - 1.7 * inch
    fields = [
        "Name:", "Date of Birth:", "Age:", "Started This Journal:",
        "Last Menstrual Period:", "Typical Cycle Length:",
        "Gynecologist:", "Phone:", "Pharmacy:", "Emergency Contact:",
        "Current HRT / Medications:", "", "",
        "Supplements:", "",
        "Known Allergies:", "",
        "Other Health Conditions:", "",
    ]
    for f in fields:
        underline_field(c, MARGIN, y, W - 2 * MARGIN - 110, label=f if f else None)
        y -= 26
    page_break(c)


def draw_how_to_use(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "How To Use This Tracker")

    y = H - 1.7 * inch
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    paragraphs = [
        "Perimenopause symptoms can shift week to week. Tracking them daily for 14 weeks gives you a clear picture of patterns — and gives your doctor real data to work with.",
        "",
        "1. Each morning or evening, fill in one DAILY page. Rate symptoms 0 (none) - 5 (severe).",
        "2. At the end of each week, complete the WEEKLY REVIEW. Spot trends in mood, sleep, and hot flashes.",
        "3. Once a month, fill in the DOCTOR VISIT PREP page before your appointment. Bring this book with you.",
        "4. If you start or change HRT, supplements, or any medication, note the date and dose so you can correlate with how you feel.",
        "",
        "This is a personal journal, not medical advice. Always discuss symptoms and treatment options with a qualified healthcare provider.",
    ]
    for p in paragraphs:
        if p == "":
            y -= 10
            continue
        # simple wrap
        words = p.split()
        line = ""
        for w_ in words:
            test = (line + " " + w_).strip()
            if c.stringWidth(test, "Helvetica", 11) > W - 2 * MARGIN:
                c.drawString(MARGIN, y, line)
                y -= 16
                line = w_
            else:
                line = test
        if line:
            c.drawString(MARGIN, y, line)
            y -= 16
    page_break(c)


def draw_symptom_reference(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "Common Perimenopause Symptoms")

    y = H - 1.6 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Use these labels in the 'Other Symptoms' field of your daily log.")
    y -= 24

    cats = [
        ("Vasomotor", ["Hot flashes", "Night sweats", "Chills", "Heart palpitations"]),
        ("Sleep", ["Insomnia", "Waking 3-5am", "Restless legs", "Vivid dreams"]),
        ("Mood", ["Anxiety", "Low mood", "Irritability", "Mood swings", "Tearfulness"]),
        ("Cognitive", ["Brain fog", "Memory lapses", "Word-finding trouble", "Difficulty focusing"]),
        ("Cycle", ["Heavy bleeding", "Spotting", "Skipped period", "Shorter cycle", "Longer cycle"]),
        ("Body", ["Joint pain", "Muscle aches", "Headaches", "Migraines", "Bloating", "Weight gain"]),
        ("Skin & Hair", ["Dry skin", "Itchy skin", "Hair thinning", "Acne", "Facial hair"]),
        ("Genitourinary", ["Vaginal dryness", "Painful sex", "Urinary urgency", "UTIs"]),
        ("Energy", ["Fatigue", "Crashing energy", "Low libido"]),
    ]
    c.setFont("Helvetica", 10)
    for cat, items in cats:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, cat)
        y -= 14
        c.setFillColor(black)
        c.setFont("Helvetica", 10)
        text = "  •  ".join(items)
        c.drawString(MARGIN + 12, y, text)
        y -= 18
    page_break(c)


def draw_hrt_reference(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "HRT & Supplement Notes")

    y = H - 1.7 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Record any hormone therapy or supplement so you can correlate with symptoms. Always discuss with your doctor.")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Hormone Therapy (HRT)")
    y -= 18
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    headers = ["Type / Brand", "Dose", "Route (oral/patch/gel)", "Started"]
    cw = [(W - 2 * MARGIN) / 4] * 4
    c.setFillColor(SOFT)
    c.rect(MARGIN, y - 2, W - 2 * MARGIN, 16, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawString(MARGIN + sum(cw[:i]) + 6, y + 2, h)
    y -= 16
    c.setFont("Helvetica", 10)
    c.setStrokeColor(MID_GRAY)
    for _ in range(5):
        c.line(MARGIN, y, W - MARGIN, y)
        for i in range(1, 4):
            c.line(MARGIN + sum(cw[:i]), y, MARGIN + sum(cw[:i]), y + 22)
        y -= 22

    y -= 16
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Supplements")
    y -= 18
    c.setFillColor(SOFT)
    c.rect(MARGIN, y - 2, W - 2 * MARGIN, 16, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    sup_h = ["Supplement", "Dose", "Times / day", "Started"]
    for i, h in enumerate(sup_h):
        c.drawString(MARGIN + sum(cw[:i]) + 6, y + 2, h)
    y -= 16
    c.setFont("Helvetica", 10)
    for _ in range(8):
        c.line(MARGIN, y, W - MARGIN, y)
        for i in range(1, 4):
            c.line(MARGIN + sum(cw[:i]), y, MARGIN + sum(cw[:i]), y + 22)
        y -= 22

    page_break(c)


def draw_daily_log(c, week, day):
    top = H - MARGIN
    # Header banner
    c.setFillColor(ACCENT)
    c.rect(MARGIN, top - 28, W - 2 * MARGIN, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 8, top - 20, f"Week {week}  |  Day {day}")
    c.drawRightString(W - MARGIN - 8, top - 20, "Date: ____/____/________")

    y = top - 50

    # Cycle / period row
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Cycle Day:  _______")
    c.drawString(MARGIN + 150, y, "Bleeding:  None / Spot / Light / Med / Heavy")
    y -= 22

    # Symptom rating table (0-5 scale)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Symptoms today  (circle 0 = none, 5 = severe)")
    y -= 14

    symptoms = [
        "Hot flashes (count: ____)",
        "Night sweats",
        "Sleep quality (5 = great)",
        "Energy (5 = high)",
        "Mood / anxiety",
        "Brain fog",
        "Joint / muscle pain",
        "Headache",
        "Bloating",
        "Libido (5 = high)",
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
            # 0..5 circles
            c.setFont("Helvetica", 9)
            for n in range(6):
                cx = col_x[col_idx] + col_w - 90 + n * 14
                c.circle(cx, cy_row - 4, 5, fill=0, stroke=1)
                c.drawCentredString(cx, cy_row - 6, str(n))
            c.setFont("Helvetica", 10)
    y -= half * row_h + 6

    # Other symptoms
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Other Symptoms:")
    c.setStrokeColor(MID_GRAY)
    c.line(MARGIN + 110, y - 2, W - MARGIN, y - 2)
    y -= 22

    # Lifestyle row
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Water:  ___ glasses")
    c.drawString(MARGIN + 160, y, "Caffeine:  ___")
    c.drawString(MARGIN + 280, y, "Alcohol:  ___")
    c.drawString(MARGIN + 400, y, "Exercise (min):  ___")
    y -= 22

    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Sleep last night (hrs):  ___")
    c.drawString(MARGIN + 200, y, "Woke up in the night:  Y / N   (count: ____)")
    y -= 22

    # HRT / meds taken today
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "HRT / Meds / Supplements taken today:")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    # Triggers / notes
    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Possible triggers (food / stress / heat / activity):")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Notes / How I felt today:")
    y -= 6
    for _ in range(3):
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
        "Hot flashes per day:",
        "Sleep hours per night:",
        "Mood (0-5 avg):",
        "Energy (0-5 avg):",
        "Days I exercised:",
        "Days I drank alcohol:",
    ]
    c.setFont("Helvetica", 11)
    for a in avgs:
        c.setFillColor(DARK)
        c.drawString(MARGIN + 14, y, a)
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN + 220, y - 2, MARGIN + 360, y - 2)
        y -= 24

    # Trend chart
    y -= 6
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Hot Flash Count - Daily Trend")
    y -= 8
    gh = 150
    c.setFillColor(SOFT)
    c.setStrokeColor(MID_GRAY)
    c.rect(MARGIN, y - gh, W - 2 * MARGIN, gh, fill=1, stroke=1)
    c.setFont("Helvetica", 8)
    c.setFillColor(DARK)
    for val in [0, 5, 10, 15, 20]:
        yy = y - gh + val * gh / 20
        c.drawRightString(MARGIN - 4, yy - 3, str(val))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    step = (W - 2 * MARGIN) / 7
    for i, d in enumerate(days):
        c.drawCentredString(MARGIN + step * i + step / 2, y - gh - 14, d)

    # Wins / what helped
    y -= gh + 36
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "What helped this week:")
    y -= 6
    for _ in range(3):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "What made symptoms worse:")
    y -= 6
    for _ in range(3):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    page_break(c)


def draw_doctor_visit_prep(c, month):
    top = H - MARGIN
    c.setFillColor(DARK)
    c.rect(MARGIN, top - 36, W - 2 * MARGIN, 36, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, top - 24, f"Doctor Visit Prep  -  Month {month}")

    y = top - 60
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, f"Appointment date:  ____ / ____ / ________     Provider: __________________________")
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
    c.drawString(MARGIN, y, "Cycle changes since last visit")
    y -= 6
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "HRT / supplement changes & how I feel on them")
    y -= 6
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Questions to ask my doctor")
    y -= 6
    for _ in range(5):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Tests / labs requested today")
    y -= 6
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Plan / next steps")
    y -= 6
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    page_break(c)


def draw_closing(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "You Did It")

    y = H - 1.8 * inch
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    msg = [
        "Fourteen weeks of tracking is real, valuable data — about you, by you.",
        "",
        "Look back through the pages. What patterns surprised you? Which",
        "weeks felt strongest? Which interventions helped most?",
        "",
        "Bring this book to your next appointment. You now have evidence,",
        "not guesswork, to guide your next steps.",
    ]
    for line in msg:
        c.drawCentredString(W / 2, y, line)
        y -= 18

    page_break(c)


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Perimenopause Symptom Tracker")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_personal_info(c)
    draw_how_to_use(c)
    draw_symptom_reference(c)
    draw_hrt_reference(c)

    # 14 weeks: 7 daily + 1 weekly = 8 pages * 14 = 112
    # monthly doctor prep every ~5 weeks (3 total)
    monthly_after_weeks = {5, 10, 14}
    month_n = 0
    for week in range(1, WEEKS + 1):
        for day in range(1, 8):
            draw_daily_log(c, week, day)
        draw_weekly_review(c, week)
        if week in monthly_after_weeks:
            month_n += 1
            draw_doctor_visit_prep(c, month_n)

    draw_closing(c)
    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
