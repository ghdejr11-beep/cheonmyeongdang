"""YouTube 챕터 자동 생성기.

YouTube는 설명란 최상단에 `0:00:00` 으로 시작하는 타임스탬프 3개 이상이
있으면 챕터 UI를 자동 활성화한다. 챕터가 있으면 시청 지속률이 체감으로
10~20% 증가.

두 가지 모드:
  - build_loop_chapters(): 8시간 BGM 루프용 — 시간대별 무드 마커로
    균등 분할 (실제 트랙 변화가 없어도 UX 상 유용)
  - build_lyric_chapters(): 3~5분 가사곡용 — 너무 짧으면 생략

auto_watcher.py / lyrics_watcher.py 양쪽에서 사용.

사용:
    from music_pipeline.enhancements.chapter_generator import (
        build_loop_chapters, prepend_chapters,
    )

    chapters = build_loop_chapters(style_name, total_hours=8)
    description = prepend_chapters(description, chapters)
"""

from __future__ import annotations


LOOP_MOOD_PRESETS = {
    "lofi": [
        "Warm Intro",
        "Afternoon Chill",
        "Golden Hour",
        "Night Study",
        "Deep Focus",
        "Late Night Flow",
        "Midnight Calm",
        "Dawn Wind-down",
    ],
    "sleep": [
        "Falling Asleep",
        "Light Dreams",
        "Deep Slumber",
        "REM Cycle",
        "Midnight Stillness",
        "Early Morning Dreams",
        "Gentle Wake-up",
        "Final Rest",
    ],
    "rain": [
        "Light Drizzle",
        "Steady Rain",
        "Distant Thunder",
        "Heavy Downpour",
        "Midnight Storm",
        "Calm After the Storm",
        "Gentle Dawn Rain",
        "Morning Mist",
    ],
    "meditation": [
        "Grounding",
        "Deep Breath",
        "Body Scan",
        "Silent Mind",
        "Inner Peace",
        "Heart Opening",
        "Letting Go",
        "Integration",
    ],
    "jazz": [
        "Morning Espresso",
        "Afternoon Cafe",
        "Evening Jazz Bar",
        "Late Night Lounge",
        "After Hours",
        "Midnight Whiskey",
        "Dawn Reflection",
        "Sunrise Piano",
    ],
    "study": [
        "Warm-up",
        "Focus Block 1",
        "Deep Work",
        "Focus Block 2",
        "Pomodoro Reset",
        "Evening Review",
        "Night Study",
        "Final Push",
    ],
    "classical": [
        "Morning Prelude",
        "Daylight Sonata",
        "Afternoon Concerto",
        "Sunset Nocturne",
        "Evening Symphony",
        "Night Fantasia",
        "Midnight Adagio",
        "Dawn Reverie",
    ],
    "electronic": [
        "Synth Awakening",
        "Neon Drive",
        "Night City",
        "Deep Synthwave",
        "Cyber Dream",
        "Retro Rush",
        "Dawn Protocol",
        "Sunrise Circuit",
    ],
    "pop": [
        "Opening Track",
        "Soft Ballad",
        "Emotional Peak",
        "Reflective Mid",
        "Hopeful Turn",
        "Late Night Feelings",
        "Quiet Finale",
        "Closing Track",
    ],
    "general": [
        "Opening",
        "Flow 1",
        "Flow 2",
        "Flow 3",
        "Mid-session",
        "Deep Flow",
        "Wind-down",
        "Closing",
    ],
}


def _format_timestamp(seconds: int, hour_aware: bool = False) -> str:
    """초 → 타임스탬프. hour_aware=True 면 항상 H:MM:SS.

    YouTube 는 첫 챕터가 `0:00` 또는 `0:00:00` 모두 인식하지만, 영상이
    1시간 이상이면 뒤 챕터들이 H:MM:SS 로 나와야 하므로 첫 챕터도 같은
    포맷으로 맞춰야 일관성 있다.
    """
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if hour_aware or h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def build_loop_chapters(
    style_name: str,
    total_hours: float = 8.0,
    chapter_count: int = 8,
) -> list[tuple[str, str]]:
    """BGM 루프용 챕터 생성.

    Returns:
        [("0:00:00", "Warm Intro"), ("1:00:00", "Afternoon Chill"), ...]
    """
    moods = LOOP_MOOD_PRESETS.get(style_name) or LOOP_MOOD_PRESETS["general"]
    # 시간에 비례해 mood 개수 조정 (최소 3, 최대 len(moods))
    n = max(3, min(chapter_count, len(moods)))
    total_sec = int(total_hours * 3600)
    step = total_sec // n

    chapters: list[tuple[str, str]] = []
    hour_aware = total_hours >= 1.0
    for i in range(n):
        start = i * step if i > 0 else 0
        label = moods[i % len(moods)]
        chapters.append((_format_timestamp(start, hour_aware=hour_aware), label))
    return chapters


def build_lyric_chapters(lyrics_raw: str, audio_duration: float) -> list[tuple[str, str]]:
    """가사곡용 챕터 생성.

    [Verse], [Chorus] 같은 섹션 마커가 있으면 그것 기반으로,
    없으면 길이가 짧으므로 (<4분) 챕터 생략 (빈 리스트).

    챕터 최소 요건: 3개 + 10초 이상 간격. 2분짜리 곡에 억지로 챕터 넣으면
    역효과.
    """
    if audio_duration < 180:  # 3분 미만은 챕터 생략
        return []

    import re
    sections: list[tuple[int, str]] = []
    line_count = 0
    total_lines = len([ln for ln in lyrics_raw.splitlines() if ln.strip()])

    for line in lyrics_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\[([^\]]+)\]\s*$", line)
        if m:
            label = m.group(1).strip()
            # [00:23.45] 같은 타임스탬프는 스킵
            if re.match(r"^\d", label):
                continue
            # 대략적인 시작 시간 = (지금까지 읽은 라인 비율) × 총 길이
            if total_lines > 0:
                approx_sec = int(line_count / total_lines * audio_duration)
            else:
                approx_sec = 0
            sections.append((approx_sec, label))
        else:
            line_count += 1

    if len(sections) < 3:
        return []

    # 첫 챕터는 반드시 0 으로
    first_sec, first_label = sections[0]
    if first_sec > 0:
        sections[0] = (0, first_label)

    # 10초 미만 간격 머지
    merged: list[tuple[int, str]] = []
    for sec, label in sections:
        if merged and sec - merged[-1][0] < 10:
            continue
        merged.append((sec, label))

    if len(merged) < 3:
        return []

    return [(_format_timestamp(s), lbl) for s, lbl in merged]


def prepend_chapters(description: str, chapters: list[tuple[str, str]]) -> str:
    """설명 최상단에 챕터 블록 삽입.

    YouTube 챕터 조건:
      - 첫 줄은 `0:00` 또는 `0:00:00` 로 시작
      - 3개 이상
      - 최소 10초 간격
      - 설명란 내 위치 무관하지만 상단이 시청자에게 잘 보임
    """
    if not chapters or len(chapters) < 3:
        return description

    lines = ["⏱️ Chapters"]
    for ts, label in chapters:
        lines.append(f"{ts} {label}")
    block = "\n".join(lines) + "\n\n"

    if not description:
        return block
    return block + description.lstrip()


if __name__ == "__main__":
    # 자체 테스트
    ch = build_loop_chapters("lofi", total_hours=8.0, chapter_count=8)
    assert len(ch) == 8
    assert ch[0][0] == "0:00:00"
    assert ch[-1][0] == "7:00:00"
    assert "Warm Intro" in ch[0][1]

    ch = build_loop_chapters("jazz", total_hours=8.0)
    assert "Cafe" in ch[1][1] or "Bar" in ch[2][1] or "Jazz" in " ".join(l for _, l in ch)

    # 가사곡 - 섹션 없음 (짧은 곡)
    ch = build_lyric_chapters("가사 한 줄\n두 줄\n세 줄", audio_duration=120)
    assert ch == []  # 3분 미만

    # 가사곡 - 섹션 있음
    lyrics = """[Verse 1]
밤하늘
너의 눈

[Chorus]
사랑해

[Bridge]
잠들지 마

[Verse 2]
계속

[Outro]
끝
"""
    ch = build_lyric_chapters(lyrics, audio_duration=240)
    assert len(ch) >= 3

    # prepend
    desc = "원래 설명"
    out = prepend_chapters(desc, ch)
    assert out.startswith("⏱️ Chapters")
    assert "원래 설명" in out

    print("✓ chapter_generator.py 자체 테스트 통과")
    print("예시 (lofi 8h):")
    for ts, label in build_loop_chapters("lofi", 8.0):
        print(f"  {ts}  {label}")
