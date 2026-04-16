"""Budget Planner for Couples - 8.5x11, 124 pages"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "budget_planner_couples.pdf")

DARK = HexColor("#263238")
ACCENT = HexColor("#00897B")
PINK = HexColor("#E91E63")
LIGHT = HexColor("#E0F2F1")
MID_GRAY = HexColor("#CCCCCC")
LIGHT_GRAY = HexColor("#F5F5F5")


def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0.75*inch, H*0.44, W - 1.5*inch, 4, fill=1, stroke=0)
    c.rect(0.75*inch, H*0.60, W - 1.5*inch, 4, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(W/2, H*0.54, "Budget Planner")
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(PINK)
    c.drawCentredString(W/2, H*0.54 - 38, "for Couples")
    c.setFillColor(white)
    c.setFont("Helvetica", 13)
    c.drawCentredString(W/2, H*0.37, "Joint & Individual Finances | Savings | Debt Payoff")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H*0.10, "Deokgu Studio")
    c.showPage()


def draw_financial_snapshot(c):
    margin = 0.75*inch
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(DARK)
    c.drawCentredString(W/2, H - 0.8*inch, "Our Financial Snapshot")
    y = H - 1.5*inch

    sections = [
        ("Partner 1", ["Name:", "Monthly Income:", "Employer:", "Pay Frequency:"]),
        ("Partner 2", ["Name:", "Monthly Income:", "Employer:", "Pay Frequency:"]),
        ("Combined", ["Total Monthly Income:", "Total Monthly Expenses:", "Net Monthly:",
                      "Emergency Fund Goal:", "Current Emergency Fund:"]),
    ]
    c.setFont("Helvetica", 10)
    for title, fields in sections:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, title)
        y -= 6
        c.setFont("Helvetica", 10)
        for f in fields:
            y -= 22
            c.setFillColor(DARK)
            c.drawString(margin + 16, y + 3, f)
            c.setStrokeColor(MID_GRAY)
            c.line(margin + 200, y, W - margin, y)
        y -= 18
    c.showPage()


def draw_savings_goals(c):
    margin = 0.75*inch
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(DARK)
    c.drawCentredString(W/2, H - 0.8*inch, "Savings Goals")
    y = H - 1.5*inch

    for i in range(5):
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, f"Goal {i+1}:")
        c.setStrokeColor(MID_GRAY)
        c.line(margin + 50, y - 2, W - margin, y - 2)
        y -= 22
        c.setFont("Helvetica", 9)
        c.setFillColor(DARK)
        c.drawString(margin + 16, y, "Target Amount: $_______  Deadline: ________  Monthly Saving: $_______")
        y -= 18
        # Progress bar
        c.setStrokeColor(ACCENT)
        c.setFillColor(LIGHT)
        c.rect(margin + 16, y - 2, W - 2*margin - 16, 12, fill=1, stroke=1)
        c.setFont("Helvetica", 7)
        c.setFillColor(DARK)
        for pct in [0, 25, 50, 75, 100]:
            px = margin + 16 + (W - 2*margin - 16) * pct / 100
            c.drawCentredString(px, y - 14, f"{pct}%")
        y -= 32
    c.showPage()


def draw_debt_tracker(c):
    margin = 0.75*inch
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(DARK)
    c.drawCentredString(W/2, H - 0.8*inch, "Debt Payoff Tracker")
    y = H - 1.4*inch

    # Table header
    cols = [margin, margin + 130, margin + 240, margin + 340, margin + 420]
    headers = ["Debt Name", "Total Owed", "Interest %", "Min Payment", "Target Date"]
    col_w = [130, 110, 100, 80, W - 2*margin - 420]

    c.setFillColor(DARK)
    c.rect(margin, y - 14, W - 2*margin, 14, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    for i, h in enumerate(headers):
        c.drawCentredString(cols[i] + col_w[i]/2, y - 10, h)

    y -= 22
    c.setFont("Helvetica", 9)
    for row in range(10):
        c.setFillColor(LIGHT_GRAY if row % 2 == 0 else white)
        c.rect(margin, y - 4, W - 2*margin, 18, fill=1, stroke=0)
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y - 4, W - margin, y - 4)
        for cx in cols[1:]:
            c.line(cx, y - 4, cx, y + 14)
        y -= 20

    y -= 20
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Payoff Strategy:  [ ] Snowball  [ ] Avalanche  [ ] Custom")
    y -= 28
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Total Debt: $____________     Monthly Payment: $____________")
    y -= 22
    c.drawString(margin, y, "Projected Debt-Free Date: ________________")

    c.showPage()


def draw_monthly_budget(c, month_name):
    margin = 0.75*inch
    top = H - margin
    # Header
    c.setFillColor(ACCENT)
    c.rect(margin, top - 30, W - 2*margin, 30, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, top - 22, f"{month_name} - Monthly Budget")

    y = top - 48
    # Income
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "INCOME")
    y -= 6
    income_items = ["Partner 1 Salary:", "Partner 2 Salary:", "Side Income:", "Other:", "TOTAL INCOME:"]
    c.setFont("Helvetica", 9)
    for item in income_items:
        y -= 16
        bold = "TOTAL" in item
        if bold:
            c.setFont("Helvetica-Bold", 9)
        c.setFillColor(DARK)
        c.drawString(margin + 8, y + 2, item)
        c.setStrokeColor(MID_GRAY)
        c.line(margin + 180, y, margin + 300, y)
        if bold:
            c.setFont("Helvetica", 9)

    # Joint expenses
    y -= 20
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "JOINT EXPENSES")
    y -= 6
    joint = ["Rent/Mortgage:", "Utilities:", "Groceries:", "Insurance:", "Car Payment:",
             "Subscriptions:", "Dining Out:", "Entertainment:", "Other Joint:", "TOTAL JOINT:"]
    c.setFont("Helvetica", 9)
    for item in joint:
        y -= 14
        bold = "TOTAL" in item
        if bold:
            c.setFont("Helvetica-Bold", 9)
        c.setFillColor(DARK)
        c.drawString(margin + 8, y + 2, item)
        # Budget / Actual / Diff columns
        for col_off in [180, 260, 340]:
            c.setStrokeColor(MID_GRAY)
            c.line(margin + col_off, y, margin + col_off + 70, y)
        if bold:
            c.setFont("Helvetica", 9)

    # Column headers for expenses
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(ACCENT)
    header_y = top - 48 - 6 - 16*5 - 20 - 6 + 10
    for label, off in [("Budget", 180), ("Actual", 260), ("Diff", 340)]:
        c.drawCentredString(margin + off + 35, y + 14*len(joint) + 8, label)

    c.showPage()


def draw_individual_expenses(c, month_name):
    margin = 0.75*inch
    top = H - margin
    c.setFillColor(PINK)
    c.rect(margin, top - 28, W - 2*margin, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W/2, top - 20, f"{month_name} - Individual Expenses")

    y = top - 48
    for partner in ["Partner 1", "Partner 2"]:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, partner)
        y -= 6
        items = ["Personal Care:", "Clothing:", "Hobbies:", "Gifts:", "Other:", "TOTAL:"]
        c.setFont("Helvetica", 9)
        for item in items:
            y -= 16
            bold = "TOTAL" in item
            if bold:
                c.setFont("Helvetica-Bold", 9)
            c.setFillColor(DARK)
            c.drawString(margin + 8, y + 2, item)
            for col_off in [150, 230, 310]:
                c.setStrokeColor(MID_GRAY)
                c.line(margin + col_off, y, margin + col_off + 70, y)
            if bold:
                c.setFont("Helvetica", 9)
        y -= 18

    # Monthly summary
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Monthly Summary")
    y -= 20
    c.setFont("Helvetica", 10)
    c.setFillColor(DARK)
    summaries = ["Total Income:", "Total Joint Expenses:", "Total Partner 1:", "Total Partner 2:",
                 "Total All Expenses:", "NET (Income - Expenses):", "Saved This Month:"]
    for s in summaries:
        c.drawString(margin + 8, y, s)
        c.setStrokeColor(MID_GRAY)
        c.line(margin + 230, y - 2, margin + 380, y - 2)
        y -= 20

    # Notes
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Monthly Notes & Goals:")
    y -= 6
    for _ in range(4):
        y -= 16
        c.line(margin, y, W - margin, y)

    c.showPage()


def draw_weekly_expense_page(c, week, part):
    """Draw weekly expense tracker - part 1 (Mon-Thu) or part 2 (Fri-Sun + summary)."""
    margin = 0.75*inch
    top = H - margin
    c.setFillColor(DARK)
    c.rect(margin, top - 24, W - 2*margin, 24, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    label = "Mon - Thu" if part == 1 else "Fri - Sun + Summary"
    c.drawString(margin + 6, top - 18, f"Week {week} ({label})")
    c.drawRightString(W - margin - 6, top - 18, "Date Range: ____/____  -  ____/____")

    y = top - 38
    days = ["Monday", "Tuesday", "Wednesday", "Thursday"] if part == 1 else ["Friday", "Saturday", "Sunday"]

    # Column headers
    cols_x = [margin, margin + 35, margin + 230, margin + 310, margin + 380, margin + 440]
    col_headers = ["#", "Description", "Joint", "P1", "P2", "Category"]
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(DARK)
    for i, h in enumerate(col_headers):
        c.drawString(cols_x[i] + 2, y, h)
    y -= 6

    rows_per_day = 4 if part == 1 else 5
    row_h = 14

    for d, day in enumerate(days):
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y - 10, day)
        y -= 14
        c.setFont("Helvetica", 7)
        for r in range(rows_per_day):
            c.setFillColor(LIGHT if r % 2 == 0 else white)
            c.rect(margin, y - row_h + 2, W - 2*margin, row_h, fill=1, stroke=0)
            c.setStrokeColor(MID_GRAY)
            c.line(margin, y - row_h + 2, W - margin, y - row_h + 2)
            c.setFillColor(DARK)
            c.drawString(margin + 4, y - row_h + 5, str(r + 1))
            for cx_val in cols_x[1:]:
                c.line(cx_val, y - row_h + 2, cx_val, y + 2)
            y -= row_h
        # Day subtotal
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 7)
        c.drawRightString(margin + 230, y - 8, f"{day} Total:")
        c.setStrokeColor(MID_GRAY)
        for off in [230, 310, 380]:
            c.line(margin + off, y - 10, margin + off + 65, y - 10)
        y -= 18

    if part == 2:
        # Weekly summary
        y -= 6
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, "Weekly Summary")
        y -= 20
        c.setFont("Helvetica", 9)
        c.setFillColor(DARK)
        for label in ["Total Joint:", "Total Partner 1:", "Total Partner 2:",
                      "Week Grand Total:", "Under/Over Budget:"]:
            c.drawString(margin + 16, y, label)
            c.setStrokeColor(MID_GRAY)
            c.line(margin + 180, y - 2, margin + 320, y - 2)
            y -= 18
        # Notes
        y -= 8
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "Notes:")
        y -= 4
        for _ in range(3):
            y -= 14
            c.line(margin, y, W - margin, y)

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 6)
    c.drawCentredString(W/2, margin - 8, "Budget Planner for Couples | Deokgu Studio")
    c.showPage()


MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Budget Planner for Couples")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_financial_snapshot(c)
    draw_savings_goals(c)
    draw_debt_tracker(c)

    # 12 months * 2 pages each = 24 pages
    for month in MONTHS:
        draw_monthly_budget(c, month)
        draw_individual_expenses(c, month)

    # Weekly expense tracker pages (52 weeks, 2 pages each = 104 pages)
    for week in range(1, 53):
        draw_weekly_expense_page(c, week, 1)
        draw_weekly_expense_page(c, week, 2)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
