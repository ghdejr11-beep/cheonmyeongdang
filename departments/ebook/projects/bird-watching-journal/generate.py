"""
Bird Watching Journal Generator
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas as pdfcanvas

PAGE_W = 6 * IN
PAGE_H = 9 * IN
MARGIN = 0.75 * IN
INNER_W = PAGE_W - 2 * MARGIN

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bird-watching-journal.pdf")

FOREST    = colors.HexColor("#2C5F2D")
SAGE      = colors.HexColor("#7BA05B")
CREAM     = colors.HexColor("#F4F1E8")
GOLD      = colors.HexColor("#C9A227")
RUST      = colors.HexColor("#A0522D")
DGRAY     = colors.HexColor("#333333")
LGRAY     = colors.HexColor("#F5F5F0")
MGRAY     = colors.HexColor("#999999")
LINEC     = colors.HexColor("#BDBDBD")
WHITE     = colors.white


def ps(name, base="Normal", **kw):
    styles = getSampleStyleSheet()
    return ParagraphStyle(name, parent=styles[base], **kw)


def draw_cover(c, doc):
    c.saveState()
    c.setFillColor(FOREST); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(SAGE);   c.rect(0, PAGE_H*0.34, PAGE_W, PAGE_H*0.30, fill=1, stroke=0)
    c.setFillColor(GOLD);   c.rect(0, PAGE_H*0.34-0.035*IN, PAGE_W, 0.035*IN, fill=1, stroke=0)
    c.setFillColor(GOLD);   c.rect(0, PAGE_H*0.64, PAGE_W, 0.035*IN, fill=1, stroke=0)

    # subtle leaf-like horizontal stripes
    c.setStrokeColor(colors.HexColor("#FFFFFF20")); c.setLineWidth(0.5)
    for i in range(12):
        y = PAGE_H*0.35 + i * 0.024*IN
        c.line(MARGIN*0.4, y, PAGE_W - MARGIN*0.4, y)

    # Title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 30); c.drawCentredString(PAGE_W/2, PAGE_H*0.80, "BIRD")
    c.setFont("Helvetica-Bold", 30); c.drawCentredString(PAGE_W/2, PAGE_H*0.73, "WATCHING")
    c.setFont("Helvetica-Bold", 26); c.drawCentredString(PAGE_W/2, PAGE_H*0.665, "JOURNAL")

    # Mid strip
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.535, "A Birder's Field Logbook")
    c.setFont("Helvetica", 9); c.setFillColor(colors.HexColor("#FFFFFFCC"))
    c.drawCentredString(PAGE_W/2, PAGE_H*0.495, "Track Sightings  *  Build Your Life List")
    c.drawCentredString(PAGE_W/2, PAGE_H*0.458, "100 Detailed Entries + Life List + Trip Planner")

    # Gold divider bottom
    c.setStrokeColor(GOLD); c.setLineWidth(1.5)
    c.line(MARGIN, PAGE_H*0.20, PAGE_W - MARGIN, PAGE_H*0.20)

    # Simple bird silhouette using Helvetica chars
    c.setFont("Helvetica-Bold", 22); c.setFillColor(GOLD)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.225, "v  ^  v")

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


def log_page(num):
    lbl  = ps("lbl",  fontSize=7.5, fontName="Helvetica-Bold", textColor=FOREST)
    sec  = ps("sec",  fontSize=8,   fontName="Helvetica-Bold", textColor=FOREST, spaceBefore=4, spaceAfter=2)

    elems = []

    # Header bar
    hdr = Table([[
        Paragraph(f"<b>SIGHTING #{num:03d}</b>",
                  ps("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph("Date: ___________   Time: ____:____   [ ] AM  [ ] PM",
                  ps("td", fontSize=8, fontName="Helvetica", textColor=WHITE)),
    ]], colWidths=[1.05*IN, INNER_W - 1.05*IN])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), FOREST),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (0,0), 6),
        ("RIGHTPADDING", (1,0), (1,0), 6),
    ]))
    elems.append(hdr)
    elems.append(Spacer(1, 4))

    # Species block
    species = Table([
        [Paragraph("COMMON NAME", lbl), Paragraph("SCIENTIFIC NAME", lbl)],
        ["________________________", "________________________"],
        [Paragraph("FAMILY / GROUP", lbl), Paragraph("# OBSERVED", lbl)],
        ["________________________", "_______"],
    ], colWidths=[INNER_W*0.62, INNER_W*0.38])
    species.setStyle(TableStyle([
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 1),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2),
        ("LEFTPADDING",  (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [CREAM, WHITE]*2),
        ("BOX",          (0,0), (-1,-1), 0.5, LINEC),
        ("INNERGRID",    (0,0), (-1,-1), 0.3, LINEC),
    ]))
    elems.append(species)
    elems.append(Spacer(1, 4))

    # Location & habitat
    loc = Table([
        [Paragraph("LOCATION", lbl), Paragraph("HABITAT", lbl)],
        ["______________________", "[ ] Forest  [ ] Wetland  [ ] Grassland"],
        [Paragraph("COORDINATES / PARK", lbl), ""],
        ["______________________", "[ ] Coastal  [ ] Urban  [ ] Backyard"],
        [Paragraph("WEATHER", lbl), Paragraph("TEMP / WIND", lbl)],
        ["[ ] Sunny [ ] Cloudy [ ] Rain [ ] Fog", "______ F   /   ______ mph"],
    ], colWidths=[INNER_W*0.5, INNER_W*0.5])
    loc.setStyle(TableStyle([
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 1),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2),
        ("LEFTPADDING",  (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [CREAM, WHITE]*3),
        ("BOX",          (0,0), (-1,-1), 0.5, LINEC),
        ("INNERGRID",    (0,0), (-1,-1), 0.3, LINEC),
    ]))
    elems.append(loc)
    elems.append(Spacer(1, 4))

    # Identification details
    elems.append(Paragraph("IDENTIFICATION", sec))
    ident = Table([
        ["Size:  [ ] Sparrow  [ ] Robin  [ ] Crow  [ ] Goose  [ ] Eagle"],
        ["Plumage / Colors: ______________________________________________"],
        ["Beak:  [ ] Short  [ ] Long  [ ] Hooked  [ ] Conical  [ ] Pointed"],
        ["Song / Call: ___________________________________________________"],
    ], colWidths=[INNER_W])
    ident.setStyle(TableStyle([
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("FONTNAME",     (0,0), (-1,-1), "Helvetica"),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, LGRAY]*2),
        ("BOX",          (0,0), (-1,-1), 0.5, LINEC),
    ]))
    elems.append(ident)
    elems.append(Spacer(1, 4))

    # Behavior
    elems.append(Paragraph("BEHAVIOR", sec))
    beh = Table([
        ["[ ] Feeding   [ ] Singing   [ ] Flying   [ ] Nesting   [ ] Perched"],
        ["[ ] Mating display   [ ] Foraging   [ ] Bathing   [ ] Wading   [ ] Diving"],
    ], colWidths=[INNER_W])
    beh.setStyle(TableStyle([
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("FONTNAME",     (0,0), (-1,-1), "Helvetica"),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LGRAY, WHITE]),
        ("BOX",          (0,0), (-1,-1), 0.5, LINEC),
    ]))
    elems.append(beh)
    elems.append(Spacer(1, 4))

    # Notes & sketch
    elems.append(Paragraph("NOTES / FIELD SKETCH", sec))
    note_rows = [[""] for _ in range(4)]
    notes = Table(note_rows, colWidths=[INNER_W], rowHeights=[0.22*IN]*4)
    notes.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 8),
        ("BOX",       (0,0), (-1,-1), 0.5, LINEC),
        ("LINEBELOW", (0,0), (-1,-2), 0.3, LINEC),
        ("TOPPADDING",(0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    elems.append(notes)
    elems.append(Spacer(1, 4))

    # Footer rating
    rating = Table([[
        Paragraph("Lifer?", ps("rl", fontSize=8, fontName="Helvetica-Bold", textColor=FOREST)),
        Paragraph("[ ] Yes  [ ] No     Photo? [ ] Yes  [ ] No     Audio? [ ] Yes  [ ] No",
                  ps("rv", fontSize=8, fontName="Helvetica", textColor=DGRAY)),
    ]], colWidths=[0.65*IN, INNER_W - 0.65*IN])
    rating.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,-1), CREAM),
        ("TOPPADDING",     (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 4),
        ("LEFTPADDING",    (0,0), (-1,-1), 5),
        ("BOX",            (0,0), (-1,-1), 0.5, LINEC),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
    ]))
    elems.append(rating)
    return elems


def life_list_page():
    lbl = ps("lbl", fontSize=7, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    hdr = [Paragraph(x, lbl) for x in ["#", "SPECIES", "DATE", "LOCATION"]]
    rows = [["", "", "", ""] for _ in range(20)]
    t = Table([hdr] + rows,
              colWidths=[0.30*IN, 1.85*IN, 0.85*IN, INNER_W - 0.30*IN - 1.85*IN - 0.85*IN],
              rowHeights=[0.20*IN] + [0.27*IN]*20)
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0), FOREST),
        ("TEXTCOLOR",      (0,0), (-1,0), WHITE),
        ("FONTNAME",       (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",       (0,0), (-1,-1), 8),
        ("ALIGN",          (0,0), (-1,-1), "LEFT"),
        ("ALIGN",          (0,0), (0,-1), "CENTER"),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID",           (0,0), (-1,-1), 0.4, LINEC),
        ("LEFTPADDING",    (1,1), (-1,-1), 4),
    ]))
    return t


def trip_planner_page():
    lbl = ps("lbl", fontSize=7.5, fontName="Helvetica-Bold", textColor=FOREST)
    rows = [
        [Paragraph("DESTINATION", lbl), "_______________________________________________"],
        [Paragraph("DATE / TIME", lbl), "_______________________________________________"],
        [Paragraph("PARTY", lbl), "_______________________________________________"],
        [Paragraph("TARGET SPECIES", lbl), "_______________________________________________"],
        [Paragraph("HABITATS TO COVER", lbl), "_______________________________________________"],
        [Paragraph("GEAR CHECKLIST", lbl),
         "[ ] Binoculars  [ ] Field guide  [ ] Camera  [ ] Notebook  [ ] Water"],
        [Paragraph("WEATHER FORECAST", lbl), "_______________________________________________"],
        [Paragraph("NOTES", lbl), "_______________________________________________"],
    ]
    t = Table(rows, colWidths=[1.4*IN, INNER_W - 1.4*IN])
    t.setStyle(TableStyle([
        ("FONTNAME",     (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("TEXTCOLOR",    (1,0), (1,-1), DGRAY),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [CREAM, WHITE]),
        ("BOX",          (0,0), (-1,-1), 0.5, LINEC),
        ("INNERGRID",    (0,0), (-1,-1), 0.3, LINEC),
    ]))
    return t


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
    hstyle = ps("h", fontSize=12, fontName="Helvetica-Bold", textColor=FOREST, spaceAfter=4, spaceBefore=8)
    tstyle = ps("t", fontSize=18, fontName="Helvetica-Bold", textColor=FOREST, alignment=TA_CENTER, spaceAfter=6)
    sstyle = ps("s", fontSize=8,  fontName="Helvetica", textColor=MGRAY, alignment=TA_CENTER)
    tipst  = ps("tip", fontSize=8.5, fontName="Helvetica", textColor=DGRAY, leading=12, spaceAfter=3, leftIndent=6)

    story = [
        ActionFlowable(("nextPageTemplate", "content")),
        PageBreak(),

        # Intro
        Paragraph("Welcome, Birder!", tstyle),
        HRFlowable(width="100%", thickness=2, color=SAGE, spaceAfter=10),
        Paragraph(
            "This <b>Bird Watching Journal</b> is your personal companion for the field. "
            "Birding rewards patience and observation — and detailed records turn each outing into "
            "lifelong knowledge. Track every sighting, build your life list, and watch your skills grow.",
            bstyle),
        Spacer(1,6),
        Paragraph("<b>What this journal helps you record:</b>", hstyle),
    ]

    for title, desc in [
        ("Species & Identification",   "Common name, scientific name, plumage, calls, and beak shape."),
        ("Location & Habitat",         "GPS, parks, refuges — plus forest, wetland, urban, coastal habitat."),
        ("Weather & Conditions",       "Temperature, wind, sky — patterns that shape activity windows."),
        ("Behavior & Counts",          "Feeding, singing, nesting, mating displays — and how many."),
        ("Life List & Lifers",         "Mark each new species, tally your year list and life list."),
        ("Trips & Sketches",           "Plan outings, jot observations, and sketch field marks."),
    ]:
        story.append(Paragraph(f"<b>{title}</b> -- {desc}", tipst))
        story.append(Spacer(1,3))

    story += [
        Spacer(1,10),
        Paragraph("<b>How to Use This Journal</b>", hstyle),
        Paragraph(
            "Carry this book in your field bag. Fill in each sighting page on the spot or just after — "
            "details fade fast. Use the Life List section to log each new species. Use the Trip Planner "
            "pages before outings, and review your records seasonally to spot patterns.",
            bstyle),
        Spacer(1,12),
        Paragraph("Wishing you full skies and patient eyes.", bstyle),
        Spacer(1,4),
        Paragraph("-- Deokgu Studio", sstyle),
        PageBreak(),

        # Birder profile
        Paragraph("My Birder Profile", tstyle),
        HRFlowable(width="100%", thickness=2, color=SAGE, spaceAfter=12),
    ]

    profile = Table([
        ["Name:",                "_" * 32],
        ["Home Region:",         "_" * 28],
        ["Local Patch:",         "_" * 28],
        ["Favorite Habitat:",    "_" * 26],
        ["Favorite Species:",    "_" * 26],
        ["Birding Since:",       "_" * 28],
        ["Life List Total:",     "_" * 28],
        ["Year Goal:",           "_" * 30],
    ], colWidths=[1.5*IN, 2.8*IN])
    profile.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("TEXTCOLOR",     (0,0), (0,-1), FOREST),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
    ]))
    story.append(profile)
    story.append(Spacer(1,10))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEC, spaceAfter=8))
    story.append(Paragraph("Pro Tips for Birders", hstyle))

    for tip in [
        "Dawn chorus is best — most species sing and feed in the first two hours after sunrise.",
        "Learn songs and calls — at least half of your IDs in dense cover are by ear.",
        "Note GISS first: General Impression of Size and Shape, before colors.",
        "Wind under 10 mph means more activity. After rain, songbirds become very vocal.",
        "Spring and fall migration bring rare visitors -- check eBird hotspots near you.",
        "Sketch field marks before checking your guide — it sharpens observation.",
        "Stay still and quiet. Movement scatters mixed flocks faster than sound.",
        "Keep your binoculars up — never look down to find a bird with naked eyes.",
    ]:
        story.append(Paragraph(f"* {tip}", tipst))
        story.append(Spacer(1,2))

    story.append(PageBreak())

    # Trip planner pages (4 pages)
    story.append(Paragraph("Trip Planner", tstyle))
    story.append(HRFlowable(width="100%", thickness=2, color=SAGE, spaceAfter=10))
    story.append(Paragraph("Use these pages to plan birding outings before you head out.", bstyle))
    story.append(Spacer(1, 8))
    for i in range(4):
        story.append(Paragraph(f"<b>Trip {i+1}</b>", hstyle))
        story.append(trip_planner_page())
        story.append(Spacer(1, 14))
        if i == 1:
            story.append(PageBreak())
    story.append(PageBreak())

    # 100 Sighting log pages
    for i in range(1, 101):
        story.extend(log_page(i))
        if i < 100:
            story.append(PageBreak())

    story.append(PageBreak())

    # Life List (5 pages × 20 = 100 species)
    story.append(Paragraph("My Life List", tstyle))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=10))
    story.append(Paragraph(
        "Record every new species you encounter in the field. Each lifer is a moment worth keeping.",
        bstyle))
    story.append(Spacer(1, 6))
    for i in range(5):
        story.append(life_list_page())
        story.append(Spacer(1, 6))
        if i < 4:
            story.append(PageBreak())
    story.append(PageBreak())

    # Closing page
    story.append(Paragraph("Field Notes & Reflections", tstyle))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=12))
    story.append(Paragraph(
        "Use the remaining pages for migration notes, weather patterns, equipment "
        "logs, and reflections on your favorite outings.",
        bstyle))
    story.append(Spacer(1, 8))
    free_rows = [[""] for _ in range(20)]
    free = Table(free_rows, colWidths=[INNER_W], rowHeights=[0.30*IN]*20)
    free.setStyle(TableStyle([
        ("LINEBELOW", (0,0), (-1,-1), 0.3, LINEC),
        ("FONTSIZE",  (0,0), (-1,-1), 8),
        ("TOPPADDING",(0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    story.append(free)
    story.append(PageBreak())

    free2 = Table([[""] for _ in range(22)], colWidths=[INNER_W], rowHeights=[0.30*IN]*22)
    free2.setStyle(TableStyle([
        ("LINEBELOW", (0,0), (-1,-1), 0.3, LINEC),
        ("FONTSIZE",  (0,0), (-1,-1), 8),
        ("TOPPADDING",(0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    story.append(free2)
    story.append(PageBreak())

    story.append(Spacer(1, 100))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEC, spaceAfter=8))
    story.append(Paragraph(
        "\"In nature's economy the currency is not money, it is life.\"  -- Vandana Shiva",
        sstyle))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Thank you for using this Bird Watching Journal. Keep your eyes on the sky!", sstyle))
    story.append(Spacer(1, 4))
    story.append(Paragraph("(c) Deokgu Studio -- All Rights Reserved", sstyle))

    doc.build(story)
    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    build()
