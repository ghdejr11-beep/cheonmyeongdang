"""
📚 AI Side Hustle Blueprint — English KDP Version
Based on Korean original (50 chapters, 4,759 lines)
Restructured for Western market: 20 chapters, actionable, KDP-optimized
6x9 inches (standard KDP non-fiction), ~200 pages
"""
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from pathlib import Path
import os, textwrap

OUTPUT_DIR = Path(__file__).parent
PDF_PATH = OUTPUT_DIR / "AI_Side_Hustle_Blueprint_Interior.pdf"

# 6x9 trim (standard KDP)
W = 6 * inch
H = 9 * inch
M = 0.6 * inch
TW = W - 2*M  # text width

DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#2563EB")
GOLD = HexColor("#D97706")
TEXT = HexColor("#1f2937")
GRAY = HexColor("#6b7280")
LIGHT = HexColor("#f3f4f6")
LINE = HexColor("#e5e7eb")

CHAPTERS = [
    ("Part I: THE FOUNDATION", None, []),
    ("Chapter 1", "Why Your Salary Will Never Be Enough", [
        "Let's do the math nobody wants to do.",
        "Average salary: $4,000/month after tax. Rent: $1,200. Food: $500. Transport: $200. Insurance: $300. Subscriptions: $100. What's left? Maybe $1,500. One car repair or medical bill wipes that out.",
        "At this rate, saving $100,000 takes 5-6 years. And inflation erodes it while you save.",
        "This isn't a motivation speech. It's arithmetic. The system wasn't designed for you to get ahead on salary alone.",
        "THE DIGITAL PRODUCT FORMULA:",
        "| Type | Hourly Rate | Scalability |",
        "| Labor (delivery, driving) | $10-15 | Zero |",
        "| Skill (freelance design) | $30-50 | Low |",
        "| Digital Products | Unlimited | High |",
        "",
        "Digital products are 'build once, sell forever.' An eBook sells its 1,000th copy with zero additional work from you. Add AI, and the creation time drops by 80%.",
        "",
        "THE $5,000/MONTH FORMULA:",
        "A $29 digital product x 172 sales/month = $4,988",
        "That's ~6 sales per day. With 3 products, each needs just 2 sales/day.",
        "Not impossible. Not even hard. Just systematic.",
    ]),
    ("Chapter 2", "The 2026 AI Side Hustle Landscape", [
        "Seven types of digital products that actually sell:",
        "",
        "1. EBOOKS & GUIDES ($9-49): Lowest barrier. Write with AI in days, not months. Best for: niche expertise, how-to content.",
        "2. TEMPLATES (Notion/Excel/Canva) ($5-39): Visual, instantly useful. AI generates formulas, layouts, and variations at scale.",
        "3. PROMPT PACKS ($9-29): Curated ChatGPT/Midjourney prompts. Meta: using AI to sell AI tools.",
        "4. ONLINE MINI-COURSES ($29-199): AI writes scripts, you record with free tools. Loom + Canva + AI = professional course.",
        "5. PRINTABLES & PLANNERS ($5-15): Journals, trackers, coloring books. Low competition in micro-niches.",
        "6. AI CHATBOT TEMPLATES ($49-299): Pre-built Make.com/Zapier workflows. High value, low competition.",
        "7. DESIGN ASSET PACKS ($15-49): Instagram templates, YouTube thumbnails, brand kits.",
        "",
        "KEY INSIGHT: The winners in 2026 aren't selling ONE product. They're building a PORTFOLIO of 5-10 products across 2-3 types, creating a flywheel where each product promotes the others.",
    ]),
    ("Chapter 3", "Claude vs ChatGPT vs Gemini: Choosing Your AI", [
        "You don't need all of them. You need the RIGHT one for each task.",
        "",
        "CLAUDE (Anthropic):",
        "- Best for: Long-form writing, analysis, coding, nuanced content",
        "- Strength: 200K context window, follows complex instructions",
        "- Use when: Writing eBooks, creating detailed guides, building systems",
        "",
        "CHATGPT (OpenAI):",
        "- Best for: Quick tasks, GPTs marketplace, DALL-E images, plugins",
        "- Strength: Ecosystem (GPT Store, plugins, API breadth)",
        "- Use when: Image generation, quick brainstorming, customer-facing chatbots",
        "",
        "GEMINI (Google):",
        "- Best for: Research, data analysis, Google Workspace integration",
        "- Strength: Real-time web access, multimodal understanding",
        "- Use when: Market research, trend analysis, YouTube optimization",
        "",
        "MY RECOMMENDATION: Start with Claude for creation, ChatGPT for images, Gemini for research. As you grow, you'll naturally gravitate toward 1-2 primary tools.",
    ]),
    ("Chapter 4", "The 100-Day Roadmap", [
        "Stop planning forever. Here's your timeline:",
        "",
        "DAYS 1-30: BUILD",
        "- Week 1: Choose your niche (Chapter 5 method)",
        "- Week 2: Create Product #1 (eBook or template)",
        "- Week 3: Create Product #2",
        "- Week 4: Set up sales platform + payment",
        "",
        "DAYS 31-60: LAUNCH",
        "- Week 5-6: Build one marketing channel (Instagram OR blog OR YouTube)",
        "- Week 7: Get first 10 sales (even if friends/family)",
        "- Week 8: Collect reviews + iterate based on feedback",
        "",
        "DAYS 61-100: SCALE",
        "- Week 9-10: Add second marketing channel",
        "- Week 11: Create Product #3 (bundle or premium)",
        "- Week 12-14: Automate: email sequences, social posting, customer support",
        "",
        "THE RULE: 2 hours per day. No more. Consistency beats intensity.",
        "Track everything in a simple spreadsheet: hours worked, products created, sales, revenue.",
    ]),
    ("Part II: CREATING PRODUCTS", None, []),
    ("Chapter 5", "Finding Profitable Niches: The 3-Point Method", [
        "Most people fail because they pick the wrong niche. Use this framework:",
        "",
        "POINT 1 — SEARCH VOLUME: Are people actively looking for this?",
        "Tools: Google Trends, Ubersuggest (free), Amazon search suggestions",
        "Target: 1,000-10,000 monthly searches (enough demand, not too competitive)",
        "",
        "POINT 2 — COMPETITION LEVEL: Can you actually rank/get seen?",
        "Check: Amazon KDP top 10 for your keyword. If they have <100 reviews, you can compete.",
        "Check: Instagram hashtag volume. If <500K posts, there's room.",
        "",
        "POINT 3 — WILLINGNESS TO PAY: Will they actually buy?",
        "Signal: Existing products selling at $10+",
        "Signal: Active communities (Reddit, Facebook groups) discussing the problem",
        "Signal: People already spending money on solutions (courses, coaching, tools)",
        "",
        "SWEET SPOT: All three points score 7+/10. Example niches that work:",
        "- ADHD productivity tools for adults",
        "- AI prompt engineering for marketers",
        "- Sleep improvement journals",
        "- Budget planners for couples",
        "- Meal prep templates for busy parents",
    ]),
    ("Chapter 6", "Writing an eBook in 1 Day with AI", [
        "Yes, one day. Here's the exact process:",
        "",
        "HOUR 1-2: OUTLINE",
        "Prompt Claude: 'Create a detailed outline for a [niche] eBook. Target audience: [who]. Length: 15,000-20,000 words. Include chapter titles, 3-5 bullet points per chapter, and a compelling hook for each.'",
        "",
        "HOUR 3-6: DRAFT",
        "Feed Claude each chapter outline one by one:",
        "'Write Chapter 3 based on this outline: [paste]. Tone: conversational, practical. Include 2 real examples, 1 actionable exercise, and 1 key takeaway box.'",
        "",
        "HOUR 7-8: EDIT & POLISH",
        "- Read through once (out loud if possible)",
        "- Ask Claude to 'improve clarity and flow' for weak sections",
        "- Add personal anecdotes or case studies (AI can't fake these)",
        "- Format: headers, bullet points, callout boxes",
        "",
        "HOUR 9-10: DESIGN",
        "- Cover: Canva (free) + AI-generated imagery",
        "- Interior: Clean, simple formatting. No fancy layouts needed.",
        "- Export as PDF (for Gumroad) or EPUB (for KDP)",
        "",
        "CRITICAL: AI writes the first draft. YOU add the soul. The difference between a $5 eBook and a $29 eBook is your unique perspective, real examples, and genuine advice that only comes from experience.",
    ]),
    ("Chapter 7", "Templates That Sell: Notion, Excel, Canva", [
        "Templates are the easiest digital product to create and the hardest to get wrong.",
        "",
        "NOTION TEMPLATES ($5-29):",
        "- AI generates the structure: 'Create a Notion template for [use case] with these sections...'",
        "- Add visual appeal: icons, covers, color coding",
        "- Include a video walkthrough (5 min, Loom, free)",
        "- Package: Template + Setup Guide PDF + Video Tutorial",
        "",
        "EXCEL/GOOGLE SHEETS ($9-39):",
        "- AI writes ALL the formulas: 'Create an Excel budget tracker with automatic category totals, monthly comparison, and visual charts'",
        "- Test thoroughly (broken formulas = instant refund)",
        "- Include: Instructions tab, Example data, Clean design",
        "",
        "CANVA TEMPLATES ($15-49):",
        "- Instagram post templates (30-pack): same style, different layouts",
        "- YouTube thumbnail templates (20-pack)",
        "- Brand kit templates",
        "- AI helps with copy; you arrange in Canva",
        "",
        "PRO TIP: Bundle 3 related templates for 2x the price of one. 'The Complete Content Creator Bundle' > individual template.",
    ]),
    ("Chapter 8", "Prompt Packs & AI Tool Products", [
        "Selling prompts is the most meta side hustle of 2026. And it works.",
        "",
        "WHAT SELLS:",
        "- ChatGPT prompt packs for specific professions (realtors, teachers, marketers)",
        "- Midjourney/DALL-E prompt libraries with example outputs",
        "- 'Copy-paste' business prompts (emails, proposals, social posts)",
        "- System prompts for building custom GPTs",
        "",
        "HOW TO CREATE:",
        "1. Pick a niche audience (e.g., 'Real Estate Agents')",
        "2. List 50 tasks they do daily",
        "3. Write optimized prompts for each task",
        "4. Test every single prompt. Screenshot the outputs.",
        "5. Package: PDF guide + prompt library + example outputs",
        "",
        "PRICING: $9-29 for basic packs, $49-99 for comprehensive collections with video tutorials.",
        "",
        "The key: specificity. 'AI Prompts for Everyone' = $0 sales. 'AI Prompts for Etsy Sellers to Write Product Descriptions' = money.",
    ]),
    ("Part III: SELLING & MARKETING", None, []),
    ("Chapter 9", "Choosing Your Sales Platform", [
        "Where you sell matters almost as much as what you sell.",
        "",
        "GUMROAD: Best for beginners. 10% fee but zero setup friction. Good for eBooks, templates, digital downloads. Global payments built in.",
        "",
        "AMAZON KDP: Best for eBooks and print books. Massive built-in audience. 30-65% royalty depending on pricing. You can't sell templates here.",
        "",
        "ETSY: Best for templates and printables. Huge buyer audience looking for exactly these products. $0.20 listing + 6.5% fee.",
        "",
        "YOUR OWN WEBSITE (Shopify/WooCommerce): Best for bundles and premium products. Full control, lowest fees long-term, but you drive ALL the traffic.",
        "",
        "MY RECOMMENDATION FOR BEGINNERS:",
        "Month 1: Gumroad (fastest to launch)",
        "Month 2: Add Amazon KDP (for eBooks)",
        "Month 3: Add Etsy (for templates)",
        "Month 6+: Consider your own site",
        "",
        "Don't overthink this. Pick one. Launch. You can always add more later.",
    ]),
    ("Chapter 10", "Instagram: 0 to 1,000 Followers in 30 Days", [
        "Instagram is the fastest free traffic source for digital products in 2026.",
        "",
        "THE 30-DAY PLAN:",
        "Days 1-7: Foundation",
        "- Niche-specific handle and bio",
        "- 9 initial posts (3x3 grid aesthetic)",
        "- Bio link to your Gumroad/product page",
        "",
        "Days 8-21: Content Machine",
        "- Post 1 Reel per day (15-30 seconds, trending audio)",
        "- AI writes all captions and hooks",
        "- Content formula: 40% value/tips, 30% behind-the-scenes, 20% product showcases, 10% personal stories",
        "",
        "Days 22-30: Engagement Sprint",
        "- Comment on 30 accounts in your niche daily (genuine comments, not spam)",
        "- Collaborate with 2-3 similar-sized accounts",
        "- Run one giveaway (your product as the prize)",
        "",
        "REEL FORMULA THAT WORKS:",
        "Hook (0-1s): 'Stop doing [common mistake]'",
        "Value (1-10s): The actual tip/insight",
        "CTA (10-15s): 'Link in bio for the full [product]'",
        "",
        "AI does: captions, hashtags, content ideas, scheduling",
        "You do: record yourself talking for 15 seconds (even just hands + voiceover)",
    ]),
    ("Chapter 11", "SEO Blog: AI-Written Articles That Rank", [
        "Blogging isn't dead. It's just automated now.",
        "",
        "THE SYSTEM: 3 articles per week, AI-assisted, targeting long-tail keywords.",
        "",
        "STEP 1: Find keywords",
        "Use Ubersuggest or Google 'People Also Ask'. Target keywords with 500-5,000 monthly searches and low competition.",
        "",
        "STEP 2: AI writes the draft",
        "'Write a 2,000-word blog post targeting the keyword [X]. Include an intro hook, H2 subheadings with the keyword, 3 actionable tips, internal linking suggestions, and a CTA for my [product].'",
        "",
        "STEP 3: You add value",
        "- Personal experience/case study (1-2 paragraphs)",
        "- Original screenshots or images",
        "- Internal links to your other content and products",
        "",
        "STEP 4: Publish consistently",
        "WordPress + free theme. Or Medium (built-in audience).",
        "",
        "RESULTS TIMELINE: Months 1-2: crickets. Month 3: trickle. Month 6: steady traffic. Month 12: passive income from SEO alone.",
        "The key is NOT quitting in month 2.",
    ]),
    ("Chapter 12", "Email Marketing: Your Most Valuable Asset", [
        "Social media followers aren't yours. Email subscribers are.",
        "",
        "THE SETUP (1 hour):",
        "1. Sign up for free email tool (MailerLite or ConvertKit free plan)",
        "2. Create a lead magnet: free mini-version of your product",
        "3. Set up a landing page (built into the email tool)",
        "4. Add signup form to your blog/Instagram bio",
        "",
        "THE 7-DAY SALES SEQUENCE (AI writes all of these):",
        "Day 1: Welcome + deliver lead magnet + your story",
        "Day 2: The problem your product solves (pain points)",
        "Day 3: Case study or social proof",
        "Day 4: How your product works (features → benefits)",
        "Day 5: FAQ + objection handling",
        "Day 6: Limited-time offer or bonus",
        "Day 7: Final call + scarcity",
        "",
        "ONGOING: Weekly newsletter with value + soft product mention.",
        "",
        "MATH: 1,000 email subscribers × 2% conversion × $29 product = $580 per email campaign. Send one campaign per month = $580/month from email alone.",
    ]),
    ("Part IV: AUTOMATION & SCALING", None, []),
    ("Chapter 13", "Automate Everything: Make.com & Zapier", [
        "The goal: customer pays → product delivered → thank you email → review request. All without you touching anything.",
        "",
        "AUTOMATION STACK (free/cheap):",
        "- Gumroad/Etsy: auto-delivers product on purchase",
        "- Make.com (free tier): connects everything else",
        "- Email tool: sends automated sequences",
        "",
        "AUTOMATIONS TO SET UP:",
        "1. New sale → Slack/Telegram notification",
        "2. New sale → Add to email list",
        "3. 7 days after purchase → Automated review request email",
        "4. New blog post → Auto-share to social media",
        "5. Monthly → Revenue report to your inbox",
        "",
        "TIME SAVED: ~10 hours/week of manual work → 0. This is how you stay at 2 hours/day.",
    ]),
    ("Chapter 14", "Scaling to $10,000/Month", [
        "You hit $5,000/month. Now what?",
        "",
        "LEVEL 1: MORE PRODUCTS (same niche)",
        "- Your first product proved the niche works",
        "- Create variations: beginner/advanced/specific audience",
        "- Bundle existing products at premium price",
        "",
        "LEVEL 2: MORE CHANNELS",
        "- You proved Instagram works → Add YouTube Shorts (same content, repurposed)",
        "- Blog bringing traffic → Add Pinterest (same content, visual format)",
        "- Email converting → Add webinars (higher ticket)",
        "",
        "LEVEL 3: HIGHER PRICES",
        "- Add a premium tier ($99-299): includes video course + community access",
        "- 1-on-1 consulting calls ($100-300/hour): use as upsell",
        "- Group coaching program ($499-999): scale your expertise",
        "",
        "LEVEL 4: OUTSOURCE",
        "- Hire a VA for customer support ($500/month)",
        "- Hire a designer for product improvements ($300-500/project)",
        "- Keep strategy and content creation for yourself",
        "",
        "THE $10K FORMULA: 3 products × 3 channels × premium pricing = exponential growth, not linear.",
    ]),
    ("Chapter 15", "Legal Basics: Business Registration & Taxes", [
        "Don't skip this chapter. It's boring but essential.",
        "",
        "WHEN TO REGISTER A BUSINESS:",
        "- Immediately if you're in the US (LLC protects personal assets)",
        "- When you hit consistent $500+/month income",
        "- Before accepting business-to-business payments",
        "",
        "TAX BASICS FOR SIDE HUSTLERS:",
        "- All income is taxable (yes, even digital products)",
        "- Set aside 25-30% of revenue for taxes",
        "- Track ALL expenses (software, tools, courses = deductions)",
        "- Use accounting software: Wave (free) or QuickBooks",
        "",
        "AI-GENERATED CONTENT & COPYRIGHT:",
        "- In 2026, AI-assisted works are generally copyrightable if you provide substantial creative input",
        "- Pure AI output with no human direction: copyright is uncertain",
        "- Best practice: always add your own analysis, examples, and structure",
        "- Never copy someone else's prompts or outputs verbatim",
        "",
        "DISCLAIMER: This is educational information, not legal advice. Consult a tax professional for your specific situation.",
    ]),
    ("Part V: THE SYSTEM", None, []),
    ("Chapter 16", "The Daily 2-Hour Workflow", [
        "Here's exactly what your 2 hours look like:",
        "",
        "MINUTE 0-15: CHECK & RESPOND",
        "- Check sales notifications",
        "- Reply to customer messages (or confirm auto-replies handled it)",
        "- Check analytics: what's working?",
        "",
        "MINUTE 15-75: CREATE (THE BIG BLOCK)",
        "- Monday/Wednesday: Create new content (eBook chapters, templates)",
        "- Tuesday/Thursday: Marketing content (Reels, blog posts, emails)",
        "- Friday: Product improvement based on customer feedback",
        "- Weekend: Optional — batch-create next week's social content",
        "",
        "MINUTE 75-105: PUBLISH & SCHEDULE",
        "- Post today's content",
        "- Schedule tomorrow's content",
        "- Update product listings if needed",
        "",
        "MINUTE 105-120: LEARN & PLAN",
        "- 15 minutes of learning (one article, one video, one idea)",
        "- Write tomorrow's task list (3 items max)",
        "",
        "THE RULE: When your 2 hours are up, STOP. Close the laptop. The system works because it's sustainable. Burnout is the real enemy, not lack of hustle.",
    ]),
    ("Chapter 17", "Month-by-Month Milestones", [
        "WHERE YOU SHOULD BE (roughly):",
        "",
        "MONTH 1: $0-100",
        "- 2 products launched",
        "- 1 marketing channel active",
        "- First sale (even if it's $5)",
        "- Learning, iterating, not quitting",
        "",
        "MONTH 2: $100-500",
        "- 3 products live",
        "- 100+ social followers",
        "- Email list started (even 20 subscribers)",
        "- First organic sale (not friends/family)",
        "",
        "MONTH 3: $500-1,500",
        "- Automations running",
        "- Second marketing channel added",
        "- First customer review/testimonial",
        "- Starting to see patterns in what sells",
        "",
        "MONTH 6: $1,500-3,000",
        "- Product portfolio of 5+",
        "- 1,000+ social followers",
        "- 500+ email subscribers",
        "- Consistent daily sales",
        "",
        "MONTH 12: $3,000-5,000+",
        "- Multiple income streams",
        "- Systems running semi-autonomously",
        "- Considering quitting day job (or not — that's okay too)",
        "",
        "NOTE: These are averages. Some people hit $5K in month 3. Others take 18 months. Both are fine. The only failure is quitting.",
    ]),
    ("Chapter 18", "Common Mistakes & How to Avoid Them", [
        "I've made all of these. Learn from my pain:",
        "",
        "MISTAKE 1: Perfection Paralysis",
        "Fix: Launch at 80% quality. Iterate based on real feedback.",
        "",
        "MISTAKE 2: Too Many Products Too Fast",
        "Fix: 1 product → prove it sells → then expand.",
        "",
        "MISTAKE 3: Ignoring Marketing",
        "Fix: 50% creation, 50% marketing. Creating without marketing = invisible.",
        "",
        "MISTAKE 4: Copying Successful Products Exactly",
        "Fix: Be inspired, don't clone. Add YOUR unique angle.",
        "",
        "MISTAKE 5: Not Building an Email List",
        "Fix: Start collecting emails from day 1. It's your safety net when algorithms change.",
        "",
        "MISTAKE 6: Relying 100% on AI Without Editing",
        "Fix: AI writes the draft. You add the expertise, stories, and quality control.",
        "",
        "MISTAKE 7: Comparing Your Month 1 to Someone's Month 36",
        "Fix: Track YOUR progress. $50 in month 1 is incredible if it was $0 last month.",
        "",
        "MISTAKE 8: Working More Than 2 Hours/Day",
        "Fix: The system is designed for 2 hours. More hours ≠ more results. Better systems = more results.",
    ]),
    ("Chapter 19", "Your First Week Action Plan", [
        "Stop reading after this chapter and DO these things:",
        "",
        "DAY 1 (30 min):",
        "☐ Pick your niche using the 3-Point Method (Chapter 5)",
        "☐ Write down your target customer in one sentence",
        "",
        "DAY 2 (2 hours):",
        "☐ Create outline for Product #1 using AI",
        "☐ Write first 3 chapters/sections",
        "",
        "DAY 3 (2 hours):",
        "☐ Finish Product #1 draft",
        "☐ Ask AI to review and improve it",
        "",
        "DAY 4 (2 hours):",
        "☐ Design cover (Canva, 30 min)",
        "☐ Format and export (PDF/EPUB)",
        "☐ Sign up for Gumroad",
        "",
        "DAY 5 (1 hour):",
        "☐ Upload product to Gumroad",
        "☐ Write product description (AI-assisted)",
        "☐ Set price",
        "",
        "DAY 6 (1 hour):",
        "☐ Create Instagram account (if needed)",
        "☐ Post 3 initial posts about your niche",
        "☐ Add Gumroad link to bio",
        "",
        "DAY 7 (30 min):",
        "☐ Share your product with 10 people you know",
        "☐ Reflect: What went well? What was hard?",
        "☐ Plan next week",
        "",
        "That's it. In 7 days, you'll have a live product for sale on the internet. Most people never get this far. You're already ahead.",
    ]),
    ("Chapter 20", "100 Days From Now", [
        "Close your eyes for a moment.",
        "",
        "Imagine it's 100 days from now. You wake up, check your phone, and see:",
        "",
        "  '3 new sales overnight — $87 while you slept.'",
        "",
        "You open your dashboard. This month's revenue: $2,340. Not $5,000 yet, but growing. Last month was $1,800. The month before, $900.",
        "",
        "Your email list has 800 subscribers. Your Instagram just crossed 2,000 followers. Someone left a 5-star review saying your eBook changed how they work.",
        "",
        "You still have your day job. But for the first time, it feels like a choice — not a cage.",
        "",
        "This isn't fantasy. This is what happens when you show up for 2 hours a day, 100 days in a row, with the right system.",
        "",
        "The tools are free. The knowledge is in this book. The AI is ready.",
        "",
        "The only variable is you.",
        "",
        "Your 100 days start now.",
        "",
        "— Deokhun Hong",
        "Founder, Deokgu Studio",
    ]),
]


def wrap_text(c, text, x, y, width, font="Helvetica", size=10, leading=14, color=TEXT):
    """Word-wrap text and draw, return new y position."""
    c.setFont(font, size)
    c.setFillColor(color)
    chars_per_line = int(width / (size * 0.5))
    lines = textwrap.wrap(text, width=chars_per_line) if text.strip() else [""]
    for line in lines:
        if y < M + 20:
            c.showPage()
            y = H - M
            c.setFont(font, size)
            c.setFillColor(color)
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_title_page(c):
    c.setFillColor(DARK)
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)

    cx = W/2
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(cx, H*0.78, "THE 100-DAY SYSTEM")

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(cx, H*0.68, "AI SIDE HUSTLE")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(cx, H*0.62, "BLUEPRINT")

    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(cx-60, H*0.59, cx+60, H*0.59)

    c.setFont("Helvetica", 12)
    c.setFillColor(GOLD)
    c.drawCentredString(cx, H*0.52, "Build $5,000/Month in Digital Products")
    c.drawCentredString(cx, H*0.48, "with Claude & ChatGPT")

    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#999999"))
    c.drawCentredString(cx, H*0.38, "No coding. No expertise. No excuses.")
    c.drawCentredString(cx, H*0.34, "Just 2 hours a day for 100 days.")

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor("#cccccc"))
    c.drawCentredString(cx, H*0.15, "DEOKHUN HONG")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#888888"))
    c.drawCentredString(cx, H*0.11, "Deokgu Studio")
    c.showPage()


def draw_toc(c):
    y = H - M
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(DARK)
    c.drawString(M, y, "Table of Contents")
    y -= 30

    ch_num = 0
    for title, subtitle, _ in CHAPTERS:
        if subtitle is None:  # Part header
            y -= 10
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(ACCENT)
            c.drawString(M, y, title)
            y -= 18
        else:
            ch_num += 1
            c.setFont("Helvetica", 10)
            c.setFillColor(TEXT)
            c.drawString(M + 15, y, f"{ch_num}. {subtitle}")
            y -= 15
        if y < M + 30:
            c.showPage()
            y = H - M
    c.showPage()


def generate():
    c = canvas.Canvas(str(PDF_PATH), pagesize=(W, H))
    c.setTitle("AI Side Hustle Blueprint")
    c.setAuthor("Deokhun Hong / Deokgu Studio")

    draw_title_page(c)

    # Copyright page
    y = H - M
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(M, y, "AI Side Hustle Blueprint")
    c.drawString(M, y-14, "Copyright 2026 Deokhun Hong / Deokgu Studio")
    c.drawString(M, y-28, "All rights reserved.")
    c.drawString(M, y-56, "No part of this book may be reproduced without permission.")
    c.drawString(M, y-84, "This book is for educational purposes only.")
    c.drawString(M, y-98, "Results vary. No income is guaranteed.")
    c.showPage()

    draw_toc(c)

    # Chapters
    for title, subtitle, paragraphs in CHAPTERS:
        if subtitle is None:
            # Part divider page
            c.setFillColor(DARK)
            c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
            c.setFillColor(ACCENT)
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(W/2, H/2+10, title)
            c.setStrokeColor(GOLD)
            c.setLineWidth(1)
            c.line(W/2-40, H/2-5, W/2+40, H/2-5)
            c.showPage()
            continue

        # Chapter title page
        y = H - M
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(M, y, title.upper())
        y -= 8
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 18)

        # Word wrap title
        if len(subtitle) > 40:
            words = subtitle.split()
            line1 = ""
            line2 = ""
            for w in words:
                if len(line1) < 35:
                    line1 += (" " + w if line1 else w)
                else:
                    line2 += (" " + w if line2 else w)
            c.drawString(M, y, line1)
            if line2:
                y -= 22
                c.drawString(M, y, line2)
        else:
            c.drawString(M, y, subtitle)

        y -= 10
        c.setStrokeColor(ACCENT)
        c.setLineWidth(2)
        c.line(M, y, M + 50, y)
        y -= 25

        # Chapter content
        for para in paragraphs:
            if not para.strip():
                y -= 8
                continue
            if para.startswith("|"):
                # Table-like row
                y = wrap_text(c, para, M, y, TW, "Courier", 8.5, 13, GRAY)
            elif para.startswith("☐"):
                y = wrap_text(c, para, M, y, TW, "Helvetica", 9.5, 14, TEXT)
            elif para.isupper() or para.endswith(":"):
                y -= 5
                y = wrap_text(c, para, M, y, TW, "Helvetica-Bold", 10.5, 15, DARK)
            elif para.startswith("-") or para.startswith("•"):
                y = wrap_text(c, para, M + 10, y, TW - 10, "Helvetica", 9.5, 13, TEXT)
            elif para.startswith(">") or para.startswith("  "):
                y = wrap_text(c, para.lstrip("> "), M + 15, y, TW - 30, "Helvetica-Oblique", 10, 14, GRAY)
            else:
                y = wrap_text(c, para, M, y, TW, "Helvetica", 10, 14, TEXT)
            y -= 4

        c.showPage()

    # Final page
    c.setFillColor(DARK)
    c.rect(M+5, M+5, W - 2*M-10, H - 2*M-10, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W/2, H/2+30, "Thank You for Reading")
    c.setFont("Helvetica", 11)
    c.setFillColor(GOLD)
    c.drawCentredString(W/2, H/2-10, "If this book helped you,")
    c.drawCentredString(W/2, H/2-28, "please leave a review on Amazon.")
    c.setFillColor(HexColor("#888888"))
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H/2-60, "Connect: deokgu.studio")
    c.showPage()

    c.save()
    print(f"PDF: {PDF_PATH}")
    print(f"Pages: {c.getPageNumber()-1}")
    print(f"Size: {os.path.getsize(PDF_PATH)/1024:.0f} KB")

if __name__ == "__main__":
    generate()
