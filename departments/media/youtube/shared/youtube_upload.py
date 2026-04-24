#!/usr/bin/env python3
"""
YouTube Data API v3 업로더 (OAuth + 자동 refresh, 채널별 토큰 분리).

각 채널 1회 인증:
    python youtube_upload.py --channel deokgune   # 덕구네 노래모음 (Sleep)
    python youtube_upload.py --channel wealth     # Wealth Blueprint (AI 부업)
    python youtube_upload.py --channel kunstudio  # KunStudio (AI 튜토)

이후 import 후:
    from youtube_upload import upload_video
    upload_video("video.mp4", channel="deokgune", title="...", ...)
"""
import os, pickle, sys, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
CLIENT_SECRET = HERE / "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]

CHANNEL_MAP = {
    "deokgune":   "token_deokgune.pickle",    # 덕구네 노래모음 (Sleep)
    "wealth":     "token_wealth.pickle",      # Wealth Blueprint
    "kunstudio":  "token_kunstudio.pickle",   # KunStudio
}


def get_credentials(channel):
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    if channel not in CHANNEL_MAP:
        raise ValueError(f"알 수 없는 channel: {channel}. 가능: {list(CHANNEL_MAP)}")

    token_file = HERE / CHANNEL_MAP[channel]
    creds = None
    if token_file.exists():
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                raise FileNotFoundError(f"{CLIENT_SECRET} 없음")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            print(f"\n🔐 {channel} 채널 인증 — 브라우저에서 해당 채널 선택해줘")
            creds = flow.run_local_server(port=0)

        with open(token_file, "wb") as f:
            pickle.dump(creds, f)

    return creds


def get_channel_info(channel):
    """현재 토큰의 채널 이름·ID 확인용."""
    from googleapiclient.discovery import build
    creds = get_credentials(channel)
    yt = build("youtube", "v3", credentials=creds)
    r = yt.channels().list(part="snippet,statistics", mine=True).execute()
    if r.get("items"):
        it = r["items"][0]
        return {
            "id": it["id"],
            "title": it["snippet"]["title"],
            "subscribers": it["statistics"].get("subscriberCount", "0"),
            "videos": it["statistics"].get("videoCount", "0"),
        }
    return None


def upload_video(video_path, channel, title, description="", tags=None, privacy="private", category_id="22"):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = get_credentials(channel)
    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": title[:100], "description": description[:5000],
            "tags": tags or [], "categoryId": category_id,
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/*")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"📤 [{channel}] 업로드 시작: {Path(video_path).name}")
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"  진행 {int(status.progress()*100)}%")
    vid = response.get("id")
    print(f"✅ https://youtu.be/{vid}")
    return vid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True, choices=list(CHANNEL_MAP))
    args = ap.parse_args()
    info = get_channel_info(args.channel)
    if info:
        print(f"✅ 인증 완료: {info['title']} (id={info['id']}, 구독 {info['subscribers']}, 영상 {info['videos']})")
    else:
        print("⚠️ 채널 정보 못 가져옴 — 토큰은 저장됨")
