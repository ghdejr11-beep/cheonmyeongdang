# 🎥 YouTube 자동화 부서 (쿤스튜디오)

3개 채널 운영 — 모두 faceless(얼굴 X) + 법적 안전(CC0/공개 소스만).

## 채널

| 디렉토리 | 채널명 | 포맷 | 리스크 |
|---|---|---|---|
| `sleep_gyeongju/` | Sleep Gyeongju | 롱폼 3~10시간 무내레이션 ASMR | 🟢 0 (CC0만) |
| `future_stack/` | Future Stack | AI/Claude 튜토리얼 롱폼 | 🟢 거의 0 (공식 문서) |
| `ai_sidehustle/` | AI Side Hustle Empire | 쇼츠+롱폼 부업 콘텐츠 | 🟢 낮음 ("Not financial advice" 고지) |

## 공통 의존
- ffmpeg 8.1 ✓ (이미 설치)
- Python 3.11 ✓
- `.secrets` 에 필요한 키:
  - `PIXABAY_API_KEY` — 스톡 영상 (무료, https://pixabay.com/api/docs/)
  - `ELEVENLABS_API_KEY` — 영어 TTS (월 $22, 무료 10K char)
  - `OPENAI_API_KEY` — TTS 대안 ($0.015/1K char, 저렴)
  - `YOUTUBE_CLIENT_SECRET_JSON` — OAuth (Google Cloud 프로젝트, 무료)
  - `ANTHROPIC_API_KEY` — Claude (스크립트 생성)
- FAL API 키 이미 있음 (이미지 생성용)

## 워크플로우
```
Claude 스크립트 → TTS (ElevenLabs/OpenAI) → 스톡 다운로드 (Pixabay) → ffmpeg 조합 → YouTube API 업로드
```

## 스케줄
- Sleep Gyeongju: 주 2회 자동 렌더·업로드 (긴 영상 = 렌더 오래 걸림)
- Future Stack: 주 1회 롱폼
- AI Side Hustle: 매일 쇼츠 1편
