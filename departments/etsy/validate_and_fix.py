# -*- coding: utf-8 -*-
"""
Etsy listings validator + auto-fixer for listings_2026_05_05.csv.

Rules enforced (per Etsy 2026 policy + SEO best-practice):
  - Title       : 1-140 chars (Etsy hard limit)
  - Description : >= 160 chars (SEO minimum)
  - Tags        : exactly 13 (Etsy recommended max for digital)
  - Price       : 5.00 - 50.00 USD (digital sweet-spot)
  - Image1      : path must exist on disk

Auto-fixes applied:
  - Title  > 140 -> truncate at last word boundary <= 137 + "..."
  - Tags   > 13  -> keep first 13
  - Tags   < 13  -> pad with safe filler tags from category bank
  - Price  > 50  -> 49.99 ; Price < 5 -> 5.99
  - Description < 160 -> append a generic SEO suffix paragraph

Anything that cannot be auto-fixed (missing image, etc.) -> logged in report.
"""

import csv
import os
import sys
import re
from pathlib import Path

CSV_PATH = Path(__file__).parent / 'listings_2026_05_05.csv'
REPORT_PATH = Path(__file__).parent / 'listings_validation_report.md'

MIN_DESC = 160
MAX_TITLE = 140
TARGET_TAGS = 13
MIN_PRICE = 5.0
MAX_PRICE = 50.0

FILLER_TAGS = [
    'instant download', 'printable pdf', 'digital download',
    'digital planner', 'home printable', 'pdf template',
    'minimalist', 'aesthetic', 'a4 letter', 'self care',
    'productivity', 'organization', 'gift idea',
]

GENERIC_SEO_SUFFIX = (
    "\n\nWHAT YOU GET:\n"
    "- High-resolution PDF (US Letter + A4 sizes)\n"
    "- Print at home or send to your favorite print shop\n"
    "- Instant digital download right after purchase\n"
    "- For personal use; please do not resell the file\n\n"
    "Need a custom version? Send a message - we usually reply within 24 hours."
)


def truncate_title(title: str) -> str:
    if len(title) <= MAX_TITLE:
        return title
    cut = title[:137]
    # cut at last space
    if ' ' in cut:
        cut = cut[:cut.rfind(' ')]
    return cut + '...'


def fix_tags(tags_raw: str) -> str:
    tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
    if len(tags) > TARGET_TAGS:
        tags = tags[:TARGET_TAGS]
    elif len(tags) < TARGET_TAGS:
        existing = {t.lower() for t in tags}
        for f in FILLER_TAGS:
            if len(tags) >= TARGET_TAGS:
                break
            if f.lower() not in existing:
                tags.append(f)
                existing.add(f.lower())
    # ensure each tag <= 20 chars (Etsy rule)
    tags = [t[:20] for t in tags]
    return ', '.join(tags)


def fix_price(price_raw: str) -> str:
    try:
        p = float(price_raw)
    except Exception:
        return '9.99'
    if p < MIN_PRICE:
        return '5.99'
    if p > MAX_PRICE:
        return '49.99'
    return f'{p:.2f}'


def fix_description(desc: str) -> str:
    if len(desc) >= MIN_DESC:
        return desc
    return desc + GENERIC_SEO_SUFFIX


def main():
    with open(CSV_PATH, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    report_lines = ["# Etsy Listings Validation Report", ""]
    report_lines.append(f"Source: `{CSV_PATH.name}`")
    report_lines.append(f"Total listings: **{len(rows)}**")
    report_lines.append("")
    report_lines.append("## Auto-fixes applied")
    report_lines.append("")

    fix_counter = {
        'title_truncated': 0,
        'tags_padded': 0,
        'tags_trimmed': 0,
        'price_clamped': 0,
        'desc_extended': 0,
        'image_missing': 0,
    }

    for idx, r in enumerate(rows, start=1):
        title_key = 'Title' if 'Title' in r else list(r.keys())[0]
        title = r[title_key] or ''
        desc = r.get('Description', '') or ''
        tags = r.get('Tags', '') or ''
        price = r.get('Price', '') or ''
        img1 = r.get('Image1', '') or ''

        line_changes = []

        # Title
        if len(title) > MAX_TITLE:
            new_title = truncate_title(title)
            r[title_key] = new_title
            fix_counter['title_truncated'] += 1
            line_changes.append(f"title {len(title)}c -> {len(new_title)}c (truncated to fit Etsy 140 limit)")

        # Tags
        tag_count = len([t for t in tags.split(',') if t.strip()])
        if tag_count != TARGET_TAGS:
            new_tags = fix_tags(tags)
            r['Tags'] = new_tags
            new_count = len([t for t in new_tags.split(',') if t.strip()])
            if tag_count > TARGET_TAGS:
                fix_counter['tags_trimmed'] += 1
                line_changes.append(f"tags {tag_count} -> {new_count} (trimmed to Etsy max)")
            else:
                fix_counter['tags_padded'] += 1
                line_changes.append(f"tags {tag_count} -> {new_count} (padded with SEO fillers)")

        # Price
        try:
            p = float(price)
            if p < MIN_PRICE or p > MAX_PRICE:
                new_price = fix_price(price)
                r['Price'] = new_price
                fix_counter['price_clamped'] += 1
                line_changes.append(f"price ${p:.2f} -> ${new_price} (clamped to $5-$50 digital range)")
        except Exception:
            r['Price'] = '9.99'
            fix_counter['price_clamped'] += 1
            line_changes.append(f"price '{price}' -> $9.99 (invalid value)")

        # Description
        if len(desc) < MIN_DESC:
            new_desc = fix_description(desc)
            r['Description'] = new_desc
            fix_counter['desc_extended'] += 1
            line_changes.append(f"description {len(desc)}c -> {len(new_desc)}c (SEO minimum 160c)")

        # Image existence (no auto-fix, just report)
        img_status = 'OK'
        if img1:
            if not os.path.exists(img1):
                img_status = 'MISSING'
                fix_counter['image_missing'] += 1
                line_changes.append(f"WARNING image1 missing: {img1}")
        else:
            img_status = 'EMPTY'
            fix_counter['image_missing'] += 1
            line_changes.append("WARNING image1 path empty")

        if line_changes:
            short_title = (r[title_key][:60] + '...') if len(r[title_key]) > 60 else r[title_key]
            report_lines.append(f"### #{idx}: {short_title}")
            for c in line_changes:
                report_lines.append(f"- {c}")
            report_lines.append("")

    # Save fixed CSV
    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append(f"- Titles truncated      : **{fix_counter['title_truncated']}**")
    report_lines.append(f"- Tags trimmed to 13    : **{fix_counter['tags_trimmed']}**")
    report_lines.append(f"- Tags padded to 13     : **{fix_counter['tags_padded']}**")
    report_lines.append(f"- Prices clamped        : **{fix_counter['price_clamped']}**")
    report_lines.append(f"- Descriptions extended : **{fix_counter['desc_extended']}**")
    report_lines.append(f"- Image1 missing/empty  : **{fix_counter['image_missing']}**")
    report_lines.append("")
    report_lines.append("CSV file updated in place. Backup recommended via git history.")

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"Validation complete. Report -> {REPORT_PATH}")
    for k, v in fix_counter.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
