# 🗂️ 쿤스튜디오 미디어 계정 인벤토리

> 서비스별 타겟 국가·플랫폼 매핑 + 계정 보유 현황 중앙 관리  
> 이 문서를 채우면 `unified_poster.py` 자동 라우팅 구조 확정.

---

## 📋 현재 확인된 계정 (코드 기준)

| 플랫폼 | 계정 ID / 이름 | 토큰 위치 | 상태 |
|---|---|---|---|
| 📱 텔레그램 | `deokgune_ai_team_bot` (8650272218) | `.secrets` TELEGRAM_BOT_TOKEN | ✅ 검증 완료 |
| 🐦 X (Twitter) | ID 2042656247892029440 | `.secrets` X_* | ⚠️ 토큰 있음, 미검증 |
| 📷 Instagram Business | `deokgune_ai` | Meta 앱 세팅 필요 | 🔄 세팅 중 |
| 📘 Facebook 페이지 | "세금N혜택" | Meta 앱 세팅 필요 | 🔄 세팅 중 |
| 💬 카카오톡 채널 | **(확인 필요)** | 토큰 없음 | ❓ |

---

## 🎯 서비스 × 타겟 × 플랫폼 매핑 (초안)

### 🔍 KORLENS (외국인+한국인, 글로벌)
- **타겟**: 방한 외국인 + 국내 여행자
- **언어**: 한국어 + 영어 둘 다
- **필요 플랫폼**:
  - [ ] Instagram Business (글로벌) — 기존 `deokgune_ai` 공유? or 신규 `korlens_official`?
  - [ ] Threads (Meta, IG 연동) — IG와 자동 연동
  - [ ] TikTok Business — 신규 필요?
  - [ ] YouTube Shorts — 신규 채널 필요?
  - [ ] Pinterest Business — 신규 필요?
  - [ ] 카카오톡 채널 — 쿤스튜디오 채널 활용?
  - [ ] 네이버 블로그 — 신규 필요?

### 💰 세금N혜택 (한국 전용)
- **타겟**: 한국 직장인·프리랜서
- **언어**: 한국어
- **필요 플랫폼**:
  - [x] 텔레그램 — 기존 `deokgune_ai_team_bot`
  - [ ] 카카오톡 채널 — 홍보 채널 있는지?
  - [ ] 네이버 블로그 — SEO 유입용, 신규 필요
  - [ ] Threads (KR) — 공유? 신규?
  - [ ] YouTube (한국어 설명 영상)

### 🔮 천명당 (한국 전용, 사주 문화)
- **타겟**: 한국 20~40대
- **언어**: 한국어
- **필요 플랫폼**:
  - [x] 텔레그램
  - [ ] 카카오톡 채널
  - [ ] Instagram (한국어) — deokgune_ai 공유?
  - [ ] Threads (KR)

### 🎮 HexDrop (글로벌 게임)
- **타겟**: 전 세계 게이머
- **언어**: 한국어 + 영어
- **필요 플랫폼**:
  - [ ] YouTube Shorts — 게임 플레이 영상용
  - [ ] TikTok — 바이럴 핵심
  - [ ] X — 영어 게이머 커뮤니티
  - [ ] Reddit (r/IndieGames, r/AndroidGaming)
  - [ ] Threads

### 📖 전자책 KDP (영어권)
- **타겟**: Amazon KDP 독자 (영어권)
- **언어**: 영어
- **필요 플랫폼**:
  - [ ] X (영어 계정) — 기존 X 영어권 맞는지?
  - [ ] Pinterest — 북커버용, 매우 중요
  - [ ] Reddit (r/KDP, r/selfpublish)
  - [ ] YouTube (책 소개 영상)

### 🛡️ 보험다보여 (한국 전용)
- **타겟**: 한국 보험 가입자·설계사
- **언어**: 한국어
- **필요 플랫폼**:
  - [ ] 네이버 블로그 (SEO)
  - [ ] 카카오톡 채널
  - [ ] YouTube (설명 영상)

---

## ✅ 사용자 결정 사항 (2026-04-18)

1. **카카오톡 채널**: ❌ 없음 → 제외 (나중에 별도 개설 시 추가)
2. **Instagram 전략**: 🅰 `deokgune_ai` 단일 계정으로 전 서비스 운영
3. **YouTube**: 쿤스튜디오 메인 채널 1개 신규 생성 (HexDrop·KORLENS·천명당 등 공용)
4. **X**: 영어+한국어 혼용 (기존 계정 확인 필요)
5. **네이버 블로그**: 확인 필요

### 확정된 플랫폼 조합
| 서비스 | 대상 플랫폼 |
|---|---|
| 🔍 KORLENS | 텔레그램·X·IG·Threads·YouTube |
| 💰 세금N혜택 | 텔레그램·IG·Threads |
| 🔮 천명당 | 텔레그램·IG·Threads |
| 🎮 HexDrop | 텔레그램·X·IG·YouTube |
| 📖 전자책 | X (영어 위주) |
| 🛡️ 보험다보여 | 텔레그램·IG |

---

## ❓ 네가 확인/결정해야 할 것

### 1️⃣ 카카오톡 채널
- [ ] **쿤스튜디오 공식 카카오톡 채널 있어?** 있으면:
  - 채널명: ________
  - 채널 URL: ________
  - 친구(구독자) 수: ________
  - 비즈니스 채널 여부: ☐ Yes ☐ No
- [ ] **친구톡/알림톡 API 신청했어?** (API 발송 가능한지)

### 2️⃣ Instagram 전략
3가지 중 선택:
- [ ] 🅰 **기존 `deokgune_ai` 단일 계정**에서 전체 서비스 포스팅 (포트폴리오형)
- [ ] 🅱 **서비스별 분리 계정** (korlens_official, tax_korea, cheonmyeongdang_official 등)
- [ ] 🅲 **혼합** — 브랜드 통합 계정 + KORLENS만 별도 (외국인 타겟)

### 3️⃣ 신규 계정 만들 거 (체크)
- [ ] KORLENS 전용 TikTok
- [ ] KORLENS 전용 YouTube 채널
- [ ] KORLENS 전용 Pinterest
- [ ] 쿤스튜디오 네이버 블로그 1개 (서비스 전부 공용) 또는 서비스별 블로그
- [ ] 쿤스튜디오 YouTube 메인 채널 (HexDrop 게임플레이용)

### 4️⃣ X (Twitter) 전략
- 기존 계정이 영어 중심? 한국어 중심? 둘 다?
- 전자책(KDP)과 HexDrop 둘 다 여기서 운영 가능?
- 신규 영어 전용 계정 필요한지?

### 5️⃣ 네이버 블로그
- [ ] 블로그 있음 (주소: __________)
- [ ] 없음 → 신규 생성 필요 (주제별 카테고리 분류로 단일 블로그 운영 권장)

---

## 🚀 다음 단계 (계정 확정 후)

1. 이 문서 체크리스트 채움
2. `accounts.json` 자동 생성 (unified_poster.py 참조용)
3. Postiz 셀프호스팅 세팅 + OAuth로 글로벌 플랫폼 연결
4. 카카오톡 채널 API (또는 Selenium fallback) 별도 세팅
5. 네이버 블로그 반자동 세팅 (공식 API 제한 많음)
6. 첫 통합 포스팅 테스트 (KORLENS 런칭)

---

## 📞 필요 시 참고

- **Meta Business Suite**: https://business.facebook.com/
- **TikTok for Business**: https://www.tiktok.com/business/
- **YouTube Studio**: https://studio.youtube.com/
- **Pinterest Business**: https://business.pinterest.com/
- **카카오 비즈니스 채널**: https://center-pf.kakao.com/
- **네이버 블로그**: https://blog.naver.com/
