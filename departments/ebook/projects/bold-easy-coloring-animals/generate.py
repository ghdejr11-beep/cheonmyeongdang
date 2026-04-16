"""Bold and Easy Coloring Book: Animals - 8.5x11, 50 single-sided pages + blanks"""
import os, math, random
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bold_easy_coloring_animals.pdf")
random.seed(42)

DARK = HexColor("#333333")
LIGHT_GRAY = HexColor("#F0F0F0")

LINE_W = 3.5  # Bold thick lines


def draw_title_page(c):
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setStrokeColor(black)
    c.setLineWidth(4)
    c.rect(0.75*inch, 0.75*inch, W-1.5*inch, H-1.5*inch, stroke=1, fill=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(W/2, H*0.65, "Bold & Easy")
    c.drawCentredString(W/2, H*0.65 - 40, "Coloring Book")
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W/2, H*0.50, "ANIMALS")
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H*0.40, "50 Simple Designs with Thick Lines")
    c.drawCentredString(W/2, H*0.36, "For Adults, Seniors & Beginners")
    # Simple geometric animal on cover
    cx, cy = W/2, H*0.22
    _draw_geometric_cat(c, cx, cy, 60)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H*0.08, "Deokgu Studio")
    c.showPage()


def _draw_geometric_cat(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body - circle
    c.circle(cx, cy, s*0.6, fill=0, stroke=1)
    # Head - circle
    c.circle(cx, cy + s*0.9, s*0.4, fill=0, stroke=1)
    # Ears - triangles
    for dx in [-1, 1]:
        ear_x = cx + dx * s * 0.3
        ear_y = cy + s * 1.3
        p = c.beginPath()
        p.moveTo(ear_x - s*0.12, ear_y - s*0.1)
        p.lineTo(ear_x, ear_y + s*0.2)
        p.lineTo(ear_x + s*0.12, ear_y - s*0.1)
        p.close()
        c.drawPath(p, fill=0, stroke=1)
    # Eyes
    for dx in [-1, 1]:
        c.circle(cx + dx * s * 0.15, cy + s * 0.95, s * 0.06, fill=1, stroke=1)
    # Nose
    p = c.beginPath()
    p.moveTo(cx, cy + s*0.85)
    p.lineTo(cx - s*0.05, cy + s*0.80)
    p.lineTo(cx + s*0.05, cy + s*0.80)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    # Whiskers
    for dx in [-1, 1]:
        for dy in [-0.03, 0.03]:
            c.line(cx + dx * s * 0.1, cy + s * 0.82 + dy * s,
                   cx + dx * s * 0.4, cy + s * 0.82 + dy * s * 3)


def draw_geometric_fish(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body - ellipse via oval
    c.ellipse(cx - s*0.7, cy - s*0.35, cx + s*0.5, cy + s*0.35, fill=0, stroke=1)
    # Tail
    p = c.beginPath()
    p.moveTo(cx + s*0.4, cy)
    p.lineTo(cx + s*0.8, cy + s*0.3)
    p.lineTo(cx + s*0.8, cy - s*0.3)
    p.close()
    c.drawPath(p, fill=0, stroke=1)
    # Eye
    c.circle(cx - s*0.35, cy + s*0.05, s*0.06, fill=1, stroke=1)
    # Fin
    p = c.beginPath()
    p.moveTo(cx - s*0.1, cy + s*0.1)
    p.lineTo(cx, cy + s*0.4)
    p.lineTo(cx + s*0.15, cy + s*0.1)
    c.drawPath(p, fill=0, stroke=1)
    # Scales - arcs
    for i in range(3):
        for j in range(2):
            sx = cx - s*0.4 + i * s * 0.25
            sy = cy - s*0.1 + j * s * 0.15
            c.arc(sx - s*0.08, sy - s*0.08, sx + s*0.08, sy + s*0.08, 0, 180)


def draw_geometric_owl(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body
    c.ellipse(cx - s*0.5, cy - s*0.7, cx + s*0.5, cy + s*0.3, fill=0, stroke=1)
    # Head
    c.circle(cx, cy + s*0.55, s*0.35, fill=0, stroke=1)
    # Ears
    for dx in [-1, 1]:
        p = c.beginPath()
        p.moveTo(cx + dx*s*0.2, cy + s*0.85)
        p.lineTo(cx + dx*s*0.15, cy + s*1.05)
        p.lineTo(cx + dx*s*0.35, cy + s*0.8)
        c.drawPath(p, fill=0, stroke=1)
    # Eyes - big circles
    for dx in [-1, 1]:
        c.circle(cx + dx*s*0.15, cy + s*0.58, s*0.14, fill=0, stroke=1)
        c.circle(cx + dx*s*0.15, cy + s*0.58, s*0.06, fill=1, stroke=1)
    # Beak
    p = c.beginPath()
    p.moveTo(cx, cy + s*0.48)
    p.lineTo(cx - s*0.06, cy + s*0.40)
    p.lineTo(cx + s*0.06, cy + s*0.40)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    # Wing patterns
    for dx in [-1, 1]:
        for i in range(3):
            wy = cy - s*0.1 - i*s*0.15
            c.arc(cx + dx*s*0.15 - s*0.12, wy - s*0.06,
                  cx + dx*s*0.15 + s*0.12, wy + s*0.06, 0 if dx > 0 else 180, 180)


def draw_geometric_butterfly(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body
    c.ellipse(cx - s*0.06, cy - s*0.5, cx + s*0.06, cy + s*0.3, fill=0, stroke=1)
    # Wings
    for dx in [-1, 1]:
        # Upper wing
        c.ellipse(cx + dx*s*0.05, cy, cx + dx*s*0.7, cy + s*0.5, fill=0, stroke=1)
        # Lower wing
        c.ellipse(cx + dx*s*0.05, cy - s*0.45, cx + dx*s*0.55, cy + s*0.05, fill=0, stroke=1)
        # Wing patterns
        c.circle(cx + dx*s*0.35, cy + s*0.25, s*0.1, fill=0, stroke=1)
        c.circle(cx + dx*s*0.28, cy - s*0.15, s*0.08, fill=0, stroke=1)
    # Antennae
    for dx in [-1, 1]:
        c.line(cx, cy + s*0.3, cx + dx*s*0.2, cy + s*0.6)
        c.circle(cx + dx*s*0.2, cy + s*0.6, s*0.03, fill=1, stroke=1)


def draw_geometric_turtle(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Shell
    c.ellipse(cx - s*0.5, cy - s*0.2, cx + s*0.5, cy + s*0.5, fill=0, stroke=1)
    # Shell pattern - hexagons approximated by circles
    c.circle(cx, cy + s*0.15, s*0.18, fill=0, stroke=1)
    for angle in range(0, 360, 60):
        px = cx + s*0.25 * math.cos(math.radians(angle))
        py = cy + s*0.15 + s*0.25 * math.sin(math.radians(angle))
        c.circle(px, py, s*0.1, fill=0, stroke=1)
    # Head
    c.circle(cx + s*0.55, cy + s*0.2, s*0.15, fill=0, stroke=1)
    c.circle(cx + s*0.60, cy + s*0.24, s*0.03, fill=1, stroke=1)
    # Legs
    for pos in [(-0.35, -0.2), (0.35, -0.2), (-0.2, -0.25), (0.2, -0.25)]:
        c.ellipse(cx + pos[0]*s - s*0.08, cy + pos[1]*s - s*0.12,
                  cx + pos[0]*s + s*0.08, cy + pos[1]*s + s*0.02, fill=0, stroke=1)
    # Tail
    c.line(cx - s*0.5, cy + s*0.15, cx - s*0.6, cy + s*0.1)


def draw_geometric_elephant(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body
    c.ellipse(cx - s*0.5, cy - s*0.3, cx + s*0.4, cy + s*0.4, fill=0, stroke=1)
    # Head
    c.circle(cx + s*0.5, cy + s*0.25, s*0.3, fill=0, stroke=1)
    # Ear
    c.ellipse(cx + s*0.7, cy + s*0.1, cx + s*1.0, cy + s*0.5, fill=0, stroke=1)
    # Trunk
    p = c.beginPath()
    p.moveTo(cx + s*0.65, cy + s*0.0)
    p.curveTo(cx + s*0.75, cy - s*0.2, cx + s*0.6, cy - s*0.4, cx + s*0.5, cy - s*0.5)
    c.drawPath(p, fill=0, stroke=1)
    # Eye
    c.circle(cx + s*0.55, cy + s*0.3, s*0.04, fill=1, stroke=1)
    # Legs
    for lx in [-0.3, -0.1, 0.1, 0.3]:
        c.rect(cx + lx*s - s*0.06, cy - s*0.55, s*0.12, s*0.25, fill=0, stroke=1)
    # Tail
    c.line(cx - s*0.5, cy + s*0.1, cx - s*0.65, cy + s*0.2)


def draw_geometric_bird(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body
    c.ellipse(cx - s*0.3, cy - s*0.25, cx + s*0.3, cy + s*0.25, fill=0, stroke=1)
    # Head
    c.circle(cx + s*0.35, cy + s*0.25, s*0.18, fill=0, stroke=1)
    # Eye
    c.circle(cx + s*0.38, cy + s*0.28, s*0.04, fill=1, stroke=1)
    # Beak
    p = c.beginPath()
    p.moveTo(cx + s*0.52, cy + s*0.25)
    p.lineTo(cx + s*0.7, cy + s*0.22)
    p.lineTo(cx + s*0.52, cy + s*0.19)
    p.close()
    c.drawPath(p, fill=0, stroke=1)
    # Wing
    c.ellipse(cx - s*0.15, cy - s*0.05, cx + s*0.25, cy + s*0.2, fill=0, stroke=1)
    # Tail
    for i in range(3):
        angle = math.radians(150 + i*15)
        c.line(cx - s*0.3, cy, cx - s*0.3 + s*0.35*math.cos(angle), cy + s*0.35*math.sin(angle))
    # Legs
    c.line(cx - s*0.05, cy - s*0.25, cx - s*0.05, cy - s*0.5)
    c.line(cx + s*0.05, cy - s*0.25, cx + s*0.05, cy - s*0.5)
    # Feet
    for dx in [-0.05, 0.05]:
        fx = cx + dx*s
        c.line(fx, cy - s*0.5, fx - s*0.08, cy - s*0.55)
        c.line(fx, cy - s*0.5, fx + s*0.08, cy - s*0.55)


def draw_geometric_dog(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body
    c.ellipse(cx - s*0.5, cy - s*0.2, cx + s*0.3, cy + s*0.3, fill=0, stroke=1)
    # Head
    c.circle(cx + s*0.4, cy + s*0.3, s*0.25, fill=0, stroke=1)
    # Ears
    for dx in [-1, 1]:
        c.ellipse(cx + s*0.4 + dx*s*0.2 - s*0.1, cy + s*0.48,
                  cx + s*0.4 + dx*s*0.2 + s*0.1, cy + s*0.7, fill=0, stroke=1)
    # Eyes
    c.circle(cx + s*0.35, cy + s*0.35, s*0.04, fill=1, stroke=1)
    c.circle(cx + s*0.45, cy + s*0.35, s*0.04, fill=1, stroke=1)
    # Nose
    c.circle(cx + s*0.42, cy + s*0.22, s*0.04, fill=1, stroke=1)
    # Legs
    for lx in [-0.35, -0.15, 0.05, 0.2]:
        c.rect(cx + lx*s - s*0.05, cy - s*0.5, s*0.1, s*0.3, fill=0, stroke=1)
    # Tail
    p = c.beginPath()
    p.moveTo(cx - s*0.5, cy + s*0.1)
    p.curveTo(cx - s*0.65, cy + s*0.3, cx - s*0.7, cy + s*0.5, cx - s*0.6, cy + s*0.55)
    c.drawPath(p, fill=0, stroke=1)


def draw_geometric_rabbit(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body
    c.ellipse(cx - s*0.35, cy - s*0.4, cx + s*0.35, cy + s*0.2, fill=0, stroke=1)
    # Head
    c.circle(cx, cy + s*0.4, s*0.25, fill=0, stroke=1)
    # Ears
    for dx in [-1, 1]:
        c.ellipse(cx + dx*s*0.1 - s*0.07, cy + s*0.6,
                  cx + dx*s*0.1 + s*0.07, cy + s*1.0, fill=0, stroke=1)
        c.ellipse(cx + dx*s*0.1 - s*0.03, cy + s*0.65,
                  cx + dx*s*0.1 + s*0.03, cy + s*0.95, fill=0, stroke=1)
    # Eyes
    for dx in [-1, 1]:
        c.circle(cx + dx*s*0.1, cy + s*0.44, s*0.04, fill=1, stroke=1)
    # Nose
    p = c.beginPath()
    p.moveTo(cx, cy + s*0.35)
    p.lineTo(cx - s*0.04, cy + s*0.32)
    p.lineTo(cx + s*0.04, cy + s*0.32)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    # Whiskers
    for dx in [-1, 1]:
        c.line(cx + dx*s*0.05, cy + s*0.34, cx + dx*s*0.25, cy + s*0.36)
        c.line(cx + dx*s*0.05, cy + s*0.32, cx + dx*s*0.25, cy + s*0.30)
    # Feet
    c.ellipse(cx - s*0.25, cy - s*0.5, cx - s*0.05, cy - s*0.38, fill=0, stroke=1)
    c.ellipse(cx + s*0.05, cy - s*0.5, cx + s*0.25, cy - s*0.38, fill=0, stroke=1)
    # Tail
    c.circle(cx - s*0.3, cy - s*0.2, s*0.08, fill=0, stroke=1)


def draw_geometric_lion(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Mane - big circle
    c.circle(cx, cy + s*0.2, s*0.5, fill=0, stroke=1)
    # Mane rays
    for angle in range(0, 360, 20):
        r1 = s * 0.5
        r2 = s * 0.6
        x1 = cx + r1 * math.cos(math.radians(angle))
        y1 = cy + s*0.2 + r1 * math.sin(math.radians(angle))
        x2 = cx + r2 * math.cos(math.radians(angle))
        y2 = cy + s*0.2 + r2 * math.sin(math.radians(angle))
        c.line(x1, y1, x2, y2)
    # Face
    c.circle(cx, cy + s*0.2, s*0.3, fill=0, stroke=1)
    # Eyes
    for dx in [-1, 1]:
        c.circle(cx + dx*s*0.1, cy + s*0.28, s*0.04, fill=1, stroke=1)
    # Nose
    p = c.beginPath()
    p.moveTo(cx, cy + s*0.18)
    p.lineTo(cx - s*0.05, cy + s*0.13)
    p.lineTo(cx + s*0.05, cy + s*0.13)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    # Mouth
    c.arc(cx - s*0.06, cy + s*0.05, cx, cy + s*0.13, 180, 180)
    c.arc(cx, cy + s*0.05, cx + s*0.06, cy + s*0.13, 180, 180)
    # Body
    c.ellipse(cx - s*0.3, cy - s*0.5, cx + s*0.3, cy - s*0.1, fill=0, stroke=1)
    # Legs
    for lx in [-0.15, 0.15]:
        c.rect(cx + lx*s - s*0.06, cy - s*0.75, s*0.12, s*0.25, fill=0, stroke=1)


# Animal drawing functions list
ANIMALS = [
    ("Cat", _draw_geometric_cat),
    ("Fish", draw_geometric_fish),
    ("Owl", draw_geometric_owl),
    ("Butterfly", draw_geometric_butterfly),
    ("Turtle", draw_geometric_turtle),
    ("Elephant", draw_geometric_elephant),
    ("Bird", draw_geometric_bird),
    ("Dog", draw_geometric_dog),
    ("Rabbit", draw_geometric_rabbit),
    ("Lion", draw_geometric_lion),
]


def draw_coloring_page(c, name, draw_fn, page_num):
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    # Animal name at top
    c.setFillColor(DARK)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H - 0.75*inch, name)
    # Draw the animal centered
    draw_fn(c, W/2, H/2, min(W, H) * 0.3)
    # Page number
    c.setFont("Helvetica", 8)
    c.setFillColor(DARK)
    c.drawCentredString(W/2, 0.5*inch, str(page_num))
    c.showPage()


def draw_blank_back(c):
    """Blank page for single-sided printing"""
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(LIGHT_GRAY)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H/2, "This page intentionally left blank")
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Bold and Easy Coloring Book: Animals")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_blank_back(c)

    # 50 coloring pages (cycling through 10 animals, 5 times with slight variation)
    for i in range(50):
        name, draw_fn = ANIMALS[i % len(ANIMALS)]
        variant = i // len(ANIMALS) + 1
        if variant > 1:
            display_name = f"{name} #{variant}"
        else:
            display_name = name
        draw_coloring_page(c, display_name, draw_fn, i + 1)
        draw_blank_back(c)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
