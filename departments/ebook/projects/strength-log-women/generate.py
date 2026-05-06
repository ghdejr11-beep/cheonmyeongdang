"""Strength Training Log for Women - 12-Week Progressive Overload Tracker, 6x9, ~120 pages"""
import os
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = 6 * inch, 9 * inch
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strength_log_women.pdf")

# Bold, modern, feminine-strong palette (rose-gold + slate)
DARK = HexColor("#3B0F2A")          # deep plum
ACCENT = HexColor("#C2185B")         # bold rose
LIGHT = HexColor("#FCE4EC")          # blush
MID_GRAY = HexColor("#BBBBBB")
SLATE = HexColor("#37474F")
GOLD = HexColor("#B7791F")

MARGIN = 0.75 * inch  # KDP-safe margin (per CLAUDE.md ebook rules)


def hr(c, y, color=MID_GRAY):
    c.setStrokeColor(color)
    c.line(MARGIN, y, W - MARGIN, y)


def footer(c):
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 6)
    c.drawCentredString(W / 2, MARGIN - 12, "Strength Training Log for Women | Deokgu Studio")


def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(MARGIN, MARGIN, W - 2 * MARGIN, H - 2 * MARGIN, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(MARGIN + 6, H * 0.46, W - 2 * MARGIN - 12, 3, fill=1, stroke=0)
    c.rect(MARGIN + 6, H * 0.60, W - 2 * MARGIN - 12, 3, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W / 2, H * 0.55, "Strength Training")
    c.drawCentredString(W / 2, H * 0.55 - 32, "Log for Women")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H * 0.40, "12-Week Progressive Overload Tracker")
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(W / 2, H * 0.36, "Lift Heavy. Track Smart. Build Strong.")
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, MARGIN + 12, "Deokgu Studio")
    c.showPage()


def draw_intro_page(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - MARGIN - 14, "How to Use This Log")
    y = H - MARGIN - 50
    body = [
        ("WHY PROGRESSIVE OVERLOAD?",
         "Strength gains come from gradually adding load, reps, or volume. "
         "Tracking each session is the difference between guessing and growing."),
        ("THE PUSH-PULL-LEGS SPLIT",
         "This log is built around a 4-day Upper / Lower / Push / Pull rotation "
         "but works with any program. Pick your lifts, fill your numbers."),
        ("HOW TO FILL EACH PAGE",
         "Date, body weight, sleep, energy. Then 5-7 main lifts: weight x reps for "
         "every set. Mark RPE (Rate of Perceived Exertion 1-10). Note PRs in red."),
        ("WEEKLY REVIEW",
         "Every 7 days, write what worked, what hurt, and the lift you'll push next "
         "week. Re-read it before your next training block."),
        ("12-WEEK BLOCK",
         "Most programs (5/3/1, GZCLP, StrongCurves, Bret Contreras Glute Lab) run "
         "12 weeks. After Week 12, deload, retest 1RMs, and start Block 2."),
    ]
    c.setFont("Helvetica", 9)
    for header, text in body:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, header)
        y -= 14
        c.setFillColor(SLATE)
        c.setFont("Helvetica", 9)
        # word-wrap
        words = text.split()
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, "Helvetica", 9) > W - 2 * MARGIN:
                c.drawString(MARGIN, y, line)
                y -= 12
                line = w
            else:
                line = test
        if line:
            c.drawString(MARGIN, y, line)
            y -= 12
        y -= 10
    footer(c)
    c.showPage()


def draw_baseline_page(c):
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - MARGIN - 14, "Starting Stats & Goals")

    y = H - MARGIN - 50
    fields = [
        "Name:", "Start Date:", "Age:", "Height:", "Body Weight:",
        "Body Fat %:", "Years Lifting:", "Program/Coach:",
        "", "Current 1-Rep Maxes:",
        "  Squat:", "  Bench:", "  Deadlift:", "  Overhead Press:", "  Hip Thrust:",
        "", "Body Measurements:",
        "  Chest:", "  Waist:", "  Hips:", "  Thigh (L/R):", "  Arm (L/R):",
        "", "Top 3 Goals for This Block:", "1.", "2.", "3.",
    ]
    c.setFont("Helvetica", 9)
    for f in fields:
        if f.strip():
            c.setFillColor(SLATE)
            c.drawString(MARGIN, y + 3, f)
            c.setStrokeColor(MID_GRAY)
            c.line(MARGIN + 110, y, W - MARGIN, y)
        y -= 18
    footer(c)
    c.showPage()


def draw_workout_page(c, day_num, day_label):
    """Daily lift log with 7 exercise rows, 5 set columns each."""
    top = H - MARGIN
    # header bar
    c.setFillColor(ACCENT)
    c.rect(MARGIN, top - 26, W - 2 * MARGIN, 26, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 8, top - 18, f"Day {day_num}  -  {day_label}")
    c.drawRightString(W - MARGIN - 8, top - 18, "Date: ___ / ___ / ___")

    y = top - 44
    # quick metrics row
    c.setFillColor(SLATE)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, y, "Body Wt: ____  |  Sleep: ___ hr  |  Energy 1-10: ___  |  Cycle Day: ___  |  Pre-Workout: ____")
    y -= 14
    c.drawString(MARGIN, y, "Warm-up: __________________________________________________________")
    y -= 18

    # Exercise table headers (fits within 324pt content width)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 8)
    col_x = [MARGIN, MARGIN + 110, MARGIN + 147, MARGIN + 184, MARGIN + 221, MARGIN + 258, MARGIN + 295]
    headers = ["Exercise", "Set 1", "Set 2", "Set 3", "Set 4", "Set 5", "RPE"]
    for x, h in zip(col_x, headers):
        c.drawString(x, y, h)
    y -= 4
    hr(c, y, ACCENT)
    y -= 12

    # 7 exercise rows
    c.setFont("Helvetica", 8)
    cell_w = 35
    rpe_w = 28
    for _ in range(7):
        c.setStrokeColor(MID_GRAY)
        # name field
        c.line(col_x[0], y - 3, col_x[1] - 4, y - 3)
        # set cells
        for i in range(1, 6):
            c.rect(col_x[i], y - 8, cell_w, 16, fill=0, stroke=1)
        # RPE cell
        c.rect(col_x[6], y - 8, rpe_w, 16, fill=0, stroke=1)
        y -= 24

    # Accessory + cardio
    y -= 4
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "Accessory / Core:")
    y -= 6
    c.setFont("Helvetica", 8)
    for _ in range(3):
        y -= 14
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    y -= 14
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "Cardio / Conditioning:")
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN + 130, y, "Type: ________  Time: ___  HR: ___")
    y -= 18

    # PR + notes
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "PR Today?  [ ] Yes   [ ] No   Lift: ____________   Weight: ______")
    y -= 18
    c.setFillColor(DARK)
    c.drawString(MARGIN, y, "Notes / How It Felt:")
    y -= 6
    c.setFont("Helvetica", 8)
    for _ in range(3):
        y -= 14
        c.setStrokeColor(MID_GRAY)
        c.line(MARGIN, y, W - MARGIN, y)

    footer(c)
    c.showPage()


def draw_weekly_review(c, week):
    top = H - MARGIN
    c.setFillColor(GOLD)
    c.rect(MARGIN, top - 30, W - 2 * MARGIN, 30, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W / 2, top - 21, f"Week {week} Review")

    y = top - 56
    c.setFillColor(SLATE)
    c.setFont("Helvetica", 9)
    rows = [
        "Sessions Completed:  ___ / 4",
        "Total Volume (sets x reps x lbs):  ____________",
        "Body Weight Change:  ____________",
        "Sleep Average:  ____ hr",
        "Stress / Recovery (1-10):  ____",
    ]
    for r in rows:
        c.drawString(MARGIN, y, r)
        y -= 18

    y -= 4
    sections = [
        "PRs Hit This Week:",
        "What Worked:",
        "What Didn't (form / fatigue / pain):",
        "Lift to Push Next Week:",
        "One-Word Mindset for Next Week:",
    ]
    for s in sections:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y, s)
        y -= 6
        c.setStrokeColor(MID_GRAY)
        for _ in range(2):
            y -= 14
            c.line(MARGIN, y, W - MARGIN, y)
        y -= 6

    footer(c)
    c.showPage()


def draw_pr_tracker(c):
    top = H - MARGIN
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, top - 14, "12-Week PR Tracker")

    y = top - 50
    lifts = ["Back Squat", "Bench Press", "Deadlift", "Overhead Press",
             "Hip Thrust", "Romanian DL", "Front Squat", "Bulgarian Split",
             "Bent-Over Row", "Pull-Up (reps)"]

    # header row (5 cols fits inside 324pt content area)
    box_w = 41
    box_step = 43
    first_box = 105
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN, y, "Lift")
    for i, label in enumerate(["Start", "Wk 4", "Wk 8", "Wk 12", "Gain"]):
        c.drawString(MARGIN + first_box + i * box_step, y, label)
    y -= 4
    hr(c, y, ACCENT)
    y -= 14

    c.setFillColor(SLATE)
    c.setFont("Helvetica", 9)
    for lift in lifts:
        c.drawString(MARGIN, y, lift)
        for i in range(5):
            c.setStrokeColor(MID_GRAY)
            c.rect(MARGIN + first_box + i * box_step, y - 6, box_w, 16, fill=0, stroke=1)
        y -= 26

    footer(c)
    c.showPage()


def draw_measurements_page(c):
    top = H - MARGIN
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, top - 14, "Measurements & Photos")

    y = top - 50
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 8)
    headers = ["Date", "Weight", "Chest", "Waist", "Hips", "Thigh", "Arm"]
    col_w = (W - 2 * MARGIN) / 7
    for i, h in enumerate(headers):
        c.drawString(MARGIN + i * col_w + 4, y, h)
    y -= 4
    hr(c, y, ACCENT)
    y -= 14

    c.setStrokeColor(MID_GRAY)
    for _ in range(14):
        for i in range(7):
            c.rect(MARGIN + i * col_w, y - 14, col_w, 18, fill=0, stroke=1)
        y -= 18

    y -= 12
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, y, "Photo Log: paste / staple progress photos here")
    y -= 6
    c.setStrokeColor(MID_GRAY)
    for _ in range(4):
        y -= 18
        c.line(MARGIN, y, W - MARGIN, y)

    footer(c)
    c.showPage()


def draw_block_review(c):
    top = H - MARGIN
    c.setFillColor(GOLD)
    c.rect(MARGIN, top - 30, W - 2 * MARGIN, 30, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, top - 21, "12-Week Block Review")

    y = top - 56
    sections = [
        "Biggest Wins:",
        "What I Learned About My Body:",
        "Lifts That Surprised Me:",
        "Setbacks (injury, life, motivation):",
        "What I'll Change in Block 2:",
        "New 1-Rep Maxes (Squat / Bench / DL / OHP / Hip Thrust):",
        "Goal for Next 12 Weeks:",
    ]
    c.setFillColor(SLATE)
    for s in sections:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(ACCENT)
        c.drawString(MARGIN, y, s)
        y -= 6
        c.setStrokeColor(MID_GRAY)
        for _ in range(3):
            y -= 14
            c.line(MARGIN, y, W - MARGIN, y)
        y -= 8

    footer(c)
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=(W, H))
    c.setTitle("Strength Training Log for Women")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_intro_page(c)
    draw_baseline_page(c)
    draw_pr_tracker(c)

    # 12 weeks x (4 workout days + 1 weekly review) = 60 pages
    day_labels = ["Lower Body", "Upper Push", "Lower Glutes", "Upper Pull"]
    for week in range(1, 13):
        for d in range(4):
            day_num = (week - 1) * 4 + (d + 1)
            draw_workout_page(c, day_num, day_labels[d])
        draw_weekly_review(c, week)

    draw_measurements_page(c)
    draw_block_review(c)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
