"""Airbnb Guest Book - 6x9, 104 pages"""
import os
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = 6 * inch, 9 * inch
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "airbnb_guest_book.pdf")

DARK = HexColor("#2C3E50")
ACCENT = HexColor("#E67E22")
LIGHT = HexColor("#FDF2E9")
MID_GRAY = HexColor("#CCCCCC")
WARM = HexColor("#F39C12")


def draw_title_page(c):
    c.setFillColor(HexColor("#FAF0E6"))
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    # Decorative border
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.rect(0.75*inch, 0.75*inch, W - 1.5*inch, H - 1.5*inch, fill=0, stroke=1)
    c.setLineWidth(1)
    c.rect(0.85*inch, 0.85*inch, W - 1.7*inch, H - 1.7*inch, fill=0, stroke=1)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W / 2, H * 0.62, "Guest Book")
    c.setFont("Helvetica", 14)
    c.setFillColor(ACCENT)
    c.drawCentredString(W / 2, H * 0.55, "~ Welcome to Our Home ~")

    c.setFont("Helvetica", 11)
    c.setFillColor(DARK)
    c.drawCentredString(W / 2, H * 0.40, "Property Name: _________________________")
    c.drawCentredString(W / 2, H * 0.36, "Address: _______________________________")
    c.drawCentredString(W / 2, H * 0.32, "Host: __________________________________")

    c.setFont("Helvetica", 10)
    c.setFillColor(MID_GRAY)
    c.drawCentredString(W / 2, H * 0.10, "Deokgu Studio")
    c.showPage()


def draw_welcome_page(c):
    margin = 0.6 * inch
    c.setFillColor(HexColor("#FAF0E6"))
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 1 * inch, "Welcome!")
    y = H - 1.6 * inch
    c.setFont("Helvetica", 10)
    lines = [
        "Thank you for choosing to stay with us!",
        "",
        "We hope you enjoy your time here. This guest book",
        "is a collection of memories from all our wonderful",
        "visitors. We would love for you to share your",
        "experience, favorite moments, and recommendations",
        "for future guests.",
        "",
        "Please feel free to write as much or as little as",
        "you'd like. Your words mean the world to us!",
        "",
        "Enjoy your stay,",
        "Your Hosts",
    ]
    for line in lines:
        c.drawCentredString(W / 2, y, line)
        y -= 18
    c.showPage()


def draw_house_rules(c):
    margin = 0.6 * inch
    c.setFillColor(HexColor("#FAF0E6"))
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 1 * inch, "House Information")
    y = H - 1.6 * inch
    items = [
        "WiFi Network: _________________________",
        "WiFi Password: _________________________",
        "Check-in Time: _________________________",
        "Check-out Time: _________________________",
        "Emergency Contact: _____________________",
        "Nearest Hospital: ______________________",
        "Trash Day: _____________________________",
        "Thermostat: ____________________________",
        "Special Instructions:",
    ]
    c.setFont("Helvetica", 10)
    for item in items:
        c.drawString(margin, y, item)
        y -= 26
    # Lines for special instructions
    for _ in range(6):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)
    c.showPage()


def draw_local_recommendations(c):
    margin = 0.6 * inch
    c.setFillColor(HexColor("#FAF0E6"))
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, H - 1 * inch, "Local Recommendations")
    y = H - 1.5 * inch
    categories = ["Restaurants", "Coffee Shops", "Attractions", "Shopping", "Outdoor Activities"]
    c.setFont("Helvetica", 10)
    for cat in categories:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, cat)
        y -= 6
        c.setFont("Helvetica", 10)
        c.setStrokeColor(MID_GRAY)
        for _ in range(3):
            y -= 18
            c.line(margin + 10, y, W - margin, y)
        y -= 14
    c.showPage()


def draw_guest_page(c, guest_num):
    margin = 0.6 * inch
    c.setFillColor(HexColor("#FAF0E6"))
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)

    # Decorative top line
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.line(margin, H - margin - 5, W - margin, H - margin - 5)
    c.setLineWidth(0.5)

    y = H - margin - 30
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, y, f"Guest #{guest_num}")

    y -= 30
    c.setFont("Helvetica", 10)
    fields = [
        ("Name(s):", 2.0 * inch),
        ("Date:", 2.0 * inch),
        ("From:", 2.0 * inch),
        ("Occasion:", 2.0 * inch),
    ]
    for label, lw in fields:
        c.setFillColor(DARK)
        c.drawString(margin, y + 2, label)
        c.setStrokeColor(MID_GRAY)
        c.line(margin + 70, y, W - margin, y)
        y -= 24

    # Star rating
    y -= 8
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Overall Rating:")
    star_x = margin + 100
    c.setFont("Helvetica", 16)
    for i in range(5):
        c.setStrokeColor(WARM)
        c.setFillColor(white)
        # Draw star outline as circle placeholder
        c.circle(star_x + i * 28, y + 4, 10, fill=0, stroke=1)
        c.setFillColor(WARM)
        c.setFont("Helvetica", 14)
        c.drawCentredString(star_x + i * 28, y, str(i + 1))

    # Experience
    y -= 35
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Tell us about your stay:")
    y -= 8
    for _ in range(8):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    # Recommendations
    y -= 25
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK)
    c.drawString(margin, y, "Your favorite spot nearby:")
    y -= 8
    for _ in range(3):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    # Message to host
    y -= 25
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "A message for your host:")
    y -= 8
    for _ in range(4):
        y -= 18
        c.setStrokeColor(MID_GRAY)
        c.line(margin, y, W - margin, y)

    # Bottom decoration
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.line(margin, margin + 15, W - margin, margin + 15)
    c.setLineWidth(0.5)

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, margin, "Airbnb Guest Book | Deokgu Studio")
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=(W, H))
    c.setTitle("Airbnb Guest Book")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_welcome_page(c)
    draw_house_rules(c)
    draw_local_recommendations(c)

    # 100 guest pages
    for i in range(1, 101):
        draw_guest_page(c, i)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
