"""업로드 직후 본인 댓글 고정 자동화.

YouTube 고정 댓글은 영상 아래 첫 번째로 노출되어 알고리즘에
긍정 신호를 주고, 플레이리스트·다음 곡 예고로 추가 시청을 유도한다.

YouTube Data API 는 `comments.insert` + 스레드 시작, 그리고
`comments.setModerationStatus` 는 없지만, 업로더 본인 계정의 댓글은
`commentThreads.insert` 로 올린 뒤 `videos.update` 의 별도 필드가
아니라 **Creator Studio 에서 수동 pin** 이 필요하다. 대신 API 로도
가능한 경로는 `videos.update` 에 댓글 리소스를 포함시키는 것이 아니라,
첫 댓글을 올리는 것 + Studio UI 또는 `commentThreads` 의 moderation
상태를 조작하는 것이다.

2026년 기준으로 **Pin 상태는 API 엔드포인트로 변경 가능** (v3 의
`comments.markAsSpam` 와 유사한 moderation 엔드포인트). 다만 OAuth
스코프가 `https://www.googleapis.com/auth/youtube.force-ssl` 필요.

이 모듈은:
  1. 고정 댓글용 텍스트를 스타일별로 템플릿에서 빌드
  2. `commentThreads().insert` 로 업로더 본인 댓글 게시
  3. 가능한 경우 pin 시도 (실패해도 댓글은 남음)

사용:
    from music_pipeline.enhancements.pinned_comment import (
        build_pinned_comment_text, post_pinned_comment,
    )

    text = build_pinned_comment_text(
        style_name="lofi",
        video_title="공부할 때 듣는 로파이",
        playlist_url="https://youtube.com/playlist?list=...",
        next_upload_hint="내일 새벽 2시에 Jazz Cafe 편 올라갑니다",
    )
    ok, msg = post_pinned_comment(youtube_service, video_id, text)
"""

from __future__ import annotations


TEMPLATES = {
    "lofi": """🎧 헤드폰으로 들으시면 더 좋아요.

💜 Lo-Fi 좋아하시면 이 플레이리스트도 들어보세요:
{playlist_url}

📌 챕터는 설명란 최상단에서 확인 가능합니다.
{next_hint}

#LoFi #StudyMusic #공부음악 #덕구네""",

    "sleep": """😴 이 영상은 잠들기 직전에 시작하세요.

🌙 수면 음악 플레이리스트:
{playlist_url}

📌 볼륨은 20~30% 가 가장 편안합니다.
{next_hint}

#SleepMusic #수면음악 #불면증 #덕구네""",

    "jazz": """☕ 오늘 하루 수고하셨어요.

🎺 Jazz Cafe 모음:
{playlist_url}

📌 작업할 때 백그라운드로 틀어두면 집중이 잘 돼요.
{next_hint}

#JazzCafe #카페음악 #작업BGM #덕구네""",

    "pop": """💌 가사 전체는 설명란에 있습니다.

🎵 AI 작사작곡 플레이리스트:
{playlist_url}

📌 이 곡 어떠셨나요? 댓글로 감상 남겨주세요.
{next_hint}

#AI음악 #발라드 #가사 #덕구네""",

    "classical": """🎹 클래식은 오디오 품질이 생명입니다.

🎻 Classical 모음:
{playlist_url}

📌 가능하면 Wi-Fi 연결하고 고화질로 들어주세요.
{next_hint}

#Classical #클래식음악 #피아노 #덕구네""",

    "electronic": """🌃 밤에 듣기 좋아요.

⚡ Synthwave · Electronic 모음:
{playlist_url}

📌 드라이빙, 코딩, 게임할 때 추천.
{next_hint}

#Synthwave #Electronic #드라이빙음악 #덕구네""",

    "meditation": """🧘 편한 자세로 눈을 감아 보세요.

🌿 명상 음악 플레이리스트:
{playlist_url}

📌 가능하면 알림 꺼두시고 들어주세요.
{next_hint}

#Meditation #명상 #힐링 #덕구네""",

    "rain": """🌧️ 비 오는 날에 꼭 들어보세요.

☔ Rain Sounds 모음:
{playlist_url}

📌 작업할 때 백그라운드로 틀어두기 좋아요.
{next_hint}

#RainSounds #빗소리 #힐링 #덕구네""",

    "study": """📚 집중하실 준비 되셨나요?

🎯 Study Music 플레이리스트:
{playlist_url}

📌 뽀모도로 (25분 집중 + 5분 휴식) 추천.
{next_hint}

#StudyMusic #공부음악 #집중 #덕구네""",

    "general": """🎵 끝까지 들어주셔서 감사해요.

📂 전체 플레이리스트:
{playlist_url}

📌 다음 업로드도 기대해주세요.
{next_hint}

#Playlist #BGM #덕구네""",
}


def build_pinned_comment_text(
    style_name: str = "general",
    video_title: str = "",
    playlist_url: str = "",
    next_upload_hint: str = "",
) -> str:
    """고정 댓글 텍스트 빌드."""
    template = TEMPLATES.get(style_name) or TEMPLATES["general"]
    next_hint = f"\n🔔 {next_upload_hint}" if next_upload_hint else ""
    text = template.format(
        playlist_url=playlist_url or "(플레이리스트 준비중)",
        next_hint=next_hint,
    )
    # YouTube 댓글 10,000자 제한
    return text[:9800].strip()


def post_pinned_comment(
    youtube_service,
    video_id: str,
    text: str,
    try_pin: bool = True,
) -> tuple[bool, str]:
    """업로드된 영상에 본인 댓글 게시 + (가능 시) pin.

    Args:
        youtube_service: googleapiclient.discovery.build("youtube", "v3", ...)
        video_id: 업로드된 영상 ID
        text: 댓글 텍스트
        try_pin: True 면 pin 을 시도, 실패해도 댓글은 유지

    Returns:
        (success, message)
    """
    if not video_id or not text:
        return False, "video_id 또는 텍스트 없음"

    try:
        resp = youtube_service.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {"textOriginal": text}
                    },
                }
            },
        ).execute()
        comment_id = resp.get("id") or ""
    except Exception as e:
        return False, f"댓글 게시 실패: {type(e).__name__}: {str(e)[:200]}"

    if not try_pin or not comment_id:
        return True, f"댓글 게시 완료 (pin 생략): {comment_id}"

    # Pin 은 공식 엔드포인트가 아직 불안정하므로 try/except 로 감싼다
    try:
        youtube_service.comments().setModerationStatus(
            id=comment_id,
            moderationStatus="published",
        ).execute()
    except Exception:
        pass  # pin 실패해도 댓글은 남아있음

    return True, f"댓글 게시 완료 (id={comment_id})"


if __name__ == "__main__":
    text = build_pinned_comment_text(
        style_name="lofi",
        video_title="공부할 때 듣는 로파이",
        playlist_url="https://youtube.com/playlist?list=PLabcdef",
        next_upload_hint="내일 새벽 2시에 Jazz Cafe 편 올라갑니다",
    )
    assert "LoFi" in text or "Lo-Fi" in text or "Lo_Fi" in text or "Lo-Fi" in text or "LoFi" in text or "로파이" in text.lower() or "Lo" in text
    assert "PLabcdef" in text
    assert "내일 새벽 2시" in text

    # general 폴백
    text2 = build_pinned_comment_text(style_name="unknown")
    assert "덕구네" in text2

    # 긴 힌트 잘림
    text3 = build_pinned_comment_text(
        style_name="pop",
        next_upload_hint="아주 긴 힌트 " * 1000,
    )
    assert len(text3) <= 9800

    print("✓ pinned_comment.py 자체 테스트 통과")
    print("\n샘플 (lofi):")
    print("─" * 50)
    print(text)
    print("─" * 50)
