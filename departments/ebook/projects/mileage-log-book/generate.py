"""Mileage Log Book for Taxes - 8.5x11, ~120 pages
Target: Self-employed, rideshare (Uber/Lyft/DoorDash), realtors, small business
Records vehicle business mileage for IRS tax deduction (Schedule C / Form 2106).
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter  # 8.5 x 11 inches
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mileage_log_book.pdf")

DARK = HexColor("#1F3A5F")
ACCENT = HexColor("#F39C12")
LIGHT_GRAY = HexColor("#F4F6F8")
MID_GRAY = HexColor("#BDC3C7")
HEADER_BG = HexColor("#1F3A5F")


def draw_title_page(c):
    margin = 0.8 * inch
    c.setFillColor(DARK)
    c.rect(margin, margin, W - 2 * margin, H - 2 * margin, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(margin, H * 0.46, W - 2 * margin, 4, fill=1, stroke=0)
    c.rect(margin, H * 0.60, W - 2 * margin, 4, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 38)
    c.drawCentredString(W / 2, H * 0.54, "Mileage Log Book")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H * 0.50, "for Taxes")

    c.setFont("Helvetica", 13)
    c.drawCentredString(W / 2, H * 0.40, "Vehicle Mileage Tracker for Self-Employed,")
    c.drawCentredString(W / 2, H * 0.40 - 18, "Rideshare Drivers, Realtors & Small Business")

    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, H * 0.30, "IRS Compliant | Date | Odometer | Purpose | Total Miles")

    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.13, "Deokgu Studio")
    c.showPage()


def draw_instructions_page(c):
    margin = 0.75 * inch
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1.2 * inch, "How to Use This Mileage Log")

    y = H - 1.9 * inch
    c.setFillColor(black)
    c.setFont("Helvetica", 11)
    instructions = [
        "1. Record EVERY business trip on the day you take it. The IRS requires",
        "   timely, contemporaneous records. Do not reconstruct from memory.",
        "2. For each trip, log: Date, Starting Odometer, Ending Odometer,",
        "   Total Miles, Destination, and Business Purpose.",
        "3. Keep this log in your vehicle so it is always within reach.",
        "4. Add up totals at the end of each month using the Monthly Summary page.",
        "5. At year-end, transfer your annual total to your tax return.",
        "",
        "What Counts as Business Mileage (IRS):",
        "  - Driving from one workplace to another",
        "  - Driving to meet clients or customers",
        "  - Driving to temporary work locations",
        "  - Driving for rideshare / delivery while online",
        "  - Driving to business-related conferences or training",
        "",
        "What Does NOT Count:",
        "  - Commuting from home to your regular workplace",
        "  - Personal errands and trips",
        "",
        "2026 Standard Mileage Rate (verify current rate with IRS):",
        "  - Business: 67.0 cents per mile (was 65.5 cents in 2025)",
        "  - Medical / Moving: 21 cents per mile",
        "  - Charitable: 14 cents per mile",
        "",
        "Tip: Take a photo of your odometer on January 1 and December 31",
        "each year. The IRS asks for total annual miles driven on your return.",
    ]
    for line in instructions:
        c.drawString(margin, y, line)
        y -= 16
    c.showPage()


def draw_vehicle_info_page(c):
    margin = 0.75 * inch
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, H - 1.2 * inch, "Vehicle & Owner Information")

    fields = [
        "Owner Name:",
        "Business Name:",
        "Business Tax ID / EIN:",
        "Phone:",
        "Email:",
        "",
        "Vehicle Make:",
        "Vehicle Model:",
        "Year:",
        "License Plate:",
        "VIN:",
        "Color:",
        "",
        "Date Vehicle Placed in Service:",
        "Odometer at Start of Year:",
        "Odometer at End of Year:",
        "",
        "Insurance Provider:",
        "Insurance Policy #:",
        "",
        "Notes:",
        "", "", "",
    ]
    y = H - 1.9 * inch
    c.setFillColor(black)
    c.setFont("Helvetica", 12)
    for field in fields:
        if field:
            c.setFillColor(DARK)
            c.drawString(margin, y + 4, field)
            c.setStrokeColor(MID_GRAY)
            c.line(margin + 2.3 * inch, y, W - margin, y)
        else:
            c.setStrokeColor(MID_GRAY)
            c.line(margin, y, W - margin, y)
        y -= 26
    c.showPage()


def draw_year_summary_page(c):
    margin = 0.75 * inch
    top = H - margin
    c.setFillColor(HEADER_BG)
    c.rect(margin, top - 35, W - 2 * margin, 35, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, top - 25, "Annual Mileage Summary")

    y = top - 70
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Year: __________")
    y -= 30

    c.setFont("Helvetica-Bold", 11)
    headers = ["Month", "Business Miles", "Personal Miles", "Total Miles", "Notes"]
    col_x = [margin, margin + 110, margin + 230, margin + 340, margin + 450]
    col_w = [110, 120, 110, 110, W - margin - col_x[4]]

    c.setFillColor(DARK)
    c.rect(margin, y - 18, W - 2 * margin, 18, fill=1, stroke=0)
    c.setFillColor(white)
    for i, hdr in enumerate(headers):
        c.drawCentredString(col_x[i] + col_w[i] / 2, y - 14, hdr)

    y -= 18
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December", "TOTAL"]
    c.setFont("Helvetica", 10)
    for i, m in enumerate(months):
        is_total = (m == "TOTAL")
        c.setFillColor(DARK if is_total else (LIGHT_GRAY if i % 2 == 0 else white))
        c.rect(margin, y - 22, W - 2 * margin, 22, fill=1, stroke=0)
        c.setStrokeColor(MID_GRAY)
        c.rect(margin, y - 22, W - 2 * margin, 22, fill=0, stroke=1)
        for cx in col_x[1:]:
            c.line(cx, y, cx, y - 22)
        c.setFillColor(white if is_total else black)
        c.setFont("Helvetica-Bold" if is_total else "Helvetica", 10)
        c.drawString(col_x[0] + 8, y - 15, m)
        y -= 22

    # Tax calculation box
    y -= 30
    c.setFillColor(LIGHT_GRAY)
    c.rect(margin, y - 110, W - 2 * margin, 110, fill=1, stroke=0)
    c.setStrokeColor(DARK)
    c.rect(margin, y - 110, W - 2 * margin, 110, fill=0, stroke=1)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 10, y - 18, "Tax Deduction Calculation")
    c.setFont("Helvetica", 10)
    c.drawString(margin + 10, y - 40, "Total Business Miles:  ____________________")
    c.drawString(margin + 10, y - 60, "Standard Mileage Rate:  ____________________  (cents per mile)")
    c.drawString(margin + 10, y - 80, "Business Miles X Rate = $ ____________________  (deduction)")
    c.drawString(margin + 10, y - 100, "Verify the current IRS rate before filing your return.")

    c.showPage()


def draw_monthly_summary_page(c, month_num):
    margin = 0.75 * inch
    top = H - margin
    c.setFillColor(HEADER_BG)
    c.rect(margin, top - 30, W - 2 * margin, 30, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, top - 22, f"Monthly Summary - Month {month_num}")

    y = top - 60
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)

    summary_fields = [
        ("Month / Year:", "____________________"),
        ("Starting Odometer:", "____________________"),
        ("Ending Odometer:", "____________________"),
        ("Total Miles Driven:", "____________________"),
        ("Business Miles:", "____________________"),
        ("Personal Miles:", "____________________"),
        ("Number of Trips:", "____________________"),
        ("Fuel Spent ($):", "____________________"),
        ("Maintenance ($):", "____________________"),
        ("Tolls / Parking ($):", "____________________"),
    ]
    c.setFont("Helvetica", 12)
    for label, line in summary_fields:
        c.setFillColor(DARK)
        c.drawString(margin + 10, y, label)
        c.setFillColor(black)
        c.drawString(margin + 200, y, line)
        y -= 28

    # Top destinations / clients
    y -= 10
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Top Destinations / Clients This Month:")
    y -= 8
    for _ in range(6):
        y -= 22
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    y -= 20
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Notes & Reminders:")
    y -= 8
    for _ in range(5):
        y -= 22
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    c.showPage()


def draw_trip_log_page(c, page_num):
    margin = 0.75 * inch
    top = H - margin
    # Header
    c.setFillColor(HEADER_BG)
    c.rect(margin, top - 28, W - 2 * margin, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 10, top - 19, f"Trip Log - Page {page_num}")
    c.drawRightString(W - margin - 10, top - 19, "Month: __________  Year: __________")

    # Column setup - widths sum must equal page width minus 2*margin (504 pt for 8.5" letter)
    avail = W - 2 * margin
    cols = [
        ("Date", 55),
        ("Start\nOdometer", 60),
        ("End\nOdometer", 60),
        ("Total\nMiles", 45),
        ("Destination", 105),
        ("Business Purpose", 150),
        ("B/P", 29),
    ]
    total_w = sum(w for _, w in cols)
    # Auto-scale to fit available width
    scale = avail / total_w
    cols = [(label, w * scale) for (label, w) in cols]

    x_positions = [margin]
    for _, w in cols:
        x_positions.append(x_positions[-1] + w)

    # Header row
    y = top - 30
    c.setFillColor(DARK)
    c.rect(margin, y - 32, avail, 32, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    for i, (label, w) in enumerate(cols):
        cx = x_positions[i] + w / 2
        if "\n" in label:
            top_lbl, bot_lbl = label.split("\n")
            c.drawCentredString(cx, y - 12, top_lbl)
            c.drawCentredString(cx, y - 24, bot_lbl)
        else:
            c.drawCentredString(cx, y - 18, label)
    y -= 32

    # Rows
    rows = 22
    row_h = (y - margin - 24) / rows
    if row_h > 26:
        row_h = 26
    c.setFont("Helvetica", 9)
    for r in range(rows):
        ry = y - row_h
        c.setFillColor(LIGHT_GRAY if r % 2 == 0 else white)
        c.rect(margin, ry, avail, row_h, fill=1, stroke=0)
        c.setStrokeColor(MID_GRAY)
        c.rect(margin, ry, avail, row_h, fill=0, stroke=1)
        for xp in x_positions[1:-1]:
            c.line(xp, ry, xp, y)
        y = ry

    # Footer key
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawString(margin, margin - 14, "B/P = Business or Personal (B / P)")
    c.drawCentredString(W / 2, margin - 14, "Mileage Log Book for Taxes | Deokgu Studio")
    c.drawRightString(W - margin, margin - 14, "Keep records 7 years.")

    c.showPage()


def draw_expense_log_page(c, section_num):
    margin = 0.75 * inch
    top = H - margin
    c.setFillColor(HEADER_BG)
    c.rect(margin, top - 30, W - 2 * margin, 30, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, top - 22, f"Vehicle Expense Log - {section_num}")

    y = top - 50
    headers = ["Date", "Vendor", "Type", "Amount", "Odometer", "Notes"]
    widths = [60, 130, 80, 70, 80, W - 2 * margin - 420]
    x_pos = [margin]
    for w in widths:
        x_pos.append(x_pos[-1] + w)

    c.setFillColor(DARK)
    c.rect(margin, y - 20, W - 2 * margin, 20, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    for i, h in enumerate(headers):
        c.drawCentredString(x_pos[i] + widths[i] / 2, y - 14, h)
    y -= 20

    rows = 26
    row_h = 24
    c.setFont("Helvetica", 9)
    for r in range(rows):
        ry = y - row_h
        c.setFillColor(LIGHT_GRAY if r % 2 == 0 else white)
        c.rect(margin, ry, W - 2 * margin, row_h, fill=1, stroke=0)
        c.setStrokeColor(MID_GRAY)
        c.rect(margin, ry, W - 2 * margin, row_h, fill=0, stroke=1)
        for xp in x_pos[1:-1]:
            c.line(xp, ry, xp, y)
        y = ry

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawString(margin, margin - 14, "Type: Fuel | Maintenance | Tolls | Parking | Insurance | Repair | Other")
    c.drawRightString(W - margin, margin - 14, "Deokgu Studio")

    c.showPage()


def draw_back_page(c):
    margin = 0.75 * inch
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 1.4 * inch, "Year-End Tax Checklist")

    y = H - 2 * inch
    items = [
        "Photograph odometer on December 31.",
        "Total all monthly mileage summaries.",
        "Verify Business + Personal miles equal Total miles.",
        "Calculate deduction (Business Miles X IRS rate).",
        "Compile fuel, maintenance, tolls, parking receipts.",
        "Compare Standard Mileage vs. Actual Expense methods.",
        "File Schedule C (Form 1040) or Form 2106 as applicable.",
        "Save this log book with your tax records (keep 7 years).",
        "Save digital backup (scan or photograph each page).",
        "Start a new log book on January 1.",
    ]
    c.setFillColor(black)
    c.setFont("Helvetica", 12)
    for item in items:
        c.setFillColor(ACCENT)
        c.rect(margin, y - 4, 14, 14, fill=0, stroke=1)
        c.setFillColor(black)
        c.drawString(margin + 24, y, item)
        y -= 28

    y -= 20
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Useful Resources")
    y -= 24
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    for line in [
        "IRS Publication 463 (Travel, Gift, and Car Expenses)",
        "IRS Standard Mileage Rate updates: irs.gov",
        "Schedule C (Profit or Loss from Business)",
        "Form 2106 (Employee Business Expenses)",
        "Consult a tax professional for your specific situation.",
    ]:
        c.drawString(margin + 10, y, "- " + line)
        y -= 20

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(W / 2, margin + 10,
                        "This log book is a record-keeping tool. It does not constitute tax advice.")
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Mileage Log Book for Taxes")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_instructions_page(c)
    draw_vehicle_info_page(c)
    draw_year_summary_page(c)

    # 12 months: each = 1 monthly summary + 7 trip log pages = 8 pages -> 96 pages
    for month in range(1, 13):
        draw_monthly_summary_page(c, month)
        for trip_page in range(1, 8):
            draw_trip_log_page(c, trip_page)

    # 4 vehicle expense log pages
    for section in range(1, 5):
        draw_expense_log_page(c, f"Section {section}")

    draw_back_page(c)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
