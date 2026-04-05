# 폴더 감시 자동 실행기
# music_drop 폴더에 MP3를 넣으면
# 12시간 루프 -> 애니메이션 MP4 -> 스타일 폴더 분류 -> YouTube 자동 업로드
# 사용법: 더블클릭으로 실행하면 백그라운드에서 폴더를 계속 감시합니다.

import os, sys, time, shutil, threading, logging
from datetime import datetime

# ============================================================
# 설정
# ============================================================

# 감시할 폴더 (여기에 MP3를 넣으면 자동 실행)
WATCH_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "music_drop")

# 처리 완료된 파일을 이동시킬 폴더
DONE_DIR = os.path.join(WATCH_DIR, "done")

# 기본 설정
DEFAULT_HOURS = 12
DEFAULT_COLOR = "#ffffff"
DEFAULT_PRIVACY = "public"

# 로그 파일
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
        # playlist_maker.py와 같은 폴더에서 import
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        from youtube_uploader import (
            detect_style, get_style_folder, read_mp3_metadata,
            generate_title, generate_description, upload_to_youtube
        )

        # 여기서 playlist_maker의 핵심 함수들을 가져옴
        # (gradio 없이 직접 호출)
        from playlist_maker_core import loop_single_mp3, make_video_core

    except ImportError:
        # playlist_maker_core가 없으면 subprocess로 대체
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

    # 3단계: subprocess로 playlist_maker.py 호출 (가장 안정적)
    import subprocess

    output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "playlist_output")
    style_folder = os.path.join(output_dir, style_info.get("folder", "General"))
    os.makedirs(style_folder, exist_ok=True)

    # 안전한 경로로 MP3 복사 (한글 경로 회피)
    for base in [os.path.join("C:\\", "pl"), os.path.join(os.environ.get("TEMP", "/tmp"), "pl")]:
        try:
            os.makedirs(base, exist_ok=True)
            safe_mp3 = os.path.join(base, "auto_input.mp3")
            shutil.copy2(mp3_path, safe_mp3)
            break
        except:
            safe_mp3 = mp3_path

    # 3-1: MP3 루프 (12시간)
    log.info("MP3 루프 생성 중... (12시간)")
    loop_mp3_path = os.path.join(style_folder, f"loop_{int(time.time())}.mp3")

    # ffmpeg/ffprobe 찾기
    ffmpeg = "ffmpeg"
    ffprobe = "ffprobe"
    for p in [r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"]:
        if os.path.exists(p):
            ffmpeg = p
            ffprobe = p.replace("ffmpeg.exe", "ffprobe.exe")
            break

    # 원본 길이 확인
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

    # concat 리스트 생성
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

    # 프레임 생성을 위해 playlist_maker의 함수 직접 사용
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        # gradio import를 피하기 위해 필요한 함수만 가져옴
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pm", os.path.join(os.path.dirname(os.path.abspath(__file__)), "playlist_maker.py"),
            submodule_search_locations=[]
        )
        # gradio를 모킹하여 import 문제 회피
        import types
        mock_gr = types.ModuleType("gradio")
        mock_gr.Progress = lambda: lambda *a, **k: None
        mock_gr.Blocks = lambda **k: type('ctx', (), {'__enter__': lambda s: s, '__exit__': lambda *a: None})()
        mock_gr.Markdown = lambda *a, **k: None
        mock_gr.Tab = lambda *a, **k: type('ctx', (), {'__enter__': lambda s: s, '__exit__': lambda *a: None})()
        mock_gr.Row = lambda *a, **k: type('ctx', (), {'__enter__': lambda s: s, '__exit__': lambda *a: None})()
        mock_gr.Column = lambda *a, **k: type('ctx', (), {'__enter__': lambda s: s, '__exit__': lambda *a: None})()
        mock_gr.File = lambda **k: None
        mock_gr.Slider = lambda *a, **k: None
        mock_gr.Button = lambda *a, **k: type('b', (), {'click': lambda *a, **k: None})()
        mock_gr.Textbox = lambda **k: None
        mock_gr.ColorPicker = lambda **k: None
        mock_gr.Radio = lambda **k: None
        sys.modules['gradio'] = mock_gr

        from playlist_maker import (
            make_animation_frames, parse_color, get_tmp, unique_path,
            ANIM_FPS, get_duration, run_cmd, FFMPEG
        )

        tmp_dir = get_tmp("auto_vid")
        frames_dir = os.path.join(tmp_dir, "frames")
        color_tuple = parse_color(DEFAULT_COLOR)

        # 배경 이미지: music_drop 폴더에 bg.png/bg.jpg가 있으면 사용, 없으면 자동 생성
        bg_src = None
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            bg_check = os.path.join(WATCH_DIR, f"bg{ext}")
            if os.path.exists(bg_check):
                bg_copy = os.path.join(tmp_dir, f"bg{ext}")
                shutil.copy2(bg_check, bg_copy)
                bg_src = bg_copy
                log.info(f"배경 이미지 사용: {bg_check}")
                break

        # 배경 없으면 스타일에 맞게 자동 생성
        if bg_src is None:
            from youtube_uploader import generate_background
            bg_src = os.path.join(tmp_dir, f"auto_bg_{style_name}.png")
            generate_background(style_name, style_info, bg_src)
            log.info(f"배경 자동 생성: {style_name} 스타일")

        # 스타일에 맞는 텍스트 색상
        color_tuple = parse_color(style_info.get("text_color", DEFAULT_COLOR))

        # 오디오 분석은 원본 MP3로 (루프 전 원본이 더 빠름)
        duration = get_duration(loop_mp3_path) or target_sec
        max_analyze_sec = min(duration, 600)
        analyze_frames = int(max_analyze_sec * ANIM_FPS)

        log.info(f"프레임 생성 중... ({analyze_frames}개)")
        frame_pattern = make_animation_frames(
            bg_src, color_tuple, frames_dir, safe_mp3, tmp_dir, analyze_frames, None)

        # MP4 인코딩
        video_filename = f"playlist_{style_name}_{int(time.time())}.mp4"
        out_path = unique_path(os.path.join(style_folder, video_filename))

        mp3_for_video = os.path.join(tmp_dir, "audio.mp3")
        shutil.copy2(loop_mp3_path, mp3_for_video)

        cmd = [FFMPEG, "-y",
               "-stream_loop", "-1",
               "-framerate", str(ANIM_FPS), "-i", frame_pattern,
               "-i", mp3_for_video,
               "-c:v", "libx264", "-preset", "medium", "-crf", "23",
               "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k",
               "-shortest", "-movflags", "+faststart",
               out_path]

        log.info("ffmpeg 인코딩 중...")
        result = run_cmd(cmd, timeout=7200)

        if not result or result.returncode != 0 or not os.path.exists(out_path):
            log.error("MP4 생성 실패")
            return False

        size_mb = os.path.getsize(out_path) / 1024 / 1024
        log.info(f"MP4 완성: {out_path} ({size_mb:.1f} MB)")

        # 프레임 정리
        try:
            shutil.rmtree(frames_dir)
        except:
            pass

    except Exception as e:
        log.error(f"MP4 생성 중 오류: {e}")
        import traceback
        log.error(traceback.format_exc())
        return False

    # 4단계: YouTube 업로드
    log.info("YouTube 업로드 중...")
    playlist_name = style_info.get("playlist", "")
    upload_ok, upload_msg = upload_to_youtube(
        out_path, auto_title, auto_desc, tags,
        category=style_info.get("category", "10"),
        privacy=DEFAULT_PRIVACY,
        playlist_name=playlist_name
    )
    log.info(upload_msg)

    # 5단계: 원본 MP3를 done 폴더로 이동
    done_path = os.path.join(DONE_DIR, filename)
    try:
        shutil.move(mp3_path, done_path)
        log.info(f"원본 이동: {done_path}")
    except:
        log.info("원본 파일 이동 실패 (수동으로 옮겨주세요)")

    # 루프 MP3 삭제 (용량 절약)
    try:
        os.remove(loop_mp3_path)
    except:
        pass

    log.info(f"===== 처리 완료: {filename} =====\n")
    return True

# ============================================================
# 폴더 감시
# ============================================================

def watch_folder():
    """폴더를 주기적으로 확인하여 새 MP3 파일 처리"""
    log.info(f"=" * 50)
    log.info(f"폴더 감시 시작!")
    log.info(f"감시 폴더: {WATCH_DIR}")
    log.info(f"MP3 파일을 이 폴더에 넣으면 자동으로 처리됩니다.")
    log.info(f"배경 이미지를 사용하려면 bg.png 또는 bg.jpg를 같은 폴더에 넣으세요.")
    log.info(f"종료: Ctrl+C")
    log.info(f"=" * 50)

    processed = set()

    while True:
        try:
            # 폴더 내 MP3 파일 검색
            for f in os.listdir(WATCH_DIR):
                if not f.lower().endswith(".mp3"):
                    continue
                if f in processed:
                    continue

                mp3_path = os.path.join(WATCH_DIR, f)

                # 파일이 아직 다운로드 중인지 확인 (크기 변화 체크)
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

                # 처리 시작
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

        time.sleep(5)  # 5초마다 폴더 확인

if __name__ == "__main__":
    watch_folder()
