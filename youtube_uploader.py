"""YouTube 자동 업로드 + 제목/설명 자동 생성 + 스타일별 폴더 분류"""
import os, json, re

# ============================================================
# 1) 스타일 감지 및 폴더 분류
# ============================================================

STYLE_KEYWORDS = {
    "lofi": {
        "keywords": ["lofi", "lo-fi", "lo fi", "chillhop", "study beat", "homework"],
        "folder": "LoFi",
        "tags": ["lofi", "lo-fi hip hop", "study music", "chill beats", "relaxing"],
        "category": "10",  # YouTube Music category
    },
    "sleep": {
        "keywords": ["sleep", "ambient", "drone", "meditation", "calm", "relax", "healing", "asmr", "rain", "nature"],
        "folder": "Sleep_Ambient",
        "tags": ["sleep music", "ambient", "relaxing", "meditation", "deep sleep", "calm"],
        "category": "10",
    },
    "jazz": {
        "keywords": ["jazz", "bossa", "swing", "cafe", "saxophone", "smooth jazz"],
        "folder": "Jazz_Cafe",
        "tags": ["jazz", "cafe music", "smooth jazz", "bossa nova", "relaxing jazz"],
        "category": "10",
    },
    "classical": {
        "keywords": ["classical", "piano", "orchestra", "symphony", "sonata", "chopin", "beethoven", "mozart"],
        "folder": "Classical",
        "tags": ["classical music", "piano", "classical piano", "orchestra", "relaxing classical"],
        "category": "10",
    },
    "electronic": {
        "keywords": ["edm", "electronic", "synth", "synthwave", "retrowave", "techno", "house", "trance"],
        "folder": "Electronic",
        "tags": ["electronic music", "synthwave", "EDM", "electronic", "synth"],
        "category": "10",
    },
    "pop": {
        "keywords": ["pop", "kpop", "k-pop", "ballad"],
        "folder": "Pop",
        "tags": ["pop music", "pop", "ballad", "music playlist"],
        "category": "10",
    },
}

DEFAULT_STYLE = {
    "folder": "General",
    "tags": ["playlist", "music", "relaxing", "background music"],
    "category": "10",
}

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

def get_youtube_service():
    """YouTube API 서비스 객체 생성 (처음 한 번만 브라우저 인증 필요)"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        return None, "필요한 라이브러리 설치 필요!\n아래 명령어를 실행하세요:\npip install google-auth google-auth-oauthlib google-api-python-client"

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
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
            if not os.path.exists(CLIENT_SECRET_PATH):
                return None, f"client_secret.json 파일을 찾을 수 없습니다!\n경로: {CLIENT_SECRET_PATH}"

            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # 토큰 저장 (다음에 다시 로그인 안 해도 됨)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    try:
        service = build("youtube", "v3", credentials=creds)
        return service, "YouTube 연결 성공!"
    except Exception as e:
        return None, f"YouTube 서비스 생성 실패: {e}"

def upload_to_youtube(video_path, title, description, tags, category="10", privacy="public"):
    """MP4 파일을 YouTube에 업로드"""
    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        return False, "라이브러리 설치 필요: pip install google-api-python-client"

    service, msg = get_youtube_service()
    if not service:
        return False, msg

    body = {
        "snippet": {
            "title": title[:100],  # YouTube 제목 최대 100자
            "description": description[:5000],
            "tags": tags[:30],  # 최대 30개 태그
            "categoryId": category,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy,  # public, unlisted, private
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB 청크
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
        return True, f"업로드 성공!\nURL: {video_url}"

    except Exception as e:
        return False, f"업로드 실패: {e}"
