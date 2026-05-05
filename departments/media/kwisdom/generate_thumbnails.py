#!/usr/bin/env python3
"""K-Wisdom 25 thumbnail generator via Pollinations Flux (free, no API key).

Reads `video_metadata_25.json` and downloads 1280x720 thumbnails to `thumbnails/`.
Idempotent (skips existing). Parallel (8 workers) with retry-once on timeout.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
META_PATH = HERE / "video_metadata_25.json"
OUT_DIR = HERE / "thumbnails"
OUT_DIR.mkdir(exist_ok=True)

BASE = "https://image.pollinations.ai/prompt/"
TIMEOUT_SEC = 60
USER_AGENT = "Mozilla/5.0 KunStudio-K-Wisdom-Thumbnail/1.0"
MAX_WORKERS = 8


def fetch_once(prompt: str, out_path: Path, seed: int) -> tuple[bool, str]:
    enc = urllib.parse.quote(prompt[:550])
    url = (
        f"{BASE}{enc}?width=1280&height=720&model=flux&nologo=true&seed={seed}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        data = resp.read()
    if len(data) < 2000:
        return False, f"tiny ({len(data)}B)"
    out_path.write_bytes(data)
    return True, f"{len(data)//1024}KB"


def fetch(v: dict) -> tuple[int, str, bool, str]:
    name = v["thumbnail_file"]
    out = OUT_DIR / name
    if out.exists() and out.stat().st_size > 1000:
        return v["day"], name, True, "skip-exists"
    prompt = v["thumbnail_prompt"]
    seed = 1000 + int(v["day"])
    # Try with primary seed; if fail, retry with a perturbed seed once.
    for attempt, s in enumerate([seed, seed + 17000], start=1):
        try:
            ok, info = fetch_once(prompt, out, s)
            if ok:
                return v["day"], name, True, f"a{attempt} {info}"
        except Exception as exc:
            info = str(exc)[:80]
            if attempt == 2:
                return v["day"], name, False, f"fail2 {info}"
            time.sleep(3)
    return v["day"], name, False, "exhausted"


def main() -> int:
    if not META_PATH.exists():
        print(f"missing {META_PATH}", file=sys.stderr)
        return 2
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    videos = meta["videos"]

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch, v): v for v in videos}
        for fut in as_completed(futures):
            day, name, ok, info = fut.result()
            mark = "OK " if ok else "FAIL"
            print(f"[{mark}] day{day:02d} {name} ({info})", flush=True)
            results.append((day, name, ok, info))

    ok = sum(1 for _, _, b, _ in results if b)
    fail = len(results) - ok
    print(f"\nDONE: ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
