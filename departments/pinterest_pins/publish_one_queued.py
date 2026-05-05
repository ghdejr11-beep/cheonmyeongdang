"""publish_one_queued.py — Daily helper that picks 1 queued pin from queue.json
and prints upload instructions. Marks status as 'published' after.

Usage:
    python publish_one_queued.py            # picks oldest queued, prints instructions
    python publish_one_queued.py --mark SLUG  # mark a slug as published

Designed to complement the existing KunStudio_Pinterest_Pins_Daily task. Run
manually each day, or wire into a separate schtask after testing.
"""
import sys, json, datetime, argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE_JSON = ROOT / "queue.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mark", help="Mark slug as published")
    ap.add_argument("--list", action="store_true", help="List remaining queued")
    args = ap.parse_args()

    q = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
    made = q.get("made", [])

    if args.list:
        queued = [x for x in made if x.get("status") == "queued"]
        print(f"Remaining queued: {len(queued)}")
        for x in queued[:10]:
            print(f"  {x['slug']}  ->  {x.get('destination_url','')}")
        return

    if args.mark:
        for x in made:
            if x.get("slug") == args.mark:
                x["status"] = "published"
                x["published_at"] = datetime.datetime.now().isoformat()
                QUEUE_JSON.write_text(
                    json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                print(f"OK marked {args.mark} as published")
                return
        print(f"NOT FOUND {args.mark}")
        return

    queued = [x for x in made if x.get("status") == "queued"]
    if not queued:
        print("No queued pins remaining.")
        return

    pin = queued[0]
    print("=" * 60)
    print(f"Pin to publish today ({len(queued)} remaining):")
    print("=" * 60)
    print(f"Title       : {pin.get('title','')}")
    print(f"Image       : {pin.get('image_path','')}")
    print(f"Destination : {pin.get('destination_url','')}")
    print()
    print("--- Pinterest description (copy-paste) ---")
    print(pin.get("description", ""))
    print()
    print("--- After uploading, run ---")
    print(f"   python publish_one_queued.py --mark {pin['slug']}")
    print()


if __name__ == "__main__":
    main()
