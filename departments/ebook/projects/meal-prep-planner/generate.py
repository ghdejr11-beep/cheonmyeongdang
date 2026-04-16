"""Weekly Meal Prep Planner - 8.5x11, 108 pages"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meal_prep_planner.pdf")

DARK = HexColor("#33691E")
ACCENT = HexColor("#558B2F")
ORANGE = HexColor("#E65100")
LIGHT = HexColor("#F1F8E9")
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
    c.drawCentredString(W/2, H*0.54, "Weekly Meal Prep")
    c.drawCentredString(W/2, H*0.54 - 38, "Planner")
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H*0.37, "52 Weeks | Grocery Lists | Macro Tracking")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H*0.10, "Deokgu Studio")
    c.showPage()


def draw_intro_pages(c):
    margin = 0.75*inch
    # Personal info
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(DARK)
    c.drawCentredString(W/2, H - 0.8*inch, "My Nutrition Profile")
    y = H - 1.5*inch
    fields = ["Name:", "Date Started:", "Goal Weight:", "Current Weight:",
              "Daily Calorie Target:", "Protein Target (g):", "Carb Target (g):",
              "Fat Target (g):", "Water Target (cups):", "Dietary Restrictions:", "", "Allergies:"]
    c.setFont("Helvetica", 10)
    for f in fields:
        if f:
            c.setFillColor(DARK)
            c.drawString(margin, y + 3, f)
            c.setStrokeColor(MID_GRAY)
            c.line(margin + 180, y, W - margin, y)
        else:
            c.line(margin, y, W - margin, y)
        y -= 24
    c.showPage()

    # Favorite recipes page
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(DARK)
    c.drawCentredString(W/2, H - 0.8*inch, "My Go-To Recipes")
    y = H - 1.3*inch
    categories = ["Breakfast", "Lunch", "Dinner", "Snacks"]
    for cat in categories:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, cat)
        y -= 6
        c.setFont("Helvetica", 10)
        c.setStrokeColor(MID_GRAY)
        for _ in range(4):
            y -= 18
            c.line(margin + 10, y, W - margin, y)
        y -= 14
    c.showPage()


def draw_weekly_meal_plan(c, week_num):
    margin = 0.75*inch
    top = H - margin
    # Header
    c.setFillColor(ACCENT)
    c.rect(margin, top - 28, W - 2*margin, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 8, top - 20, f"Week {week_num} Meal Plan")
    c.drawRightString(W - margin - 8, top - 20, "Dates: ____/____ - ____/____")

    y = top - 42
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]

    # Table header
    col_start = margin + 70
    col_w = (W - 2*margin - 70) / 4
    c.setFillColor(DARK)
    c.rect(margin, y - 12, W - 2*margin, 12, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(margin + 4, y - 10, "Day")
    for i, meal in enumerate(meals):
        c.drawCentredString(col_start + i * col_w + col_w/2, y - 10, meal)

    y -= 18
    row_h = (y - margin - 30) / 7
    c.setFont("Helvetica", 7)
    for d, day in enumerate(days):
        c.setFillColor(LIGHT if d % 2 == 0 else white)
        c.rect(margin, y - row_h, W - 2*margin, row_h, fill=1, stroke=0)
        c.setStrokeColor(MID_GRAY)
        c.rect(margin, y - row_h, W - 2*margin, row_h, fill=0, stroke=1)
        # Day name
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(margin + 4, y - row_h/2, day[:3])
        # Vertical dividers
        for i in range(4):
            cx = col_start + i * col_w
            c.line(cx, y, cx, y - row_h)
        y -= row_h

    # Prep notes
    y -= 8
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin, y, "Prep Notes:")
    y -= 4
    for _ in range(2):
        y -= 12
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 6)
    c.drawCentredString(W/2, margin - 8, "Weekly Meal Prep Planner | Deokgu Studio")
    c.showPage()


def draw_grocery_list(c, week_num):
    margin = 0.75*inch
    top = H - margin
    c.setFillColor(ORANGE)
    c.rect(margin, top - 24, W - 2*margin, 24, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W/2, top - 18, f"Week {week_num} Grocery List")

    y = top - 40
    categories = [
        ("Produce (Fruits & Vegetables)", 8),
        ("Protein (Meat, Fish, Eggs, Tofu)", 6),
        ("Dairy & Alternatives", 4),
        ("Grains & Bread", 4),
        ("Canned & Packaged", 4),
        ("Frozen", 3),
        ("Spices & Condiments", 3),
        ("Other", 3),
    ]

    col_w = (W - 2*margin) / 2
    col = 0
    col_y = [y, y]

    for cat_name, items in categories:
        if col_y[col] < margin + items * 14 + 30:
            col = 1
        cx = margin + col * col_w + 4
        cy = col_y[col]

        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(cx, cy, cat_name)
        cy -= 4
        c.setFont("Helvetica", 7)
        for _ in range(items):
            cy -= 14
            # Checkbox
            c.setStrokeColor(MID_GRAY)
            c.rect(cx + 4, cy, 7, 7, fill=0, stroke=1)
            c.line(cx + 16, cy, cx + col_w - 16, cy)
        cy -= 10
        col_y[col] = cy

    # Budget
    bottom_y = min(col_y)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, bottom_y - 10, "Estimated Budget: $______     Actual Spent: $______     Saved: $______")

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 6)
    c.drawCentredString(W/2, margin - 8, "Weekly Meal Prep Planner | Deokgu Studio")
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Weekly Meal Prep Planner")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_intro_pages(c)

    # 52 weeks, 2 pages each (meal plan + grocery list)
    for week in range(1, 53):
        draw_weekly_meal_plan(c, week)
        draw_grocery_list(c, week)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
