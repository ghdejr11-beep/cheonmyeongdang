"""
Password Logbook Premium: Extra Large Print for Seniors — Amazon KDP Ready
8.5 x 11 inches, 150+ pages
Senior-friendly: 30% larger text, wider input fields, high contrast
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "Password_Logbook_Premium_Seniors.pdf"

W, H = letter  # 8.5 x 11 inches
MARGIN = 0.75 * inch

# Colors — high contrast for seniors
DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#2563eb")
ACCENT_DARK = HexColor("#1e40af")
LIGHT_BG = HexColor("#f0f4ff")
WHITE = HexColor("#ffffff")
TEXT_COLOR = HexColor("#1a1a1a")
MUTED = HexColor("#666666")
LINE_COLOR = HexColor("#b0c4de")
FIELD_BG = HexColor("#fafbff")
HIGHLIGHT = HexColor("#dbeafe")

# Font sizes — 30% larger than standard
LABEL_SIZE = 13       # was ~10
FIELD_SIZE = 14       # was ~11
HEADING_SIZE = 20     # was ~16
SUBHEADING_SIZE = 16  # was ~12
TITLE_SIZE = 40       # was ~32
BODY_SIZE = 13        # was ~10
TAB_LETTER_SIZE = 84  # was ~72


def draw_title_page(c):
    """Premium title page with large, clear text."""
    c.setFillColor(DARK)
    c.rect(MARGIN+5, MARGIN+5, W - 2*MARGIN-10, H - 2*MARGIN-10, fill=1)

    # Decorative double border
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.rect(MARGIN, MARGIN, W - 2*MARGIN, H - 2*MARGIN)
    c.setLineWidth(1)
    c.rect(MARGIN+0.1*inch, MARGIN+0.1*inch, W-2*MARGIN-0.2*inch, H-2*MARGIN-0.2*inch)

    # Lock icon (larger)
    cx, cy = W/2, H * 0.65
    c.setFillColor(ACCENT)
    c.circle(cx, cy, 40, fill=1)
    c.setFillColor(DARK)
    c.circle(cx, cy, 24, fill=1)
    c.setFillColor(ACCENT)
    c.rect(cx - 32, cy - 55, 64, 42, fill=1)
    c.setFillColor(DARK)
    c.circle(cx, cy - 38, 8, fill=1)

    # Title — extra large
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", TITLE_SIZE)
    c.drawCentredString(W/2, H * 0.48, "PASSWORD")
    c.drawCentredString(W/2, H * 0.42, "LOGBOOK")

    # Premium badge
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W/2, H * 0.35, "PREMIUM EDITION")

    # Subtitle
    c.setFont("Helvetica", 16)
    c.setFillColor(HexColor("#aabbdd"))
    c.drawCentredString(W/2, H * 0.28, "Extra Large Print for Easy Reading")

    # Features
    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor("#8899bb"))
    c.drawCentredString(W/2, H * 0.15, "Large Text  |  Wide Writing Spaces  |  150+ Pages")
    c.drawCentredString(W/2, H * 0.12, "Alphabetical Tabs  |  High Contrast  |  Senior-Friendly")

    c.showPage()


def draw_how_to_use(c):
    """How to use page with extra large text."""
    y = H - MARGIN

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(ACCENT_DARK)
    c.drawCentredString(W/2, y, "How to Use This Book")
    y -= 50

    instructions = [
        ("1.", "Find the letter tab for the website or app name."),
        ("2.", "Write the website name and web address (URL)."),
        ("3.", "Write your username (or email) and password."),
        ("4.", "Use the notes area for security questions or hints."),
        ("5.", "Update entries when you change a password."),
        ("6.", "Keep this book in a safe, private place."),
    ]

    for num, text in instructions:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", BODY_SIZE + 2)
        c.drawString(MARGIN + 10, y, num)
        c.setFillColor(TEXT_COLOR)
        c.setFont("Helvetica", BODY_SIZE + 2)
        c.drawString(MARGIN + 40, y, text)
        y -= 35

    y -= 20

    # Tips box — larger
    c.setFillColor(LIGHT_BG)
    c.roundRect(MARGIN, y - 160, W - 2*MARGIN, 170, 10, fill=1)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.roundRect(MARGIN, y - 160, W - 2*MARGIN, 170, 10, fill=0)

    c.setFillColor(ACCENT_DARK)
    c.setFont("Helvetica-Bold", SUBHEADING_SIZE)
    c.drawString(MARGIN + 20, y - 15, "Helpful Tips")

    c.setFont("Helvetica", BODY_SIZE)
    c.setFillColor(TEXT_COLOR)
    tips = [
        "Use a PENCIL so you can erase and update easily.",
        "Use strong passwords: mix letters, numbers, and symbols.",
        "Change important passwords every few months.",
        "Never share this book with anyone.",
        "Write clearly and take your time.",
    ]
    ty = y - 45
    for tip in tips:
        c.drawString(MARGIN + 25, ty, f"- {tip}")
        ty -= 22

    c.showPage()


def draw_password_tips(c):
    """Password safety tips page."""
    y = H - MARGIN

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(ACCENT_DARK)
    c.drawCentredString(W/2, y, "Password Safety Tips")
    y -= 50

    tips = [
        ("Make passwords long", "Use at least 8-12 characters. Longer is better."),
        ("Mix it up", "Use uppercase letters, lowercase letters, numbers, and symbols like !@#$."),
        ("Avoid obvious words", "Don't use your name, birthday, '123456', or 'password'."),
        ("Use different passwords", "Don't use the same password for every website."),
        ("Change regularly", "Update important passwords (bank, email) every 3-6 months."),
        ("Be careful online", "Never give your password to someone who emails or calls you."),
        ("Two-factor authentication", "When available, turn on two-factor (2FA) for extra security."),
    ]

    for title, desc in tips:
        if y < MARGIN + 40:
            c.showPage()
            y = H - MARGIN

        # Tip box
        c.setFillColor(HIGHLIGHT)
        c.roundRect(MARGIN, y - 50, W - 2*MARGIN, 55, 6, fill=1)

        c.setFillColor(ACCENT_DARK)
        c.setFont("Helvetica-Bold", BODY_SIZE + 1)
        c.drawString(MARGIN + 15, y - 12, title)

        c.setFillColor(TEXT_COLOR)
        c.setFont("Helvetica", BODY_SIZE)
        c.drawString(MARGIN + 15, y - 35, desc)
        y -= 70

    c.showPage()


def draw_alpha_tab(c, letter_char):
    """Large alphabetical section divider."""
    # Header bar — extra tall
    c.setFillColor(ACCENT)
    c.rect(MARGIN, H - MARGIN - inch, W - 2*MARGIN, inch, fill=1)

    # Letter — extra large
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", TAB_LETTER_SIZE)
    c.drawCentredString(W/2, H - MARGIN - 0.5*inch, letter_char)

    # Section label
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#ccdaff"))
    c.drawCentredString(W/2, H - MARGIN - 0.8*inch, f"Websites & Apps Starting With \"{letter_char}\"")

    # Draw 2 entries on tab page (fewer per page = more space)
    draw_entry_rows(c, H - 2.2*inch, 2)
    c.showPage()


def draw_entry_rows(c, start_y, count=2):
    """Draw password entry rows — PREMIUM size (30% larger, wider fields)."""
    y = start_y
    row_height = 2.8 * inch  # Much taller than standard (was ~1.6)

    for i in range(count):
        if y - row_height < MARGIN:
            break

        # Entry box with visible border
        c.setFillColor(FIELD_BG)
        c.roundRect(MARGIN, y - row_height, W - 2*MARGIN, row_height - 12, 8, fill=1)
        c.setStrokeColor(LINE_COLOR)
        c.setLineWidth(1)
        c.roundRect(MARGIN, y - row_height, W - 2*MARGIN, row_height - 12, 8, fill=0)

        inner_x = MARGIN + 15
        label_x = inner_x
        value_x = inner_x + 130  # Wider label column
        line_end = W - MARGIN - 15

        fields = [
            ("Website / App:", 0),
            ("Web Address (URL):", -30),
            ("Username:", -60),
            ("Password:", -90),
            ("Email:", -120),
            ("Security Question:", -150),
            ("Notes:", -180),
        ]

        for label, offset in fields:
            ly = y - 25 + offset

            # Label — large bold
            c.setFont("Helvetica-Bold", LABEL_SIZE)
            c.setFillColor(ACCENT_DARK)
            c.drawString(label_x, ly, label)

            # Writing line — solid, visible
            c.setStrokeColor(LINE_COLOR)
            c.setLineWidth(0.6)
            c.line(value_x, ly - 3, line_end, ly - 3)

        y -= row_height


def draw_entry_page(c):
    """Full page of password entries — 2 per page for premium spacing."""
    draw_entry_rows(c, H - MARGIN, 2)
    c.showPage()


def draw_notes_page(c, title="Notes"):
    """Lined notes page with extra large spacing."""
    y = H - MARGIN

    c.setFont("Helvetica-Bold", HEADING_SIZE)
    c.setFillColor(ACCENT_DARK)
    c.drawString(MARGIN, y, title)
    y -= 40

    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.4)
    line_spacing = 30  # Wider lines for seniors (was ~22)
    while y > MARGIN + 15:
        c.line(MARGIN, y, W - MARGIN, y)
        y -= line_spacing

    c.showPage()


def draw_important_contacts(c):
    """Important contacts page (tech support, etc.)."""
    y = H - MARGIN

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(ACCENT_DARK)
    c.drawCentredString(W/2, y, "Important Contacts")
    y -= 15
    c.setFont("Helvetica", BODY_SIZE)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, y, "Keep important phone numbers and contacts here")
    y -= 40

    contacts = [
        "Internet Provider",
        "Computer/Phone Support",
        "Bank",
        "Email Provider",
        "Family Tech Helper",
        "Other",
    ]

    for contact in contacts:
        if y < MARGIN + 80:
            c.showPage()
            y = H - MARGIN

        # Contact box
        c.setFillColor(LIGHT_BG)
        c.roundRect(MARGIN, y - 90, W - 2*MARGIN, 95, 8, fill=1)
        c.setStrokeColor(LINE_COLOR)
        c.setLineWidth(0.8)
        c.roundRect(MARGIN, y - 90, W - 2*MARGIN, 95, 8, fill=0)

        inner_x = MARGIN + 15
        line_end = W - MARGIN - 15

        c.setFont("Helvetica-Bold", SUBHEADING_SIZE)
        c.setFillColor(ACCENT_DARK)
        c.drawString(inner_x, y - 15, contact)

        fields = [("Name:", -40), ("Phone:", -62), ("Email / Notes:", -84)]
        for label, offset in fields:
            ly = y + offset
            c.setFont("Helvetica-Bold", LABEL_SIZE - 1)
            c.setFillColor(TEXT_COLOR)
            c.drawString(inner_x, ly, label)
            c.setStrokeColor(LINE_COLOR)
            c.setLineWidth(0.5)
            c.line(inner_x + 120, ly - 2, line_end, ly - 2)

        y -= 110

    c.showPage()


def draw_wifi_page(c):
    """Wi-Fi passwords page."""
    y = H - MARGIN

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(ACCENT_DARK)
    c.drawCentredString(W/2, y, "Wi-Fi Passwords")
    y -= 15
    c.setFont("Helvetica", BODY_SIZE)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, y, "Keep your Wi-Fi network information here")
    y -= 45

    for i in range(4):
        if y < MARGIN + 120:
            c.showPage()
            y = H - MARGIN

        c.setFillColor(LIGHT_BG)
        c.roundRect(MARGIN, y - 130, W - 2*MARGIN, 135, 8, fill=1)
        c.setStrokeColor(LINE_COLOR)
        c.setLineWidth(0.8)
        c.roundRect(MARGIN, y - 130, W - 2*MARGIN, 135, 8, fill=0)

        inner_x = MARGIN + 15
        line_end = W - MARGIN - 15

        c.setFont("Helvetica-Bold", SUBHEADING_SIZE)
        c.setFillColor(ACCENT_DARK)
        c.drawString(inner_x, y - 18, f"Wi-Fi Network {i+1}")

        fields = [
            ("Location:", -48),
            ("Network Name (SSID):", -73),
            ("Password:", -98),
            ("Notes:", -123),
        ]
        for label, offset in fields:
            ly = y + offset
            c.setFont("Helvetica-Bold", LABEL_SIZE - 1)
            c.setFillColor(TEXT_COLOR)
            c.drawString(inner_x, ly, label)
            label_w = c.stringWidth(label, "Helvetica-Bold", LABEL_SIZE - 1) + 10
            c.setStrokeColor(LINE_COLOR)
            c.setLineWidth(0.5)
            c.line(inner_x + label_w, ly - 2, line_end, ly - 2)

        y -= 150

    c.showPage()


def draw_final_page(c):
    """Thank you / back page."""
    c.setFillColor(DARK)
    c.rect(MARGIN+5, MARGIN+5, W - 2*MARGIN-10, H - 2*MARGIN-10, fill=1)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W/2, H/2 + 40, "Thank You!")

    c.setFont("Helvetica", 16)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, H/2 - 5, "We hope this book helps you")
    c.drawCentredString(W/2, H/2 - 28, "keep your passwords safe and organized.")

    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#8899bb"))
    c.drawCentredString(W/2, H * 0.2, "If you found this book helpful,")
    c.drawCentredString(W/2, H * 0.17, "please leave a review on Amazon.")
    c.drawCentredString(W/2, H * 0.14, "Your feedback helps us create better books!")

    c.showPage()


def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("Password Logbook Premium: Extra Large Print for Seniors")
    c.setAuthor("Deokgu Studio")
    c.setSubject("Senior-Friendly Password Organizer — Extra Large Print Edition")

    # Title page
    draw_title_page(c)

    # How to use
    draw_how_to_use(c)

    # Password safety tips
    draw_password_tips(c)

    # Important contacts page
    draw_important_contacts(c)

    # Wi-Fi passwords page
    draw_wifi_page(c)

    # Alphabetical sections: A-Z
    # 6 pages per letter (tab + 5 entry pages) = 156 pages for entries
    for letter_char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        draw_alpha_tab(c, letter_char)
        for _ in range(5):
            draw_entry_page(c)

    # Extra notes pages (10 pages)
    for i in range(10):
        draw_notes_page(c, f"Additional Notes — Page {i+1}")

    # Final page
    draw_final_page(c)

    c.save()
    page_count = c.getPageNumber() - 1
    file_size = os.path.getsize(PDF_PATH) / 1024
    print(f"PDF generated: {PDF_PATH}")
    print(f"Total pages: {page_count}")
    print(f"File size: {file_size:.0f} KB")


if __name__ == "__main__":
    generate()
