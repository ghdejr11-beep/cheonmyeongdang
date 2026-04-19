"""music_pipeline.enhancements — 2026 YouTube 최적화 애드온 모듈 패키지.

각 모듈은 독립 실행 가능 (자체 테스트 내장).
상위 파이프라인(auto_watcher.py, lyrics_watcher.py, youtube_uploader.py)에
import 해서 쓴다.
"""

from . import (
    ai_label,
    ass_subtitles,
    chapter_generator,
    pinned_comment,
    purpose_playlists,
    shorts_extractor,
    thumbnail_maker,
)

__all__ = [
    "ai_label",
    "ass_subtitles",
    "chapter_generator",
    "pinned_comment",
    "purpose_playlists",
    "shorts_extractor",
    "thumbnail_maker",
]
