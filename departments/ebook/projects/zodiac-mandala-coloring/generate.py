"""Zodiac Mandala Coloring Book - 8.5x11, 50 single-sided pages"""
import os, math
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zodiac_mandala_coloring.pdf")

DARK = HexColor("#1A237E")
LINE_W = 2.5
LIGHT_GRAY = HexColor("#F0F0F0")

ZODIAC = [
    ("Aries", "Mar 21 - Apr 19", "Fire Sign | Cardinal | Ram", 3),
    ("Taurus", "Apr 20 - May 20", "Earth Sign | Fixed | Bull", 5),
    ("Gemini", "May 21 - Jun 20", "Air Sign | Mutable | Twins", 6),
    ("Cancer", "Jun 21 - Jul 22", "Water Sign | Cardinal | Crab", 4),
    ("Leo", "Jul 23 - Aug 22", "Fire Sign | Fixed | Lion", 8),
    ("Virgo", "Aug 23 - Sep 22", "Earth Sign | Mutable | Maiden", 7),
    ("Libra", "Sep 23 - Oct 22", "Air Sign | Cardinal | Scales", 6),
    ("Scorpio", "Oct 23 - Nov 21", "Water Sign | Fixed | Scorpion", 5),
    ("Sagittarius", "Nov 22 - Dec 21", "Fire Sign | Mutable | Archer", 9),
    ("Capricorn", "Dec 22 - Jan 19", "Earth Sign | Cardinal | Goat", 4),
    ("Aquarius", "Jan 20 - Feb 18", "Air Sign | Fixed | Water Bearer", 7),
    ("Pisces", "Feb 19 - Mar 20", "Water Sign | Mutable | Fish", 12),
]


def draw_title_page(c):
    c.setFillColor(HexColor("#0D1B3E"))
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    # Stars
    import random
    random.seed(42)
    c.setFillColor(white)
    for _ in range(80):
        sx = random.uniform(0.3*inch, W - 0.3*inch)
        sy = random.uniform(0.3*inch, H - 0.3*inch)
        c.circle(sx, sy, random.uniform(1, 3), fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W/2, H*0.58, "Zodiac Mandala")
    c.drawCentredString(W/2, H*0.52, "Coloring Book")
    c.setFont("Helvetica", 13)
    c.drawCentredString(W/2, H*0.42, "12 Star Signs | 50 Geometric Mandalas")
    # Simple mandala on cover
    _draw_mandala(c, W/2, H*0.25, 80, 8, white, 1.5)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H*0.08, "Deokgu Studio")
    c.showPage()


def _draw_mandala(c, cx, cy, radius, symmetry, color, lw):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.setFillColor(white if color == black else HexColor("#0D1B3E"))

    # Concentric circles
    for r in [radius, radius * 0.75, radius * 0.5, radius * 0.25]:
        c.circle(cx, cy, r, fill=0, stroke=1)

    # Radial lines
    for i in range(symmetry):
        angle = math.radians(i * 360 / symmetry)
        c.line(cx, cy, cx + radius * math.cos(angle), cy + radius * math.sin(angle))

    # Petal pattern at each layer
    for layer, r in enumerate([radius * 0.35, radius * 0.6, radius * 0.85]):
        petal_count = symmetry * (layer + 1)
        petal_r = r * 0.15
        for i in range(petal_count):
            angle = math.radians(i * 360 / petal_count + layer * 15)
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            c.circle(px, py, petal_r, fill=0, stroke=1)

    # Diamond shapes between petals
    for i in range(symmetry):
        angle1 = math.radians(i * 360 / symmetry)
        angle2 = math.radians((i + 0.5) * 360 / symmetry)
        r1, r2 = radius * 0.45, radius * 0.65
        p = c.beginPath()
        p.moveTo(cx + r1 * math.cos(angle1), cy + r1 * math.sin(angle1))
        p.lineTo(cx + (r1 + r2)/2 * math.cos(angle2), cy + (r1 + r2)/2 * math.sin(angle2))
        p.lineTo(cx + r2 * math.cos(angle1), cy + r2 * math.sin(angle1))
        p.lineTo(cx + (r1 + r2)/2 * math.cos(math.radians(i * 360 / symmetry - 360 / symmetry / 2)),
                 cy + (r1 + r2)/2 * math.sin(math.radians(i * 360 / symmetry - 360 / symmetry / 2)))
        p.close()
        c.drawPath(p, fill=0, stroke=1)


def draw_zodiac_mandala(c, cx, cy, radius, symmetry, variant):
    """Generate unique mandala based on symmetry count and variant."""
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)

    # Outer border circle
    c.circle(cx, cy, radius, fill=0, stroke=1)
    c.circle(cx, cy, radius * 0.97, fill=0, stroke=1)

    # Layer 1: Outer petals
    n_outer = symmetry * 2
    for i in range(n_outer):
        angle = math.radians(i * 360 / n_outer + variant * 7)
        r1 = radius * 0.8
        r2 = radius * 0.92
        px = cx + (r1 + r2) / 2 * math.cos(angle)
        py = cy + (r1 + r2) / 2 * math.sin(angle)
        # Elongated petal
        a1 = angle + math.pi / 2
        pw = radius * 0.06
        ph = (r2 - r1) / 2
        c.ellipse(px - pw, py - ph, px + pw, py + ph, fill=0, stroke=1)

    # Layer 2: Star points
    for i in range(symmetry):
        angle = math.radians(i * 360 / symmetry + variant * 13)
        next_angle = math.radians((i + 1) * 360 / symmetry + variant * 13)
        mid_angle = (angle + next_angle) / 2

        r_in = radius * 0.5
        r_out = radius * 0.75
        r_mid = radius * 0.55

        p = c.beginPath()
        p.moveTo(cx + r_in * math.cos(angle), cy + r_in * math.sin(angle))
        p.lineTo(cx + r_out * math.cos(mid_angle), cy + r_out * math.sin(mid_angle))
        p.lineTo(cx + r_in * math.cos(next_angle), cy + r_in * math.sin(next_angle))
        c.drawPath(p, fill=0, stroke=1)

    # Layer 3: Inner circles
    n_inner = symmetry
    inner_r = radius * 0.08
    for i in range(n_inner):
        angle = math.radians(i * 360 / n_inner + variant * 5)
        ix = cx + radius * 0.35 * math.cos(angle)
        iy = cy + radius * 0.35 * math.sin(angle)
        c.circle(ix, iy, inner_r, fill=0, stroke=1)
        # Dot in center of each
        c.circle(ix, iy, inner_r * 0.3, fill=0, stroke=1)

    # Layer 4: Connecting arcs
    for i in range(symmetry):
        angle = math.radians(i * 360 / symmetry + variant * 3)
        next_angle = math.radians((i + 1) * 360 / symmetry + variant * 3)
        r = radius * 0.6
        x1 = cx + r * math.cos(angle)
        y1 = cy + r * math.sin(angle)
        x2 = cx + r * math.cos(next_angle)
        y2 = cy + r * math.sin(next_angle)
        # Small arc circle between points
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        c.circle(mx, my, radius * 0.04, fill=0, stroke=1)

    # Center
    c.circle(cx, cy, radius * 0.2, fill=0, stroke=1)
    c.circle(cx, cy, radius * 0.12, fill=0, stroke=1)
    c.circle(cx, cy, radius * 0.04, fill=0, stroke=1)

    # Center rays
    for i in range(symmetry):
        angle = math.radians(i * 360 / symmetry)
        c.line(cx + radius * 0.04 * math.cos(angle), cy + radius * 0.04 * math.sin(angle),
               cx + radius * 0.2 * math.cos(angle), cy + radius * 0.2 * math.sin(angle))


def draw_zodiac_intro(c, name, dates, desc):
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W/2, H*0.6, name)
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H*0.54, dates)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H*0.48, desc)
    # Decorative mandala preview (small)
    c.showPage()


def draw_coloring_page(c, page_num, symmetry, variant):
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    draw_zodiac_mandala(c, W/2, H/2, min(W, H) * 0.38, symmetry, variant)
    c.setFillColor(DARK)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, 0.4*inch, str(page_num))
    c.showPage()


def draw_blank(c):
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(LIGHT_GRAY)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H/2, "This page intentionally left blank")
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Zodiac Mandala Coloring Book")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_blank(c)

    page = 1
    for name, dates, desc, sym in ZODIAC:
        draw_zodiac_intro(c, name, dates, desc)
        draw_blank(c)
        # 4 mandala pages per sign
        for v in range(4):
            draw_coloring_page(c, page, sym, v)
            draw_blank(c)
            page += 1

    # 2 bonus mandalas
    for v in range(2):
        draw_coloring_page(c, page, 12, v + 10)
        draw_blank(c)
        page += 1

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
