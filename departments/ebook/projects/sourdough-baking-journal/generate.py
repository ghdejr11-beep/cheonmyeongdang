"""
Sourdough Baking Journal Generator
KDP 6x9 paperback, ~120 pages
Run: python generate.py
"""
import os
from reportlab.lib import colors
from reportlab.lib.units import inch as IN
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, ActionFlowable,
    Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

PAGE_W = 6 * IN
PAGE_H = 9 * IN
MARGIN = 0.75 * IN
INNER_W = PAGE_W - 2 * MARGIN

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sourdough-baking-journal.pdf")

BROWN     = colors.HexColor("#6B3410")
RUST      = colors.HexColor("#A0522D")
TAN       = colors.HexColor("#D2B48C")
WHEAT     = colors.HexColor("#F5DEB3")
CREAM     = colors.HexColor("#FFF8E7")
GOLD      = colors.HexColor("#C9A227")
DGRAY     = colors.HexColor("#333333")
LGRAY     = colors.HexColor("#F5F1EA")
MGRAY     = colors.HexColor("#AAAAAA")
LINEC     = colors.HexColor("#C8B8A2")
WHITE     = colors.white


def ps(name, base="Normal", **kw):
    styles = getSampleStyleSheet()
    return ParagraphStyle(name, parent=styles[base], **kw)


def draw_cover(c, doc):
    c.saveState()
    c.setFillColor(BROWN);  c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(WHEAT);  c.rect(0, PAGE_H*0.34, PAGE_W, PAGE_H*0.32, fill=1, stroke=0)
    c.setFillColor(GOLD);   c.rect(0, PAGE_H*0.34-0.04*IN, PAGE_W, 0.04*IN, fill=1, stroke=0)
    c.setFillColor(GOLD);   c.rect(0, PAGE_H*0.66, PAGE_W, 0.04*IN, fill=1, stroke=0)

    # Subtle hatching as "crumb"
    c.setStrokeColor(colors.HexColor("#00000018")); c.setLineWidth(0.4)
    for i in range(28):
        y = PAGE_H*0.35 + i * 0.024*IN
        c.line(MARGIN*0.4, y, PAGE_W - MARGIN*0.4, y)

    # Title block
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 30); c.drawCentredString(PAGE_W/2, PAGE_H*0.83, "SOURDOUGH")
    c.setFont("Helvetica-Bold", 22); c.drawCentredString(PAGE_W/2, PAGE_H*0.76, "BAKING JOURNAL")
    c.setFont("Helvetica-Oblique", 11); c.setFillColor(WHEAT)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.71, "From Starter to Perfect Loaf")

    # Mid strip
    c.setFillColor(BROWN)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.555, "Track Every Bake  *  Master the Craft")
    c.setFont("Helvetica", 9.5); c.setFillColor(RUST)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.510, "Hydration  *  Fermentation  *  Crumb")
    c.drawCentredString(PAGE_W/2, PAGE_H*0.475, "100 Bake Log Entries + Starter Tracker")

    # Bottom symbol (simple wheat)
    c.setStrokeColor(GOLD); c.setLineWidth(2)
    c.line(MARGIN, PAGE_H*0.20, PAGE_W - MARGIN, PAGE_H*0.20)

    c.setFont("Helvetica-Bold", 16); c.setFillColor(GOLD)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.227, "/ | \\")  # stylized wheat

    # Publisher
    c.setFont("Helvetica", 8); c.setFillColor(WHITE)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.10, "Deokgu Studio")
    c.restoreState()


def draw_page_num(c, doc):
    n = c.getPageNumber()
    if n > 4:
        c.saveState()
        c.setFont("Helvetica", 8); c.setFillColor(MGRAY)
        c.drawCentredString(PAGE_W/2, 0.45*IN, str(n - 4))
        c.restoreState()


def bake_log_page(num):
    lbl  = ps("lbl",  fontSize=7.5, fontName="Helvetica-Bold", textColor=RUST)
    sec  = ps("sec",  fontSize=8,   fontName="Helvetica-Bold", textColor=BROWN, spaceBefore=4, spaceAfter=2)

    elems = []

    # Header bar
    hdr = Table([[
        Paragraph(f"<b>BAKE #{num:03d}</b>",
                  ps("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph("Date: ____________   Loaf Name: ______________________",
                  ps("td", fontSize=8, fontName="Helvetica", textColor=WHITE)),
    ]], colWidths=[0.85*IN, INNER_W - 0.85*IN])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BROWN),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (0,0), 6),
        ("RIGHTPADDING", (1,0), (1,0), 6),
    ]))
    elems.append(hdr)
    elems.append(Spacer(1, 4))

    # Recipe / Ingredients
    elems.append(Paragraph("RECIPE & INGREDIENTS", sec))
    recipe = Table([
        [Paragraph("FLOUR (type)", lbl), Paragraph("WEIGHT (g)", lbl), Paragraph("BAKER %", lbl)],
        ["________________________", "_________", "_________"],
        ["________________________", "_________", "_________"],
        [Paragraph("WATER (g)", lbl), Paragraph("STARTER (g)", lbl), Paragraph("SALT (g)", lbl)],
        ["_________", "_________", "_________"],
    ], colWidths=[INNER_W*0.50, INNER_W*0.25, INNER_W*0.25])
    recipe.setStyle(TableStyle([
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [WHEAT, WHITE]*3),
        ("BOX",           (0,0), (-1,-1), 0.5, LINEC),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, LINEC),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
    ]))
    elems.append(recipe)
    elems.append(Spacer(1, 4))

    # Hydration & Conditions
    elems.append(Paragraph("CONDITIONS", sec))
    cond = Table([
        [Paragraph("TOTAL HYDRATION %", lbl), Paragraph("STARTER HYDRATION %", lbl), Paragraph("LEVAIN RATIO", lbl)],
        ["________________", "________________", "_____ : _____ : _____"],
        [Paragraph("ROOM TEMP (F/C)", lbl), Paragraph("DOUGH TEMP (F/C)", lbl), Paragraph("OVEN TEMP (F/C)", lbl)],
        ["________________", "________________", "________________"],
    ], colWidths=[INNER_W/3]*3)
    cond.setStyle(TableStyle([
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [LGRAY, WHITE]*2),
        ("BOX",           (0,0), (-1,-1), 0.5, LINEC),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, LINEC),
    ]))
    elems.append(cond)
    elems.append(Spacer(1, 4))

    # Timeline / Schedule
    elems.append(Paragraph("BAKE TIMELINE", sec))
    ch_style = ps("ch", fontSize=7, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    hdrs = [Paragraph(x, ch_style) for x in ["STAGE", "START", "END", "DURATION", "NOTES"]]
    rows = []
    for stage in ["Levain Build", "Mix / Fold", "Bulk Ferment", "Cold Proof", "Bake"]:
        rows.append([stage, "______", "______", "______", "______________"])
    timeline = Table([hdrs] + rows,
                     colWidths=[1.0*IN, 0.65*IN, 0.65*IN, 0.75*IN, INNER_W - 3.05*IN],
                     rowHeights=[0.20*IN] + [0.22*IN]*5)
    timeline.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0), RUST),
        ("FONTNAME",       (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",       (0,1), (-1,-1), 8),
        ("FONTNAME",       (0,1), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",      (0,1), (0,-1), BROWN),
        ("ALIGN",          (1,0), (-1,-1), "CENTER"),
        ("ALIGN",          (0,0), (0,-1), "LEFT"),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",    (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID",           (0,0), (-1,-1), 0.4, LINEC),
    ]))
    elems.append(timeline)
    elems.append(Spacer(1, 4))

    # Result / Crumb
    elems.append(Paragraph("RESULT & CRUMB", sec))
    result = Table([
        ["Crust:", "[ ] Pale  [ ] Golden  [ ] Dark  [ ] Burnt"],
        ["Crumb:", "[ ] Tight  [ ] Even  [ ] Open  [ ] Wild  [ ] Gummy"],
        ["Rise:",  "[ ] Flat  [ ] Medium  [ ] Tall  [ ] Over-proof"],
        ["Taste:", "[ ] Mild  [ ] Tangy  [ ] Sour  [ ] Sweet  [ ] Nutty"],
    ], colWidths=[0.6*IN, INNER_W - 0.6*IN])
    result.setStyle(TableStyle([
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,0), (0,-1), BROWN),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [WHITE, LGRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, LINEC),
    ]))
    elems.append(result)
    elems.append(Spacer(1, 4))

    # Rating + Notes
    rating = Table([[
        Paragraph("Bake Rating:", ps("rl", fontSize=8, fontName="Helvetica-Bold", textColor=BROWN)),
        Paragraph("* * * * *  (circle)   Will I bake again? [ ] Yes  [ ] Tweak  [ ] No",
                  ps("rv", fontSize=8, fontName="Helvetica", textColor=DGRAY)),
    ]], colWidths=[0.95*IN, INNER_W - 0.95*IN])
    rating.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,-1), WHEAT),
        ("TOPPADDING",     (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 4),
        ("LEFTPADDING",    (0,0), (-1,-1), 5),
        ("BOX",            (0,0), (-1,-1), 0.5, LINEC),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
    ]))
    elems.append(rating)
    return elems


def starter_log_page(num):
    lbl = ps("lbl", fontSize=7.5, fontName="Helvetica-Bold", textColor=RUST)
    sec = ps("sec", fontSize=10, fontName="Helvetica-Bold", textColor=BROWN, spaceAfter=6)

    elems = [
        Paragraph(f"Starter Maintenance Log — Page {num}", sec),
        HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8),
    ]

    ch_style = ps("ch", fontSize=7, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    hdrs = [Paragraph(x, ch_style) for x in
            ["DATE", "TIME", "FEED RATIO", "FLOUR", "TEMP", "RISE", "ACT 1-5"]]

    rows = [["", "", "", "", "", "", ""] for _ in range(18)]
    tbl = Table([hdrs] + rows,
                colWidths=[0.70*IN, 0.55*IN, 0.75*IN, 0.80*IN, 0.55*IN, 0.55*IN, 0.60*IN],
                rowHeights=[0.24*IN] + [0.32*IN]*18)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0), BROWN),
        ("FONTSIZE",       (0,0), (-1,-1), 7.5),
        ("ALIGN",          (0,0), (-1,-1), "CENTER"),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID",           (0,0), (-1,-1), 0.4, LINEC),
    ]))
    elems.append(tbl)
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        "<i>Activity: 1=sluggish, 2=slow, 3=normal, 4=lively, 5=peak. Note any color, smell, or hooch.</i>",
        ps("hint", fontSize=7.5, fontName="Helvetica-Oblique", textColor=MGRAY)))
    return elems


def recipe_library_page(num):
    sec = ps("sec", fontSize=10, fontName="Helvetica-Bold", textColor=BROWN, spaceAfter=6)
    lbl = ps("lbl", fontSize=7.5, fontName="Helvetica-Bold", textColor=RUST)

    elems = [
        Paragraph(f"My Recipe Library — Page {num}", sec),
        HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=10),
    ]

    # Two recipe cards per page
    for slot in range(2):
        head = Table([[
            Paragraph(f"<b>RECIPE NAME:</b>  ___________________________________________",
                      ps("rn", fontSize=9, fontName="Helvetica", textColor=BROWN)),
        ]], colWidths=[INNER_W])
        head.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), WHEAT),
            ("TOPPADDING",   (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0), (-1,-1), 5),
            ("LEFTPADDING",  (0,0), (-1,-1), 6),
            ("BOX",          (0,0), (-1,-1), 0.5, LINEC),
        ]))
        elems.append(head)

        body = Table([
            [Paragraph("FLOUR BLEND", lbl), Paragraph("HYDRATION %", lbl)],
            ["__________________________________", "_________"],
            [Paragraph("LEVAIN", lbl), Paragraph("BULK TIME", lbl)],
            ["__________________________________", "_________"],
            [Paragraph("PROOF", lbl), Paragraph("BAKE", lbl)],
            ["__________________________________", "_________"],
            [Paragraph("METHOD NOTES", lbl), ""],
            ["________________________________________________________________", ""],
            ["________________________________________________________________", ""],
            ["________________________________________________________________", ""],
        ], colWidths=[INNER_W*0.65, INNER_W*0.35])
        body.setStyle(TableStyle([
            ("FONTSIZE",      (0,0), (-1,-1), 8),
            ("TOPPADDING",    (0,0), (-1,-1), 1),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
            ("LEFTPADDING",   (0,0), (-1,-1), 4),
            ("BOX",           (0,0), (-1,-1), 0.5, LINEC),
            ("INNERGRID",     (0,0), (-1,3), 0.3, LINEC),
            ("SPAN",          (0,6), (1,6)),
            ("SPAN",          (0,7), (1,7)),
            ("SPAN",          (0,8), (1,8)),
            ("SPAN",          (0,9), (1,9)),
            ("BACKGROUND",    (0,6), (-1,6), LGRAY),
        ]))
        elems.append(body)
        if slot == 0:
            elems.append(Spacer(1, 14))

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

    bstyle = ps("b", fontSize=9.5, fontName="Helvetica", textColor=DGRAY, leading=13.5, spaceAfter=4)
    hstyle = ps("h", fontSize=12, fontName="Helvetica-Bold", textColor=BROWN, spaceAfter=4, spaceBefore=8)
    tstyle = ps("t", fontSize=18, fontName="Helvetica-Bold", textColor=BROWN, alignment=TA_CENTER, spaceAfter=6)
    sstyle = ps("s", fontSize=8,  fontName="Helvetica", textColor=MGRAY, alignment=TA_CENTER)
    tipst  = ps("tip", fontSize=8.5, fontName="Helvetica", textColor=DGRAY, leading=12, spaceAfter=3, leftIndent=6)

    story = [
        ActionFlowable(("nextPageTemplate", "content")),
        PageBreak(),

        # Intro
        Paragraph("Welcome to Your Sourdough Journey", tstyle),
        HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=10),
        Paragraph(
            "This <b>Sourdough Baking Journal</b> is built for the bakers who know that great bread "
            "isn't luck — it's a record. Every loaf you bake is a small experiment: a mix of flour, "
            "hydration, time, and temperature. Write it down, and your starter will reward you.",
            bstyle),
        Spacer(1, 6),
        Paragraph("<b>What this journal helps you track:</b>", hstyle),
    ]

    for title, desc in [
        ("Recipes & Hydration",  "Lock in flour blends and baker's percentages so you can repeat or refine."),
        ("Schedule & Timing",    "Levain, bulk, shape, proof, bake — the full timeline for every loaf."),
        ("Temperature",          "Room, dough, and oven — the variables that secretly control your crumb."),
        ("Crumb & Crust",        "Score the result while it's fresh in your mouth, not three weeks later."),
        ("Starter Maintenance",  "When you fed, how it rose, and how it smelled. The starter log section pays off fast."),
        ("Recipe Library",       "Save your winners in a clean format — the back section is your personal cookbook."),
    ]:
        story.append(Paragraph(f"<b>{title}</b> — {desc}", tipst))
        story.append(Spacer(1,3))

    story += [
        Spacer(1,10),
        Paragraph("<b>How to Use This Book</b>", hstyle),
        Paragraph(
            "Fill in a <b>Bake Log</b> page for each loaf, ideally while the bread is cooling. "
            "Use the <b>Starter Maintenance Log</b> to spot when your starter peaks. "
            "Move repeatable winners into the <b>Recipe Library</b> at the back. "
            "After ten loaves, patterns emerge. After fifty, you'll bake on instinct.",
            bstyle),
        Spacer(1,12),
        Paragraph("Happy baking — may your scoring be sharp and your crumb be open.", bstyle),
        Spacer(1,4),
        Paragraph("— Deokgu Studio", sstyle),
        PageBreak(),

        # Baker profile
        Paragraph("My Baker Profile", tstyle),
        HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=12),
    ]

    profile = Table([
        ["Name:",              "_" * 32],
        ["Starter Name:",      "_" * 28],
        ["Starter Birthdate:", "_" * 26],
        ["Flour I Love:",      "_" * 28],
        ["Oven / Vessel:",     "_" * 27],
        ["Baking Since:",      "_" * 28],
        ["Best Loaf So Far:",  "_" * 25],
        ["Goal Loaf:",         "_" * 30],
    ], colWidths=[1.7*IN, 2.6*IN])
    profile.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("TEXTCOLOR",     (0,0), (0,-1), BROWN),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
    ]))
    story.append(profile)
    story.append(Spacer(1,14))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEC, spaceAfter=10))
    story.append(Paragraph("Quick Tips for Better Loaves", hstyle))

    for tip in [
        "Feed your starter at the same time each day to build predictable peaks.",
        "Cooler dough = slower fermentation = better flavor; warmer dough = faster, milder.",
        "Use the float test: a teaspoon of starter that floats in water is ready to bake with.",
        "Bulk fermentation ends when dough is jiggly, domed, and 50-75% larger — not by the clock.",
        "Score at a low angle with a sharp blade for a dramatic ear.",
        "A preheated dutch oven traps steam — that's where shiny crust comes from.",
        "If your crumb is gummy, the bake was too short. Push the internal temp to 205-210 F.",
        "Keep an under-fed starter in the fridge for weekly bakes; revive 12 hours before mixing.",
    ]:
        story.append(Paragraph(f"* {tip}", tipst))
        story.append(Spacer(1,2))

    story.append(PageBreak())

    # Hydration cheat sheet
    story.append(Paragraph("Baker's Percentage Cheat Sheet", tstyle))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=10))
    story.append(Paragraph(
        "Every ingredient is scaled relative to total flour weight (= 100%). "
        "This is how you scale a recipe up or down without losing your hydration.",
        bstyle))
    story.append(Spacer(1, 8))

    ch_style = ps("ch", fontSize=8, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    hdrs = [Paragraph(x, ch_style) for x in ["LOAF STYLE", "HYDRATION", "STARTER", "SALT", "BULK"]]
    cheat_rows = [
        ["Beginner Country",     "70%",  "20%", "2%",   "4-5 hr"],
        ["Classic Sourdough",    "75%",  "20%", "2%",   "4-6 hr"],
        ["Open-Crumb Artisan",   "80%",  "15%", "2%",   "5-7 hr"],
        ["High-Hydration",       "85%",  "15%", "2%",   "5-8 hr"],
        ["Whole Wheat",          "80%",  "20%", "2.2%", "4-5 hr"],
        ["Rye Blend",            "78%",  "20%", "2%",   "3-4 hr"],
        ["Focaccia",             "80%",  "20%", "2%",   "4-5 hr"],
        ["Sandwich Loaf",        "65%",  "15%", "2%",   "4-6 hr"],
        ["Baguette Style",       "70%",  "10%", "2%",   "3-4 hr"],
        ["Pizza Dough (cold)",   "65%",  "10%", "2.5%", "1 hr + cold"],
    ]
    cheat = Table([hdrs] + cheat_rows,
                  colWidths=[1.6*IN, 0.85*IN, 0.75*IN, 0.55*IN, 0.75*IN],
                  rowHeights=[0.25*IN] + [0.28*IN]*10)
    cheat.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0), BROWN),
        ("FONTNAME",       (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",       (0,0), (-1,-1), 8.5),
        ("ALIGN",          (1,0), (-1,-1), "CENTER"),
        ("ALIGN",          (0,0), (0,-1), "LEFT"),
        ("LEFTPADDING",    (0,0), (-1,-1), 5),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID",           (0,0), (-1,-1), 0.5, LINEC),
    ]))
    story.append(cheat)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<i>Hydration only counts water added; flour in the starter counts toward total flour. "
        "Starter %% is starter weight divided by total flour weight.</i>",
        ps("hint", fontSize=8, fontName="Helvetica-Oblique", textColor=MGRAY)))
    story.append(PageBreak())

    # 100 Bake log pages
    for i in range(1, 101):
        story.extend(bake_log_page(i))
        if i < 100:
            story.append(PageBreak())

    story.append(PageBreak())

    # Starter maintenance log: 6 pages x 18 entries = 108 feeds
    for i in range(1, 7):
        story.extend(starter_log_page(i))
        story.append(PageBreak())

    # Recipe library: 8 pages x 2 cards = 16 saved recipes
    for i in range(1, 9):
        story.extend(recipe_library_page(i))
        if i < 8:
            story.append(PageBreak())

    story.append(PageBreak())

    # Closing
    story.append(Paragraph("Closing Notes", tstyle))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=12))
    story.append(Paragraph(
        "\"Bread, in all its forms, is the most successful food invention ever. "
        "Sourdough is the original.\"",
        ps("q", fontSize=10, fontName="Helvetica-Oblique", textColor=BROWN, alignment=TA_CENTER)))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Thank you for using this Sourdough Baking Journal. Trust your starter, trust the process, "
        "and don't be afraid to push the hydration. The next loaf is always your best teacher.",
        bstyle))
    story.append(Spacer(1, 10))
    story.append(Paragraph("(c) Deokgu Studio -- All Rights Reserved", sstyle))

    doc.build(story)
    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    build()
