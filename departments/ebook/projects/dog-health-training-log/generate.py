"""
Dog Health & Training Log
KDP 6x9 paperback, 120 pages, 0.75" margins
"""
from reportlab.lib.pagesizes import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "dog-health-training-log.pdf")

PAGE_W = 6 * inch
PAGE_H = 9 * inch
MARGIN = 0.75 * inch

# Colors
PAW_BROWN = colors.HexColor("#5C3D2E")
PAW_TAN = colors.HexColor("#D4A76A")
PAW_CREAM = colors.HexColor("#FDF6E3")
PAW_LIGHT = colors.HexColor("#F5E6CC")
ACCENT = colors.HexColor("#8B5E3C")
LINE_COLOR = colors.HexColor("#C4956A")
GREY = colors.HexColor("#6B6B6B")
LIGHT_GREY = colors.HexColor("#F0EDE8")

styles = getSampleStyleSheet()

def h1(text):
    return Paragraph(text, ParagraphStyle(
        'H1', fontName='Helvetica-Bold', fontSize=16,
        textColor=PAW_BROWN, spaceAfter=6, alignment=TA_CENTER
    ))

def h2(text):
    return Paragraph(text, ParagraphStyle(
        'H2', fontName='Helvetica-Bold', fontSize=12,
        textColor=ACCENT, spaceAfter=4, alignment=TA_LEFT
    ))

def body(text):
    return Paragraph(text, ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=9,
        textColor=GREY, spaceAfter=3
    ))

def small(text):
    return Paragraph(text, ParagraphStyle(
        'Small', fontName='Helvetica', fontSize=8,
        textColor=GREY, spaceAfter=2
    ))

def center(text, size=10, color=None):
    return Paragraph(text, ParagraphStyle(
        'Center', fontName='Helvetica', fontSize=size,
        textColor=color or GREY, spaceAfter=4, alignment=TA_CENTER
    ))

def section_header(text):
    return Paragraph(text, ParagraphStyle(
        'SecHeader', fontName='Helvetica-Bold', fontSize=11,
        textColor=PAW_BROWN, spaceAfter=6, spaceBefore=10,
        borderPad=4, backColor=PAW_LIGHT,
        leftIndent=0
    ))

def labeled_field(label, width=None):
    """Returns a table row for a labeled blank field"""
    lbl_w = 1.4 * inch
    field_w = (width or 3.8) * inch
    t = Table(
        [[Paragraph(label, ParagraphStyle('Lbl', fontName='Helvetica-Bold', fontSize=8, textColor=ACCENT)),
          Paragraph("", ParagraphStyle('Fld', fontName='Helvetica', fontSize=9))]],
        colWidths=[lbl_w, field_w],
        rowHeights=[0.3 * inch]
    )
    t.setStyle(TableStyle([
        ('LINEBELOW', (1, 0), (1, 0), 0.5, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return t

def blank_line_row(num=1):
    rows = []
    for _ in range(num):
        t = Table([[""]],
                  colWidths=[PAGE_W - 2*MARGIN],
                  rowHeights=[0.32 * inch])
        t.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (0, 0), 0.5, LINE_COLOR),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        rows.append(t)
        rows.append(Spacer(1, 2))
    return rows

def log_table(headers, col_widths, row_count=8, row_h=0.32*inch):
    data = [headers]
    for _ in range(row_count):
        data.append([""] * len(headers))
    t = Table(data, colWidths=col_widths, rowHeights=[0.3*inch] + [row_h]*row_count)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PAW_TAN),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7.5),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ('GRID', (0, 0), (-1, -1), 0.4, LINE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return t

# ─── PAGE SECTIONS ────────────────────────────────────────────────────────────

def cover_page(story):
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("🐾", ParagraphStyle('Paw', fontName='Helvetica', fontSize=40,
                                                 alignment=TA_CENTER, spaceAfter=10)))
    story.append(Paragraph("Dog Health &amp; Training Log", ParagraphStyle(
        'CoverTitle', fontName='Helvetica-Bold', fontSize=22,
        textColor=PAW_BROWN, alignment=TA_CENTER, spaceAfter=10, leading=28
    )))
    story.append(HRFlowable(width="80%", thickness=2, color=PAW_TAN, spaceAfter=14))
    story.append(Paragraph("Complete Pet Care Journal for Tracking<br/>Vet Visits, Vaccinations, Training &amp; Daily Care",
                            ParagraphStyle('CoverSub', fontName='Helvetica', fontSize=11,
                                           textColor=ACCENT, alignment=TA_CENTER, spaceAfter=30, leading=16)))
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph("Deokgu Studio", ParagraphStyle(
        'CoverAuthor', fontName='Helvetica', fontSize=10,
        textColor=GREY, alignment=TA_CENTER
    )))
    story.append(PageBreak())


def how_to_use(story):
    story.append(h1("How to Use This Log"))
    story.append(Spacer(1, 0.15*inch))
    tips = [
        ("Pet Profile", "Fill in your dog's basic information on the first page. Keep it updated as your dog grows."),
        ("Vet Visits", "Log every veterinary appointment with date, reason, and follow-up notes."),
        ("Vaccinations", "Track all vaccines with dates and next due dates to stay on schedule."),
        ("Medications", "Record all medications including dose, frequency, and start/end dates."),
        ("Weight Tracker", "Monitor your dog's weight monthly for early health detection."),
        ("Training Log", "Track commands and progress — celebrate every milestone!"),
        ("Daily Care", "Use the daily care and walk logs to build healthy routines."),
        ("Grooming", "Schedule and record grooming appointments and at-home care."),
    ]
    for title, desc in tips:
        story.append(body(f"<b>{title}:</b> {desc}"))
        story.append(Spacer(1, 3))
    story.append(PageBreak())


def pet_profile(story):
    story.append(h1("My Dog's Profile"))
    story.append(Spacer(1, 0.1*inch))

    fields = [
        ("Dog's Name:", 3.8),
        ("Breed:", 3.8),
        ("Date of Birth:", 3.8),
        ("Color / Markings:", 3.8),
        ("Gender:", 3.8),
        ("Microchip #:", 3.8),
        ("License #:", 3.8),
        ("Insurance Policy #:", 3.8),
    ]
    for label, w in fields:
        story.append(labeled_field(label, w))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 0.12*inch))
    story.append(section_header("  Veterinarian & Emergency Contacts"))
    story.append(Spacer(1, 6))

    contacts = [
        ("Primary Vet Name:", 3.8),
        ("Vet Phone:", 3.8),
        ("Vet Clinic:", 3.8),
        ("Emergency Vet:", 3.8),
        ("Emergency Phone:", 3.8),
        ("Pet Sitter / Boarder:", 3.8),
        ("Sitter Phone:", 3.8),
    ]
    for label, w in contacts:
        story.append(labeled_field(label, w))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 0.1*inch))
    story.append(section_header("  Food & Diet Notes"))
    story.append(Spacer(1, 6))
    diet = [
        ("Food Brand:", 3.8),
        ("Amount Per Meal:", 3.8),
        ("Meals Per Day:", 3.8),
        ("Known Allergies:", 3.8),
        ("Treats Allowed:", 3.8),
    ]
    for label, w in diet:
        story.append(labeled_field(label, w))
        story.append(Spacer(1, 5))

    story.append(PageBreak())


def vet_visit_pages(story, count=3):
    for i in range(count):
        story.append(h1("Veterinary Visit Record"))
        story.append(Spacer(1, 0.08*inch))

        fields = [
            ("Date:", 3.8), ("Vet Name:", 3.8), ("Clinic:", 3.8),
            ("Reason for Visit:", 3.8), ("Weight at Visit:", 3.8),
            ("Temperature:", 3.8),
        ]
        for label, w in fields:
            story.append(labeled_field(label, w))
            story.append(Spacer(1, 4))

        story.append(section_header("  Diagnosis / Findings"))
        story.append(Spacer(1, 4))
        for row in blank_line_row(4):
            story.append(row)

        story.append(Spacer(1, 8))
        story.append(section_header("  Treatments / Prescriptions"))
        story.append(Spacer(1, 4))
        for row in blank_line_row(4):
            story.append(row)

        story.append(Spacer(1, 8))
        story.append(section_header("  Follow-up & Notes"))
        story.append(Spacer(1, 4))
        fields2 = [
            ("Next Appointment:", 3.8),
            ("Cost:", 3.8),
        ]
        for label, w in fields2:
            story.append(labeled_field(label, w))
            story.append(Spacer(1, 4))
        for row in blank_line_row(3):
            story.append(row)
        story.append(PageBreak())


def vaccination_log(story):
    story.append(h1("Vaccination & Preventive Care Log"))
    story.append(Spacer(1, 0.1*inch))
    story.append(small("Keep this section updated and bring to every vet appointment."))
    story.append(Spacer(1, 8))

    hdrs = ["Vaccine / Treatment", "Date Given", "Next Due", "Vet / Clinic"]
    widths = [1.6*inch, 0.95*inch, 0.95*inch, 1.2*inch]
    story.append(log_table(hdrs, widths, row_count=14, row_h=0.3*inch))
    story.append(Spacer(1, 10))
    story.append(section_header("  Notes"))
    story.append(Spacer(1, 4))
    for row in blank_line_row(4):
        story.append(row)
    story.append(PageBreak())


def medication_log(story, count=2):
    for i in range(count):
        story.append(h1("Medication Log"))
        story.append(Spacer(1, 0.08*inch))
        hdrs = ["Medication", "Reason", "Dose", "Freq.", "Start", "End", "Prescribed by"]
        widths = [0.7*inch, 0.65*inch, 0.5*inch, 0.4*inch, 0.55*inch, 0.55*inch, 0.85*inch]
        story.append(log_table(hdrs, widths, row_count=10, row_h=0.35*inch))
        story.append(Spacer(1, 10))
        story.append(section_header("  Notes / Side Effects Observed"))
        story.append(Spacer(1, 4))
        for row in blank_line_row(4):
            story.append(row)
        story.append(PageBreak())


def weight_tracker(story):
    story.append(h1("Weight & Health Tracker"))
    story.append(Spacer(1, 0.08*inch))
    hdrs = ["Date", "Weight (lbs/kg)", "Body Condition*", "Notes"]
    widths = [1.0*inch, 1.3*inch, 1.4*inch, 1.0*inch]
    story.append(log_table(hdrs, widths, row_count=18, row_h=0.3*inch))
    story.append(Spacer(1, 8))
    story.append(small("* Body Condition Score: 1–9 scale (1=very thin, 5=ideal, 9=obese). Ask your vet."))
    story.append(PageBreak())


def training_pages(story, count=4):
    for i in range(count):
        story.append(h1("Training Progress Log"))
        story.append(Spacer(1, 0.08*inch))
        story.append(small("Track each command or skill — use ✓ when fully mastered!"))
        story.append(Spacer(1, 6))

        hdrs = ["Command / Skill", "Date Started", "Stage*", "Date Mastered", "Notes"]
        widths = [1.25*inch, 0.9*inch, 0.55*inch, 1.0*inch, 1.0*inch]
        story.append(log_table(hdrs, widths, row_count=10, row_h=0.35*inch))
        story.append(Spacer(1, 8))
        story.append(small("* Stages: L=Learning, P=Practicing, M=Mastered"))
        story.append(Spacer(1, 8))
        story.append(section_header("  Training Notes & Observations"))
        story.append(Spacer(1, 4))
        for row in blank_line_row(4):
            story.append(row)
        story.append(PageBreak())


def grooming_log(story, count=2):
    for i in range(count):
        story.append(h1("Grooming Log"))
        story.append(Spacer(1, 0.08*inch))
        hdrs = ["Date", "Bath", "Brush", "Nails", "Ears", "Teeth", "Haircut", "Groomer / Notes"]
        widths = [0.7*inch, 0.45*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.55*inch, 0.6*inch, 0.9*inch]
        story.append(log_table(hdrs, widths, row_count=12, row_h=0.3*inch))
        story.append(Spacer(1, 8))
        story.append(section_header("  Grooming Notes"))
        story.append(Spacer(1, 4))
        for row in blank_line_row(4):
            story.append(row)
        story.append(PageBreak())


def daily_walk_log(story, count=4):
    for i in range(count):
        story.append(h1("Daily Walk & Activity Log"))
        story.append(Spacer(1, 0.08*inch))
        hdrs = ["Date", "Walk 1\nTime/Dist", "Walk 2\nTime/Dist", "Play\nTime", "Mood*", "Poop ✓", "Notes"]
        widths = [0.65*inch, 0.85*inch, 0.85*inch, 0.6*inch, 0.55*inch, 0.5*inch, 0.7*inch]
        story.append(log_table(hdrs, widths, row_count=12, row_h=0.32*inch))
        story.append(Spacer(1, 6))
        story.append(small("* Mood: H=Happy, C=Calm, A=Anxious, T=Tired"))
        story.append(PageBreak())


def incident_log(story):
    story.append(h1("Incident & Injury Log"))
    story.append(Spacer(1, 0.08*inch))
    story.append(small("Record any accidents, unusual behavior, injuries, or health concerns here."))
    story.append(Spacer(1, 8))
    for j in range(5):
        story.append(section_header(f"  Incident {j+1}"))
        story.append(Spacer(1, 4))
        fields = [("Date:", 3.8), ("Description:", 3.8), ("Action Taken:", 3.8), ("Outcome:", 3.8)]
        for label, w in fields:
            story.append(labeled_field(label, w))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 6))
    story.append(PageBreak())


def notes_pages(story, count=3):
    for i in range(count):
        story.append(h1("Notes"))
        story.append(Spacer(1, 0.1*inch))
        for row in blank_line_row(18):
            story.append(row)
        story.append(PageBreak())


def back_page(story):
    story.append(Spacer(1, 1.2*inch))
    story.append(Paragraph("🐾", ParagraphStyle('BackPaw', fontName='Helvetica', fontSize=36,
                                                  alignment=TA_CENTER, spaceAfter=16)))
    story.append(center("Thank You for Choosing", 11, ACCENT))
    story.append(center("<b>Dog Health &amp; Training Log</b>", 14, PAW_BROWN))
    story.append(Spacer(1, 0.2*inch))
    story.append(HRFlowable(width="60%", thickness=1.5, color=PAW_TAN, spaceAfter=14))
    story.append(center("Every wag, every milestone, every vet visit —", 9, GREY))
    story.append(center("this journal holds your dog's whole story.", 9, GREY))
    story.append(Spacer(1, 0.3*inch))
    story.append(center("Published by Deokgu Studio", 8, GREY))
    story.append(PageBreak())


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def build():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=(PAGE_W, PAGE_H),
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Dog Health & Training Log",
        author="Deokgu Studio",
    )

    story = []

    cover_page(story)            # 1
    how_to_use(story)            # 1
    pet_profile(story)           # 1
    vet_visit_pages(story, 20)   # 20  (20 vet visits)
    vaccination_log(story)       # 1
    medication_log(story, 6)     # 6
    weight_tracker(story)        # 1
    weight_tracker(story)        # 1  (year 2)
    training_pages(story, 12)    # 12 (12 training spreads)
    grooming_log(story, 10)      # 10
    daily_walk_log(story, 52)    # 52 (~1 year of walks)
    incident_log(story)          # 1
    notes_pages(story, 12)       # 12
    back_page(story)             # 1
    # Total ≈ 120 pages

    doc.build(story)
    print(f"PDF generated: {OUTPUT_PATH}")
    import os
    size = os.path.getsize(OUTPUT_PATH)
    print(f"File size: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    build()
