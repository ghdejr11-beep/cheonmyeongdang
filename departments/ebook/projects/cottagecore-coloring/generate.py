"""Cottagecore Aesthetic Coloring Book - 8.5x11, 50 single-sided pages"""
import os, math
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

W, H = letter
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cottagecore_coloring.pdf")

LINE_W = 3.0
DARK = HexColor("#333333")
LIGHT_GRAY = HexColor("#F0F0F0")


def draw_title_page(c):
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setStrokeColor(black)
    c.setLineWidth(3)
    # Floral border
    for i in range(0, 36):
        angle = math.radians(i * 10)
        bx = W/2 + (W/2 - 0.6*inch) * math.cos(angle)
        by = H/2 + (H/2 - 0.6*inch) * math.sin(angle)
        c.circle(bx, by, 6, fill=0, stroke=1)
    c.setLineWidth(1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W/2, H*0.60, "Cottagecore")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W/2, H*0.54, "Coloring Book")
    c.setFont("Helvetica", 13)
    c.drawCentredString(W/2, H*0.44, "Flowers  |  Gardens  |  Tea  |  Cozy Life")
    _draw_flower(c, W/2, H*0.28, 50)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H*0.08, "Deokgu Studio")
    c.showPage()


def _draw_flower(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Petals
    for i in range(6):
        angle = math.radians(i * 60)
        px = cx + s*0.4 * math.cos(angle)
        py = cy + s*0.4 * math.sin(angle)
        c.circle(px, py, s*0.25, fill=0, stroke=1)
    # Center
    c.circle(cx, cy, s*0.18, fill=0, stroke=1)
    # Dots in center
    for i in range(6):
        angle = math.radians(i * 60 + 30)
        dx = cx + s*0.08 * math.cos(angle)
        dy = cy + s*0.08 * math.sin(angle)
        c.circle(dx, dy, s*0.02, fill=1, stroke=0)


def _draw_teacup(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Cup body
    c.ellipse(cx - s*0.4, cy - s*0.3, cx + s*0.4, cy + s*0.2, fill=0, stroke=1)
    # Rim
    c.ellipse(cx - s*0.42, cy + s*0.15, cx + s*0.42, cy + s*0.25, fill=0, stroke=1)
    # Saucer
    c.ellipse(cx - s*0.55, cy - s*0.38, cx + s*0.55, cy - s*0.28, fill=0, stroke=1)
    # Handle
    c.arc(cx + s*0.35, cy - s*0.1, cx + s*0.6, cy + s*0.2, -90, 180)
    # Steam
    for i in range(3):
        sx = cx - s*0.15 + i*s*0.15
        p = c.beginPath()
        p.moveTo(sx, cy + s*0.25)
        p.curveTo(sx + s*0.05, cy + s*0.35, sx - s*0.05, cy + s*0.45, sx, cy + s*0.55)
        c.drawPath(p, fill=0, stroke=1)
    # Decorative dots on cup
    for i in range(5):
        c.circle(cx - s*0.2 + i*s*0.1, cy, s*0.025, fill=0, stroke=1)


def _draw_cottage(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # House body
    c.rect(cx - s*0.4, cy - s*0.3, s*0.8, s*0.5, fill=0, stroke=1)
    # Roof
    p = c.beginPath()
    p.moveTo(cx - s*0.5, cy + s*0.2)
    p.lineTo(cx, cy + s*0.6)
    p.lineTo(cx + s*0.5, cy + s*0.2)
    p.close()
    c.drawPath(p, fill=0, stroke=1)
    # Door
    c.rect(cx - s*0.1, cy - s*0.3, s*0.2, s*0.3, fill=0, stroke=1)
    c.circle(cx + s*0.05, cy - s*0.15, s*0.02, fill=1, stroke=1)
    # Windows
    for dx in [-1, 1]:
        wx = cx + dx*s*0.22
        c.rect(wx - s*0.08, cy - s*0.05, s*0.16, s*0.14, fill=0, stroke=1)
        c.line(wx, cy - s*0.05, wx, cy + s*0.09)
        c.line(wx - s*0.08, cy + s*0.02, wx + s*0.08, cy + s*0.02)
    # Chimney
    c.rect(cx + s*0.2, cy + s*0.35, s*0.1, s*0.2, fill=0, stroke=1)
    # Flowers at base
    for i in range(5):
        fx = cx - s*0.35 + i*s*0.18
        c.circle(fx, cy - s*0.35, s*0.04, fill=0, stroke=1)
        c.line(fx, cy - s*0.39, fx, cy - s*0.5)


def _draw_cat(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body - sitting
    c.ellipse(cx - s*0.3, cy - s*0.4, cx + s*0.3, cy + s*0.1, fill=0, stroke=1)
    # Head
    c.circle(cx, cy + s*0.3, s*0.22, fill=0, stroke=1)
    # Ears
    for dx in [-1, 1]:
        p = c.beginPath()
        p.moveTo(cx + dx*s*0.12, cy + s*0.48)
        p.lineTo(cx + dx*s*0.08, cy + s*0.62)
        p.lineTo(cx + dx*s*0.22, cy + s*0.45)
        c.drawPath(p, fill=0, stroke=1)
    # Eyes
    for dx in [-1, 1]:
        c.circle(cx + dx*s*0.08, cy + s*0.33, s*0.035, fill=1, stroke=1)
    # Nose
    p = c.beginPath()
    p.moveTo(cx, cy + s*0.27)
    p.lineTo(cx - s*0.03, cy + s*0.24)
    p.lineTo(cx + s*0.03, cy + s*0.24)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    # Tail curving
    p = c.beginPath()
    p.moveTo(cx + s*0.25, cy - s*0.2)
    p.curveTo(cx + s*0.5, cy - s*0.1, cx + s*0.5, cy + s*0.2, cx + s*0.35, cy + s*0.25)
    c.drawPath(p, fill=0, stroke=1)


def _draw_bread(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Loaf shape
    c.ellipse(cx - s*0.4, cy - s*0.15, cx + s*0.4, cy + s*0.3, fill=0, stroke=1)
    c.rect(cx - s*0.4, cy - s*0.2, s*0.8, s*0.15, fill=0, stroke=1)
    # Score lines
    for i in range(3):
        lx = cx - s*0.2 + i*s*0.2
        c.line(lx - s*0.08, cy + s*0.05, lx + s*0.08, cy + s*0.15)
    # Steam
    for i in range(3):
        sx = cx - s*0.1 + i*s*0.1
        p = c.beginPath()
        p.moveTo(sx, cy + s*0.3)
        p.curveTo(sx + s*0.03, cy + s*0.38, sx - s*0.03, cy + s*0.45, sx, cy + s*0.52)
        c.drawPath(p, fill=0, stroke=1)


def _draw_garden_scene(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Fence
    for i in range(7):
        fx = cx - s*0.6 + i*s*0.2
        c.rect(fx - s*0.03, cy - s*0.3, s*0.06, s*0.35, fill=0, stroke=1)
        # Pointed top
        p = c.beginPath()
        p.moveTo(fx - s*0.03, cy + s*0.05)
        p.lineTo(fx, cy + s*0.12)
        p.lineTo(fx + s*0.03, cy + s*0.05)
        p.close()
        c.drawPath(p, fill=0, stroke=1)
    # Horizontal bars
    c.line(cx - s*0.6, cy - s*0.15, cx + s*0.6, cy - s*0.15)
    c.line(cx - s*0.6, cy - s*0.02, cx + s*0.6, cy - s*0.02)
    # Flowers behind fence
    for i in range(5):
        fx = cx - s*0.4 + i*s*0.2
        fy = cy + s*0.15
        c.line(fx, cy + s*0.05, fx, fy + s*0.15)
        # Flower head
        for j in range(5):
            angle = math.radians(j * 72)
            px = fx + s*0.06 * math.cos(angle)
            py = fy + s*0.15 + s*0.06 * math.sin(angle)
            c.circle(px, py, s*0.035, fill=0, stroke=1)
        c.circle(fx, fy + s*0.15, s*0.025, fill=0, stroke=1)


def _draw_mushroom(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Stem
    c.rect(cx - s*0.12, cy - s*0.35, s*0.24, s*0.4, fill=0, stroke=1)
    # Cap
    c.ellipse(cx - s*0.4, cy - s*0.05, cx + s*0.4, cy + s*0.4, fill=0, stroke=1)
    # Spots
    spots = [(-0.15, 0.2), (0.1, 0.25), (0.0, 0.12), (-0.25, 0.1), (0.2, 0.1)]
    for sx, sy in spots:
        c.circle(cx + sx*s, cy + sy*s, s*0.05, fill=0, stroke=1)
    # Grass
    for i in range(5):
        gx = cx - s*0.3 + i*s*0.15
        c.line(gx, cy - s*0.35, gx - s*0.03, cy - s*0.45)
        c.line(gx, cy - s*0.35, gx + s*0.03, cy - s*0.45)


def _draw_watering_can(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Body
    c.rect(cx - s*0.3, cy - s*0.25, s*0.6, s*0.4, fill=0, stroke=1)
    # Spout
    p = c.beginPath()
    p.moveTo(cx + s*0.3, cy + s*0.05)
    p.lineTo(cx + s*0.6, cy + s*0.3)
    p.lineTo(cx + s*0.55, cy + s*0.35)
    p.lineTo(cx + s*0.25, cy + s*0.1)
    c.drawPath(p, fill=0, stroke=1)
    # Sprinkler
    c.ellipse(cx + s*0.52, cy + s*0.28, cx + s*0.65, cy + s*0.38, fill=0, stroke=1)
    # Dots on sprinkler
    for i in range(3):
        c.circle(cx + s*0.57 + i*s*0.03, cy + s*0.33, s*0.01, fill=1, stroke=0)
    # Handle
    c.arc(cx - s*0.1, cy + s*0.15, cx + s*0.2, cy + s*0.45, 0, 180)
    # Decorative flower on body
    c.circle(cx, cy - s*0.02, s*0.06, fill=0, stroke=1)
    for j in range(5):
        angle = math.radians(j * 72)
        c.circle(cx + s*0.08*math.cos(angle), cy - s*0.02 + s*0.08*math.sin(angle),
                 s*0.035, fill=0, stroke=1)


def _draw_sunflower(c, cx, cy, s):
    c.setStrokeColor(black)
    c.setLineWidth(LINE_W)
    c.setFillColor(white)
    # Stem
    c.line(cx, cy - s*0.5, cx, cy - s*0.1)
    # Leaves
    for dx in [-1, 1]:
        ly = cy - s*0.3
        c.ellipse(cx, ly - s*0.06, cx + dx*s*0.25, ly + s*0.06, fill=0, stroke=1)
    # Petals
    for i in range(12):
        angle = math.radians(i * 30)
        px = cx + s*0.25 * math.cos(angle)
        py = cy + s*0.15 + s*0.25 * math.sin(angle)
        c.ellipse(px - s*0.06, py - s*0.12, px + s*0.06, py + s*0.0, fill=0, stroke=1)
    # Center
    c.circle(cx, cy + s*0.15, s*0.15, fill=0, stroke=1)
    # Cross-hatch center
    for i in range(4):
        for j in range(4):
            dot_x = cx - s*0.08 + i*s*0.05
            dot_y = cy + s*0.08 + j*s*0.05
            dist = math.sqrt((dot_x - cx)**2 + (dot_y - cy - s*0.15)**2)
            if dist < s*0.12:
                c.circle(dot_x, dot_y, s*0.015, fill=1, stroke=0)


COTTAGECORE = [
    ("Wildflower Bouquet", _draw_flower),
    ("Afternoon Tea", _draw_teacup),
    ("Country Cottage", _draw_cottage),
    ("Cozy Cat", _draw_cat),
    ("Fresh Bread", _draw_bread),
    ("Garden Fence", _draw_garden_scene),
    ("Forest Mushroom", _draw_mushroom),
    ("Watering Can", _draw_watering_can),
    ("Sunflower", _draw_sunflower),
]


def draw_coloring_page(c, name, draw_fn, page_num):
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H - 0.75*inch, name)
    draw_fn(c, W/2, H/2, min(W, H)*0.32)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, 0.4*inch, str(page_num))
    c.showPage()


def draw_blank_back(c):
    c.setFillColor(white)
    c.rect(0.8*inch, 0.8*inch, W - 1.6*inch, H - 1.6*inch, fill=1, stroke=0)
    c.setFillColor(LIGHT_GRAY)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H/2, "This page intentionally left blank")
    c.showPage()


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("Cottagecore Aesthetic Coloring Book")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_blank_back(c)

    for i in range(50):
        name, draw_fn = COTTAGECORE[i % len(COTTAGECORE)]
        variant = i // len(COTTAGECORE) + 1
        display = f"{name} #{variant}" if variant > 1 else name
        draw_coloring_page(c, display, draw_fn, i + 1)
        draw_blank_back(c)

    c.save()
    file_size = os.path.getsize(OUTPUT)
    print(f"PDF: {OUTPUT}")
    print(f"Pages: {c.getPageNumber() - 1}")
    print(f"Size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
