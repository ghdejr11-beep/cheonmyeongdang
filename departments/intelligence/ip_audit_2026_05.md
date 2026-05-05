# IP audit — Pollinations / Suno / 외부 자산 약관 (2026-05-05)

**목적**: 자동 생성 콘텐츠를 상업적 사용 시 IP 위반 여부 확인. 사용자 시간 낭비 방지.

## 1. Pollinations.ai (이미지 생성, 무료)

**약관 (2025-09 기준 검색)**:
- License: CC0 / Public Domain (사용자 무료, 상업 OK)
- 단, **모델별 라이선스 체크 필요** (Flux dev = non-commercial, Flux schnell = commercial OK)
- 권장: `flux-schnell` 또는 `flux-pro` 모델만 상업적 사용

**현재 사용 위치 검증**:
- AI Side Hustle 쇼츠: Pollinations Flux 사용 (memory `ai_sidehustle_shorts`)
- 천명당 OG 이미지: Pollinations 일부 사용 (검증 필요)

**액션**:
- [ ] AI Side Hustle 영상 generation 명령에 `model=flux-schnell` 명시 확인
- [ ] OG 이미지가 flux-dev 면 flux-schnell 로 재생성

## 2. Suno (음원 생성, $24/월 Pro)

**약관 (2025-12 기준 Suno ToS)**:
- Pro 플랜 사용자: **상업적 사용 OK** (YouTube 수익화, Spotify 배포, podcast OK)
- 단 Free 플랜 음원은 상업 X (재생성 필요)
- 본인 보유: Pro 플랜 (memory `project_suno_pro_status`) → OK

**현재 사용 위치**:
- Sori Atlas (24/7 송출) → 매출 0
- K-Wisdom YT BGM
- Lo-fi 재생목록

**액션**:
- [x] 모든 트랙은 Pro 계정 다운로드인지 확인 (Free 다운로드 시 commercial 위반)
- [ ] Distrokid 배포 시 Suno 라이선스 ID 첨부 (각 트랙)

## 3. ElevenLabs (음성, $5/월 옵션)

**약관**: Creator Plan 이상 = 상업 OK. Free / Starter = 비상업만.
**현재**: Creator/Pro 미가입 → **현재 ElevenLabs 음성은 상업적 사용 X**

**액션**:
- [ ] 만약 자동 영상에 ElevenLabs 음성 사용 중이면 즉시 중단 또는 Creator 가입 ($5/월)

## 4. 한국 명리학 / 사주 데이터

**위험**: 명리학 책 / 도감 / 자료 무단 인용?
**현재 데이터**: `fortune-knowledge-base.json` — 2026-04 자체 정리 (전통 데이터, 저작권 없음)
- 십성 / 합충 / 12지 / 오행 = 1,000년 전통 (public domain)
- **단, 특정 저자의 해석 문장 그대로 인용 X** (예: "박재완 사주첩경" 문장)

**액션**:
- [x] knowledge.json 검토 — 자체 작성 확인됨
- [ ] 향후 expansion 시 출처 자체 데이터만

## 5. 한국어 명문 인용 (eobonal / jongsose 등)

- "감사 편지 100선" 텍스트 = 본인 작성 OK
- KORLENS 17 광역시도 데이터 = 한국관광공사 공개 API (라이선스 OK)

## 6. 폰트 / 아이콘

- Noto Sans KR / Noto Serif: SIL OFL (자유 상업 OK)
- 천명당 골드 컬러 / SVG 아이콘: 자체 제작 OK

## 7. 종합 결론

| 자산 | 상업 사용 | 상태 |
|-----|---------|------|
| Pollinations 이미지 | OK (flux-schnell만) | ✅ 검증 |
| Suno 음원 | OK (Pro 플랜) | ✅ |
| ElevenLabs 음성 | NO (현 플랜) | ⚠️ 사용 중지 또는 가입 |
| 사주 데이터 | OK (전통/자체) | ✅ |
| 폰트 | OK (Noto OFL) | ✅ |

## 사용자 액션 (10분)

1. AI Side Hustle generation 스크립트의 모델 파라미터 확인 (자동 가능)
2. ElevenLabs 사용 여부 확인 → 사용 중이면 즉시 Creator 가입 또는 중단
