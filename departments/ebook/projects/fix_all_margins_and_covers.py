"""
Master script to:
1. Fix margins in all 20 generate.py files
2. Regenerate all interior PDFs
3. Generate full-wrap KDP covers for all 20 books

Run: python fix_all_margins_and_covers.py
"""
import os, sys, re, subprocess
from pathlib import Path

BASE = Path(__file__).parent

# ============================================================
# BOOK DEFINITIONS
# ============================================================
BOOKS = [
    # (folder, trim, interior_pdf_name)
    ("password-logbook",            "8.5x11", "Password_Logbook_Interior.pdf"),
    ("adhd-planner",                "8.5x11", "ADHD_Planner_Interior.pdf"),
    ("mental-reset-journal",        "8.5x11", "Mental_Reset_Journal_Interior.pdf"),
    ("sleep-planner",               "8.5x11", "Sleep_Planner_Interior.pdf"),
    ("ai-side-hustle-en",           "6x9",    "AI_Side_Hustle_Blueprint_Interior.pdf"),
    ("dot-marker-kids",             "8.5x11", "Dot_Marker_Activity_Book_Interior.pdf"),
    ("spot-difference-seniors",     "8.5x11", "Spot_Difference_Seniors_Interior.pdf"),
    ("genz-stress",                 "8.5x11", "GenZ_Stress_Workbook.pdf"),
    ("introvert-confidence",        "6x9",    "Confidence_Building_Introverts.pdf"),
    ("password-logbook-premium",    "8.5x11", "Password_Logbook_Premium_Seniors.pdf"),
    ("blood-pressure-log",          "8.5x11", "blood_pressure_log_book.pdf"),
    ("blood-sugar-tracker",         "8.5x11", "diabetic_blood_sugar_log.pdf"),
    ("airbnb-guestbook",            "6x9",    "airbnb_guest_book.pdf"),
    ("bold-easy-coloring-animals",  "8.5x11", "bold_easy_coloring_animals.pdf"),
    ("cottagecore-coloring",        "8.5x11", "cottagecore_coloring.pdf"),
    ("math-workbook-grade1",        "8.5x11", "math_workbook_grade1.pdf"),
    ("yoga-progress-journal",       "6x9",    "yoga_progress_journal.pdf"),
    ("budget-planner-couples",      "8.5x11", "budget_planner_couples.pdf"),
    ("zodiac-mandala-coloring",     "8.5x11", "zodiac_mandala_coloring.pdf"),
    ("meal-prep-planner",           "8.5x11", "meal_prep_planner.pdf"),
]


def fix_margins():
    """Fix margin values in all generate.py files."""
    print("=" * 60)
    print("STEP 1: Fixing margins in all generate.py files")
    print("=" * 60)

    for folder, trim, _ in BOOKS:
        gen_py = BASE / folder / "generate.py"
        if not gen_py.exists():
            print(f"  SKIP {folder}: no generate.py")
            continue

        content = gen_py.read_text(encoding="utf-8")
        original = content

        if trim == "8.5x11":
            target_margin = 0.75
            # Fix top-level MARGIN / M definitions
            # Pattern: MARGIN = X.XX * inch  or  M = X.XX * inch
            content = re.sub(
                r'^(MARGIN\s*=\s*)[\d.]+(\s*\*\s*inch)',
                rf'\g<1>{target_margin}\2',
                content, flags=re.MULTILINE
            )
            content = re.sub(
                r'^(M\s*=\s*)[\d.]+(\s*\*\s*inch)',
                rf'\g<1>{target_margin}\2',
                content, flags=re.MULTILINE
            )
            # Fix local margin = 0.5 * inch or margin = 0.6 * inch in functions
            content = re.sub(
                r'(\bmargin\s*=\s*)0\.[456]\s*\*\s*inch',
                rf'\g<1>{target_margin} * inch',
                content
            )
        else:  # 6x9
            target_margin = 0.6
            content = re.sub(
                r'^(MARGIN\s*=\s*)[\d.]+(\s*\*\s*inch)',
                rf'\g<1>{target_margin}\2',
                content, flags=re.MULTILINE
            )
            content = re.sub(
                r'^(M\s*=\s*)[\d.]+(\s*\*\s*inch)',
                rf'\g<1>{target_margin}\2',
                content, flags=re.MULTILINE
            )
            # For introvert-confidence which has MARGIN_OUTER / MARGIN_INNER etc
            content = re.sub(
                r'^(MARGIN_OUTER\s*=\s*)[\d.]+(\s*\*\s*inch)',
                rf'\g<1>{target_margin}\2',
                content, flags=re.MULTILINE
            )
            content = re.sub(
                r'^(MARGIN_INNER\s*=\s*)[\d.]+(\s*\*\s*inch)',
                rf'\g<1>{target_margin + 0.15}\2',  # gutter slightly wider
                content, flags=re.MULTILINE
            )
            content = re.sub(
                r'^(MARGIN_TOP\s*=\s*)[\d.]+(\s*\*\s*inch)',
                rf'\g<1>{target_margin}\2',
                content, flags=re.MULTILINE
            )
            content = re.sub(
                r'^(MARGIN_BOTTOM\s*=\s*)[\d.]+(\s*\*\s*inch)',
                rf'\g<1>{target_margin}\2',
                content, flags=re.MULTILINE
            )
            # Fix local margin in functions
            content = re.sub(
                r'(\bmargin\s*=\s*)0\.[45]\s*\*\s*inch',
                rf'\g<1>{target_margin} * inch',
                content
            )

        if content != original:
            gen_py.write_text(content, encoding="utf-8")
            print(f"  FIXED {folder} -> margin={target_margin}\"")
        else:
            print(f"  OK    {folder} (already correct or no match)")


def regenerate_interiors():
    """Run each generate.py to regenerate interior PDFs."""
    print("\n" + "=" * 60)
    print("STEP 2: Regenerating all interior PDFs")
    print("=" * 60)

    for folder, trim, pdf_name in BOOKS:
        gen_py = BASE / folder / "generate.py"
        if not gen_py.exists():
            print(f"  SKIP {folder}")
            continue

        print(f"\n  [{folder}] Running generate.py...")
        result = subprocess.run(
            [sys.executable, str(gen_py)],
            cwd=str(BASE / folder),
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            print(f"    {result.stdout.strip()}")
        else:
            print(f"    ERROR: {result.stderr.strip()}")


def count_pages(pdf_path):
    """Count pages in a PDF using PyPDF2 or reportlab."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except ImportError:
        pass
    # Fallback: parse the file
    try:
        with open(pdf_path, 'rb') as f:
            data = f.read()
        # Count /Type /Page (not /Pages)
        import re as _re
        pages = _re.findall(rb'/Type\s*/Page(?!s)', data)
        return len(pages)
    except:
        return 0


def generate_full_wrap_covers():
    """Generate full-wrap KDP covers (back + spine + front) for all 20 books."""
    print("\n" + "=" * 60)
    print("STEP 3: Generating full-wrap KDP covers")
    print("=" * 60)

    from reportlab.lib.units import inch as rl_inch
    from reportlab.lib.colors import HexColor, Color, white, black
    from reportlab.pdfgen import canvas
    import math

    def hex_alpha(hex_str, alpha):
        col = HexColor(hex_str)
        return Color(col.red, col.green, col.blue, alpha)

    def brightness_of(hex_str):
        r = int(hex_str[1:3], 16)
        g = int(hex_str[3:5], 16)
        b = int(hex_str[5:7], 16)
        return (r * 299 + g * 587 + b * 114) / 1000

    # Cover design data for each book
    COVER_DATA = [
        {
            "folder": "password-logbook",
            "trim": "8.5x11",
            "bg": "#0f0f2e",
            "accent": "#4a90d9",
            "title_lines": ["PASSWORD", "LOGBOOK"],
            "subtitle_lines": ["Keep Your Internet Passwords", "Safe & Organized"],
            "title_size": 48,
            "features": ["Alphabetical A-Z Tabs", "Large Print", "120+ Pages"],
        },
        {
            "folder": "adhd-planner",
            "trim": "8.5x11",
            "bg": "#6A0DAD",
            "accent": "#FFD700",
            "title_lines": ["ADHD DAILY", "PLANNER"],
            "subtitle_lines": ["Stay Focused, Stay Organized", "A Practical Planning System for ADHD Minds"],
            "title_size": 46,
        },
        {
            "folder": "mental-reset-journal",
            "trim": "8.5x11",
            "bg": "#A8B89C",
            "accent": "#5C4033",
            "title_lines": ["MENTAL", "RESET", "JOURNAL"],
            "subtitle_lines": ["Clear Your Mind, Reclaim Your Peace", "A 90-Day Guided Journal"],
            "title_size": 42,
        },
        {
            "folder": "sleep-planner",
            "trim": "8.5x11",
            "bg": "#0B0B3B",
            "accent": "#F0E68C",
            "title_lines": ["SLEEP", "PLANNER"],
            "subtitle_lines": ["Track Your Nights, Transform Your Days", "A Complete Sleep Tracking System"],
            "title_size": 48,
        },
        {
            "folder": "ai-side-hustle-en",
            "trim": "6x9",
            "bg": "#0D1B2A",
            "accent": "#FFD700",
            "title_lines": ["AI SIDE", "HUSTLE"],
            "subtitle_lines": ["How to Make Money with AI", "A Step-by-Step Guide"],
            "title_size": 38,
        },
        {
            "folder": "dot-marker-kids",
            "trim": "8.5x11",
            "bg": "#FF4444",
            "accent": "#FFFFFF",
            "title_lines": ["DOT MARKER", "ACTIVITY", "BOOK"],
            "subtitle_lines": ["Fun Coloring for Toddlers!", "Ages 2-5"],
            "title_size": 44,
        },
        {
            "folder": "spot-difference-seniors",
            "trim": "8.5x11",
            "bg": "#1A3A4A",
            "accent": "#20B2AA",
            "title_lines": ["SPOT THE", "DIFFERENCE"],
            "subtitle_lines": ["Large Print Puzzle Book", "For Adults & Seniors"],
            "title_size": 44,
        },
        {
            "folder": "genz-stress",
            "trim": "8.5x11",
            "bg": "#4A0E4E",
            "accent": "#FF8C94",
            "title_lines": ["GEN Z", "STRESS", "RELIEF"],
            "subtitle_lines": ["A No-BS Guide to Chilling Out", "Journaling & De-Stressing"],
            "title_size": 44,
        },
        {
            "folder": "introvert-confidence",
            "trim": "6x9",
            "bg": "#2C3E6B",
            "accent": "#87CEEB",
            "title_lines": ["THE QUIET", "CONFIDENCE", "JOURNAL"],
            "subtitle_lines": ["Build Inner Strength", "Without Changing Who You Are"],
            "title_size": 34,
        },
        {
            "folder": "password-logbook-premium",
            "trim": "8.5x11",
            "bg": "#0F0F2E",
            "accent": "#D4A843",
            "title_lines": ["PASSWORD", "LOGBOOK", "PREMIUM"],
            "subtitle_lines": ["Internet Password Organizer", "Large Print | A-Z Tabs | 180+ Pages"],
            "title_size": 44,
        },
        {
            "folder": "blood-pressure-log",
            "trim": "8.5x11",
            "bg": "#FFFFFF",
            "accent": "#DC143C",
            "title_lines": ["BLOOD", "PRESSURE", "LOG"],
            "subtitle_lines": ["Daily Blood Pressure Tracker", "Monitor Your Health Every Day"],
            "title_size": 46,
        },
        {
            "folder": "blood-sugar-tracker",
            "trim": "8.5x11",
            "bg": "#F0FFFF",
            "accent": "#20B2AA",
            "title_lines": ["BLOOD SUGAR", "TRACKER"],
            "subtitle_lines": ["Daily Glucose Monitoring Log", "Track Meals, Insulin & Levels"],
            "title_size": 44,
        },
        {
            "folder": "airbnb-guestbook",
            "trim": "6x9",
            "bg": "#FFF5E6",
            "accent": "#D2691E",
            "title_lines": ["WELCOME", "GUEST BOOK"],
            "subtitle_lines": ["A Keepsake for Your Airbnb", "Vacation Rental & Guest House"],
            "title_size": 36,
        },
        {
            "folder": "bold-easy-coloring-animals",
            "trim": "8.5x11",
            "bg": "#7CFC00",
            "accent": "#006400",
            "title_lines": ["BOLD & EASY", "COLORING", "ANIMALS"],
            "subtitle_lines": ["Simple Designs for All Ages", "Large Print | Stress-Free Fun"],
            "title_size": 40,
        },
        {
            "folder": "cottagecore-coloring",
            "trim": "8.5x11",
            "bg": "#FFE4E1",
            "accent": "#DB7093",
            "title_lines": ["COTTAGECORE", "COLORING", "BOOK"],
            "subtitle_lines": ["Whimsical Floral & Country Designs", "Relaxing Pages for All Ages"],
            "title_size": 40,
        },
        {
            "folder": "math-workbook-grade1",
            "trim": "8.5x11",
            "bg": "#4169E1",
            "accent": "#FFFFFF",
            "title_lines": ["MATH", "WORKBOOK", "GRADE 1"],
            "subtitle_lines": ["Addition, Subtraction & More!", "Fun Practice for Young Learners"],
            "title_size": 44,
        },
        {
            "folder": "yoga-progress-journal",
            "trim": "6x9",
            "bg": "#E6E6FA",
            "accent": "#20B2AA",
            "title_lines": ["YOGA", "PROGRESS", "JOURNAL"],
            "subtitle_lines": ["Track Your Practice", "Mind, Body & Spirit"],
            "title_size": 34,
        },
        {
            "folder": "budget-planner-couples",
            "trim": "8.5x11",
            "bg": "#0F0F2E",
            "accent": "#D4A843",
            "title_lines": ["BUDGET", "PLANNER", "FOR COUPLES"],
            "subtitle_lines": ["Plan Together, Grow Together", "Monthly Finance Tracker"],
            "title_size": 42,
        },
        {
            "folder": "zodiac-mandala-coloring",
            "trim": "8.5x11",
            "bg": "#1A0A2E",
            "accent": "#D4A843",
            "title_lines": ["ZODIAC", "MANDALA", "COLORING"],
            "subtitle_lines": ["Mystical Astrology Designs", "Relaxing Mandala Art for Adults"],
            "title_size": 42,
        },
        {
            "folder": "meal-prep-planner",
            "trim": "8.5x11",
            "bg": "#F5F5DC",
            "accent": "#228B22",
            "title_lines": ["MEAL PREP", "PLANNER"],
            "subtitle_lines": ["Plan, Shop, Cook, Repeat", "Weekly Meal Planning Made Simple"],
            "title_size": 46,
        },
    ]

    for data in COVER_DATA:
        folder = data["folder"]
        trim = data["trim"]
        bg_hex = data["bg"]
        accent_hex = data["accent"]

        # Find the interior PDF to count pages
        interior_pdf = None
        for _, t, pdf_name in BOOKS:
            if _ == folder:
                interior_pdf = BASE / folder / pdf_name
                break

        if interior_pdf and interior_pdf.exists():
            page_count = count_pages(interior_pdf)
        else:
            print(f"  WARNING: {folder} - interior PDF not found, estimating pages")
            page_count = 100

        # Calculate cover dimensions
        BLEED = 0.125  # inches
        spine_width = page_count * 0.002252  # white paper

        if trim == "8.5x11":
            trim_w, trim_h = 8.5, 11.0
        else:  # 6x9
            trim_w, trim_h = 6.0, 9.0

        cover_w_in = 2 * trim_w + spine_width + 2 * BLEED
        cover_h_in = trim_h + 2 * BLEED

        cover_w = cover_w_in * rl_inch
        cover_h = cover_h_in * rl_inch
        spine_w = spine_width * rl_inch
        bleed = BLEED * rl_inch

        # Region boundaries
        back_start = 0
        back_end = (trim_w + BLEED) * rl_inch
        spine_start = back_end
        spine_end = spine_start + spine_w
        front_start = spine_end
        front_end = cover_w

        # Centers
        back_cx = (back_start + back_end) / 2
        front_cx = (front_start + front_end) / 2
        spine_cx = (spine_start + spine_end) / 2

        # Output path
        cover_path = BASE / folder / "cover.pdf"

        # Also handle password-logbook's separate name
        if folder == "password-logbook":
            cover_path2 = BASE / folder / "Password_Logbook_Cover.pdf"

        print(f"\n  [{folder}] pages={page_count}, spine={spine_width:.3f}\", "
              f"cover={cover_w_in:.3f}\"x{cover_h_in:.3f}\"")

        c = canvas.Canvas(str(cover_path), pagesize=(cover_w, cover_h))

        # --- BACKGROUND ---
        bg = HexColor(bg_hex)
        accent = HexColor(accent_hex)
        c.setFillColor(bg)
        c.rect(0, 0, cover_w, cover_h, fill=1, stroke=0)

        # --- FRONT COVER (right side) ---
        br = brightness_of(bg_hex)
        title_color = black if br > 160 else white

        # Border on front
        front_margin = 0.5 * rl_inch
        c.setStrokeColor(accent)
        c.setLineWidth(2)
        c.rect(front_start + front_margin, front_margin,
               (front_end - front_start) - 2 * front_margin,
               cover_h - 2 * front_margin)

        # Title
        c.setFillColor(title_color)
        ts = data["title_size"]
        c.setFont("Helvetica-Bold", ts)
        ty = cover_h * 0.58
        for line in data["title_lines"]:
            c.drawCentredString(front_cx, ty, line)
            ty -= ts + 4

        # Decorative line
        c.setStrokeColor(accent)
        c.setLineWidth(2)
        c.line(front_cx - 60, ty + 2, front_cx + 60, ty + 2)

        # Subtitle
        c.setFont("Helvetica", 14 if trim == "8.5x11" else 12)
        c.setFillColor(accent)
        sy = ty - 16
        for line in data["subtitle_lines"]:
            c.drawCentredString(front_cx, sy, line)
            sy -= 18

        # Author on front
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(accent)
        c.drawCentredString(front_cx, bleed + 0.45 * rl_inch, "Deokgu Studio")

        # --- SPINE ---
        if page_count >= 79 and spine_width >= 0.15:
            c.saveState()
            c.setFillColor(title_color)
            # Spine text (rotated 90 degrees)
            spine_font_size = min(10, spine_w / rl_inch * 50)
            if spine_font_size >= 5:
                c.setFont("Helvetica-Bold", spine_font_size)
                # Vertical text along spine
                spine_text = " ".join(data["title_lines"])
                c.saveState()
                c.translate(spine_cx, cover_h / 2)
                c.rotate(90)
                c.drawCentredString(0, -spine_font_size / 3, spine_text)
                c.restoreState()

                # Author at bottom of spine
                if spine_font_size >= 6:
                    c.setFont("Helvetica", max(5, spine_font_size - 2))
                    c.setFillColor(accent)
                    c.saveState()
                    c.translate(spine_cx, bleed + 0.4 * rl_inch)
                    c.rotate(90)
                    c.drawCentredString(0, -spine_font_size / 4, "Deokgu Studio")
                    c.restoreState()
            c.restoreState()

        # --- BACK COVER ---
        # Simple back cover
        back_margin = 0.6 * rl_inch

        # Border on back
        c.setStrokeColor(accent)
        c.setLineWidth(1)
        c.rect(back_start + back_margin, back_margin,
               (back_end - back_start) - 2 * back_margin,
               cover_h - 2 * back_margin)

        # Book title on back (smaller)
        c.setFont("Helvetica-Bold", 16 if trim == "8.5x11" else 14)
        c.setFillColor(title_color)
        back_title = " ".join(data["title_lines"])
        c.drawCentredString(back_cx, cover_h * 0.82, back_title)

        # Decorative line
        c.setStrokeColor(accent)
        c.setLineWidth(1)
        c.line(back_cx - 50, cover_h * 0.80, back_cx + 50, cover_h * 0.80)

        # Features/description on back
        c.setFont("Helvetica", 10)
        c.setFillColor(title_color)
        features = data.get("features", data["subtitle_lines"])
        fy = cover_h * 0.72
        for feat in features:
            c.drawCentredString(back_cx, fy, feat)
            fy -= 16

        # Publisher on back
        c.setFont("Helvetica", 9)
        c.setFillColor(accent)
        c.drawCentredString(back_cx, bleed + 0.8 * rl_inch, "Deokgu Studio")
        c.drawCentredString(back_cx, bleed + 0.6 * rl_inch, "deokgu.studio")

        # Barcode area (leave blank rectangle at bottom-right of back)
        barcode_w = 2.0 * rl_inch
        barcode_h = 1.2 * rl_inch
        barcode_x = back_cx + 0.5 * rl_inch
        barcode_y = bleed + 0.3 * rl_inch
        c.setFillColor(white)
        c.rect(barcode_x, barcode_y, barcode_w, barcode_h, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#cccccc"))
        c.setLineWidth(0.5)
        c.rect(barcode_x, barcode_y, barcode_w, barcode_h, fill=0, stroke=1)
        c.setFillColor(HexColor("#999999"))
        c.setFont("Helvetica", 7)
        c.drawCentredString(barcode_x + barcode_w / 2, barcode_y + barcode_h / 2,
                           "ISBN Barcode Area")

        c.save()
        fsize = os.path.getsize(cover_path) / 1024
        print(f"    cover.pdf -> {fsize:.0f} KB ({cover_w_in:.2f}\" x {cover_h_in:.2f}\")")

        # For password-logbook, also copy to the legacy name
        if folder == "password-logbook":
            import shutil
            shutil.copy2(str(cover_path), str(cover_path2))
            print(f"    Also copied to {cover_path2.name}")


def verify_all():
    """Verify all generated PDFs."""
    print("\n" + "=" * 60)
    print("STEP 4: Verification")
    print("=" * 60)

    all_ok = True
    for folder, trim, pdf_name in BOOKS:
        interior = BASE / folder / pdf_name
        cover = BASE / folder / "cover.pdf"

        int_ok = interior.exists()
        cov_ok = cover.exists()

        if int_ok:
            pages = count_pages(interior)
            int_size = os.path.getsize(interior) / 1024
            int_status = f"OK ({pages}p, {int_size:.0f}KB)"
        else:
            int_status = "MISSING"
            all_ok = False

        if cov_ok:
            cov_size = os.path.getsize(cover) / 1024
            cov_status = f"OK ({cov_size:.0f}KB)"
        else:
            cov_status = "MISSING"
            all_ok = False

        print(f"  {folder:35s} Interior: {int_status:25s} Cover: {cov_status}")

    print()
    if all_ok:
        print("ALL 20 BOOKS: Interior + Cover generated successfully!")
    else:
        print("Some files are missing - check errors above.")


if __name__ == "__main__":
    fix_margins()
    regenerate_interiors()
    generate_full_wrap_covers()
    verify_all()
