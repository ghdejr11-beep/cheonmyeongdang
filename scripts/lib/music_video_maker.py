"""
뮤직비디오 자동 생성기.

가사 분석 → Pexels 영상 다운 → 자막 합성 → 최종 MP4.
lyrics_watcher.py 에서 호출됨.

흐름:
  1. Claude 가 가사에서 장면 키워드 추출 (영어)
  2. Pexels API 로 키워드별 무료 영상 다운로드
  3. ffmpeg 로: 영상 클립 이어붙이기 + 자막 오버레이 + 오디오 합성
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def make_pexels_music_video(
    mp3_path: str,
    lyrics_text: str,
    srt_path: str,
    out_path: str,
    ffmpeg: str,
    tmp_dir: str,
    duration: float,
    log=None,
) -> bool:
    """Pexels 영상 + 자막으로 뮤직비디오 생성.

    Args:
        mp3_path: 오디오 파일 경로
        lyrics_text: 가사 원문 (키워드 추출용)
        srt_path: SRT 자막 파일 경로 (None 이면 자막 없이)
        out_path: 출력 MP4 경로
        ffmpeg: ffmpeg 실행 경로
        tmp_dir: 임시 작업 폴더
        duration: 오디오 길이 (초)
        log: 로거 (None 이면 print)

    Returns:
        성공 여부
    """
    def _log(msg):
        if log:
            log.info(msg)
        else:
            print(msg)

    try:
        from scripts.lib.pexels_video import extract_keywords_from_lyrics, get_clips_for_keywords
    except ImportError as e:
        _log(f"pexels_video import 실패: {e}")
        return False

    # 1. 가사에서 키워드 추출
    _log("Claude 가사 분석 → 키워드 추출 중...")
    keywords = extract_keywords_from_lyrics(lyrics_text)
    _log(f"키워드 {len(keywords)}개: {keywords[:5]}...")

    if not keywords:
        _log("키워드 추출 실패 → Pexels 영상 없이 진행 불가")
        return False

    # 2. Pexels 영상 다운로드
    clips_dir = os.path.join(tmp_dir, "pexels_clips")
    os.makedirs(clips_dir, exist_ok=True)

    _log("Pexels 영상 다운로드 중...")
    clips = get_clips_for_keywords(keywords, clips_dir, clips_per_keyword=1)
    _log(f"다운로드 완료: {len(clips)}개 클립")

    if not clips:
        _log("Pexels 영상 0개 → 실패")
        return False

    # 3. 클립들을 이어붙여서 오디오 길이에 맞추기
    concat_list = os.path.join(tmp_dir, "concat.txt")
    _build_concat_list(clips, concat_list, duration, ffmpeg, tmp_dir)

    # 4. ffmpeg 로 최종 합성: 영상 + 오디오 + 자막
    _log("영상 합성 중 (ffmpeg)...")

    # 4-1: 영상 클립 이어붙이기 (무음)
    merged_video = os.path.join(tmp_dir, "merged_clips.mp4")
    cmd_merge = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-an",  # 오디오 제거
        "-t", f"{duration:.2f}",
        merged_video,
    ]

    result = subprocess.run(
        cmd_merge, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=600,
    )
    if result.returncode != 0 or not os.path.exists(merged_video):
        _log(f"영상 이어붙이기 실패: {result.stderr[-500:]}")
        return False

    # 4-2: 오디오 합성 + 자막 오버레이
    cmd_final = [
        ffmpeg, "-y",
        "-i", merged_video,
        "-i", mp3_path,
    ]

    # 자막 필터
    if srt_path and os.path.exists(srt_path):
        # Windows 경로 이스케이프
        srt_safe = srt_path.replace("\\", "/").replace(":", "\\:")
        # 시스템 한국어 폰트 사용 (ASCII 경로)
        font_path = "C\\:/Windows/Fonts/malgun.ttf"
        if not os.path.exists(r"C:\Windows\Fonts\malgun.ttf"):
            font_path = ""

        if font_path:
            vf = (
                f"subtitles='{srt_safe}':"
                f"fontsdir='C\\:/Windows/Fonts':"
                f"force_style='FontName=Malgun Gothic,FontSize=32,"
                f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
                f"BackColour=&H80000000,BorderStyle=1,Outline=2,"
                f"Shadow=1,Alignment=2,MarginV=60'"
            )
            cmd_final.extend(["-vf", vf])
            _log("자막 오버레이 적용 (Malgun Gothic)")
        else:
            _log("한국어 폰트 없음 → 자막 생략")
    else:
        _log("SRT 없음 → 자막 없이 진행")

    cmd_final.extend([
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-map", "0:v:0", "-map", "1:a:0",
        "-shortest",
        "-t", f"{duration:.2f}",
        "-movflags", "+faststart",
        out_path,
    ])

    result = subprocess.run(
        cmd_final, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=600,
    )

    if result.returncode != 0 or not os.path.exists(out_path):
        _log(f"최종 합성 실패: {result.stderr[-800:]}")
        return False

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    _log(f"뮤직비디오 완성: {out_path} ({size_mb:.1f}MB)")
    return True


def _build_concat_list(clips: list[str], concat_path: str,
                       target_duration: float, ffmpeg: str,
                       tmp_dir: str):
    """클립 리스트를 target_duration 에 맞춰 반복 배치.

    각 클립을 순서대로 사용하고, 모자라면 처음부터 반복.
    """
    # 각 클립 길이 측정
    clip_durations = []
    for clip in clips:
        dur = _get_duration(clip, ffmpeg)
        if dur > 0:
            clip_durations.append((clip, dur))

    if not clip_durations:
        # 폴백: 클립 길이 모르면 균등 배분
        with open(concat_path, "w", encoding="utf-8") as f:
            for clip in clips:
                safe = clip.replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{safe}'\n")
        return

    # target_duration 채울 때까지 반복
    total = 0.0
    entries = []
    idx = 0
    while total < target_duration:
        clip, dur = clip_durations[idx % len(clip_durations)]
        entries.append(clip)
        total += dur
        idx += 1
        if idx > 100:  # 안전장치
            break

    with open(concat_path, "w", encoding="utf-8") as f:
        for clip in entries:
            safe = clip.replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{safe}'\n")


def _get_duration(filepath: str, ffmpeg: str) -> float:
    """ffprobe 로 영상 길이 측정."""
    ffprobe = ffmpeg.replace("ffmpeg", "ffprobe")
    try:
        result = subprocess.run(
            [ffprobe, "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", filepath],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0
