"""
BGM 채널 주제 라이브러리
- 덕훈님 천명당 브랜드 연계
- 장르별 프롬프트 + 제목 템플릿 + SEO 태그
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


Genre = Literal["sleep", "meditation", "buddhist", "focus", "wealth", "healing"]


@dataclass
class Topic:
    genre: Genre
    title_ko: str
    title_en: str
    prompt: str
    duration_hours: float
    tags: list[str]
    thumbnail_prompt: str


TOPICS: list[Topic] = [
    # ── 수면 BGM (메인, 광고주 선호) ──
    Topic(
        genre="sleep",
        title_ko="🌙 3분만 들으면 잠드는 수면 음악 | 10시간",
        title_en="Deep Sleep Music - Fall Asleep in 3 Minutes | 10 Hours",
        prompt="ultra calm deep sleep ambient music, 528Hz healing frequency, soft pad drones, rain sounds, ocean waves, no beats, perfect for insomnia",
        duration_hours=10,
        tags=["sleep music", "수면음악", "불면증", "백색소음", "10시간"],
        thumbnail_prompt="serene moonlit night over calm ocean, mystical blue purple gradient, star sky, peaceful meditation scene, cinematic",
    ),
    Topic(
        genre="sleep",
        title_ko="🌊 불면증 치료 파도 소리 | 뇌파 안정",
        title_en="Insomnia Cure Ocean Waves - Brainwave Relaxation",
        prompt="soft ocean waves crashing on shore, binaural delta waves 1-4Hz, very gentle ambient drone underneath, no melody, pure nature soundscape",
        duration_hours=8,
        tags=["파도소리", "ocean waves", "insomnia", "delta wave"],
        thumbnail_prompt="calm ocean waves at night, soft moonlight reflection, deep blue horizon, peaceful",
    ),
    # ── 명상·불교 (천명당 브랜드 연계) ──
    Topic(
        genre="buddhist",
        title_ko="🙏 천수경 명상 음악 | 마음 정화",
        title_en="Buddhist Meditation - Thousand Hands Sutra Ambient",
        prompt="korean buddhist temple ambient, deep singing bowls, distant temple bell, monk humming chant, rain on temple roof, ultra spiritual",
        duration_hours=3,
        tags=["불교", "명상음악", "천수경", "사찰음악", "buddhist"],
        thumbnail_prompt="ancient korean buddhist temple at dawn, soft mist, golden buddha silhouette, lotus flowers, serene",
    ),
    Topic(
        genre="meditation",
        title_ko="🕉️ 108배 명상 BGM | 번뇌 소멸",
        title_en="108 Prostrations Meditation - Clear Mind",
        prompt="tibetan singing bowls slow rhythm, om mani padme hum distant humming, deep bass drone, sacred meditation",
        duration_hours=2,
        tags=["108배", "명상", "tibetan bowls", "meditation"],
        thumbnail_prompt="108 glowing candles in dark temple, golden light, meditation posture silhouette",
    ),
    # ── 집중·공부 (Lofi) ──
    Topic(
        genre="focus",
        title_ko="📚 천재가 되는 공부 Lofi | 알파파 집중",
        title_en="Genius Study Lofi - Alpha Wave Focus",
        prompt="lofi hip hop beats slow tempo, soft piano, vinyl crackle, alpha wave binaural 8-12Hz, rain sounds, cozy study vibe",
        duration_hours=3,
        tags=["공부음악", "study lofi", "집중", "alpha wave"],
        thumbnail_prompt="cozy study desk by window at night, warm lamp, open book, coffee steam, lofi aesthetic",
    ),
    Topic(
        genre="focus",
        title_ko="💼 업무 집중 Deep Work | 고소득자 루틴",
        title_en="Deep Work Focus - High Performer Routine",
        prompt="minimal ambient electronic, subtle pulse, binaural beta waves 15-18Hz, no distractions, flow state music",
        duration_hours=4,
        tags=["deep work", "집중음악", "flow state", "productivity"],
        thumbnail_prompt="modern minimalist workspace, mechanical keyboard glow, dual monitor, dark mode aesthetic",
    ),
    # ── 금전운·행운 (천명당 운세 연계) ──
    Topic(
        genre="wealth",
        title_ko="💰 3일 안에 돈이 들어오는 주파수 | 528Hz",
        title_en="Money Attraction Frequency 528Hz - Wealth Manifestation",
        prompt="528Hz solfeggio frequency, abundant golden tones, warm harmonic drones, wealth manifestation ambient",
        duration_hours=2,
        tags=["528Hz", "money frequency", "금전운", "부자", "돈버는음악"],
        thumbnail_prompt="golden coins pouring from sky, abundance aesthetic, mystical gold light rays, luxurious",
    ),
    Topic(
        genre="wealth",
        title_ko="🍀 복 받는 아침 음악 | 금전운 상승",
        title_en="Morning Abundance Music - Lucky Energy",
        prompt="uplifting morning ambient, gentle harp, bird songs, sunrise feel, positive energy, lucky vibration",
        duration_hours=1,
        tags=["아침음악", "금전운상승", "행운", "복"],
        thumbnail_prompt="sunrise over mountain with four-leaf clover, golden morning light, lucky charm aesthetic",
    ),
    # ── 힐링·트라우마 치유 ──
    Topic(
        genre="healing",
        title_ko="💚 상처받은 마음 치유 | 세로토닌 분비 음악",
        title_en="Heart Healing - Serotonin Release Music",
        prompt="emotional healing ambient, soft strings pad, gentle piano, warm reverb, self-love frequency 639Hz",
        duration_hours=3,
        tags=["힐링음악", "마음치유", "serotonin", "healing"],
        thumbnail_prompt="hands holding glowing heart, soft pink green gradient, emotional healing aesthetic",
    ),
]


# 스케줄 (요일별 업로드)
WEEKLY_SCHEDULE = {
    "monday": "sleep",
    "tuesday": "focus",
    "wednesday": "buddhist",
    "thursday": "focus",
    "friday": "meditation",
    "saturday": "healing",
    "sunday": "wealth",
}


def topic_for_today(weekday: str) -> Topic:
    """요일에 맞는 주제 1개 선택 (라운드로빈)"""
    import random
    genre = WEEKLY_SCHEDULE.get(weekday.lower(), "sleep")
    candidates = [t for t in TOPICS if t.genre == genre]
    return random.choice(candidates) if candidates else TOPICS[0]
