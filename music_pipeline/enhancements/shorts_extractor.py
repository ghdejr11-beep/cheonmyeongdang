"""롱폼 영상 → YouTube Shorts (9:16, 최대 60초) 자동 추출기.

잘 되는 채널들의 공식: 롱폼 업로드 직후 동일 오디오의 **hook 구간**
(드롭, 후렴, 비트 강한 구간) 30~55초를 9:16 으로 크롭해서 Shorts 에
크로스포스트. Shorts 가 Home/Subscriptions 피드로 유입을 끌어오고,
그 유입이 롱폼 완주율로 이어지는 FlyWheel 이 2026 YouTube 알고리즘의
핵심.

이 모듈은:
  1. librosa 없이도 작동하도록 RMS 기반 간단한 하이라이트 감지
     (원본 코드의 auto_watcher.py `analyze_audio` 로직과 유사)
  2. ffmpeg 로 해당 구간만 추출 + 9:16 크롭 + 자막 하드섭 (선택)
  3. Shorts 타이틀은 "... #Shorts" 필수 포함

사용:
    from music_pipeline.enhancements.shorts_extractor import extract_shorts

    short_path = extract_shorts(
        src_video="long_video.mp4",
        src_audio="track.mp3",     # 원본 오디오 (MP4 보다 짧음)
        out_dir="/tmp/shorts",
        ffmpeg="ffmpeg",
        ffprobe="ffprobe",
        short_duration=50,          # 30~55 권장
        hook_text="공부할 때 듣는 로파이",  # 9:16 가운데 자막
    )

그 다음 `upload_to_youtube(short_path, title="... #Shorts", ...)` 로
업로드. Shorts 감지는 YouTube 가 자동으로 하므로 별도 플래그 없음
(9:16 세로 + 60초 이하 + 제목 #Shorts 이면 자동 분류).
"""

from __future__ import annotations

import math
import os
import random
import struct
import subprocess
import wave
from pathlib import Path


def _run(cmd, timeout=300) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except Exception as e:
        print(f"[shorts] cmd 실패: {e}")
        return None


def _get_duration(path: str, ffprobe: str) -> float:
    r = _run(
        [
            ffprobe, "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        timeout=30,
    )
    if not r or not r.stdout.strip():
        return 0.0
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def find_hook_moment(
    audio_path: str,
    ffmpeg: str,
    ffprobe: str,
    tmp_dir: str,
    short_duration: float = 50,
    skip_intro_sec: float = 15,
) -> float:
    """오디오에서 가장 강한 음량 구간의 **시작 초** 반환.

    간단한 RMS 프레임 분석으로 후렴 직전·드롭 직전을 찾는다.
    librosa 없이도 동작 (wave + struct 만 사용).

    Args:
        skip_intro_sec: 인트로 스킵 (보통 첫 15초는 인트로라 Shorts 로 쓰면
            hook 부족)

    Returns:
        하이라이트 시작 초. 분석 실패 시 총 길이의 1/3 지점.
    """
    total_dur = _get_duration(audio_path, ffprobe)
    if total_dur < short_duration + skip_intro_sec:
        return 0.0

    # 16kHz mono WAV 로 변환
    tmp_wav = os.path.join(tmp_dir, "shorts_analyze.wav")
    r = _run(
        [ffmpeg, "-y", "-i", audio_path, "-ac", "1", "-ar", "16000",
         "-sample_fmt", "s16", tmp_wav],
        timeout=180,
    )
    if not r or r.returncode != 0 or not os.path.exists(tmp_wav):
        return max(skip_intro_sec, total_dur / 3)

    try:
        wf = wave.open(tmp_wav, "rb")
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = wf.readframes(n)
        wf.close()
        samples = struct.unpack(f"<{n}h", raw)
    except Exception:
        return max(skip_intro_sec, total_dur / 3)

    # 1초 단위 RMS
    window = sr  # 1초
    rms_per_sec: list[float] = []
    for i in range(0, n, window):
        chunk = samples[i:i + window]
        if not chunk:
            break
        rms = math.sqrt(sum(s * s for s in chunk) / len(chunk)) / 32768.0
        rms_per_sec.append(rms)

    if len(rms_per_sec) < short_duration + skip_intro_sec:
        return max(skip_intro_sec, total_dur / 3)

    # 슬라이딩 윈도우: 각 시작 지점에서 `short_duration` 초 평균 RMS
    best_start = skip_intro_sec
    best_score = 0.0
    max_start = len(rms_per_sec) - int(short_duration) - 5
    for start in range(int(skip_intro_sec), max_start):
        score = sum(rms_per_sec[start:start + int(short_duration)]) / short_duration
        # 뒷부분 가중치: 2/3 지점을 선호 (후렴이 자주 등장)
        position_weight = 1.0 + 0.3 * math.exp(-((start / len(rms_per_sec) - 0.66) ** 2) * 20)
        score *= position_weight
        if score > best_score:
            best_score = score
            best_start = start

    try:
        os.remove(tmp_wav)
    except Exception:
        pass

    return float(best_start)


def _escape_drawtext(text: str) -> str:
    """ffmpeg drawtext 필터용 이스케이프."""
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace(",", "\\,")
    )


def extract_shorts(
    src_video: str,
    out_path: str,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
    src_audio: str | None = None,
    short_duration: float = 50.0,
    hook_text: str = "",
    hook_start: float | None = None,
    tmp_dir: str | None = None,
) -> tuple[bool, str]:
    """롱폼 영상에서 Shorts 추출.

    Args:
        src_video: 롱폼 MP4 경로
        out_path: 출력 Shorts MP4 경로
        src_audio: 분석용 짧은 오디오 원본 (없으면 src_video 에서 추출)
        short_duration: 30~55 권장
        hook_text: 중앙에 박을 한글 문구 (비워두면 생략)
        hook_start: 수동 지정 시작 초 (None 이면 자동 감지)
        tmp_dir: 임시 폴더

    Returns:
        (success, message)
    """
    if not os.path.exists(src_video):
        return False, f"원본 영상 없음: {src_video}"

    if tmp_dir is None:
        tmp_dir = os.path.dirname(out_path) or "/tmp"
    os.makedirs(tmp_dir, exist_ok=True)

    # 1. 하이라이트 시작 찾기
    if hook_start is None:
        analyze_src = src_audio or src_video
        hook_start = find_hook_moment(
            analyze_src, ffmpeg, ffprobe, tmp_dir,
            short_duration=short_duration,
        )
        print(f"[shorts] 하이라이트 시작: {hook_start:.1f}초")

    # 2. 9:16 크롭 + 하드섭 필터
    # 16:9 (1920x1080) → 9:16 (1080x1920) 로 변환:
    #   영상을 세로로 리사이즈 + 블러 배경 겹치기 + 원본 중앙 배치 (2025년 표준)
    filter_parts = [
        # 원본을 배경용으로 블러 처리
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=20:5[bg]",
        # 원본을 중앙에 자리잡게 스케일
        "[0:v]scale=1080:-2[fg]",
        # 배경 + 중앙 영상
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[v1]",
    ]

    last_label = "v1"

    # 3. 훅 텍스트 (선택)
    if hook_text:
        # 폰트 경로 (Windows 우선, fallback)
        font_paths = [
            r"C\:/Windows/Fonts/malgunbd.ttf",
            r"C\:/Windows/Fonts/malgun.ttf",
            "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        ]
        font_path = None
        for fp in font_paths:
            # ffmpeg 는 raw path 를 쓰므로 OS 실제 경로 체크
            real = fp.replace("\\:", ":").replace("C:/", r"C:/")
            if os.path.exists(real):
                font_path = fp
                break

        safe_text = _escape_drawtext(hook_text)
        drawtext = (
            f"[{last_label}]drawtext="
            f"text='{safe_text}':"
            f"fontsize=72:"
            f"fontcolor=white:"
            f"borderw=6:"
            f"bordercolor=black:"
            f"box=1:boxcolor=0x00000088:boxborderw=20:"
            f"x=(w-text_w)/2:"
            f"y=h*0.12:"
            f"enable='between(t,0,{short_duration})'"
        )
        if font_path:
            drawtext += f":fontfile='{font_path}'"
        drawtext += f"[{last_label}_txt]"
        filter_parts.append(drawtext)
        last_label = f"{last_label}_txt"

    filter_complex = ";".join(filter_parts)

    # 4. ffmpeg 실행
    cmd = [
        ffmpeg, "-y",
        "-ss", f"{hook_start:.2f}",
        "-i", src_video,
        "-t", f"{short_duration:.2f}",
        "-filter_complex", filter_complex,
        "-map", f"[{last_label}]",
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        out_path,
    ]

    r = _run(cmd, timeout=600)
    if not r or r.returncode != 0 or not os.path.exists(out_path):
        err = (r.stderr or "")[-800:] if r else "ffmpeg 실행 실패"
        return False, f"Shorts 생성 실패:\n{err}"

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    return True, f"Shorts 완성: {out_path} ({size_mb:.1f} MB, hook={hook_start:.1f}s)"


def build_shorts_title(original_title: str, hook_text: str = "") -> str:
    """Shorts 전용 제목. 100자 제한, #Shorts 필수."""
    if hook_text:
        base = hook_text.strip()
    else:
        base = original_title.split("|")[0].strip() if original_title else "Playlist"

    # 해시태그가 이미 있으면 중복 제거
    base_clean = base.replace("#Shorts", "").replace("#shorts", "").strip()
    # 95자까지 본문 + " #Shorts"
    if len(base_clean) > 90:
        base_clean = base_clean[:90].rsplit(" ", 1)[0]
    return f"{base_clean} #Shorts"


if __name__ == "__main__":
    # 빌드 테스트
    title = build_shorts_title("공부할 때 듣는 로파이 | 8 Hours Playlist | Study Music")
    assert "#Shorts" in title
    assert len(title) <= 100
    print(f"✓ Shorts 제목: {title}")

    # 긴 제목
    long_t = "가" * 200
    title2 = build_shorts_title(long_t)
    assert len(title2) <= 100
    assert "#Shorts" in title2
    print(f"✓ 긴 제목 잘라짐: {title2}")

    # 중복 태그 방지
    title3 = build_shorts_title("이미 있음 #Shorts")
    assert title3.count("#Shorts") == 1
    print(f"✓ 중복 방지: {title3}")

    print("\n(주의) extract_shorts 는 ffmpeg + 실제 파일 필요 → 여기서는 dry-run 테스트만)")
    ok, msg = extract_shorts(
        src_video="/nonexistent/fake.mp4",
        out_path="/tmp/out.mp4",
    )
    assert not ok
    assert "원본 영상 없음" in msg
    print("✓ 파일 없을 때 에러 처리 OK")

    print("\n✓ shorts_extractor.py 자체 테스트 통과")
