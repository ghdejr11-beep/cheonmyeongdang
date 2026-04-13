"""YouTube 자동 업로드 + 제목/설명 자동 생성 + 스타일별 폴더 분류 + 배경 자동 생성"""
import os, json, re, random, math

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
        "bg_colors": [(25, 20, 40), (45, 30, 60)],     # 보라-남색 야경
        "accent": (200, 160, 255),                       # 연보라
        "text_color": "#c8a0ff",
    },
    "sleep": {
        "keywords": ["sleep", "ambient", "drone", "healing", "asmr", "deep sleep"],
        "folder": "Sleep_Ambient",
        "tags": ["sleep music", "ambient", "relaxing", "deep sleep", "calm"],
        "category": "10",
        "playlist": "🌙 Sleep Music",
        "bg_colors": [(5, 5, 25), (10, 15, 40)],        # 깊은 남색 밤하늘
        "accent": (100, 140, 220),                        # 은은한 파랑
        "text_color": "#80b0ff",
    },
    "rain": {
        "keywords": ["rain", "nature", "thunder", "ocean", "wave", "forest", "wind"],
        "folder": "Rain_Nature",
        "tags": ["rain sounds", "nature music", "sleep sounds", "relaxing rain"],
        "category": "10",
        "playlist": "🌧️ Rain Sounds",
        "bg_colors": [(15, 20, 25), (25, 35, 45)],      # 어두운 청회색
        "accent": (120, 170, 190),                        # 비 오는 느낌
        "text_color": "#90c0d0",
    },
    "meditation": {
        "keywords": ["meditation", "yoga", "mindful", "calm", "zen", "relax", "peaceful"],
        "folder": "Meditation",
        "tags": ["meditation music", "yoga music", "mindfulness", "relaxing"],
        "category": "10",
        "playlist": "🧘 Meditation",
        "bg_colors": [(10, 20, 15), (20, 40, 30)],      # 깊은 숲 초록
        "accent": (100, 190, 140),                        # 연초록
        "text_color": "#70c090",
    },
    "jazz": {
        "keywords": ["jazz", "bossa", "swing", "cafe", "saxophone", "smooth jazz", "coffee"],
        "folder": "Jazz_Cafe",
        "tags": ["jazz", "cafe music", "smooth jazz", "bossa nova", "relaxing jazz"],
        "category": "10",
        "playlist": "☕ Cafe BGM",
        "bg_colors": [(30, 18, 10), (50, 30, 15)],      # 따뜻한 갈색 카페
        "accent": (210, 170, 100),                        # 골드
        "text_color": "#d4aa64",
    },
    "study": {
        "keywords": ["study", "focus", "concentrate", "productive", "work"],
        "folder": "Study",
        "tags": ["study music", "focus music", "concentration", "productivity"],
        "category": "10",
        "playlist": "📚 Study Music",
        "bg_colors": [(15, 15, 30), (25, 25, 50)],      # 차분한 남색
        "accent": (150, 180, 255),                        # 연파랑
        "text_color": "#a0b8ff",
    },
    "classical": {
        "keywords": ["classical", "piano", "orchestra", "symphony", "sonata", "chopin", "beethoven", "mozart"],
        "folder": "Classical",
        "tags": ["classical music", "piano", "classical piano", "orchestra", "relaxing classical"],
        "category": "10",
        "playlist": "📚 Study Music",
        "bg_colors": [(10, 10, 15), (20, 18, 25)],      # 고급스러운 검정
        "accent": (220, 200, 160),                        # 크림 골드
        "text_color": "#e0d0a0",
    },
    "electronic": {
        "keywords": ["edm", "electronic", "synth", "synthwave", "retrowave", "techno", "house", "trance"],
        "folder": "Electronic",
        "tags": ["electronic music", "synthwave", "EDM", "electronic", "synth"],
        "category": "10",
        "playlist": "📚 Study Music",
        "bg_colors": [(10, 5, 20), (30, 10, 50)],       # 네온 보라
        "accent": (255, 50, 200),                         # 핑크 네온
        "text_color": "#ff40c8",
    },
    "pop": {
        "keywords": ["pop", "kpop", "k-pop", "ballad"],
        "folder": "Pop",
        "tags": ["pop music", "pop", "ballad", "music playlist"],
        "category": "10",
        "playlist": "🌙 Sleep Music",
        "bg_colors": [(20, 10, 25), (40, 15, 45)],      # 핑크-보라
        "accent": (255, 120, 180),                        # 핑크
        "text_color": "#ff80b8",
    },
}

DEFAULT_STYLE = {
    "folder": "General",
    "tags": ["playlist", "music", "relaxing", "background music"],
    "category": "10",
    "playlist": "🌙 Sleep Music",
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
    # 매번 다른 패턴 생성 (시드 고정하지 않음)

    if style_name in ("sleep", "lofi", "study", "classical"):
        # 별/빛 점 효과
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
        # 빗줄기 효과
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
        # 원형 만다라 패턴
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
        # 따뜻한 보케 원 (카페 조명 느낌)
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
        # 네온 라인 그리드
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
        # 큰 보케 원 + 작은 반짝이
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
        # 기본: 은은한 별
        for _ in range(60):
            x = random.randint(0, W)
            y = random.randint(0, H)
            sz = random.uniform(0.5, 2)
            brightness = random.uniform(0.2, 0.5)
            cr = int(accent[0] * brightness)
            cg = int(accent[1] * brightness)
            cb = int(accent[2] * brightness)
            draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(cr, cg, cb))

    # 중앙부 비네팅 (가장자리 어둡게)
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
    """스타일에 맞는 출력 폴더 경로 반환 (없으면 생성)"""
    folder = os.path.join(base_dir, style_info.get("folder", "General"))
    os.makedirs(folder, exist_ok=True)
    return folder

def read_mp3_metadata(mp3_path):
    """MP3 메타데이터 읽기 (mutagen 없이 ID3v1/파일명 기반)"""
    metadata = {"title": "", "artist": "", "genre": ""}
    basename = os.path.splitext(os.path.basename(mp3_path))[0]

    # 파일명에서 아티스트 - 제목 추출 시도
    if " - " in basename:
        parts = basename.split(" - ", 1)
        metadata["artist"] = parts[0].strip()
        metadata["title"] = parts[1].strip()
    else:
        metadata["title"] = basename.strip()

    # mutagen이 있으면 더 정확한 메타데이터 사용
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
    """스타일에 맞는 영어 제목 자동 생성"""
    import random
    templates = TITLE_TEMPLATES.get(style_name, TITLE_TEMPLATES["general"])
    template = random.choice(templates)

    title = metadata.get("title", "Relaxing Music")
    if not title or title.strip() == "":
        title = "Relaxing Music"

    # 제목이 너무 길면 자르기
    if len(title) > 40:
        title = title[:40].rsplit(" ", 1)[0]

    return template.format(title=title, hours=int(hours))

def generate_description(style_name, style_info, metadata, hours):
    """스타일에 맞는 영어 설명 자동 생성"""
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
    """client_secret.json 파일을 자동으로 찾기 (이름이 약간 달라도 찾음)"""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    # 정확한 이름 먼저
    if os.path.exists(CLIENT_SECRET_PATH):
        return CLIENT_SECRET_PATH
    # 비슷한 이름 검색 (client_secret.json.json 등)
    import glob
    patterns = [
        os.path.join(desktop, "client_secret*.json"),
        os.path.join(desktop, "client_secret*.json.json"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            found = matches[0]
            # 올바른 이름으로 복사
            if found != CLIENT_SECRET_PATH:
                import shutil
                shutil.copy2(found, CLIENT_SECRET_PATH)
                print(f"[정보] client_secret 파일 발견: {found} -> {CLIENT_SECRET_PATH}")
            return CLIENT_SECRET_PATH
    return None

def get_youtube_service():
    """YouTube API 서비스 객체 생성 (처음 한 번만 브라우저 인증 필요)"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        return None, "필요한 라이브러리 설치 필요!\n아래 명령어를 실행하세요:\npip install google-auth google-auth-oauthlib google-api-python-client"

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube"]
    creds = None

    # 저장된 토큰이 있으면 재사용
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except:
            pass

    # 토큰이 없거나 만료됨
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

        # 토큰 저장 (다음에 다시 로그인 안 해도 됨)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    try:
        service = build("youtube", "v3", credentials=creds)
        return service, "YouTube 연결 성공!"
    except Exception as e:
        return None, f"YouTube 서비스 생성 실패: {e}"

def find_playlist_id(service, playlist_name):
    """유튜브 재생목록 이름으로 ID 검색"""
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
    """업로드된 동영상을 재생목록에 추가"""
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

def upload_to_youtube(video_path, title, description, tags, category="10", privacy="public", playlist_name=""):
    """MP4 파일을 YouTube에 업로드 후 재생목록에 자동 추가"""
    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        return False, "라이브러리 설치 필요: pip install google-api-python-client"

    service, msg = get_youtube_service()
    if not service:
        return False, msg

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

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,
    )

    try:
        request = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()

        video_id = response.get("id", "")
        video_url = f"https://youtube.com/watch?v={video_id}"
        result_msg = f"업로드 성공!\nURL: {video_url}"

        # 재생목록에 자동 추가
        if playlist_name:
            playlist_id = find_playlist_id(service, playlist_name)
            if playlist_id:
                pl_ok, pl_msg = add_to_playlist(service, playlist_id, video_id)
                result_msg += f"\n재생목록 '{playlist_name}'에 추가 완료!"
            else:
                result_msg += f"\n[경고] 재생목록 '{playlist_name}'을 찾을 수 없습니다"

        return True, result_msg

    except Exception as e:
        return False, f"업로드 실패: {e}"
