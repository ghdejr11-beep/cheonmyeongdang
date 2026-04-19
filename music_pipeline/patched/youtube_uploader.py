"""YouTube 자동 업로드 + 제목/설명 자동 생성 + 스타일별 폴더 분류 + 배경 자동 생성.

[2026-04 PATCHED VERSION — music_pipeline 통합본]
원본 대비 추가 사항:
  P1.1  AI 합성 라벨 자동 주입 (containsSyntheticMedia=True)
  P1.2  설명란 끝에 human-input 증거 푸터 자동 부착
  P2.4  thumbnail_path 매개변수 → 업로드 후 thumbnails().set() 자동 호출
  P2.5  업로드 직후 본인 댓글 자동 게시 (pin 시도)
  P3.8  장르 플리 + 용도 플리 12종 동시 추가
"""
import os, json, re, random, math, time, socket, ssl, http.client, sys
from pathlib import Path

# music_pipeline.enhancements import (스크립트 폴더 기준)
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

try:
    from music_pipeline.enhancements.ai_label import (
        inject_ai_label, append_human_input_footer,
    )
    from music_pipeline.enhancements.purpose_playlists import (
        get_all_playlists_for,
    )
    from music_pipeline.enhancements.pinned_comment import (
        build_pinned_comment_text, post_pinned_comment,
    )
    _ENHANCEMENTS_OK = True
except ImportError as _e:
    print(f"[경고] music_pipeline.enhancements 미설치: {_e}")
    print("       → 기본 동작으로 폴백 (AI 라벨/고정댓/다중 플리 비활성)")
    _ENHANCEMENTS_OK = False


# ============================================================
# 1) 스타일 감지 및 폴더 분류
# ============================================================

STYLE_KEYWORDS = {
    "lofi": {
        "keywords": ["lofi", "lo-fi", "lo fi", "chillhop", "study beat", "homework"],
        "folder": "LoFi",
        "tags": ["lofi", "lo-fi hip hop", "study music", "chill beats", "relaxing"],
        "category": "10",
        "playlist": "📚 Study Music",
        "bg_colors": [(25, 20, 40), (45, 30, 60)],
        "accent": (200, 160, 255),
        "text_color": "#c8a0ff",
    },
    "sleep": {
        "keywords": ["sleep", "ambient", "drone", "healing", "asmr", "deep sleep"],
        "folder": "Sleep_Ambient",
        "tags": ["sleep music", "ambient", "relaxing", "deep sleep", "calm"],
        "category": "10",
        "playlist": "🌙 Sleep Music",
        "bg_colors": [(5, 5, 25), (10, 15, 40)],
        "accent": (100, 140, 220),
        "text_color": "#80b0ff",
    },
    "rain": {
        "keywords": ["rain", "nature", "thunder", "ocean", "wave", "forest", "wind"],
        "folder": "Rain_Nature",
        "tags": ["rain sounds", "nature music", "sleep sounds", "relaxing rain"],
        "category": "10",
        "playlist": "🌧️ Rain Sounds",
        "bg_colors": [(15, 20, 25), (25, 35, 45)],
        "accent": (120, 170, 190),
        "text_color": "#90c0d0",
    },
    "meditation": {
        "keywords": ["meditation", "yoga", "mindful", "calm", "zen", "relax", "peaceful"],
        "folder": "Meditation",
        "tags": ["meditation music", "yoga music", "mindfulness", "relaxing"],
        "category": "10",
        "playlist": "🧘 Meditation",
        "bg_colors": [(10, 20, 15), (20, 40, 30)],
        "accent": (100, 190, 140),
        "text_color": "#70c090",
    },
    "jazz": {
        "keywords": ["jazz", "bossa", "swing", "cafe", "saxophone", "smooth jazz", "coffee"],
        "folder": "Jazz_Cafe",
        "tags": ["jazz", "cafe music", "smooth jazz", "bossa nova", "relaxing jazz"],
        "category": "10",
        "playlist": "☕ Cafe BGM",
        "bg_colors": [(30, 18, 10), (50, 30, 15)],
        "accent": (210, 170, 100),
        "text_color": "#d4aa64",
    },
    "study": {
        "keywords": ["study", "focus", "concentrate", "productive", "work"],
        "folder": "Study",
        "tags": ["study music", "focus music", "concentration", "productivity"],
        "category": "10",
        "playlist": "📚 Study Music",
        "bg_colors": [(15, 15, 30), (25, 25, 50)],
        "accent": (150, 180, 255),
        "text_color": "#a0b8ff",
    },
    "classical": {
        "keywords": ["classical", "piano", "orchestra", "symphony", "sonata", "chopin", "beethoven", "mozart"],
        "folder": "Classical",
        "tags": ["classical music", "piano", "classical piano", "orchestra", "relaxing classical"],
        "category": "10",
        "playlist": "📚 Study Music",
        "bg_colors": [(10, 10, 15), (20, 18, 25)],
        "accent": (220, 200, 160),
        "text_color": "#e0d0a0",
    },
    "electronic": {
        "keywords": ["edm", "electronic", "synth", "synthwave", "retrowave", "techno", "house", "trance"],
        "folder": "Electronic",
        "tags": ["electronic music", "synthwave", "EDM", "electronic", "synth"],
        "category": "10",
        "playlist": "🎵 AI 작사작곡",
        "bg_colors": [(10, 5, 20), (30, 10, 50)],
        "accent": (255, 50, 200),
        "text_color": "#ff40c8",
    },
    "pop": {
        "keywords": ["pop", "kpop", "k-pop", "ballad"],
        "folder": "Pop",
        "tags": ["pop music", "pop", "ballad", "music playlist"],
        "category": "10",
        "playlist": "🎵 AI 작사작곡",
        "bg_colors": [(20, 10, 25), (40, 15, 45)],
        "accent": (255, 120, 180),
        "text_color": "#ff80b8",
    },
}

DEFAULT_STYLE = {
    "folder": "General",
    "tags": ["playlist", "music", "relaxing", "background music"],
    "category": "10",
    "playlist": "🎵 AI 작사작곡",
    "bg_colors": [(13, 13, 13), (25, 25, 30)],
    "accent": (200, 200, 200),
    "text_color": "#ffffff",
}

# ============================================================
# 1.5) 스타일별 배경 자동 생성
# ============================================================

def generate_background(style_name, style_info, save_path, W=2112, H=1188):
    """스타일에 맞는 배경 이미지 자동 생성 (줌 효과 대비 약간 크게)"""
    from PIL import Image, ImageDraw

    bg1, bg2 = style_info.get("bg_colors", [(13, 13, 13), (25, 25, 30)])
    accent = style_info.get("accent", (200, 200, 200))

    img = Image.new("RGB", (W, H), bg1)
    draw = ImageDraw.Draw(img)

    # 그라데이션 배경
    for y in range(H):
        ratio = y / H
        r = int(bg1[0] + (bg2[0] - bg1[0]) * ratio)
        g = int(bg1[1] + (bg2[1] - bg1[1]) * ratio)
        b = int(bg1[2] + (bg2[2] - bg1[2]) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # 스타일별 장식 요소
    random.seed(42)

    if style_name in ("sleep", "lofi", "study", "classical"):
        for _ in range(120):
            x = random.randint(0, W)
            y = random.randint(0, H)
            sz = random.uniform(0.5, 2.5)
            brightness = random.uniform(0.2, 0.7)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(cr, cg, cb))

    elif style_name == "rain":
        for _ in range(80):
            x = random.randint(0, W)
            y = random.randint(0, H)
            length = random.randint(20, 80)
            brightness = random.uniform(0.1, 0.3)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.line([(x, y), (x - 3, y + length)], fill=(cr, cg, cb), width=1)

    elif style_name == "meditation":
        cx, cy = W // 2, H // 2
        for i in range(8):
            radius = 150 + i * 60
            brightness = 0.08 + 0.03 * (8 - i) / 8
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                        outline=(cr, cg, cb), width=1)

    elif style_name == "jazz":
        for _ in range(25):
            x = random.randint(0, W)
            y = random.randint(0, H)
            sz = random.randint(30, 100)
            brightness = random.uniform(0.03, 0.08)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(cr, cg, cb))

    elif style_name == "electronic":
        for x in range(0, W, 80):
            brightness = random.uniform(0.05, 0.15)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.line([(x, 0), (x, H)], fill=(cr, cg, cb), width=1)
        for y in range(0, H, 80):
            brightness = random.uniform(0.05, 0.15)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.line([(0, y), (W, y)], fill=(cr, cg, cb), width=1)

    elif style_name == "pop":
        for _ in range(15):
            x = random.randint(0, W)
            y = random.randint(0, H)
            sz = random.randint(50, 150)
            brightness = random.uniform(0.03, 0.06)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(cr, cg, cb))
        for _ in range(80):
            x = random.randint(0, W)
            y = random.randint(0, H)
            sz = random.uniform(1, 3)
            brightness = random.uniform(0.3, 0.8)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(cr, cg, cb))

    else:
        for _ in range(60):
            x = random.randint(0, W)
            y = random.randint(0, H)
            sz = random.uniform(0.5, 2)
            brightness = random.uniform(0.2, 0.5)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(cr, cg, cb))

    # 비네팅
    vignette = Image.new("RGB", (W, H), (0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for i in range(40):
        ratio = i / 40
        alpha = int(255 * (1 - ratio) * 0.4)
        margin = int(min(W, H) * ratio * 0.5)
        vdraw.rectangle(
            [margin, margin, W - margin, H - margin],
            outline=(alpha, alpha, alpha)
        )

    img.save(save_path, quality=95)
    print(f"[정보] 배경 자동 생성: {save_path} (스타일: {style_name})")
    return save_path

def detect_style(filename, metadata=None):
    """파일명과 메타데이터에서 음악 스타일을 감지"""
    search_text = filename.lower()
    if metadata:
        search_text += " " + " ".join(str(v).lower() for v in metadata.values() if v)

    for style_name, info in STYLE_KEYWORDS.items():
        for kw in info["keywords"]:
            if kw in search_text:
                return style_name, info
    return "general", DEFAULT_STYLE

def get_style_folder(base_dir, style_info):
    folder = os.path.join(base_dir, style_info.get("folder", "General"))
    os.makedirs(folder, exist_ok=True)
    return folder

def read_mp3_metadata(mp3_path):
    metadata = {"title": "", "artist": "", "genre": ""}
    basename = os.path.splitext(os.path.basename(mp3_path))[0]

    if " - " in basename:
        parts = basename.split(" - ", 1)
        metadata["artist"] = parts[0].strip()
        metadata["title"] = parts[1].strip()
    else:
        metadata["title"] = basename.strip()

    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3
        audio = MP3(mp3_path, ID3=ID3)
        if audio.tags:
            metadata["title"] = str(audio.tags.get("TIT2", metadata["title"]))
            metadata["artist"] = str(audio.tags.get("TPE1", metadata["artist"]))
            metadata["genre"] = str(audio.tags.get("TCON", ""))
    except:
        pass

    return metadata

# ============================================================
# 2) 자동 제목/설명 생성
# ============================================================

TITLE_TEMPLATES = {
    "lofi": [
        "{title} | Lo-Fi Hip Hop Mix | {hours}H Study & Relax",
        "Lo-Fi Chill Beats | {title} | {hours} Hours Playlist",
    ],
    "sleep": [
        "{title} | {hours}H Deep Sleep Music | Relaxing Ambient",
        "Sleep Music | {title} | {hours} Hours for Deep Rest",
    ],
    "jazz": [
        "{title} | Smooth Jazz Cafe Music | {hours}H Playlist",
        "Jazz & Bossa Nova | {title} | {hours} Hours Cafe BGM",
    ],
    "classical": [
        "{title} | Classical Piano | {hours}H Relaxing Playlist",
        "Classical Music | {title} | {hours} Hours Study & Focus",
    ],
    "electronic": [
        "{title} | Electronic Mix | {hours}H Synthwave Playlist",
        "Synthwave & Electronic | {title} | {hours} Hours Mix",
    ],
    "general": [
        "{title} | {hours}H Music Playlist | Relaxing BGM",
        "Music Playlist | {title} | {hours} Hours Non-Stop",
    ],
}

DESCRIPTION_TEMPLATE = """🎵 {title} | {hours} Hours Non-Stop Playlist

Enjoy {hours} hours of continuous {style_name} music.
Perfect for studying, working, sleeping, or just relaxing.

⏰ Duration: {hours} Hours
🎧 Genre: {style_name}
{artist_line}

━━━━━━━━━━━━━━━━━━━━━━━

🔔 Subscribe for more playlists!
👍 Like & Share if you enjoy this music.

━━━━━━━━━━━━━━━━━━━━━━━

{tags_text}

#playlist #{style_tag} #music #relaxing #{hours}hours #studymusic #backgroundmusic
"""

def generate_title(style_name, metadata, hours):
    templates = TITLE_TEMPLATES.get(style_name, TITLE_TEMPLATES["general"])
    template = random.choice(templates)

    title = metadata.get("title", "Relaxing Music")
    if not title or title.strip() == "":
        title = "Relaxing Music"

    if len(title) > 40:
        title = title[:40].rsplit(" ", 1)[0]

    return template.format(title=title, hours=int(hours))

def generate_description(style_name, style_info, metadata, hours):
    title = metadata.get("title", "Relaxing Music")
    artist = metadata.get("artist", "")
    artist_line = f"🎤 Artist: {artist}" if artist else ""

    tags = style_info.get("tags", [])
    tags_text = " ".join(f"#{t.replace(' ', '')}" for t in tags)
    style_tag = style_name.replace(" ", "")

    desc = DESCRIPTION_TEMPLATE.format(
        title=title,
        hours=int(hours),
        style_name=style_name.replace("_", " ").title(),
        artist_line=artist_line,
        tags_text=tags_text,
        style_tag=style_tag,
    )
    return desc.strip()

# ============================================================
# 3) YouTube 업로드
# ============================================================

CLIENT_SECRET_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "client_secret.json")
TOKEN_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "youtube_token.json")

def _find_client_secret():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.exists(CLIENT_SECRET_PATH):
        return CLIENT_SECRET_PATH
    import glob
    patterns = [
        os.path.join(desktop, "client_secret*.json"),
        os.path.join(desktop, "client_secret*.json.json"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            found = matches[0]
            if found != CLIENT_SECRET_PATH:
                import shutil
                shutil.copy2(found, CLIENT_SECRET_PATH)
                print(f"[정보] client_secret 파일 발견: {found} -> {CLIENT_SECRET_PATH}")
            return CLIENT_SECRET_PATH
    return None

def get_youtube_service():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        return None, "필요한 라이브러리 설치 필요!\npip install google-auth google-auth-oauthlib google-api-python-client"

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube.force-ssl"]
    creds = None

    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except:
            pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None

        if not creds:
            secret_path = _find_client_secret()
            if not secret_path:
                return None, f"client_secret.json 파일을 찾을 수 없습니다!\n경로: {CLIENT_SECRET_PATH}"

            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    try:
        service = build("youtube", "v3", credentials=creds)
        return service, "YouTube 연결 성공!"
    except Exception as e:
        return None, f"YouTube 서비스 생성 실패: {e}"

def find_playlist_id(service, playlist_name):
    try:
        request = service.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        )
        response = request.execute()

        for item in response.get("items", []):
            if item["snippet"]["title"] == playlist_name:
                return item["id"]
    except Exception as e:
        print(f"[경고] 재생목록 검색 실패: {e}")
    return None

def add_to_playlist(service, playlist_id, video_id):
    try:
        service.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id,
                    }
                }
            }
        ).execute()
        return True, "재생목록 추가 성공!"
    except Exception as e:
        return False, f"재생목록 추가 실패: {e}"


def _upload_thumbnail(service, video_id: str, thumbnail_path: str) -> tuple[bool, str]:
    """업로드된 영상에 썸네일 첨부."""
    if not thumbnail_path or not os.path.exists(thumbnail_path):
        return False, "썸네일 파일 없음"
    try:
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(thumbnail_path, mimetype="image/png")
        service.thumbnails().set(videoId=video_id, media_body=media).execute()
        return True, "썸네일 첨부 성공"
    except Exception as e:
        return False, f"썸네일 첨부 실패: {type(e).__name__}: {str(e)[:200]}"


def upload_to_youtube(video_path, title, description, tags, category="10",
                      privacy="public", playlist_name="",
                      thumbnail_path=None, style_name=None,
                      pinned_comment_text=None):
    """MP4 업로드 + 다중 플리 추가 + 썸네일 + 고정 댓글.

    [PATCHED] 추가 매개변수:
        thumbnail_path: 1280x720 PNG 경로 (선택). thumbnail_maker.make_thumbnail 결과.
        style_name: youtube_uploader.detect_style 의 style_name. 다중 플리·고정댓에 사용.
        pinned_comment_text: 직접 작성한 고정 댓글. 미지정 시 템플릿으로 자동 생성.
    """
    try:
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
    except ImportError:
        return False, "라이브러리 설치 필요: pip install google-api-python-client"

    try:
        import httplib2
    except ImportError:
        httplib2 = None

    try:
        socket.setdefaulttimeout(600)
    except Exception:
        pass

    service, msg = get_youtube_service()
    if not service:
        return False, msg

    # ================ [PATCH] AI 라벨 + human-input 푸터 ================
    if _ENHANCEMENTS_OK:
        # style_name 미지정 시 tags 첫 항목에서 추론
        sn = (style_name or (tags[0] if tags else "general") or "general")
        sn = sn.lower().replace("-", "").replace(" ", "")
        # 알려진 스타일이 아니면 general 로 매핑
        if sn not in STYLE_KEYWORDS and sn != "general":
            sn = "general"
        description = append_human_input_footer(description, sn)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": category,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    if _ENHANCEMENTS_OK:
        body = inject_ai_label(body)
    # ================ [PATCH 끝] ================

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1 * 1024 * 1024,
    )

    retriable_exc = [
        IOError, OSError,
        ssl.SSLError, ssl.SSLEOFError,
        socket.error, socket.timeout,
        http.client.NotConnected,
        http.client.IncompleteRead,
        http.client.ImproperConnectionState,
        http.client.CannotSendRequest,
        http.client.CannotSendHeader,
        http.client.ResponseNotReady,
        http.client.BadStatusLine,
        ConnectionError,
        ConnectionResetError,
        ConnectionAbortedError,
    ]
    if httplib2 is not None:
        retriable_exc.append(httplib2.HttpLib2Error)
    RETRIABLE_EXCEPTIONS = tuple(retriable_exc)
    RETRIABLE_STATUS_CODES = {500, 502, 503, 504}
    MAX_RETRIES = 20
    MAX_HARD_FAILURES = 4

    def _force_close_http_connections(svc):
        try:
            http_obj = getattr(svc, "_http", None)
            if http_obj is None:
                return
            connections = getattr(http_obj, "connections", None)
            if connections:
                for conn in list(connections.values()):
                    try:
                        conn.close()
                    except Exception:
                        pass
                try:
                    connections.clear()
                except Exception:
                    pass
        except Exception:
            pass

    try:
        request = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        retry = 0
        hard_failures = 0
        last_progress = 0
        while response is None:
            error = None
            try:
                status, response = request.next_chunk()
                if status is not None:
                    cur = getattr(status, "resumable_progress", 0) or 0
                    if cur > last_progress:
                        last_progress = cur
                        hard_failures = 0
                        pct = (cur / status.total_size * 100) if status.total_size else 0
                        print(f"[업로드 진행] {cur/1024/1024:.1f}MB / {status.total_size/1024/1024:.1f}MB ({pct:.1f}%)")
                if response is not None and "id" not in response:
                    return False, f"업로드 실패: 응답에 ID 없음: {response}"
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f"재시도 가능한 HTTP {e.resp.status}: {e}"
                else:
                    return False, f"업로드 실패: {e}"
            except RETRIABLE_EXCEPTIONS as e:
                error = f"재시도 가능한 네트워크 오류: {type(e).__name__}: {e}"

            if error is not None:
                retry += 1
                hard_failures += 1
                if retry > MAX_RETRIES:
                    return False, f"업로드 실패 (최대 재시도 {MAX_RETRIES}회 초과): {error}"

                if hard_failures >= MAX_HARD_FAILURES:
                    print(f"[연결 재생성] {hard_failures}회 연속 진척 없음 → SSL 연결 강제 종료")
                    _force_close_http_connections(service)
                    hard_failures = 0

                sleep_seconds = min(2 ** retry, 120) + random.random()
                print(f"[업로드 재시도] {error} → {sleep_seconds:.1f}초 후 이어올리기 ({retry}/{MAX_RETRIES})")
                time.sleep(sleep_seconds)

        video_id = response.get("id", "")
        video_url = f"https://youtube.com/watch?v={video_id}"
        result_msg = f"업로드 성공!\nURL: {video_url}"

        # ================ [PATCH] 썸네일 첨부 ================
        if thumbnail_path:
            thumb_ok, thumb_msg = _upload_thumbnail(service, video_id, thumbnail_path)
            result_msg += f"\n  {'✓' if thumb_ok else '✗'} 썸네일: {thumb_msg}"

        # ================ [PATCH] 다중 플레이리스트 추가 ================
        if _ENHANCEMENTS_OK and (style_name or playlist_name):
            sn = (style_name or "general").lower()
            if sn not in STYLE_KEYWORDS and sn != "general":
                sn = "general"
            all_pls = get_all_playlists_for(sn, playlist_name)
            for pl_name in all_pls:
                pl_id = find_playlist_id(service, pl_name)
                if pl_id:
                    pl_ok, _ = add_to_playlist(service, pl_id, video_id)
                    if pl_ok:
                        result_msg += f"\n  ✓ 플리: {pl_name}"
                    else:
                        result_msg += f"\n  ✗ 플리 실패: {pl_name}"
                else:
                    result_msg += f"\n  ⚠ 플리 없음: {pl_name}"
        elif playlist_name:
            # enhancements 없을 때 기존 동작
            playlist_id = find_playlist_id(service, playlist_name)
            if playlist_id:
                add_to_playlist(service, playlist_id, video_id)
                result_msg += f"\n재생목록 '{playlist_name}'에 추가 완료!"

        # ================ [PATCH] 고정 댓글 ================
        if _ENHANCEMENTS_OK:
            try:
                if pinned_comment_text is None:
                    sn = (style_name or "general").lower()
                    if sn not in STYLE_KEYWORDS and sn != "general":
                        sn = "general"
                    primary_pl_id = find_playlist_id(service, playlist_name) if playlist_name else None
                    pl_url = (
                        f"https://youtube.com/playlist?list={primary_pl_id}"
                        if primary_pl_id else ""
                    )
                    pinned_comment_text = build_pinned_comment_text(
                        style_name=sn,
                        video_title=title,
                        playlist_url=pl_url,
                    )
                cmt_ok, cmt_msg = post_pinned_comment(service, video_id, pinned_comment_text)
                result_msg += f"\n  {'✓' if cmt_ok else '✗'} 댓글: {cmt_msg}"
            except Exception as e:
                result_msg += f"\n  ⚠ 댓글 실패: {type(e).__name__}: {str(e)[:120]}"

        return True, result_msg

    except Exception as e:
        return False, f"업로드 실패: {e}"
