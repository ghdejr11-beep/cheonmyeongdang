# music_pipeline 통합 가이드

기존 `auto_watcher.py` / `lyrics_watcher.py` / `youtube_uploader.py` (노트북의
`C:\Users\쿤\Desktop\cheonmyeongdang\`) 에 **최소한의 수정**으로 붙이는
방법입니다. 파일을 새로 쓰지 않고 import 만 추가합니다.

## 1. 설치 (1회)

노트북에서:

```powershell
cd C:\Users\쿤\Desktop\cheonmyeongdang
git pull origin claude/add-video-generation-ure6j
```

또는 이 저장소의 `music_pipeline/` 폴더를 그대로 복사해서
`C:\Users\쿤\Desktop\cheonmyeongdang\music_pipeline\` 로 붙여넣기.

Python 패키지 설치:

```powershell
pip install Pillow
```

## 2. YouTube 에 용도 플레이리스트 미리 생성

아래 12개 플리를 YouTube Studio 에서 **이 이름 그대로** 먼저 만들어야
자동 추가가 동작합니다 (스튜디오 > 콘텐츠 > 플레이리스트 > 새 플리):

- 📚 공부할 때 듣는 음악
- 💻 작업할 때 듣는 음악
- 🌙 잠 올 때 듣는 음악
- 🚗 운전할 때 듣는 음악
- ☕ 카페 분위기 만드는 음악
- 🚶 산책할 때 듣는 음악
- 🌧️ 비 오는 날 듣는 음악
- 🌅 새벽에 듣는 음악
- 🌃 밤에 듣는 음악
- 💚 지친 하루 힐링
- 💪 운동할 때 듣는 음악
- 💔 이별 후 듣는 음악

설명·썸네일 없이 "비공개" 로 만들어두면 충분합니다 (영상이 쌓이면
나중에 공개 전환).

---

## 3. 코드 패치

### 3-1. `youtube_uploader.py` 상단에 import 추가

```python
# 파일 맨 위 import 아래쪽에 추가
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from music_pipeline.enhancements.ai_label import (
    inject_ai_label, append_human_input_footer,
)
from music_pipeline.enhancements.purpose_playlists import (
    get_all_playlists_for,
)
from music_pipeline.enhancements.pinned_comment import (
    build_pinned_comment_text, post_pinned_comment,
)
```

### 3-2. `upload_to_youtube()` 내부 — AI 라벨 주입 + 설명 푸터

기존:

```python
body = {
    "snippet": {
        "title": title[:100],
        "description": description[:5000],
        ...
    },
    "status": {
        "privacyStatus": privacy,
        "selfDeclaredMadeForKids": False,
    },
}
```

→ 수정:

```python
# 스타일명을 역추출 (tags 에 있으면)
style_name = (tags[0] if tags else "general").lower().replace("-", "").replace(" ", "")
description = append_human_input_footer(description, style_name)

body = {
    "snippet": {
        "title": title[:100],
        "description": description[:5000],
        ...
    },
    "status": {
        "privacyStatus": privacy,
        "selfDeclaredMadeForKids": False,
    },
}
body = inject_ai_label(body)   # containsSyntheticMedia=True
```

### 3-3. `upload_to_youtube()` 하단 — 다중 플리 + 고정 댓글

기존:

```python
if playlist_name:
    playlist_id = find_playlist_id(service, playlist_name)
    if playlist_id:
        pl_ok, pl_msg = add_to_playlist(service, playlist_id, video_id)
        result_msg += f"\n재생목록 '{playlist_name}'에 추가 완료!"
```

→ 수정:

```python
# 장르 플리 + 용도 플리들 모두 추가
all_playlists = get_all_playlists_for(style_name, playlist_name)
for pl in all_playlists:
    pl_id = find_playlist_id(service, pl)
    if pl_id:
        add_to_playlist(service, pl_id, video_id)
        result_msg += f"\n  ✓ {pl}"

# 고정 댓글
try:
    channel_url = f"https://youtube.com/playlist?list={find_playlist_id(service, playlist_name) or ''}"
    comment_text = build_pinned_comment_text(
        style_name=style_name,
        video_title=title,
        playlist_url=channel_url,
    )
    post_pinned_comment(service, video_id, comment_text)
    result_msg += f"\n  ✓ 고정 댓글 게시"
except Exception as e:
    result_msg += f"\n  ⚠ 고정 댓글 실패: {e}"
```

---

### 3-4. `auto_watcher.py` — 챕터 주입

`process_mp3` 함수에서 `auto_desc` 를 만든 직후:

```python
auto_desc = generate_description(style_name, style_info, metadata, DEFAULT_HOURS)

# ↓ 여기 추가
from music_pipeline.enhancements.chapter_generator import (
    build_loop_chapters, prepend_chapters,
)
chapters = build_loop_chapters(style_name, total_hours=DEFAULT_HOURS)
auto_desc = prepend_chapters(auto_desc, chapters)
```

---

### 3-5. `auto_watcher.py` / `lyrics_watcher.py` — 썸네일 첨부

업로드 직전에:

```python
from music_pipeline.enhancements.thumbnail_maker import make_thumbnail, pick_hook_kr

hook = pick_hook_kr(style_name)
thumb_path = os.path.join(tmp_dir, "thumb.png")
make_thumbnail(
    out_path=thumb_path,
    style_name=style_name,
    hook_kr=hook,
    duration_label=f"{int(DEFAULT_HOURS)} HOURS" if DEFAULT_HOURS >= 1 else "",
    bg_image_path=bg_path,  # 이미 있는 배경 이미지 재사용
)
```

그리고 `youtube_uploader.upload_to_youtube` 업로드 후:

```python
try:
    service.thumbnails().set(
        videoId=video_id,
        media_body=thumb_path,
    ).execute()
except Exception as e:
    log.warning(f"썸네일 첨부 실패: {e}")
```

---

### 3-6. `lyrics_watcher.py` — ASS 자막 전환

기존 `make_lyric_video` 함수에서 SRT 를 쓰는 부분:

```python
srt_path = None
if lrc_path and os.path.exists(lrc_path) and tmp_dir:
    srt_candidate = os.path.join(tmp_dir, "lyrics.srt")
    if convert_lrc_to_srt(lrc_path, srt_candidate):
        srt_path = srt_candidate
```

→ 대체:

```python
from music_pipeline.enhancements.ass_subtitles import lrc_to_ass, pick_style_for

ass_path = None
if lrc_path and os.path.exists(lrc_path) and tmp_dir:
    ass_candidate = os.path.join(tmp_dir, "lyrics.ass")
    if lrc_to_ass(lrc_path, ass_candidate, style=pick_style_for(style_name)):
        ass_path = ass_candidate
```

그리고 ffmpeg `subtitles` 필터를 `ass` 필터로 교체:

```python
# 기존
f"subtitles='{srt_safe}':force_style='FontName=Malgun Gothic,...'"

# → 대체
f"ass='{ass_safe}'"
```

ASS 는 내부에 스타일이 있으므로 `force_style` 불필요.

---

### 3-7. `lyrics_watcher.py` / `auto_watcher.py` — Shorts 크로스포스트

업로드 성공 후에 Shorts 도 함께:

```python
from music_pipeline.enhancements.shorts_extractor import (
    extract_shorts, build_shorts_title,
)

shorts_path = os.path.join(tmp_dir, "shorts.mp4")
ok, msg = extract_shorts(
    src_video=out_mp4,
    src_audio=mp3_path,
    out_path=shorts_path,
    ffmpeg=ffmpeg,
    ffprobe=ffmpeg.replace("ffmpeg", "ffprobe"),
    short_duration=50,
    hook_text=hook,  # 썸네일 만들 때 쓴 후킹 카피 재사용
)
if ok:
    shorts_title = build_shorts_title(auto_title, hook_text=hook)
    shorts_desc = f"{auto_title}\n\n전체 버전: https://youtube.com/watch?v={video_id}"
    upload_to_youtube(
        video_path=shorts_path,
        title=shorts_title,
        description=shorts_desc,
        tags=tags,
        category=style_info.get("category", "10"),
        privacy=DEFAULT_PRIVACY,
        playlist_name="",  # Shorts 는 플리 생략
    )
```

---

## 4. 최소 통합 (10분만에 P1 만)

시간이 없으면 **3-1 + 3-2 + 3-4 만** 반영해도 수익화 리스크 100%
방어 + 챕터 노출률 개선이 됩니다. 나머지는 이후 주말에 단계적으로.

## 5. 자체 테스트

각 모듈은 단독 실행 가능:

```powershell
cd C:\Users\쿤\Desktop\cheonmyeongdang\music_pipeline\enhancements
python ai_label.py
python chapter_generator.py
python ass_subtitles.py
python thumbnail_maker.py
python pinned_comment.py
python shorts_extractor.py
python purpose_playlists.py
```

각각 `✓ ... 자체 테스트 통과` 가 떠야 정상.
