r"""
build_etsy_csv.py - Generate Etsy bulk-import CSV from KDP listings + Notion templates + Saju Premium.

Sources:
  - D:\cheonmyeongdang\departments\ebook\projects\*\KDP_LISTING.md  (English-only)
  - D:\notion_templates_2026_05_global_v2\*\README.md (+ tags.txt, features.txt, price_usd.txt)
  - D:\saju_premium_pdf\README.md
  - cover assets per listing

Output:
  - listings_2026_05_05.csv  (Etsy bulk-import format)
  - images_manifest.csv      (per-listing image paths for upload)
  - skipped.txt              (Korean-only items skipped)
"""
import os, re, csv, json, sys, glob

ROOT_KDP   = r"D:\cheonmyeongdang\departments\ebook\projects"
ROOT_NOTION= r"D:\notion_templates_2026_05_global_v2"
SAJU_DIR   = r"D:\saju_premium_pdf"
OUT_DIR    = r"D:\cheonmyeongdang\departments\etsy"
IMG_OUT    = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_OUT, exist_ok=True)

ETSY_HEADER = [
    "Title", "Description", "Price", "Currency Code", "Quantity",
    "Tags", "Materials", "Section", "When Made", "Renewal Option", "Who Made", "Is Supply",
    "Image1", "Image2", "Image3", "Image4", "Image5", "Image6", "Image7", "Image8", "Image9", "Image10",
    "Variations", "SKU", "Production Partner", "Shipping",
    "Listing Type", "Category", "Digital File"
]

def has_korean(s: str) -> bool:
    return any('가' <= c <= '힯' for c in s or '')

def first_match(pattern, text, flags=0, group=1):
    m = re.search(pattern, text, flags)
    if m:
        try: return m.group(group).strip()
        except IndexError: return m.group(0).strip()
    return ""

def read_text(path):
    try:
        with open(path, encoding='utf-8') as f: return f.read()
    except Exception:
        return ""

def parse_kdp_listing(md_text: str) -> dict:
    """Parse KDP_LISTING.md; return {title, subtitle, description, keywords[], price_usd, paperback}"""
    out = {"title": "", "subtitle": "", "description": "", "keywords": [], "price_usd": None}

    # Title - try multiple patterns
    # Pattern 1: ### Title \n **....**
    t = first_match(r'###?\s*Title[^\n]*\n\s*\*\*(.+?)\*\*', md_text)
    if not t: t = first_match(r'-\s*\*\*Title\*\*\s*:\s*(.+?)$', md_text, re.M)
    if not t: t = first_match(r'##\s*Title[^\n]*\n([^\n#]+)', md_text)
    if not t:
        # First H1 stripped
        t = first_match(r'^#\s*[^\n]*?(?:KDP\s*Listing|등록\s*정보|—)?\s*[—\-]\s*(.+?)$', md_text, re.M)
    if not t:
        t = first_match(r'^#\s+(.+?)$', md_text, re.M)
    out["title"] = re.sub(r'^[📚\s]+|[\s—\-]+(?:KDP|등록|정보).*$', '', t).strip()

    # Description block (in code fence)
    desc = first_match(r'(?:Description[^\n]*\n)```\s*\n(.+?)\n```', md_text, re.S)
    if not desc:
        # Fallback: first paragraph after Description heading
        desc = first_match(r'###?\s*Description[^\n]*\n(.+?)(?=\n###?\s|\n##\s|$)', md_text, re.S)
    out["description"] = desc.strip() if desc else ""

    # Keywords
    kws = first_match(r'###?\s*Keywords?[^\n]*\n```\s*\n(.+?)\n```', md_text, re.S)
    if not kws:
        # Numbered/bulleted multi-line list
        block = first_match(r'###?\s*Keywords?[^\n]*\n((?:(?:\d+\.|-|\*)\s*[^\n]+\n?){2,})', md_text)
        if block: kws = block
    if not kws:
        kws = first_match(r'###?\s*Keywords?[^\n]*\n([^\n]+)', md_text)
    if kws:
        # split on commas or newlines, strip leading "1.", "-", "*", quotes
        parts = []
        for k in re.split(r'[,\n]', kws):
            k = k.strip()
            k = re.sub(r'^\d+\.\s*', '', k)  # "1. " prefix
            k = k.strip(' "\'-•*')
            if k: parts.append(k)
        out["keywords"] = parts[:13]

    # Price - look for $X.XX
    pp = first_match(r'(?:Paperback|paperback)[:\*\s]*\$\s*(\d+\.?\d*)', md_text)
    if not pp:
        # Look for ## Price section followed by $XX.XX
        block = first_match(r'##\s*Price[^\n]*\n(?:.|\n){0,200}', md_text)
        pp = first_match(r'\$\s*(\d+\.?\d*)', block) if block else ""
    if pp:
        try: out["price_usd"] = float(pp)
        except: pass

    return out

def english_etsy_title(t: str) -> str:
    """Etsy title max 140 chars, break at word boundary, no pipe chars."""
    t = re.sub(r'\s+', ' ', t).strip()
    t = t.replace('|', ' - ')
    if len(t) <= 140: return t
    # Truncate at last space before 140
    cut = t[:140]
    last_space = cut.rfind(' ')
    if last_space > 100:
        cut = cut[:last_space]
    # Strip trailing punctuation/dashes
    return cut.rstrip(' -,;:&')

def to_tags(keywords, fallback_topic="digital download"):
    """Etsy: max 13 tags, max 20 chars each, lowercase, no commas."""
    out = []
    for k in keywords:
        k = k.lower().strip()
        k = re.sub(r'[^a-z0-9 ]', '', k)
        k = re.sub(r'\s+', ' ', k).strip()
        if not k or len(k) > 20: continue
        if k in out: continue
        out.append(k)
        if len(out) >= 13: break
    # Pad with fallback
    pad = ["printable","digital download","instant download","pdf download","planner","journal","digital art","printable planner","minimalist","pdf","digital","aesthetic","download"]
    for p in pad:
        if len(out) >= 13: break
        if p not in out and len(p) <= 20: out.append(p)
    return out[:13]

def kdp_section(book_id: str) -> str:
    s = book_id.lower()
    if any(x in s for x in ["coloring","mandala","dot-marker","spot-difference"]): return "Printable Art"
    if any(x in s for x in ["planner","tracker","log","journal","notebook","diary","logbook"]): return "Printable Planner"
    if any(x in s for x in ["math","workbook","kids"]): return "Kids Printable"
    if any(x in s for x in ["fortune","saju","zodiac","mandala"]): return "Astrology Printable"
    return "Digital Download"

def kdp_price(book_id: str, parsed_price) -> float:
    if parsed_price and parsed_price > 0: return parsed_price
    s = book_id.lower()
    if "coloring" in s or "kids" in s or "math" in s: return 4.99
    if "ai-side-hustle" in s: return 9.99
    if "premium" in s: return 7.99
    if "logbook" in s or "log" in s or "tracker" in s or "journal" in s: return 5.99
    return 6.99

def cover_to_png(book_id: str) -> str:
    """Copy cover.pdf or .png to images dir; return PNG path or empty if missing."""
    src_dir = os.path.join(ROOT_KDP, book_id)
    # Look for any image first
    for ext in ('cover.png','cover.jpg','cover.jpeg'):
        p = os.path.join(src_dir, ext)
        if os.path.exists(p): return p
    # Look for any *.png or *.jpg in folder
    for f in os.listdir(src_dir) if os.path.isdir(src_dir) else []:
        if f.lower().endswith(('.png','.jpg','.jpeg')) and 'cover' in f.lower():
            return os.path.join(src_dir, f)
    # Fall back to cover.pdf path (Etsy accepts PDF preview but prefers PNG)
    p = os.path.join(src_dir, "cover.pdf")
    if os.path.exists(p): return p
    return ""

def collect_kdp_rows():
    rows, manifest, skipped = [], [], []
    if not os.path.isdir(ROOT_KDP):
        return rows, manifest, skipped
    for d in sorted(os.listdir(ROOT_KDP)):
        full = os.path.join(ROOT_KDP, d)
        if not os.path.isdir(full): continue
        listing = os.path.join(full, "KDP_LISTING.md")
        if not os.path.exists(listing): continue
        md = read_text(listing)
        parsed = parse_kdp_listing(md)
        title = english_etsy_title(parsed["title"])
        desc  = parsed["description"]
        if has_korean(title) or has_korean(desc):
            skipped.append(f"{d}: Korean content - skip for global Etsy")
            continue
        if not title or len(title) < 6:
            skipped.append(f"{d}: title too short / missing")
            continue
        # Compose desc with refund + delivery footer
        desc_full = (desc or title) + "\n\n---\n\nINSTANT DOWNLOAD\nAfter purchase, you'll receive a downloadable PDF immediately.\n\nFORMAT\n- High-quality printable PDF\n- US Letter (8.5 x 11) and A4 friendly\n- Print at home, at any print shop, or use digitally\n\nREFUND POLICY\nDigital downloads are non-refundable due to their instant nature. If you have any issues, message me and I'll make it right.\n\nCOPYRIGHT\nFor personal use only. Not for resale or redistribution.\n\nThank you for supporting an indie creator."
        tags = to_tags(parsed["keywords"], fallback_topic=d.replace('-',' '))
        cover = cover_to_png(d)
        manifest.append({"sku": d, "image1": cover, "image_count": 1 if cover else 0})
        row = {
            "Title": title,
            "Description": desc_full,
            "Price": f"{kdp_price(d, parsed['price_usd']):.2f}",
            "Currency Code": "USD",
            "Quantity": "999",
            "Tags": ",".join(tags),
            "Materials": "PDF,digital,printable",
            "Section": kdp_section(d),
            "When Made": "made_to_order",
            "Renewal Option": "automatic",
            "Who Made": "i_did",
            "Is Supply": "false",
            "Image1": cover,
            "Image2": "", "Image3": "", "Image4": "", "Image5": "",
            "Image6": "", "Image7": "", "Image8": "", "Image9": "", "Image10": "",
            "Variations": "",
            "SKU": f"KDP-{d.upper()}",
            "Production Partner": "",
            "Shipping": "Digital",
            "Listing Type": "download",
            "Category": "Craft Supplies & Tools > Patterns & How To > Patterns",
            "Digital File": os.path.join(full, f"{d.replace('-','_')}.pdf"),
        }
        rows.append(row)
    return rows, manifest, skipped

def collect_notion_rows():
    rows, manifest = [], []
    products = [
        ("ai-prompt-library-200", "AI Prompt Library 200 - 200 Production-Ready ChatGPT and Claude Prompts for Notion", 12.00),
        ("freelancer-client-toolkit", "Freelancer Client Toolkit - Notion Template for Solo Freelancers and Consultants", 15.00),
        ("habit-tracker-365", "Habit Tracker 365 - Daily Habit Notion Template with Streak Tracking", 7.00),
        ("budget-net-worth-tracker", "Budget and Net Worth Tracker - Personal Finance Notion Template", 9.00),
        ("weekly-aesthetic-planner", "Weekly Aesthetic Planner - Minimalist Notion Weekly Planning Template", 6.00),
    ]
    for slug, title, price in products:
        d = os.path.join(ROOT_NOTION, slug)
        if not os.path.isdir(d):
            continue
        readme = read_text(os.path.join(d, "README.md"))
        tags_txt = read_text(os.path.join(d, "tags.txt"))
        tags = [t.strip() for t in tags_txt.split(',') if t.strip()]
        tags = to_tags(tags)
        cover_jpg = os.path.join(ROOT_NOTION, "_covers", f"{slug}.jpg")
        if not os.path.exists(cover_jpg): cover_jpg = ""
        zip_file = os.path.join(ROOT_NOTION, "_zips", f"{slug}.zip")
        desc_full = readme + "\n\n---\n\nINSTANT DOWNLOAD\nAfter purchase, you'll receive a Notion-ready markdown file you can drag-and-drop into your workspace.\n\nWORKS WITH\n- Notion (Free + Paid)\n- ChatGPT, Claude, Gemini, Mistral\n- Desktop, Mobile, Web\n\nREFUND POLICY\n7-day money-back guarantee.\n\nThank you for supporting an indie creator."
        manifest.append({"sku": slug, "image1": cover_jpg, "image_count": 1 if cover_jpg else 0})
        row = {
            "Title": english_etsy_title(title),
            "Description": desc_full,
            "Price": f"{price:.2f}",
            "Currency Code": "USD",
            "Quantity": "999",
            "Tags": ",".join(tags),
            "Materials": "Notion,template,digital",
            "Section": "Notion Template",
            "When Made": "made_to_order",
            "Renewal Option": "automatic",
            "Who Made": "i_did",
            "Is Supply": "false",
            "Image1": cover_jpg,
            "Image2": "", "Image3": "", "Image4": "", "Image5": "",
            "Image6": "", "Image7": "", "Image8": "", "Image9": "", "Image10": "",
            "Variations": "",
            "SKU": f"NOTION-{slug.upper()}",
            "Production Partner": "",
            "Shipping": "Digital",
            "Listing Type": "download",
            "Category": "Paper & Party Supplies > Paper > Stationery > Planners & Calendars",
            "Digital File": zip_file,
        }
        rows.append(row)

    # Bundle
    bundle_zip = os.path.join(ROOT_NOTION, "_zips", "KUNSTUDIO_GLOBAL_BUNDLE_5pack.zip")
    bundle_cover = os.path.join(ROOT_NOTION, "_covers", "BUNDLE_global.jpg")
    if os.path.exists(bundle_zip):
        manifest.append({"sku": "BUNDLE-NOTION-5PACK", "image1": bundle_cover if os.path.exists(bundle_cover) else "", "image_count": 1})
        rows.append({
            "Title": english_etsy_title("Notion Operator Bundle - 5 Templates for Knowledge Work, Money, and Life - 30% Off"),
            "Description": "Five battle-tested Notion templates in one bundle: AI Prompt Library 200, Freelancer Client Toolkit, Habit Tracker 365, Budget and Net Worth Tracker, and Weekly Aesthetic Planner. Save 30% versus buying separately.\n\nWHAT YOU GET\n- AI Prompt Library 200 (200 prompts across 10 categories)\n- Freelancer Client Toolkit (proposals, invoicing, CRM)\n- Habit Tracker 365 (daily habit tracking with streaks)\n- Budget and Net Worth Tracker (personal finance dashboard)\n- Weekly Aesthetic Planner (minimalist weekly planning)\n\nINSTANT DOWNLOAD\nAfter purchase, you'll receive 5 Notion-ready files plus a quickstart guide.\n\nWORKS WITH\nNotion (Free and Paid). Desktop, Mobile, Web.\n\nREFUND POLICY\n7-day money-back guarantee.\n\nThank you for supporting an indie creator.",
            "Price": "35.00",
            "Currency Code": "USD",
            "Quantity": "999",
            "Tags": "notion bundle,notion template,productivity,ai prompts,habit tracker,budget tracker,freelancer,planner,digital download,knowledge work,instant download,notion pack,template bundle",
            "Materials": "Notion,template,bundle",
            "Section": "Notion Template",
            "When Made": "made_to_order",
            "Renewal Option": "automatic",
            "Who Made": "i_did",
            "Is Supply": "false",
            "Image1": bundle_cover if os.path.exists(bundle_cover) else "",
            "Image2": "", "Image3": "", "Image4": "", "Image5": "",
            "Image6": "", "Image7": "", "Image8": "", "Image9": "", "Image10": "",
            "Variations": "",
            "SKU": "NOTION-BUNDLE-5PACK",
            "Production Partner": "",
            "Shipping": "Digital",
            "Listing Type": "download",
            "Category": "Paper & Party Supplies > Paper > Stationery > Planners & Calendars",
            "Digital File": bundle_zip,
        })
    return rows, manifest

def collect_saju_row():
    rows, manifest = [], []
    readme = read_text(os.path.join(SAJU_DIR, "README.md"))
    cover_jpg = os.path.join(SAJU_DIR, "_cover", "saju_premium_cover.jpg")
    sample_pdf = os.path.join(SAJU_DIR, "output", "saju_SAMPLE.pdf")
    listing_zip = os.path.join(SAJU_DIR, "saju_premium_listing_pack.zip")
    if not readme: return rows, manifest
    desc_full = readme.replace("$21.99", "$21.99")  # keep
    manifest.append({"sku": "SAJU-PREMIUM-PDF", "image1": cover_jpg if os.path.exists(cover_jpg) else "", "image_count": 1})
    rows.append({
        "Title": english_etsy_title("Korean Saju Premium PDF Reading - Personalized BaZi Four Pillars of Destiny Report"),
        "Description": desc_full,
        "Price": "21.99",
        "Currency Code": "USD",
        "Quantity": "999",
        "Tags": "saju reading,bazi reading,four pillars,korean astrology,birth chart reading,personalized reading,astrology pdf,bazi report,day master,five elements,2026 forecast,asian astrology,instant download",
        "Materials": "PDF,personalized,digital",
        "Section": "Astrology Printable",
        "When Made": "made_to_order",
        "Renewal Option": "automatic",
        "Who Made": "i_did",
        "Is Supply": "false",
        "Image1": cover_jpg if os.path.exists(cover_jpg) else "",
        "Image2": sample_pdf if os.path.exists(sample_pdf) else "",
        "Image3": "", "Image4": "", "Image5": "",
        "Image6": "", "Image7": "", "Image8": "", "Image9": "", "Image10": "",
        "Variations": "",
        "SKU": "SAJU-PREMIUM-PDF",
        "Production Partner": "",
        "Shipping": "Digital",
        "Listing Type": "download",
        "Category": "Craft Supplies & Tools > Patterns & How To",
        "Digital File": listing_zip if os.path.exists(listing_zip) else "",
    })
    return rows, manifest

def main():
    all_rows, all_manifest, skipped = [], [], []

    kdp_rows, kdp_man, kdp_skip = collect_kdp_rows()
    all_rows += kdp_rows; all_manifest += kdp_man; skipped += kdp_skip
    notion_rows, notion_man = collect_notion_rows()
    all_rows += notion_rows; all_manifest += notion_man
    saju_rows, saju_man = collect_saju_row()
    all_rows += saju_rows; all_manifest += saju_man

    # Write CSV
    out_csv = os.path.join(OUT_DIR, "listings_2026_05_05.csv")
    with open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=ETSY_HEADER)
        w.writeheader()
        for r in all_rows:
            # Sanitize description: Etsy allows newlines but we strip carriage returns
            r["Description"] = r["Description"].replace('\r', '').strip()
            w.writerow(r)

    # Manifest
    out_mani = os.path.join(OUT_DIR, "images_manifest.csv")
    with open(out_mani, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(["SKU", "Image1_Path", "Image_Count", "Notes"])
        for m in all_manifest:
            note = "OK" if m["image_count"] >= 1 and m["image1"] else "MISSING - generate via Pollinations"
            w.writerow([m["sku"], m["image1"], m["image_count"], note])

    # Skipped
    out_skip = os.path.join(OUT_DIR, "skipped.txt")
    with open(out_skip, 'w', encoding='utf-8') as f:
        f.write("Items skipped (Korean content / missing assets):\n\n")
        for s in skipped: f.write(f"- {s}\n")

    print(f"OK: {len(all_rows)} listings written to {out_csv}")
    print(f"   Manifest: {out_mani}")
    print(f"   Skipped:  {len(skipped)} items -> {out_skip}")
    print(f"   KDP:    {len(kdp_rows)}")
    print(f"   Notion: {len(notion_rows)}")
    print(f"   Saju:   {len(saju_rows)}")

if __name__ == "__main__":
    main()
