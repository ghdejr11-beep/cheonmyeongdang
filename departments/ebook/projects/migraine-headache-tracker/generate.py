"""Migraine & Headache Tracker - 8.5x11, ~120 pages

For chronic migraine and headache sufferers (and the neurologists who treat them).
13 weeks of daily attack logs + weekly review + monthly Neurologist Visit Prep.

Designed to surface trigger patterns (food, sleep, weather, hormones, stress)
and give doctors hard data to refine treatment.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migraine_headache_tracker.pdf")

DARK = HexColor("#2D1B4E")        # deep indigo (neurology / calm)
ACCENT = HexColor("#6A4FBB")      # soft violet
SOFT = HexColor("#EDE7F6")        # pale lavender
MID_GRAY = HexColor("#CCCCCC")
LIGHT_GRAY = HexColor("#F5F5F5")
GREEN = HexColor("#2E7D32")
ORANGE = HexColor("#E65100")
RED = HexColor("#C62828")

MARGIN = 0.75 * inch
WEEKS = 13   # 13 weeks * (7 daily + 1 weekly) = 104 pages of logs
MONTHS = 3   # 3 monthly doctor-visit prep pages


def footer(c, title="Migraine & Headache Tracker | Deokgu Studio"):
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


def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(MARGIN, MARGIN, W - 2 * MARGIN, H - 2 * MARGIN, fill=1, stroke=0)
    c.setFillColor(SOFT)
    c.rect(MARGIN, H * 0.42, W - 2 * MARGIN, 4, fill=1, stroke=0)
    c.rect(MARGIN, H * 0.62, W - 2 * MARGIN, 4, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(W / 2, H * 0.55, "Migraine &")
    c.drawCentredString(W / 2, H * 0.55 - 40, "Headache Tracker")

    c.setFont("Helvetica", 13)
    c.drawCentredString(W / 2, H * 0.36, "Pain  |  Triggers  |  Medication  |  Sleep  |  Hormones")
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, H * 0.30, "A 13-Week Daily Journal with Neurologist Visit Prep")

    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.14, "Deokgu Studio")
    c.showPage()


def draw_personal_info(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "About Me")

    y = H - 1.7 * inch
    fields = [
        "Name:", "Date of Birth:", "Started This Journal:",
        "Headache History (years):", "Primary Diagnosis:",
        "Neurologist:", "Phone:", "Pharmacy:", "Emergency Contact:",
        "Preventive Medications:", "",
        "Acute / Rescue Medications:", "",
        "Known Triggers:", "",
        "Allergies / Sensitivities:", "",
        "Other Health Conditions:", "",
    ]
    for f in fields:
        underline_field(c, MARGIN, y, W - 2 * MARGIN - 130, label=f if f else None)
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
        "Migraine and headache patterns can take months to surface. Tracking them daily for 13 weeks gives you real evidence of what triggers attacks, what medication actually works, and which lifestyle factors matter.",
        "",
        "1. Each evening, fill in one DAILY page. Even on pain-free days, log sleep, stress, and any triggers you noticed.",
        "2. If you had an attack, rate pain 0 (none) - 10 (worst possible). Note location, type, duration, and what relieved it.",
        "3. At the end of each week, complete the WEEKLY REVIEW. Count attack days, average pain, and rescue meds used.",
        "4. Once a month, fill in the NEUROLOGIST VISIT PREP page before your appointment. Bring this book.",
        "5. Watch for MOH (medication-overuse headache): if you take acute meds more than 2 days per week, flag it for your doctor.",
        "",
        "This is a personal journal, not medical advice. Always discuss symptoms and treatment with a qualified healthcare provider.",
    ]
    for p in paragraphs:
        if p == "":
            y -= 10
            continue
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


def draw_trigger_reference(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "Common Migraine & Headache Triggers")

    y = H - 1.6 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Use these as labels in the 'Triggers' field of your daily log.")
    y -= 24

    cats = [
        ("Food / Drink", ["Aged cheese", "Red wine", "Cured meats", "Chocolate", "MSG", "Aspartame", "Citrus", "Caffeine withdrawal"]),
        ("Sleep", ["Too little sleep", "Too much sleep", "Disrupted sleep", "Jet lag", "Shift change"]),
        ("Hormonal", ["Menstrual cycle", "Ovulation", "Hormonal contraceptive", "HRT change", "Pregnancy", "Perimenopause"]),
        ("Environment", ["Bright lights", "Flickering screens", "Strong smells", "Smoke", "Perfume", "Loud noise"]),
        ("Weather", ["Barometric pressure drop", "Storm front", "High humidity", "Heat wave", "Cold snap"]),
        ("Stress", ["Acute stress", "Letdown (post-stress)", "Anxiety", "Crying spell", "Conflict"]),
        ("Physical", ["Skipped meal", "Dehydration", "Eye strain", "Neck tension", "Posture", "Exertion"]),
        ("Medical", ["Medication overuse", "Missed preventive dose", "New medication", "Infection / fever"]),
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
        # wrap if needed
        if c.stringWidth(text, "Helvetica", 10) > W - 2 * MARGIN - 12:
            mid = len(items) // 2
            c.drawString(MARGIN + 12, y, "  -  ".join(items[:mid]))
            y -= 14
            c.drawString(MARGIN + 12, y, "  -  ".join(items[mid:]))
        else:
            c.drawString(MARGIN + 12, y, text)
        y -= 18
    page_break(c)


def draw_medication_reference(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1 * inch, "My Medications")

    y = H - 1.7 * inch
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, y, "Record preventive and acute medications. Watch for medication-overuse headache (MOH).")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Preventive Medications (taken daily / scheduled)")
    y -= 18
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    headers = ["Drug / Brand", "Dose", "Schedule", "Started"]
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
    c.drawString(MARGIN, y, "Acute / Rescue Medications (taken during an attack)")
    y -= 18
    c.setFillColor(SOFT)
    c.rect(MARGIN, y - 2, W - 2 * MARGIN, 16, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    acute_h = ["Drug / Brand", "Dose", "Max per week", "Notes"]
    for i, h in enumerate(acute_h):
        c.drawString(MARGIN + sum(cw[:i]) + 6, y + 2, h)
    y -= 16
    c.setFont("Helvetica", 10)
    for _ in range(6):
        c.line(MARGIN, y, W - MARGIN, y)
        for i in range(1, 4):
            c.line(MARGIN + sum(cw[:i]), y, MARGIN + sum(cw[:i]), y + 22)
        y -= 22

    y -= 18
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "MOH alert:")
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN + 70, y, "Using triptans / NSAIDs more than 2 days/week can worsen headache. Track and discuss with your doctor.")

    page_break(c)


def draw_daily_log(c, week, day):
    top = H - MARGIN
    c.setFillColor(ACCENT)
    c.rect(MARGIN, top - 28, W - 2 * MARGIN, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 8, top - 20, f"Week {week}  |  Day {day}")
    c.drawRightString(W - MARGIN - 8, top - 20, "Date: ____/____/________")

    y = top - 50

    # Attack today?
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Headache today?   No  /  Yes")
    c.drawString(MARGIN + 230, y, "Started:  ____ : ____   Ended:  ____ : ____")
    y -= 22

    # Pain rating bar (0-10)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Peak pain  (circle 0 = none, 10 = worst)")
    y -= 16
    bar_w = (W - 2 * MARGIN) / 11
    for n in range(11):
        cx = MARGIN + n * bar_w + bar_w / 2
        c.circle(cx, y, 8, fill=0, stroke=1)
        c.setFont("Helvetica", 9)
        c.drawCentredString(cx, y - 3, str(n))
    y -= 28

    # Type & location
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Type:")
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN + 40, y, "Migraine  /  Tension  /  Cluster  /  Sinus  /  Other ____________")
    y -= 18
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Location:")
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN + 65, y, "L temple  /  R temple  /  Forehead  /  Behind eye  /  Crown  /  Back of head  /  Neck")
    y -= 18
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Aura:")
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN + 40, y, "None  /  Visual  /  Tingling  /  Speech  /  Other ___________________________")
    y -= 22

    # Associated symptoms checkboxes
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Associated symptoms (check all):")
    y -= 16
    syms = ["Nausea", "Vomiting", "Light sensitivity", "Sound sensitivity",
            "Smell sensitivity", "Dizziness", "Blurred vision", "Neck pain",
            "Allodynia (skin pain)", "Fatigue"]
    cols = 2
    col_w = (W - 2 * MARGIN) / cols
    for i, s in enumerate(syms):
        col = i % cols
        row = i // cols
        cx = MARGIN + col * col_w
        cy = y - row * 14
        c.rect(cx, cy - 4, 8, 8, fill=0, stroke=1)
        c.setFont("Helvetica", 10)
        c.drawString(cx + 14, cy - 3, s)
    y -= ((len(syms) + cols - 1) // cols) * 14 + 6

    # Triggers
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Possible triggers:")
    c.setStrokeColor(MID_GRAY)
    c.line(MARGIN + 110, y - 2, W - MARGIN, y - 2)
    y -= 22

    # Lifestyle row
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Sleep (hrs):  ___")
    c.drawString(MARGIN + 130, y, "Water (glasses):  ___")
    c.drawString(MARGIN + 290, y, "Caffeine:  ___")
    c.drawString(MARGIN + 410, y, "Stress (1-5):  ___")
    y -= 18
    c.drawString(MARGIN, y, "Meals on time:  Y / N")
    c.drawString(MARGIN + 150, y, "Exercise (min):  ___")
    c.drawString(MARGIN + 310, y, "Cycle day:  ___")
    y -= 22

    # Rescue meds
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Rescue medication taken (drug, dose, time, relief Y/N):")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    # Notes
    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Notes / what helped:")
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
    c.drawString(MARGIN, y, "This week's totals:")
    y -= 24
    avgs = [
        "Headache days (out of 7):",
        "Average peak pain (0-10):",
        "Days I took rescue meds:",
        "Days with aura:",
        "Average sleep (hrs):",
        "Days I exercised:",
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
    c.drawString(MARGIN, y, "Daily Pain Trend (0-10)")
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

    # Patterns
    y -= gh + 36
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Triggers I noticed this week:")
    y -= 6
    for _ in range(2):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 14
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, "What helped most:")
    y -= 6
    for _ in range(2):
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
    c.drawCentredString(W / 2, top - 24, f"Neurologist Visit Prep  -  Month {month}")

    y = top - 60
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, f"Appointment date:  ____ / ____ / ________     Provider: __________________________")
    y -= 26

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Headache summary since last visit")
    y -= 20
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawString(MARGIN + 14, y, "Total headache days:  _____      Severe (7+) days:  _____      Days disabled:  _____")
    y -= 18
    c.drawString(MARGIN + 14, y, "Avg pain:  _____      Rescue med doses (total):  _____      Aura episodes:  _____")
    y -= 24

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Top 3 triggers I identified")
    y -= 6
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    for i in range(1, 4):
        y -= 22
        c.drawString(MARGIN, y, f"{i}.")
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN + 18, y - 2, W - MARGIN, y - 2)

    y -= 22
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "How current medications are working")
    y -= 6
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Side effects to report")
    y -= 6
    for _ in range(3):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 18
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Questions to ask my neurologist")
    y -= 6
    for _ in range(4):
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
    c.drawCentredString(W / 2, H - 1 * inch, "Thirteen Weeks of Real Data")

    y = H - 1.8 * inch
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    msg = [
        "You now have a record most patients never bring to their neurologist.",
        "",
        "Look back through the pages. Which triggers showed up most often?",
        "Which weeks were worst, and what came before them? What pattern is",
        "your body trying to tell you?",
        "",
        "Bring this book to your next appointment. The conversation will be",
        "different — because for the first time, you have evidence.",
    ]
    for line in msg:
        c.drawCentredString(W / 2, y, line)
        y -= 18

    page_break(c)


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Migraine & Headache Tracker")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_personal_info(c)
    draw_how_to_use(c)
    draw_trigger_reference(c)
    draw_medication_reference(c)

    monthly_after_weeks = {5, 9, 13}
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
