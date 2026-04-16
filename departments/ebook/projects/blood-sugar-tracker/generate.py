"""Diabetic Blood Sugar Log Book - 8.5x11, 124 pages"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diabetic_blood_sugar_log.pdf")

DARK = HexColor("#1A237E")
ACCENT = HexColor("#0D47A1")
LIGHT_BLUE = HexColor("#E3F2FD")
MID_GRAY = HexColor("#CCCCCC")
LIGHT_GRAY = HexColor("#F5F5F5")
GREEN = HexColor("#2E7D32")
RED = HexColor("#C62828")


def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0.8*inch, H * 0.44, W - 1.6*inch, 6, fill=1, stroke=0)
    c.rect(0.8*inch, H * 0.60, W - 1.6*inch, 6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(W / 2, H * 0.54, "Diabetic Blood Sugar")
    c.drawCentredString(W / 2, H * 0.54 - 40, "Log Book")
    c.setFont("Helvetica", 14)
    c.drawCentredString(W / 2, H * 0.37, "Daily Glucose Tracking | Insulin Log | Meal Notes")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.12, "Deokgu Studio")
    c.showPage()


def draw_info_pages(c):
    margin = 0.75 * inch
    # Personal info
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(DARK)
    c.drawCentredString(W / 2, H - 1 * inch, "Personal Information")
    y = H - 1.8 * inch
    fields = ["Name:", "Date of Birth:", "Diabetes Type:", "Diagnosed Date:",
              "Doctor:", "Doctor Phone:", "Pharmacy:", "Emergency Contact:",
              "Current Medications:", "", "", "Allergies:", "", "Insurance Info:"]
    c.setFont("Helvetica", 11)
    for f in fields:
        if f:
            c.setFillColor(DARK)
            c.drawString(margin, y + 4, f)
            c.setStrokeColor(MID_GRAY)
            c.line(margin + 170, y, W - margin, y)
        else:
            c.setStrokeColor(MID_GRAY)
            c.line(margin, y, W - margin, y)
        y -= 28
    c.showPage()

    # Target ranges
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(DARK)
    c.drawCentredString(W / 2, H - 1 * inch, "My Target Ranges")
    y = H - 1.8 * inch
    targets = [
        ("Fasting / Before Meal:", "_____ - _____ mg/dL"),
        ("2 Hours After Meal:", "_____ - _____ mg/dL"),
        ("Bedtime:", "_____ - _____ mg/dL"),
        ("A1C Goal:", "_____ %"),
    ]
    c.setFont("Helvetica", 13)
    for label, val in targets:
        c.setFillColor(DARK)
        c.drawString(margin, y, label)
        c.setFillColor(ACCENT)
        c.drawString(margin + 250, y, val)
        y -= 35

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(DARK)
    c.drawString(margin, y, "Blood Sugar Reference Chart")
    y -= 25
    ref = [
        ("Normal (Fasting)", "70 - 100 mg/dL", GREEN),
        ("Pre-Diabetes (Fasting)", "100 - 125 mg/dL", HexColor("#FF8F00")),
        ("Diabetes (Fasting)", "126+ mg/dL", RED),
        ("Normal (After Meal)", "< 140 mg/dL", GREEN),
        ("Pre-Diabetes (After Meal)", "140 - 199 mg/dL", HexColor("#FF8F00")),
        ("Diabetes (After Meal)", "200+ mg/dL", RED),
    ]
    c.setFont("Helvetica", 11)
    for label, val, color in ref:
        c.setFillColor(color)
        c.rect(margin, y - 2, 8, 8, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.drawString(margin + 16, y, label)
        c.drawString(margin + 280, y, val)
        y -= 22
    c.showPage()


def draw_daily_log(c, week, day):
    margin = 0.75 * inch
    top = H - margin
    # Header
    c.setFillColor(ACCENT)
    c.rect(margin, top - 28, W - 2 * margin, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin + 8, top - 20, f"Week {week} | Day {day}")
    c.drawRightString(W - margin - 8, top - 20, "Date: ____/____/________")

    y = top - 48
    # Readings table
    times = [("Fasting / Before Breakfast", "After Breakfast"),
             ("Before Lunch", "After Lunch"),
             ("Before Dinner", "After Dinner"),
             ("Bedtime", "Other")]
    cols_x = [margin, margin + 160, margin + 250, margin + 340, margin + 430]
    col_headers = ["Time / Meal", "Blood Sugar\n(mg/dL)", "Insulin\nDose", "Carbs\n(g)", "Notes"]
    col_w = [160, 90, 90, 90, W - 2 * margin - 430]

    c.setFillColor(DARK)
    c.rect(margin, y - 16, W - 2 * margin, 16, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    for i, h in enumerate(col_headers):
        c.drawCentredString(cols_x[i] + col_w[i] / 2, y - 12, h.split("\n")[0])
    y -= 24

    c.setFont("Helvetica", 9)
    row_h = 24
    for pair in times:
        for label in pair:
            c.setFillColor(LIGHT_BLUE if times.index(pair) % 2 == 0 else LIGHT_GRAY)
            c.rect(margin, y - 6, W - 2 * margin, row_h, fill=1, stroke=0)
            c.setFillColor(DARK)
            c.drawString(margin + 4, y + 2, label)
            c.setStrokeColor(MID_GRAY)
            for cx in cols_x[1:]:
                c.line(cx, y - 6, cx, y - 6 + row_h)
            c.line(margin, y - 6, W - margin, y - 6)
            y -= row_h

    # Exercise
    y -= 16
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Exercise / Activity:")
    y -= 8
    c.setStrokeColor(MID_GRAY)
    ex_headers = ["Type", "Duration", "Intensity"]
    ex_x = [margin, margin + 200, margin + 340]
    ex_w = [200, 140, W - 2 * margin - 340]
    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(ex_headers):
        c.drawString(ex_x[i] + 4, y - 10, h)
    y -= 16
    c.setFont("Helvetica", 9)
    for _ in range(3):
        y -= 20
        c.line(margin, y, W - margin, y)
        for x in ex_x[1:]:
            c.line(x, y, x, y + 20)

    # Meals
    y -= 20
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Meal Notes:")
    y -= 6
    meals = ["Breakfast:", "Lunch:", "Dinner:", "Snacks:"]
    c.setFont("Helvetica", 9)
    for meal in meals:
        y -= 20
        c.setFillColor(DARK)
        c.drawString(margin + 4, y + 4, meal)
        c.setStrokeColor(MID_GRAY)
        c.line(margin + 80, y, W - margin, y)

    # Daily notes
    y -= 24
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "How I Feel Today:")
    y -= 6
    for _ in range(3):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, margin - 10, "Diabetic Blood Sugar Log Book | Deokgu Studio")
    c.showPage()


def draw_weekly_review(c, week):
    margin = 0.75 * inch
    top = H - margin
    c.setFillColor(ACCENT)
    c.rect(margin, top - 32, W - 2 * margin, 32, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, top - 24, f"Week {week} Review")

    y = top - 55
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Weekly Averages:")
    y -= 28
    avgs = ["Fasting Average:", "After Meal Average:", "Bedtime Average:",
            "Highest Reading:", "Lowest Reading:", "Total Insulin Used:"]
    c.setFont("Helvetica", 11)
    for a in avgs:
        c.setFillColor(DARK)
        c.drawString(margin + 20, y, a)
        c.setStrokeColor(MID_GRAY)
        c.line(margin + 220, y - 2, margin + 380, y - 2)
        y -= 26

    # Graph area
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK)
    c.drawString(margin, y, "Blood Sugar Trend (Plot your daily readings)")
    y -= 10
    gh = 180
    c.setFillColor(LIGHT_BLUE)
    c.setStrokeColor(MID_GRAY)
    c.rect(margin, y - gh, W - 2 * margin, gh, fill=1, stroke=1)
    c.setFont("Helvetica", 8)
    c.setFillColor(DARK)
    for val in [70, 100, 140, 180, 200, 250]:
        yy = y - gh + (val - 50) * gh / 250
        if y - gh < yy < y:
            c.drawRightString(margin - 4, yy - 3, str(val))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    step = (W - 2 * margin) / 7
    for i, d in enumerate(days):
        c.drawCentredString(margin + step * i + step / 2, y - gh - 14, d)

    # A1C
    y -= gh + 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "A1C Tracking:")
    y -= 26
    c.setFont("Helvetica", 11)
    c.drawString(margin + 20, y, "Last A1C: _______  Date: _______  Next Test: _______")

    # Reflection
    y -= 35
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Weekly Reflection:")
    y -= 6
    for _ in range(5):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Diabetic Blood Sugar Log Book")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_info_pages(c)

    # 16 weeks: 7 daily + 1 summary = 8 pages per week = 128
    # + title + 2 info = 131 total, trimmed to ~124
    for week in range(1, 16):
        for day in range(1, 8):
            draw_daily_log(c, week, day)
        draw_weekly_review(c, week)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
