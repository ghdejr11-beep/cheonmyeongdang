# Etsy Bulk Listing - 40 Digital Products (2026-05-05)

40 listings ready for Etsy bulk import: 33 KDP-derived English digital downloads + 6 Notion templates (5 individual + 1 bundle) + 1 Saju Premium PDF.

## Files

| File | Purpose |
|---|---|
| `listings_2026_05_05.csv` | 40-row Etsy bulk-import CSV (UTF-8 BOM, Title/Description/Price/Tags/Image1/SKU/Digital File) |
| `images_manifest.csv` | SKU -> primary cover image mapping (40 rows, all OK) |
| `cover_generated/*.png` | 5 covers auto-generated via Pollinations Flux for listings missing originals |
| `skipped.txt` | 3 Korean-only KDP titles excluded (ai-prompt-workbook, fortune-notebook, saju-diary) |
| `build_etsy_csv.py` | Regenerator if any source listing changes |
| `generate_missing_covers.py` | Pollinations cover generator for any future missing assets |

## Listing breakdown

| Source | Count | Price range | SKU prefix |
|---|---:|---|---|
| KDP English ebook (printable PDF interior) | 33 | $4.99 - $14.99 | `KDP-*` |
| Notion templates (individual) | 5 | $6.00 - $15.00 | `NOTION-*` |
| Notion templates (5-pack bundle) | 1 | $35.00 | `NOTION-BUNDLE-5PACK` |
| Saju Premium personalized PDF | 1 | $21.99 | `SAJU-PREMIUM-PDF` |
| **TOTAL** | **40** | | |

Etsy listing fees: 40 x $0.20 = **$8.00** (vs. estimated $6.60 for 33).

## Step 1 - Etsy seller account (user action, ~15 min)

1. Open https://www.etsy.com/sell - "Get Started"
2. Email: `ghdejr11@gmail.com`
3. Shop name: `KunstudioStudio` or `DeokguStudio` (4-20 chars, English+digits, no spaces)
4. Currency: **USD** (global pricing). Shop language: **English**.
5. Country/region: **South Korea**
6. Sales tax: skip for digital downloads (Etsy auto-collects VAT/GST in EU/UK/AU/etc.)
7. Stock photo: skip ("I'll add later")
8. Set up billing - **Etsy Payments not available in Korea** -> use **Payoneer**:
   - During onboarding choose "Connect Payoneer"
   - Payoneer business account: sign up at https://www.payoneer.com with business number `552-59-00848`
   - Payouts in USD to your Payoneer USD receiving account, then convert to KRW via Payoneer or transfer to KEB Hana / Shinhan USD account.
9. Verify identity (passport scan + business registration certificate `552-59-00848`)
10. Skip the "first listing" walkthrough - we will use bulk import

## Step 2 - CSV bulk upload (user action, ~5 min)

Etsy does **not** offer a public self-serve CSV bulk import for new shops. Two paths:

### Path A - eRank / Vela / Marmalead (recommended)
1. Sign up free at https://e-rank.com or https://www.getvela.com (Vela has free CSV import)
2. Connect your Etsy shop (OAuth)
3. In Vela: **Listings -> Import CSV**, upload `listings_2026_05_05.csv`
4. Map columns (Title -> Title, Description -> Description, etc. - the header names already match Vela's expected schema)
5. Bulk-attach cover images: Vela's image picker accepts the local paths in `images_manifest.csv` (drag-drop the `cover_generated/` folder + each KDP project's cover.pdf rasterized)
6. Bulk-attach digital files (the `Digital File` column points at each PDF / ZIP)
7. Click "Push to Etsy" - all 40 listings go live as drafts; review and publish in batches

### Path B - Etsy API (advanced, no UI needed)
- Apply for an Etsy API key: https://www.etsy.com/developers/register
- Use the `createListing` endpoint with the CSV rows
- Sample script can be added on request - currently the CSV format above already mirrors the API field names

### Path C - Manual paste (fallback if eRank/Vela unavailable)
- Open each CSV row, copy Title/Description/Tags/Price into Etsy's listing form
- Upload Image1 from `images_manifest.csv` and Digital File from the `Digital File` column
- Estimated 3-5 min per listing x 40 = 2-3 hours one-time

## Step 3 - Post-launch checklist

- [ ] Set shop policies: 7-day refund for digital downloads (no physical returns - Etsy auto-disables for digital)
- [ ] Set shop announcement: "All products are instant digital downloads. PDFs delivered immediately."
- [ ] Add 4-5 FAQ items: "Is this a printable file?" / "Can I print at home?" / "Will this work on iPad?" / "Refund policy?"
- [ ] Connect Etsy Ads ($1/day budget for first 14 days = $14 -> only if first 3 sales already happened, otherwise wait)
- [ ] Cross-link from Gumroad / weekly newsletter / Pinterest pins
- [ ] Add `etsy.com/shop/<your-shop>` to all product CTAs across Notion landing pages

## First sale ETA

- Day 0-3: Etsy SEO indexing (titles + tags surface in search)
- Day 3-7: First impressions ramp (Etsy "new shop" boost is real, ~50-200 free impressions/day)
- Day 7-21: First organic sale typical for digital download shops with 30+ listings
- Day 30: 10-30 sales target if pricing $5-$15 sweet spot ($150-$450 gross)
- Etsy fees: 6.5% transaction + $0.20 per listing renewal (auto-renew every 4 months)
- Net per $9.99 sale ~ $9.20 after Etsy fees, ~$8.85 after Payoneer 1% USD->KRW

## Image quality notes

- Etsy minimum 2000x2000px recommended (we use 1280x1280 for Pollinations-generated, 800x1200+ for KDP cover.pdf rasterized)
- For best CTR, replace any cover.pdf with PNG at 2000x2000 over time. Use Canva or Photoshop.
- 5 Pollinations-generated covers are stylistically consistent (minimalist book cover aesthetic) but indie-quality - swap with paid Canva/Midjourney covers as revenue allows.

## Source provenance

| SKU prefix | Source folder |
|---|---|
| `KDP-*` | `cheonmyeongdang/departments/ebook/projects/<id>/` |
| `NOTION-*` | `D:\notion_templates_2026_05_global_v2\<slug>\` |
| `SAJU-PREMIUM-PDF` | `D:\saju_premium_pdf\` |

## Regeneration

If any KDP_LISTING.md changes or new product added:

```
cd D:\cheonmyeongdang\departments\etsy
python build_etsy_csv.py
python generate_missing_covers.py
```

CSV is overwritten in place. Re-upload to Vela / Etsy API.

## Compliance

- All copy is **100% English** (3 Korean-only KDP titles auto-skipped)
- No third-party brand names (Samsung / BTS / specific celebrities) - generic categories only
- Per-listing AI disclosure inherited from source README / KDP listing
- 7-day refund policy stated in description (matches Etsy digital-download standard)
- Personal data (real name, phone) absent from all listings (`Deokgu Studio` brand only)
