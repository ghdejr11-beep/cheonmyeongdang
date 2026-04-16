"""
📚 Spot the Difference for Seniors — Large Print
8.5x11, 50 puzzles + answer key
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pathlib import Path
import os, random, math

PDF_PATH = Path(__file__).parent / "Spot_Difference_Seniors_Interior.pdf"
W, H = letter
M = 0.75 * inch
NAVY = HexColor("#2C3E50")
TEAL = HexColor("#1ABC9C")
LIGHT = HexColor("#ECF0F1")
TEXT = HexColor("#2C3E50")
GRAY = HexColor("#95A5A6")

def draw_title_page(c):
    c.setFillColor(NAVY)
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
    cx = W/2
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(cx, H*0.72, "LARGE PRINT EDITION")
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(cx, H*0.60, "SPOT THE")
    c.drawCentredString(cx, H*0.54, "DIFFERENCE")
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(TEAL)
    c.drawCentredString(cx, H*0.46, "FOR SENIORS")
    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawCentredString(cx, H*0.36, "50 Puzzles  |  5 Differences Each")
    c.drawCentredString(cx, H*0.33, "Large Print  |  Answer Key Included")
    c.drawCentredString(cx, H*0.30, "Brain Training & Cognitive Exercise")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#666666"))
    c.drawCentredString(cx, M+20, "Deokgu Studio")
    c.showPage()

def draw_instructions(c):
    y = H - M
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(NAVY)
    c.drawCentredString(W/2, y, "How to Play")
    y -= 40
    c.setFont("Helvetica", 13)
    c.setFillColor(TEXT)
    lines = [
        "Each puzzle has two pictures that look almost the same.",
        "But there are 5 small differences between them!",
        "",
        "Look carefully at both pictures and try to find",
        "all 5 differences. Circle them with a pencil.",
        "",
        "Take your time — there's no rush.",
        "",
        "Answers are at the back of the book.",
        "",
        "These puzzles are designed to be fun and to help",
        "keep your mind sharp. Enjoy!",
    ]
    for line in lines:
        c.drawCentredString(W/2, y, line)
        y -= 20
    c.showPage()

THEMES = [
    "Garden Scene", "Kitchen Table", "Living Room", "Park Bench",
    "Flower Vase", "Bookshelf", "Tea Time", "Bird Feeder",
    "Window View", "Fruit Basket", "Sewing Kit", "Clock Tower",
    "Fishing Dock", "Mailbox Lane", "Bicycle Path", "Sunset Beach",
    "Lighthouse", "Country Road", "Farm Animals", "Rainy Day",
    "Cozy Fireplace", "Library Corner", "Market Stall", "Harbor View",
    "Mountain Lake", "Autumn Leaves", "Winter Cabin", "Spring Garden",
    "Summer Picnic", "Starry Night", "Cottage Door", "Village Square",
    "Bakery Shop", "Toy Store", "Music Room", "Art Gallery",
    "Train Station", "Boat House", "Flower Field", "Old Bridge",
    "Candle Light", "Chess Board", "Rocking Chair", "Porch Swing",
    "Herb Garden", "Butterfly Bush", "Stone Path", "Vintage Car",
    "Compass Rose", "Final Challenge"
]

def draw_scene(c, x, y, w, h, seed, modified=False):
    """Draw a simple geometric scene with clipping to stay inside bounds."""
    random.seed(seed)

    # Clip to scene bounds so nothing goes outside
    c.saveState()
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0)

    # Background
    c.setFillColor(LIGHT)
    c.rect(x, y, w, h, fill=1)

    # Ground
    c.setFillColor(HexColor("#90EE90"))
    c.rect(x, y, w, h*0.25, fill=1)

    # Sun
    sun_r = 12 if not modified else 16
    c.setFillColor(HexColor("#FFD700"))
    c.circle(x + w*0.8, y + h*0.82, sun_r, fill=1)

    # Houses
    house_count = 3 if not modified else 2
    for i in range(house_count):
        hx = x + 15 + i * (w/3.5)
        hy = y + h*0.25
        hw = w*0.18
        hh = h*0.2
        c.setFillColor(HexColor(random.choice(["#E74C3C","#3498DB","#F39C12"])))
        c.rect(hx, hy, hw, hh, fill=1)
        # Roof (no overhang)
        c.setFillColor(HexColor("#8B4513"))
        path = c.beginPath()
        path.moveTo(hx, hy + hh)
        path.lineTo(hx + hw/2, hy + hh + h*0.1)
        path.lineTo(hx + hw, hy + hh)
        path.close()
        c.drawPath(path, fill=1)
        # Window
        wsize = 8 if not (modified and i == 0) else 11
        c.setFillColor(HexColor("#87CEEB"))
        c.rect(hx + hw*0.3, hy + hh*0.4, wsize, wsize, fill=1)

    # Trees
    tree_count = random.randint(2, 3)
    tree_positions = sorted(random.sample(range(int(x+15), int(x+w-15), 30), min(tree_count, 4)))
    for i, tx in enumerate(tree_positions):
        trunk_h = random.randint(15, 25)
        c.setFillColor(HexColor("#8B4513"))
        c.rect(tx, y + h*0.25, 5, trunk_h, fill=1)
        tree_color = "#27AE60" if not (modified and i == len(tree_positions)-1) else "#F39C12"
        c.setFillColor(HexColor(tree_color))
        c.circle(tx + 3, y + h*0.25 + trunk_h + 8, 12, fill=1)

    # Clouds
    cloud_count = 2 if not modified else 3
    for i in range(cloud_count):
        cx_c = x + 25 + i * (w*0.35)
        cy_c = y + h*0.72
        c.setFillColor(HexColor("#ffffff"))
        c.circle(cx_c, cy_c, 9, fill=1)
        c.circle(cx_c+8, cy_c+4, 8, fill=1)
        c.circle(cx_c+16, cy_c, 9, fill=1)

    # Restore state (remove clipping)
    c.restoreState()

    # Draw border on top
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.rect(x, y, w, h)

def draw_puzzle_page(c, num, theme):
    y_top = H - M
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(NAVY)
    c.drawCentredString(W/2, y_top, f"Puzzle #{num}: {theme}")
    c.setFont("Helvetica", 10)
    c.setFillColor(GRAY)
    c.drawCentredString(W/2, y_top - 18, "Find 5 differences between the two pictures!")

    SAFE = M + 20  # Extra safe inset from margin
    pic_w = W - 2*SAFE
    pic_h = (H - 2*SAFE) / 2 - 50

    # Picture A
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(TEAL)
    pic_a_y = SAFE + pic_h + 45
    c.drawString(SAFE, pic_a_y + pic_h + 5, "Picture A")
    draw_scene(c, SAFE, pic_a_y, pic_w, pic_h, seed=num*100)

    # Picture B (modified)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(SAFE, SAFE + pic_h + 5, "Picture B")
    draw_scene(c, SAFE, SAFE, pic_w, pic_h, seed=num*100, modified=True)

    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawCentredString(W/2, M + 10, f"Page {num}")
    c.showPage()

def draw_answer_page(c, start, end):
    y = H - M
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(NAVY)
    c.drawCentredString(W/2, y, f"Answers: Puzzles {start}-{end}")
    y -= 30

    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT)
    for i in range(start, end+1):
        if y < M + 60:
            c.showPage()
            y = H - M
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(NAVY)
            c.drawCentredString(W/2, y, f"Answers (continued)")
            y -= 30
            c.setFont("Helvetica", 10)
            c.setFillColor(TEXT)

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(TEAL)
        c.drawString(M, y, f"Puzzle #{i}:")
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT)
        answers = [
            "1. Sun is different size",
            "2. Different number of houses",
            "3. Window size changed on first house",
            "4. Last tree changed color",
            "5. Extra cloud added"
        ]
        ans_text = "  |  ".join(answers)
        c.drawString(M + 70, y, ans_text[:90])
        if len(ans_text) > 90:
            y -= 13
            c.drawString(M + 70, y, ans_text[90:])
        y -= 20

    c.showPage()

def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("Spot the Difference for Seniors")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_instructions(c)

    for i in range(50):
        draw_puzzle_page(c, i+1, THEMES[i])

    # Answer pages
    draw_answer_page(c, 1, 25)
    draw_answer_page(c, 26, 50)

    # Final
    c.setFillColor(NAVY)
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W/2, H/2+20, "Well Done!")
    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#ffffff"))
    c.drawCentredString(W/2, H/2-15, "You completed all 50 puzzles!")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawCentredString(W/2, H/2-45, "Please leave a review on Amazon!")
    c.showPage()

    c.save()
    print(f"PDF: {PDF_PATH}")
    print(f"Pages: {c.getPageNumber()-1}")
    print(f"Size: {os.path.getsize(PDF_PATH)/1024:.0f} KB")

if __name__ == "__main__":
    generate()
