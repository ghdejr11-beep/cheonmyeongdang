"""
📚 30-Day Mental Reset Journal — Amazon KDP Ready
8.5 x 11 inches, ~100 pages
Daily prompts for emotional regulation, gratitude, and mental clarity
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "Mental_Reset_Journal_Interior.pdf"
W, H = letter
M = 0.75 * inch

# Calming palette
SAGE = HexColor("#7B9E87")
SAND = HexColor("#C9B99A")
DEEP = HexColor("#2C3E50")
BLUSH = HexColor("#E8D5C4")
LINE = HexColor("#D5CEBC")
LIGHT = HexColor("#F7F4EF")
TEXT = HexColor("#3A3A3A")

DAILY_PROMPTS = [
    ("What am I holding onto that no longer serves me?", "Release"),
    ("List 3 things that went right yesterday.", "Gratitude"),
    ("What would I do today if fear didn't exist?", "Courage"),
    ("Write a letter to your past self. What would you say?", "Compassion"),
    ("What boundary do I need to set this week?", "Boundaries"),
    ("Describe your ideal morning in detail.", "Vision"),
    ("What emotion have I been avoiding? Why?", "Awareness"),
    ("List 5 things that make me feel calm.", "Peace"),
    ("What story am I telling myself that isn't true?", "Truth"),
    ("Write about someone who believed in you.", "Connection"),
    ("What does 'enough' look like for me?", "Contentment"),
    ("If I could change one habit starting today, what would it be?", "Growth"),
    ("What am I grateful for that I usually take for granted?", "Gratitude"),
    ("Describe a moment when you felt truly free.", "Freedom"),
    ("What would I say to someone going through what I'm going through?", "Wisdom"),
    ("List 3 things I did well this week.", "Pride"),
    ("What does my body need right now?", "Body"),
    ("Write about a time you surprised yourself.", "Strength"),
    ("What would my life look like without social media for a week?", "Detox"),
    ("Name one thing I can forgive myself for today.", "Forgiveness"),
    ("What brings me joy that costs nothing?", "Joy"),
    ("Write a 'not to-do' list — things I will stop doing.", "Release"),
    ("What relationship needs more of my attention?", "Love"),
    ("Describe the person I want to become in 6 months.", "Vision"),
    ("What is one kind thing I can do for myself today?", "Self-Care"),
    ("Write about a challenge that made me stronger.", "Resilience"),
    ("What does peace feel like in my body?", "Mindfulness"),
    ("List everything that's worrying me. Then circle what I can control.", "Control"),
    ("Write a thank-you note to someone (even if you never send it).", "Gratitude"),
    ("How do I want to feel when I wake up tomorrow?", "Intention"),
]


def draw_title_page(c):
    c.setFillColor(DEEP)
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
    c.setStrokeColor(SAND)
    c.setLineWidth(2)
    c.rect(M, M, W-2*M, H-2*M)

    cx = W/2
    c.setFillColor(SAGE)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(cx, H*0.68, "— 30 DAYS —")

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 38)
    c.drawCentredString(cx, H*0.58, "MENTAL")
    c.drawCentredString(cx, H*0.52, "RESET")

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(SAND)
    c.drawCentredString(cx, H*0.45, "JOURNAL")

    c.setStrokeColor(SAND)
    c.setLineWidth(1)
    c.line(cx-80, H*0.43, cx+80, H*0.43)

    c.setFont("Helvetica", 13)
    c.setFillColor(HexColor("#aabbaa"))
    c.drawCentredString(cx, H*0.36, "Daily Prompts for Clarity,")
    c.drawCentredString(cx, H*0.33, "Calm, and Emotional Freedom")

    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#888888"))
    c.drawCentredString(cx, M+20, "Guided Journal  |  30 Days  |  100+ Pages")
    c.showPage()


def draw_intro(c):
    y = H - M
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(SAGE)
    c.drawCentredString(W/2, y, "Before You Begin")
    y -= 40

    paras = [
        "This journal is not about fixing yourself. You are not broken.",
        "This is about creating space — space to breathe, to think clearly, and to reconnect with what matters to you.",
        "Each day has one prompt. That's it. No pressure to write a novel. A single sentence counts. Some days you'll write pages. Other days, three words. Both are valid.",
        "There are no rules here. Skip days if you need to. Go out of order. Tear out a page and start over. This is YOUR journal.",
        "The only thing I ask: be honest with yourself. Not perfect. Honest.",
        "Ready? Take a deep breath. Let's begin."
    ]

    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT)
    for p in paras:
        words = p.split()
        line = ""
        for w in words:
            test = line + " " + w if line else w
            if c.stringWidth(test, "Helvetica", 11) > W - 2*M - 20:
                c.drawString(M+10, y, line)
                y -= 16
                line = w
            else:
                line = test
        if line:
            c.drawString(M+10, y, line)
            y -= 16
        y -= 10
    c.showPage()


def draw_daily_page(c, day, prompt, theme):
    y = H - M

    # Header
    c.setFillColor(LIGHT)
    c.rect(M, H - M - 40, W - 2*M, 40, fill=1)
    c.setFillColor(SAGE)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(M, H-38, f"Day {day}")
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT)
    c.drawString(M+70, H-38, f"Theme: {theme}")
    c.setFillColor(HexColor("#999999"))
    c.drawRightString(W-M, H-38, "Date: _______________")

    y = H - M - 50

    # Mood check
    c.setFillColor(SAGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(M, y, "How I feel right now:")
    moods = ["Anxious", "Low", "Neutral", "Calm", "Hopeful"]
    ex = M + 145
    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT)
    for mood in moods:
        c.circle(ex, y+3, 5)
        c.drawString(ex+8, y, mood)
        ex += 70
    y -= 30

    # Prompt
    c.setFillColor(BLUSH)
    c.roundRect(M, y-45, W-2*M, 50, 8, fill=1)
    c.setFillColor(DEEP)
    c.setFont("Helvetica-Bold", 12)
    # Word wrap prompt
    words = prompt.split()
    line = ""
    py = y - 15
    for w in words:
        test = line + " " + w if line else w
        if c.stringWidth(test, "Helvetica-Bold", 12) > W - 2*M - 30:
            c.drawCentredString(W/2, py, line)
            py -= 16
            line = w
        else:
            line = test
    if line:
        c.drawCentredString(W/2, py, line)
    y -= 65

    # Writing lines
    c.setStrokeColor(LINE)
    c.setLineWidth(0.3)
    line_count = 0
    while y > M + 100:
        c.line(M, y, W-M, y)
        y -= 22
        line_count += 1

    # Bottom section
    y -= 5
    c.setFillColor(SAGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(M, y, "One thing I'm letting go of today:")
    y -= 18
    c.setStrokeColor(LINE)
    c.setDash(1, 2)
    c.line(M, y, W-M, y)
    c.setDash()

    y -= 25
    c.setFillColor(SAGE)
    c.drawString(M, y, "One thing I'm grateful for:")
    y -= 18
    c.setStrokeColor(LINE)
    c.setDash(1, 2)
    c.line(M, y, W-M, y)
    c.setDash()

    c.showPage()


def draw_reflection_page(c, week):
    y = H - M
    c.setFillColor(DEEP)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W/2, y, f"Week {week} Reflection")
    y -= 35

    qs = [
        ("What shifted in me this week?", 5),
        ("What pattern did I notice?", 4),
        ("What do I want more of?", 4),
        ("What do I want less of?", 4),
        ("A word that describes this week:", 2),
    ]
    for q, lines in qs:
        c.setFillColor(SAGE)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(M, y, q)
        y -= 18
        c.setStrokeColor(LINE)
        c.setLineWidth(0.3)
        for _ in range(lines):
            c.line(M+10, y, W-M, y)
            y -= 20
        y -= 12
    c.showPage()


def draw_free_write(c, num):
    y = H - M
    c.setFillColor(SAND)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(M, y, f"Free Write — Page {num}")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#999"))
    c.drawString(M, y-18, "No prompt. No rules. Just write.")
    y -= 45
    c.setStrokeColor(LINE)
    c.setLineWidth(0.3)
    while y > M+10:
        c.line(M, y, W-M, y)
        y -= 22
    c.showPage()


def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("30-Day Mental Reset Journal")
    c.setAuthor("Deokgu Studio")

    draw_title_page(c)
    draw_intro(c)

    for day in range(1, 31):
        prompt, theme = DAILY_PROMPTS[day-1]
        draw_daily_page(c, day, prompt, theme)

        if day % 7 == 0:
            draw_reflection_page(c, day // 7)

    # 10 free write pages
    for i in range(1, 11):
        draw_free_write(c, i)

    # Final page
    c.setFillColor(DEEP)
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
    c.setFillColor(SAGE)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W/2, H/2+30, "You did it.")
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#ffffff"))
    c.drawCentredString(W/2, H/2-10, "30 days of showing up for yourself.")
    c.drawCentredString(W/2, H/2-35, "That takes courage.")
    c.setFillColor(SAND)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H/2-75, "If this journal helped you,")
    c.drawCentredString(W/2, H/2-93, "please leave a review on Amazon.")
    c.showPage()

    c.save()
    print(f"PDF: {PDF_PATH}")
    print(f"Pages: {c.getPageNumber()-1}")
    print(f"Size: {os.path.getsize(PDF_PATH)/1024:.0f} KB")

if __name__ == "__main__":
    generate()
