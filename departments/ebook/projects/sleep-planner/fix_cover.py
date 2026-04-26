"""
Sleep Improvement Planner — full-wrap cover 수정 재생성

KDP 거절 원인 수정:
1. Spine 상하 0.5" 안전 마진 확보 (KDP 최소 0.375")
2. "ISBN Barcode Area" 박스 및 텍스트 완전 제거 (템플릿 텍스트 금지)
3. Deokgu Studio 저자명 유지
"""
import math, os
from pathlib import Path
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader

BASE = Path(__file__).parent
INTERIOR = BASE / "Sleep_Planner_Interior.pdf"
OUTPUT = BASE / "cover.pdf"

TRIM_W, TRIM_H = 8.5, 11.0
BLEED = 0.125
SPINE_SAFE = 0.5  # inch — 상하 안전 마진

BG = HexColor("#0B0B3B")
ACCENT = HexColor("#F0E68C")
MOON_COLOR = HexColor("#F0E68C")
BORDER = HexColor("#4169E1")

pages = len(PdfReader(str(INTERIOR)).pages)
spine_w_in = pages * 0.002252

cover_w_in = 2 * TRIM_W + spine_w_in + 2 * BLEED
cover_h_in = TRIM_H + 2 * BLEED

W = cover_w_in * inch
H = cover_h_in * inch
SP = spine_w_in * inch
BL = BLEED * inch

back_x0 = 0
back_x1 = (TRIM_W + BLEED) * inch
spine_x0 = back_x1
spine_x1 = spine_x0 + SP
front_x0 = spine_x1
front_x1 = W

back_cx = (back_x0 + back_x1) / 2
spine_cx = (spine_x0 + spine_x1) / 2
front_cx = (front_x0 + front_x1) / 2

c = canvas.Canvas(str(OUTPUT), pagesize=(W, H))

# Background
c.setFillColor(BG)
c.rect(0, 0, W, H, fill=1, stroke=0)


# ───────────────────────────────────
# FRONT COVER (right)
# ───────────────────────────────────
front_margin = 0.5 * inch

# Border
c.setStrokeColor(BORDER)
c.setLineWidth(1.5)
c.rect(front_x0 + front_margin, front_margin,
       (front_x1 - front_x0) - 2 * front_margin,
       H - 2 * front_margin)

# Stars on front (decorative)
def draw_star(cx, cy, r_out, r_in, points, color):
    c.setFillColor(color)
    p = c.beginPath()
    for i in range(points * 2):
        a = math.pi / 2 + i * math.pi / points
        r = r_out if i % 2 == 0 else r_in
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    c.drawPath(p, fill=1)

front_w_in = (front_x1 - front_x0) / inch
star_positions = [
    (front_x0 + front_w_in*inch*0.2, H*0.85),
    (front_x0 + front_w_in*inch*0.78, H*0.88),
    (front_x0 + front_w_in*inch*0.3, H*0.75),
    (front_x0 + front_w_in*inch*0.82, H*0.72),
    (front_x0 + front_w_in*inch*0.15, H*0.65),
    (front_x0 + front_w_in*inch*0.9, H*0.8),
    (front_x0 + front_w_in*inch*0.65, H*0.78),
]
for i, (sx, sy) in enumerate(star_positions):
    sz = 6 + (i % 3) * 3
    draw_star(sx, sy, sz, sz * 0.4, 5, MOON_COLOR)

# Crescent moon
moon_cx = front_cx
moon_cy = H * 0.76
c.setFillColor(MOON_COLOR)
c.circle(moon_cx, moon_cy, 32, fill=1, stroke=0)
c.setFillColor(BG)
c.circle(moon_cx + 12, moon_cy + 5, 28, fill=1, stroke=0)

# Title
c.setFillColor(white)
c.setFont("Helvetica-Bold", 56)
ty = H * 0.55
c.drawCentredString(front_cx, ty, "SLEEP")
ty -= 60
c.drawCentredString(front_cx, ty, "PLANNER")
ty -= 12

# Decorative line
c.setStrokeColor(ACCENT)
c.setLineWidth(2)
c.line(front_cx - 80, ty, front_cx + 80, ty)

# Subtitle
c.setFillColor(ACCENT)
c.setFont("Helvetica", 16)
sy = ty - 30
c.drawCentredString(front_cx, sy, "Track Your Nights, Transform Your Days")
sy -= 22
c.drawCentredString(front_cx, sy, "A Complete Sleep Tracking System")

# Author on front (safe distance from bottom)
c.setFillColor(ACCENT)
c.setFont("Helvetica-Bold", 14)
c.drawCentredString(front_cx, BL + 0.7 * inch, "Deokgu Studio")


# ───────────────────────────────────
# SPINE — 상하 0.5" 안전 마진 확보
# ───────────────────────────────────
if spine_w_in >= 0.15:
    spine_font = min(10, spine_w_in * 45)
    if spine_font >= 5:
        # Title at spine center (safely within top/bottom 0.5" margin)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", spine_font)
        c.saveState()
        c.translate(spine_cx, H / 2)
        c.rotate(90)
        c.drawCentredString(0, -spine_font / 3, "SLEEP PLANNER")
        c.restoreState()

        # Author near bottom — at least 0.5" from bottom edge
        author_size = max(5, spine_font - 2)
        author_y = BL + SPINE_SAFE * inch + author_size + 10  # safe margin + text height buffer

        c.setFillColor(ACCENT)
        c.setFont("Helvetica", author_size)
        c.saveState()
        c.translate(spine_cx, author_y)
        c.rotate(90)
        c.drawCentredString(0, -author_size / 3, "Deokgu Studio")
        c.restoreState()


# ───────────────────────────────────
# BACK COVER (left)
# ISBN Barcode Area 박스 제거 (템플릿 텍스트 금지)
# ───────────────────────────────────
back_margin = 0.6 * inch

c.setStrokeColor(BORDER)
c.setLineWidth(1.2)
c.rect(back_x0 + back_margin, back_margin,
       (back_x1 - back_x0) - 2 * back_margin,
       H - 2 * back_margin)

# Back title
c.setFont("Helvetica-Bold", 20)
c.setFillColor(white)
c.drawCentredString(back_cx, H * 0.85, "SLEEP PLANNER")

# Accent line
c.setStrokeColor(ACCENT)
c.setLineWidth(2)
c.line(back_cx - 70, H * 0.82, back_cx + 70, H * 0.82)

# Description
c.setFont("Helvetica", 12)
c.setFillColor(white)
description = [
    "A complete 90-night sleep tracking system",
    "designed to help you finally get the rest",
    "you deserve.",
]
fy = H * 0.76
for line in description:
    c.drawCentredString(back_cx, fy, line)
    fy -= 18

# Features
fy -= 20
c.setFont("Helvetica-Bold", 12)
c.setFillColor(ACCENT)
c.drawCentredString(back_cx, fy, "INSIDE THIS PLANNER:")
fy -= 22

c.setFont("Helvetica", 11)
c.setFillColor(white)
features = [
    "90 daily sleep tracking pages",
    "Sleep hygiene essentials guide",
    "Weekly sleep reviews & patterns",
    "Dream journal space on every page",
    "Pre-sleep checklist & wind-down routines",
]
for feat in features:
    c.drawCentredString(back_cx, fy, "• " + feat)
    fy -= 18

# Publisher (bottom) — NO barcode template
c.setFont("Helvetica-Bold", 11)
c.setFillColor(ACCENT)
c.drawCentredString(back_cx, BL + 0.9 * inch, "Deokgu Studio")

c.save()

fsize = os.path.getsize(OUTPUT) / 1024
print(f"Cover regenerated: {cover_w_in:.3f}\" x {cover_h_in:.3f}\" ({pages} pages, spine {spine_w_in:.3f}\")")
print(f"File: {OUTPUT.name} ({fsize:.0f} KB)")
print(f"Fixes: spine 0.5\" safe margin, ISBN template removed")
