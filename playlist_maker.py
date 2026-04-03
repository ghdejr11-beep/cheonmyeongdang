import gradio as gr
import os, shutil, subprocess, tempfile, json
from PIL import Image, ImageDraw, ImageFont
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

def run_cmd(cmd):
    try:
        return subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding='utf-8', errors='replace',
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

def make_frame(bg_src, color_tuple, frame_path):
    W, H = 1920, 1080

    # 배경 생성
    if bg_src and os.path.exists(bg_src):
        try:
            img = Image.open(bg_src).convert("RGB")
            iw, ih = img.size
            if iw/ih > W/H:
                new_h, new_w = H, int(H * iw/ih)
            else:
                new_w, new_h = W, int(W * ih/iw)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left, top = (new_w-W)//2, (new_h-H)//2
            img = img.crop((left, top, left+W, top+H))
            dark = Image.new("RGB", (W, H), (0, 0, 0))
            img = Image.blend(img, dark, alpha=0.35)
        except Exception as e:
            print(f"[경고] 배경 이미지 로드 실패: {e}")
            img = Image.new("RGB", (W, H), (13, 13, 13))
    else:
        img = Image.new("RGB", (W, H), (13, 13, 13))

    draw = ImageDraw.Draw(img)

    # 폰트 로드
    font = None
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
                font = ImageFont.truetype(fc, 120)
                break
            except:
                continue
    if font is None:
        try:
            font = ImageFont.load_default(size=120)
        except:
            font = ImageFont.load_default()

    r, g, b = color_tuple
    text = "Play List"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (W - tw) // 2
    ty = (H - th) // 2

    draw.text((tx+4, ty+4), text, font=font, fill=(0, 0, 0))
    draw.text((tx, ty), text, font=font, fill=(r, g, b))
    draw.rectangle([W//2-200, ty+th+25, W//2+200, ty+th+30], fill=(r, g, b))

    # PNG로 저장 (무손실, ffmpeg 호환성 더 좋음)
    img.save(frame_path, quality=95)
    print(f"[정보] 프레임 저장됨: {frame_path} ({os.path.getsize(frame_path)} bytes)")

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

    progress(0.1, desc="배경 프레임 생성 중..")
    tmp_dir = get_tmp(f"vid{slot}")
    frame_path = os.path.join(tmp_dir, "frame.png")

    # 배경 이미지를 안전한 경로로 복사
    bg_src = None
    if bg_image is not None:
        bp = bg_image.name if hasattr(bg_image, 'name') else str(bg_image)
        if bp and os.path.exists(bp):
            bg_copy = os.path.join(tmp_dir, "bg" + os.path.splitext(bp)[1])
            shutil.copy2(bp, bg_copy)
            bg_src = bg_copy

    make_frame(bg_src, parse_color(text_color), frame_path)

    # 프레임 파일 검증
    if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
        return None, "프레임 이미지 생성 실패"

    progress(0.4, desc="MP4 변환 중..")
    mp3_src = mp3_file.name if hasattr(mp3_file, 'name') else str(mp3_file)
    mp3_safe = os.path.join(tmp_dir, "audio.mp3")
    shutil.copy2(mp3_src, mp3_safe)

    suffix = f"_{slot}" if slot else ""
    out_path = unique_path(os.path.join(OUTPUT_DIR, f"playlist_video{suffix}.mp4"))

    # ffmpeg: -framerate 1 추가, -pix_fmt yuv420p 추가 (호환성)
    cmd = [FFMPEG, "-y",
           "-loop", "1", "-framerate", "1", "-i", frame_path,
           "-i", mp3_safe,
           "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
           "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart",
           out_path]

    print(f"[정보] ffmpeg 명령어: {' '.join(cmd)}")
    result = run_cmd(cmd)

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

    progress(0.5, desc="2단계: MP4 변환 중..")
    video_result, video_msg = make_video(FakeFile(loop_result), bg_safe, color, progress, slot=slot)
    return video_result, f"완료!\n\n[1단계]\n{loop_msg}\n\n[2단계]\n{video_msg}"

def run_all_1(f, h, bg, c, progress=gr.Progress()): return run_all(f, h, bg, c, progress, slot=1)
def run_all_2(f, h, bg, c, progress=gr.Progress()): return run_all(f, h, bg, c, progress, slot=2)

with gr.Blocks(title="Playlist Maker") as app:
    gr.Markdown(f"# Playlist Maker\n2개 병렬처리 | 폴더: `{OUTPUT_DIR}`")

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
                v_btn = gr.Button("영상 만들기", variant="primary", size="lg")
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
