"""
bulk_write_descriptions.py
==========================
Fills the `description` field in each book's manifest.json under
`departments/ebook/projects/<book_id>/manifest.json` with a KDP-ready
plain-text description (1500-2500 chars target, 4000 char hard limit).

Run from anywhere:
    python bulk_write_descriptions.py

Behavior:
- Skips books whose description does NOT contain the "[TODO" sentinel
  (i.e. already filled in).
- Removes "description" from the `todo` array on success.
- Prints a summary table at the end.

Per-book copy is written below as DESCRIPTIONS dict (keyed by book_id).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECTS_DIR = Path(__file__).resolve().parent / "projects"

# ---------------------------------------------------------------------------
# Descriptions - KDP-ready plain text
# ---------------------------------------------------------------------------
# Style rules:
#  * Hook -> Target reader -> What's inside (bullets via "-") -> Use cases -> CTA
#  * Plain text only (no HTML, no markdown headers - KDP renders raw text)
#  * 1500-2500 chars sweet spot; never above 4000
#  * SEO keywords woven in naturally
#  * "Adjust tone" for low_content (planners/journals) vs content books

DESCRIPTIONS: dict[str, str] = {
    # -----------------------------------------------------------------
    "adhd-planner": (
        "Built for the ADHD brain - finally a planner that works with your wiring, not against it.\n\n"
        "If traditional planners leave you blank-page-paralyzed by 9 a.m., this 129-page workbook gives you the structure you need without the overwhelm. Every spread is dopamine-friendly, executive-function-aware, and forgiving on the days your brain decides to do its own thing.\n\n"
        "Who it's for:\n"
        "- Adults living with ADHD, ADD, or suspected neurodivergence\n"
        "- Students, freelancers, and parents juggling too many open tabs\n"
        "- Anyone who has bought (and abandoned) five planners already\n\n"
        "What's inside:\n"
        "- Daily focus pages with task triage, energy check-in, and a single \"if nothing else\" priority\n"
        "- Time-blindness fighters: visual time blocks, pomodoro logs, and transition cues\n"
        "- Brain-dump and idea-park sections so racing thoughts have a home\n"
        "- Weekly executive-function review: wins, friction points, and one thing to tweak\n"
        "- Habit and medication tracker grids you can actually keep up with\n\n"
        "Use it on the morning you can't get started, the afternoon your focus crashes, the Sunday you want to reset the week. No rigid date columns to fall behind on - undated pages mean you can pick it up after a missed week without guilt.\n\n"
        "Pair it with therapy, coaching, or solo work. It's a tool, not a cure - and that's the point.\n\n"
        "Tap \"Add to Cart\" and start your next 90 days with a planner that finally fits the way you think."
    ),
    # -----------------------------------------------------------------
    "ai-prompt-workbook": (
        "Stop typing \"write me something good\" and watch ChatGPT (or Claude, Gemini, or any LLM) actually deliver. This 130-page prompt workbook teaches you to engineer prompts the way professionals do - and gives you the space to practice until it's muscle memory.\n\n"
        "Who it's for:\n"
        "- Beginners who feel like AI \"never gets what I mean\"\n"
        "- Marketers, writers, students, and small-business owners using ChatGPT every day\n"
        "- Power users who want a paper system to refine and reuse winning prompts\n\n"
        "What's inside:\n"
        "- A simple, repeatable prompt framework (Role, Context, Task, Format, Constraints)\n"
        "- Fill-in templates for 30+ real use cases: emails, blog posts, code, study notes, ad copy, resumes, and more\n"
        "- Side-by-side compare pages: weak prompt vs. upgraded prompt vs. final output\n"
        "- A personal prompt library you build over time, indexed by goal\n"
        "- Iteration loops so you learn to refine, not just retype\n\n"
        "Use it during your morning planning, beside your laptop while you work, or on the train when you want to draft prompts offline before pasting them in. Works with ChatGPT, Claude, Gemini, Copilot, and any future model - because the framework is model-agnostic.\n\n"
        "By the last page you won't be \"prompting\" anymore. You'll be directing.\n\n"
        "Get your copy and turn AI from a guess-machine into your most reliable assistant."
    ),
    # -----------------------------------------------------------------
    "ai-side-hustle-en": (
        "The honest, no-fluff playbook for turning ChatGPT and other AI tools into a real second income stream - without quitting your job, learning to code, or buying a $997 course.\n\n"
        "This is a focused 31-page blueprint, not a 400-page brick. Every page exists to move you closer to your first paying client or first dollar of digital-product revenue.\n\n"
        "Who it's for:\n"
        "- 9-to-5 workers who want $500-$3,000 extra per month\n"
        "- Stay-at-home parents and students with limited weekly hours\n"
        "- Existing freelancers who want to multiply their output with AI\n\n"
        "What's inside:\n"
        "- 7 vetted AI side hustles ranked by start-up cost, time to first dollar, and ceiling\n"
        "- Step-by-step launch checklists for each (no \"and then magic happens\" gaps)\n"
        "- Pricing scripts, outreach templates, and the exact tools used\n"
        "- Common pitfalls that kill beginners - and how to avoid them\n"
        "- A weekly action tracker so you ship, not just read\n\n"
        "Built for evenings and weekends. Most readers can launch their first offer within 14 days of finishing the book.\n\n"
        "Stop bookmarking AI hustle threads on Reddit. Get the blueprint, pick one path, and start this weekend."
    ),
    # -----------------------------------------------------------------
    "airbnb-guestbook": (
        "Turn every stay into a five-star review and a memory worth keeping. This beautifully laid-out 104-page guestbook is built for Airbnb, VRBO, and short-term rental hosts who treat hospitality like a craft.\n\n"
        "Who it's for:\n"
        "- New and seasoned Airbnb / VRBO hosts\n"
        "- Owners of vacation cabins, beach houses, lake homes, and city apartments\n"
        "- Property managers running multiple short-term rentals\n\n"
        "What's inside:\n"
        "- Welcome pages with space for your house name, Wi-Fi, and check-out instructions\n"
        "- Local recommendations sections: restaurants, coffee, hikes, hidden gems, emergency info\n"
        "- 80+ structured guest entry pages: name, hometown, dates, favorite memory, drawing space\n"
        "- House rules and \"things you should know\" pages, kept friendly not clinical\n"
        "- A keepsake section so the book becomes part of the property's story over the years\n\n"
        "Use it as the centerpiece on your coffee table. Guests flip through entries from couples on their honeymoon, families from three states over, and travelers who left thank-you sketches - and they instinctively raise their own bar.\n\n"
        "Better reviews start with a better welcome. Order one for every property you host."
    ),
    # -----------------------------------------------------------------
    "blood-pressure-log": (
        "A simple, doctor-friendly blood pressure log designed for people who actually want to use it - not file it away after a week.\n\n"
        "Hypertension management lives or dies in the data. This 127-page log makes daily readings effortless, pattern-spotting obvious, and your next doctor visit ten times more productive.\n\n"
        "Who it's for:\n"
        "- Adults monitoring high or borderline blood pressure at home\n"
        "- Heart patients tracking trends between cardiology visits\n"
        "- Caregivers logging readings for an aging parent or partner\n"
        "- Anyone whose doctor said \"start measuring twice a day and bring me the numbers\"\n\n"
        "What's inside:\n"
        "- 52 weeks of dated grids: AM/PM systolic, diastolic, pulse, and notes\n"
        "- Medication tracker so you can correlate doses with readings\n"
        "- Mood, sleep, and salt-intake notes - the variables doctors actually ask about\n"
        "- Weekly average summary boxes so trends pop off the page\n"
        "- Reference pages: BP categories, when to call your doctor, healthy lifestyle reminders\n\n"
        "Compact 6x9 format slips into a purse, glove box, or kitchen drawer next to the cuff. Large, clean grids work for older eyes and shaky mornings.\n\n"
        "Not medical advice - always follow your physician. But bring this to your next appointment and watch the conversation get sharper.\n\n"
        "Order today and take ownership of the most important number you're not paying enough attention to."
    ),
    # -----------------------------------------------------------------
    "blood-sugar-tracker": (
        "Take control of your glucose - one honest reading at a time.\n\n"
        "This 123-page blood sugar tracker turns the daily routine of finger sticks, meal logs, and insulin doses into something you can actually learn from. Built for type 1, type 2, gestational, and prediabetic readers who want to understand their numbers, not just record them.\n\n"
        "Who it's for:\n"
        "- People newly diagnosed with diabetes who need a simple system\n"
        "- Long-term diabetics tired of spreadsheet apps\n"
        "- Anyone tracking A1C trends, insulin response, or carb-glucose patterns\n"
        "- Caregivers monitoring a family member's diabetes\n\n"
        "What's inside:\n"
        "- 100+ daily logs: fasting, pre/post meal, bedtime readings (mg/dL or mmol/L)\n"
        "- Carb count, insulin dose, exercise, and mood columns side-by-side\n"
        "- Weekly review pages: averages, highs, lows, and what your body told you\n"
        "- Monthly A1C and weight tracker\n"
        "- Reference: target ranges, hypo/hyper symptoms, and questions to ask your doctor\n\n"
        "Travel-ready 6x9 size. Wide grids for tired eyes and post-meal hands. No app to forget your password to.\n\n"
        "Your glucose meter gives you a number. This book turns it into knowledge.\n\n"
        "Buy now and bring better data to your next endocrinology visit."
    ),
    # -----------------------------------------------------------------
    "bold-easy-coloring-animals": (
        "Bold lines. Big shapes. Adorable animals. This easy coloring book is made for the people most coloring books forget - seniors, those with low vision, beginners, and anyone who just wants to color without squinting.\n\n"
        "Who it's for:\n"
        "- Older adults and seniors looking for relaxing, low-stress activities\n"
        "- People with macular degeneration, cataracts, or general low vision\n"
        "- Beginners and reluctant colorers\n"
        "- Memory care and assisted-living activity coordinators\n\n"
        "What's inside:\n"
        "- 50+ original animal designs: cats, dogs, owls, elephants, bunnies, foxes, sea creatures, and more\n"
        "- Thick, bold outlines that stay visible even with tired eyes\n"
        "- Wide-open spaces - no tiny details, no frustration\n"
        "- One image per page (back side blank) so markers don't bleed through and ruin the next page\n"
        "- Large 8.5 x 11 inch format - the canvas your hands deserve\n\n"
        "Perfect for therapy sessions, rainy afternoons, hospital stays, group activities at senior centers, or quiet mornings with a cup of tea. Works with crayons, markers, colored pencils, and gel pens.\n\n"
        "Coloring is proven to lower stress, sharpen focus, and bring small daily joy. This book makes that joy accessible.\n\n"
        "Add to cart and gift one to yourself, a parent, or a friend who could use a calmer hour."
    ),
    # -----------------------------------------------------------------
    "budget-planner-couples": (
        "Money fights are the #1 predictor of divorce. This budget planner is the antidote.\n\n"
        "Built specifically for couples, this 132-page workbook turns \"the money talk\" from a dreaded fight into a 20-minute monthly ritual you actually look forward to. Whether you're newlyweds, long-married, or moving in for the first time - this is the planner that gets you on the same financial page.\n\n"
        "Who it's for:\n"
        "- Married, engaged, and cohabiting couples managing joint finances\n"
        "- Partners who don't agree on saving vs. spending styles\n"
        "- Couples with shared goals: house, baby, debt-free, retirement, travel\n\n"
        "What's inside:\n"
        "- Joint values + goals worksheets: define \"enough\" together before you split a single bill\n"
        "- 12 monthly budgets: income, fixed bills, variable categories, sinking funds\n"
        "- Bi-weekly money date templates: 5 questions, 20 minutes, zero blame\n"
        "- Debt avalanche/snowball trackers and net-worth check-ins\n"
        "- His / Hers / Ours columns so personal autonomy stays intact\n\n"
        "Use it side-by-side at the kitchen table once a month. Couples who track together stay together - and retire richer.\n\n"
        "Stop guessing where the paycheck went. Order today and have the money talk you've been avoiding - on paper, on purpose, on the same team."
    ),
    # -----------------------------------------------------------------
    "caregiver-daily-log": (
        "When you're caring for a loved one, you can't remember everything. You shouldn't have to. This 112-page caregiver daily log gives you and the rest of the care team a single trusted source of truth.\n\n"
        "Who it's for:\n"
        "- Family caregivers looking after aging parents\n"
        "- Dementia, Alzheimer's, and Parkinson's caregivers\n"
        "- Home-health aides and rotating shift caregivers\n"
        "- Anyone managing a recovery from surgery, stroke, or chronic illness\n\n"
        "What's inside:\n"
        "- 100+ daily log spreads: meals, fluids, medications (time + dose), bathroom, sleep, mood\n"
        "- Vitals tracking: blood pressure, blood sugar, temperature, weight\n"
        "- Symptom and behavior notes - critical for dementia care decisions\n"
        "- Visitor and shift handoff section so the next caregiver knows exactly where things stand\n"
        "- Appointment, prescription, and emergency contact pages up front\n\n"
        "Bring it to every doctor's appointment. Pass it between siblings, home aides, and respite caregivers. When the doctor asks \"how has she been over the last two weeks?\" - the answer is in your hand.\n\n"
        "Compact, durable, and dignified. Caregiving is hard. Remembering shouldn't be one more weight.\n\n"
        "Order one today for the loved one in your care."
    ),
    # -----------------------------------------------------------------
    "cottagecore-coloring": (
        "Slow living, by way of colored pencil. This cottagecore coloring book invites you into a softer, slower world - garden cottages, wildflower meadows, sunlit kitchens, and afternoons that smell like rising bread.\n\n"
        "Who it's for:\n"
        "- Adults who love the cottagecore aesthetic and slow-living movement\n"
        "- Coloring enthusiasts ready to graduate from generic mandalas\n"
        "- Anyone using coloring as a quiet ritual for stress relief\n"
        "- Gift-givers shopping for tea-and-blanket personalities\n\n"
        "What's inside:\n"
        "- 50+ original cottagecore illustrations: thatched cottages, herb gardens, mushroom forests, vintage kitchens, fox-and-fawn vignettes, summer picnics, autumn orchards\n"
        "- Mix of intricate detail pages and softer, calmer scenes - color matched to your mood\n"
        "- Large 8.5 x 11 inch format with single-sided pages so markers won't bleed\n"
        "- A romantic, hand-illustrated feel that makes finished pages frame-worthy\n\n"
        "Brew tea. Open a window. Color one page. The day will feel different.\n\n"
        "Whether you're new to adult coloring or you've worn out three pencil sets already, this book is the one you'll keep close to your favorite chair.\n\n"
        "Add it to your cart and bring the countryside home."
    ),
    # -----------------------------------------------------------------
    "dog-health-training-log": (
        "One book, your dog's whole life. From puppyhood vaccinations to senior-dog vet visits, this 142-page health and training log is the complete record every responsible owner wishes they'd started on day one.\n\n"
        "Who it's for:\n"
        "- New puppy parents (start here on day one)\n"
        "- Owners of multiple dogs, foster dogs, or breeding programs\n"
        "- Anyone training a service dog, working dog, or competition dog\n"
        "- Pet sitters and dog walkers tracking other people's pups\n\n"
        "What's inside:\n"
        "- Profile, microchip, breed info, and emergency contact pages\n"
        "- Vaccination, deworming, and flea/tick treatment schedules\n"
        "- Vet visit log: weight, diagnosis, prescriptions, follow-ups\n"
        "- Grooming, dental, and nail care tracking\n"
        "- Training progress: commands learned, dates mastered, problem behaviors\n"
        "- Daily walk, exercise, and food/water log spreads\n"
        "- Photo memory pages for each milestone\n\n"
        "Vets can finally look back instead of guessing. New trainers can pick up exactly where the last one left off. And on the heartbreaking day you lose your best friend, you'll have a record of every adventure you shared.\n\n"
        "Get the journal your dog deserves."
    ),
    # -----------------------------------------------------------------
    "dot-marker-kids": (
        "Big circles. Big smiles. Toddler-sized fun.\n\n"
        "This dot marker activity book is purpose-built for little hands holding their first bingo daubers. Every page is a small win - building hand-eye coordination, color recognition, counting, and confidence.\n\n"
        "Who it's for:\n"
        "- Toddlers and preschoolers ages 1-4\n"
        "- Homeschool families building early fine-motor skills\n"
        "- Daycares, preschools, and Sunday schools\n"
        "- Grandparents stocking the activity drawer\n\n"
        "What's inside:\n"
        "- 50+ original dot-marker pages: animals, vehicles, alphabet letters, numbers 1-10, shapes, fruits, weather\n"
        "- Big, well-spaced dots sized for standard bingo daubers and Do-A-Dot markers\n"
        "- Single-image pages on bright white paper - no clutter, no overwhelm\n"
        "- Large 8.5 x 11 inch format so little arms can work without crowding\n"
        "- Mix of \"fill the dots\" pages and \"follow the pattern\" pages for gradual difficulty\n\n"
        "Independent play, screen-free quiet time, restaurant rescue, road-trip lifesaver, preschool prep all wrapped into one. Toddlers feel proud when they finish a page - and parents finally get five minutes to drink coffee while it's still hot.\n\n"
        "Order it today and watch your kid choose this book over the iPad."
    ),
    # -----------------------------------------------------------------
    "fishing-log-book": (
        "Every angler has \"the spot.\" Smart anglers have a logbook.\n\n"
        "This 104-page fishing journal helps you fish smarter, remember more, and turn lucky days into repeatable strategies. Whether you chase bass on a weekend lake, fly-fish quiet rivers, or charter the deep blue, your patterns live in here.\n\n"
        "Who it's for:\n"
        "- Bass, trout, and panfish anglers\n"
        "- Fly fishers, kayak fishers, and ice fishers\n"
        "- Charter captains and tournament fishermen\n"
        "- Dad-and-kid fishing buddies building a multi-year story\n\n"
        "What's inside:\n"
        "- 100+ structured trip log pages: date, location, weather, water temp, moon phase\n"
        "- Tackle and lure breakdowns - what worked, what didn't\n"
        "- Catch records: species, length, weight, depth, time, photo space\n"
        "- Tide and seasonal pattern reference pages\n"
        "- Trip-of-the-year highlights and \"return here\" map sketch pages\n\n"
        "Compact 6x9 size fits a tackle box. Scribble in it while the fish stop biting. Read it back two seasons later and notice the bite-window your gut was right about all along.\n\n"
        "The river forgets. The book remembers. Get yours and stack the deck on every trip."
    ),
    # -----------------------------------------------------------------
    "fortune-notebook": (
        "Money flows where attention goes. This 151-page fortune notebook turns abundance from a vague hope into a daily practice you can see, measure, and feel shift over time.\n\n"
        "Who it's for:\n"
        "- Manifestation and Law-of-Attraction practitioners\n"
        "- Lottery players, dreamers, and gratitude-journal believers\n"
        "- Anyone rebuilding their relationship with money after debt or scarcity seasons\n"
        "- Spiritual journalers ready for something more intentional than a blank notebook\n\n"
        "What's inside:\n"
        "- Daily prompts for gratitude, intention, money-mindset, and luck-noticing\n"
        "- Lucky number, dream, and synchronicity logs\n"
        "- Wealth visualization pages: define the life you're calling in\n"
        "- Weekly review: what came, what shifted, what to release\n"
        "- Affirmation library and abundance script templates\n"
        "- Year-end reflection: how your fortune actually changed\n\n"
        "This isn't a magic spell. It's the simple, repeatable habit that almost every wealthy person credits when asked. Five minutes a day. Pen on paper. Mind aligned with money.\n\n"
        "Start writing the next year of your fortune. Order today."
    ),
    # -----------------------------------------------------------------
    "genz-stress": (
        "School, jobs, climate dread, social media, situationships, rent. No wonder you're tired.\n\n"
        "The Gen Z Stress Workbook is a research-backed, 68-page hands-on guide built for young adults staring down a world that didn't come with instructions. No \"just meditate, sweetie\" advice. Real tools that fit between classes, shifts, and TikTok scrolls.\n\n"
        "Who it's for:\n"
        "- High school and college students\n"
        "- Early-career 20-somethings navigating burnout\n"
        "- Anyone whose anxiety spikes the moment notifications turn on\n"
        "- Therapists looking for a workbook to hand clients between sessions\n\n"
        "What's inside:\n"
        "- A self-assessment to map your specific stress signature\n"
        "- 7 evidence-based techniques: cognitive reframing, somatic grounding, boundary scripts, sleep repair, social-media detoxes, financial-anxiety triage, friendship audit\n"
        "- Fill-in worksheets - this is a workbook, not a lecture\n"
        "- A 4-week reset plan you can actually finish\n"
        "- Crisis-line and resource page in the back, no stigma\n\n"
        "If you've cycled through wellness apps that all sound the same, this is the offline reset your brain has been begging for.\n\n"
        "Get your copy and take back the next month of your life."
    ),
    # -----------------------------------------------------------------
    "introvert-confidence": (
        "Confidence isn't loud. The world just acts like it is.\n\n"
        "This 56-page workbook is for the quiet ones - the readers, the listeners, the deep-thinkers who feel drained by small talk and underestimated in meetings. You don't need to become an extrovert. You need to stop apologizing for the way you already work.\n\n"
        "Who it's for:\n"
        "- Self-identified introverts and shy adults\n"
        "- HSPs (highly sensitive people) navigating loud workplaces\n"
        "- Students and early professionals tired of being told to \"speak up more\"\n"
        "- Anyone who finishes a party and needs three days to recover\n\n"
        "What's inside:\n"
        "- An introvert-strengths inventory: name what you're already great at\n"
        "- Energy management worksheets - protect the battery, do better work\n"
        "- Scripts for hard moments: meetings, networking events, dating, family dinners\n"
        "- Boundary-setting templates that don't sound aggressive\n"
        "- A 30-day quiet-confidence plan with daily micro-practices\n\n"
        "Built on the work of Susan Cain, Carl Jung, and modern psychology - distilled into pages you can fill out in 10 minutes a day.\n\n"
        "The world needs your kind of strength. Get the workbook that helps you bring it - on your terms."
    ),
    # -----------------------------------------------------------------
    "math-workbook-grade1": (
        "Confidence with numbers starts here.\n\n"
        "This 101-page first-grade math workbook is everything a 6- to 7-year-old needs to master the foundations of arithmetic - addition, subtraction, place value, simple time and money, and beginner word problems - without tears or screen time.\n\n"
        "Who it's for:\n"
        "- 1st grade students (ages 6-7) and advanced kindergarteners\n"
        "- Homeschool families following a Common Core or classical math sequence\n"
        "- Parents supplementing classroom learning at home\n"
        "- Tutors and after-school program coordinators\n\n"
        "What's inside:\n"
        "- 100+ pages of carefully sequenced practice: numbers to 100, addition and subtraction within 20, then within 100\n"
        "- Place-value drills (tens and ones), comparing numbers, simple skip counting\n"
        "- Time-telling, money basics, measurement, and shapes\n"
        "- Word problems that build reading-and-math fluency at the same time\n"
        "- Weekly review pages and confidence-building \"I can do this\" check-ins\n"
        "- Large 8.5 x 11 format with kid-friendly fonts and plenty of writing space\n\n"
        "Use it as a school-year supplement, a summer-bridge book, or a daily 15-minute habit. Built so kids can work mostly independently while parents check at the end.\n\n"
        "Set your child up to walk into 2nd grade fearless. Order today."
    ),
    # -----------------------------------------------------------------
    "meal-prep-planner": (
        "Eat better, spend less, and reclaim your evenings. This 107-page meal prep planner makes weekly meal planning, grocery shopping, and Sunday cooking the smoothest part of your week.\n\n"
        "Who it's for:\n"
        "- Busy professionals and parents who keep ordering takeout because the week ran them over\n"
        "- Fitness, keto, paleo, vegetarian, and macro-tracking eaters\n"
        "- Couples and families who want one shared system for food\n"
        "- Anyone trying to cut grocery bills without sacrificing nutrition\n\n"
        "What's inside:\n"
        "- 52 weekly meal-plan spreads: breakfast, lunch, dinner, snacks for 7 days\n"
        "- Pull-out grocery lists organized by store section (produce, protein, pantry, dairy, frozen)\n"
        "- Pantry inventory and freezer-stash logs - never re-buy what you already have\n"
        "- Recipe-keeper pages so the favorites that work get reused\n"
        "- Macros, calories, and budget columns where you want them\n"
        "- Weekly reflection: what worked, what got wasted, what to keep next week\n\n"
        "Pin it on the kitchen wall. Bring it to the grocery store. Watch your food spend drop and your weeknight stress disappear.\n\n"
        "Order today and make the next four weeks of dinners decisions you've already made."
    ),
    # -----------------------------------------------------------------
    "mental-reset-journal": (
        "When your mind feels like 47 browser tabs and a low battery warning - open this journal.\n\n"
        "The Mental Reset Journal is a 47-page guided notebook designed for the moments you most need it: the anxious morning, the burnt-out afternoon, the 2 a.m. spiral. Short. Honest. Genuinely calming.\n\n"
        "Who it's for:\n"
        "- Adults dealing with anxiety, low mood, or burnout\n"
        "- Therapy clients who need between-session work\n"
        "- High-achievers learning that productivity isn't the same as wellness\n"
        "- First-time journalers who don't know where to start\n\n"
        "What's inside:\n"
        "- Mental-reset prompts grounded in CBT, ACT, and mindfulness traditions\n"
        "- Brain dump and worry-park pages so racing thoughts have a place to land\n"
        "- Body scan and grounding exercises in printed step-by-step form\n"
        "- Gratitude, self-compassion, and reframe pages - paced gently\n"
        "- A 7-day mini-reset structure for harder weeks\n\n"
        "Keep it on your nightstand, in your bag, or beside your therapist's couch. When the noise gets loud, pick it up. Five minutes of pen on paper does more than an hour of doomscrolling - and your nervous system already knows it.\n\n"
        "Order your reset today."
    ),
    # -----------------------------------------------------------------
    "password-logbook": (
        "Stop emailing yourself your own passwords.\n\n"
        "This 117-page password logbook is the offline, hack-proof, mom-can-actually-use-it solution to digital chaos. No subscription. No account to recover. Just an alphabetized book that stays exactly where you put it.\n\n"
        "Who it's for:\n"
        "- Adults overwhelmed by 100+ online accounts\n"
        "- Seniors and parents who don't trust password managers\n"
        "- Small-business owners juggling vendor logins\n"
        "- Anyone who keeps clicking \"Forgot Password?\" three times a week\n\n"
        "What's inside:\n"
        "- A-to-Z tabbed sections so finding \"Netflix\" takes two seconds\n"
        "- Structured fields per entry: website, username, password, security questions, recovery email, notes\n"
        "- Multiple entries per letter - real-world capacity, not 5-account toy size\n"
        "- Wi-Fi network and modem reset reference page\n"
        "- Software license, subscription, and renewal tracker\n"
        "- Emergency-info page so a trusted person can step in if needed\n\n"
        "Compact 6x9 size. Soft, durable cover. Looks like a journal so it doesn't scream \"my passwords are inside.\" Keep it in a desk drawer, not a laptop bag.\n\n"
        "Get yours and stop the password panic - today."
    ),
    # -----------------------------------------------------------------
    "password-logbook-premium": (
        "The biggest, most generous password keeper on the market - made for serious users.\n\n"
        "At 173 pages, the Password Logbook Premium is the senior-friendly, large-print, large-capacity edition for anyone who has finally given up on app-based password managers and wants a system that just works on paper.\n\n"
        "Who it's for:\n"
        "- Seniors and adults with low vision who need genuinely large print\n"
        "- Heavy users with hundreds of accounts (think: small business + personal + family)\n"
        "- Anyone who has been locked out of a password manager and never wants that feeling again\n"
        "- Caregivers helping a parent organize their digital life\n\n"
        "What's inside:\n"
        "- A-to-Z alphabetized sections with extra room per letter\n"
        "- Large-print fields for site name, username, password, security questions, notes\n"
        "- Wi-Fi, router, smart-home, and ISP reference pages\n"
        "- Subscription and software license tracker\n"
        "- Banking and finance section (kept separate, with a discreet header)\n"
        "- Emergency access info so a spouse or executor can step in\n\n"
        "Built for clarity. Big fields. Soft cover. 6x9 size that fits a desk drawer. No batteries, no updates, no \"please verify your identity to log in.\"\n\n"
        "Order the premium edition and finally have your digital life in one trustworthy place."
    ),
    # -----------------------------------------------------------------
    "perimenopause-symptom-tracker": (
        "Hot flashes, mood swings, brain fog, sleep that breaks at 3 a.m. - perimenopause is real, and you deserve a doctor who takes it seriously. This 121-page symptom tracker hands you the data to make that happen.\n\n"
        "Who it's for:\n"
        "- Women in their late 30s, 40s, and early 50s navigating perimenopause\n"
        "- Patients preparing for OB/GYN, GP, or HRT specialist visits\n"
        "- Anyone tracking the impact of hormone therapy, supplements, or lifestyle changes\n"
        "- Daughters and partners supporting someone through midlife transition\n\n"
        "What's inside:\n"
        "- Daily symptom log: hot flashes, sleep, mood, energy, brain fog (1-10 scale)\n"
        "- Cycle tracker - because cycles get weird before they end\n"
        "- HRT, supplement, and medication log with dose and side-effect notes\n"
        "- Weight, BP, and exercise tracking\n"
        "- Monthly review pages: \"what got better, what got worse, what's new\"\n"
        "- Doctor visit prep pages: questions to ask, symptoms to flag\n"
        "- Resource section: 35+ named symptoms most women never knew were perimenopause\n\n"
        "You're not crazy. You're not broken. You're not alone. You're in a hormonal transition that medicine has spent decades dismissing - and you're about to walk into your next appointment with receipts.\n\n"
        "Order today and turn confusion into clarity."
    ),
    # -----------------------------------------------------------------
    "saju-diary": (
        "내 사주, 내 손으로 풀어보는 1년치 일진 다이어리.\n\n"
        "사주명리에 막연한 호기심만 있던 분도, 이미 만세력 앱과 친한 분도, 매일 아침 5분이면 오늘의 흐름과 내 상태를 기록할 수 있는 393페이지 본격 사주 다이어리입니다.\n\n"
        "이런 분께 추천합니다:\n"
        "- 사주 입문자: 매일 적으며 자연스럽게 음양오행과 십신을 익히고 싶은 분\n"
        "- 사주 중급자: 일진을 직접 추적하며 본인의 운세 패턴을 검증하고 싶은 분\n"
        "- 명리 상담을 받아본 후 일상에서 활용하고 싶은 분\n"
        "- 단순 운세보다 깊이 있는 자기 이해를 원하는 분\n\n"
        "이런 내용이 들어 있습니다:\n"
        "- 1일 1페이지 일진 기록 양식: 천간지지, 오늘의 십신, 길흉 메모, 컨디션 체크\n"
        "- 음양오행 균형 자가 진단 페이지\n"
        "- 12지지·10천간·60갑자 핵심 요약 레퍼런스\n"
        "- 월별 회고 페이지: 들어온 운, 빠져나간 운, 잡아야 할 흐름\n"
        "- 인연·재물·건강·진로 영역별 기록 섹션\n"
        "- 주요 절기와 입춘 기점 표기\n\n"
        "단순한 운세 노트가 아닙니다. 매일 적는 데이터가 쌓이면 \"내가 어떤 흐름에 강하고 약한지\"가 직접 보입니다. 1년 후에는 누군가의 풀이가 아니라 본인의 사주를 본인이 가장 잘 아는 사람이 됩니다.\n\n"
        "올해를 운명에 맡기지 말고, 운명을 기록해 보세요.\n\n"
        "지금 주문하고 오늘부터 첫 페이지를 시작하세요."
    ),
    # -----------------------------------------------------------------
    "sleep-planner": (
        "Better sleep is a system, not a miracle.\n\n"
        "This 105-page sleep planner is the practical, science-aligned tracker that turns \"I don't sleep well\" into a real strategy. Whether you're battling chronic insomnia or just want to wake up feeling human again, this is the offline reset your nervous system has been waiting for.\n\n"
        "Who it's for:\n"
        "- Adults with insomnia, restless sleep, or shift-work disruption\n"
        "- People testing CBT-I, sleep restriction, or stimulus-control techniques\n"
        "- Anyone tracking the effect of melatonin, magnesium, alcohol, or screen time\n"
        "- Patients preparing for sleep-clinic or doctor visits\n\n"
        "What's inside:\n"
        "- 90-day sleep log: bedtime, wake time, time to fall asleep, awakenings, total hours\n"
        "- Sleep quality 1-10, mood at wake, daytime energy crash points\n"
        "- Pre-bed routine, caffeine, alcohol, and screen-time check-ins\n"
        "- Weekly review: average hours, sleep efficiency, biggest disruptors\n"
        "- Bedtime routine builder and 30-day habit reset\n"
        "- Reference: sleep hygiene basics, what your circadian rhythm actually needs\n\n"
        "Most sleep apps overload you with charts you can't act on. This planner forces clarity - one page, one night, one tweak. Fill it in for 30 days and most readers see a measurable shift.\n\n"
        "Order today and reclaim your mornings, one good night at a time."
    ),
    # -----------------------------------------------------------------
    "spot-difference-seniors": (
        "Sharper eyes, calmer minds, and a smile worth coming back for.\n\n"
        "This 57-page Spot the Difference activity book is built specifically for seniors, dementia care, and anyone who finds standard puzzle books too small or frustrating. Big art. Bold differences. Real satisfaction.\n\n"
        "Who it's for:\n"
        "- Seniors looking for a relaxing, screen-free brain workout\n"
        "- Memory care, assisted-living, and adult day-program activity coordinators\n"
        "- Caregivers searching for shared activities with loved ones in early dementia\n"
        "- Adults with low vision or arthritis who can't use small puzzle books\n\n"
        "What's inside:\n"
        "- 50+ original spot-the-difference pairs - everyday scenes seniors recognize and love\n"
        "- Large 8.5 x 11 inch format - easy on tired eyes\n"
        "- Bold lines, generous spacing, and varied difficulty (5-10 differences per puzzle)\n"
        "- Answer keys at the back so no frustration, only success\n"
        "- Friendly themes: kitchens, gardens, parks, pets, holiday scenes\n\n"
        "Spot-the-difference puzzles activate visual memory and attention - two of the first cognitive areas to soften with age. Daily 15-minute sessions are an easy, dignity-preserving habit.\n\n"
        "A perfect gift for grandparents, parents in care, or your own quiet afternoon. Order today."
    ),
    # -----------------------------------------------------------------
    "yoga-progress-journal": (
        "Your yoga practice deserves more than a sticky mat and good intentions.\n\n"
        "This 91-page yoga progress journal helps you track poses, breath, body sensations, and growth over time - turning your practice from a series of classes into a real, evolving discipline you can see.\n\n"
        "Who it's for:\n"
        "- Beginner yogis building consistency\n"
        "- Intermediate practitioners working toward arm balances, inversions, or splits\n"
        "- Yoga teachers in training (200/500 hour) documenting their own practice\n"
        "- Studios and teachers gifting students a deeper learning tool\n\n"
        "What's inside:\n"
        "- Daily session pages: style (vinyasa, yin, hatha, ashtanga), duration, focus\n"
        "- Pose tracker with progress notes: how it felt, where the edge was, what changed\n"
        "- Breath, mood, and body-scan check-ins (pre and post practice)\n"
        "- Goal-pose worksheets for poses you're working toward\n"
        "- Weekly and monthly reflections - the pattern only shows up over time\n"
        "- Mantra, intention, and gratitude pages woven through\n\n"
        "Yoga isn't about flexibility - it's about awareness. This journal gives that awareness somewhere to land. Six months in, you won't recognize your old self.\n\n"
        "Order your copy and roll out your mat with intention starting today."
    ),
    # -----------------------------------------------------------------
    "zodiac-mandala-coloring": (
        "Where the stars meet the page.\n\n"
        "This 126-page zodiac mandala coloring book blends two of the most beloved themes in adult coloring - sacred-geometry mandalas and the 12 astrological signs - into a single meditative practice that's as beautiful as it is calming.\n\n"
        "Who it's for:\n"
        "- Adult coloring enthusiasts ready for intricate, statement-piece designs\n"
        "- Astrology lovers and spiritual seekers\n"
        "- Anyone using coloring as a meditation, journaling, or shadow-work tool\n"
        "- Gift-givers shopping for the witchy, woo-curious, or zodiac-obsessed\n\n"
        "What's inside:\n"
        "- 50+ original mandala designs, each one tied to a zodiac sign and its symbolism\n"
        "- Aries through Pisces: ruling planet, element, archetype, and key glyphs woven into the geometry\n"
        "- Mix of detailed mandalas and softer, simpler patterns - color matched to your mood\n"
        "- Large 8.5 x 11 inch format with single-sided pages so markers won't bleed through\n"
        "- Short astrology insight at the start of each sign's section\n\n"
        "Whether Mercury is in retrograde or you just need a quiet hour, this book centers you. Pick your sign, light a candle, color one mandala. Notice what shifts.\n\n"
        "Order today and bring the zodiac to your fingertips."
    ),
}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    if not PROJECTS_DIR.exists():
        print(f"[FATAL] Projects directory not found: {PROJECTS_DIR}")
        return 2

    folders = sorted(p for p in PROJECTS_DIR.iterdir() if p.is_dir() and not p.name.startswith("__"))

    pass_count = 0
    skip_count = 0
    fail_count = 0
    char_lengths: list[int] = []
    review_needed: list[str] = []

    for folder in folders:
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            continue

        book_id = folder.name
        try:
            with manifest_path.open("r", encoding="utf-8") as fh:
                manifest = json.load(fh)
        except Exception as exc:
            print(f"[FAIL] {book_id}: cannot read manifest ({exc})")
            fail_count += 1
            continue

        existing = manifest.get("description", "")
        # If description is already filled (no TODO sentinel), skip
        if "[TODO" not in existing and existing.strip():
            print(f"[SKIP] {book_id}: description already filled ({len(existing)} chars)")
            skip_count += 1
            continue

        new_desc = DESCRIPTIONS.get(book_id)
        if not new_desc:
            print(f"[FAIL] {book_id}: no description authored in DESCRIPTIONS dict")
            fail_count += 1
            review_needed.append(book_id)
            continue

        # Sanity: KDP hard cap is 4000 chars
        if len(new_desc) > 4000:
            print(f"[FAIL] {book_id}: description exceeds 4000 chars ({len(new_desc)})")
            fail_count += 1
            continue

        manifest["description"] = new_desc

        # Remove "description" from todo
        todo = manifest.get("todo", [])
        if "description" in todo:
            todo = [t for t in todo if t != "description"]
            manifest["todo"] = todo

        try:
            with manifest_path.open("w", encoding="utf-8") as fh:
                json.dump(manifest, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
        except Exception as exc:
            print(f"[FAIL] {book_id}: cannot write manifest ({exc})")
            fail_count += 1
            continue

        char_lengths.append(len(new_desc))
        pass_count += 1
        flag = ""
        if len(new_desc) < 1500:
            flag = " (short - review)"
            review_needed.append(book_id)
        print(f"[ OK ] {book_id}: {len(new_desc)} chars{flag}")

    total = pass_count + skip_count + fail_count
    avg = sum(char_lengths) // len(char_lengths) if char_lengths else 0

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"PASS : {pass_count}/{total}")
    print(f"SKIP : {skip_count} (already had description)")
    print(f"FAIL : {fail_count}")
    print(f"Avg chars (newly written): {avg}")
    if review_needed:
        print(f"Review suggested for: {', '.join(review_needed)}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
