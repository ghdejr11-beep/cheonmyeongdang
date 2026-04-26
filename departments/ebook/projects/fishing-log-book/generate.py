"""
Fishing Log Book Generator
KDP 6x9 paperback, ~120 pages
Run: python generate.py
"""
import os
from reportlab.lib.pagesizes import inch
from reportlab.lib import colors
from reportlab.lib.units import inch as IN
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, ActionFlowable,
    Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas as pdfcanvas

PAGE_W = 6 * IN
PAGE_H = 9 * IN
MARGIN = 0.75 * IN
INNER_W = PAGE_W - 2 * MARGIN

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fishing-log-book.pdf")

NAVY      = colors.HexColor("#1B3A6B")
TEAL      = colors.HexColor("#2E7D87")
LIGHTBLUE = colors.HexColor("#E8F4F6")
GOLD      = colors.HexColor("#D4A017")
DGRAY     = colors.HexColor("#333333")
LGRAY     = colors.HexColor("#F5F5F5")
MGRAY     = colors.HexColor("#AAAAAA")
LINEC     = colors.HexColor("#C0C0C0")
WHITE     = colors.white


def ps(name, base="Normal", **kw):
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    return ParagraphStyle(name, parent=styles[base], **kw)


def draw_cover(c, doc):
    c.saveState()
    c.setFillColor(NAVY);  c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(TEAL);  c.rect(0, PAGE_H*0.36, PAGE_W, PAGE_H*0.28, fill=1, stroke=0)
    c.setFillColor(GOLD);  c.rect(0, PAGE_H*0.36-0.035*IN, PAGE_W, 0.035*IN, fill=1, stroke=0)
    c.setFillColor(GOLD);  c.rect(0, PAGE_H*0.64, PAGE_W, 0.035*IN, fill=1, stroke=0)

    # Wave lines
    c.setStrokeColor(colors.HexColor("#FFFFFF25")); c.setLineWidth(0.5)
    for i in range(10):
        y = PAGE_H*0.37 + i * 0.025*IN
        c.line(MARGIN*0.4, y, PAGE_W - MARGIN*0.4, y)

    # Title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28); c.drawCentredString(PAGE_W/2, PAGE_H*0.80, "FISHING")
    c.setFont("Helvetica-Bold", 30); c.drawCentredString(PAGE_W/2, PAGE_H*0.72, "LOG BOOK")
    c.setFont("Helvetica",      10); c.setFillColor(LIGHTBLUE)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.67, "The Ultimate Angler's Journal")

    # Mid strip
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.535, "Track Every Cast  *  Record Every Catch")
    c.setFont("Helvetica", 9); c.setFillColor(colors.HexColor("#FFFFFFBB"))
    c.drawCentredString(PAGE_W/2, PAGE_H*0.493, "Freshwater & Saltwater")
    c.drawCentredString(PAGE_W/2, PAGE_H*0.456, "100 Fishing Trip Entries")

    # Gold divider bottom
    c.setStrokeColor(GOLD); c.setLineWidth(1.5)
    c.line(MARGIN, PAGE_H*0.20, PAGE_W - MARGIN, PAGE_H*0.20)

    # Hook symbol (ASCII)
    c.setFont("Helvetica-Bold", 18); c.setFillColor(GOLD)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.225, ")(")  # simple fish-like symbol

    # Publisher
    c.setFont("Helvetica", 8); c.setFillColor(WHITE)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.10, "Deokgu Studio")
    c.restoreState()


def draw_page_num(c, doc):
    n = c.getPageNumber()
    if n > 3:
        c.saveState()
        c.setFont("Helvetica", 8); c.setFillColor(MGRAY)
        c.drawCentredString(PAGE_W/2, 0.45*IN, str(n - 3))
        c.restoreState()


def log_page(num):
    lbl  = ps("lbl",  fontSize=7.5, fontName="Helvetica-Bold", textColor=TEAL)
    fval = ps("fval", fontSize=8,   fontName="Helvetica",       textColor=DGRAY)
    sec  = ps("sec",  fontSize=8,   fontName="Helvetica-Bold",  textColor=NAVY, spaceBefore=4, spaceAfter=2)

    elems = []

    # --- Header bar ---
    hdr = Table([[
        Paragraph(f"<b>TRIP #{num:03d}</b>",
                  ps("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph("Date: ________________  From: ________ To: ________",
                  ps("td", fontSize=8, fontName="Helvetica", textColor=WHITE)),
    ]], colWidths=[0.9*IN, INNER_W - 0.9*IN])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (0,0), 6),
        ("RIGHTPADDING", (1,0), (1,0), 6),
    ]))
    elems.append(hdr)
    elems.append(Spacer(1, 4))

    # --- Location / Conditions grid ---
    conds = Table([
        [Paragraph("LOCATION", lbl), Paragraph("WATER BODY", lbl)],
        ["_________________________", "[ ] Lake  [ ] River  [ ] Ocean  [ ] Pond  [ ] Bay"],
        [Paragraph("WEATHER", lbl), Paragraph("WATER TEMP", lbl)],
        ["[ ]Sunny [ ]Cloudy [ ]Overcast [ ]Rainy [ ]Windy", "_________"],
        [Paragraph("AIR TEMP", lbl), Paragraph("WATER CLARITY", lbl)],
        ["_________", "[ ] Clear  [ ] Stained  [ ] Murky"],
    ], colWidths=[INNER_W*0.5, INNER_W*0.5])
    conds.setStyle(TableStyle([
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 1),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2),
        ("LEFTPADDING",  (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LIGHTBLUE, WHITE]*3),
        ("BOX",          (0,0), (-1,-1), 0.5, LINEC),
        ("INNERGRID",    (0,0), (-1,-1), 0.3, LINEC),
    ]))
    elems.append(conds)
    elems.append(Spacer(1, 4))

    # --- Gear ---
    elems.append(Paragraph("GEAR USED", sec))
    gear = Table([
        ["Rod: _______________________   Reel: _____________________   Line: ____________"],
        ["Bait / Lure: _______________________________________   Hook Size: ____________"],
        ["Technique: [ ] Casting  [ ] Trolling  [ ] Fly fishing  [ ] Jigging  [ ] Still  [ ] Other: ______"],
    ], colWidths=[INNER_W])
    gear.setStyle(TableStyle([
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("FONTNAME",     (0,0), (-1,-1), "Helvetica"),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, LGRAY, WHITE]),
        ("BOX",          (0,0), (-1,-1), 0.5, LINEC),
        ("LINEBELOW",    (0,0), (0,0), 0.3, LINEC),
    ]))
    elems.append(gear)
    elems.append(Spacer(1, 4))

    # --- Catch Record ---
    elems.append(Paragraph("CATCH RECORD", sec))
    ch_style = ps("ch", fontSize=7, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    ch = [Paragraph(x, ch_style) for x in ["SPECIES", "LENGTH", "WEIGHT", "TIME", "RELEASED?"]]
    rows = [["", "", "", "", "[ ] Y  [ ] N"] for _ in range(5)]
    catch = Table([ch] + rows,
                  colWidths=[1.35*IN, 0.82*IN, 0.82*IN, 0.65*IN, 0.80*IN],
                  rowHeights=[0.20*IN] + [0.22*IN]*5)
    catch.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0), TEAL),
        ("TEXTCOLOR",      (0,0), (-1,0), WHITE),
        ("FONTNAME",       (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",       (0,1), (-1,-1), 8),
        ("ALIGN",          (0,0), (-1,-1), "CENTER"),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID",           (0,0), (-1,-1), 0.4, LINEC),
    ]))
    elems.append(catch)
    elems.append(Spacer(1, 4))

    # --- Notes ---
    elems.append(Paragraph("NOTES & OBSERVATIONS", sec))
    note_rows = [["_" * 62] for _ in range(4)]
    notes = Table(note_rows, colWidths=[INNER_W], rowHeights=[0.22*IN]*4)
    notes.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 8),
        ("TEXTCOLOR", (0,0), (-1,-1), LINEC),
        ("TOPPADDING",(0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ("VALIGN",    (0,0), (-1,-1), "BOTTOM"),
    ]))
    elems.append(notes)
    elems.append(Spacer(1, 4))

    # --- Rating ---
    rating = Table([[
        Paragraph("Trip Rating:", ps("rl", fontSize=8, fontName="Helvetica-Bold", textColor=NAVY)),
        Paragraph("* * * * *  (circle)   Total Fish: _____   Biggest Catch: _____________",
                  ps("rv", fontSize=8, fontName="Helvetica", textColor=DGRAY)),
    ]], colWidths=[0.9*IN, INNER_W - 0.9*IN])
    rating.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,-1), LGRAY),
        ("TOPPADDING",     (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 4),
        ("LEFTPADDING",    (0,0), (-1,-1), 5),
        ("BOX",            (0,0), (-1,-1), 0.5, LINEC),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
    ]))
    elems.append(rating)
    return elems


def build():
    doc = BaseDocTemplate(
        OUTPUT, pagesize=(PAGE_W, PAGE_H),
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
    )
    cover_tpl   = PageTemplate("cover",   frames=[Frame(0,0,PAGE_W,PAGE_H,id="cf")], onPage=draw_cover)
    content_tpl = PageTemplate("content", frames=[Frame(MARGIN, MARGIN, INNER_W, PAGE_H-2*MARGIN, id="mf")], onPage=draw_page_num)
    doc.addPageTemplates([cover_tpl, content_tpl])

    bstyle = ps("b", fontSize=9, fontName="Helvetica", textColor=DGRAY, leading=13, spaceAfter=4)
    hstyle = ps("h", fontSize=12, fontName="Helvetica-Bold", textColor=NAVY, spaceAfter=4, spaceBefore=8)
    tstyle = ps("t", fontSize=18, fontName="Helvetica-Bold", textColor=NAVY, alignment=TA_CENTER, spaceAfter=6)
    sstyle = ps("s", fontSize=8,  fontName="Helvetica", textColor=MGRAY, alignment=TA_CENTER)
    tipst  = ps("tip", fontSize=8.5, fontName="Helvetica", textColor=DGRAY, leading=12, spaceAfter=3, leftIndent=6)

    story = [
        ActionFlowable(("nextPageTemplate", "content")),
        PageBreak(),

        # ── Intro page ──
        Paragraph("Welcome, Angler!", tstyle),
        HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=10),
        Paragraph(
            "This <b>Fishing Log Book</b> is your personal record of every fishing adventure. "
            "Experienced anglers know that keeping detailed records is the secret to catching more fish consistently. "
            "Track weather, gear, locations and catches — then watch your patterns emerge.",
            bstyle),
        Spacer(1,6),
        Paragraph("<b>What this log helps you track:</b>", hstyle),
    ]

    for icon, title, desc in [
        (">>", "Location & Spot Details",  "Remember exactly where you caught that trophy fish."),
        (">>", "Weather & Conditions",     "Discover patterns between conditions and fish activity."),
        (">>", "Gear & Techniques",        "Track which lures, rigs, and methods work best."),
        (">>", "Catch Records",            "Log species, size, weight — and celebrate personal bests!"),
        (">>", "Notes & Observations",     "Record insights that make you a smarter angler."),
    ]:
        story.append(Paragraph(f"<b>{title}</b> — {desc}", tipst))
        story.append(Spacer(1,3))

    story += [
        Spacer(1,10),
        Paragraph("<b>How to Use This Book</b>", hstyle),
        Paragraph(
            "Each log entry page covers one fishing session. Fill in fields right after your trip "
            "while details are fresh. Over time, patterns emerge that dramatically improve your success rate.",
            bstyle),
        Spacer(1,12),
        Paragraph("Good luck out there. Tight lines!", bstyle),
        Spacer(1,4),
        Paragraph("— Deokgu Studio", sstyle),
        PageBreak(),

        # ── Angler profile ──
        Paragraph("My Fishing Profile", tstyle),
        HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=12),
    ]

    profile = Table([
        ["Name:",              "_" * 32],
        ["Home Waters:",       "_" * 28],
        ["License #:",         "_" * 29],
        ["Favorite Species:",  "_" * 26],
        ["Favorite Technique:","_" * 24],
        ["Fishing Since:",     "_" * 28],
        ["Personal Best:",     "_" * 28],
        ["Dream Catch:",       "_" * 29],
    ], colWidths=[1.5*IN, 2.8*IN])
    profile.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("TEXTCOLOR",     (0,0), (0,-1), NAVY),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
    ]))
    story.append(profile)
    story.append(Spacer(1,14))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEC, spaceAfter=10))
    story.append(Paragraph("Pro Tips for Anglers", hstyle))

    for tip in [
        "Fish are most active at dawn and dusk — plan your trips accordingly.",
        "Water temperature affects fish behavior. Cold water = deeper; warm water = shallows.",
        "Barometric pressure drops before rain often trigger feeding frenzies.",
        "Match your bait to the natural food sources in each body of water.",
        "Reduce noise and vibration — fish sense disturbances through their lateral line.",
        "Record lunar phases — full and new moons often improve bite rates.",
        "Vary your retrieve speed until you find what works on that particular day.",
        "Practice catch-and-release when possible to preserve fish populations.",
    ]:
        story.append(Paragraph(f"* {tip}", tipst))
        story.append(Spacer(1,2))

    story.append(PageBreak())

    # ── 100 Log pages ──
    for i in range(1, 101):
        story.extend(log_page(i))
        if i < 100:
            story.append(PageBreak())

    story.append(PageBreak())

    # ── Trophy summary ──
    story.append(Paragraph("Trophy Catches & Records", tstyle))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=12))
    story.append(Paragraph("Record your personal bests and most memorable catches here.", bstyle))
    story.append(Spacer(1,8))

    ch_s = ps("chs2", fontSize=7, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    hdrs = [Paragraph(x, ch_s) for x in ["SPECIES", "WEIGHT", "LENGTH", "LOCATION", "DATE"]]
    rows = [["","","","",""] for _ in range(16)]
    trophy = Table([hdrs]+rows,
                   colWidths=[1.05*IN, 0.75*IN, 0.75*IN, 1.10*IN, 0.85*IN],
                   rowHeights=[0.22*IN]+[0.26*IN]*16)
    trophy.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",      (0,0), (-1,0), WHITE),
        ("FONTNAME",       (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",       (0,0), (-1,-1), 8),
        ("ALIGN",          (0,0), (-1,-1), "CENTER"),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID",           (0,0), (-1,-1), 0.5, LINEC),
    ]))
    story.append(trophy)
    story.append(Spacer(1,16))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEC, spaceAfter=8))
    story.append(Paragraph(
        "\"The charm of fishing is that it is the pursuit of what is elusive but attainable,\n"
        "a perpetual series of occasions for hope.\"  -- John Buchan",
        sstyle))
    story.append(Spacer(1,6))
    story.append(Paragraph("Thank you for using this Fishing Log Book. Tight lines always!", sstyle))
    story.append(Spacer(1,4))
    story.append(Paragraph("(c) Deokgu Studio -- All Rights Reserved", sstyle))

    doc.build(story)
    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    build()
