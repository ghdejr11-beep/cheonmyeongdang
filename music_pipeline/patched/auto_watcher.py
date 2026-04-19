# 폴더 감시 자동 실행기
# music_drop 폴더에 MP3를 넣으면
# 8시간 루프 -> 애니메이션 MP4 -> 스타일 폴더 분류 -> YouTube 자동 업로드
# (12시간은 YouTube 업로드 한도 경계라 삭제 위험. 8시간으로 안전 마진 확보)
#
# [2026-04 PATCHED — music_pipeline 통합본]
# 추가 사항:
#   P1.2  업로드 전 챕터 자동 생성 → 설명란 최상단 주입
#   P2.4  업로드 전 1280x720 썸네일 자동 생성 → 업로드 후 첨부
#   P3.8  업로드 시 style_name 전달 → 다중 플리 자동 추가

import os, sys, time, shutil, threading, logging
from datetime import datetime
from pathlib import Path

# music_pipeline.enhancements import (스크립트 폴더 기준)
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from music_pipeline.enhancements.chapter_generator import (
        build_loop_chapters, prepend_chapters,
    )
    from music_pipeline.enhancements.thumbnail_maker import (
        make_thumbnail, pick_hook_kr,
    )
    _ENHANCEMENTS_OK = True
except ImportError as _e:
    print(f"[경고] music_pipeline.enhancements 미설치: {_e}")
    _ENHANCEMENTS_OK = False

# ============================================================
# 설정
# ============================================================

WATCH_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "music_drop")
DONE_DIR = os.path.join(WATCH_DIR, "done")

DEFAULT_HOURS = 8
DEFAULT_COLOR = "#ffffff"
DEFAULT_PRIVACY = "public"

LOG_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "playlist_output", "auto_log.txt")

# ============================================================
# 초기화
# ============================================================

os.makedirs(WATCH_DIR, exist_ok=True)
os.makedirs(DONE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("AutoWatcher")

# ============================================================
# 메인 처리 함수
# ============================================================

def process_mp3(mp3_path):
    """MP3 파일 하나를 전체 파이프라인으로 처리"""
    filename = os.path.basename(mp3_path)
    log.info(f"===== 새 파일 감지: {filename} =====")

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        from youtube_uploader import (
            detect_style, get_style_folder, read_mp3_metadata,
            generate_title, generate_description, upload_to_youtube
        )
    except ImportError:
        pass

    # 1단계: 스타일 감지
    metadata = read_mp3_metadata(mp3_path)
    style_name, style_info = detect_style(filename, metadata)
    log.info(f"스타일 감지: {style_name} → 재생목록: {style_info.get('playlist', '없음')}")

    # 2단계: 제목/설명 생성
    auto_title = generate_title(style_name, metadata, DEFAULT_HOURS)
    auto_desc = generate_description(style_name, style_info, metadata, DEFAULT_HOURS)
    tags = style_info.get("tags", [])
    log.info(f"제목: {auto_title}")

    # ============== [PATCH] 챕터 자동 주입 ==============
    if _ENHANCEMENTS_OK:
        try:
            chapters = build_loop_chapters(style_name, total_hours=DEFAULT_HOURS)
            auto_desc = prepend_chapters(auto_desc, chapters)
            log.info(f"챕터 {len(chapters)}개 주입")
        except Exception as e:
            log.warning(f"챕터 생성 실패: {e}")

    # 3단계: subprocess
    import subprocess

    output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "playlist_output")
    style_folder = os.path.join(output_dir, style_info.get("folder", "General"))
    os.makedirs(style_folder, exist_ok=True)

    # 안전 경로로 원본 복사 (한글 경로 회피)
    src_ext = os.path.splitext(mp3_path)[1].lower() or ".mp3"
    for base in [os.path.join("C:\\", "pl"), os.path.join(os.environ.get("TEMP", "/tmp"), "pl")]:
        try:
            os.makedirs(base, exist_ok=True)
            safe_src = os.path.join(base, f"auto_input{src_ext}")
            shutil.copy2(mp3_path, safe_src)
            break
        except:
            safe_src = mp3_path

    # ffmpeg/ffprobe 찾기
    ffmpeg = "ffmpeg"
    ffprobe = "ffprobe"
    for p in [r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"]:
        if os.path.exists(p):
            ffmpeg = p
            ffprobe = p.replace("ffmpeg.exe", "ffprobe.exe")
            break

    # 비-MP3 → MP3 변환
    if src_ext != ".mp3":
        log.info(f"{src_ext.upper()} 파일 감지 → MP3 로 변환 중...")
        safe_mp3 = os.path.join(os.path.dirname(safe_src), "auto_input.mp3")
        convert_result = subprocess.run(
            [ffmpeg, "-y", "-i", safe_src,
             "-vn",
             "-c:a", "libmp3lame",
             "-b:a", "192k",
             "-ar", "44100",
             safe_mp3],
            capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if convert_result.returncode != 0 or not os.path.exists(safe_mp3):
            log.error(f"MP3 변환 실패: {convert_result.stderr[-500:]}")
            return False
        log.info(f"MP3 변환 완료: {os.path.getsize(safe_mp3) / 1024 / 1024:.1f} MB")
    else:
        safe_mp3 = safe_src

    # 3-1: MP3 루프
    log.info(f"MP3 루프 생성 중... ({DEFAULT_HOURS}시간)")
    loop_mp3_path = os.path.join(style_folder, f"loop_{int(time.time())}.mp3")

    probe_result = subprocess.run(
        [ffprobe, "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", safe_mp3],
        capture_output=True, text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    try:
        src_duration = float(probe_result.stdout.strip())
    except:
        log.error("MP3 길이를 확인할 수 없습니다")
        return False

    target_sec = int(DEFAULT_HOURS * 3600)
    repeat = max(1, int(target_sec / src_duration) + 1)

    tmp_base = os.path.dirname(safe_mp3)
    list_txt = os.path.join(tmp_base, "loop.txt")
    with open(list_txt, "w", encoding="utf-8") as f:
        for _ in range(repeat):
            f.write(f"file '{safe_mp3}'\n")

    tmp_long = os.path.join(tmp_base, "long.mp3")
    subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", tmp_long],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    subprocess.run(
        [ffmpeg, "-y", "-i", tmp_long, "-t", str(target_sec), "-c", "copy", loop_mp3_path],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    if not os.path.exists(loop_mp3_path):
        log.error("MP3 루프 생성 실패")
        return False
    log.info(f"MP3 루프 완료: {os.path.getsize(loop_mp3_path) / 1024 / 1024:.1f} MB")

    # 3-2: 애니메이션 MP4 생성
    log.info("애니메이션 MP4 생성 중...")

    # 썸네일 미리 만들 변수 (P2.4)
    thumb_path = None
    hook_kr = ""

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        from playlist_maker import (
            make_animation_frames, parse_color, get_tmp, unique_path,
            ANIM_FPS, get_duration, run_cmd, FFMPEG
        )

        tmp_dir = get_tmp("auto_vid")
        frames_dir = os.path.join(tmp_dir, "frames")

        # 배경 이미지
        bg_src = None
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            bg_check = os.path.join(WATCH_DIR, f"bg{ext}")
            if os.path.exists(bg_check):
                bg_copy = os.path.join(tmp_dir, f"bg{ext}")
                shutil.copy2(bg_check, bg_copy)
                bg_src = bg_copy
                log.info(f"배경 이미지 사용: {bg_check}")
                break

        if bg_src is None:
            from youtube_uploader import generate_background
            bg_src = os.path.join(tmp_dir, f"auto_bg_{style_name}.png")
            generate_background(style_name, style_info, bg_src)
            log.info(f"배경 자동 생성: {style_name} 스타일")

        # ============== [PATCH] 썸네일 자동 생성 ==============
        if _ENHANCEMENTS_OK:
            try:
                hook_kr = pick_hook_kr(style_name)
                thumb_path = os.path.join(tmp_dir, f"thumb_{style_name}.png")
                made = make_thumbnail(
                    out_path=thumb_path,
                    style_name=style_name,
                    hook_kr=hook_kr,
                    duration_label=f"{DEFAULT_HOURS} HOURS",
                    bg_image_path=bg_src,
                )
                if made:
                    log.info(f"썸네일 생성: {thumb_path} (후킹: '{hook_kr}')")
                else:
                    thumb_path = None
            except Exception as e:
                log.warning(f"썸네일 생성 실패: {e}")
                thumb_path = None

        color_tuple = parse_color(style_info.get("text_color", DEFAULT_COLOR))

        short_frames = ANIM_FPS * 10
        log.info(f"프레임 생성 중... ({short_frames}개, 10초 루프)")
        frame_pattern = make_animation_frames(
            bg_src, color_tuple, frames_dir, safe_mp3, tmp_dir, short_frames, None)

        short_video = os.path.join(tmp_dir, "short_loop.mp4")
        cmd_short = [FFMPEG, "-y",
               "-framerate", str(ANIM_FPS), "-i", frame_pattern,
               "-c:v", "libx264", "-preset", "medium", "-crf", "30",
               "-pix_fmt", "yuv420p",
               short_video]

        log.info("1/2: 짧은 루프 영상 인코딩 중...")
        result = run_cmd(cmd_short, timeout=300)

        if not result or result.returncode != 0 or not os.path.exists(short_video):
            log.error("짧은 루프 영상 생성 실패")
            return False

        try:
            shutil.rmtree(frames_dir)
        except:
            pass

        video_filename = f"playlist_{style_name}_{int(time.time())}.mp4"
        out_path = unique_path(os.path.join(style_folder, video_filename))

        mp3_for_video = os.path.join(tmp_dir, "audio.mp3")
        shutil.copy2(loop_mp3_path, mp3_for_video)

        cmd_final = [FFMPEG, "-y",
               "-stream_loop", "-1", "-i", short_video,
               "-i", mp3_for_video,
               "-c:v", "copy",
               "-c:a", "aac", "-b:a", "192k",
               "-shortest", "-movflags", "+faststart",
               out_path]

        log.info(f"2/2: {DEFAULT_HOURS}시간 영상 합치기 중 (빠름)...")
        result = run_cmd(cmd_final, timeout=3600)

        if not result or result.returncode != 0 or not os.path.exists(out_path):
            log.error("MP4 생성 실패")
            return False

        size_mb = os.path.getsize(out_path) / 1024 / 1024
        log.info(f"MP4 완성: {out_path} ({size_mb:.1f} MB)")

        try:
            shutil.rmtree(frames_dir)
        except:
            pass

    except Exception as e:
        log.error(f"MP4 생성 중 오류: {e}")
        import traceback
        log.error(traceback.format_exc())
        return False

    # 4단계: YouTube 업로드 (재시도 포함)
    log.info("YouTube 업로드 중...")
    playlist_name = style_info.get("playlist", "")
    upload_ok = False
    upload_msg = ""
    for attempt in range(1, 4):
        # ============== [PATCH] thumbnail_path + style_name 전달 ==============
        upload_ok, upload_msg = upload_to_youtube(
            video_path=out_path,
            title=auto_title,
            description=auto_desc,
            tags=tags,
            category=style_info.get("category", "10"),
            privacy=DEFAULT_PRIVACY,
            playlist_name=playlist_name,
            thumbnail_path=thumb_path,
            style_name=style_name,
        )
        if upload_ok:
            break
        log.info(f"업로드 실패 (시도 {attempt}/3): {upload_msg}")
        if attempt < 3:
            wait = attempt * 10
            log.info(f"{wait}초 후 재시도...")
            time.sleep(wait)
    log.info(upload_msg)

    # 5단계: 원본 done 폴더로 이동
    done_path = os.path.join(DONE_DIR, filename)
    try:
        shutil.move(mp3_path, done_path)
        log.info(f"원본 이동: {done_path}")
    except:
        log.info("원본 파일 이동 실패 (수동으로 옮겨주세요)")

    try:
        os.remove(loop_mp3_path)
        log.info("루프 MP3 삭제 완료 (용량 절약)")
    except:
        pass

    if upload_ok:
        try:
            os.remove(out_path)
            log.info("업로드 완료된 MP4 삭제 완료 (용량 절약)")
        except:
            pass

    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except:
        pass

    log.info(f"===== 처리 완료: {filename} =====\n")
    return True

# ============================================================
# 폴더 감시
# ============================================================

def watch_folder():
    log.info(f"=" * 50)
    log.info(f"폴더 감시 시작!")
    log.info(f"감시 폴더: {WATCH_DIR}")
    log.info(f"MP3 파일을 이 폴더에 넣으면 자동으로 처리됩니다.")
    log.info(f"배경 이미지를 사용하려면 bg.png 또는 bg.jpg를 같은 폴더에 넣으세요.")
    log.info(f"종료: Ctrl+C")
    log.info(f"=" * 50)

    processed = set()
    audio_extensions = (".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".opus", ".wma")

    while True:
        try:
            for f in os.listdir(WATCH_DIR):
                if not f.lower().endswith(audio_extensions):
                    continue
                if f in processed:
                    continue

                mp3_path = os.path.join(WATCH_DIR, f)

                size1 = os.path.getsize(mp3_path)
                time.sleep(2)
                if not os.path.exists(mp3_path):
                    continue
                size2 = os.path.getsize(mp3_path)

                if size1 != size2:
                    log.info(f"다운로드 중... 대기: {f}")
                    continue

                if size2 < 1000:
                    continue

                processed.add(f)
                try:
                    process_mp3(mp3_path)
                except Exception as e:
                    log.error(f"처리 실패: {f} - {e}")
                    import traceback
                    log.error(traceback.format_exc())

        except KeyboardInterrupt:
            log.info("종료됨")
            break
        except Exception as e:
            log.error(f"감시 오류: {e}")

        time.sleep(5)

if __name__ == "__main__":
    watch_folder()
