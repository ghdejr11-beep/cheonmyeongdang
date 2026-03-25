"""
영상 자동 편집기
- 폴더 내 영상/음악 자동 합치기
- 자막 자동 추가 (OpenAI Whisper)
- 배경음악 선택적 추가
- 하이라이트 추출 선택적 기능
"""

import gradio as gr
import os
import glob
import tempfile
import traceback
import numpy as np
from pathlib import Path


# ── 파일 검색 유틸 ──────────────────────────────────────────────────────────

VIDEO_EXT = ["mp4", "avi", "mov", "mkv", "wmv", "flv", "m4v", "webm"]
AUDIO_EXT = ["mp3", "wav", "aac", "m4a", "ogg", "flac"]


def find_files(folder: str, extensions: list[str]) -> list[str]:
    files = []
    for ext in extensions:
        files += glob.glob(os.path.join(folder, f"*.{ext}"))
        files += glob.glob(os.path.join(folder, f"*.{ext.upper()}"))
    return sorted(set(files))


# ── 하이라이트 추출 ──────────────────────────────────────────────────────────

def extract_highlights(clip, count: int, duration: float):
    """오디오 에너지 기반 하이라이트 구간 추출"""
    try:
        from moviepy.editor import concatenate_videoclips

        if clip.audio is None:
            return None

        fps = 22050
        arr = clip.audio.to_soundarray(fps=fps)
        if arr.ndim > 1:
            arr = arr.mean(axis=1)

        win = int(fps * duration)
        step = win // 2
        candidates = []
        for i in range(0, len(arr) - win, step):
            energy = float(np.mean(arr[i : i + win] ** 2))
            candidates.append((energy, i / fps))

        candidates.sort(reverse=True)

        selected_times = []
        highlights = []
        for energy, t in candidates:
            if all(abs(t - used) > duration for used in selected_times):
                end = t + duration
                if end <= clip.duration:
                    highlights.append((t, clip.subclip(t, end)))
                    selected_times.append(t)
            if len(highlights) >= count:
                break

        if not highlights:
            return None

        highlights.sort(key=lambda x: x[0])
        return concatenate_videoclips([c for _, c in highlights])

    except Exception as e:
        print(f"[하이라이트 오류] {e}")
        return None


# ── 자막 추가 ────────────────────────────────────────────────────────────────

def add_subtitles(clip, model_size: str):
    """Whisper로 음성 인식 후 자막 합성"""
    try:
        import whisper
        from moviepy.editor import TextClip, CompositeVideoClip

        # 오디오 임시 저장
        tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_wav.close()
        clip.audio.write_audiofile(tmp_wav.name, logger=None)

        # Whisper 인식
        model = whisper.load_model(model_size)
        result = model.transcribe(tmp_wav.name)
        os.unlink(tmp_wav.name)

        # 자막 TextClip 생성
        sub_clips = []
        for seg in result.get("segments", []):
            text = seg["text"].strip()
            if not text:
                continue
            try:
                txt = (
                    TextClip(
                        text,
                        fontsize=30,
                        color="white",
                        stroke_color="black",
                        stroke_width=2,
                        method="caption",
                        size=(clip.w - 60, None),
                    )
                    .set_start(seg["start"])
                    .set_end(seg["end"])
                    .set_position(("center", 0.87), relative=True)
                )
                sub_clips.append(txt)
            except Exception:
                continue

        if sub_clips:
            return CompositeVideoClip([clip] + sub_clips)
        return clip

    except Exception as e:
        print(f"[자막 오류] {e}")
        return clip


# ── 메인 처리 함수 ────────────────────────────────────────────────────────────

def run_editor(
    input_folder,
    output_folder,
    output_name,
    use_subtitles,
    subtitle_model,
    use_bgm,
    bgm_path,
    bgm_volume,
    use_highlight,
    highlight_count,
    highlight_duration,
    progress=gr.Progress(),
):
    try:
        from moviepy.editor import (
            VideoFileClip,
            AudioFileClip,
            concatenate_videoclips,
            concatenate_audioclips,
            CompositeAudioClip,
        )

        # ── 입력 검증
        if not input_folder or not os.path.isdir(input_folder):
            return None, "❌ 입력 폴더 경로가 올바르지 않습니다."

        progress(0.05, desc="영상 파일 검색 중...")
        video_files = find_files(input_folder, VIDEO_EXT)
        if not video_files:
            return None, "❌ 폴더에서 영상 파일을 찾을 수 없습니다."

        file_list = "\n".join([f"  • {os.path.basename(f)}" for f in video_files])

        # ── 영상 로드
        progress(0.10, desc=f"영상 {len(video_files)}개 로딩 중...")
        clips = [VideoFileClip(f) for f in video_files]

        # ── 영상 합치기
        progress(0.25, desc="영상 합치는 중...")
        merged = concatenate_videoclips(clips, method="compose") if len(clips) > 1 else clips[0]

        # ── 하이라이트 추출 (선택)
        if use_highlight:
            progress(0.35, desc="하이라이트 추출 중...")
            hl = extract_highlights(merged, int(highlight_count), float(highlight_duration))
            if hl:
                merged = hl
            else:
                print("[경고] 하이라이트 추출 실패, 전체 영상 사용")

        # ── 자막 추가 (선택)
        if use_subtitles:
            if merged.audio is None:
                print("[경고] 오디오 없음 - 자막 생략")
            else:
                progress(0.50, desc=f"자막 생성 중... (Whisper {subtitle_model})")
                merged = add_subtitles(merged, subtitle_model)

        # ── 배경음악 추가 (선택)
        if use_bgm and bgm_path and os.path.isfile(bgm_path):
            progress(0.75, desc="배경음악 추가 중...")
            bgm = AudioFileClip(bgm_path).volumex(float(bgm_volume))

            # BGM 길이 맞추기 (루프 또는 자르기)
            if bgm.duration < merged.duration:
                loops = int(merged.duration / bgm.duration) + 1
                bgm = concatenate_audioclips([bgm] * loops).subclip(0, merged.duration)
            else:
                bgm = bgm.subclip(0, merged.duration)

            if merged.audio:
                mixed = CompositeAudioClip([merged.audio, bgm])
                merged = merged.set_audio(mixed)
            else:
                merged = merged.set_audio(bgm)

        # ── 저장
        progress(0.85, desc="영상 저장 중...")
        os.makedirs(output_folder or "output", exist_ok=True)
        name = output_name.strip() or "output"
        if not name.endswith(".mp4"):
            name += ".mp4"
        out_path = os.path.join(output_folder or "output", name)

        merged.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None, threads=4)

        for c in clips:
            c.close()

        progress(1.0, desc="완료!")
        msg = f"✅ 완료!\n\n📁 저장 위치: {out_path}\n\n📋 처리된 파일:\n{file_list}"
        return out_path, msg

    except Exception as e:
        return None, f"❌ 오류 발생:\n{e}\n\n{traceback.format_exc()}"


# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks(
    title="영상 자동 편집기",
    theme=gr.themes.Soft(primary_hue="indigo"),
    css="""
    #run-btn { background: linear-gradient(135deg,#4f46e5,#7c3aed); color:white; font-size:1.1rem; padding:12px; }
    .panel { border-radius:12px; }
    """,
) as demo:

    gr.Markdown(
        """
        # 🎬 영상 자동 편집기
        폴더의 영상을 자동으로 합치고, 자막·배경음악·하이라이트를 추가합니다.
        """
    )

    with gr.Row():
        # ── 왼쪽: 설정 패널
        with gr.Column(scale=1, elem_classes="panel"):
            gr.Markdown("### 📂 폴더 설정")
            input_folder = gr.Textbox(label="입력 폴더 경로", placeholder="/home/user/videos", value="")
            output_folder = gr.Textbox(label="출력 폴더 경로", placeholder="/home/user/output", value="output")
            output_name = gr.Textbox(label="출력 파일명", placeholder="완성본 (확장자 생략 가능)", value="완성본")

            gr.Markdown("---")
            gr.Markdown("### 📝 자막 설정")
            use_subtitles = gr.Checkbox(label="자막 자동 추가", value=False)
            with gr.Group(visible=False) as sub_group:
                subtitle_model = gr.Radio(
                    ["tiny", "base", "small", "medium"],
                    label="Whisper 모델 (클수록 정확, 느림)",
                    value="base",
                )
            use_subtitles.change(lambda v: gr.update(visible=v), use_subtitles, sub_group)

            gr.Markdown("---")
            gr.Markdown("### 🎵 배경음악 설정")
            use_bgm = gr.Checkbox(label="배경음악 추가", value=False)
            with gr.Group(visible=False) as bgm_group:
                bgm_path = gr.Textbox(label="음악 파일 경로", placeholder="/home/user/bgm.mp3")
                bgm_volume = gr.Slider(0.0, 1.0, value=0.3, step=0.05, label="음악 볼륨 (0~1)")
            use_bgm.change(lambda v: gr.update(visible=v), use_bgm, bgm_group)

            gr.Markdown("---")
            gr.Markdown("### ✨ 하이라이트 설정")
            use_highlight = gr.Checkbox(label="하이라이트만 추출", value=False)
            with gr.Group(visible=False) as hl_group:
                highlight_count = gr.Slider(1, 10, value=3, step=1, label="하이라이트 개수")
                highlight_duration = gr.Slider(3, 30, value=5, step=1, label="구간 길이 (초)")
            use_highlight.change(lambda v: gr.update(visible=v), use_highlight, hl_group)

            gr.Markdown("---")
            run_btn = gr.Button("▶ 편집 실행", elem_id="run-btn", variant="primary")

        # ── 오른쪽: 결과 패널
        with gr.Column(scale=1, elem_classes="panel"):
            gr.Markdown("### 🎥 결과")
            output_video = gr.Video(label="완성된 영상", interactive=False)
            status_msg = gr.Textbox(label="처리 상태", lines=8, interactive=False)

    run_btn.click(
        fn=run_editor,
        inputs=[
            input_folder, output_folder, output_name,
            use_subtitles, subtitle_model,
            use_bgm, bgm_path, bgm_volume,
            use_highlight, highlight_count, highlight_duration,
        ],
        outputs=[output_video, status_msg],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
