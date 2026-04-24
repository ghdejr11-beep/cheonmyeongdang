#!/usr/bin/env python3
"""
쿤스튜디오 미디어부 — YouTube 채널 전수 분석
- OAuth 1회 인증 후 토큰 저장
- 내 채널 + 브랜드 채널 목록
- 영상별 조회수·좋아요·댓글
- 가장 성과 좋은 영상 / 약한 영상 자동 식별
"""
import os, sys, json, pathlib, datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.stdout.reconfigure(encoding='utf-8')

CLIENT_SECRET = os.path.expanduser(
    r'~/Downloads/client_secret_95091510329-6vdp64c4ddm04gbea1pcgs1m7s36t2p4.apps.googleusercontent.com.json'
)
TOKEN_PATH = os.path.expanduser(r'~/Desktop/cheonmyeongdang/.secrets_youtube_token.json')

# YouTube Data API 읽기 권한 + 분석 권한 (video retention, audience)
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
]


def get_service(api='youtube', version='v3'):
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception:
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            print("브라우저가 열립니다. YouTube 계정 선택 후 '허용' 클릭해주세요.")
            creds = flow.run_local_server(port=0, prompt='consent')
        pathlib.Path(TOKEN_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
        print(f"토큰 저장됨: {TOKEN_PATH}")

    if api == 'youtube':
        return build('youtube', 'v3', credentials=creds)
    else:
        return build('youtubeAnalytics', 'v2', credentials=creds)


def analyze_channels():
    yt = get_service('youtube')

    # 1. 내가 관리하는 채널 목록 (mine=true = 현재 인증된 채널)
    ch_resp = yt.channels().list(
        part='snippet,statistics,brandingSettings,contentDetails',
        mine=True
    ).execute()

    channels = ch_resp.get('items', [])
    print(f"=== 인증된 채널 {len(channels)}개 ===\n")

    results = []
    for ch in channels:
        info = {
            'channel_id': ch['id'],
            'name': ch['snippet']['title'],
            'description': ch['snippet'].get('description', '')[:200],
            'created': ch['snippet']['publishedAt'][:10],
            'subscriber_count': int(ch['statistics'].get('subscriberCount', 0)),
            'video_count': int(ch['statistics'].get('videoCount', 0)),
            'view_count': int(ch['statistics'].get('viewCount', 0)),
            'uploads_playlist': ch['contentDetails']['relatedPlaylists']['uploads'],
        }

        # 2. 최근 영상 20개
        videos = []
        next_token = None
        for _ in range(2):  # 최대 50 + 50 = 100개까지
            plr = yt.playlistItems().list(
                part='contentDetails,snippet',
                playlistId=info['uploads_playlist'],
                maxResults=50,
                pageToken=next_token,
            ).execute()
            video_ids = [it['contentDetails']['videoId'] for it in plr.get('items', [])]
            if not video_ids:
                break
            # 상세 통계
            vr = yt.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids),
            ).execute()
            for v in vr.get('items', []):
                s = v.get('statistics', {})
                videos.append({
                    'id': v['id'],
                    'title': v['snippet']['title'],
                    'published': v['snippet']['publishedAt'][:10],
                    'duration': v['contentDetails']['duration'],
                    'views': int(s.get('viewCount', 0)),
                    'likes': int(s.get('likeCount', 0)),
                    'comments': int(s.get('commentCount', 0)),
                    'url': f"https://youtu.be/{v['id']}",
                    'thumbnail': v['snippet']['thumbnails'].get('high', {}).get('url', ''),
                })
            next_token = plr.get('nextPageToken')
            if not next_token:
                break

        info['videos_fetched'] = len(videos)
        info['videos'] = videos
        results.append(info)

    return results


def print_report(channels):
    for c in channels:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"[{c['name']}]  (ID: {c['channel_id']})")
        print(f"  생성: {c['created']} | 구독자: {c['subscriber_count']:,}명 | 전체 영상: {c['video_count']}개 | 누적 조회: {c['view_count']:,}")
        if c['description']:
            print(f"  설명: {c['description'][:100]}")

        if not c['videos']:
            print("  (영상 없음)\n")
            continue

        # 상위 5
        top = sorted(c['videos'], key=lambda v: v['views'], reverse=True)[:5]
        bot = sorted(c['videos'], key=lambda v: v['views'])[:3]
        total_views = sum(v['views'] for v in c['videos'])
        avg = total_views // len(c['videos']) if c['videos'] else 0
        recent = sorted(c['videos'], key=lambda v: v['published'], reverse=True)[:3]

        print(f"\n  📊 분석 샘플 {len(c['videos'])}개 영상")
        print(f"     평균 조회수: {avg:,}")
        print(f"\n  🏆 TOP 5 영상")
        for v in top:
            print(f"     {v['views']:>8,}  {v['title'][:60]}")
        print(f"\n  📉 BOTTOM 3 영상 (개선 타깃)")
        for v in bot:
            print(f"     {v['views']:>8,}  {v['title'][:60]}")
        print(f"\n  🗓️  최신 3 영상")
        for v in recent:
            print(f"     {v['published']}  조회 {v['views']:>6,}  {v['title'][:50]}")
        print()


if __name__ == '__main__':
    data = analyze_channels()
    # 결과 저장
    out_path = os.path.expanduser(r'~/Desktop/cheonmyeongdang/departments/media/youtube_analysis.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print_report(data)
    print(f"\n📁 전체 데이터 저장: {out_path}")
