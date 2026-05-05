#!/usr/bin/env python3
"""Prepend the user's 30s intro clip to all 25 K-Wisdom video bodies via ffmpeg.

Usage:
    python intro_merger.py --intro D:/KunStudio/intro/kwisdom_intro_master.mp4 \
                           --bodies D:/KunStudio/media/kwisdom/bodies/ \
                           --out D:/KunStudio/media/kwisdom/final/

Both intro and body should be 1080p (or both 720p) at the same fps. Re-encodes
with libx264 + aac so any source mismatch is normalized.

The schtask `KunStudio_KWisdom_Daily` (07:00) calls this per-day with a single
body file via the --single flag.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
META_PATH = HERE / "video_metadata_25.json"


def have_ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def merge(intro: Path, body: Path, out: Path) -> bool:
    """Re-encode intro+body into a single clean MP4."""
    if not intro.exists() or not body.exists():
        print(f"missing input: intro={intro.exists()} body={body.exists()}",
              file=sys.stderr)
        return False
    # Build a concat list and use ffmpeg concat demuxer with re-encode.
    list_path = out.parent / f"_concat_{out.stem}.txt"
    list_path.parent.mkdir(parents=True, exist_ok=True)
    list_path.write_text(
        f"file '{intro.as_posix()}'\nfile '{body.as_posix()}'\n",
        encoding="utf-8",
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return out.exists() and out.stat().st_size > 1000
    finally:
        try:
            list_path.unlink()
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intro", required=True, type=Path,
                    help="Path to the user's 30s intro master MP4")
    ap.add_argument("--bodies", type=Path,
                    help="Folder of 25 AI-generated body MP4s")
    ap.add_argument("--out", type=Path, required=True,
                    help="Output folder for final merged MP4s")
    ap.add_argument("--single", type=int,
                    help="Merge only one day (1-25); used by daily schtask")
    args = ap.parse_args()

    if not have_ffmpeg():
        print("ffmpeg not found in PATH", file=sys.stderr)
        return 2
    if not META_PATH.exists():
        print(f"missing {META_PATH}", file=sys.stderr)
        return 2

    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    videos = meta["videos"]
    if args.single:
        videos = [v for v in videos if v["day"] == args.single]

    args.out.mkdir(parents=True, exist_ok=True)
    ok = fail = skip = 0
    for v in videos:
        body_name = f"body_{v['day']:02d}.mp4"
        out_name = f"kwisdom_d{v['day']:02d}_final.mp4"
        body = (args.bodies / body_name) if args.bodies else None
        out = args.out / out_name

        if out.exists() and out.stat().st_size > 1000:
            print(f"SKIP (exists): {out_name}")
            skip += 1
            continue
        if not body or not body.exists():
            print(f"WAIT (no body yet): {body_name}")
            fail += 1
            continue
        print(f"MERGE day{v['day']:02d}: {v['title']}")
        if merge(args.intro, body, out):
            print(f"  OK: {out_name}")
            ok += 1
        else:
            print(f"  FAIL: {out_name}")
            fail += 1

    print(f"\nDONE ok={ok} fail={fail} skip={skip}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
