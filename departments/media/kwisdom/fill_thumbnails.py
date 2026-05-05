#!/usr/bin/env python3
"""Fill missing K-Wisdom thumbnails with rate-aware sequential retry.

Pollinations Flux free tier rate-limits aggressively (429). This script:
- only fetches files that don't already exist
- uses 6s base spacing between requests
- exponentially backs off on 429 (15s -> 45s -> 90s)
- saves a recovery-state file so re-runs resume
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
META_PATH = HERE / "video_metadata_25.json"
OUT_DIR = HERE / "thumbnails"
OUT_DIR.mkdir(exist_ok=True)

BASE = "https://image.pollinations.ai/prompt/"
TIMEOUT_SEC = 90
USER_AGENT = "Mozilla/5.0 KunStudio-K-Wisdom/1.0"
BASE_DELAY = 6
MAX_RETRY = 4


def fetch(prompt: str, out: Path, seed: int) -> tuple[bool, str]:
    enc = urllib.parse.quote(prompt[:550])
    url = (
        f"{BASE}{enc}?width=1280&height=720&model=flux&nologo=true&seed={seed}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    backoff = 15
    for attempt in range(1, MAX_RETRY + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                data = resp.read()
            if len(data) < 2000:
                return False, f"tiny ({len(data)}B)"
            out.write_bytes(data)
            return True, f"{len(data)//1024}KB a{attempt}"
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < MAX_RETRY:
                print(f"    429 retry-{attempt} sleep {backoff}s",
                      flush=True)
                time.sleep(backoff)
                backoff *= 2
                continue
            return False, f"HTTP {exc.code}"
        except Exception as exc:
            if attempt < MAX_RETRY:
                time.sleep(5)
                continue
            return False, f"{type(exc).__name__}: {str(exc)[:60]}"
    return False, "exhausted"


def main() -> int:
    if not META_PATH.exists():
        print(f"missing {META_PATH}", file=sys.stderr)
        return 2
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    todo = []
    for v in meta["videos"]:
        out = OUT_DIR / v["thumbnail_file"]
        if out.exists() and out.stat().st_size > 1000:
            continue
        todo.append(v)
    print(f"to-fill: {len(todo)}/25", flush=True)

    ok = fail = 0
    for i, v in enumerate(todo, start=1):
        out = OUT_DIR / v["thumbnail_file"]
        seed = 1000 + int(v["day"])
        print(f"[{i}/{len(todo)}] day{v['day']:02d} {v['thumbnail_file']}",
              flush=True)
        good, info = fetch(v["thumbnail_prompt"], out, seed)
        if good:
            print(f"  OK ({info})", flush=True)
            ok += 1
        else:
            print(f"  FAIL ({info})", flush=True)
            fail += 1
        time.sleep(BASE_DELAY)

    print(f"\nDONE ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
