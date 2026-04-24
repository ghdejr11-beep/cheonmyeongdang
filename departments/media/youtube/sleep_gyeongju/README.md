# 🌙 Sleep Gyeongju

경주 사찰·폭포 AI 생성 이미지 + 명상 음악 **8시간 ASMR 영상** 자동 생성.

## 전략
- 포맷: 무내레이션 3/5/8시간 3종
- 참고: **Lofi Girl 15M 구독, 월 2,800만~6,300만원**
- 리스크: 🟢 **0** — AI 생성 이미지(FAL Flux, 본인 소유) + CC0 음악

## 자동화 스택 (Pixabay 없음)
- **FAL Flux Schnell** — 경주 스타일 이미지 20~30장 생성 (장당 약 $0.003, 총 약 $0.10/영상)
- **ffmpeg zoompan** — Ken Burns 슬로우 줌 효과
- **음악은 사용자 1회 배치** — `assets/music.mp3`

## 사용자 준비 (1회)
1. **배경 음악 1곡** 다운로드 → `assets/music.mp3`
   - 추천 CC0/Pixabay License: https://pixabay.com/music/search/meditation%20ambient/
   - 또는 Suno/Udio로 직접 생성 (본인 저작)
   - 10~30분 트랙 1개면 충분 (ffmpeg가 루프)
2. **YouTube OAuth** (별도 upload.py)

## 실행
```bash
cd C:\Users\hdh02\Desktop\cheonmyeongdang\departments\media\youtube\sleep_gyeongju
python generate_video.py
# FAL로 이미지 20장 생성 (~1분)
# 8시간 영상 output/sleep_gyeongju_8h.mp4 (렌더 20~40분)
```

## 비용
- FAL Flux Schnell: 영상당 약 140원 (이미지 20장 × $0.003)
- 음악: 무료 (CC0)
- 유튜브: 무료

## 제목 예시
- "8 Hours Korean Temple Rain Sounds 🌧️ Gyeongju Bulguksa Sleep Music"
- "Deep Sleep · 10h · Ancient Korean Temple ASMR"
- "Buddhist Temple Meditation Music | 8 Hours Korean Heritage"

## 수익 기대
- 첫 10편 업로드 → 6개월 후 구독 1만~5만 가능
- Lofi Girl 모델 기준 월 280만~630만원 (안정화 후)
