"""
📚 Dot Marker Activity Book for Toddlers — Amazon KDP
8.5x11, 50 single-sided activity pages + coloring elements
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pathlib import Path
import os, random, math

PDF_PATH = Path(__file__).parent / "Dot_Marker_Activity_Book_Interior.pdf"
W, H = letter
M = 0.75 * inch

COLORS = ["#FF6B6B","#4ECDC4","#45B7D1","#96CEB4","#FFEAA7","#DDA0DD","#FF9F43","#6C5CE7"]

SHAPES = [
    ("Circle Fun", "circle"),
    ("Big Dots", "big_dots"),
    ("Rainbow Path", "path"),
    ("Caterpillar", "caterpillar"),
    ("Flower", "flower"),
    ("Star Pattern", "star"),
    ("Train", "train"),
    ("Balloon", "balloon"),
]

def draw_title_page(c):
    c.setFillColor(HexColor("#FF6B6B"))
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)

    # Scattered dots background (inside margins)
    random.seed(123)
    for _ in range(30):
        clr = random.choice(COLORS)
        c.setFillColor(HexColor(clr))
        c.setFillAlpha(0.3)
        c.circle(random.randint(int(M)+40, int(W-M)-40), random.randint(int(M)+40, int(H-M)-40), random.randint(10,25), fill=1)
    c.setFillAlpha(1)

    # White center box (inside margins)
    c.setFillColor(HexColor("#ffffff"))
    c.roundRect(M+20, H*0.3, W-2*M-40, H*0.4, 20, fill=1)

    c.setFillColor(HexColor("#FF6B6B"))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(W/2, H*0.58, "DOT MARKER")
    c.drawCentredString(W/2, H*0.52, "ACTIVITY BOOK")

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor("#45B7D1"))
    c.drawCentredString(W/2, H*0.44, "For Toddlers Ages 2-5")

    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor("#666666"))
    c.drawCentredString(W/2, H*0.37, "50 Fun Activities  |  Big Dots  |  Easy to Use")

    c.showPage()

def draw_dot_page(c, page_num, title):
    """Generate a dot marker activity page with circles to fill."""
    y_top = H - M

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HexColor(random.choice(COLORS)))
    c.drawCentredString(W/2, y_top, title)

    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#999999"))
    c.drawCentredString(W/2, y_top - 20, "Use your dot markers to fill each circle!")

    random.seed(page_num * 42)

    # Different layouts per page type
    layout_type = page_num % 8

    if layout_type in [0, 1]:  # Grid of circles
        rows, cols = 4, 4
        spacing_x = (W - 2*M) / (cols + 1)
        spacing_y = (H - 3*M) / (rows + 1)
        for r in range(rows):
            for col in range(cols):
                cx = M + spacing_x * (col + 1)
                cy = H - 2.5*M - spacing_y * (r + 1)
                radius = random.choice([25, 30, 35])
                c.setStrokeColor(HexColor(random.choice(COLORS)))
                c.setLineWidth(2)
                c.setDash(3, 3)
                c.circle(cx, cy, radius)
                c.setDash()

    elif layout_type == 2:  # Caterpillar (line of circles)
        cx_start = M + 40
        cy = H/2
        for i in range(8):
            cx = cx_start + i * 65
            cy_off = math.sin(i * 0.8) * 30
            c.setStrokeColor(HexColor(COLORS[i % len(COLORS)]))
            c.setLineWidth(2.5)
            c.setDash(3, 3)
            c.circle(cx, cy + cy_off, 28)
            c.setDash()
            if i == 0:  # Head with eyes
                c.setFillColor(HexColor("#333333"))
                c.circle(cx - 6, cy + cy_off + 8, 3, fill=1)
                c.circle(cx + 6, cy + cy_off + 8, 3, fill=1)

    elif layout_type == 3:  # Flower pattern
        cx, cy = W/2, H/2 - 20
        # Center
        c.setStrokeColor(HexColor("#FFEAA7"))
        c.setLineWidth(2.5)
        c.setDash(3, 3)
        c.circle(cx, cy, 30)
        # Petals
        for angle in range(0, 360, 60):
            px = cx + 65 * math.cos(math.radians(angle))
            py = cy + 65 * math.sin(math.radians(angle))
            c.setStrokeColor(HexColor(COLORS[angle // 60]))
            c.circle(px, py, 28)
        c.setDash()

    elif layout_type == 4:  # Triangle arrangement
        positions = [
            (W/2, H*0.65),
            (W/2-70, H*0.45), (W/2+70, H*0.45),
            (W/2-140, H*0.25), (W/2, H*0.25), (W/2+140, H*0.25),
        ]
        for i, (px, py) in enumerate(positions):
            c.setStrokeColor(HexColor(COLORS[i % len(COLORS)]))
            c.setLineWidth(2.5)
            c.setDash(3, 3)
            c.circle(px, py, 32)
            c.setDash()

    elif layout_type == 5:  # Big center + small around
        c.setStrokeColor(HexColor("#FF6B6B"))
        c.setLineWidth(3)
        c.setDash(4, 4)
        c.circle(W/2, H/2-10, 60)
        for angle in range(0, 360, 45):
            px = W/2 + 120 * math.cos(math.radians(angle))
            py = H/2 - 10 + 120 * math.sin(math.radians(angle))
            c.setStrokeColor(HexColor(COLORS[angle // 45 % len(COLORS)]))
            c.circle(px, py, 22)
        c.setDash()

    elif layout_type == 6:  # Two rows
        for row in range(2):
            for col in range(5):
                cx = M + 50 + col * 95
                cy = H*0.55 - row * 150
                c.setStrokeColor(HexColor(COLORS[(row*5+col) % len(COLORS)]))
                c.setLineWidth(2.5)
                c.setDash(3, 3)
                c.circle(cx, cy, 35)
                c.setDash()

    else:  # Random scatter
        for i in range(12):
            cx = random.randint(int(M)+40, int(W-M)-40)
            cy = random.randint(int(M)+40, int(H-2*M)-40)
            c.setStrokeColor(HexColor(COLORS[i % len(COLORS)]))
            c.setLineWidth(2)
            c.setDash(3, 3)
            c.circle(cx, cy, random.choice([20, 25, 30]))
            c.setDash()

    # Page number
    c.setFillColor(HexColor("#cccccc"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, M/2, str(page_num))

    c.showPage()

    # Blank back page (single-sided printing)
    c.showPage()

TITLES = [
    "Circle Party!", "Big Dot Bonanza!", "Rainbow Dots", "Caterpillar Trail",
    "Flower Power!", "Star Burst!", "Dotty Train", "Balloon Float!",
    "Dots in a Row", "Circle Garden", "Dot Mountain", "Bubbly Dots!",
    "Polka Dot Fun", "Sunny Circles", "Ocean Bubbles", "Candy Dots!",
    "Spotty Dog", "Ladybug Dots", "Pizza Toppings!", "Raindrop Dots",
    "Ice Cream Scoops!", "Snowball Fun", "Cherry Picking", "Button Collection",
    "Cookie Dots!", "Marble Mix", "Gumball Machine!", "Planet Dots",
    "Musical Notes!", "Jellyfish Tentacles", "Firework Pops!", "Dot to Dot Fun",
    "Traffic Light!", "Caterpillar Jr.", "Rainbow Bridge", "Treasure Map!",
    "Underwater Bubbles", "Space Dots!", "Garden Path", "Fruit Basket!",
    "Popcorn Time!", "Beach Balls!", "Dot Monster!", "Honeycomb!",
    "Rocket Launch!", "Cloud Puffs", "Flower Meadow", "Disco Dots!",
    "Animal Spots!", "Grand Finale!"
]

def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("Dot Marker Activity Book for Toddlers")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)

    for i in range(50):
        draw_dot_page(c, i+1, TITLES[i])

    # Final page
    c.setFillColor(HexColor("#4ECDC4"))
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W/2, H/2+20, "Great Job!")
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H/2-15, "You finished all 50 activities!")
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#ddffdd"))
    c.drawCentredString(W/2, H/2-50, "Please leave a review on Amazon!")
    c.showPage()

    c.save()
    print(f"PDF: {PDF_PATH}")
    print(f"Pages: {c.getPageNumber()-1}")
    print(f"Size: {os.path.getsize(PDF_PATH)/1024:.0f} KB")

if __name__ == "__main__":
    generate()
