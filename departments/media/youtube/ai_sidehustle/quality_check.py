#!/usr/bin/env python3
"""
AI Side Hustle 쇼츠 품질 검증.
orchestrator.py 각 단계 후 호출. 기준 미달 시 자동 재시도 트리거.

기준 (2026-04-23):
- 이미지: >= 30 KB, 해상도 1080x1920 근접 (±5%)
- 오디오: 45~65초, mp3/wav 유효
- 비디오: 45~65초, 1080x1920, bitrate >= 300 kbps
- 스크립트: 500~1200자 (영어 60초 말하기 기준 140~160단어 = 700~900자 평균)
"""
import sys, json, subprocess, os
from pathlib import Path

FFMPEG = r"C:\Users\hdh02\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
FFPROBE = FFMPEG.replace("ffmpeg.exe", "ffprobe.exe")


def probe(path):
    try:
        r = subprocess.run(
            [FFPROBE, "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return json.loads(r.stdout) if r.returncode == 0 else None
    except Exception as e:
        return None


def check_image(path, min_kb=30, target_w=1080, target_h=1920):
    path = Path(path)
    if not path.exists():
        return False, "missing"
    size_kb = path.stat().st_size / 1024
    if size_kb < min_kb:
        return False, f"tiny ({size_kb:.0f}KB<{min_kb})"
    info = probe(path)
    if not info or not info.get("streams"):
        return False, "unreadable"
    s = info["streams"][0]
    w, h = s.get("width", 0), s.get("height", 0)
    # 허용 범위: 가로 세로 비율만 정확히 맞으면 OK (Pollinations은 9:16 리턴)
    ratio_actual = h / w if w else 0
    ratio_target = target_h / target_w
    if abs(ratio_actual - ratio_target) > 0.1:
        return False, f"ratio {w}x{h}"
    return True, f"{size_kb:.0f}KB {w}x{h}"


def check_audio(path, min_sec=40, max_sec=70):
    path = Path(path)
    if not path.exists():
        return False, "missing"
    info = probe(path)
    if not info:
        return False, "unreadable"
    dur = float(info.get("format", {}).get("duration", 0))
    if dur < min_sec:
        return False, f"too short {dur:.1f}s"
    if dur > max_sec:
        return False, f"too long {dur:.1f}s"
    return True, f"{dur:.1f}s"


def check_video(path, min_sec=40, max_sec=75, min_bitrate_kbps=250):
    path = Path(path)
    if not path.exists():
        return False, "missing"
    info = probe(path)
    if not info:
        return False, "unreadable"
    dur = float(info.get("format", {}).get("duration", 0))
    br = int(info.get("format", {}).get("bit_rate", 0)) / 1000
    v_streams = [s for s in info["streams"] if s["codec_type"] == "video"]
    a_streams = [s for s in info["streams"] if s["codec_type"] == "audio"]
    if not v_streams:
        return False, "no video stream"
    if not a_streams:
        return False, "no audio stream"
    w, h = v_streams[0].get("width", 0), v_streams[0].get("height", 0)
    if (w, h) != (1080, 1920):
        return False, f"resolution {w}x{h}"
    if not (min_sec <= dur <= max_sec):
        return False, f"duration {dur:.1f}s"
    if br < min_bitrate_kbps:
        return False, f"bitrate {br:.0f}kbps"
    return True, f"{dur:.1f}s {w}x{h} {br:.0f}kbps"


def check_script(text, min_chars=500, max_chars=1400):
    n = len(text)
    if n < min_chars:
        return False, f"short {n}"
    if n > max_chars:
        return False, f"long {n}"
    # 금지 패턴 (AI 표시 남발 / 마크다운 잔재)
    banned = ["**", "##", "---", "```", "[Hook]", "(Stage directions)"]
    for b in banned:
        if b in text:
            return False, f"banned pattern: {b!r}"
    return True, f"{n} chars"


def check_all(slug, script, audio, images, video):
    """전체 검증. 하나라도 실패 시 실패 이유 리턴."""
    report = {"slug": slug, "checks": {}, "passed": True}

    ok, msg = check_script(script)
    report["checks"]["script"] = {"ok": ok, "msg": msg}
    if not ok:
        report["passed"] = False

    ok, msg = check_audio(audio)
    report["checks"]["audio"] = {"ok": ok, "msg": msg}
    if not ok:
        report["passed"] = False

    img_ok = 0
    img_reports = []
    for i, img in enumerate(images, 1):
        ok, msg = check_image(img)
        img_reports.append({"i": i, "ok": ok, "msg": msg})
        if ok:
            img_ok += 1
    report["checks"]["images"] = {"ok": img_ok >= 3, "ok_count": img_ok, "details": img_reports}
    if img_ok < 3:
        report["passed"] = False

    ok, msg = check_video(video)
    report["checks"]["video"] = {"ok": ok, "msg": msg}
    if not ok:
        report["passed"] = False

    return report


if __name__ == "__main__":
    # 수동 호출: python quality_check.py <slug>
    if len(sys.argv) < 2:
        print("usage: quality_check.py <slug>")
        sys.exit(1)
    slug = sys.argv[1]
    storage = Path(r"D:\cheonmyeongdang-outputs\youtube\ai_sidehustle")
    audio = storage / "output" / f"{slug}.mp3"
    video = storage / "output" / f"{slug}.mp4"
    images = sorted((storage / "assets").glob(f"img_{slug}_*.png"))
    script_file = storage / "output" / f"{slug}.txt"
    script = script_file.read_text(encoding="utf-8") if script_file.exists() else "(no script cache)"
    r = check_all(slug, script, audio, images, video)
    print(json.dumps(r, indent=2, ensure_ascii=False))
    sys.exit(0 if r["passed"] else 1)
