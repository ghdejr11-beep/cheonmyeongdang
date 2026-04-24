#!/usr/bin/env python3
"""
Sleep Gyeongju 자동 파이프라인:
  1. FAL Flux 로 경주 사찰 이미지 20장 생성
  2. ffmpeg zoompan → 각 이미지 30초 Ken Burns 클립
  3. CC0 음악 루프 + 8시간 concat
  4. YouTube 자동 업로드 (private 로 1차 → 사용자가 공개 전환)

Task Scheduler 에서 주 2회 실행.
"""
import sys, os, datetime, random
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DEPT = Path(__file__).parent
sys.path.insert(0, str(DEPT.parent / "shared"))

from generate_video import generate_images, render, load_secrets, PROMPTS
from youtube_upload import upload_video


# 제목 회전 풀 (중복 방지)
TITLE_POOL = [
    "{H} Hours Korean Temple Rain & Bells 🌧️ Gyeongju Sleep Music",
    "Deep Sleep {H}h · Ancient Korean Temple ASMR",
    "Buddhist Temple Meditation Music | {H} Hours Korean Heritage",
    "{H} Hours Bulguksa Temple Ambience for Sleep",
    "Korean Mountain Temple Sounds · {H} Hours · Zen Sleep",
    "Peaceful {H}h Korean Temple ASMR · Deep Sleep",
    "{H} Hours of Silent Gyeongju Temple · Sleep & Study",
    "Rainy Korean Temple · {H} Hours · Sleep, Study, Meditate",
]

DESCRIPTION_TEMPLATE = """🌙 {hours} hours of serene Korean Buddhist temple ambience for deep sleep, study, and meditation.

Experience the tranquility of Gyeongju — home of 1,500 years of Silla dynasty heritage and UNESCO World Heritage sites like Bulguksa and Seokguram.

Use this video for:
🛌 Deep sleep
📚 Study & concentration
🧘 Meditation & mindfulness
🕯️ Stress relief

🌏 Visit real Gyeongju with KORLENS AI travel curation: https://korlens.vercel.app

No talking, no ads interruption in the middle — pure ambience.

#SleepMusic #KoreanTemple #Gyeongju #ASMR #MeditationMusic #DeepSleep #StudyMusic

Made with AI-generated imagery (no copyrighted footage).
"""

TAGS = ["sleep music", "asmr", "korean temple", "gyeongju", "meditation",
        "buddhist", "study music", "relaxing music", "long sleep",
        "korean heritage", "bulguksa", "rain sounds"]


def main():
    env = load_secrets()
    key = env.get("FAL_API_KEY") or env.get("FAL_KEY")
    if not key:
        print("❌ FAL_API_KEY 없음")
        sys.exit(1)

    # 1. 이미지 생성 (이미 있으면 스킵)
    print("🎨 FAL Flux 이미지 생성...")
    # 매 실행마다 프롬프트 조금 변형 (중복 방지)
    seed = int(datetime.datetime.now().strftime("%Y%m%d"))
    random.seed(seed)
    chosen = random.sample(PROMPTS, min(len(PROMPTS), 20))
    imgs = generate_images(key, chosen)
    if len(imgs) < 10:
        print("❌ 이미지 10장 미만 — 재시도 필요")
        sys.exit(1)

    # 2. 음악 확인 (D: 저장)
    music = Path(r"D:\cheonmyeongdang-outputs\youtube\sleep_gyeongju\assets\music.mp3")
    if not music.exists():
        print(f"❌ {music} 없음 — 최초 1회 배치 필요")
        print("   추천: https://pixabay.com/music/search/meditation%20ambient/")
        sys.exit(1)

    # 3. 렌더 (주 2회 실행 → 3h/5h/8h 번갈아)
    hours_cycle = [3, 5, 8]
    today = datetime.date.today()
    hours = hours_cycle[(today.timetuple().tm_yday // 3) % len(hours_cycle)]

    print(f"🎬 {hours}시간 영상 렌더...")
    out = render(imgs, music, target_hours=hours, per_image_sec=30)
    if not out or not out.exists():
        print("❌ 렌더 실패")
        sys.exit(1)

    # 4. 업로드
    title_template = random.choice(TITLE_POOL)
    title = title_template.format(H=hours)
    description = DESCRIPTION_TEMPLATE.format(hours=hours)

    try:
        vid = upload_video(
            video_path=out,
            channel="deokgune",          # 덕구네 노래모음
            title=title,
            description=description,
            tags=TAGS,
            privacy="private",
            category_id="10",            # Music
        )
        print(f"🎥 업로드 완료: https://youtu.be/{vid} (비공개 상태)")
        print(f"   → Studio 에서 썸네일·공개 설정 후 Publish")
    except FileNotFoundError as e:
        print(f"❌ OAuth 미설정: {e}")
        print("   SETUP.md 참고하여 client_secret.json + token.pickle 준비")


if __name__ == "__main__":
    main()
