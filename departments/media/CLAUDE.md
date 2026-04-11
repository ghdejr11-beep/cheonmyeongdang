# 📺 미디어팀 (Media Division)

> **YouTube + SNS 통합 콘텐츠 부서**
> 자체 채널 수익 + 타 부서 홍보 크로스 담당.

## 📍 기본 정보

- **코드명**: `media`
- **타겟**: 🌏 글로벌 (영어 1순위)
- **언어**: English
- **수익 모델**: YouTube Ads, SNS Creator Fund, 협찬, 멤버십
- **수익 우선순위**: 🥈 2순위
- **총괄팀장**: `gm-media`

## 🌏 전략

- **영어 채널**: 한국 대비 CPM 4~5배 ($3~8 per 1000 views)
- **니치**: Mystic / Fortune / East-meets-West
- **포맷**: YouTube Shorts 메인 + Long-form 보조
- **크로스포스팅**: TikTok, Instagram Reels, X(Twitter)

## 👥 하위팀 (5팀)

| 팀 | 코드 | 담당 |
|---|---|---|
| 콘텐츠제작팀 | `lead-media-content` | 대본 → 영상 생성 (fal.ai) → 편집 |
| SNS팀 | `lead-media-sns` | 인스타/틱톡/X 숏폼 최적화, 재포맷 |
| 홍보·크로스팀 | `lead-media-promo` | 천명당/보험/전자책 홍보 콘텐츠 |
| 업로드운영팀 | `lead-media-upload` | 전 플랫폼 업로드, 제목·태그·썸네일 A/B |
| 분석팀 | `lead-media-analytics` | 조회수·수익·유지율 모니터링 |

## 💰 KPI 분리

미디어팀 `revenue.md`는 **2트랙**:
1. **직접 수익** (경쟁 랭킹 반영): 유튜브 광고·슈퍼챗·협찬·멤버십
2. **홍보 기여** (별도 추적, 랭킹 제외): 타 부서 유입 전환 추정치

## 🔑 필요한 도구

- `FAL_API_KEY` — 영상 생성 (Runway/Veo/Kling/Pika)
- `HEYGEN_API_KEY` — AI 아바타 내레이션
- `YOUTUBE_CLIENT_ID/SECRET/REFRESH_TOKEN` — YouTube Data API v3
- Video Editor MCP — FFmpeg 편집
- Instagram Graph API, TikTok Content Posting API — 추후 추가

## ⚠️ 주의사항

- 영어 채널은 초기 구독자 0에서 시작. 수익화 조건: **1,000 구독자 + 4,000 시청시간** (long-form)
- YouTube Shorts 별도 수익화: **1,000 구독자 + 1,000만 Shorts 조회수** (90일 내)
- 초기 2~3개월은 매출 0, 콘텐츠 축적 집중
