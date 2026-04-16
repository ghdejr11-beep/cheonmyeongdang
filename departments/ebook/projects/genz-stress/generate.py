"""
Gen Z Stress Management Workbook — Amazon KDP Ready
8.5 x 11 inches, 30-day workbook format
Each day: stress prompt + journal space + coping strategy
Topics: social media detox, comparison trap, mindfulness, etc.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path
import os
import textwrap

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "GenZ_Stress_Workbook.pdf"

W, H = letter  # 8.5 x 11 inches
MARGIN = 0.75 * inch

# Colors — modern, calming palette
DARK = HexColor("#1b2838")
ACCENT = HexColor("#6c5ce7")
ACCENT2 = HexColor("#00cec9")
SOFT_BG = HexColor("#f8f6ff")
LIGHT_GRAY = HexColor("#f0f0f5")
MID_GRAY = HexColor("#cccccc")
LINE_COLOR = HexColor("#e0daf5")
TEXT_COLOR = HexColor("#2d3436")
MUTED = HexColor("#888888")

# 30 days of content
DAILY_CONTENT = [
    {
        "day": 1,
        "title": "Your Stress Baseline",
        "prompt": "On a scale of 1-10, how stressed do you feel right now? What are the top 3 things causing your stress? Don't judge them — just write them down.",
        "strategy": "Body Scan Check-In",
        "strategy_desc": "Close your eyes. Starting from your toes, slowly scan up through your body. Notice where you hold tension — jaw, shoulders, stomach. Just notice. Breathe into those spots for 3 slow breaths.",
        "theme": "Self-Awareness"
    },
    {
        "day": 2,
        "title": "The Notification Audit",
        "prompt": "How many times did you check your phone in the last hour? Which apps pull you in the most? How do you feel AFTER scrolling each one?",
        "strategy": "Notification Detox",
        "strategy_desc": "Turn off non-essential notifications for 24 hours. Keep only calls and texts from real humans. Notice how different your day feels without the constant buzzing.",
        "theme": "Digital Wellness"
    },
    {
        "day": 3,
        "title": "The Comparison Trap",
        "prompt": "Write about a time you compared yourself to someone online. What were you really feeling underneath? What would you say to a friend feeling the same way?",
        "strategy": "The 'Highlight Reel' Reminder",
        "strategy_desc": "Next time you feel envy while scrolling, pause and say: 'I'm comparing my behind-the-scenes to their highlight reel.' Write down 3 things about YOUR life you're grateful for right now.",
        "theme": "Self-Compassion"
    },
    {
        "day": 4,
        "title": "Your Stress Triggers",
        "prompt": "List 5 situations that instantly spike your stress. For each one, write whether it's something you can control, partially control, or can't control at all.",
        "strategy": "The Circle of Control",
        "strategy_desc": "Draw two circles: inner = things you CAN control, outer = things you CAN'T. Put your stressors in the right circle. Focus your energy ONLY on the inner circle today.",
        "theme": "Stress Awareness"
    },
    {
        "day": 5,
        "title": "Social Media Detox Day",
        "prompt": "Can you go 24 hours without social media? Write about what you'll do instead. If you already tried, how did it feel? What did you notice?",
        "strategy": "The 24-Hour Reset",
        "strategy_desc": "Delete social media apps from your phone for one day (not your accounts, just the apps). Replace scrolling time with: a walk, music, drawing, cooking, or just sitting with your thoughts.",
        "theme": "Digital Wellness"
    },
    {
        "day": 6,
        "title": "Sleep & Stress Connection",
        "prompt": "How many hours did you sleep last night? Rate your sleep quality 1-10. How does poor sleep affect your mood and stress the next day?",
        "strategy": "The 10-Minute Wind-Down",
        "strategy_desc": "Tonight, put your phone in another room 30 minutes before bed. Dim the lights. Do 10 minutes of slow breathing: inhale 4 counts, hold 4, exhale 6. Your body will thank you.",
        "theme": "Sleep Hygiene"
    },
    {
        "day": 7,
        "title": "Weekly Check-In #1",
        "prompt": "Look back at Days 1-6. What surprised you? Which strategy felt most helpful? Rate your stress now vs Day 1. What's one thing you want to keep doing?",
        "strategy": "Gratitude Snapshot",
        "strategy_desc": "Write down 5 small things from this week that made you smile — even tiny ones like a good song, warm food, or a funny text. Gratitude literally rewires your brain's stress response.",
        "theme": "Reflection"
    },
    {
        "day": 8,
        "title": "The Productivity Pressure",
        "prompt": "Do you feel guilty when you rest? Where does that pressure to always be 'productive' come from? Write a permission slip to yourself to do nothing today.",
        "strategy": "Intentional Rest",
        "strategy_desc": "Schedule 30 minutes of NOTHING today. Not Netflix, not scrolling — actual nothing. Sit, stare out the window, doodle. Rest is not laziness. It's how your brain processes and heals.",
        "theme": "Burnout Prevention"
    },
    {
        "day": 9,
        "title": "Your Inner Critic",
        "prompt": "Write down the meanest thing your inner voice says to you regularly. Now rewrite it as if you were talking to your best friend. Feel the difference?",
        "strategy": "Name Your Inner Critic",
        "strategy_desc": "Give your inner critic a silly name (like 'Drama Dave' or 'Negative Nancy'). When it speaks up, say: 'Oh, that's just [name] again.' This creates distance between you and the thought.",
        "theme": "Self-Compassion"
    },
    {
        "day": 10,
        "title": "Boundaries with Technology",
        "prompt": "Which online spaces drain you? Which ones actually make you feel good? Write your personal 'digital boundaries' — rules for how you want to use tech.",
        "strategy": "The Phone-Free Zone",
        "strategy_desc": "Choose one daily activity to do phone-free: meals, walks, the first 30 minutes after waking. Put a physical boundary — leave the phone in another room during that time.",
        "theme": "Digital Wellness"
    },
    {
        "day": 11,
        "title": "Anxiety vs. Excitement",
        "prompt": "Think of something making you anxious. Now ask: could this also be excitement? Write about the thin line between anxiety and anticipation in your life.",
        "strategy": "Reframe the Feeling",
        "strategy_desc": "When anxiety hits, try saying 'I'm excited' instead of 'I'm anxious.' Research shows this simple reframe actually improves performance and reduces stress hormones.",
        "theme": "Mindset Shift"
    },
    {
        "day": 12,
        "title": "The People-Pleasing Pattern",
        "prompt": "When was the last time you said 'yes' but meant 'no'? Why? What would happen if you started being honest about your capacity?",
        "strategy": "The Kind 'No'",
        "strategy_desc": "Practice this script: 'I appreciate you thinking of me, but I can't take that on right now.' Say it out loud 5 times. A 'no' to others is a 'yes' to your mental health.",
        "theme": "Boundaries"
    },
    {
        "day": 13,
        "title": "Movement as Medicine",
        "prompt": "How does your body feel when you're stressed? Where do you feel it? What type of movement (walking, dancing, stretching) makes you feel better?",
        "strategy": "The 5-Minute Shake-Off",
        "strategy_desc": "Set a timer for 5 minutes. Put on your favorite upbeat song and literally shake your body — arms, legs, head. Animals do this to release trauma. It works for humans too.",
        "theme": "Physical Wellness"
    },
    {
        "day": 14,
        "title": "Weekly Check-In #2",
        "prompt": "Halfway through Week 2! Compare your stress level now to Day 1. Which coping strategies have you actually used? What's getting easier? What's still hard?",
        "strategy": "Progress Journaling",
        "strategy_desc": "Write a letter to Day-1 You from today's perspective. What would you tell yourself? Recognizing your own growth, even small steps, builds resilience.",
        "theme": "Reflection"
    },
    {
        "day": 15,
        "title": "FOMO vs. JOMO",
        "prompt": "Write about a time FOMO (Fear Of Missing Out) ruined your mood. Now write about a time you chose JOMO (Joy Of Missing Out) and it felt great.",
        "strategy": "The JOMO Practice",
        "strategy_desc": "Tonight, deliberately miss out on something. Stay in. Don't check what others are doing. Do something that nourishes YOU. Tomorrow, write about how it actually felt.",
        "theme": "Digital Wellness"
    },
    {
        "day": 16,
        "title": "Financial Stress",
        "prompt": "Does money stress you out? Write honestly about your relationship with money. What money beliefs did you inherit from your family or social media?",
        "strategy": "The 'Enough' List",
        "strategy_desc": "Write down everything you have that is ENOUGH right now. A roof, food, a phone, people who care. Abundance isn't about having more — it's about recognizing what's already here.",
        "theme": "Financial Wellness"
    },
    {
        "day": 17,
        "title": "The Overthinking Loop",
        "prompt": "What do you overthink about most? Write out a recent overthinking spiral. Now circle the parts that were actual facts vs. stories you made up.",
        "strategy": "The 5-4-3-2-1 Grounding",
        "strategy_desc": "When caught in overthinking: Name 5 things you SEE, 4 you TOUCH, 3 you HEAR, 2 you SMELL, 1 you TASTE. This pulls your brain out of the thought spiral and into the present.",
        "theme": "Mindfulness"
    },
    {
        "day": 18,
        "title": "Friendship & Social Energy",
        "prompt": "Which friendships energize you? Which ones drain you? It's okay to admit this. Write about what you need from your social connections right now.",
        "strategy": "The Social Battery Check",
        "strategy_desc": "Before saying yes to plans, check your social battery: Full? Half? Empty? Match your commitments to your energy. It's okay to say 'I need a recharge day.'",
        "theme": "Relationships"
    },
    {
        "day": 19,
        "title": "Mindful Breathing",
        "prompt": "Try 5 minutes of focused breathing before writing today. Then describe: What thoughts came up? Was it hard to focus? How do you feel now vs. before?",
        "strategy": "Box Breathing (4-4-4-4)",
        "strategy_desc": "Breathe in for 4 seconds, hold for 4, breathe out for 4, hold for 4. Repeat 4 times. Navy SEALs use this to stay calm under extreme pressure. You can use it in class, at work, anywhere.",
        "theme": "Mindfulness"
    },
    {
        "day": 20,
        "title": "Identity & Labels",
        "prompt": "What labels do others put on you? Which ones do you put on yourself? Write about who you are BEYOND the labels. What does the real you look like?",
        "strategy": "The 'I Am' Reset",
        "strategy_desc": "Write 10 'I am' statements that feel true and empowering. Examples: 'I am learning.' 'I am enough as I am.' 'I am allowed to take up space.' Read them aloud each morning.",
        "theme": "Identity"
    },
    {
        "day": 21,
        "title": "Weekly Check-In #3",
        "prompt": "Three weeks in! What patterns have you noticed about your stress? What triggers can you now predict? What coping tools are becoming habits?",
        "strategy": "Habit Stacking",
        "strategy_desc": "Attach one stress-relief practice to something you already do daily. Example: 'After I brush my teeth, I do 2 minutes of breathing.' Small habits compound into big change.",
        "theme": "Reflection"
    },
    {
        "day": 22,
        "title": "Academic / Work Pressure",
        "prompt": "Where does your pressure to perform come from — yourself, parents, society, social media? Write honestly about the expectations weighing on you.",
        "strategy": "The 'Good Enough' Mantra",
        "strategy_desc": "Perfectionism is procrastination in disguise. Today, aim for 'good enough' on one task instead of perfect. Notice: did the world end? Probably not. B+ work done beats A+ work imagined.",
        "theme": "Performance Anxiety"
    },
    {
        "day": 23,
        "title": "The News & Doom-Scrolling",
        "prompt": "How much news/doom-scrolling do you consume daily? How does it affect your mood? Write about the difference between being informed and being overwhelmed.",
        "strategy": "The Information Diet",
        "strategy_desc": "Limit news to ONE check per day, for 10 minutes max. Unfollow accounts that make you feel hopeless. Follow ones that inspire action. You can care about the world without drowning in it.",
        "theme": "Digital Wellness"
    },
    {
        "day": 24,
        "title": "Creative Expression",
        "prompt": "When was the last time you created something just for fun? No posting, no likes, no audience. Write about what creativity means to you.",
        "strategy": "The No-Audience Creation",
        "strategy_desc": "Create something today that NO ONE will see. Draw, write a poem, make a playlist, cook something weird. The point is the process, not the product. Creativity is therapy.",
        "theme": "Self-Expression"
    },
    {
        "day": 25,
        "title": "Asking for Help",
        "prompt": "Is asking for help hard for you? Why? Write about a time someone helped you and it made things better. What's stopping you from asking now?",
        "strategy": "The Help Script",
        "strategy_desc": "Practice saying: 'I'm going through something and could use support.' You don't need to have it all together. Vulnerability is not weakness — it's the birthplace of connection.",
        "theme": "Vulnerability"
    },
    {
        "day": 26,
        "title": "Nature & Grounding",
        "prompt": "When was the last time you spent time in nature without your phone? Write about a natural place that makes you feel calm. What does it look/smell/feel like?",
        "strategy": "The 20-Minute Nature Dose",
        "strategy_desc": "Research shows 20 minutes in nature significantly lowers cortisol (stress hormone). Go outside today — a park, a yard, even a balcony. Leave the phone behind. Just be there.",
        "theme": "Nature Therapy"
    },
    {
        "day": 27,
        "title": "Future Anxiety",
        "prompt": "What scares you most about the future? Write your worst-case scenario. Now write the BEST-case scenario. Which one are you spending more mental energy on?",
        "strategy": "The 'What If' Flip",
        "strategy_desc": "When your brain says 'What if it goes wrong?', practice saying 'What if it goes RIGHT?' Train your brain to give equal airtime to positive possibilities. The future isn't written yet.",
        "theme": "Future Planning"
    },
    {
        "day": 28,
        "title": "Weekly Check-In #4",
        "prompt": "Almost done! Rate your stress 1-10. Compare it to Day 1. What are the top 3 strategies that work for YOU? What will you carry forward after Day 30?",
        "strategy": "Build Your Toolkit",
        "strategy_desc": "On a fresh page, write your personal 'Stress First Aid Kit' — the top 5 strategies that work best for you. Keep this list where you can find it when stress hits hard.",
        "theme": "Reflection"
    },
    {
        "day": 29,
        "title": "Self-Forgiveness",
        "prompt": "Write about something you're still holding against yourself. What would it feel like to let it go? Write a forgiveness letter to yourself — you deserve it.",
        "strategy": "The Release Ritual",
        "strategy_desc": "Write what you're forgiving yourself for on a separate piece of paper. Read it once. Then tear it up or safely burn it. Physical release creates emotional release. Let it go.",
        "theme": "Self-Compassion"
    },
    {
        "day": 30,
        "title": "Your New Beginning",
        "prompt": "You showed up for 30 days. Write a letter to your future self. What did you learn? What do you want to remember? How will you keep taking care of your mental health?",
        "strategy": "The Daily 2-Minute Check-In",
        "strategy_desc": "Going forward, spend just 2 minutes each morning asking: 'How am I feeling? What do I need today?' This tiny habit keeps you connected to yourself. You've got this.",
        "theme": "Continuation"
    },
]


def draw_text_wrapped(c, text, x, y, max_width, font="Helvetica", size=11, leading=15, color=TEXT_COLOR):
    """Draw wrapped text and return the new y position."""
    c.setFont(font, size)
    c.setFillColor(color)
    chars_per_line = int(max_width / (size * 0.52))
    lines = textwrap.wrap(text, width=chars_per_line)
    for line in lines:
        if y < MARGIN:
            break
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_title_page(c):
    """Interior title page."""
    c.setFillColor(DARK)
    c.rect(MARGIN+5, MARGIN+5, W - 2*MARGIN-10, H - 2*MARGIN-10, fill=1)

    # Decorative elements
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.rect(MARGIN, MARGIN, W - 2*MARGIN, H - 2*MARGIN)

    c.setStrokeColor(ACCENT2)
    c.setLineWidth(1)
    c.rect(MARGIN+0.1*inch, MARGIN+0.1*inch, W-2*MARGIN-0.2*inch, H-2*MARGIN-0.2*inch)

    # Decorative circles
    for i in range(5):
        c.setFillColor(HexColor("#6c5ce7"))
        c.setFillAlpha(0.15)
        c.circle(W * 0.2 + i * 80, H * 0.7, 20 + i * 8, fill=1)
    c.setFillAlpha(1)

    # Title
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(W/2, H * 0.52, "GEN Z STRESS")
    c.drawCentredString(W/2, H * 0.46, "MANAGEMENT")
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(ACCENT2)
    c.drawCentredString(W/2, H * 0.39, "WORKBOOK")

    # Subtitle
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawCentredString(W/2, H * 0.32, "A 30-Day Journey to Managing Stress,")
    c.drawCentredString(W/2, H * 0.29, "Building Resilience & Finding Your Calm")

    # Tags
    c.setFont("Helvetica", 10)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, H * 0.15, "Social Media Detox  |  Mindfulness  |  Self-Compassion")
    c.drawCentredString(W/2, H * 0.12, "Journaling  |  Coping Strategies  |  Weekly Check-Ins")

    # Bottom
    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, H * 0.06, "30 Daily Prompts  |  Guided Coping Strategies  |  Reflection Pages")

    c.showPage()


def draw_intro_page(c):
    """Introduction / How to use this workbook."""
    y = H - MARGIN

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, y, "How to Use This Workbook")
    y -= 40

    intro_text = (
        "This workbook is designed for YOU — a Gen Z human navigating stress in a world that "
        "never stops buzzing. Over the next 30 days, you'll explore your stress triggers, "
        "learn science-backed coping strategies, and build a personal toolkit for resilience."
    )
    y = draw_text_wrapped(c, intro_text, MARGIN, y, W - 2*MARGIN, size=12, leading=18)
    y -= 20

    steps = [
        ("Each day has 3 parts:", ""),
        ("1. Stress Prompt", "A question or reflection to help you understand your stress patterns."),
        ("2. Journal Space", "Write freely — no rules, no judgment, no wrong answers."),
        ("3. Coping Strategy", "A practical technique you can use immediately."),
    ]

    for title, desc in steps:
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(ACCENT)
        c.drawString(MARGIN + 10, y, title)
        y -= 18
        if desc:
            y = draw_text_wrapped(c, desc, MARGIN + 10, y, W - 2*MARGIN - 20, size=11, leading=16)
            y -= 10

    y -= 20
    # Tips box
    c.setFillColor(SOFT_BG)
    c.roundRect(MARGIN, y - 100, W - 2*MARGIN, 110, 10, fill=1)
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 15, y - 10, "Tips for Success:")
    c.setFont("Helvetica", 10)
    tips = [
        "- Try to write at the same time each day (morning or night works great).",
        "- Be honest. No one is reading this but you.",
        "- Don't skip the coping strategies — they work best when practiced.",
        "- It's okay to have bad days. Just show up and write something.",
        "- Celebrate completing each week. You deserve it.",
    ]
    ty = y - 28
    for tip in tips:
        c.drawString(MARGIN + 15, ty, tip)
        ty -= 15

    c.showPage()


def draw_day_spread(c, day_data):
    """Draw a 2-page spread for each day."""
    day = day_data["day"]
    theme = day_data["theme"]

    # --- PAGE 1: Prompt + Strategy ---
    y = H - MARGIN

    # Day header bar
    c.setFillColor(ACCENT)
    c.roundRect(MARGIN, y - 30, W - 2*MARGIN, 40, 8, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN + 15, y - 20, f"DAY {day}")
    c.setFont("Helvetica", 12)
    c.drawRightString(W - MARGIN - 15, y - 20, theme)
    y -= 55

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(TEXT_COLOR)
    c.drawString(MARGIN, y, day_data["title"])
    y -= 30

    # Stress check-in
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "TODAY'S STRESS LEVEL:")
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT_COLOR)
    for i in range(1, 11):
        x = MARGIN + 140 + (i-1) * 28
        c.circle(x, y + 3, 10, fill=0, stroke=1)
        c.drawCentredString(x, y, str(i))
    y -= 30

    # Prompt section
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y, "Today's Prompt")
    y -= 5
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.line(MARGIN, y, MARGIN + 120, y)
    y -= 18

    y = draw_text_wrapped(c, day_data["prompt"], MARGIN, y, W - 2*MARGIN, size=12, leading=17, color=TEXT_COLOR)
    y -= 25

    # Coping strategy box
    c.setFillColor(SOFT_BG)
    box_top = y
    # Calculate box height based on text
    chars_per_line = int((W - 2*MARGIN - 30) / (10 * 0.52))
    strategy_lines = textwrap.wrap(day_data["strategy_desc"], width=chars_per_line)
    box_height = 50 + len(strategy_lines) * 14
    c.roundRect(MARGIN, y - box_height, W - 2*MARGIN, box_height + 10, 8, fill=1)

    c.setFillColor(ACCENT2)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 15, y - 5, f"Coping Strategy: {day_data['strategy']}")
    y -= 25

    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT_COLOR)
    for line in strategy_lines:
        c.drawString(MARGIN + 15, y, line)
        y -= 14

    c.showPage()

    # --- PAGE 2: Journal Space ---
    y = H - MARGIN

    # Header
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, y, f"Day {day} — Journal Space")
    c.setFont("Helvetica", 10)
    c.setFillColor(MUTED)
    c.drawRightString(W - MARGIN, y, "Write freely. No rules.")
    y -= 25

    # Lined journal area
    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.4)
    line_spacing = 24
    while y > MARGIN + 40:
        c.line(MARGIN, y, W - MARGIN, y)
        y -= line_spacing

    # Bottom reflection
    y = MARGIN + 15
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, y, f"\"You showed up today. That matters.\" — Day {day} of 30")

    c.showPage()


def draw_weekly_reflection(c, week_num):
    """Extra reflection page at end of each week."""
    y = H - MARGIN

    c.setFillColor(ACCENT2)
    c.roundRect(MARGIN, y - 30, W - 2*MARGIN, 40, 8, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W/2, y - 20, f"WEEK {week_num} REFLECTION")
    y -= 60

    questions = [
        "What was your biggest takeaway this week?",
        "Which coping strategy worked best for you?",
        "What surprised you about your stress patterns?",
        "What do you want to do differently next week?",
        "One thing you're proud of this week:",
    ]

    for q in questions:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(TEXT_COLOR)
        c.drawString(MARGIN, y, q)
        y -= 20

        # Writing lines
        c.setStrokeColor(LINE_COLOR)
        c.setLineWidth(0.3)
        for _ in range(4):
            c.line(MARGIN, y, W - MARGIN, y)
            y -= 22
        y -= 15

    c.showPage()


def draw_final_toolkit(c):
    """Final page: personal stress toolkit."""
    y = H - MARGIN

    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W/2, y, "My Personal Stress Toolkit")
    y -= 15
    c.setFont("Helvetica", 11)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, y, "Fill this in and keep it somewhere you can find it.")
    y -= 35

    sections = [
        ("My Top 5 Coping Strategies:", 5),
        ("People I Can Reach Out To:", 3),
        ("Activities That Calm Me Down:", 4),
        ("My Warning Signs (I know I'm stressed when...):", 3),
        ("My Stress-Free Zones (places that calm me):", 3),
    ]

    for title, lines in sections:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(TEXT_COLOR)
        c.drawString(MARGIN, y, title)
        y -= 18
        c.setStrokeColor(LINE_COLOR)
        c.setLineWidth(0.3)
        for i in range(lines):
            c.drawString(MARGIN + 5, y + 4, f"{i+1}.")
            c.line(MARGIN + 20, y, W - MARGIN, y)
            y -= 22
        y -= 15

    c.showPage()


def draw_final_page(c):
    """Thank you / final page."""
    c.setFillColor(DARK)
    c.rect(MARGIN+5, MARGIN+5, W - 2*MARGIN-10, H - 2*MARGIN-10, fill=1)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W/2, H/2 + 60, "You Did It.")

    c.setFont("Helvetica", 14)
    c.setFillColor(ACCENT2)
    c.drawCentredString(W/2, H/2 + 20, "30 days of showing up for yourself.")
    c.drawCentredString(W/2, H/2 - 5, "That takes real courage.")

    c.setFont("Helvetica", 12)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, H/2 - 50, "Keep going. Keep writing. Keep breathing.")

    c.setFont("Helvetica", 10)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, H * 0.15, "If this workbook helped you,")
    c.drawCentredString(W/2, H * 0.12, "please leave a review on Amazon.")
    c.drawCentredString(W/2, H * 0.09, "Your feedback helps us reach more people who need this.")

    c.showPage()


def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("Gen Z Stress Management Workbook")
    c.setAuthor("Deokgu Studio")
    c.setSubject("30-Day Stress Management Workbook for Gen Z")

    # Title page
    draw_title_page(c)

    # Introduction
    draw_intro_page(c)

    # 30 daily spreads
    for day_data in DAILY_CONTENT:
        draw_day_spread(c, day_data)

        # Weekly reflection after days 7, 14, 21, 28
        if day_data["day"] in [7, 14, 21, 28]:
            draw_weekly_reflection(c, day_data["day"] // 7)

    # Final toolkit page
    draw_final_toolkit(c)

    # Final page
    draw_final_page(c)

    c.save()
    page_count = c.getPageNumber() - 1
    file_size = os.path.getsize(PDF_PATH) / 1024
    print(f"PDF generated: {PDF_PATH}")
    print(f"Total pages: {page_count}")
    print(f"File size: {file_size:.0f} KB")


if __name__ == "__main__":
    generate()
