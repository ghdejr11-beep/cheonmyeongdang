# 🔮 천명당팀 (Cheonmyeongdang Division)

> **본진 사이트 — 사주·관상·손금 기반 운세 플랫폼**
> 기존 서비스의 **글로벌화**가 최대 미션.

## 📍 기본 정보

- **코드명**: `cheonmyeongdang`
- **타겟**: 🌏 글로벌 (1순위) + 🇰🇷 한국 (2순위)
- **언어**: English → Korean
- **수익 모델**: 광고 + 유료 리포트 + 프리미엄 기능
- **수익 우선순위**: 🥉 3순위
- **총괄팀장**: `gm-cheonmyeongdang`

## 🌏 글로벌 전략

한국식 사주는 서양에서 낯설다. 대신 **보편적 운세 상품**으로 리브랜딩:

| 원본 (한국) | 글로벌 버전 |
|---|---|
| 사주 (四柱) | Western Astrology + BaZi (중국 철학 강조) |
| 관상 (觀相) | Face Reading / Physiognomy |
| 손금 (手相) | Palmistry / Palm Reading |

**핵심 차별화:** "East meets West" 포지셔닝. 동양 지혜 + 현대 AI.

## 👥 하위팀 (3팀)

| 팀 | 코드 | 담당 |
|---|---|---|
| 사주엔진팀 | `lead-cmd-saju-engine` | `saju-engine.js`, `knowledge.json` 엔진 개선 |
| 관상·손금팀 | `lead-cmd-face-palm` | 얼굴·손금 이미지 분석 모델 고도화 |
| 그로스팀 | `lead-cmd-growth` | SEO, 수익화, 사이트 운영, 다국어 |

## 📂 폴더 구조 (예정)

```
cheonmyeongdang/
├── CLAUDE.md       (이 파일)
├── revenue.md      (월간 수익 기록)
├── roadmap.md      (로드맵)
├── src/            (기존 index.html, js/, 이미지 이사 예정)
├── i18n/           (다국어 — en, ko, ja, zh)
└── api/            (백엔드 - 유료 리포트 생성)
```

## 🔑 필요한 도구

- `FAL_API_KEY` — 관상·손금 이미지 분석
- `STRIPE_SECRET_KEY` — 글로벌 결제
- `TOSS_SECRET_KEY` — 한국 결제
- Google Analytics — 트래픽 분석

## ⚠️ 주의사항

1. 기존 `index.html`, `saju-engine.js`, `knowledge.json`, 이미지들은 **현재 리포 루트**에 있음. 이사 작업은 점진적으로.
2. 기존 트래픽·SEO를 망치지 않도록 **301 리다이렉트** 필수.
3. 글로벌 버전은 `/en/` 경로로 먼저 추가 (리스크 최소화).
