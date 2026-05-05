"""Generate 50 cold-email drafts for Saju Engine B2B sales (one-shot, idempotent)."""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cold_emails_2026_05_05.json')

sectors = {
    'A': {
        'name': 'Korean OTA / Travel',
        'count': 10,
        'titles': ['Head of Product', 'CTO', 'VP Engineering', 'Growth Lead', 'Partnerships Director'],
    },
    'B': {
        'name': 'Korean Game / Entertainment',
        'count': 10,
        'titles': ['Product Manager', 'Live Ops Lead', 'Director of Content', 'Head of Studio', 'CEO'],
    },
    'C': {
        'name': 'Matching / Dating App',
        'count': 10,
        'titles': ['Founder', 'CEO', 'Head of Product', 'Growth Lead', 'Head of Engineering'],
    },
    'D': {
        'name': 'Global Astrology / Wellness App',
        'count': 10,
        'titles': ['Founder', 'CEO', 'Head of Content', 'Product Lead', 'CTO'],
    },
    'E': {
        'name': 'Department Store / Retail',
        'count': 10,
        'titles': ['CMO', 'Head of Digital Marketing', 'Loyalty Lead', 'CRM Manager', 'Head of Personalization'],
    },
}

subjects_by_pattern = {
    'curiosity': {
        'A': 'Quick question about Saju + Korean travel personalization',
        'B': 'A question about your daily-mission engagement loop',
        'C': 'Could a Korean compatibility layer lift D7 retention?',
        'D': 'Curious — have you looked at Korean Saju as a module?',
        'E': '"Lucky shopping day" — already tested in Korean retail',
    },
    'direct_value': {
        'A': 'Saju-driven Korean travel itineraries — white-label API',
        'B': 'Korean Saju engine for daily missions — API in 1 day',
        'C': 'Korean Saju compatibility — white-label API for {COMPANY_NAME}',
        'D': 'Korean Saju add-on for {COMPANY_NAME} — white-label API',
        'E': 'Lucky-day Saju marketing API — white-label license',
    },
    'question': {
        'A': 'How are you handling Korean culture personalization at {COMPANY_NAME}?',
        'B': 'Have you tested Saju-based daily missions yet?',
        'C': 'Are K-wave fans on {COMPANY_NAME} asking for Korean astrology?',
        'D': 'Is a Korean Saju module on the {COMPANY_NAME} roadmap?',
        'E': 'Are you running Saju-based loyalty campaigns yet?',
    },
    'case_study': {
        'A': 'Posteller raised KRW 85B — your travel angle on the same wave',
        'B': 'Posteller series B + IdolSaju traction — game implications',
        'C': 'Why Korean Saju matching converts higher than Western zodiac',
        'D': 'Posteller KRW 85B series B — the gap in your Astrology category',
        'E': 'Posteller proved retail Saju tie-ins — your loyalty angle',
    },
    'mutual': {
        'A': 'From a Korean indie operator — Saju Engine for {COMPANY_NAME}',
        'B': 'Korean indie dev to Korean game / entertainment leader',
        'C': 'Indie Korean engineer to {COMPANY_NAME} product team',
        'D': 'Korean Saju operator to astrology product builder',
        'E': 'Korean operator to {COMPANY_NAME} marketing team',
    },
}

bodies = {
    'A': """Hi {RECIPIENT_NAME},

I run Cheonmyeongdang, a Korean Saju (Four Pillars astrology) production app, and the engine is now wrapped into a clean REST API. 350+ classical Korean Myeongri rules + Claude Sonnet 4.6 advice layer, English-first response.

For {COMPANY_NAME}, the angle is straightforward: "Korean travel itinerary by Saju." Lucky direction maps to a recommended region. Day-stem element suggests the activity (water-stem traveler -> coastal Busan / Sokcho; fire-stem -> Jeonju gastronomy). Inbound Korean travel is increasingly K-wave driven and Western astrology has no Korean lens for it.

API is live: POST /saju/reading. Three-second response. White-label or revenue-share — your call.

Open to a 30-minute demo this week? I will run a sample reading on a chart of your choosing.

cheonmyeongdang.vercel.app

— Deokhun Hong, KunStudio""",
    'B': """Hi {RECIPIENT_NAME},

Quick context — I operate Cheonmyeongdang, a production Korean Saju app, and I have packaged the engine as a REST API. 350+ classical rules + Claude Sonnet 4.6 prose layer.

For {COMPANY_NAME}, two clean integrations:
1. Daily fortune mission — log-in reward gated by today's Saju luck (sticky D7 retention)
2. Character / fan compatibility — match users (or in-game characters) by Four-Pillar synastry

Posteller closed a KRW 85 billion Series B last year and IdolSaju has shown that Korean entertainment audiences will pay for Saju compatibility content. The play exists; nobody has shipped it as a polished engine layer yet.

API is live, OpenAPI spec ready, integration in 1 day. White-label tier $1,999 / month.

Worth a 30-minute demo? I will read a sample chart live.

— Deokhun Hong, KunStudio · cheonmyeongdang.vercel.app""",
    'C': """Hi {RECIPIENT_NAME},

I run a Korean Saju production app (Cheonmyeongdang) and the engine is now exposed as a clean API. 350+ Myeongri rules + Claude Sonnet 4.6 English prose.

For {COMPANY_NAME}, the use case is compatibility scoring: Four-Pillar synastry produces a far richer compatibility signal than sun-sign matching. Global K-pop and K-drama audiences already engage with Saju content; bolting Saju into your match flow is a defensible differentiation against generic-zodiac competitors.

We respond in under 3 seconds. White-label license $1,999 / month or revenue share — 30 percent of Saju-feature attributable revenue.

15 minutes to walk through a sample synastry response? I can pre-run two demo charts.

— Deokhun Hong, KunStudio · cheonmyeongdang.vercel.app""",
    'D': """Hi {RECIPIENT_NAME},

Cheonmyeongdang is a production Korean Saju app, and the engine is now an API. 350+ classical Myeongri rules + Claude Sonnet 4.6 English advice layer.

For {COMPANY_NAME}, the value is positioning: every major astrology app has Western zodiac and most have Vedic. Almost none have a polished Korean Saju module — yet K-wave audiences are now a core demographic. Posteller raised KRW 85 billion on a Korean-native astrology thesis. The Western-app gap is the wedge.

White-label add-on: $4,999 / month Enterprise tier, drop-in REST endpoint, your branding on the UI. We never touch your users.

Worth a 30-minute demo? I will run a real sample chart against your existing zodiac flow.

— Deokhun Hong, KunStudio · cheonmyeongdang.vercel.app""",
    'E': """Hi {RECIPIENT_NAME},

I run Cheonmyeongdang (Korean Saju app) and have packaged the engine as a REST API. 350+ classical rules + Claude Sonnet 4.6 prose, English / Korean dual output.

For {COMPANY_NAME}, the angle is loyalty marketing: "your lucky shopping day" personalized push, lucky-color of the day -> outfit / cosmetic recommendation, seasonal Saju campaign for Lunar New Year and Chuseok. Posteller has already validated retail tie-ins as a viable category — push CTR uplift is meaningful when content is personalized to the recipient's chart.

White-label deployment. Your CRM keeps user data; our engine does the chart math. $4,999 / month Enterprise tier.

15-minute demo this week? I can pre-build a sample lucky-day push for your platform.

— Deokhun Hong, KunStudio · cheonmyeongdang.vercel.app""",
}

# Priority distribution per sector: 3 high, 4 medium, 3 low
priority_dist = ['높음', '높음', '높음', '중간', '중간', '중간', '중간', '낮음', '낮음', '낮음']
patterns = ['curiosity', 'direct_value', 'question', 'case_study', 'mutual']

emails = []
for sector_key, info in sectors.items():
    titles = info['titles']
    for i in range(info['count']):
        pattern = patterns[i % 5]
        title = titles[i % len(titles)]
        priority = priority_dist[i]
        subject = subjects_by_pattern[pattern][sector_key]
        body = bodies[sector_key]
        emails.append({
            'idx': len(emails) + 1,
            'sector': sector_key,
            'sector_name': info['name'],
            'recipient_title': title,
            'recipient_name_placeholder': '{RECIPIENT_NAME}',
            'recipient_email_placeholder': '{RECIPIENT_EMAIL}',
            'company_placeholder': '{COMPANY_NAME}',
            'subject_pattern': pattern,
            'subject': subject,
            'body': body,
            'priority': priority,
        })

out = {
    'generated_at': '2026-05-05',
    'sender': {
        'name': 'Deokhun Hong',
        'company': 'KunStudio',
        'email': 'ghdejr11@gmail.com',
        'product': 'Cheonmyeongdang Saju Engine API',
        'demo_url': 'https://cheonmyeongdang.vercel.app',
    },
    'distribution': {
        'A_korean_ota': 10,
        'B_korean_game_entertainment': 10,
        'C_matching_dating': 10,
        'D_global_astrology': 10,
        'E_retail_department_store': 10,
        'priority_high': sum(1 for e in emails if e['priority'] == '높음'),
        'priority_medium': sum(1 for e in emails if e['priority'] == '중간'),
        'priority_low': sum(1 for e in emails if e['priority'] == '낮음'),
    },
    'send_plan': '10 emails per day x 5 days, spam-safe pacing',
    'placeholders_to_fill': ['{COMPANY_NAME}', '{RECIPIENT_NAME}', '{RECIPIENT_EMAIL}'],
    'subject_patterns_used': patterns,
    'emails': emails,
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('Generated {} emails -> {}'.format(len(emails), OUT))
print('Sectors: A={} B={} C={} D={} E={}'.format(
    sum(1 for e in emails if e['sector'] == 'A'),
    sum(1 for e in emails if e['sector'] == 'B'),
    sum(1 for e in emails if e['sector'] == 'C'),
    sum(1 for e in emails if e['sector'] == 'D'),
    sum(1 for e in emails if e['sector'] == 'E'),
))
print('Priorities: high={} med={} low={}'.format(
    sum(1 for e in emails if e['priority'] == '높음'),
    sum(1 for e in emails if e['priority'] == '중간'),
    sum(1 for e in emails if e['priority'] == '낮음'),
))
