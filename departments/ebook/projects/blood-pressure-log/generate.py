"""Blood Pressure Log Book - 8.5x11, 124 pages"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT

W, H = letter  # 8.5 x 11 inches
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blood_pressure_log_book.pdf")

DARK = HexColor("#2C3E50")
ACCENT = HexColor("#E74C3C")
LIGHT_GRAY = HexColor("#F5F5F5")
MID_GRAY = HexColor("#CCCCCC")
HEADER_BG = HexColor("#E74C3C")


def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    # Accent bar
    c.setFillColor(ACCENT)
    c.rect(0.8*inch, H * 0.45, W - 1.6*inch, 4, fill=1, stroke=0)
    c.rect(0.8*inch, H * 0.58, W - 1.6*inch, 4, fill=1, stroke=0)
    # Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(W / 2, H * 0.52, "Blood Pressure")
    c.drawCentredString(W / 2, H * 0.52 - 42, "Log Book")
    # Subtitle
    c.setFont("Helvetica", 14)
    c.drawCentredString(W / 2, H * 0.38, "Daily Morning & Evening Readings")
    c.drawCentredString(W / 2, H * 0.38 - 20, "Pulse Rate | Weekly Averages | Doctor Visits")
    # Author
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.12, "Deokgu Studio")
    c.showPage()


def draw_instructions_page(c):
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(DARK)
    c.drawCentredString(W / 2, H - 1.2 * inch, "How to Use This Book")
    y = H - 2 * inch
    c.setFont("Helvetica", 11)
    instructions = [
        "1. Record your blood pressure twice daily: morning and evening.",
        "2. Write the date and time of each measurement.",
        "3. Record Systolic (SYS), Diastolic (DIA), and Pulse values.",
        "4. Add any notes about medication, food, stress, or symptoms.",
        "5. At the end of each week, calculate your weekly averages.",
        "6. Bring this book to your doctor appointments.",
        "",
        "Blood Pressure Categories (AHA Guidelines):",
        "  Normal: Less than 120/80 mmHg",
        "  Elevated: 120-129 / Less than 80 mmHg",
        "  High Stage 1: 130-139 / 80-89 mmHg",
        "  High Stage 2: 140+ / 90+ mmHg",
        "  Crisis: Higher than 180/120 mmHg",
    ]
    for line in instructions:
        c.drawString(0.75 * inch, y, line)
        y -= 18
    c.showPage()


def draw_personal_info(c):
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(DARK)
    c.drawCentredString(W / 2, H - 1.2 * inch, "Personal Information")
    fields = [
        "Name:", "Date of Birth:", "Phone:", "Emergency Contact:",
        "Doctor Name:", "Doctor Phone:", "Pharmacy:", "Pharmacy Phone:",
        "Medications:", "", "", "",
        "Allergies:", "", "",
        "Notes:", "", "",
    ]
    y = H - 2 * inch
    c.setFont("Helvetica", 12)
    for field in fields:
        if field:
            c.setFillColor(DARK)
            c.drawString(0.75 * inch, y + 4, field)
            c.setStrokeColor(MID_GRAY)
            c.line(3 * inch, y, W - 0.75 * inch, y)
        y -= 28
    c.showPage()


def draw_daily_log_page(c, week_num, page_in_week):
    margin = 0.75 * inch
    top = H - margin
    # Header
    c.setFillColor(HEADER_BG)
    c.rect(margin, top - 30, W - 2 * margin, 30, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 8, top - 22, f"Week {week_num} - Page {page_in_week}")
    c.drawRightString(W - margin - 8, top - 22, "Date: ____/____/________")

    # Table header
    y = top - 50
    cols = [margin, margin + 70, margin + 155, margin + 240, margin + 325, margin + 410, margin + 495]
    headers = ["Time", "AM/PM", "SYS", "DIA", "Pulse", "Pos.", "Notes"]
    widths = [70, 85, 85, 85, 85, 85, W - 2 * margin - 495]

    c.setFillColor(DARK)
    c.rect(margin, y - 18, W - 2 * margin, 18, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawCentredString(cols[i] + widths[i] / 2, y - 14, h)

    # Morning section
    y -= 28
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 4, y, "MORNING")
    y -= 4

    c.setFont("Helvetica", 9)
    for row in range(4):
        y -= 22
        c.setStrokeColor(MID_GRAY)
        c.setFillColor(LIGHT_GRAY if row % 2 == 0 else white)
        c.rect(margin, y - 4, W - 2 * margin, 20, fill=1, stroke=0)
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y - 4, W - margin, y - 4)
        # Vertical lines
        for col_x in cols[1:]:
            c.line(col_x, y - 4, col_x, y + 16)

    # Evening section
    y -= 20
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 4, y, "EVENING")
    y -= 4

    for row in range(4):
        y -= 22
        c.setFillColor(LIGHT_GRAY if row % 2 == 0 else white)
        c.rect(margin, y - 4, W - 2 * margin, 20, fill=1, stroke=0)
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y - 4, W - margin, y - 4)
        for col_x in cols[1:]:
            c.line(col_x, y - 4, col_x, y + 16)

    # Notes section
    y -= 30
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 4, y, "Daily Notes & Observations:")
    y -= 8
    for _ in range(6):
        y -= 20
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    # Footer
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, margin - 10, "Blood Pressure Log Book | Deokgu Studio")

    c.showPage()


def draw_weekly_summary(c, week_num):
    margin = 0.75 * inch
    top = H - margin
    c.setFillColor(HEADER_BG)
    c.rect(margin, top - 35, W - 2 * margin, 35, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, top - 26, f"Week {week_num} Summary")

    y = top - 60
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Weekly Averages")
    y -= 30

    # Average table
    avg_labels = ["Morning Avg SYS:", "Morning Avg DIA:", "Morning Avg Pulse:",
                  "Evening Avg SYS:", "Evening Avg DIA:", "Evening Avg Pulse:"]
    c.setFont("Helvetica", 11)
    for label in avg_labels:
        c.drawString(margin + 20, y, label)
        c.setStrokeColor(MID_GRAY)
        c.line(margin + 200, y - 2, margin + 350, y - 2)
        y -= 26

    # Graph space
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK)
    c.drawString(margin, y, "Weekly Trend (Plot your readings)")
    y -= 10
    graph_h = 200
    c.setStrokeColor(MID_GRAY)
    c.setFillColor(LIGHT_GRAY)
    c.rect(margin, y - graph_h, W - 2 * margin, graph_h, fill=1, stroke=1)
    # Y axis labels
    c.setFont("Helvetica", 8)
    c.setFillColor(DARK)
    for val in [60, 80, 100, 120, 140, 160, 180]:
        yy = y - graph_h + (val - 50) * graph_h / 150
        if y - graph_h < yy < y:
            c.drawRightString(margin - 4, yy - 3, str(val))
            c.setStrokeColor(HexColor("#E0E0E0"))
            c.line(margin, yy, W - margin, yy)
    # X axis labels
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    step = (W - 2 * margin) / 7
    for i, day in enumerate(days):
        x = margin + step * i + step / 2
        c.drawCentredString(x, y - graph_h - 14, day)

    # Notes
    y -= graph_h + 40
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DARK)
    c.drawString(margin, y, "Weekly Notes:")
    y -= 8
    for _ in range(5):
        y -= 22
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    c.showPage()


def draw_doctor_visit_page(c, visit_num):
    margin = 0.75 * inch
    top = H - margin
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, top - 30, f"Doctor Visit Record #{visit_num}")

    y = top - 70
    fields = [
        "Date:", "Doctor:", "Location:",
        "Blood Pressure Reading:", "Weight:", "Heart Rate:",
        "Medications Changed:", "", "",
        "Doctor's Recommendations:", "", "", "",
        "Questions to Ask:", "", "", "",
        "Follow-up Date:", "Next Appointment:",
        "Notes:", "", "", "", "",
    ]
    c.setFont("Helvetica", 11)
    for field in fields:
        if field:
            c.setFillColor(DARK)
            c.drawString(margin, y + 4, field)
            c.setStrokeColor(MID_GRAY)
            c.line(margin + 180, y, W - margin, y)
        else:
            c.setStrokeColor(MID_GRAY)
            c.line(margin, y, W - margin, y)
        y -= 26
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Blood Pressure Log Book")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_instructions_page(c)
    draw_personal_info(c)

    # 15 weeks of daily logs (7 pages per week + 1 summary = 8 per week)
    # Actually, let's do 2 daily pages per week + 1 summary = ~3 pages per week
    # 15 weeks * 7 daily + 15 summaries = 105 + 15 = 120, plus front/back = 124
    for week in range(1, 16):
        for day in range(1, 8):
            draw_daily_log_page(c, week, day)
        draw_weekly_summary(c, week)

    # Doctor visit pages
    for v in range(1, 5):
        draw_doctor_visit_page(c, v)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
