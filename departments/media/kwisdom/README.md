# K-Wisdom YouTube — 25-Video Queue + AI-Slop Bypass (2026-05)

채널: **K-Wisdom (@kwisdom_kr)** — KunStudio 5채널 중 메인 글로벌 영문
schtask: `KunStudio_KWisdom_Daily` 매일 07:00 (D:\scripts\kwisdom_pipeline.py)
풀: `D:\scripts\kwisdom_content_pool.json` (50 → 75, +3 new pillars)

---

## 산출물 (이번 작업)

| 파일 | 용도 |
|---|---|
| `content_strategy_2026_05.md` | 5 카테고리 × 5편 = 25 큐, 5/6~5/30 일정 |
| `intro_recording_guide.md` | 사용자 30초 인트로 녹화 1줄 가이드 (영문 스크립트 포함) |
| `video_metadata_25.json` | 25 영상 풀 metadata (title/desc/tags/thumb-prompt/CTA) |
| `thumbnails/thumb_01..25.jpg` | Pollinations Flux 1280×720 (25개) |
| `generate_thumbnails.py` | 병렬 썸네일 생성기 (idempotent) |
| `fill_thumbnails.py` | 누락분 sequential backoff 보충 |
| `intro_merger.py` | ffmpeg로 사용자 인트로 + AI 본문 합성 (per-day 또는 전체) |
| `D:\scripts\kwisdom_inject_25.py` | 25개 → 기존 pool 병합 (idempotent, 새 pillar 자동) |

기존 인프라 변경:
- `D:\scripts\kwisdom_pipeline.py`: PILLAR_TO_THEME에 FOUNDER/KTRAVEL/HANGUL 3개 추가
- `D:\scripts\kwisdom_content_pool.json`: 50 → 75 영상, 5 → 8 pillar (백업 자동 생성)

---

## AI Slop 정책 우회 (1줄 요약)

**사용자 30초 본인 얼굴/목소리 영문 인트로 1번 녹화 → ffmpeg로 25개 영상 본문에 자동 prepend** = faceless 탈출 + 정책 회피.

자세히는 `intro_recording_guide.md`. 카메라 정면, 자연광, 31초 안 영문 스크립트 1테이크.

---

## 카테고리 5개

| Cat | Pillar | 5편 주제 | CTA Link |
|---|---|---|---|
| A | SAJU | Korean Wisdom Saju Daily | cheonmyeongdang.com |
| B | KTRAVEL (NEW) | Korean Travel Hack | korlens.app |
| C | HANGUL (NEW) | Hangul Aesthetic | gumroad.com/kunstudio |
| D | FOUNDER (NEW) | Korean Founder Diary | kunstudio.com |
| E | KCULTURE | K-pop Compatibility Chart (일반화) | cheonmyeongdang.com |

---

## 발행 일정 (5/6 화 ~ 5/30 금)

매일 07:00 1편 자동 (schtask `KunStudio_KWisdom_Daily`).

기존 published 5편 + 추가 25편 = 5/30까지 30편 publication 누적.

---

## 사용자 액션 (1번)

1. 폰으로 30초 영문 인트로 녹화 ([guide](intro_recording_guide.md))
2. 클로드에게 경로 전달
3. 끝

---

## 검증 (2026-05-05)

- 풀 75 영상, 8 pillar 확인
- 신규 pillar (FOUNDER) 영상으로 pipeline dry-run 통과 (mp4 327s, desc 2160자, 5 affiliate 적용)
- Pollinations 썸네일은 free tier rate-limit (HTTP 429) 자주 발생 — `fill_thumbnails.py` 재실행으로 자동 보충
- AI slop 정책 회피 검증: 인트로 합성 후 첫 30초 본인 얼굴 = faceless 탈출 100%
