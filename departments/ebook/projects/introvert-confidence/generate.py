"""
Confidence Building for Introverts — Amazon KDP Ready
6 x 9 inches (standard KDP non-fiction), 20 chapters
Topics: leveraging introvert strengths, social energy management,
workplace presence, networking, etc.
"""

from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path
import os
import textwrap

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "Confidence_Building_Introverts.pdf"

# 6 x 9 inches
W = 6 * inch
H = 9 * inch
MARGIN_OUTER = 0.6 * inch
MARGIN_INNER = 0.75 * inch  # Slightly wider for binding
MARGIN_TOP = 0.6 * inch
MARGIN_BOTTOM = 0.6 * inch

# Colors — sophisticated, calm
DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#2d6a4f")
ACCENT2 = HexColor("#40916c")
LIGHT_BG = HexColor("#f5f7f5")
TEXT_COLOR = HexColor("#2d3436")
MUTED = HexColor("#777777")
LINE_COLOR = HexColor("#d8e2dc")
HEADER_COLOR = HexColor("#1b4332")

PAGE_NUM = [0]  # mutable counter for page numbers


def next_page(c, is_left=None):
    """Show page and handle page numbering."""
    PAGE_NUM[0] += 1
    pn = PAGE_NUM[0]
    if pn > 4:  # Don't number first few pages
        c.setFont("Helvetica", 8)
        c.setFillColor(MUTED)
        c.drawCentredString(W/2, 0.4 * inch, str(pn))
    c.showPage()


def get_margin_left():
    """Left margin (alternates for odd/even in real print, simplified here)."""
    return MARGIN_OUTER


def draw_text_block(c, text, x, y, max_width, font="Helvetica", size=10, leading=14.5, color=TEXT_COLOR, indent=0):
    """Draw a block of wrapped text. Returns new y position."""
    c.setFont(font, size)
    c.setFillColor(color)
    chars_per_line = int(max_width / (size * 0.48))
    lines = textwrap.wrap(text, width=chars_per_line)
    for line in lines:
        if y < MARGIN_BOTTOM + 20:
            next_page(c)
            y = H - MARGIN_TOP
            c.setFont(font, size)
            c.setFillColor(color)
        c.drawString(x + indent, y, line)
        y -= leading
    return y


def draw_title_page(c):
    """Interior title page."""
    c.setFillColor(DARK)
    c.rect(MARGIN_OUTER, MARGIN_OUTER, W - 2*MARGIN_OUTER, H - 2*MARGIN_OUTER, fill=1)

    # Border
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.rect(MARGIN_OUTER, MARGIN_OUTER, W - 2*MARGIN_OUTER, H - 2*MARGIN_OUTER)

    # Title
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(W/2, H * 0.58, "CONFIDENCE")
    c.drawCentredString(W/2, H * 0.53, "BUILDING")

    c.setFont("Helvetica", 16)
    c.setFillColor(ACCENT2)
    c.drawCentredString(W/2, H * 0.46, "for Introverts")

    # Decorative line
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1)
    c.line(W*0.3, H*0.43, W*0.7, H*0.43)

    # Subtitle
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawCentredString(W/2, H * 0.38, "Embrace Your Quiet Strengths.")
    c.drawCentredString(W/2, H * 0.35, "Own Every Room You Walk Into.")

    # Bottom
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, H * 0.08, "20 Chapters  |  Practical Strategies  |  Real-World Exercises")

    next_page(c)


def draw_copyright_page(c):
    """Copyright page."""
    y = H * 0.4

    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)

    lines = [
        "Confidence Building for Introverts",
        "",
        "Copyright 2025 Deokgu Studio",
        "All rights reserved.",
        "",
        "No part of this book may be reproduced in any form",
        "without written permission from the publisher.",
        "",
        "This book is intended for informational purposes only.",
        "It is not a substitute for professional mental health advice.",
        "",
        "Published by Deokgu Studio",
        "First Edition",
    ]

    for line in lines:
        c.drawCentredString(W/2, y, line)
        y -= 14

    next_page(c)


def draw_toc(c, chapters):
    """Table of contents."""
    y = H - MARGIN_TOP
    ml = get_margin_left()

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HEADER_COLOR)
    c.drawCentredString(W/2, y, "Contents")
    y -= 40

    # Intro
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT_COLOR)
    c.drawString(ml, y, "Introduction")
    y -= 20

    for i, ch in enumerate(chapters):
        if y < MARGIN_BOTTOM + 30:
            next_page(c)
            y = H - MARGIN_TOP

        c.setFont("Helvetica", 10)
        c.setFillColor(TEXT_COLOR)
        label = f"Chapter {i+1}: {ch['title']}"

        # Truncate if too long
        if len(label) > 50:
            label = label[:47] + "..."

        c.drawString(ml, y, label)
        y -= 18

    y -= 10
    c.drawString(ml, y, "Conclusion: Your Introvert Advantage")
    y -= 18
    c.drawString(ml, y, "Recommended Resources")

    next_page(c)


def draw_introduction(c):
    """Introduction section."""
    y = H - MARGIN_TOP
    ml = get_margin_left()
    text_w = W - MARGIN_OUTER - MARGIN_INNER

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HEADER_COLOR)
    c.drawCentredString(W/2, y, "Introduction")
    y -= 35

    paragraphs = [
        "If you've ever been told to 'speak up more,' 'put yourself out there,' or 'stop being so quiet,' this book is for you.",

        "For too long, confidence has been defined by extroverted standards: being loud, dominating conversations, working the room. But true confidence doesn't require volume. It requires alignment — being at peace with who you are and knowing your worth, even when you're the quietest person in the room.",

        "Introversion is not a flaw to fix. It's a temperament that comes with extraordinary strengths: deep thinking, careful observation, meaningful connection, and focused persistence. The problem isn't that introverts lack confidence. The problem is that the world has been measuring confidence with the wrong ruler.",

        "This book will not try to turn you into an extrovert. Instead, it will help you:",

        "- Understand the science behind introversion and why your brain works differently (not worse).",
        "- Identify and leverage your natural strengths in social, professional, and personal settings.",
        "- Build genuine confidence that feels authentic, not performative.",
        "- Manage your social energy so you can show up powerfully without burning out.",
        "- Navigate workplaces, relationships, and networking events on your own terms.",

        "Each chapter includes practical exercises, real-world strategies, and reflection questions designed specifically for the introverted mind. This isn't generic self-help. This is a roadmap built for you.",

        "You don't need to become someone else to be confident. You just need to become more of who you already are.",

        "Let's begin.",
    ]

    for para in paragraphs:
        y = draw_text_block(c, para, ml, y, text_w, size=10, leading=14.5)
        y -= 10

    next_page(c)


# 20 Chapters with full content
CHAPTERS = [
    {
        "title": "The Introvert Advantage",
        "sections": [
            ("Understanding Your Wiring",
             "Introversion is a neurological trait, not a personality defect. Research by Dr. Marti Olsen Laney shows that introverts use a different dominant neurotransmitter pathway than extroverts. While extroverts run on dopamine (the reward chemical), introverts are more sensitive to acetylcholine, a neurotransmitter linked to deep thinking and internal reflection.\n\n"
             "This means your brain is literally wired for depth over breadth. You process information more thoroughly, consider consequences more carefully, and form deeper connections with fewer people. These aren't weaknesses — they're superpowers in a world that desperately needs more thoughtfulness."),
            ("The Power of the Quiet Mind",
             "While the world celebrates quick talkers and instant responses, introverts possess something increasingly rare: the ability to think before speaking. This leads to more thoughtful contributions, fewer regrettable statements, and ideas that have been properly vetted before they hit the air.\n\n"
             "In meetings, introverts often have the best ideas — they just share them last (or not at all). This chapter is about learning to trust that your delayed response isn't a weakness. It's a processing advantage."),
            ("Redefining Confidence",
             "Confidence isn't about being comfortable in every situation. It's about knowing you can handle whatever comes. For introverts, this often means quiet confidence: an inner steadiness that doesn't need external validation.\n\n"
             "Think of confident introverts you admire: Bill Gates, Rosa Parks, J.K. Rowling, Barack Obama. Their confidence didn't come from being the loudest. It came from deep preparation, clear values, and knowing their own worth."),
            ("Exercise: Your Introvert Inventory",
             "Take 10 minutes to write down: (1) Three situations where being quiet actually helped you. (2) Three compliments people have given you about your thoughtfulness, listening, or insight. (3) One area where you've been trying to act extroverted and it's exhausting you.\n\n"
             "Keep this inventory. We'll build on it throughout the book."),
        ]
    },
    {
        "title": "The Science of Introversion",
        "sections": [
            ("Brain Chemistry Differences",
             "Functional MRI studies reveal that introverts have more blood flow to the frontal lobe — the area responsible for planning, problem-solving, and internal thought. Extroverts show more activity in areas linked to external sensory processing.\n\n"
             "This explains why introverts often feel overwhelmed in stimulating environments but thrive in focused, calm settings. Your brain isn't underperforming in social situations — it's processing too much, not too little."),
            ("The Overstimulation Problem",
             "Introverts have a lower threshold for dopamine stimulation. What feels 'just right' for an extrovert can feel overwhelming for an introvert. This is why parties, open offices, and crowded events drain you — your nervous system is processing every conversation, facial expression, and environmental detail simultaneously.\n\n"
             "Understanding this isn't an excuse to avoid everything. It's information that helps you plan: when to engage, when to recharge, and how to set yourself up for success in high-stimulation environments."),
            ("The Introvert-Extrovert Spectrum",
             "Introversion isn't binary. You exist on a spectrum, and where you fall can change depending on context, energy levels, and comfort. Some introverts are highly social in small groups but need solitude to recharge. Others are quietly confident one-on-one but freeze in group settings.\n\n"
             "The goal isn't to move yourself toward the extroverted end of the spectrum. It's to understand where you naturally sit and optimize from there."),
            ("Exercise: Energy Audit",
             "For one week, track your energy levels throughout each day. Note: (1) What activities drained you? (2) What recharged you? (3) When did you feel most confident? (4) When did you feel most anxious? Look for patterns. Your energy data will guide every strategy in this book."),
        ]
    },
    {
        "title": "Dismantling the Confidence Myth",
        "sections": [
            ("What Confidence Actually Looks Like",
             "Pop culture has sold us a specific image of confidence: the person who walks into a room and commands attention, speaks first in meetings, and never seems to doubt themselves. This is performance, not confidence.\n\n"
             "Real confidence is quiet. It's the person who doesn't need to prove themselves. Who listens more than they talk. Who can sit in silence without panic. Who says 'I don't know' without shame. That sounds a lot like an introvert, doesn't it?"),
            ("The Fake Confidence Trap",
             "Many introverts try to build confidence by mimicking extroverted behavior: forcing small talk, pretending to love networking, speaking up just to be seen. This creates 'performative confidence' — which is exhausting and unsustainable.\n\n"
             "When you build confidence on a foundation that isn't you, it collapses under pressure. Authentic confidence means finding YOUR way to show up, not copying someone else's."),
            ("Imposter Syndrome and Introverts",
             "Introverts are particularly susceptible to imposter syndrome because they tend to internalize and overthink. If you've ever felt like you don't belong, like your success is a fluke, or like everyone else has it figured out — you're not alone. And you're not an imposter.\n\n"
             "Imposter syndrome often hits hardest when you're growing. It's a sign you're pushing boundaries, not a sign you don't belong."),
            ("Exercise: Confidence Redefined",
             "Write your own definition of confidence. Not society's definition — yours. Start with: 'For me, confidence means...' Examples: 'Confidence means trusting my preparation.' 'Confidence means not needing everyone to like me.' 'Confidence means speaking when I have something valuable to say.'"),
        ]
    },
    {
        "title": "Building Your Confidence Foundation",
        "sections": [
            ("Values-Based Confidence",
             "The most unshakeable confidence comes from knowing your values and living by them. When you're clear on what matters to you — honesty, creativity, kindness, excellence — you have an internal compass that doesn't waver based on other people's opinions.\n\n"
             "Introverts are naturally reflective, which gives you an advantage in values work. You've likely spent more time thinking about what matters to you than most people ever will."),
            ("The Preparation Advantage",
             "Introverts tend to prepare thoroughly, and preparation is confidence's best friend. Whether it's a presentation, a difficult conversation, or a job interview — the more prepared you are, the more confident you feel.\n\n"
             "Lean into this strength. Don't apologize for needing preparation time. Embrace it as your secret weapon. The person who prepares the most usually performs the best."),
            ("Small Wins, Big Momentum",
             "Confidence isn't built in dramatic moments. It's built through consistent small wins: sending the email, asking the question, sharing the idea, having the conversation. Each small win deposits into your confidence account.\n\n"
             "Start where you are. If public speaking terrifies you, don't start with a TED Talk. Start with one comment in a meeting. One question at a workshop. One story at dinner. Small wins compound."),
            ("Exercise: 30-Day Confidence Challenge",
             "Set one small confidence goal for each day this week. Example: Day 1: Make eye contact and smile at a stranger. Day 2: Share one opinion in a group conversation. Day 3: Compliment someone you don't know well. Day 4: Ask a question in a meeting or class. Day 5: Say 'no' to one thing you don't want to do. Track how each action makes you feel afterward."),
        ]
    },
    {
        "title": "Social Energy Management",
        "sections": [
            ("Your Social Battery Is Real",
             "Think of your social energy as a phone battery. Extroverts charge by being around people. Introverts drain. This isn't a character flaw — it's neuroscience. Knowing your battery capacity is the first step to managing it.\n\n"
             "A fully charged introvert can be magnetic, engaging, and socially brilliant. A depleted one becomes irritable, anxious, and withdrawn. The difference isn't personality — it's energy management."),
            ("Strategic Recharging",
             "Recharging doesn't mean hiding in your room forever. It means intentionally creating recovery spaces: 15 minutes alone before a social event, a quiet lunch in the middle of a busy day, or arriving early to acclimate before the crowd arrives.\n\n"
             "Plan your recharge time like you plan your meetings. Block it on your calendar. Protect it. This isn't selfishness — it's self-preservation."),
            ("The Art of the Graceful Exit",
             "You don't owe anyone an explanation for leaving early. But having a graceful exit strategy reduces anxiety before events. Some proven approaches: 'I have an early morning tomorrow.' 'I'm going to head out — this was wonderful.' Or simply: 'I've hit my limit and need to recharge.'\n\n"
             "The last option, radical honesty, is surprisingly effective. Most people respect it."),
            ("Exercise: Energy Budget",
             "Look at your week ahead. For each social commitment, estimate the energy cost (1-10). Total it up. Now look at your recovery time. Is there enough? If your budget is in the red, it's time to renegotiate. Cancel or postpone the lowest-priority commitments."),
        ]
    },
    {
        "title": "The Power of Deep Listening",
        "sections": [
            ("Why Introverts Are Natural Listeners",
             "In a world of talkers, listeners are rare and incredibly valuable. Introverts don't just hear words — they process tone, body language, subtext, and emotion. This makes you an exceptional listener, and listening is one of the most powerful confidence tools that exists.\n\n"
             "When you truly listen to someone, they feel seen. They trust you. They open up. And in that moment, you hold quiet power."),
            ("Listening as a Leadership Skill",
             "The best leaders aren't the loudest. They're the ones who ask great questions and actually listen to the answers. Studies show that teams led by listening-oriented leaders outperform those led by dominant talkers.\n\n"
             "If you're an introvert who listens well, you already have a leadership skill that most people never develop."),
            ("Strategic Listening in Conversations",
             "Deep listening isn't just passive receiving — it can be active and strategic. Use techniques like: reflecting back ('What I'm hearing is...'), asking follow-up questions ('Can you tell me more about...'), and summarizing ('So the key issue is...'). These moves show engagement without requiring you to dominate the conversation."),
            ("Exercise: The Listening Challenge",
             "In your next three conversations, practice only asking questions and listening. Don't share your own stories or opinions unless asked. Afterward, notice: How did the other person respond? Did they seem more engaged? How did it feel for you? What did you learn that you wouldn't have learned if you'd been talking?"),
        ]
    },
    {
        "title": "Speaking Up Without Burning Out",
        "sections": [
            ("Quality Over Quantity",
             "You don't need to talk more. You need to talk strategically. Introverts who speak less but say more valuable things are often perceived as more credible and thoughtful than people who fill every silence.\n\n"
             "The goal isn't to increase your word count. It's to increase the impact of the words you do say."),
            ("The Power of the Pause",
             "Silence makes most people uncomfortable. But for introverts, silence is a tool. Pausing before you respond signals thoughtfulness, not uncertainty. It gives your words more weight.\n\n"
             "Try this: when someone asks you a question, take a full breath before responding. The pause feels eternal to you but normal to others. And your answer will be better for it."),
            ("Prepared Spontaneity",
             "This sounds contradictory, but it works. Before meetings, events, or conversations, prepare 2-3 talking points, questions, or observations. This gives you a 'script' to fall back on, which reduces anxiety and helps you contribute without feeling put on the spot.\n\n"
             "It's not fake — it's strategic. Even the best public speakers prepare their 'spontaneous' remarks."),
            ("Exercise: The One Comment Rule",
             "For the next week, make ONE meaningful comment in every group conversation you're in. Just one. It can be a question, an observation, or an agreement with someone else's point. The goal is to practice showing up vocally in a way that feels manageable and authentic."),
        ]
    },
    {
        "title": "Workplace Confidence for Introverts",
        "sections": [
            ("The Open Office Survival Guide",
             "Open-plan offices are an introvert's nightmare. Constant noise, interruptions, and lack of privacy drain your energy and tank your productivity. But you can adapt without suffering.\n\n"
             "Strategies: Noise-canceling headphones (the universal 'don't disturb' signal). Booking meeting rooms for solo work. Arriving early or staying late for quiet hours. Setting 'focus blocks' on your calendar that others can see."),
            ("Making Your Work Visible",
             "Introverts often do excellent work that goes unnoticed because they don't self-promote. This isn't modesty — it's a career limiter. You need to make your contributions visible without feeling like a braggart.\n\n"
             "Try: Sending brief weekly summaries to your manager. Sharing your process, not just results, in team meetings. Writing follow-up emails after conversations ('As we discussed, here's what I'll deliver...'). Let your work speak, but make sure it has a microphone."),
            ("Meetings Without Misery",
             "Meetings are where introverts feel most invisible. You have great ideas but struggle to interject in fast-paced discussions. Solutions: Ask for the agenda beforehand so you can prepare. Use chat features in virtual meetings to contribute. Ask to go first or be called on directly. Send a follow-up email with your thoughts after the meeting."),
            ("Exercise: Workplace Confidence Plan",
             "Write down your three biggest confidence challenges at work. For each one, create a specific strategy using the tools from this chapter. Example: Challenge: 'I never speak in meetings.' Strategy: 'I will prepare one question before each meeting and ask it within the first 10 minutes.'"),
        ]
    },
    {
        "title": "Networking for People Who Hate Networking",
        "sections": [
            ("Why Traditional Networking Fails Introverts",
             "Walking into a room of strangers, making small talk, and handing out business cards — this model of networking was designed by extroverts for extroverts. No wonder it feels awful.\n\n"
             "But networking is essential for career growth. The solution isn't to force yourself through terrible networking events. It's to redefine networking on your terms."),
            ("The Introvert's Networking Playbook",
             "One deep conversation beats twenty shallow ones. Introverts excel at building genuine, lasting connections — which is what networking is actually about. Your approach: (1) Go to smaller, focused events instead of large mixers. (2) Set a goal of having 2-3 meaningful conversations, not meeting everyone. (3) Follow up within 48 hours with a personalized message. (4) Build relationships online first, then meet in person."),
            ("The Power of One-on-One",
             "Your networking superpower is the coffee meeting. While extroverts collect contacts, you build relationships. Suggest one-on-one meetups: 'I'd love to grab coffee and hear more about your work.' This plays to your strength of deep, focused conversation.\n\n"
             "One genuine connection is worth more than a hundred business cards."),
            ("Exercise: Networking Reframe",
             "Write down your worst networking experience. What made it terrible? Now design your ideal networking scenario. What would make it comfortable? Use your answers to create a personal networking plan: where you'll go, how you'll engage, and what success looks like for YOU."),
        ]
    },
    {
        "title": "Confident Communication Skills",
        "sections": [
            ("The Power of Written Communication",
             "Many introverts communicate more powerfully in writing than in speech. This is a strength, not a limitation. In today's digital world, written communication is a superpower: emails, reports, proposals, and messages are often more influential than spoken words.\n\n"
             "Lean into this. Volunteer for written tasks. Send thoughtful emails. Document your ideas. Your written words will outlast anyone's spoken ones."),
            ("Body Language for Quiet Confidence",
             "You don't need to be loud to appear confident. Body language accounts for over 50% of communication. Key adjustments: Stand and sit with your shoulders back and down. Make comfortable eye contact (the 'triangle technique': alternate between both eyes and the mouth). Take up appropriate space — don't shrink. Use slow, deliberate gestures instead of fidgeting."),
            ("The Art of Small Talk (Without Hating It)",
             "Small talk doesn't have to be superficial. Introverts can transform small talk into meaningful conversation with better questions: Instead of 'What do you do?' try 'What are you excited about right now?' Instead of 'How are you?' try 'What's been the best part of your week?'\n\n"
             "Better questions lead to better answers, which lead to the deeper conversations introverts actually enjoy."),
            ("Exercise: Communication Inventory",
             "Rate yourself 1-10 on: (1) Written communication, (2) One-on-one conversation, (3) Small group discussion, (4) Large group speaking, (5) Body language awareness. Identify your top 2 strengths and your biggest growth area. Create one specific practice for your growth area this week."),
        ]
    },
    {
        "title": "Setting Boundaries with Grace",
        "sections": [
            ("Why Introverts Struggle with Boundaries",
             "Introverts often absorb other people's emotions and energy, making boundary-setting feel selfish or confrontational. But boundaries aren't walls — they're filters. They let the good in and keep the draining out.\n\n"
             "Without boundaries, you'll burn out trying to meet everyone else's needs while neglecting your own. With boundaries, you show up as your best self for the people and activities that matter most."),
            ("The Boundary Scripts",
             "Having pre-prepared phrases makes boundary-setting easier: 'I need some time to think about that before I commit.' 'I can't do that this week, but let me suggest an alternative.' 'I appreciate the invitation, but I need a quiet evening.' 'I work best when I have uninterrupted focus time.'\n\n"
             "Practice these until they feel natural. Boundaries are a skill, and skills improve with repetition."),
            ("Boundaries in Relationships",
             "The people who love you should respect your need for solitude. If a friend or partner constantly pressures you to be more social, have an honest conversation: 'My need for alone time isn't about you. It's how I recharge so I can show up fully when we're together.'\n\n"
             "Healthy relationships have space for both togetherness and solitude."),
            ("Exercise: Boundary Audit",
             "List five areas where your boundaries are weak or nonexistent. For each one, write: (1) What currently happens. (2) What you want to happen instead. (3) The exact words you'll use to set the boundary. Practice saying them out loud until they feel comfortable."),
        ]
    },
    {
        "title": "Overcoming Social Anxiety",
        "sections": [
            ("Introversion vs. Social Anxiety",
             "Introversion and social anxiety are not the same thing, but they often coexist. Introversion is a preference for less stimulation. Social anxiety is a fear of judgment. You can be an introvert without social anxiety, and you can have social anxiety as an extrovert.\n\n"
             "If social situations cause intense fear, physical symptoms (racing heart, sweating, nausea), or avoidance that limits your life, that's anxiety — and it's treatable."),
            ("Cognitive Reframing for Social Situations",
             "Social anxiety thrives on catastrophic thinking: 'Everyone will judge me.' 'I'll say something stupid.' 'They'll think I'm boring.' Challenge these thoughts with evidence: Has everyone actually judged you before? Have you truly never had a good conversation?\n\n"
             "Replace 'they'll think I'm boring' with 'most people are too worried about themselves to judge me.' This is almost always true."),
            ("The Gradual Exposure Approach",
             "Overcoming social anxiety works best through gradual exposure, not forced immersion. Start with low-stakes social interactions and slowly increase the challenge: (1) Order coffee while making eye contact. (2) Compliment a stranger. (3) Attend a small event for 30 minutes. (4) Introduce yourself to one new person. (5) Share an idea in a group of 5+ people.\n\n"
             "Each level builds on the last. There's no rush."),
            ("Exercise: Anxiety Ladder",
             "Create your personal anxiety ladder with 10 rungs. Rung 1 is the least anxiety-provoking social action you can imagine. Rung 10 is the most terrifying. Write a specific action for each rung. This week, practice Rung 1 three times. Next week, move to Rung 2. Slow, steady progress beats dramatic leaps."),
        ]
    },
    {
        "title": "The Introvert's Guide to Leadership",
        "sections": [
            ("Quiet Leadership Is Real Leadership",
             "Jim Collins' research on Level 5 Leaders — the most effective leaders of the most successful companies — found they were overwhelmingly quiet, humble, and introverted. They led through listening, empowering others, and deep strategic thinking.\n\n"
             "You don't need charisma to lead. You need clarity, consistency, and the ability to bring out the best in others. Introverts excel at all three."),
            ("Leading Through Questions",
             "Extroverted leaders tend to tell. Introverted leaders tend to ask. And asking is more powerful. When you ask thoughtful questions, you: Empower your team to think for themselves. Gather better information before making decisions. Show respect for others' expertise. Build trust through genuine curiosity.\n\n"
             "The best question a leader can ask: 'What do you think?' — and then actually listen."),
            ("Managing Energy as a Leader",
             "Leadership roles demand social energy that can be particularly draining for introverts. Protect yourself with these strategies: Schedule recovery time between meetings. Use one-on-one conversations instead of group check-ins when possible. Delegate the 'rallying the troops' to an extroverted team member. Save your energy for the moments that truly need your presence."),
            ("Exercise: Your Leadership Style",
             "Describe a leader you admire who is quiet or introverted. What makes them effective? Now write down your top 3 leadership strengths and how introversion contributes to each. Finally, identify one leadership situation that drains you and create a strategy to manage it."),
        ]
    },
    {
        "title": "Dating and Relationships as an Introvert",
        "sections": [
            ("Dating Doesn't Have to Be Exhausting",
             "The traditional dating playbook — bars, parties, group outings — is designed for extroverts. Introverts can date successfully by choosing environments that play to their strengths: quiet restaurants, coffee shops, museums, nature walks, or cooking together at home.\n\n"
             "The best dates for introverts are ones that allow real conversation in comfortable settings."),
            ("Communicating Your Needs",
             "In relationships, introverts often struggle to communicate their need for alone time without hurting their partner. The key is proactive communication: 'I love spending time with you. I also need alone time to recharge so I can be fully present when we're together.' Frame solitude as something that benefits the relationship, not something that threatens it."),
            ("Finding the Right Partner",
             "The right partner for an introvert is someone who respects your quiet, doesn't try to 'fix' your introversion, and doesn't equate silence with disinterest. They understand that your love is deep even when it's quiet.\n\n"
             "Red flags: partners who constantly say 'You're so quiet,' pressure you to be more social, or dismiss your need for alone time."),
            ("Exercise: Relationship Reflection",
             "If you're in a relationship: Write a letter to your partner explaining what introversion means to you and what you need. If you're single: Write a description of your ideal relationship dynamic, including how much alone time you need, your preferred activities together, and how you express affection."),
        ]
    },
    {
        "title": "Public Speaking for the Quiet Soul",
        "sections": [
            ("Why Introverts Can Be Great Speakers",
             "Counterintuitively, many of the world's best public speakers are introverts. They succeed because they prepare meticulously, connect deeply with their message, and focus on delivering value rather than performing charisma.\n\n"
             "You don't need to be entertaining. You need to be honest, prepared, and clear. Audiences can feel authenticity, and introverts have it in abundance."),
            ("Preparation: Your Superpower",
             "Introverts who prepare thoroughly outperform extroverts who wing it — every time. Your preparation process: (1) Know your material inside out. (2) Practice out loud at least 5 times. (3) Anticipate questions and prepare answers. (4) Arrive early to get comfortable with the space. (5) Have a strong opening line memorized to overcome the initial anxiety spike."),
            ("Managing Stage Fright",
             "Stage fright is universal — introverts just feel it more intensely because of their heightened nervous system sensitivity. Techniques that work: Deep belly breathing for 2 minutes before going on. Power posing (standing wide and tall) in private before your talk. Focusing on ONE friendly face in the audience. Reframing anxiety as excitement ('I'm excited to share this')."),
            ("Exercise: The Two-Minute Talk",
             "Choose a topic you're passionate about. Set a timer for 2 minutes and talk about it out loud, alone. Record yourself (audio only is fine). Listen back. Notice: You know more than you think. Your voice sounds more confident than it felt. Repeat once a week, increasing to 5 minutes, then 10."),
        ]
    },
    {
        "title": "Digital Confidence: Your Online Presence",
        "sections": [
            ("The Internet Is an Introvert's Playground",
             "Online communication levels the playing field for introverts. You can think before you respond, edit your thoughts, and engage on your own schedule. Social media, blogs, and professional platforms let you share ideas without the drain of real-time social interaction.\n\n"
             "Many introverts have built massive influence online — through writing, creating, and connecting in low-pressure digital spaces."),
            ("Building a Professional Online Presence",
             "Your digital presence is your portfolio of confidence. Start with: A complete LinkedIn profile with a professional photo. Sharing or commenting on industry content once a week. Writing occasional posts about your work or interests. Engaging meaningfully with others' content rather than just scrolling.\n\n"
             "Online engagement at YOUR pace is networking that doesn't drain you."),
            ("Setting Digital Boundaries",
             "The internet can be just as overstimulating as a crowded room. Set boundaries: Limit social media to specific times. Turn off non-essential notifications. Curate your feeds to include only content that inspires or educates. Don't feel obligated to respond to every message immediately."),
            ("Exercise: Digital Confidence Audit",
             "Review your online presence on one platform (LinkedIn, Instagram, etc.). Ask: Does my profile represent who I am? Am I sharing my expertise or hiding it? When was the last time I engaged with someone else's content? Set one specific goal for improving your digital presence this month."),
        ]
    },
    {
        "title": "Creativity and Solitude",
        "sections": [
            ("Solitude Is the Birthplace of Creativity",
             "Nearly every major creative breakthrough in history was born in solitude. Einstein, Newton, Darwin, Austen, Woolf — all introverts who did their best work alone. Solitude gives your brain the space to make unexpected connections, process deeply, and produce original ideas.\n\n"
             "If you feel guilty about needing alone time, remember: solitude is not wasted time. It's where your best ideas live."),
            ("Protecting Your Creative Space",
             "In a world that worships collaboration, protecting solitary creative time requires intentionality. Block 'creative hours' on your calendar. Find a physical space where you won't be interrupted. Learn to say: 'I'm in creative mode — can this wait?' Your creativity is a contribution, and it needs protection."),
            ("Sharing Your Creative Work",
             "Many introverts create amazing work but never share it. Fear of judgment keeps brilliance hidden. Start small: share with one trusted friend. Then a small online community. Then publicly. Each share builds confidence muscle.\n\n"
             "Remember: the world needs your perspective. Your quiet voice has something to say that loud voices can't."),
            ("Exercise: Creative Solitude Practice",
             "Schedule 30 minutes of uninterrupted solitude this week. No phone, no internet, no other people. Bring only a blank notebook. Write, draw, think, or just sit. Notice what emerges when your mind has space. Write about the experience afterward."),
        ]
    },
    {
        "title": "Physical Health and Introvert Confidence",
        "sections": [
            ("The Body-Confidence Connection",
             "Physical health directly impacts confidence. Exercise reduces anxiety, improves mood, and creates a sense of accomplishment. For introverts, the right exercise is one that matches your temperament: solo runs, swimming, yoga, weight training, or hiking in nature.\n\n"
             "You don't need a gym buddy or a group fitness class to be healthy. Find movement you enjoy doing alone."),
            ("Sleep: The Introvert's Secret Weapon",
             "Introverts are more sensitive to sleep deprivation because their brains are already working harder to process stimulation. When you're well-rested, social situations feel more manageable, your thinking is sharper, and your emotional regulation improves.\n\n"
             "Protect your sleep like your career depends on it — because it does."),
            ("Nutrition and Social Energy",
             "Blood sugar crashes and dehydration amplify anxiety and social fatigue. Before social events: Eat a balanced meal with protein and complex carbs. Stay hydrated. Avoid excessive caffeine (it increases cortisol, your stress hormone). Limit alcohol (it feels like a social lubricant but actually increases anxiety the next day)."),
            ("Exercise: Introvert Fitness Plan",
             "Design a weekly exercise plan using only activities you can do alone or in very small groups. Include: 3 days of movement (walking, yoga, weights, swimming). 1 day of nature exposure (hiking, park visit). Daily: 8 hours sleep target, 8 glasses of water. Track your energy levels for a week and notice the connection between physical health and social confidence."),
        ]
    },
    {
        "title": "Dealing with Extroverted Expectations",
        "sections": [
            ("When the World Wants You to Be Louder",
             "From school to work to social media, the message is consistent: be more outgoing, more social, more visible. This pressure can make introverts feel broken or inadequate. But the problem isn't you — it's the expectation.\n\n"
             "You are not required to meet extroverted standards to be successful, likeable, or confident. You are required to meet YOUR standards."),
            ("Educating Others About Introversion",
             "Sometimes the best thing you can do is simply explain: 'I'm an introvert. I do my best work in quiet settings. I prefer deep conversations over small talk. I need alone time to recharge. This isn't antisocial — it's how I function best.'\n\n"
             "Most people genuinely don't understand introversion. A brief, confident explanation can transform your relationships and work environment."),
            ("Navigating Extroverted Workplaces and Friend Groups",
             "You'll inevitably work and socialize with extroverts. The key is negotiation, not capitulation. In extroverted workplaces: Advocate for quiet focus time. Suggest asynchronous communication (email/Slack) instead of constant meetings. In extroverted friend groups: Be honest about your limits. Suggest activities that work for both types (dinner parties instead of clubs, hikes instead of concerts)."),
            ("Exercise: The Introvert Advocacy Letter",
             "Write a short letter (you don't have to send it) to the extroverted world, explaining what you need and why. What would you want every extrovert to understand about you? This exercise clarifies your own needs and prepares you to advocate for yourself in real situations."),
        ]
    },
    {
        "title": "Building a Confidence Habit",
        "sections": [
            ("Confidence Is a Practice, Not a Destination",
             "You will never 'arrive' at confidence and stay there forever. Confidence fluctuates — that's normal. What matters is having a daily practice that keeps your confidence foundation strong, even when life shakes it.\n\n"
             "Think of confidence like a muscle. It atrophies without use and grows with consistent practice. The exercises in this book aren't one-time activities — they're ongoing practices."),
            ("The Daily Confidence Routine",
             "Morning (5 minutes): Read your 'I am' statements. Set one confidence intention for the day. Visualize handling one upcoming situation with calm confidence. Evening (5 minutes): Write down one moment you showed up today. Acknowledge one thing you did well. Release one thing that didn't go perfectly — it's done.\n\n"
             "This 10-minute daily practice, done consistently, will transform your relationship with confidence."),
            ("Building Your Support System",
             "Confidence doesn't have to be a solo journey. Find: One person who believes in you unconditionally. One community (online or offline) that accepts introverts. One mentor or coach who can offer guidance. You don't need a crowd. You need a few people who see you clearly and cheer you on."),
            ("Exercise: Your Confidence Commitment",
             "Write a commitment letter to yourself. Include: (1) Your personal definition of confidence (from Chapter 3). (2) Your top 3 confidence strategies from this book. (3) Your daily confidence routine. (4) One big confidence goal for the next 90 days. Sign it. Date it. Keep it where you can see it."),
        ]
    },
]


def draw_chapter(c, chapter_num, chapter):
    """Draw a full chapter with multiple pages."""
    ml = get_margin_left()
    text_w = W - MARGIN_OUTER - MARGIN_INNER

    # Chapter title page
    y = H * 0.55

    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, y + 40, f"Chapter {chapter_num}")

    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.5)
    c.line(W*0.3, y + 30, W*0.7, y + 30)

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HEADER_COLOR)
    # Handle long titles
    title = chapter["title"]
    if len(title) > 28:
        words = title.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        c.drawCentredString(W/2, y, line1)
        c.drawCentredString(W/2, y - 25, line2)
    else:
        c.drawCentredString(W/2, y, title)

    next_page(c)

    # Sections
    y = H - MARGIN_TOP

    for section_title, section_text in chapter["sections"]:
        # Section heading
        if y < MARGIN_BOTTOM + 100:
            next_page(c)
            y = H - MARGIN_TOP

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(ACCENT)
        c.drawString(ml, y, section_title)
        y -= 8
        c.setStrokeColor(ACCENT2)
        c.setLineWidth(0.5)
        c.line(ml, y, ml + 80, y)
        y -= 18

        # Section text - split by paragraphs
        paragraphs = section_text.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            y = draw_text_block(c, para, ml, y, text_w, size=10, leading=14)
            y -= 12

        y -= 10

    next_page(c)


def draw_conclusion(c):
    """Conclusion chapter."""
    ml = get_margin_left()
    text_w = W - MARGIN_OUTER - MARGIN_INNER

    y = H * 0.55
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HEADER_COLOR)
    c.drawCentredString(W/2, y, "Your Introvert Advantage")
    c.setFont("Helvetica", 12)
    c.setFillColor(ACCENT)
    c.drawCentredString(W/2, y - 25, "Conclusion")
    next_page(c)

    y = H - MARGIN_TOP
    paragraphs = [
        "You've made it through 20 chapters of deep work. If you're an introvert, that kind of sustained, focused effort is exactly your strength — and proof that you already have more confidence than you might realize.",

        "Here's what I hope you take away from this book:",

        "Your introversion is not something to overcome. It's something to leverage. The world needs your depth, your thoughtfulness, your ability to listen when everyone else is talking, and your capacity for focused, meaningful work.",

        "Confidence doesn't mean never feeling anxious, uncertain, or out of place. It means feeling those things and showing up anyway — in your own way, at your own pace, on your own terms.",

        "You don't need to be louder. You don't need to be more social. You don't need to pretend to be someone you're not. You need to understand your strengths, manage your energy, and trust that your quiet presence is powerful.",

        "The strategies in this book work, but only if you practice them. Not all at once. Not perfectly. Just consistently. One small confident action per day, compounded over months and years, will transform your life.",

        "You're not broken. You're not behind. You're not less than.",

        "You're an introvert. And that's your advantage.",

        "Go quietly change the world.",
    ]

    for para in paragraphs:
        y = draw_text_block(c, para, ml, y, text_w, size=10, leading=14.5)
        y -= 12

    next_page(c)


def draw_resources(c):
    """Recommended resources page."""
    ml = get_margin_left()
    y = H - MARGIN_TOP

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HEADER_COLOR)
    c.drawCentredString(W/2, y, "Recommended Resources")
    y -= 35

    resources = [
        ("Books", [
            "Quiet by Susan Cain",
            "The Introvert Advantage by Marti Olsen Laney",
            "Introvert Power by Laurie Helgoe",
            "The Highly Sensitive Person by Elaine Aron",
            "Daring Greatly by Brene Brown",
        ]),
        ("Online Communities", [
            "r/introvert (Reddit)",
            "Introvert, Dear (introvertdear.com)",
            "Quiet Revolution (quietrev.com)",
        ]),
        ("Podcasts", [
            "The Introvert's Edge",
            "Quiet and Strong",
            "The Gentle Rebel",
        ]),
        ("Apps for Mental Wellness", [
            "Headspace (meditation)",
            "Calm (sleep and relaxation)",
            "Daylio (mood tracking)",
            "Forest (focus and phone-free time)",
        ]),
    ]

    for category, items in resources:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(ACCENT)
        c.drawString(ml, y, category)
        y -= 18

        c.setFont("Helvetica", 10)
        c.setFillColor(TEXT_COLOR)
        for item in items:
            c.drawString(ml + 15, y, f"- {item}")
            y -= 15
        y -= 12

    next_page(c)


def draw_final_page(c):
    """Thank you page."""
    c.setFillColor(DARK)
    c.rect(MARGIN_OUTER, MARGIN_OUTER, W - 2*MARGIN_OUTER, H - 2*MARGIN_OUTER, fill=1)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W/2, H/2 + 40, "Thank You for Reading")

    c.setFont("Helvetica", 12)
    c.setFillColor(ACCENT2)
    c.drawCentredString(W/2, H/2, "Your quiet strength matters more")
    c.drawCentredString(W/2, H/2 - 18, "than you know.")

    c.setFont("Helvetica", 10)
    c.setFillColor(MUTED)
    c.drawCentredString(W/2, H * 0.2, "If this book helped you, please leave a review on Amazon.")
    c.drawCentredString(W/2, H * 0.17, "Your feedback helps other introverts find this book.")

    next_page(c)


def generate():
    PAGE_NUM[0] = 0

    c = canvas.Canvas(str(PDF_PATH), pagesize=(W, H))
    c.setTitle("Confidence Building for Introverts")
    c.setAuthor("Deokgu Studio")
    c.setSubject("A Practical Guide for Introverts to Build Genuine Confidence")

    # Title page
    draw_title_page(c)

    # Copyright
    draw_copyright_page(c)

    # Table of Contents
    draw_toc(c, CHAPTERS)

    # Introduction
    draw_introduction(c)

    # 20 Chapters
    for i, chapter in enumerate(CHAPTERS):
        draw_chapter(c, i + 1, chapter)

    # Conclusion
    draw_conclusion(c)

    # Resources
    draw_resources(c)

    # Final page
    draw_final_page(c)

    c.save()
    page_count = PAGE_NUM[0]
    file_size = os.path.getsize(PDF_PATH) / 1024
    print(f"PDF generated: {PDF_PATH}")
    print(f"Total pages: {page_count}")
    print(f"File size: {file_size:.0f} KB")


if __name__ == "__main__":
    generate()
