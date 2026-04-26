"""
Caregiver Daily Log Book
KDP: 8.5 x 11 inch, 120 pages, cream interior
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "caregiver-daily-log.pdf")

# Colors
C_SAGE = HexColor("#7A9E7E")
C_SAGE_LIGHT = HexColor("#C8DEC9")
C_SAGE_PALE = HexColor("#EDF5EE")
C_CREAM = HexColor("#FEFDF8")
C_WARM_GRAY = HexColor("#6B6B6B")
C_DARK = HexColor("#2D2D2D")
C_LINE = HexColor("#C8C8C8")
C_SECTION_BG = HexColor("#F0F7F0")

W, H = letter  # 8.5 x 11 inches
MARGIN = 0.75 * inch
INNER_W = W - 2 * MARGIN

def draw_page_border(c, page_num):
    """연한 테두리 + 페이지 번호"""
    c.setStrokeColor(C_SAGE_LIGHT)
    c.setLineWidth(1)
    c.rect(MARGIN - 0.1*inch, MARGIN - 0.25*inch,
           INNER_W + 0.2*inch, H - 2*MARGIN + 0.35*inch)
    c.setFont("Helvetica", 8)
    c.setFillColor(C_WARM_GRAY)
    c.drawCentredString(W/2, 0.45*inch, str(page_num))


def draw_cover(c):
    # Background
    c.setFillColor(C_SAGE)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Top decorative band
    c.setFillColor(HexColor("#5C7D60"))
    c.rect(0, H - 1.8*inch, W, 1.8*inch, fill=1, stroke=0)

    # Bottom band
    c.setFillColor(HexColor("#5C7D60"))
    c.rect(0, 0, W, 1.2*inch, fill=1, stroke=0)

    # White center card
    c.setFillColor(white)
    c.roundRect(MARGIN + 0.2*inch, 2.5*inch,
                INNER_W - 0.4*inch, 5.2*inch, 12, fill=1, stroke=0)

    # Heart/care icon (simple)
    c.setFillColor(C_SAGE)
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(W/2, H - 1.1*inch, "♥")

    # Title
    c.setFillColor(C_DARK)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W/2, 7.1*inch, "Caregiver")
    c.drawCentredString(W/2, 6.55*inch, "Daily Log Book")

    # Divider line
    c.setStrokeColor(C_SAGE)
    c.setLineWidth(2)
    c.line(MARGIN + 1.2*inch, 6.35*inch, W - MARGIN - 1.2*inch, 6.35*inch)

    # Subtitle
    c.setFillColor(C_WARM_GRAY)
    c.setFont("Helvetica", 13)
    c.drawCentredString(W/2, 6.1*inch, "Essential Care Tracker for Family Caregivers")

    # Feature list
    features = [
        "✓  Daily Care Records",
        "✓  Medication Tracker",
        "✓  Appointment Log",
        "✓  Weekly Summaries",
        "✓  Emergency Contacts",
    ]
    c.setFont("Helvetica", 11)
    c.setFillColor(C_WARM_GRAY)
    y = 5.5*inch
    for f in features:
        c.drawCentredString(W/2, y, f)
        y -= 0.32*inch

    # Page count badge
    c.setFillColor(C_SAGE_LIGHT)
    c.roundRect(W/2 - 0.8*inch, 2.65*inch, 1.6*inch, 0.45*inch, 8, fill=1, stroke=0)
    c.setFillColor(C_DARK)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W/2, 2.83*inch, "120 Pages")

    # Bottom tagline
    c.setFillColor(white)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W/2, 0.6*inch, "Caring with Compassion, Organized with Purpose")


def draw_intro(c, page_num):
    draw_page_border(c, page_num)

    y = H - MARGIN - 0.2*inch

    # Header
    c.setFillColor(C_SAGE)
    c.rect(MARGIN, y - 0.45*inch, INNER_W, 0.45*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, y - 0.3*inch, "Welcome, Caregiver")
    y -= 0.7*inch

    paras = [
        "Caring for a loved one is one of the most meaningful — and demanding — roles a person can take on. "
        "Whether you are a family caregiver, home health aide, or supporting a parent or spouse, staying "
        "organized is essential for providing the best possible care.",
        "",
        "This Caregiver Daily Log Book gives you a simple, structured system to:",
        "",
        "  •  Track daily activities, meals, and personal care",
        "  •  Monitor medications and vital signs",
        "  •  Record appointments and follow-up notes",
        "  •  Summarize weekly progress at a glance",
        "  •  Keep emergency contacts and key information handy",
        "",
        "Consistent documentation helps you spot changes in health early, communicate clearly with "
        "doctors, and share care duties with other family members — reducing stress for everyone.",
        "",
        "How to Use This Book:",
        "",
        "  1.  Start a new Daily Log page each morning.",
        "  2.  Fill in vitals and medications as administered.",
        "  3.  Note any changes in behavior, appetite, or mood.",
        "  4.  Complete the Weekly Summary every Sunday.",
        "  5.  Update Emergency Contacts & Medication List as needed.",
        "",
        "You are doing important work. This book is here to support you.",
    ]

    c.setFont("Helvetica", 10.5)
    c.setFillColor(C_DARK)
    for para in paras:
        if para == "How to Use This Book:" or para == "Caring for a loved one is one of the most meaningful — and demanding — roles a person can take on. " \
        "Whether you are a family caregiver, home health aide, or supporting a parent or spouse, staying " \
        "organized is essential for providing the best possible care.":
            pass
        if para.startswith("How to Use") or para.startswith("  1.") or para.startswith("  2.") \
                or para.startswith("  3.") or para.startswith("  4.") or para.startswith("  5."):
            if para.startswith("How to Use"):
                c.setFont("Helvetica-Bold", 10.5)
            else:
                c.setFont("Helvetica", 10.5)
        else:
            c.setFont("Helvetica", 10.5)

        if para == "":
            y -= 0.15*inch
            continue

        # Word wrap
        words = para.split()
        line = ""
        for word in words:
            test = line + (" " if line else "") + word
            if c.stringWidth(test, "Helvetica", 10.5) > INNER_W - 0.1*inch:
                c.drawString(MARGIN + 0.05*inch, y, line)
                y -= 0.22*inch
                line = word
            else:
                line = test
        if line:
            c.drawString(MARGIN + 0.05*inch, y, line)
            y -= 0.22*inch


def draw_how_to_use(c, page_num):
    """CARE RECIPIENT INFO page"""
    draw_page_border(c, page_num)

    y = H - MARGIN - 0.2*inch
    c.setFillColor(C_SAGE)
    c.rect(MARGIN, y - 0.45*inch, INNER_W, 0.45*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, y - 0.3*inch, "Care Recipient Information")
    y -= 0.75*inch

    def field_row(label, y_pos, width=INNER_W):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(C_WARM_GRAY)
        c.drawString(MARGIN, y_pos + 0.05*inch, label)
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.7)
        c.line(MARGIN, y_pos - 0.02*inch, MARGIN + width, y_pos - 0.02*inch)
        return y_pos - 0.42*inch

    def section_header(label, y_pos):
        c.setFillColor(C_SAGE_LIGHT)
        c.rect(MARGIN, y_pos - 0.28*inch, INNER_W, 0.3*inch, fill=1, stroke=0)
        c.setFillColor(C_DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN + 0.1*inch, y_pos - 0.15*inch, label)
        return y_pos - 0.52*inch

    y = section_header("Personal Information", y)
    y = field_row("Full Name:", y)
    y = field_row("Date of Birth:", y)
    y = field_row("Primary Diagnosis / Condition:", y)
    y = field_row("Allergies:", y)
    y -= 0.1*inch

    y = section_header("Primary Care Provider", y)
    y = field_row("Doctor Name:", y)
    y = field_row("Clinic / Hospital:", y)
    y = field_row("Phone Number:", y)
    y -= 0.1*inch

    y = section_header("Insurance Information", y)
    y = field_row("Insurance Provider:", y)
    y = field_row("Policy Number:", y)
    y = field_row("Group Number:", y)
    y -= 0.1*inch

    y = section_header("Emergency Contact", y)
    y = field_row("Name & Relationship:", y)
    y = field_row("Phone:", y)


def draw_emergency_contacts(c, page_num):
    draw_page_border(c, page_num)

    y = H - MARGIN - 0.2*inch
    c.setFillColor(HexColor("#C0392B"))
    c.rect(MARGIN, y - 0.45*inch, INNER_W, 0.45*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, y - 0.3*inch, "Emergency Contacts & Key Numbers")
    y -= 0.75*inch

    cols = [
        ("Name / Role", 0), ("Phone Number", 2.2*inch), ("Notes", 4.4*inch)
    ]
    col_widths = [2.1*inch, 2.1*inch, INNER_W - 4.4*inch]

    # Table header
    c.setFillColor(C_SAGE_LIGHT)
    c.rect(MARGIN, y - 0.28*inch, INNER_W, 0.3*inch, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(C_DARK)
    for label, offset in cols:
        c.drawString(MARGIN + offset + 0.05*inch, y - 0.15*inch, label)
    y -= 0.38*inch

    # Rows
    for i in range(14):
        bg = C_CREAM if i % 2 == 0 else white
        c.setFillColor(bg)
        c.rect(MARGIN, y - 0.28*inch, INNER_W, 0.3*inch, fill=1, stroke=0)
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.5)
        c.line(MARGIN, y - 0.28*inch, MARGIN + INNER_W, y - 0.28*inch)
        # column dividers
        c.line(MARGIN + 2.2*inch, y + 0.02*inch, MARGIN + 2.2*inch, y - 0.28*inch)
        c.line(MARGIN + 4.4*inch, y + 0.02*inch, MARGIN + 4.4*inch, y - 0.28*inch)
        y -= 0.32*inch


def draw_medication_list(c, page_num):
    draw_page_border(c, page_num)

    y = H - MARGIN - 0.2*inch
    c.setFillColor(HexColor("#2980B9"))
    c.rect(MARGIN, y - 0.45*inch, INNER_W, 0.45*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, y - 0.3*inch, "Medication List")
    y -= 0.7*inch

    headers = [("Medication Name", 0, 1.9*inch),
               ("Dosage", 1.95*inch, 0.85*inch),
               ("Frequency", 2.85*inch, 0.85*inch),
               ("Purpose", 3.75*inch, 1.1*inch),
               ("Prescribing Dr.", 4.9*inch, INNER_W - 4.9*inch)]

    # Header row
    c.setFillColor(HexColor("#2980B9"))
    c.rect(MARGIN, y - 0.28*inch, INNER_W, 0.3*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    for label, offset, _ in headers:
        c.drawString(MARGIN + offset + 0.04*inch, y - 0.16*inch, label)
    y -= 0.38*inch

    def dividers(y_top, y_bot):
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.4)
        for _, offset, _ in headers[1:]:
            c.line(MARGIN + offset, y_top, MARGIN + offset, y_bot)

    for i in range(16):
        bg = C_CREAM if i % 2 == 0 else white
        c.setFillColor(bg)
        row_h = 0.38*inch
        c.rect(MARGIN, y - row_h, INNER_W, row_h, fill=1, stroke=0)
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.5)
        c.line(MARGIN, y - row_h, MARGIN + INNER_W, y - row_h)
        dividers(y, y - row_h)
        y -= row_h


def draw_daily_log(c, page_num, day_num):
    draw_page_border(c, page_num)

    y = H - MARGIN - 0.2*inch

    # Header with day number
    c.setFillColor(C_SAGE)
    c.rect(MARGIN, y - 0.45*inch, INNER_W, 0.45*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 0.15*inch, y - 0.3*inch, f"Daily Care Log")
    c.setFont("Helvetica", 10)
    c.drawRightString(MARGIN + INNER_W - 0.1*inch, y - 0.3*inch, f"Day ______  Date: _____ / _____ / _______")
    y -= 0.65*inch

    def mini_header(label, color=C_SAGE_LIGHT):
        nonlocal y
        c.setFillColor(color)
        c.rect(MARGIN, y - 0.25*inch, INNER_W, 0.26*inch, fill=1, stroke=0)
        c.setFillColor(C_DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 0.1*inch, y - 0.16*inch, label)
        y -= 0.38*inch

    def line_fields(labels, y_pos, num_lines=1):
        for label in labels:
            c.setFont("Helvetica", 8.5)
            c.setFillColor(C_WARM_GRAY)
            c.drawString(MARGIN + 0.05*inch, y_pos + 0.03*inch, label)
            label_w = c.stringWidth(label, "Helvetica", 8.5) + 0.1*inch
            c.setStrokeColor(C_LINE)
            c.setLineWidth(0.6)
            c.line(MARGIN + label_w, y_pos - 0.02*inch,
                   MARGIN + INNER_W, y_pos - 0.02*inch)
            y_pos -= 0.3*inch
        return y_pos

    # ── VITALS ──────────────────────────────────────────
    mini_header("▸  Vitals")
    # 2-column vitals
    half = INNER_W / 2 - 0.1*inch
    vitals_left = [("Blood Pressure:", 0), ("Heart Rate:", 0),  ("Temperature:", 0)]
    vitals_right = [("Blood Sugar:", 0), ("O2 Saturation:", 0), ("Weight:", 0)]

    y_vitals = y
    for label, _ in vitals_left:
        c.setFont("Helvetica", 8.5)
        c.setFillColor(C_WARM_GRAY)
        lw = c.stringWidth(label, "Helvetica", 8.5) + 0.1*inch
        c.drawString(MARGIN + 0.05*inch, y_vitals + 0.03*inch, label)
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.6)
        c.line(MARGIN + lw, y_vitals - 0.02*inch, MARGIN + half, y_vitals - 0.02*inch)
        y_vitals -= 0.3*inch
    left_end = y_vitals

    y_vitals = y
    for label, _ in vitals_right:
        c.setFont("Helvetica", 8.5)
        c.setFillColor(C_WARM_GRAY)
        lw = c.stringWidth(label, "Helvetica", 8.5) + 0.1*inch
        x0 = MARGIN + INNER_W / 2 + 0.1*inch
        c.drawString(x0, y_vitals + 0.03*inch, label)
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.6)
        c.line(x0 + lw, y_vitals - 0.02*inch, MARGIN + INNER_W, y_vitals - 0.02*inch)
        y_vitals -= 0.3*inch
    y = min(left_end, y_vitals) - 0.05*inch

    # ── MEDICATIONS GIVEN ───────────────────────────────
    mini_header("▸  Medications Given Today")
    # Small table
    med_cols = [("Medication", 0, 1.8*inch), ("Time", 1.85*inch, 0.7*inch),
                ("Dose", 2.6*inch, 0.7*inch), ("Given By", 3.35*inch, 0.9*inch),
                ("Notes", 4.3*inch, INNER_W - 4.3*inch)]
    # subheader
    c.setFillColor(HexColor("#D5E8D6"))
    c.rect(MARGIN, y - 0.22*inch, INNER_W, 0.23*inch, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(C_DARK)
    for label, offset, _ in med_cols:
        c.drawString(MARGIN + offset + 0.03*inch, y - 0.14*inch, label)
    y -= 0.3*inch
    for i in range(5):
        bg = C_CREAM if i % 2 == 0 else white
        c.setFillColor(bg)
        c.rect(MARGIN, y - 0.26*inch, INNER_W, 0.27*inch, fill=1, stroke=0)
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.4)
        c.line(MARGIN, y - 0.26*inch, MARGIN + INNER_W, y - 0.26*inch)
        for _, offset, _ in med_cols[1:]:
            c.line(MARGIN + offset, y + 0.01*inch, MARGIN + offset, y - 0.26*inch)
        y -= 0.27*inch
    y -= 0.05*inch

    # ── MEALS & FLUIDS ──────────────────────────────────
    mini_header("▸  Meals & Fluid Intake")
    meal_y = y
    c.setFont("Helvetica", 8.5)
    c.setFillColor(C_WARM_GRAY)
    meals = ["Breakfast:", "Lunch:", "Dinner:", "Snacks/Other:"]
    for meal in meals:
        c.drawString(MARGIN + 0.05*inch, meal_y + 0.03*inch, meal)
        mw = c.stringWidth(meal, "Helvetica", 8.5) + 0.1*inch
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.6)
        c.line(MARGIN + mw, meal_y - 0.02*inch, MARGIN + INNER_W/2 - 0.1*inch, meal_y - 0.02*inch)
        meal_y -= 0.28*inch
    # Fluid intake on the right
    fluid_y = y
    c.setFont("Helvetica", 8.5)
    c.setFillColor(C_WARM_GRAY)
    fluids = ["Total Fluids (oz):", "Water:", "Other Fluids:", "Appetite (1-5):"]
    x0 = MARGIN + INNER_W / 2 + 0.05*inch
    for fluid in fluids:
        c.drawString(x0, fluid_y + 0.03*inch, fluid)
        fw = c.stringWidth(fluid, "Helvetica", 8.5) + 0.1*inch
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.6)
        c.line(x0 + fw, fluid_y - 0.02*inch, MARGIN + INNER_W, fluid_y - 0.02*inch)
        fluid_y -= 0.28*inch
    y = min(meal_y, fluid_y) - 0.05*inch

    # ── MOOD & BEHAVIOR ─────────────────────────────────
    mini_header("▸  Mood & Behavior")
    mood_y = y
    c.setFont("Helvetica", 8.5)
    c.setFillColor(C_WARM_GRAY)
    c.drawString(MARGIN + 0.05*inch, mood_y + 0.03*inch, "Overall Mood:")
    c.drawString(MARGIN + 1.4*inch, mood_y + 0.03*inch, "☐ Happy  ☐ Calm  ☐ Confused  ☐ Agitated  ☐ Sad  ☐ Other: ___________")
    mood_y -= 0.28*inch
    c.drawString(MARGIN + 0.05*inch, mood_y + 0.03*inch, "Sleep Last Night:")
    c.drawString(MARGIN + 1.4*inch, mood_y + 0.03*inch, "☐ Good  ☐ Fair  ☐ Poor     Hours: _______  Notes: ___________________")
    mood_y -= 0.28*inch
    c.drawString(MARGIN + 0.05*inch, mood_y + 0.03*inch, "Pain Level (0-10):")
    c.drawString(MARGIN + 1.4*inch, mood_y + 0.03*inch, "_______    Location: _______________________________________________")
    y = mood_y - 0.35*inch

    # ── NOTES ───────────────────────────────────────────
    mini_header("▸  Notes / Observations")
    c.setStrokeColor(C_LINE)
    c.setLineWidth(0.6)
    note_lines = 4
    for _ in range(note_lines):
        c.line(MARGIN, y - 0.02*inch, MARGIN + INNER_W, y - 0.02*inch)
        y -= 0.28*inch


def draw_weekly_summary(c, page_num, week_num):
    draw_page_border(c, page_num)

    y = H - MARGIN - 0.2*inch

    c.setFillColor(HexColor("#6C5B7B"))
    c.rect(MARGIN, y - 0.45*inch, INNER_W, 0.45*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN + 0.15*inch, y - 0.3*inch, f"Weekly Summary  —  Week {week_num}")
    c.setFont("Helvetica", 10)
    c.drawRightString(MARGIN + INNER_W - 0.1*inch, y - 0.3*inch,
                      "Dates: _______ / _______ to _______ / _______")
    y -= 0.7*inch

    def sec(label):
        nonlocal y
        c.setFillColor(HexColor("#E8E0EF"))
        c.rect(MARGIN, y - 0.25*inch, INNER_W, 0.27*inch, fill=1, stroke=0)
        c.setFillColor(C_DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 0.1*inch, y - 0.16*inch, label)
        y -= 0.38*inch

    def lined(n):
        nonlocal y
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.6)
        for _ in range(n):
            c.line(MARGIN, y - 0.02*inch, MARGIN + INNER_W, y - 0.02*inch)
            y -= 0.28*inch
        y -= 0.05*inch

    def checkbox_row(items):
        nonlocal y
        c.setFont("Helvetica", 9)
        c.setFillColor(C_DARK)
        x = MARGIN + 0.05*inch
        for item in items:
            c.drawString(x, y, f"☐  {item}")
            x += (INNER_W / len(items))
        y -= 0.3*inch

    # Health overview — mini table (vitals averages)
    sec("Health Overview (Averages / Notable Changes)")
    headers = ["Vital", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    col_w = INNER_W / len(headers)
    c.setFillColor(HexColor("#D5CAE5"))
    c.rect(MARGIN, y - 0.24*inch, INNER_W, 0.25*inch, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(C_DARK)
    for i, h in enumerate(headers):
        c.drawCentredString(MARGIN + (i + 0.5) * col_w, y - 0.14*inch, h)
    y -= 0.33*inch

    vital_rows = ["Blood Pressure", "Heart Rate", "Blood Sugar", "Temperature"]
    for j, vr in enumerate(vital_rows):
        bg = C_CREAM if j % 2 == 0 else white
        c.setFillColor(bg)
        c.rect(MARGIN, y - 0.26*inch, INNER_W, 0.27*inch, fill=1, stroke=0)
        c.setFont("Helvetica", 8)
        c.setFillColor(C_DARK)
        c.drawString(MARGIN + 0.05*inch, y - 0.16*inch, vr)
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.4)
        c.line(MARGIN, y - 0.26*inch, MARGIN + INNER_W, y - 0.26*inch)
        for k in range(1, len(headers)):
            c.line(MARGIN + k * col_w, y + 0.01*inch, MARGIN + k * col_w, y - 0.26*inch)
        y -= 0.27*inch
    y -= 0.1*inch

    sec("Overall Progress & Observations")
    lined(3)

    sec("Concerns / Issues to Discuss with Doctor")
    lined(3)

    sec("Goals for Next Week")
    lined(2)

    sec("Weekly Checklist")
    checkbox_row(["Scheduled all appointments", "Refilled medications", "Contacted primary care", "Reviewed care plan"])
    y -= 0.05*inch
    checkbox_row(["Updated emergency contacts", "Organized medical records", "Self-care for caregiver", "Family update shared"])


def draw_appointment_log(c, page_num):
    draw_page_border(c, page_num)
    y = H - MARGIN - 0.2*inch

    c.setFillColor(HexColor("#E67E22"))
    c.rect(MARGIN, y - 0.45*inch, INNER_W, 0.45*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, y - 0.3*inch, "Appointment Log")
    y -= 0.7*inch

    headers = [("Date", 0, 0.8*inch), ("Provider / Specialist", 0.85*inch, 1.5*inch),
               ("Purpose", 2.4*inch, 1.1*inch), ("Outcome / Notes", 3.55*inch, INNER_W - 3.55*inch)]

    c.setFillColor(HexColor("#F5CBA7"))
    c.rect(MARGIN, y - 0.28*inch, INNER_W, 0.3*inch, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(C_DARK)
    for label, offset, _ in headers:
        c.drawString(MARGIN + offset + 0.04*inch, y - 0.16*inch, label)
    y -= 0.36*inch

    for i in range(22):
        bg = C_CREAM if i % 2 == 0 else white
        c.setFillColor(bg)
        row_h = 0.38*inch
        c.rect(MARGIN, y - row_h, INNER_W, row_h, fill=1, stroke=0)
        c.setStrokeColor(C_LINE)
        c.setLineWidth(0.5)
        c.line(MARGIN, y - row_h, MARGIN + INNER_W, y - row_h)
        for _, offset, _ in headers[1:]:
            c.line(MARGIN + offset, y + 0.02*inch, MARGIN + offset, y - row_h)
        y -= row_h


def draw_notes_page(c, page_num, title="General Notes"):
    draw_page_border(c, page_num)
    y = H - MARGIN - 0.2*inch

    c.setFillColor(C_SAGE)
    c.rect(MARGIN, y - 0.45*inch, INNER_W, 0.45*inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, y - 0.3*inch, title)
    y -= 0.7*inch

    c.setStrokeColor(C_LINE)
    c.setLineWidth(0.6)
    while y > MARGIN + 0.3*inch:
        c.line(MARGIN, y, MARGIN + INNER_W, y)
        y -= 0.32*inch


def generate():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    page_num = 1

    # Cover
    draw_cover(c)
    c.showPage()
    page_num += 1

    # Intro
    draw_intro(c, page_num)
    c.showPage()
    page_num += 1

    # Care Recipient Info
    draw_how_to_use(c, page_num)
    c.showPage()
    page_num += 1

    # Emergency Contacts
    draw_emergency_contacts(c, page_num)
    c.showPage()
    page_num += 1

    # Medication List (2 pages)
    for _ in range(2):
        draw_medication_list(c, page_num)
        c.showPage()
        page_num += 1

    # Appointment Log
    draw_appointment_log(c, page_num)
    c.showPage()
    page_num += 1

    # Daily Logs + Weekly Summaries
    # 4 weeks = 28 days + 4 weekly summaries = 32 pages
    day_num = 1
    for week in range(1, 5):
        for d in range(7):
            draw_daily_log(c, page_num, day_num)
            c.showPage()
            page_num += 1
            day_num += 1
        draw_weekly_summary(c, page_num, week)
        c.showPage()
        page_num += 1

    # Extra daily logs (blank)
    for _ in range(70):
        draw_daily_log(c, page_num, day_num)
        c.showPage()
        page_num += 1
        day_num += 1

    # Notes pages
    for title in ["Medical Notes", "General Notes", "Important Reminders"]:
        draw_notes_page(c, page_num, title)
        c.showPage()
        page_num += 1

    c.save()
    print(f"Generated: {OUTPUT} ({page_num - 1} pages)")


if __name__ == "__main__":
    generate()
