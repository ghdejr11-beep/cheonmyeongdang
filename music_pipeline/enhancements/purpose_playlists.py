"""용도(Use-case) 플레이리스트 매핑.

기존 STYLE_KEYWORDS 는 **장르별** 9종 (Lo-Fi, Sleep, Jazz...).
2026년 검색 트래픽의 절반은 "공부할 때", "운전할 때", "카페 분위기" 같은
**용도 키워드**. 같은 영상을 장르 플리 + 용도 플리 **양쪽에 추가**하면
검색 노출이 2배.

사용:
    from music_pipeline.enhancements.purpose_playlists import (
        PURPOSE_PLAYLISTS, get_purpose_playlists_for,
    )

    extra_playlists = get_purpose_playlists_for("lofi")
    # → ["📚 공부할 때 듣는 음악", "💻 작업할 때 듣는 음악"]

youtube_uploader.py 의 upload_to_youtube() 안에서 `playlist_name`
하나만 넣는 대신, 이 모듈로 여러 플리에 동시 추가하도록 확장한다.
"""

from __future__ import annotations


# 용도 플레이리스트 이름 (YouTube 에서 미리 만들어둬야 함)
PURPOSE_PLAYLISTS = {
    "study": "📚 공부할 때 듣는 음악",
    "work": "💻 작업할 때 듣는 음악",
    "sleep": "🌙 잠 올 때 듣는 음악",
    "driving": "🚗 운전할 때 듣는 음악",
    "cafe": "☕ 카페 분위기 만드는 음악",
    "walk": "🚶 산책할 때 듣는 음악",
    "rain_day": "🌧️ 비 오는 날 듣는 음악",
    "dawn": "🌅 새벽에 듣는 음악",
    "night": "🌃 밤에 듣는 음악",
    "healing": "💚 지친 하루 힐링",
    "workout": "💪 운동할 때 듣는 음악",
    "breakup": "💔 이별 후 듣는 음악",
}

# 장르 → 어울리는 용도 플리 매핑 (최대 3개 권장: 스팸 방지)
STYLE_TO_PURPOSES = {
    "lofi": ["study", "work", "dawn"],
    "sleep": ["sleep", "healing", "night"],
    "rain": ["rain_day", "sleep", "healing"],
    "meditation": ["healing", "dawn", "night"],
    "jazz": ["cafe", "work", "night"],
    "study": ["study", "work"],
    "classical": ["study", "work", "dawn"],
    "electronic": ["workout", "driving", "night"],
    "pop": ["breakup", "healing", "night"],
    "kpop": ["walk", "driving", "workout"],
    "general": ["healing"],
}


def get_purpose_playlists_for(style_name: str) -> list[str]:
    """장르명 → 용도 플리 이름 리스트."""
    keys = STYLE_TO_PURPOSES.get(style_name) or STYLE_TO_PURPOSES["general"]
    return [PURPOSE_PLAYLISTS[k] for k in keys if k in PURPOSE_PLAYLISTS]


def get_all_playlists_for(style_name: str, primary_playlist: str) -> list[str]:
    """primary 플리 + 용도 플리들을 합친 전체 리스트 (중복 제거)."""
    all_pls = [primary_playlist] if primary_playlist else []
    all_pls.extend(get_purpose_playlists_for(style_name))
    # 중복 제거, 순서 유지
    seen: set[str] = set()
    out: list[str] = []
    for pl in all_pls:
        if pl and pl not in seen:
            seen.add(pl)
            out.append(pl)
    return out


def add_to_multiple_playlists(
    youtube_service,
    video_id: str,
    playlist_names: list[str],
    find_playlist_id,
    add_to_playlist,
) -> dict:
    """여러 플레이리스트에 한 영상을 동시 추가.

    Args:
        youtube_service: googleapiclient.discovery.build(...)
        video_id: 업로드된 영상 ID
        playlist_names: 추가할 플레이리스트 이름들
        find_playlist_id: youtube_uploader.find_playlist_id 함수
        add_to_playlist: youtube_uploader.add_to_playlist 함수

    Returns:
        {"success": [...], "failed": [...]}
    """
    result = {"success": [], "failed": []}
    for pl_name in playlist_names:
        try:
            pl_id = find_playlist_id(youtube_service, pl_name)
            if not pl_id:
                result["failed"].append((pl_name, "플리 없음"))
                continue
            ok, msg = add_to_playlist(youtube_service, pl_id, video_id)
            if ok:
                result["success"].append(pl_name)
            else:
                result["failed"].append((pl_name, msg))
        except Exception as e:
            result["failed"].append((pl_name, str(e)[:120]))
    return result


if __name__ == "__main__":
    # 테스트
    p = get_purpose_playlists_for("lofi")
    assert "📚 공부할 때 듣는 음악" in p
    assert "💻 작업할 때 듣는 음악" in p
    print(f"✓ lofi 용도 플리: {p}")

    p = get_purpose_playlists_for("pop")
    assert "💔 이별 후 듣는 음악" in p
    print(f"✓ pop 용도 플리: {p}")

    p = get_purpose_playlists_for("unknown_style")
    assert "💚 지친 하루 힐링" in p
    print(f"✓ unknown 폴백: {p}")

    # 중복 제거
    all_p = get_all_playlists_for("lofi", "📚 공부할 때 듣는 음악")
    assert all_p.count("📚 공부할 때 듣는 음악") == 1
    print(f"✓ 중복 제거됨: {all_p}")

    print("\n✓ purpose_playlists.py 자체 테스트 통과")
    print("\n[중요] YouTube 에서 위 플레이리스트 이름들을 **똑같이** 먼저 만들어두세요:")
    for key, name in PURPOSE_PLAYLISTS.items():
        print(f"  - {name}")
