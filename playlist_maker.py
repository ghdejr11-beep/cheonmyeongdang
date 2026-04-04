import gradio as gr
import os, shutil, subprocess, tempfile, json, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "playlist_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def unique_path(path):
    """같은 이름 파일이 있으면 뒤에 숫자를 붙여서 고유 경로 반환"""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 1
    while os.path.exists(f"{base}_{n}{ext}"):
        n += 1
    return f"{base}_{n}{ext}"

def find_ffmpeg():
    for path in [r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\Program Files\ffmpeg\bin\ffmpeg.exe", "ffmpeg"]:
        try:
            subprocess.run([path, "-version"], capture_output=True, check=True)
            return path
        except:
            continue
    return "ffmpeg"

def find_ffprobe():
    for path in [r"C:\ffmpeg\bin\ffprobe.exe", r"C:\Program Files\ffmpeg\bin\ffprobe.exe", "ffprobe"]:
        try:
            subprocess.run([path, "-version"], capture_output=True, check=True)
            return path
        except:
            continue
    return "ffprobe"

FFMPEG = find_ffmpeg()
FFPROBE = find_ffprobe()

# 애니메이션 설정
ANIM_FPS = 30
ANIM_LOOP_SEC = 8  # 8초 루프 애니메이션
ANIM_TOTAL_FRAMES = ANIM_FPS * ANIM_LOOP_SEC  # 240프레임

def get_tmp(sub=""):
    """ASCII-only 임시 경로 사용 - 한글 경로 회피"""
    for base in [os.path.join("C:\\", "pl"), os.path.join(tempfile.gettempdir(), "pl")]:
        path = os.path.join(base, sub) if sub else base
        try:
            os.makedirs(path, exist_ok=True)
            test = os.path.join(path, "_test.txt")
            open(test, "w").close()
            os.remove(test)
            return path
        except:
            continue
    return tempfile.mkdtemp()

def run_cmd(cmd, timeout=600):
    try:
        return subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding='utf-8', errors='replace', timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
    except:
        return None

def get_duration(path):
    probe = run_cmd([FFPROBE, "-v", "quiet", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", path])
    if probe and probe.stdout and probe.stdout.strip():
        try:
            return float(probe.stdout.strip())
        except:
            pass
    result = run_cmd([FFMPEG, "-i", path])
    if result:
        for line in ((result.stdout or "") + (result.stderr or "")).split("\n"):
            if "Duration" in line:
                try:
                    t = line.split("Duration:")[1].split(",")[0].strip()
                    h, m, s = t.split(":")
                    return int(h)*3600 + int(m)*60 + float(s)
                except:
                    pass
    return None

def parse_color(c):
    if not c:
        return (255, 255, 255)
    c = str(c).strip()
    try:
        if c.startswith("rgba"):
            v = c.replace("rgba(","").replace(")","").split(",")
            return (int(float(v[0])), int(float(v[1])), int(float(v[2])))
        if c.startswith("rgb"):
            v = c.replace("rgb(","").replace(")","").split(",")
            return (int(float(v[0])), int(float(v[1])), int(float(v[2])))
        if c.startswith("#"):
            h = c.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0,2,4))
    except:
        pass
    return (255, 255, 255)

def generate_stars(count=60):
    """랜덤 별/파티클 위치 생성 (한번 생성 후 재사용)"""
    stars = []
    for _ in range(count):
        stars.append({
            'x': random.randint(0, 1919),
            'y': random.randint(0, 1079),
            'size': random.uniform(1, 3),
            'speed': random.uniform(0.3, 1.0),  # 깜빡이는 속도
            'phase': random.uniform(0, 2 * math.pi),  # 시작 위상
        })
    return stars

def draw_stars(draw, stars, frame_idx, color_tuple):
    """프레임마다 별을 그려서 반짝이는 효과"""
    r, g, b = color_tuple
    t = frame_idx / ANIM_FPS
    for s in stars:
        brightness = 0.3 + 0.7 * ((math.sin(t * s['speed'] * 4 + s['phase']) + 1) / 2)
        alpha = int(255 * brightness)
        sr = int(r * brightness)
        sg = int(g * brightness)
        sb = int(b * brightness)
        sz = s['size']
        draw.ellipse([s['x']-sz, s['y']-sz, s['x']+sz, s['y']+sz],
                     fill=(sr, sg, sb))

def draw_eq_bars(draw, frame_idx, color_tuple, y_base):
    """하단 이퀄라이저 바 애니메이션"""
    r, g, b = color_tuple
    bar_count = 40
    bar_width = 12
    bar_gap = 6
    total_w = bar_count * (bar_width + bar_gap)
    start_x = (1920 - total_w) // 2
    t = frame_idx / ANIM_FPS

    for i in range(bar_count):
        phase = i * 0.3
        height = 10 + 30 * ((math.sin(t * 2.5 + phase) + 1) / 2)
        height += 8 * ((math.sin(t * 4.1 + phase * 1.7) + 1) / 2)
        x = start_x + i * (bar_width + bar_gap)
        brightness = 0.5 + 0.5 * ((math.sin(t * 3 + phase) + 1) / 2)
        br = int(r * brightness)
        bg_ = int(g * brightness)
        bb = int(b * brightness)
        draw.rectangle([x, y_base - height, x + bar_width, y_base],
                       fill=(br, bg_, bb))

def make_base_image(bg_src, W=1920, H=1080):
    """배경 이미지 생성 (줌용으로 약간 크게)"""
    # 줌 효과를 위해 10% 크게 만듦
    ZW, ZH = int(W * 1.1), int(H * 1.1)

    if bg_src and os.path.exists(bg_src):
        try:
            img = Image.open(bg_src).convert("RGB")
            iw, ih = img.size
            if iw/ih > ZW/ZH:
                new_h, new_w = ZH, int(ZH * iw/ih)
            else:
                new_w, new_h = ZW, int(ZW * ih/iw)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left, top = (new_w-ZW)//2, (new_h-ZH)//2
            img = img.crop((left, top, left+ZW, top+ZH))
            dark = Image.new("RGB", (ZW, ZH), (0, 0, 0))
            img = Image.blend(img, dark, alpha=0.35)
        except Exception as e:
            print(f"[경고] 배경 이미지 로드 실패: {e}")
            img = Image.new("RGB", (ZW, ZH), (13, 13, 13))
    else:
        img = Image.new("RGB", (ZW, ZH), (13, 13, 13))

    return img

def get_font():
    """폰트 로드"""
    for fc in [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(fc):
            try:
                return ImageFont.truetype(fc, 120)
            except:
                continue
    try:
        return ImageFont.load_default(size=120)
    except:
        return ImageFont.load_default()

def make_animated_frame(base_img, font, stars, color_tuple, frame_idx, W=1920, H=1080):
    """한 프레임 생성 (별 반짝임 + 텍스트 글로우 + 느린 줌 + 이퀄라이저)"""
    r, g, b = color_tuple
    t = frame_idx / ANIM_TOTAL_FRAMES  # 0.0 ~ 1.0 진행률

    # 1) 느린 줌 효과 (살짝 줌인/줌아웃 반복)
    zoom = 1.0 + 0.03 * math.sin(t * 2 * math.pi)  # 1.0 ~ 1.03 줌
    ZW, ZH = base_img.size
    crop_w = int(W / zoom)
    crop_h = int(H / zoom)
    left = (ZW - crop_w) // 2
    top = (ZH - crop_h) // 2
    frame = base_img.crop((left, top, left + crop_w, top + crop_h))
    frame = frame.resize((W, H), Image.LANCZOS)

    draw = ImageDraw.Draw(frame)

    # 2) 반짝이는 별
    draw_stars(draw, stars, frame_idx, color_tuple)

    # 3) 텍스트 글로우 효과 (밝기 펄스)
    text = "Play List"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (W - tw) // 2
    ty = (H - th) // 2 - 40  # 이퀄라이저 공간 확보를 위해 약간 위로

    glow_strength = 0.7 + 0.3 * math.sin(frame_idx / ANIM_FPS * 2)
    gr_ = int(r * glow_strength)
    gg = int(g * glow_strength)
    gb = int(b * glow_strength)

    # 그림자
    draw.text((tx+4, ty+4), text, font=font, fill=(0, 0, 0))
    # 글로우 (약간 큰 텍스트 느낌)
    for offset in [(2,0),(-2,0),(0,2),(0,-2)]:
        draw.text((tx+offset[0], ty+offset[1]), text, font=font,
                  fill=(gr_//3, gg//3, gb//3))
    # 메인 텍스트
    draw.text((tx, ty), text, font=font, fill=(gr_, gg, gb))

    # 구분선
    line_alpha = 0.5 + 0.5 * math.sin(frame_idx / ANIM_FPS * 1.5)
    lr = int(r * line_alpha)
    lg = int(g * line_alpha)
    lb = int(b * line_alpha)
    draw.rectangle([W//2-200, ty+th+25, W//2+200, ty+th+30], fill=(lr, lg, lb))

    # 4) 이퀄라이저 바
    eq_y = ty + th + 80
    draw_eq_bars(draw, frame_idx, color_tuple, eq_y)

    return frame

def make_animation_frames(bg_src, color_tuple, frames_dir, progress_cb=None):
    """모든 애니메이션 프레임 생성"""
    W, H = 1920, 1080
    base_img = make_base_image(bg_src, W, H)
    font = get_font()
    stars = generate_stars(60)

    os.makedirs(frames_dir, exist_ok=True)

    for i in range(ANIM_TOTAL_FRAMES):
        frame = make_animated_frame(base_img, font, stars, color_tuple, i, W, H)
        frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
        frame.save(frame_path)
        if progress_cb and i % 30 == 0:
            progress_cb(i / ANIM_TOTAL_FRAMES)

    print(f"[정보] {ANIM_TOTAL_FRAMES}개 프레임 생성 완료: {frames_dir}")
    return os.path.join(frames_dir, "frame_%04d.png")

def process_single_file(args):
    idx, src_path, hours, tmp_base = args
    tmp_dir = get_tmp(f"w{idx:03d}")

    safe_src = os.path.join(tmp_dir, "input.mp3")
    shutil.copy2(src_path, safe_src)

    src_sec = get_duration(safe_src)
    if not src_sec:
        return idx, None, f"[{idx+1}번] 파일 길이 확인 실패"

    target_sec = int(hours * 3600)
    repeat = max(1, int(target_sec / src_sec) + 1)

    list_txt = os.path.join(tmp_dir, "loop.txt")
    with open(list_txt, "w", encoding="utf-8") as f:
        for _ in range(repeat):
            f.write(f"file '{safe_src}'\n")

    tmp_long = os.path.join(tmp_dir, "long.mp3")
    run_cmd([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", tmp_long])

    out_name = f"{idx+1:02d}_{int(hours)}h.mp3"
    out_path = unique_path(os.path.join(OUTPUT_DIR, out_name))
    run_cmd([FFMPEG, "-y", "-i", tmp_long, "-t", str(target_sec), "-c", "copy", out_path])

    if not os.path.exists(out_path):
        return idx, None, f"[{idx+1}번] 파일 생성 실패"

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    return idx, out_path, f"[{idx+1}번] {out_name} ({size_mb:.1f} MB)"

def loop_mp3(mp3_files, hours, progress=gr.Progress()):
    if not mp3_files:
        return None, "MP3 파일을 선택해주세요."

    total = len(mp3_files)
    progress(0, desc=f"총 {total}개 준비 중..")

    src_paths = [fp.name if hasattr(fp, 'name') else str(fp) for fp in mp3_files]
    tasks = [(i, src_paths[i], hours, "") for i in range(total)]

    results = [None] * total
    messages = []
    completed = 0

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(process_single_file, task): task[0] for task in tasks}
        for future in as_completed(futures):
            idx, out_path, msg = future.result()
            results[idx] = out_path
            messages.append(msg)
            completed += 1
            progress(completed / total, desc=f"{completed}/{total} 완료...")

    success = [r for r in results if r]
    status = f"{len(success)}/{total}개 완성!\n폴더: {OUTPUT_DIR}\n\n" + "\n".join(sorted(messages))
    progress(1.0)
    return success[0] if success else None, status

def make_video(mp3_file, bg_image, text_color, progress=gr.Progress(), slot=0):
    if not mp3_file:
        return None, "MP3 파일을 선택해주세요."

    progress(0.05, desc="애니메이션 프레임 생성 중 (1/2)..")
    tmp_dir = get_tmp(f"vid{slot}")
    frames_dir = os.path.join(tmp_dir, "frames")

    # 배경 이미지를 안전한 경로로 복사
    bg_src = None
    if bg_image is not None:
        bp = bg_image.name if hasattr(bg_image, 'name') else str(bg_image)
        if bp and os.path.exists(bp):
            bg_copy = os.path.join(tmp_dir, "bg" + os.path.splitext(bp)[1])
            shutil.copy2(bp, bg_copy)
            bg_src = bg_copy

    color_tuple = parse_color(text_color)

    def frame_progress(p):
        progress(0.05 + p * 0.45, desc=f"프레임 생성 중.. {int(p*100)}%")

    frame_pattern = make_animation_frames(bg_src, color_tuple, frames_dir, frame_progress)

    # 프레임 파일 검증
    first_frame = os.path.join(frames_dir, "frame_0000.png")
    if not os.path.exists(first_frame):
        return None, "프레임 이미지 생성 실패"

    progress(0.55, desc="MP4 영상 인코딩 중 (2/2)..")
    mp3_src = mp3_file.name if hasattr(mp3_file, 'name') else str(mp3_file)
    mp3_safe = os.path.join(tmp_dir, "audio.mp3")
    shutil.copy2(mp3_src, mp3_safe)

    suffix = f"_{slot}" if slot else ""
    out_path = unique_path(os.path.join(OUTPUT_DIR, f"playlist_video{suffix}.mp4"))

    # -stream_loop -1: 8초 애니메이션을 무한 루프하여 오디오 길이에 맞춤
    cmd = [FFMPEG, "-y",
           "-stream_loop", "-1",
           "-framerate", str(ANIM_FPS), "-i", frame_pattern,
           "-i", mp3_safe,
           "-c:v", "libx264", "-preset", "medium", "-crf", "23",
           "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart",
           out_path]

    print(f"[정보] ffmpeg 명령어: {' '.join(cmd)}")
    result = run_cmd(cmd, timeout=3600)

    if not result or result.returncode != 0 or not os.path.exists(out_path):
        err = ""
        if result:
            err = ((result.stdout or "") + (result.stderr or ""))[-500:]
        return None, f"영상 생성 실패:\n{err}"

    # 검증
    probe = run_cmd([FFPROBE, "-v", "quiet", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", out_path])
    dur = 0
    if probe and probe.stdout and probe.stdout.strip():
        try:
            dur = float(probe.stdout.strip())
        except:
            pass
    if dur < 1:
        return None, "영상 재생 시간이 너무 짧습니다"

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    progress(1.0)

    # 프레임 폴더 정리
    try:
        shutil.rmtree(frames_dir)
    except:
        pass

    return out_path, f"완성!\n경로: {out_path}\n크기: {size_mb:.1f} MB\n길이: {dur:.0f}초"

def run_all(mp3_files, hours, bg, color, progress=gr.Progress(), slot=0):
    progress(0, desc="1단계: MP3 루프 중..")
    loop_result, loop_msg = loop_mp3(mp3_files, hours, progress)
    if not loop_result:
        return None, f"루프 실패:\n{loop_msg}"

    class FakeFile:
        def __init__(self, p): self.name = p

    bg_safe = None
    if bg is not None:
        bp = bg.name if hasattr(bg, 'name') else str(bg)
        if bp and os.path.exists(bp):
            ext = os.path.splitext(bp)[1] or ".png"
            bc = os.path.join(get_tmp(), f"bg{slot}{ext}")
            shutil.copy2(bp, bc)
            bg_safe = FakeFile(bc)

    progress(0.5, desc="2단계: 애니메이션 MP4 생성 중..")
    video_result, video_msg = make_video(FakeFile(loop_result), bg_safe, color, progress, slot=slot)
    return video_result, f"완료!\n\n[1단계]\n{loop_msg}\n\n[2단계]\n{video_msg}"

def run_all_1(f, h, bg, c, progress=gr.Progress()): return run_all(f, h, bg, c, progress, slot=1)
def run_all_2(f, h, bg, c, progress=gr.Progress()): return run_all(f, h, bg, c, progress, slot=2)

with gr.Blocks(title="Playlist Maker") as app:
    gr.Markdown(f"# Playlist Maker\n애니메이션 효과 포함 | 2개 병렬처리 | 폴더: `{OUTPUT_DIR}`")

    with gr.Tab("MP3 루프 만들기"):
        with gr.Row():
            mp3_input = gr.File(label="MP3 파일 (여러 개 가능)", file_types=[".mp3"], file_count="multiple")
            with gr.Column():
                hours_slider = gr.Slider(1, 12, value=12, step=0.5, label="목표 시간")
                loop_btn = gr.Button("루프 시작", variant="primary", size="lg")
        loop_status = gr.Textbox(label="상태", lines=5)
        loop_out = gr.File(label="완성된 MP3")
        loop_btn.click(loop_mp3, [mp3_input, hours_slider], [loop_out, loop_status])

    with gr.Tab("MP4 영상 만들기"):
        with gr.Row():
            with gr.Column():
                v_mp3 = gr.File(label="MP3 파일", file_types=[".mp3"])
                v_bg = gr.File(label="배경 사진 (선택)", file_types=["image"])
                v_color = gr.ColorPicker(label="텍스트 색상", value="#ffffff")
                v_btn = gr.Button("애니메이션 영상 만들기", variant="primary", size="lg")
            with gr.Column():
                v_status = gr.Textbox(label="상태", lines=4)
                v_out = gr.File(label="완성된 MP4")
        v_btn.click(make_video, [v_mp3, v_bg, v_color], [v_out, v_status])

    with gr.Tab("한번에 처리 1번"):
        with gr.Row():
            with gr.Column():
                a1_mp3 = gr.File(label="MP3 파일", file_types=[".mp3"], file_count="multiple")
                a1_hours = gr.Slider(1, 12, value=12, step=0.5, label="목표 시간")
                a1_bg = gr.File(label="배경 사진 (선택)", file_types=["image"])
                a1_color = gr.ColorPicker(label="텍스트 색상", value="#ffffff")
                a1_btn = gr.Button("1번 시작", variant="primary", size="lg")
            with gr.Column():
                a1_status = gr.Textbox(label="상태", lines=6)
                a1_out = gr.File(label="완성된 MP4")
        a1_btn.click(run_all_1, [a1_mp3, a1_hours, a1_bg, a1_color], [a1_out, a1_status])

    with gr.Tab("한번에 처리 2번"):
        with gr.Row():
            with gr.Column():
                a2_mp3 = gr.File(label="MP3 파일", file_types=[".mp3"], file_count="multiple")
                a2_hours = gr.Slider(1, 12, value=12, step=0.5, label="목표 시간")
                a2_bg = gr.File(label="배경 사진 (선택)", file_types=["image"])
                a2_color = gr.ColorPicker(label="텍스트 색상", value="#ffffff")
                a2_btn = gr.Button("2번 시작", variant="primary", size="lg")
            with gr.Column():
                a2_status = gr.Textbox(label="상태", lines=6)
                a2_out = gr.File(label="완성된 MP4")
        a2_btn.click(run_all_2, [a2_mp3, a2_hours, a2_bg, a2_color], [a2_out, a2_status])

app.launch(share=False, inbrowser=True, allowed_paths=[OUTPUT_DIR])
