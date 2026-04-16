"""
Generate KDP front cover PDFs for all 20 ebook projects.
Each cover: background color, title, subtitle, author, geometric decorations.
Run: python generate_all_covers.py
"""

from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.pdfgen import canvas
from pathlib import Path
import os, math

BASE = Path(__file__).parent

# Size presets
SIZE_85x11 = (8.75 * inch, 11.25 * inch)  # 8.5x11 trim with bleed
SIZE_6x9   = (6.25 * inch, 9.25 * inch)   # 6x9 trim with bleed


def hex_alpha(hex_str, alpha):
    """Create a Color from hex string with alpha transparency."""
    col = HexColor(hex_str)
    return Color(col.red, col.green, col.blue, alpha)


def draw_border(c, W, H, color, width=2, margin=0.4*inch):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.rect(margin, margin, W - 2*margin, H - 2*margin)


def draw_corner_dots(c, W, H, color, margin=0.4*inch, r=4):
    c.setFillColor(color)
    for x, y in [(margin+15, H-margin-15), (W-margin-15, H-margin-15),
                  (margin+15, margin+15), (W-margin-15, margin+15)]:
        c.circle(x, y, r, fill=1)


def draw_diamond(c, cx, cy, size, color):
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(cx, cy + size)
    p.lineTo(cx + size, cy)
    p.lineTo(cx, cy - size)
    p.lineTo(cx - size, cy)
    p.close()
    c.drawPath(p, fill=1)


def draw_star(c, cx, cy, r_outer, r_inner, points, color):
    c.setFillColor(color)
    p = c.beginPath()
    for i in range(points * 2):
        angle = math.pi/2 + i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    c.drawPath(p, fill=1)


def draw_circle_pattern(c, cx, cy, count, radius, dot_r, color):
    c.setFillColor(color)
    for i in range(count):
        angle = 2 * math.pi * i / count
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        c.circle(x, y, dot_r, fill=1)


def draw_heart(c, cx, cy, size, color):
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(cx, cy - size * 0.4)
    p.curveTo(cx, cy + size * 0.6, cx - size, cy + size * 0.6, cx - size, cy)
    p.curveTo(cx - size, cy - size * 0.5, cx, cy - size, cx, cy - size * 1.2)
    p.moveTo(cx, cy - size * 0.4)
    p.curveTo(cx, cy + size * 0.6, cx + size, cy + size * 0.6, cx + size, cy)
    p.curveTo(cx + size, cy - size * 0.5, cx, cy - size, cx, cy - size * 1.2)
    p.close()
    c.drawPath(p, fill=1)


def draw_crescent_moon(c, cx, cy, r, color, bg_color):
    c.setFillColor(color)
    c.circle(cx, cy, r, fill=1)
    c.setFillColor(bg_color)
    c.circle(cx + r*0.35, cy + r*0.15, r*0.85, fill=1)


def draw_horizontal_line(c, cx, y, half_w, color, width=2):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(cx - half_w, y, cx + half_w, y)


def brightness_of(hex_str):
    r = int(hex_str[1:3], 16)
    g = int(hex_str[3:5], 16)
    b = int(hex_str[5:7], 16)
    return (r * 299 + g * 587 + b * 114) / 1000


def make_cover(folder, filename, size, bg_hex, accent_hex, title_lines, subtitle_lines,
               decor_fn=None, title_size=44, sub_size=15):
    W, H = size
    path = BASE / folder / filename
    bg = HexColor(bg_hex)
    accent = HexColor(accent_hex)
    c = canvas.Canvas(str(path), pagesize=(W, H))

    # Background
    c.setFillColor(bg)
    c.rect(0, 0, W, H, fill=1)

    # Call custom decoration
    if decor_fn:
        decor_fn(c, W, H, bg, accent)

    # Determine title color based on background brightness
    br = brightness_of(bg_hex)
    title_color = black if br > 160 else white

    # Title
    c.setFillColor(title_color)
    c.setFont("Helvetica-Bold", title_size)
    ty = H * 0.52
    for line in title_lines:
        c.drawCentredString(W/2, ty, line)
        ty -= title_size + 4

    # Decorative line under title
    draw_horizontal_line(c, W/2, ty + 2, 60, accent, 2)

    # Subtitle
    c.setFont("Helvetica", sub_size)
    c.setFillColor(accent)
    sy = ty - 16
    for line in subtitle_lines:
        c.drawCentredString(W/2, sy, line)
        sy -= sub_size + 4

    # Author
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(accent)
    c.drawCentredString(W/2, 0.45 * inch, "Deokgu Studio")

    c.save()
    fsize = os.path.getsize(path) / 1024
    print(f"  [{folder}] cover.pdf -> {fsize:.0f} KB")
    return path


# ============================================================
# DECORATION FUNCTIONS
# ============================================================

def decor_adhd(c, W, H, bg, accent):
    draw_border(c, W, H, accent)
    draw_corner_dots(c, W, H, accent)
    colors = [HexColor("#FFD700"), HexColor("#FF69B4"), HexColor("#00CED1"), accent]
    positions = [(W*0.15, H*0.8), (W*0.85, H*0.82), (W*0.1, H*0.25), (W*0.9, H*0.2)]
    for i, (x, y) in enumerate(positions):
        draw_diamond(c, x, y, 12, colors[i % len(colors)])
    draw_circle_pattern(c, W/2, H*0.72, 8, 40, 5, hex_alpha("#FFD700", 0.5))


def decor_mental(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#8B7355"), 1.5)
    c.setFillColor(HexColor("#7D9B76"))
    for x, y, a in [(W*0.2, H*0.8, 30), (W*0.8, H*0.78, -20),
                     (W*0.15, H*0.22, 45), (W*0.85, H*0.25, -35)]:
        c.saveState()
        c.translate(x, y)
        c.rotate(a)
        c.ellipse(-15, -5, 15, 5, fill=1)
        c.restoreState()
    draw_horizontal_line(c, W/2, H*0.68, 80, HexColor("#8B7355"), 1)
    draw_horizontal_line(c, W/2, H*0.35, 80, HexColor("#8B7355"), 1)


def decor_sleep(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#4169E1"), 1.5)
    draw_crescent_moon(c, W*0.5, H*0.75, 35, HexColor("#F0E68C"), bg)
    star_color = HexColor("#F0E68C")
    star_positions = [(W*0.2, H*0.85), (W*0.75, H*0.88), (W*0.3, H*0.72),
                      (W*0.8, H*0.7), (W*0.15, H*0.65), (W*0.9, H*0.8),
                      (W*0.5, H*0.9), (W*0.65, H*0.78)]
    for i, (x, y) in enumerate(star_positions):
        sz = 6 + (i % 3) * 3
        draw_star(c, x, y, sz, sz*0.4, 5, star_color)


def decor_ai(c, W, H, bg, accent):
    draw_border(c, W, H, accent, 2, 0.35*inch)
    c.setStrokeColor(hex_alpha("#FFD700", 0.3))
    c.setLineWidth(1)
    for y_frac in [0.75, 0.78, 0.81]:
        c.line(W*0.15, H*y_frac, W*0.85, H*y_frac)
    c.setFillColor(accent)
    for x in [0.2, 0.35, 0.5, 0.65, 0.8]:
        for y in [0.75, 0.78, 0.81]:
            c.circle(W*x, H*y, 3, fill=1)
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(hex_alpha("#FFD700", 0.4))
    for x, y in [(W*0.15, H*0.28), (W*0.85, H*0.3)]:
        c.drawCentredString(x, y, "$")


def decor_dots(c, W, H, bg, accent):
    import random
    random.seed(42)
    colors = [HexColor("#FF6B6B"), HexColor("#4ECDC4"), HexColor("#45B7D1"),
              HexColor("#96CEB4"), HexColor("#FFEAA7"), HexColor("#DDA0DD"),
              HexColor("#FF8C00"), HexColor("#7FFF00")]
    for _ in range(30):
        x = random.uniform(W*0.05, W*0.95)
        y_top = random.uniform(H*0.7, H*0.95)
        y_bot = random.uniform(H*0.05, H*0.3)
        r = random.uniform(10, 25)
        col = random.choice(colors)
        c.setFillColor(col)
        c.circle(x, y_top, r, fill=1, stroke=0)
        c.circle(x + random.uniform(-30, 30), y_bot, r*0.8, fill=1, stroke=0)


def decor_spot(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#20B2AA"), 2)
    cx, cy = W/2, H*0.72
    c.setStrokeColor(HexColor("#20B2AA"))
    c.setLineWidth(4)
    c.circle(cx, cy, 30, fill=0)
    c.line(cx+22, cy-22, cx+42, cy-42)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(hex_alpha("#20B2AA", 0.5))
    for x, y in [(W*0.15, H*0.8), (W*0.85, H*0.78), (W*0.2, H*0.25), (W*0.8, H*0.22)]:
        c.drawCentredString(x, y, "?")


def decor_genz(c, W, H, bg, accent):
    for i in range(5):
        c.setFillColor(hex_alpha("#FF6B6B", 0.1 + i * 0.03))
        c.rect(0, H - (i+1)*20, W, 20, fill=1, stroke=0)
        c.rect(0, i*20, W, 20, fill=1, stroke=0)
    draw_border(c, W, H, HexColor("#FF8C94"), 1.5)
    c.setFillColor(HexColor("#FFD700"))
    for x, dy in [(W*0.15, 0), (W*0.85, 10)]:
        y = H*0.75 + dy
        p = c.beginPath()
        p.moveTo(x, y+20)
        p.lineTo(x+8, y+5)
        p.lineTo(x+3, y+5)
        p.lineTo(x+10, y-15)
        p.lineTo(x+2, y)
        p.lineTo(x+7, y)
        p.close()
        c.drawPath(p, fill=1)


def decor_introvert(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#87CEEB"), 1.5, 0.35*inch)
    cx, cy = W/2, H*0.73
    c.setFillColor(hex_alpha("#87CEEB", 0.4))
    c.ellipse(cx-25, cy-5, cx-3, cy+20, fill=1, stroke=0)
    c.ellipse(cx+3, cy-5, cx+25, cy+20, fill=1, stroke=0)
    c.ellipse(cx-18, cy-15, cx-3, cy, fill=1, stroke=0)
    c.ellipse(cx+3, cy-15, cx+18, cy, fill=1, stroke=0)


def decor_premium(c, W, H, bg, accent):
    m1, m2 = 0.35*inch, 0.5*inch
    c.setStrokeColor(accent)
    c.setLineWidth(3)
    c.rect(m1, m1, W-2*m1, H-2*m1)
    c.setLineWidth(1)
    c.rect(m2, m2, W-2*m2, H-2*m2)
    draw_corner_dots(c, W, H, accent, m1, 5)
    cx, cy = W/2, H*0.72
    c.setFillColor(accent)
    p = c.beginPath()
    p.moveTo(cx, cy+35)
    p.lineTo(cx+30, cy+20)
    p.lineTo(cx+30, cy-10)
    p.lineTo(cx, cy-30)
    p.lineTo(cx-30, cy-10)
    p.lineTo(cx-30, cy+20)
    p.close()
    c.drawPath(p, fill=1)
    c.setFillColor(bg)
    c.roundRect(cx-10, cy-8, 20, 18, 3, fill=1)
    c.setStrokeColor(bg)
    c.setLineWidth(3)
    c.arc(cx-7, cy+8, cx+7, cy+22, 0, 180)


def decor_bp(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#DC143C"), 2)
    cx, cy = W/2, H*0.73
    draw_heart(c, cx, cy, 30, HexColor("#DC143C"))
    c.setStrokeColor(HexColor("#DC143C"))
    c.setLineWidth(2)
    pts = [(W*0.2, H*0.65), (W*0.3, H*0.65), (W*0.35, H*0.68),
           (W*0.4, H*0.6), (W*0.45, H*0.7), (W*0.5, H*0.62),
           (W*0.55, H*0.65), (W*0.7, H*0.65), (W*0.8, H*0.65)]
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    c.drawPath(p, fill=0)


def decor_sugar(c, W, H, bg, accent):
    draw_border(c, W, H, accent, 2)
    cx, cy = W/2, H*0.73
    c.setFillColor(accent)
    c.rect(cx-8, cy-20, 16, 40, fill=1)
    c.rect(cx-20, cy-8, 40, 16, fill=1)
    c.setStrokeColor(hex_alpha("#20B2AA", 0.5))
    c.setLineWidth(1)
    for y_off in range(-30, 31, 15):
        c.setDash(3, 3)
        c.line(W*0.2, H*0.63 + y_off, W*0.8, H*0.63 + y_off)
    c.setDash()


def decor_airbnb(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#8B4513"), 1.5, 0.35*inch)
    cx, cy = W/2, H*0.73
    c.setFillColor(HexColor("#8B4513"))
    p = c.beginPath()
    p.moveTo(cx-35, cy+5)
    p.lineTo(cx, cy+30)
    p.lineTo(cx+35, cy+5)
    p.close()
    c.drawPath(p, fill=1)
    c.rect(cx-25, cy-20, 50, 27, fill=1)
    c.setFillColor(bg)
    c.rect(cx-8, cy-20, 16, 20, fill=1)
    c.setFillColor(HexColor("#D2691E"))
    for x_off in range(-20, 25, 10):
        c.circle(cx + x_off, cy - 25, 2, fill=1)


def decor_animals(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#228B22"), 2)
    # Cat silhouette
    cx, cy = W*0.25, H*0.78
    c.setFillColor(hex_alpha("#228B22", 0.4))
    c.ellipse(cx-15, cy-10, cx+15, cy+10, fill=1, stroke=0)
    c.circle(cx, cy+18, 10, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(cx-8, cy+25); p.lineTo(cx-3, cy+35); p.lineTo(cx+2, cy+25)
    c.drawPath(p, fill=1)
    p = c.beginPath()
    p.moveTo(cx+2, cy+25); p.lineTo(cx+7, cy+35); p.lineTo(cx+12, cy+25)
    c.drawPath(p, fill=1)
    # Bird silhouette
    bx, by = W*0.75, H*0.8
    c.setFillColor(hex_alpha("#228B22", 0.4))
    c.ellipse(bx-12, by-8, bx+12, by+8, fill=1, stroke=0)
    c.circle(bx+8, by+10, 7, fill=1, stroke=0)
    c.ellipse(bx-15, by-2, bx+5, by+10, fill=1, stroke=0)
    # Paw prints
    c.setFillColor(hex_alpha("#228B22", 0.25))
    for x in [W*0.2, W*0.4, W*0.6, W*0.8]:
        c.circle(x, H*0.18, 8, fill=1, stroke=0)
        for dx, dy in [(-5, 8), (5, 8), (-8, 3), (8, 3)]:
            c.circle(x+dx, H*0.18+dy, 3, fill=1, stroke=0)


def decor_cottage(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#DB7093"), 1.5)
    flower_color = HexColor("#DB7093")
    center_color = HexColor("#FFD700")
    for fx, fy in [(W*0.2, H*0.82), (W*0.8, H*0.85), (W*0.5, H*0.78),
                   (W*0.15, H*0.2), (W*0.85, H*0.18), (W*0.5, H*0.22)]:
        c.setFillColor(flower_color)
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            px = fx + 12 * math.cos(rad)
            py = fy + 12 * math.sin(rad)
            c.circle(px, py, 6, fill=1, stroke=0)
        c.setFillColor(center_color)
        c.circle(fx, fy, 4, fill=1, stroke=0)


def decor_math(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#1E90FF"), 2)
    c.setFont("Helvetica-Bold", 36)
    symbols = [("+", W*0.15, H*0.82), ("-", W*0.85, H*0.8),
               ("x", W*0.2, H*0.2), ("=", W*0.8, H*0.22),
               ("/", W*0.12, H*0.5), ("+", W*0.88, H*0.5)]
    colors = [HexColor("#FF6B6B"), HexColor("#4ECDC4"), HexColor("#FFD700"),
              HexColor("#FF69B4"), HexColor("#45B7D1"), HexColor("#96CEB4")]
    for (sym, x, y), col in zip(symbols, colors):
        c.setFillColor(col)
        c.drawCentredString(x, y, sym)
    for x, y in [(W*0.3, H*0.88), (W*0.7, H*0.88)]:
        draw_star(c, x, y, 15, 6, 5, HexColor("#FFD700"))


def decor_yoga(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#20B2AA"), 1.5, 0.35*inch)
    cx, cy = W/2, H*0.73
    c.setFillColor(hex_alpha("#DDA0DD", 0.5))
    for angle in range(0, 360, 45):
        c.saveState()
        c.translate(cx, cy)
        c.rotate(angle)
        c.ellipse(-5, 5, 5, 28, fill=1, stroke=0)
        c.restoreState()
    c.setFillColor(HexColor("#FFD700"))
    c.circle(cx, cy, 6, fill=1, stroke=0)
    c.setStrokeColor(hex_alpha("#20B2AA", 0.4))
    c.setLineWidth(1)
    c.circle(cx, cy, 40, fill=0)


def decor_budget(c, W, H, bg, accent):
    draw_border(c, W, H, accent, 2)
    draw_corner_dots(c, W, H, accent)
    c.setStrokeColor(accent)
    c.setLineWidth(2)
    for x, y in [(W*0.25, H*0.78), (W*0.75, H*0.76)]:
        c.circle(x, y, 18, fill=0)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(accent)
        c.drawCentredString(x, y-5, "$")
    cx, cy = W/2, H*0.73
    c.setStrokeColor(accent)
    c.setLineWidth(2)
    c.circle(cx-12, cy, 18, fill=0)
    c.circle(cx+12, cy, 18, fill=0)


def decor_zodiac(c, W, H, bg, accent):
    draw_border(c, W, H, accent, 2)
    cx, cy = W/2, H*0.73
    c.setStrokeColor(accent)
    c.setLineWidth(1)
    for r in [20, 35, 50]:
        c.circle(cx, cy, r, fill=0)
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = cx + 20 * math.cos(rad)
        y1 = cy + 20 * math.sin(rad)
        x2 = cx + 50 * math.cos(rad)
        y2 = cy + 50 * math.sin(rad)
        c.line(x1, y1, x2, y2)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        x = cx + 55 * math.cos(rad)
        y = cy + 55 * math.sin(rad)
        draw_star(c, x, y, 6, 2.5, 5, accent)


def decor_meal(c, W, H, bg, accent):
    draw_border(c, W, H, HexColor("#228B22"), 2)
    cx, cy = W/2, H*0.73
    c.setStrokeColor(HexColor("#228B22"))
    c.setLineWidth(3)
    c.line(cx+15, cy-25, cx+15, cy+25)
    c.line(cx-15, cy-25, cx-15, cy+10)
    c.line(cx-15, cy+10, cx-20, cy+25)
    c.line(cx-15, cy+10, cx-10, cy+25)
    c.line(cx-15, cy+10, cx-15, cy+25)
    c.setLineWidth(2)
    c.circle(cx, cy, 35, fill=0)
    c.setFillColor(hex_alpha("#228B22", 0.4))
    for x, y, a in [(W*0.15, H*0.85, 30), (W*0.85, H*0.83, -30),
                     (W*0.1, H*0.2, 45), (W*0.9, H*0.18, -45)]:
        c.saveState()
        c.translate(x, y)
        c.rotate(a)
        c.ellipse(-12, -4, 12, 4, fill=1, stroke=0)
        c.restoreState()


# ============================================================
# BOOK DEFINITIONS
# ============================================================
BOOKS = [
    # (folder, size, bg_hex, accent_hex, title_lines, subtitle_lines, decor_fn, title_size)
    ("adhd-planner", SIZE_85x11, "#6A0DAD", "#FFD700",
     ["ADHD DAILY", "PLANNER"],
     ["Stay Focused, Stay Organized", "A Practical Planning System for ADHD Minds"],
     decor_adhd, 46),

    ("mental-reset-journal", SIZE_85x11, "#A8B89C", "#5C4033",
     ["MENTAL", "RESET", "JOURNAL"],
     ["Clear Your Mind, Reclaim Your Peace", "A 90-Day Guided Journal"],
     decor_mental, 42),

    ("sleep-planner", SIZE_85x11, "#0B0B3B", "#F0E68C",
     ["SLEEP", "PLANNER"],
     ["Track Your Nights, Transform Your Days", "A Complete Sleep Tracking System"],
     decor_sleep, 48),

    ("ai-side-hustle-en", SIZE_6x9, "#0D1B2A", "#FFD700",
     ["AI SIDE", "HUSTLE"],
     ["How to Make Money with AI", "A Step-by-Step Guide to AI-Powered Income"],
     decor_ai, 38),

    ("dot-marker-kids", SIZE_85x11, "#FF4444", "#FFFFFF",
     ["DOT MARKER", "ACTIVITY", "BOOK"],
     ["Fun Coloring for Toddlers!", "Ages 2-5"],
     decor_dots, 44),

    ("spot-difference-seniors", SIZE_85x11, "#1A3A4A", "#20B2AA",
     ["SPOT THE", "DIFFERENCE"],
     ["Large Print Puzzle Book", "For Adults & Seniors"],
     decor_spot, 44),

    ("genz-stress", SIZE_85x11, "#4A0E4E", "#FF8C94",
     ["GEN Z", "STRESS", "RELIEF"],
     ["A No-BS Guide to Chilling Out", "Journaling, Doodling & De-Stressing"],
     decor_genz, 44),

    ("introvert-confidence", SIZE_6x9, "#2C3E6B", "#87CEEB",
     ["THE QUIET", "CONFIDENCE", "JOURNAL"],
     ["Build Inner Strength", "Without Changing Who You Are"],
     decor_introvert, 34),

    ("password-logbook-premium", SIZE_85x11, "#0F0F2E", "#D4A843",
     ["PASSWORD", "LOGBOOK", "PREMIUM"],
     ["Internet Password Organizer", "Large Print  |  A-Z Tabs  |  180+ Pages"],
     decor_premium, 44),

    ("blood-pressure-log", SIZE_85x11, "#FFFFFF", "#DC143C",
     ["BLOOD", "PRESSURE", "LOG"],
     ["Daily Blood Pressure Tracker", "Monitor Your Health Every Day"],
     decor_bp, 46),

    ("blood-sugar-tracker", SIZE_85x11, "#F0FFFF", "#20B2AA",
     ["BLOOD SUGAR", "TRACKER"],
     ["Daily Glucose Monitoring Log", "Track Meals, Insulin & Levels"],
     decor_sugar, 44),

    ("airbnb-guestbook", SIZE_6x9, "#FFF5E6", "#D2691E",
     ["WELCOME", "GUEST BOOK"],
     ["A Keepsake for Your Airbnb", "Vacation Rental & Guest House"],
     decor_airbnb, 36),

    ("bold-easy-coloring-animals", SIZE_85x11, "#7CFC00", "#006400",
     ["BOLD & EASY", "COLORING", "ANIMALS"],
     ["Simple Designs for All Ages", "Large Print  |  Stress-Free Fun"],
     decor_animals, 40),

    ("cottagecore-coloring", SIZE_85x11, "#FFE4E1", "#DB7093",
     ["COTTAGECORE", "COLORING", "BOOK"],
     ["Whimsical Floral & Country Designs", "Relaxing Pages for All Ages"],
     decor_cottage, 40),

    ("math-workbook-grade1", SIZE_85x11, "#4169E1", "#FFFFFF",
     ["MATH", "WORKBOOK", "GRADE 1"],
     ["Addition, Subtraction & More!", "Fun Practice for Young Learners"],
     decor_math, 44),

    ("yoga-progress-journal", SIZE_6x9, "#E6E6FA", "#20B2AA",
     ["YOGA", "PROGRESS", "JOURNAL"],
     ["Track Your Practice", "Mind, Body & Spirit"],
     decor_yoga, 34),

    ("budget-planner-couples", SIZE_85x11, "#0F0F2E", "#D4A843",
     ["BUDGET", "PLANNER", "FOR COUPLES"],
     ["Plan Together, Grow Together", "Monthly Finance Tracker & Goal Setter"],
     decor_budget, 42),

    ("zodiac-mandala-coloring", SIZE_85x11, "#1A0A2E", "#D4A843",
     ["ZODIAC", "MANDALA", "COLORING"],
     ["Mystical Astrology Designs", "Relaxing Mandala Art for Adults"],
     decor_zodiac, 42),

    ("meal-prep-planner", SIZE_85x11, "#F5F5DC", "#228B22",
     ["MEAL PREP", "PLANNER"],
     ["Plan, Shop, Cook, Repeat", "Weekly Meal Planning Made Simple"],
     decor_meal, 46),
]


def main():
    print("=" * 50)
    print("Generating KDP Cover PDFs for 20 books...")
    print("=" * 50)

    # password-logbook already has its own script
    print("\n[1/20] password-logbook -- running existing generate_cover.py")
    import subprocess, sys
    pw_script = BASE / "password-logbook" / "generate_cover.py"
    subprocess.run([sys.executable, str(pw_script)], cwd=str(BASE / "password-logbook"))

    for i, (folder, size, bg_hex, accent_hex, titles, subs, decor, tsize) in enumerate(BOOKS, 2):
        print(f"\n[{i}/20] {folder}")
        try:
            make_cover(folder, "cover.pdf", size, bg_hex, accent_hex,
                       titles, subs, decor, tsize)
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()

    print("\n" + "=" * 50)
    print("Done! Checking generated files...")
    print("=" * 50)
    all_ok = True
    for folder in ["password-logbook"] + [b[0] for b in BOOKS]:
        if folder == "password-logbook":
            # Check both possible names
            pdf1 = BASE / folder / "Password_Logbook_Cover.pdf"
            pdf2 = BASE / folder / "cover.pdf"
            exists = pdf1.exists() or pdf2.exists()
        else:
            pdf = BASE / folder / "cover.pdf"
            exists = pdf.exists()
        status = "OK" if exists else "MISSING"
        if not exists:
            all_ok = False
        print(f"  {folder}: {status}")

    if all_ok:
        print("\nAll 20 covers generated successfully!")
    else:
        print("\nSome covers are missing - check errors above.")


if __name__ == "__main__":
    main()
