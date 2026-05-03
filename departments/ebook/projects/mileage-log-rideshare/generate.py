"""
Mileage Log Book for Self-Employed & Rideshare Drivers
IRS-compliant vehicle mileage tracker (2026 tax year)
6x9 paperback, ~120 pages
"""
import os
from reportlab.lib.pagesizes import inch
from reportlab.lib.units import inch as INCH
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib import colors

PAGE_W = 6 * INCH
PAGE_H = 9 * INCH
MARGIN = 0.75 * INCH
INNER = MARGIN + 0.125 * INCH  # KDP gutter on inside edge

OUT_PDF = os.path.join(os.path.dirname(__file__), "mileage-log-rideshare-interior.pdf")

NAVY = HexColor("#1B3A5C")
ACCENT = HexColor("#C2873B")
LIGHT = HexColor("#F1ECE0")
GREY = HexColor("#888888")
RULE = HexColor("#D5D5D5")


def draw_page_border(c, page_num):
    # Light footer with page number
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY)
    c.drawCentredString(PAGE_W / 2, 0.4 * INCH, str(page_num))
    c.setFillColor(black)


def title_page(c):
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 3.5 * INCH, PAGE_W, 3.5 * INCH, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.6 * INCH, "MILEAGE")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.1 * INCH, "LOG BOOK")
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.7 * INCH, "For Self-Employed & Rideshare Drivers")
    c.setFillColor(ACCENT)
    c.rect(PAGE_W / 2 - 1 * INCH, PAGE_H - 3.0 * INCH, 2 * INCH, 0.04 * INCH, stroke=0, fill=1)
    c.setFillColor(black)
    c.setFont("Helvetica", 11)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.2 * INCH, "IRS-Compliant Vehicle Mileage Tracker")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.5 * INCH, "Track Business, Medical & Charity Miles")
    c.setFillColor(GREY)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 5.2 * INCH, "120 Days  -  Vehicle Profile  -  Annual Summary")
    c.setFillColor(black)
    # Bottom band
    c.setFillColor(LIGHT)
    c.rect(0, 0, PAGE_W, 1.2 * INCH, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, 0.55 * INCH, "Tax Year 2026")
    c.setFillColor(black)
    c.showPage()


def copyright_page(c):
    c.setFont("Helvetica", 9)
    c.setFillColor(GREY)
    y = PAGE_H - 1.5 * INCH
    lines = [
        "Mileage Log Book for Self-Employed & Rideshare Drivers",
        "",
        "Copyright (c) 2026 Deokgu Studio. All rights reserved.",
        "",
        "This logbook is a personal record-keeping tool. The publisher",
        "does not provide tax, legal, or financial advice. Please consult",
        "a qualified tax professional regarding deduction eligibility,",
        "documentation requirements, and IRS Publication 463.",
        "",
        "First Edition - 2026",
    ]
    for ln in lines:
        c.drawString(MARGIN, y, ln)
        y -= 0.22 * INCH
    c.setFillColor(black)
    c.showPage()


def how_to_page(c):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(INNER, PAGE_H - 1.0 * INCH, "How to Use This Logbook")
    c.setFillColor(ACCENT)
    c.rect(INNER, PAGE_H - 1.15 * INCH, 1.0 * INCH, 0.04 * INCH, stroke=0, fill=1)

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(INNER, PAGE_H - 1.6 * INCH, "1.  Fill in your Vehicle Profile")
    c.setFont("Helvetica", 10)
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 1.85 * INCH, "Record VIN, plate, and starting odometer on")
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 2.05 * INCH, "January 1 (or the day you start tracking).")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(INNER, PAGE_H - 2.5 * INCH, "2.  Record Every Trip")
    c.setFont("Helvetica", 10)
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 2.75 * INCH, "Date, start/end odometer, miles, purpose,")
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 2.95 * INCH, "destination, and category (Business / Medical /")
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 3.15 * INCH, "Charity / Personal). The IRS requires contemporaneous")
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 3.35 * INCH, "logs - record the day of, not at year-end.")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(INNER, PAGE_H - 3.8 * INCH, "3.  Total Each Page")
    c.setFont("Helvetica", 10)
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 4.05 * INCH, "Add daily totals at the bottom of every page,")
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 4.25 * INCH, "then carry to the Monthly Summary.")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(INNER, PAGE_H - 4.7 * INCH, "4.  Apply the IRS Standard Mileage Rate")
    c.setFont("Helvetica", 10)
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 4.95 * INCH, "Use the rate published for your tax year:")
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 5.15 * INCH, "Business / Medical / Charity have separate rates.")
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 5.35 * INCH, "Multiply category miles by the rate for deduction.")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(INNER, PAGE_H - 5.8 * INCH, "5.  Keep With Your Tax Records")
    c.setFont("Helvetica", 10)
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 6.05 * INCH, "Retain this logbook for at least 3 years")
    c.drawString(INNER + 0.2 * INCH, PAGE_H - 6.25 * INCH, "(IRS recommendation). 7 years for safety.")

    # Tip box
    c.setFillColor(LIGHT)
    c.rect(INNER, PAGE_H - 7.5 * INCH, PAGE_W - 2 * INNER, 0.9 * INCH, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(INNER + 0.15 * INCH, PAGE_H - 6.85 * INCH, "RIDESHARE TIP")
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    c.drawString(INNER + 0.15 * INCH, PAGE_H - 7.05 * INCH, "Uber/Lyft drivers: log the deadhead miles between")
    c.drawString(INNER + 0.15 * INCH, PAGE_H - 7.22 * INCH, "rides and to/from your home base. The platform")
    c.drawString(INNER + 0.15 * INCH, PAGE_H - 7.39 * INCH, "summary only counts on-trip miles - you can")
    c.drawString(INNER + 0.15 * INCH, PAGE_H - 7.56 * INCH, "deduct significantly more with a complete log.")
    c.showPage()


def vehicle_profile(c):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(INNER, PAGE_H - 1.0 * INCH, "Vehicle Profile")
    c.setFillColor(ACCENT)
    c.rect(INNER, PAGE_H - 1.15 * INCH, 1.0 * INCH, 0.04 * INCH, stroke=0, fill=1)
    c.setFillColor(black)

    fields = [
        "Driver Name",
        "Tax Year",
        "Vehicle Make",
        "Vehicle Model",
        "Year",
        "VIN",
        "License Plate",
        "Date Placed in Service",
        "Odometer on January 1",
        "Odometer on December 31",
        "Total Miles for Year",
        "Primary Use (check one): Business  /  Personal  /  Mixed",
        "Rideshare Platform(s)",
        "Insurance Carrier",
        "Insurance Policy #",
    ]
    y = PAGE_H - 1.7 * INCH
    c.setFont("Helvetica", 10)
    for f in fields:
        c.drawString(INNER, y, f)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(INNER + 1.9 * INCH, y - 0.04 * INCH, PAGE_W - INNER, y - 0.04 * INCH)
        y -= 0.4 * INCH
    c.showPage()


def irs_rate_page(c):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(INNER, PAGE_H - 1.0 * INCH, "IRS Standard Mileage Rates")
    c.setFillColor(ACCENT)
    c.rect(INNER, PAGE_H - 1.15 * INCH, 1.4 * INCH, 0.04 * INCH, stroke=0, fill=1)
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    c.drawString(INNER, PAGE_H - 1.4 * INCH, "Record the rate published by the IRS for your tax year. Verify on irs.gov.")

    headers = ["Year", "Business", "Medical / Moving", "Charity"]
    col_x = [INNER, INNER + 1.0 * INCH, INNER + 2.0 * INCH, INNER + 3.6 * INCH]
    y = PAGE_H - 2.0 * INCH

    c.setFillColor(LIGHT)
    c.rect(INNER, y - 0.05 * INCH, PAGE_W - 2 * INNER, 0.32 * INCH, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    for i, h in enumerate(headers):
        c.drawString(col_x[i], y + 0.08 * INCH, h)
    y -= 0.32 * INCH

    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    for yr in range(2024, 2031):
        c.drawString(col_x[0], y, str(yr))
        for i in range(1, 4):
            c.setStrokeColor(RULE)
            c.line(col_x[i], y - 0.04 * INCH, col_x[i] + 0.9 * INCH, y - 0.04 * INCH)
        y -= 0.42 * INCH

    # Calculation worksheet
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(INNER, 3.5 * INCH, "Annual Deduction Worksheet")
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    rows = [
        "Total Business Miles  x  $______ /mi  =  $",
        "Total Medical Miles   x  $______ /mi  =  $",
        "Total Charity Miles   x  $______ /mi  =  $",
        "TOTAL MILEAGE DEDUCTION                =  $",
    ]
    yy = 3.0 * INCH
    for r in rows:
        c.drawString(INNER, yy, r)
        c.setStrokeColor(RULE)
        c.line(PAGE_W - INNER - 1.2 * INCH, yy - 0.04 * INCH, PAGE_W - INNER, yy - 0.04 * INCH)
        yy -= 0.45 * INCH
    c.showPage()


def daily_log_page(c, page_label):
    # Header
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(INNER, PAGE_H - 0.7 * INCH, f"Mileage Log  -  {page_label}")
    c.setFillColor(ACCENT)
    c.rect(INNER, PAGE_H - 0.78 * INCH, 0.7 * INCH, 0.025 * INCH, stroke=0, fill=1)

    # Week of / Month input
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    c.drawString(PAGE_W - INNER - 1.7 * INCH, PAGE_H - 0.7 * INCH, "Week of: __________")

    # Table
    cols = [
        ("Date",        0.55 * INCH),
        ("Start Odo",   0.65 * INCH),
        ("End Odo",     0.65 * INCH),
        ("Miles",       0.45 * INCH),
        ("Purpose / Destination", 1.55 * INCH),
        ("Cat.",        0.35 * INCH),
    ]
    table_x = INNER
    table_y_top = PAGE_H - 1.05 * INCH
    avail_w = PAGE_W - 2 * INNER
    # Normalize column widths
    total = sum(w for _, w in cols)
    scale = avail_w / total
    widths = [w * scale for _, w in cols]

    # Header row
    c.setFillColor(NAVY)
    c.rect(table_x, table_y_top - 0.32 * INCH, avail_w, 0.32 * INCH, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8.5)
    cx = table_x
    for (label, _), w in zip(cols, widths):
        c.drawString(cx + 0.05 * INCH, table_y_top - 0.21 * INCH, label)
        cx += w

    # Rows
    rows = 14
    row_h = 0.42 * INCH
    c.setFillColor(black)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    y = table_y_top - 0.32 * INCH
    for r in range(rows):
        y -= row_h
        if r % 2 == 0:
            c.setFillColor(HexColor("#FAF8F2"))
            c.rect(table_x, y, avail_w, row_h, stroke=0, fill=1)
        c.setFillColor(black)
        # Cell borders
        c.setStrokeColor(RULE)
        cx = table_x
        c.line(table_x, y, table_x + avail_w, y)
        for w in widths[:-1]:
            cx += w
            c.line(cx, y, cx, y + row_h)

    # Outer border
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.7)
    c.rect(table_x, y, avail_w, table_y_top - y, stroke=1, fill=0)

    # Daily totals row
    totals_y = y - 0.5 * INCH
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NAVY)
    c.drawString(table_x, totals_y + 0.05 * INCH, "PAGE TOTALS")
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    labels = ["Business: ____", "Medical: ____", "Charity: ____", "Personal: ____"]
    lx = table_x
    spacing = avail_w / 4
    for i, lbl in enumerate(labels):
        c.drawString(table_x + i * spacing, totals_y - 0.2 * INCH, lbl)

    # Legend
    c.setFont("Helvetica-Oblique", 7.5)
    c.setFillColor(GREY)
    c.drawString(table_x, totals_y - 0.55 * INCH, "Cat. codes:  B = Business    M = Medical    C = Charity    P = Personal")
    c.setFillColor(black)


def monthly_summary_page(c, month_name):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(INNER, PAGE_H - 1.0 * INCH, f"{month_name} - Monthly Summary")
    c.setFillColor(ACCENT)
    c.rect(INNER, PAGE_H - 1.15 * INCH, 1.0 * INCH, 0.04 * INCH, stroke=0, fill=1)
    c.setFillColor(black)

    # Summary block
    c.setFont("Helvetica", 10)
    items = [
        "Starting Odometer",
        "Ending Odometer",
        "Total Miles This Month",
        "Business Miles",
        "Medical / Moving Miles",
        "Charity Miles",
        "Personal Miles",
        "Number of Trips Logged",
        "Fuel Cost This Month  $",
        "Maintenance Cost  $",
        "Tolls / Parking  $",
    ]
    y = PAGE_H - 1.7 * INCH
    for it in items:
        c.drawString(INNER, y, it)
        c.setStrokeColor(RULE)
        c.line(INNER + 2.4 * INCH, y - 0.04 * INCH, PAGE_W - INNER, y - 0.04 * INCH)
        y -= 0.36 * INCH

    # Notes
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(INNER, y - 0.1 * INCH, "Notes / Observations")
    c.setFillColor(black)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    ny = y - 0.45 * INCH
    for _ in range(7):
        c.line(INNER, ny, PAGE_W - INNER, ny)
        ny -= 0.3 * INCH


def annual_summary_page(c):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(INNER, PAGE_H - 1.0 * INCH, "Annual Summary")
    c.setFillColor(ACCENT)
    c.rect(INNER, PAGE_H - 1.15 * INCH, 1.0 * INCH, 0.04 * INCH, stroke=0, fill=1)
    c.setFillColor(black)

    # Monthly grid
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    # Header
    headers = ["Month", "Business", "Medical", "Charity", "Total"]
    col_x = [INNER, INNER + 1.3 * INCH, INNER + 2.3 * INCH, INNER + 3.0 * INCH, INNER + 3.8 * INCH]

    y = PAGE_H - 1.7 * INCH
    c.setFillColor(LIGHT)
    c.rect(INNER, y - 0.05 * INCH, PAGE_W - 2 * INNER, 0.3 * INCH, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    for i, h in enumerate(headers):
        c.drawString(col_x[i], y + 0.06 * INCH, h)
    y -= 0.3 * INCH

    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    for m in months:
        c.drawString(col_x[0], y, m)
        c.setStrokeColor(RULE)
        for i in range(1, 5):
            c.line(col_x[i], y - 0.04 * INCH, col_x[i] + 0.9 * INCH, y - 0.04 * INCH)
        y -= 0.32 * INCH

    # YEAR TOTAL row
    c.setFillColor(LIGHT)
    c.rect(INNER, y - 0.06 * INCH, PAGE_W - 2 * INNER, 0.32 * INCH, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col_x[0], y + 0.05 * INCH, "YEAR TOTAL")
    c.setFillColor(black)


def back_page(c):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(INNER, PAGE_H - 1.0 * INCH, "Tax Filing Checklist")
    c.setFillColor(ACCENT)
    c.rect(INNER, PAGE_H - 1.15 * INCH, 1.0 * INCH, 0.04 * INCH, stroke=0, fill=1)
    c.setFillColor(black)

    items = [
        "[ ] Vehicle Profile completed (top of book)",
        "[ ] Starting odometer recorded on Jan 1",
        "[ ] Ending odometer recorded on Dec 31",
        "[ ] Every trip logged contemporaneously",
        "[ ] Each daily entry has destination + purpose",
        "[ ] Page totals filled in at bottom of each log",
        "[ ] Monthly summary completed (12 months)",
        "[ ] Annual summary table totaled",
        "[ ] IRS Standard Mileage Rate applied",
        "[ ] Form 1040 Schedule C / Schedule A line",
        "[ ] 1099-K from rideshare platform attached",
        "[ ] Receipts for parking + tolls organized",
        "[ ] Logbook stored with tax records (3-7 yrs)",
    ]
    c.setFont("Helvetica", 11)
    y = PAGE_H - 1.7 * INCH
    for it in items:
        c.drawString(INNER, y, it)
        y -= 0.36 * INCH

    # Footer thank-you
    c.setFillColor(LIGHT)
    c.rect(0, 0, PAGE_W, 1.2 * INCH, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, 0.7 * INCH, "Drive Smart. Track Everything. Deduct More.")
    c.setFont("Helvetica", 9)
    c.setFillColor(GREY)
    c.drawCentredString(PAGE_W / 2, 0.45 * INCH, "Thank you for using this logbook  -  Deokgu Studio")
    c.setFillColor(black)


def main():
    c = canvas.Canvas(OUT_PDF, pagesize=(PAGE_W, PAGE_H))

    page_num = 1

    title_page(c); page_num += 1
    copyright_page(c); page_num += 1
    how_to_page(c); page_num += 1
    vehicle_profile(c); page_num += 1
    irs_rate_page(c); page_num += 1

    months = [
        ("January", 8),
        ("February", 8),
        ("March", 8),
        ("April", 8),
        ("May", 8),
        ("June", 8),
        ("July", 8),
        ("August", 8),
        ("September", 8),
        ("October", 8),
        ("November", 8),
        ("December", 8),
    ]
    for month, log_pages in months:
        # Month divider with summary at end
        for i in range(log_pages):
            daily_log_page(c, f"{month} {i+1}/{log_pages}")
            draw_page_border(c, page_num)
            c.showPage()
            page_num += 1
        monthly_summary_page(c, month)
        draw_page_border(c, page_num)
        c.showPage()
        page_num += 1

    annual_summary_page(c)
    draw_page_border(c, page_num)
    c.showPage()
    page_num += 1

    back_page(c)
    c.showPage()
    page_num += 1

    c.save()
    print(f"PDF created: {OUT_PDF}")
    print(f"Total pages: {page_num - 1}")


if __name__ == "__main__":
    main()
