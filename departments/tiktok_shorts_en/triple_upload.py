"""triple_upload — TikTok 쇼츠 영상 1편 → TikTok + IG Reels + YT Shorts 동시 게시.

기존 tiktok_shorts_en/generate.py가 만든 mp4 → upload_post_client로 3채널 동시 배포.
ROI: 1편 만들고 3채널 노출 = 3배 viral 확률.
스케줄: 매일 13:30 schtask (10:00에 영상 만든 후 03:30 후 게시).
"""
import os
import sys
import json
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "media" / "src"))
from upload_post_client import post_video

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "queue.json"
TRIPLE_LOG = ROOT / "logs" / f"triple_{datetime.date.today()}.log"
TRIPLE_DONE = ROOT / "triple_done.json"
TRIPLE_LOG.parent.mkdir(exist_ok=True)


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with TRIPLE_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_done():
    if TRIPLE_DONE.exists():
        return json.loads(TRIPLE_DONE.read_text(encoding="utf-8"))
    return {"posted": []}


def main():
    if not QUEUE.exists():
        sys.exit("[ERR] tiktok queue.json missing")
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    made = q.get("made", [])
    if not made:
        log("no shorts to triple-post")
        return

    done = load_done()
    posted_kws = {x["kw"] for x in done.get("posted", [])}
    candidates = [m for m in made if m["kw"] not in posted_kws]
    if not candidates:
        log("all shorts already triple-posted")
        return

    item = candidates[0]
    kw = item["kw"]
    title = item["title"]
    file_name = item["file"]
    video_path = Path(r"D:\kunstudio-outputs\tiktok_en") / file_name
    if not video_path.exists():
        log(f"[ERR] video not found: {video_path}")
        return

    log(f"=== {file_name} ===")
    log(f"  title: {title}")

    # 3 채널 매핑 — 'kunstudio' 프로필 = TikTok + IG + Threads + FB + X
    # YT Shorts는 별도 채널 (K-Wisdom)
    description_short = f"Korean culture insight on {kw}. Full guide → kunstudio.hashnode.dev"

    results = {}

    # 1) TikTok + IG Reels + Threads + FB (kunstudio 프로필)
    try:
        r1 = post_video(
            video_path=str(video_path),
            user="kunstudio",
            platforms=["tiktok", "instagram", "threads", "facebook"],
            title=title[:80],
            description=description_short,
        )
        log(f"  kunstudio multi: {str(r1)[:120]}")
        results["kunstudio_multi"] = r1
    except Exception as e:
        log(f"  kunstudio FAIL: {type(e).__name__}: {str(e)[:80]}")
        results["kunstudio_multi"] = {"err": str(e)[:200]}

    # 2) YT Shorts via K-Wisdom 채널
    # whisper_atlas_yt_api_uploader.py 사용 (직접 YT Data API)
    try:
        import subprocess
        proc = subprocess.run(
            [
                "python",
                r"D:\scripts\whisper_atlas_yt_api_uploader.py",
                "--video", str(video_path),
                "--title", f"{title} #shorts",
                "--description", description_short,
            ],
            capture_output=True, encoding="utf-8", errors="ignore", timeout=300,
            env={**os.environ, "KS_YT_TOKEN_PATH": r"D:\cheonmyeongdang\.secrets_yt_upload_kwisdom.json"},
        )
        ok = "[OK] video_id=" in (proc.stdout or "")
        log(f"  yt_shorts: ok={ok}")
        if proc.stderr:
            log(f"    stderr: {proc.stderr[:200]}")
        results["yt_shorts"] = {"ok": ok, "stdout": (proc.stdout or "")[-300:]}
    except Exception as e:
        log(f"  YT FAIL: {type(e).__name__}: {str(e)[:80]}")
        results["yt_shorts"] = {"err": str(e)[:200]}

    done["posted"].append({
        "kw": kw, "file": file_name, "title": title,
        "posted_at": datetime.datetime.now().isoformat(),
        "results": results,
    })
    TRIPLE_DONE.write_text(json.dumps(done, ensure_ascii=False, indent=2), encoding="utf-8")
    log("[DONE]")


if __name__ == "__main__":
    main()
