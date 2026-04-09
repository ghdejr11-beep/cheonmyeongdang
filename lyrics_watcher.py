"""
가사 있는 짧은 노래 자동 업로더.

사용법:
  1. 이 파일 더블클릭 (또는: python lyrics_watcher.py)
  2. ~/Desktop/lyrics_drop 폴더에 MP3 드롭
  3. 자동으로 3~5분 음악 비디오 MP4 생성 + YouTube 업로드

기존 auto_watcher.py (12시간 루프용) 와는 별도로 동작.
youtube_uploader.py 의 SSL 이어올리기 로직 그대로 재사용.

종료: Ctrl+C
"""

import os
import sys
import time
import shutil
import random
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# ============================================================
# 설정
# ============================================================
HOME = Path.home()
WATCH_DIR = HOME / "Desktop" / "lyrics_drop"
DONE_DIR = WATCH_DIR / "done"
LOG_PATH = HOME / "Desktop" / "playlist_output" / "lyrics_log.txt"

DEFAULT_PRIVACY = "public"
DEFAULT_STYLE_FALLBACK = "pop"   # 가사 있는 노래의 기본 스타일
LYRIC_PLAYLIST = "🎵 AI 작사작곡"

# 처리 중 파일 중복 감지 방지
_processing: set[str] = set()

# ============================================================
# 초기화
# ============================================================
WATCH_DIR.mkdir(parents=True, exist_ok=True)
DONE_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("LyricsWatcher")

# 스크립트 폴더를 sys.path 에 추가 (import 보장)
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


# ============================================================
# 제목/설명 템플릿 (가사 있는 노래용)
# ============================================================
LYRIC_TITLE_TEMPLATES = [
    "{title} - {artist} | Official Audio",
    "[AI 오리지널] {title} - {artist}",
    "{title} ({artist}) | Lyric Audio",
    "🎵 {title} - {artist} [AI Music]",
    "{artist} - {title} | 가사 있는 AI 노래",
    "{title} by {artist} | AI Generated Song",
]

LYRIC_DESCRIPTION_TEMPLATE = """🎵 {title} - {artist}

AI 로 작곡·작사한 오리지널 트랙입니다.
듣고 마음에 드시면 좋아요 & 구독 부탁드려요!

━━━━━━━━━━━━━━━━━━━
👤 아티스트: {artist}
📀 제목: {title}
🎼 스타일: {style_ko}
📅 업로드: {date}
━━━━━━━━━━━━━━━━━━━

📜 가사 (Lyrics)
[여기에 가사가 자동으로 들어갑니다 — .lrc 파일 동봉 시]

━━━━━━━━━━━━━━━━━━━
🔔 덕구네 AI 음악 채널
매일 새로운 AI 작곡 트랙을 업로드합니다.
구독하시면 신곡 알림을 받을 수 있어요.

#AI음악 #AI작곡 #AI작사 #AIMusic #OriginalSong #{style_hashtag}
"""


def title_case_from_filename(filename: str) -> str:
    """파일명에서 제목 추출. 'my_song_title.mp3' → 'My Song Title'."""
    stem = Path(filename).stem
    # 특수문자 → 공백
    for ch in ["_", "-", ".", "[", "]", "(", ")"]:
        stem = stem.replace(ch, " ")
    parts = [p for p in stem.split() if p]
    return " ".join(parts).strip() or "Untitled"


def generate_lyric_title(metadata: dict, filename: str) -> str:
    title = (metadata.get("title") or "").strip()
    artist = (metadata.get("artist") or "").strip()

    if not title:
        title = title_case_from_filename(filename)
    if not artist:
        artist = "AI 작곡"

    template = random.choice(LYRIC_TITLE_TEMPLATES)
    full_title = template.format(title=title, artist=artist)
    return full_title[:95]  # YouTube 100자 제한 여유


def generate_lyric_description(metadata: dict, filename: str, style_name: str, style_info: dict) -> str:
    title = (metadata.get("title") or title_case_from_filename(filename)).strip()
    artist = (metadata.get("artist") or "AI 작곡").strip()

    style_ko_map = {
        "lofi": "로파이", "sleep": "수면", "rain": "빗소리", "meditation": "명상",
        "jazz": "재즈", "study": "스터디", "classical": "클래식",
        "electronic": "일렉트로닉", "pop": "팝", "kpop": "K-POP",
    }
    style_ko = style_ko_map.get(style_name, style_name)

    # 가사 파일 (.lrc) 자동 감지
    lrc_path = Path(filename).with_suffix(".lrc")
    lyrics_section = ""
    if lrc_path.exists():
        try:
            lyrics_text = lrc_path.read_text(encoding="utf-8")
            # 타임스탬프 제거 ([00:12.34] → '')
            import re
            clean = re.sub(r"\[\d{1,2}:\d{1,2}[.:]?\d*\]", "", lyrics_text)
            clean = "\n".join(line.strip() for line in clean.splitlines() if line.strip())
            lyrics_section = clean[:2000]
        except Exception:
            pass

    desc = LYRIC_DESCRIPTION_TEMPLATE.format(
        title=title,
        artist=artist,
        style_ko=style_ko,
        date=datetime.now().strftime("%Y-%m-%d"),
        style_hashtag=style_name,
    )

    if lyrics_section:
        desc = desc.replace(
            "[여기에 가사가 자동으로 들어갑니다 — .lrc 파일 동봉 시]",
            lyrics_section,
        )

    return desc[:4900]  # YouTube 5000자 제한 여유


# ============================================================
# MP4 생성 (정적 배경 + 음원)
# ============================================================
def make_lyric_video(mp3_path: str, bg_image: str, out_path: str, ffmpeg: str) -> bool:
    """MP3 길이 그대로 MP4 생성. 정적 이미지 + 오디오.

    12시간 루프 같은 거 없음. 그냥 원본 길이.
    """
    try:
        # ffprobe 로 오디오 길이 확인 (fallback: playlist_maker.get_duration)
        from playlist_maker import get_duration
        duration = get_duration(mp3_path)
        if duration <= 0:
            log.error("MP3 길이 감지 실패")
            return False

        log.info(f"비디오 생성: {duration:.1f}초 길이")

        cmd = [
            ffmpeg, "-y",
            "-loop", "1", "-i", bg_image,
            "-i", mp3_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-preset", "veryfast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
            "-shortest",
            "-t", f"{duration:.2f}",
            out_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode != 0:
            log.error(f"ffmpeg 에러: {result.stderr[-500:]}")
            return False

        size_mb = os.path.getsize(out_path) / 1024 / 1024
        log.info(f"MP4 완성: {out_path} ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        log.error(f"비디오 생성 실패: {e}")
        return False


# ============================================================
# 메인 처리 파이프라인
# ============================================================
def process_mp3(mp3_path: str) -> bool:
    filename = os.path.basename(mp3_path)
    log.info(f"===== 새 파일: {filename} =====")

    try:
        from youtube_uploader import (
            detect_style, read_mp3_metadata,
            generate_background, upload_to_youtube,
        )
        from playlist_maker import find_ffmpeg, get_tmp, unique_path, parse_color
    except ImportError as e:
        log.error(f"모듈 import 실패: {e}")
        return False

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        log.error("ffmpeg 를 찾을 수 없음. C:\\ffmpeg\\bin 에 설치하거나 PATH 추가")
        return False

    # 1. 메타데이터 읽기
    metadata = read_mp3_metadata(mp3_path) or {}
    log.info(f"메타: title={metadata.get('title', '없음')}, artist={metadata.get('artist', '없음')}")

    # 2. 스타일 감지 (없으면 pop 기본)
    style_name, style_info = detect_style(filename, metadata)
    if not style_name or style_name == "unknown":
        style_name = DEFAULT_STYLE_FALLBACK
        # youtube_uploader.STYLE_KEYWORDS 에서 style_info 재조회
        try:
            from youtube_uploader import STYLE_KEYWORDS
            style_info = STYLE_KEYWORDS.get(DEFAULT_STYLE_FALLBACK, {})
        except Exception:
            style_info = {}
    log.info(f"스타일: {style_name}")

    # 3. 제목/설명 생성
    auto_title = generate_lyric_title(metadata, filename)
    auto_description = generate_lyric_description(metadata, mp3_path, style_name, style_info)
    log.info(f"제목: {auto_title}")

    # 4. 작업 폴더
    tmp_dir = get_tmp(f"lyrics_{int(time.time())}")

    # 5. 배경 이미지 (있으면 사용자 제공 bg.*, 없으면 스타일 자동 생성)
    bg_path = None
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        bg_check = WATCH_DIR / f"bg{ext}"
        if bg_check.exists():
            bg_copy = os.path.join(tmp_dir, f"bg{ext}")
            shutil.copy2(str(bg_check), bg_copy)
            bg_path = bg_copy
            log.info(f"사용자 배경 사용: {bg_check}")
            break

    if bg_path is None:
        bg_path = os.path.join(tmp_dir, f"auto_bg_{style_name}.png")
        try:
            generate_background(style_name, style_info, bg_path)
            log.info(f"스타일 배경 자동 생성: {style_name}")
        except Exception as e:
            log.error(f"배경 생성 실패: {e}")
            return False

    # 6. MP4 생성
    out_dir = HOME / "Desktop" / "playlist_output" / "Lyrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = "".join(c if c.isalnum() or c in " -_" else "_" for c in Path(filename).stem)
    out_mp4 = str(unique_path(str(out_dir / f"lyric_{safe_stem}.mp4")))

    if not make_lyric_video(mp3_path, bg_path, out_mp4, ffmpeg):
        log.error("MP4 생성 실패 → 중단")
        return False

    # 7. YouTube 업로드
    log.info("YouTube 업로드 시작...")
    tags = style_info.get("tags", []) + ["AI 음악", "AI 작곡", "AI 노래", "가사", "오리지널"]
    tags = tags[:15]

    ok, msg = upload_to_youtube(
        video_path=out_mp4,
        title=auto_title,
        description=auto_description,
        tags=tags,
        category=style_info.get("category", "10"),
        privacy=DEFAULT_PRIVACY,
        playlist_name=LYRIC_PLAYLIST,
    )
    log.info(msg)

    if not ok:
        log.error("업로드 실패 → 파일 유지 (재시도 가능)")
        return False

    # 8. 처리 완료 파일 이동 + 정리
    try:
        done_path = DONE_DIR / filename
        if done_path.exists():
            done_path = DONE_DIR / f"{int(time.time())}_{filename}"
        shutil.move(mp3_path, str(done_path))
        log.info(f"원본 이동: {done_path}")
    except Exception as e:
        log.warning(f"원본 이동 실패 (업로드는 성공): {e}")

    try:
        os.remove(out_mp4)
        log.info("MP4 삭제 (용량 절약)")
    except Exception:
        pass

    log.info(f"===== 처리 완료: {filename} =====\n")
    return True


# ============================================================
# 폴더 감시 루프
# ============================================================
def watch_loop():
    log.info("=" * 50)
    log.info("가사 노래 자동 업로더 시작")
    log.info(f"감시 폴더: {WATCH_DIR}")
    log.info("MP3 파일을 이 폴더에 넣으면 자동으로 처리됩니다.")
    log.info("배경 이미지를 쓰려면 bg.png 또는 bg.jpg 를 같은 폴더에 넣으세요.")
    log.info(".lrc 파일을 MP3 와 같은 이름으로 두면 가사가 자동 포함됩니다.")
    log.info("종료: Ctrl+C")
    log.info("=" * 50)

    while True:
        try:
            for f in os.listdir(WATCH_DIR):
                full = os.path.join(WATCH_DIR, f)
                if not os.path.isfile(full):
                    continue
                if not f.lower().endswith(".mp3"):
                    continue
                if full in _processing:
                    continue

                # 파일 복사가 끝났는지 확인 (크기 변화 없음)
                try:
                    size1 = os.path.getsize(full)
                    time.sleep(1.0)
                    size2 = os.path.getsize(full)
                    if size1 != size2:
                        continue
                except OSError:
                    continue

                _processing.add(full)
                try:
                    process_mp3(full)
                except Exception as e:
                    log.exception(f"처리 중 예외: {e}")
                finally:
                    _processing.discard(full)

            time.sleep(3)
        except KeyboardInterrupt:
            log.info("종료 신호 감지. 안녕.")
            return
        except Exception as e:
            log.exception(f"감시 루프 예외: {e}")
            time.sleep(5)


if __name__ == "__main__":
    watch_loop()
