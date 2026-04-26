"""
BGM 10시간 유튜브 영상 자동 파이프라인

흐름:
  1. ElevenLabs Music으로 최대 22분 BGM 생성
  2. ffmpeg로 10시간 루프 MP3 제작
  3. 다크 앰비언트 배경 + 텍스트 오버레이로 MP4 제작
  4. (선택) YouTube 업로드

사용:
  python bgm_pipeline.py --topic sleep --title "Deep Sleep 528Hz" --upload
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path

# .secrets 로드
_ROOT = Path(__file__).parents[5]
_SECRETS = _ROOT / ".secrets"
if _SECRETS.exists():
    for _line in _SECRETS.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

from elevenlabs_music import generate_music, ElevenLabsError
from topics import TOPICS, topic_for_today

OUTPUT_DIR = Path("D:/documents/쿤스튜디오/bgm_output")

# 장르별 배경색 (hex) — 다크 앰비언트
GENRE_COLORS = {
    "sleep":      "0x050510",
    "meditation": "0x050a05",
    "buddhist":   "0x0a0800",
    "focus":      "0x05050a",
    "wealth":     "0x0a0800",
    "healing":    "0x05080a",
}


def _ffmpeg(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["ffmpeg", "-y", *args], capture_output=True, text=True, check=check)


def make_loop(src: Path, dest: Path, hours: float = 10) -> Path:
    """MP3를 N시간 루프로 확장"""
    total_sec = int(hours * 3600)
    dest.parent.mkdir(parents=True, exist_ok=True)
    _ffmpeg(
        "-stream_loop", "-1",
        "-i", str(src),
        "-t", str(total_sec),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(dest),
    )
    return dest


def make_video(audio: Path, dest: Path, title_text: str, genre: str = "sleep") -> Path:
    """10시간 오디오 + 다크 배경 → MP4"""
    color = GENRE_COLORS.get(genre, "0x050510")
    dest.parent.mkdir(parents=True, exist_ok=True)

    # 배경: 단색 + 미묘한 vignette
    vf = (
        f"color=c={color}:size=1920x1080:rate=1,"
        "vignette=PI/4"
    )

    _ffmpeg(
        "-f", "lavfi", "-i", vf,
        "-i", str(audio),
        "-shortest",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "35",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(dest),
        check=True,
    )
    return dest


def run(topic_name: str | None = None, upload: bool = False) -> None:
    from datetime import datetime

    # 토픽 선택
    if topic_name:
        matches = [t for t in TOPICS if t.genre == topic_name]
        topic = matches[0] if matches else topic_for_today(datetime.now().strftime("%A"))
    else:
        topic = topic_for_today(datetime.now().strftime("%A"))

    slug = topic.genre + "_" + datetime.now().strftime("%Y%m%d")
    work_dir = OUTPUT_DIR / slug
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. BGM 생성 (최대 22분)
    raw_mp3 = work_dir / "raw.mp3"
    if not raw_mp3.exists():
        print(f"[1/4] ElevenLabs Music 생성 중: {topic.prompt[:60]}...")
        try:
            generate_music(topic.prompt, raw_mp3, duration_seconds=1320)
            print(f"      생성 완료: {raw_mp3.stat().st_size // 1024 // 1024}MB")
        except ElevenLabsError as e:
            print(f"      [오류] {e}")
            sys.exit(1)
    else:
        print(f"[1/4] 기존 파일 재사용: {raw_mp3}")

    # 2. 10시간 루프
    loop_mp3 = work_dir / "loop_10h.mp3"
    if not loop_mp3.exists():
        print(f"[2/4] 10시간 루프 생성 중...")
        make_loop(raw_mp3, loop_mp3, hours=topic.duration_hours)
        print(f"      루프 완료: {loop_mp3.stat().st_size // 1024 // 1024}MB")
    else:
        print(f"[2/4] 기존 루프 파일 재사용")

    # 3. 영상 제작
    video_mp4 = work_dir / "video_10h.mp4"
    if not video_mp4.exists():
        print(f"[3/4] 영상 제작 중...")
        make_video(loop_mp3, video_mp4, topic.title_en, topic.genre)
        print(f"      영상 완료: {video_mp4.stat().st_size // 1024 // 1024}MB")
    else:
        print(f"[3/4] 기존 영상 파일 재사용")

    # 4. 업로드 (선택)
    if upload:
        print(f"[4/4] YouTube 업로드...")
        _upload(video_mp4, topic)
    else:
        print(f"[4/4] 업로드 스킵 (--upload 옵션 추가 시 자동 업로드)")
        print(f"\n완료! 파일: {video_mp4}")
        print(f"제목(KO): {topic.title_ko}")
        print(f"제목(EN): {topic.title_en}")
        print(f"태그: {', '.join(topic.tags)}")


def _upload(video: Path, topic) -> None:
    """YouTube Data API v3 업로드 (token 필요)"""
    upload_script = Path(__file__).parent.parent / "shared" / "youtube_upload.py"
    if not upload_script.exists():
        print("  youtube_upload.py 없음, 스킵")
        return
    subprocess.run([
        sys.executable, str(upload_script),
        "--file", str(video),
        "--title", topic.title_en,
        "--description", f"{topic.title_ko}\n\n{topic.prompt}",
        "--tags", ",".join(topic.tags),
        "--category", "10",
    ], check=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BGM 10시간 YouTube 영상 파이프라인")
    parser.add_argument("--topic", help="장르 (sleep/meditation/buddhist/focus/wealth/healing)")
    parser.add_argument("--upload", action="store_true", help="YouTube 자동 업로드")
    args = parser.parse_args()
    run(args.topic, args.upload)
