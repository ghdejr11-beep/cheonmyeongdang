# K-Wisdom YouTube — Content Strategy (2026-05)

채널: **K-Wisdom (@kwisdom_kr)** — KunStudio 5채널 중 메인 글로벌 영문
스택: ffmpeg + Whisper + Suno + Pollinations Flux
schtask: `KunStudio_KWisdom_Daily` 매일 07:00 (5/6~5/30 = 25일치 큐)

---

## 0. AI Slop 정책 우회 전략 (핵심)

YouTube 2026 AI slop 정책의 5/5 risk 신호 (faceless + synthetic + template + volume + low-info) 중 **3개 이상 차단**.

| Risk 신호 | 대응 |
|---|---|
| Faceless | **30초 본인 인트로** (사용자 1회 녹화, 25개 자동 합성) — `intro_recording_guide.md` |
| Synthetic voice only | 인트로는 본인 목소리, 본문은 ElevenLabs/AI but **named character narrative** |
| Template repetition | 5개 카테고리 × 5편 = 시각적/주제적 다변화 |
| Volume/low-info | 영상마다 1개 actionable insight + 천명당/KORLENS 실제 무료 도구 link |
| Faceless thumbnail | 본인 얼굴 frame 1개 추출 to thumbnail (한 번만) |

**1줄 요약**: 본인 30초 인트로 1번 녹화 → ffmpeg로 25개에 자동 prepend → 사용자 얼굴/목소리 + AI 본문 hybrid = AI slop 회피.

---

## 1. 카테고리 5개 (각 5편 = 25 영상)

### A. Korean Wisdom Saju Daily (5편) — link: cheonmyeongdang.com
- 글로벌 영어권 K-pop/K-drama 팬 → 본인의 사주 궁금증
- 매 영상 = 1 actionable insight (오늘의 saju element / 띠 운세 영문)
- CTA: "Get your free Saju reading at cheonmyeongdang.com"

### B. Korean Travel Hack (5편) — link: korlens.app
- 한국 여행 hidden gem / 현지인 픽 / 카페·맛집·박물관
- KORLENS 앱 시연: 사진 한 장 → AI가 한국 장소 추천
- CTA: "Download KORLENS — Korea's local pick AI"

### C. Hangul Aesthetic (5편) — link: gumroad.com/kunstudio
- 한글 calligraphy / typography / 단어 의미 (예: 한, 정, 흥)
- aesthetic 한글 wallpaper / sticker 번들 판매
- CTA: "Hangul Aesthetic Mega Bundle — $29.99 on Gumroad"

### D. Korean Founder Diary (5편) — link: kunstudio.com (or all)
- KunStudio 1인기업 founder story (실제 경험, AI slop 회피 핵심)
- 사주앱 만들면서 배운 것 / Korean indie hacker journey / 매출 솔직 공개
- CTA: "Follow my journey at @kunstudio_kr"

### E. K-pop Compatibility Chart (5편) — Saju + entertainment
- 일반화 표현만 ("K-pop fans", "Korean entertainment idols") — memory `no_specific_company_names`
- "Which K-pop archetype matches your Saju element?" 같은 quiz
- CTA: "Find your K-pop archetype — free Saju at cheonmyeongdang.com"

---

## 2. 발행 일정 (5/6~5/30, 25일)

```
Day  Date     Cat   Title
1    5/6 Tue  A     Korean Saju 101: What Is Your Element?
2    5/7 Wed  B     Korea's Hidden Cafes Tourists Never Find
3    5/8 Thu  C     The Most Beautiful Hangul Words That Don't Translate
4    5/9 Fri  D     Why I Quit My Job to Build a Korean Saju App
5    5/10 Sat E     Your K-pop Archetype Based on Korean Astrology
6    5/11 Sun A     Tomorrow's Luck: Free Saju Daily Reading
7    5/12 Mon B     Seoul vs Busan: AI Picks Real Local Spots
8    5/13 Tue C     Hangul Calligraphy: 5 Words to Know
9    5/14 Wed D     My First $1,000 Month as a Korean Indie Hacker
10   5/15 Thu E     K-Drama Lead Personality Types in Saju
11   5/16 Fri A     Saju vs Western Astrology: The Real Difference
12   5/17 Sat B     Gyeongju: Korea's Forgotten Ancient Capital
13   5/18 Sun C     Korean Aesthetic: How "Han" Shapes Design
14   5/19 Mon D     I Built a Saju App in 30 Days — Here's What Worked
15   5/20 Tue E     Why K-pop Fans Are Obsessed with Korean Astrology
16   5/21 Wed A     Your Birth Hour Changes Your Saju (Most Don't Know)
17   5/22 Thu B     Korean Convenience Store Hacks for Travelers
18   5/23 Fri C     Hangul Typography: From Sejong to Modern Brands
19   5/24 Sat D     Korean Founder vs Silicon Valley: 5 Differences
20   5/25 Sun E     Korean Boy/Girl Group Stage Names & Saju Elements
21   5/26 Mon A     Saju Compatibility: Friends vs Lovers
22   5/27 Tue B     Jeju Island: AI's Top 7 Local Picks
23   5/28 Wed C     "Jeong" — The Korean Word for Unspoken Bond
24   5/29 Thu D     My 100-Day KunStudio Journey: Lessons + Numbers
25   5/30 Fri E     K-pop Idol Saju Charts: A Fan's Curiosity Guide
```

---

## 3. 자동화 파이프라인

```
[Day N]  schtask 07:00
  ├─ pick video N from video_metadata_25.json
  ├─ ffmpeg merge: intro.mp4 (사용자 녹화) + body_N.mp4 (AI 생성)
  ├─ Whisper auto-caption (English first, Korean assist)
  ├─ Pollinations Flux thumbnail (already pre-generated)
  ├─ Upload-Post API → YouTube K-Wisdom channel
  └─ Notion log + briefing append
```

---

## 4. 사용자 1줄 액션

폰으로 30초 영문 인트로 1번 녹화 ([intro_recording_guide.md](intro_recording_guide.md)) → 그 후 25 영상 모두 자동.

---

## 5. KPI (5/30 측정)

- 25 영상 발행 100% (자동)
- 평균 조회 ≥ 200 (영문 글로벌, faceless 탈출 효과)
- 천명당/KORLENS click ≥ 100 (description link tracking)
- AI slop strike 0 (정책 회피 검증)
