"""
📚 Password Logbook Generator — Amazon KDP Ready
8.5 x 11 inches, 120 pages, interior PDF (no bleed needed for paperback)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "Password_Logbook_Interior.pdf"

W, H = letter  # 8.5 x 11 inches
MARGIN = 0.75 * inch

# Colors
DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#4a90d9")
LIGHT_GRAY = HexColor("#f0f0f5")
MID_GRAY = HexColor("#cccccc")
LINE_COLOR = HexColor("#dddddd")
TEXT_COLOR = HexColor("#333333")


def draw_title_page(c):
    """Cover-style interior title page."""
    c.setFillColor(DARK)
    c.rect(MARGIN+5, MARGIN+5, W - 2*MARGIN-10, H - 2*MARGIN-10, fill=1)

    # Decorative border
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.rect(MARGIN, MARGIN, W - 2*MARGIN, H - 2*MARGIN)
    c.rect(MARGIN + 0.1*inch, MARGIN + 0.1*inch, W - 2*MARGIN - 0.2*inch, H - 2*MARGIN - 0.2*inch)

    # Lock icon (simple)
    cx, cy = W/2, H*0.62
    c.setFillColor(ACCENT)
    c.circle(cx, cy, 30, fill=1)
    c.setFillColor(DARK)
    c.circle(cx, cy, 18, fill=1)
    c.setFillColor(ACCENT)
    c.rect(cx-25, cy-45, 50, 35, fill=1)
    c.setFillColor(DARK)
    c.circle(cx, cy-30, 6, fill=1)

    # Title
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(W/2, H*0.48, "PASSWORD")
    c.drawCentredString(W/2, H*0.43, "LOGBOOK")

    # Subtitle
    c.setFont("Helvetica", 14)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, H*0.36, "Keep Your Internet Passwords")
    c.drawCentredString(W/2, H*0.33, "Safe & Organized")

    # Bottom info
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#888888"))
    c.drawCentredString(W/2, H*0.08, "Alphabetical Tabs  |  Large Print  |  120 Pages")

    c.showPage()


def draw_how_to_use(c):
    """Instructions page."""
    y = H - MARGIN

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, y, "How to Use This Book")
    y -= 40

    instructions = [
        ("1.", "Find the alphabetical tab for the website or service."),
        ("2.", "Write the website name, URL, username, and password."),
        ("3.", "Use the notes field for security questions or hints."),
        ("4.", "Update entries when you change passwords."),
        ("5.", "Keep this book in a safe, private place."),
    ]

    c.setFont("Helvetica", 13)
    for num, text in instructions:
        y -= 8
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(MARGIN + 10, y, num)
        c.setFillColor(TEXT_COLOR)
        c.setFont("Helvetica", 13)
        c.drawString(MARGIN + 35, y, text)
        y -= 22

    y -= 30
    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W/2, y, "Tip: Use a pencil so you can easily erase and update passwords.")

    y -= 50
    # Security reminder box
    c.setFillColor(LIGHT_GRAY)
    c.roundRect(MARGIN, y - 80, W - 2*MARGIN, 90, 10, fill=1)
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 15, y - 10, "Security Reminder")
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN + 15, y - 30, "- Never share this book with anyone.")
    c.drawString(MARGIN + 15, y - 45, "- Use strong passwords: mix letters, numbers, and symbols.")
    c.drawString(MARGIN + 15, y - 60, "- Change important passwords every 3-6 months.")

    c.showPage()


def draw_alpha_tab(c, letter_char):
    """Alphabetical section divider page."""
    c.setFillColor(ACCENT)
    c.rect(MARGIN, H - MARGIN - inch, W - 2*MARGIN, inch, fill=1)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 72)
    c.drawCentredString(W/2, H - MARGIN - 0.6*inch, letter_char)

    # Draw first entry template on same page
    draw_entry_rows(c, H - 2*inch, 3)

    c.showPage()


def draw_entry_rows(c, start_y, count=4):
    """Draw password entry rows."""
    y = start_y
    row_height = 1.6 * inch

    for i in range(count):
        if y - row_height < MARGIN:
            break

        # Entry box
        c.setStrokeColor(LINE_COLOR)
        c.setLineWidth(0.5)
        c.roundRect(MARGIN, y - row_height, W - 2*MARGIN, row_height - 10, 5)

        inner_x = MARGIN + 12
        inner_w = W - 2*MARGIN - 24
        label_x = inner_x
        value_x = inner_x + 100

        fields = [
            ("Website:", 0),
            ("URL:", -20),
            ("Username:", -40),
            ("Password:", -60),
            ("Email:", -80),
            ("Notes:", -100),
        ]

        for label, offset in fields:
            ly = y - 18 + offset
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(ACCENT)
            c.drawString(label_x, ly, label)

            # Dotted line for writing
            c.setStrokeColor(LINE_COLOR)
            c.setLineWidth(0.3)
            c.setDash(1, 2)
            c.line(value_x, ly - 2, MARGIN + inner_w, ly - 2)
            c.setDash()

        y -= row_height


def draw_entry_page(c):
    """Full page of password entries (4 entries per page)."""
    draw_entry_rows(c, H - MARGIN, 4)
    c.showPage()


def draw_notes_page(c, title="Notes"):
    """Lined notes page."""
    y = H - MARGIN
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, title)
    y -= 30

    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.3)
    while y > MARGIN + 10:
        c.line(MARGIN, y, W - MARGIN, y)
        y -= 22

    c.showPage()


def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("Password Logbook")
    c.setAuthor("Deokgu Studio")
    c.setSubject("Internet Password Organizer")

    # Page 1: Title
    draw_title_page(c)

    # Page 2: How to use
    draw_how_to_use(c)

    # Pages 3-106: Alphabetical sections (A-Z, 4 pages each)
    for letter_char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        draw_alpha_tab(c, letter_char)
        # 3 more entry pages per letter
        for _ in range(3):
            draw_entry_page(c)

    # Pages 107-116: Extra notes pages
    for i in range(10):
        draw_notes_page(c, f"Additional Notes — Page {i+1}")

    # Final page
    c.setFillColor(DARK)
    c.rect(MARGIN+5, MARGIN+5, W - 2*MARGIN-10, H - 2*MARGIN-10, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W/2, H/2 + 20, "Thank You!")
    c.setFont("Helvetica", 12)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, H/2 - 10, "If you found this book helpful,")
    c.drawCentredString(W/2, H/2 - 30, "please leave a review on Amazon.")
    c.drawCentredString(W/2, H/2 - 50, "Your feedback helps us create better books!")
    c.showPage()

    c.save()
    print(f"PDF generated: {PDF_PATH}")
    print(f"Total pages: {c.getPageNumber() - 1}")
    print(f"File size: {os.path.getsize(PDF_PATH) / 1024:.0f} KB")


if __name__ == "__main__":
    generate()
