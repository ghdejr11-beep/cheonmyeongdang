"""Math Workbook for 1st Graders - 8.5x11, 110 pages"""
import os, random
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_workbook_grade1.pdf")
random.seed(2024)

DARK = HexColor("#1565C0")
ACCENT = HexColor("#FF6F00")
LIGHT = HexColor("#E3F2FD")
MID_GRAY = HexColor("#CCCCCC")


def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    # Stars decoration
    c.setFillColor(HexColor("#FDD835"))
    for i in range(20):
        sx = random.uniform(0.5*inch, W - 0.5*inch)
        sy = random.uniform(0.5*inch, H - 0.5*inch)
        c.circle(sx, sy, random.uniform(3, 8), fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(W/2, H*0.62, "Math Workbook")
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, H*0.55, "for 1st Graders")
    c.setFillColor(white)
    c.setFont("Helvetica", 16)
    c.drawCentredString(W/2, H*0.43, "Addition & Subtraction")
    c.drawCentredString(W/2, H*0.39, "Numbers 1-20")
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H*0.30, "100+ Pages of Practice")
    c.drawCentredString(W/2, H*0.26, "Answer Key Included")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H*0.10, "Deokgu Studio")
    c.showPage()


def draw_instructions(c):
    margin = 0.75*inch
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(DARK)
    c.drawCentredString(W/2, H - 1*inch, "How to Use This Book")
    y = H - 1.8*inch
    c.setFont("Helvetica", 12)
    tips = [
        "This workbook is designed for 1st graders learning",
        "addition and subtraction with numbers 1 through 20.",
        "",
        "Each page has 20 problems. Difficulty increases gradually:",
        "",
        "  Pages 1-20:   Simple Addition (sums up to 10)",
        "  Pages 21-40:  Addition with sums up to 20",
        "  Pages 41-60:  Simple Subtraction (within 10)",
        "  Pages 61-80:  Subtraction within 20",
        "  Pages 81-90:  Mixed Addition & Subtraction",
        "",
        "Tips for Parents:",
        "  - Set a timer for 5 minutes per page",
        "  - Praise effort, not just correct answers",
        "  - Use the answer key to check together",
        "  - Review mistakes as learning opportunities",
        "",
        "Name: _________________________________",
        "",
        "Date Started: __________________________",
    ]
    for line in tips:
        c.drawString(margin, y, line)
        y -= 20
    c.showPage()


def generate_problems(page_type, count=20):
    """Generate math problems based on difficulty level."""
    problems = []
    for _ in range(count):
        if page_type == "add_10":
            a = random.randint(1, 9)
            b = random.randint(1, 10 - a)
            problems.append((a, "+", b, a + b))
        elif page_type == "add_20":
            a = random.randint(1, 15)
            b = random.randint(1, 20 - a)
            problems.append((a, "+", b, a + b))
        elif page_type == "sub_10":
            a = random.randint(2, 10)
            b = random.randint(1, a)
            problems.append((a, "-", b, a - b))
        elif page_type == "sub_20":
            a = random.randint(5, 20)
            b = random.randint(1, a)
            problems.append((a, "-", b, a - b))
        elif page_type == "mixed":
            if random.random() < 0.5:
                a = random.randint(1, 15)
                b = random.randint(1, 20 - a)
                problems.append((a, "+", b, a + b))
            else:
                a = random.randint(2, 20)
                b = random.randint(1, a)
                problems.append((a, "-", b, a - b))
    return problems


def draw_problem_page(c, page_num, page_type, section_name, all_answers):
    margin = 0.75*inch
    top = H - margin
    # Header
    c.setFillColor(DARK)
    c.rect(margin, top - 28, W - 2*margin, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin + 8, top - 20, f"Page {page_num} - {section_name}")
    c.drawRightString(W - margin - 8, top - 20, "Score: ____ / 20")

    # Name and date
    c.setFillColor(DARK)
    c.setFont("Helvetica", 9)
    c.drawString(margin, top - 44, "Name: ________________    Date: ____________")

    problems = generate_problems(page_type, 20)
    all_answers.append((page_num, problems))

    y = top - 70
    col_w = (W - 2*margin) / 2
    c.setFont("Helvetica", 16)
    for i, (a, op, b, ans) in enumerate(problems):
        col = i % 2
        row = i // 2
        x = margin + col * col_w + 20
        py = y - row * 52

        # Problem number
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x, py, f"{i+1}.")

        # Problem
        c.setFillColor(black)
        c.setFont("Helvetica", 20)
        c.drawString(x + 25, py - 2, f"{a}  {op}  {b}  =  ____")

        # Underline for answer
        c.setStrokeColor(MID_GRAY)
        c.line(x + 155, py - 5, x + 210, py - 5)

    # Footer
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W/2, margin - 15, "Math Workbook for 1st Graders | Deokgu Studio")
    c.showPage()


def draw_answer_page(c, answers_batch):
    margin = 0.75*inch
    top = H - margin
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W/2, top - 20, "Answer Key")

    y = top - 50
    c.setFont("Helvetica", 8)
    for page_num, problems in answers_batch:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, f"Page {page_num}:")
        c.setFont("Helvetica", 8)
        answers_str = "  ".join([f"{i+1}){ans}" for i, (a, op, b, ans) in enumerate(problems)])
        # Split into lines if too long
        c.setFillColor(black)
        line = ""
        x = margin + 50
        for i, (a, op, b, ans) in enumerate(problems):
            piece = f"{i+1}){ans}  "
            if c.stringWidth(line + piece, "Helvetica", 8) > (W - 2*margin - 50):
                c.drawString(x, y, line)
                y -= 12
                line = piece
                x = margin + 50
            else:
                line += piece
        if line:
            c.drawString(x, y, line)
        y -= 18
        if y < margin + 20:
            c.showPage()
            y = top - 30
            c.setFillColor(DARK)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(W/2, top - 20, "Answer Key (continued)")
            y = top - 50

    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Math Workbook for 1st Graders")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_instructions(c)

    all_answers = []
    page = 1

    sections = [
        (20, "add_10", "Addition (Sums to 10)"),
        (20, "add_20", "Addition (Sums to 20)"),
        (20, "sub_10", "Subtraction (Within 10)"),
        (20, "sub_20", "Subtraction (Within 20)"),
        (10, "mixed", "Mixed Practice"),
    ]

    for count, ptype, sname in sections:
        for _ in range(count):
            draw_problem_page(c, page, ptype, sname, all_answers)
            page += 1

    # Answer key pages
    batch_size = 10
    for i in range(0, len(all_answers), batch_size):
        draw_answer_page(c, all_answers[i:i+batch_size])

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
