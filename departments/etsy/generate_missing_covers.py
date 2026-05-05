r"""
generate_missing_covers.py - Generate missing cover images via Pollinations Flux (free, no API key).
Reads images_manifest.csv, finds rows with image_count=0, generates 1280x1280 PNG covers,
writes them under cover_generated\ and updates the manifest + listings CSV in place.
"""
import os, csv, urllib.parse, urllib.request, time

OUT_DIR = r"C:\Users\hdh02\Desktop\cheonmyeongdang\departments\etsy"
MANIFEST = os.path.join(OUT_DIR, "images_manifest.csv")
LISTINGS = os.path.join(OUT_DIR, "listings_2026_05_05.csv")
COVER_DIR = os.path.join(OUT_DIR, "cover_generated")
os.makedirs(COVER_DIR, exist_ok=True)

POLLI = "https://image.pollinations.ai/prompt/"

PROMPTS = {
    "bird-watching-journal": "minimalist book cover, bird watching journal, soft sage green and cream colors, hand-drawn songbird illustration, rustic typography, vintage naturalist field guide aesthetic, clean composition, indie publishing, square 1280x1280",
    "mileage-log-book":      "minimalist book cover, mileage log book for taxes, navy blue and gold accent, vector car steering wheel icon, bold serif title, professional financial planner aesthetic, clean composition, square 1280x1280",
    "mileage-log-rideshare": "minimalist book cover, rideshare driver mileage tracker, navy blue and bright yellow, vector car icon, bold sans-serif title, modern gig economy aesthetic, clean composition, square 1280x1280",
    "pelvic-floor-recovery-journal": "minimalist book cover, postpartum pelvic floor recovery journal, soft pink and warm beige, abstract feminine wellness illustration, calming typography, motherhood self-care aesthetic, clean composition, square 1280x1280",
    "sourdough-baking-journal": "minimalist book cover, sourdough baking journal, warm cream and toasted brown colors, hand-drawn rustic bread loaf illustration, artisan bakery typography, cozy farmhouse aesthetic, clean composition, square 1280x1280",
}

def fetch(prompt: str, dest: str):
    qs = urllib.parse.quote(prompt)
    url = f"{POLLI}{qs}?width=1280&height=1280&nologo=true&model=flux"
    print(f"  fetch -> {dest}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, 'wb') as out:
        out.write(r.read())

def main():
    with open(MANIFEST, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    updated = []
    for row in rows:
        sku = row["SKU"]
        if row["Image_Count"] == "0" and sku in PROMPTS:
            dest = os.path.join(COVER_DIR, f"{sku}.png")
            if not os.path.exists(dest):
                try:
                    fetch(PROMPTS[sku], dest)
                    time.sleep(2)
                except Exception as e:
                    print(f"  FAIL {sku}: {e}")
                    updated.append(row)
                    continue
            row["Image1_Path"] = dest
            row["Image_Count"] = "1"
            row["Notes"] = "OK (generated via Pollinations Flux)"
        updated.append(row)

    # Write manifest
    with open(MANIFEST, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=["SKU","Image1_Path","Image_Count","Notes"])
        w.writeheader()
        w.writerows(updated)

    # Patch listings CSV: replace Image1 cell where blank for matching SKU
    with open(LISTINGS, encoding='utf-8-sig') as f:
        listings = list(csv.DictReader(f))

    sku_to_img = {r["SKU"]: r["Image1_Path"] for r in updated if r["Image1_Path"]}
    for row in listings:
        # Listing SKU is "KDP-<id>" but manifest SKU is "<id>"
        candidates = [row["SKU"], row["SKU"].replace("KDP-","").lower(), row["SKU"].replace("NOTION-","").lower()]
        for c in candidates:
            if c in sku_to_img and not row.get("Image1"):
                row["Image1"] = sku_to_img[c]
                break

    fields = list(listings[0].keys())
    with open(LISTINGS, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(listings)
    print(f"OK: regenerated {sum(1 for r in updated if 'generated' in (r.get('Notes') or ''))} covers")

if __name__ == "__main__":
    main()
