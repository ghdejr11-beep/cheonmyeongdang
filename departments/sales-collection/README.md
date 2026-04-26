# 수익집계부 (sales-collection)

AdMob 광고 매출 자동 수집 + CEO 브리핑 v2 통합.

## 추적 대상 앱
- 천명당 (`com.cheonmyeongdang`)
- HexDrop (`com.hexdrop`)

## 1회 설치 (사용자 직접)

### 1) 라이브러리 설치
```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 2) Google Cloud OAuth 클라이언트 생성
1. https://console.cloud.google.com 접속 (ghdejr11@gmail.com)
2. 프로젝트 선택/생성
3. **APIs & Services → Library → AdMob API → Enable**
4. **APIs & Services → OAuth consent screen** 설정 (External, Test users 에 본인 이메일 추가)
5. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
   - Application type: **Desktop app**
6. JSON 다운로드 → 이 폴더에 `client_secret.json` 저장

### 3) AdMob Publisher ID 확인
AdMob 콘솔 → 계정 → 게시자 ID (`pub-XXXXXXXXXXXXXXXX`)

### 4) `.secrets` 에 키 추가
`C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets` 파일에 아래 두 줄 추가:
```
ADMOB_PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX
ADMOB_OAUTH_TOKEN_PATH=C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets_admob_token.json
```

### 5) 1회 인증 (브라우저 자동 오픈)
```bash
cd C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection
python admob_auth_setup.py
```
→ 브라우저에서 Google 로그인 + 권한 승인 → token.json 저장 완료.

### 6) 동작 테스트
```bash
python admob_collector.py
```
→ 어제~오늘 매출이 JSON으로 출력되면 성공.

### 7) Windows 작업 스케줄러 등록 (매일 09:00)
관리자 PowerShell에서:
```powershell
schtasks /Create /SC DAILY /TN "KunStudio_AdMobDaily" /TR "python C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection\admob_collector.py" /ST 09:00 /F
```

## 데이터 위치
- 누적 일별 매출: `data/admob_daily.json`
- 차원: APP, DATE
- 메트릭: ESTIMATED_EARNINGS (USD), AD_REQUESTS, IMPRESSIONS, CLICKS, MATCH_RATE

## 브리핑 통합
`departments/ceo-briefing/briefing_v2.py` 가 `daily_summary()` 를 호출하여
어제 매출 + 7일 평균 + 30일 누적을 텔레그램 메시지에 포함시킵니다.
토큰 만료 / 미설정 시 자동으로 "AdMob API 인증 필요" 표시 (graceful fallback).

---

# Gumroad / KDP / 크티 / 통합 매출 (3번 agent)

## 모듈 매트릭스

| 파일 | 채널 | 방식 | 데이터 |
|-----|------|------|--------|
| `gumroad_collector.py` | 디지털 상품 (Notion/프롬프트팩) | Gumroad API v2 (Bearer) | `data/gumroad_daily.json` |
| `kdp_scraper.py` | Amazon 자가출판 책 | Playwright (옵트인) / 수동 CSV | `data/kdp_daily.json` |
| `kreatie_manual.py` | 크티 (한국 디지털) | 수동 입력 CLI | `data/kreatie_manual.json` |
| `unified_revenue.py` | 통합기 | AdMob + YT + Gumroad + KDP + 크티 합산 | `data/unified_revenue_daily.json` |

## 환율
USD → KRW 환산은 `unified_revenue.FX_USD_KRW` (기본 1380, 매일 자동 갱신 안 함).

## .secrets 추가 키
```
GUMROAD_ACCESS_TOKEN=...                 # 이미 등록됨 (2026-04-20)
KDP_EMAIL=...                            # (선택) Playwright 자동 로그인용
KDP_PASSWORD=...                         # (선택) — Amazon ToS 회색지대, 사용자 자기 책임
```

## KDP 자동화 위험 안내
- KDP 공식 Reports API 없음 (2026-04 기준)
- Playwright 자동 로그인은 Amazon ToS 회색지대 → **계정 정지 위험 0이 아님**
- 권장: 매주 수동 KDP Reports → CSV 다운로드 → `.kdp_reports/` 저장
  (기존 `ceo-briefing/integrations/kdp.py` 가 이 폴더를 자동 파싱)
- `kdp_scraper.py` 는 옵트인: `KDP_EMAIL` + `KDP_PASSWORD` 둘 다 있을 때만 동작
- 2FA / CAPTCHA / 본인인증 발생 시 즉시 중단하고 사용자 알림

## 크티 수동 입력
크티는 공식 API 없음. 매일 1회 수동 입력 (CLI).
```bash
python kreatie_manual.py    # 어제 매출 / 건수 / 환불 입력
```
입력 안 하면 마지막 값 유지.

## 통합 실행 / 스케줄
```bash
python unified_revenue.py            # 어제 통합 매출 출력
python unified_revenue.py --collect  # 모든 콜렉터 실행 + JSON 저장
```

Windows 작업 스케줄러 (매일 08:30 — 브리핑 09:00 직전):
```powershell
schtasks /Create /SC DAILY /TN "KunStudio_RevenueDaily" /TR "python C:\Users\hdh02\Desktop\cheonmyeongdang\departments\sales-collection\unified_revenue.py --collect" /ST 08:30 /F
```

## 브리핑 v2 통합
`briefing_v2.build_unified_revenue_section()` 이 `unified_revenue.daily_summary()` 호출 →
메시지 최상단에 **💰 어제 매출 ₩XX,XXX (전일 대비 +X.X%)** 큰 글씨 배너.

---

# YouTube 4채널 대시보드 (yt_dashboard.py)

4채널 통합 분석 — Healing Sleep Realm / Whisper Atlas / Wealth Blueprint / Inner Archetypes.

## 라이브러리 (이미 설치됨이면 skip)
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 인증 (이미 설정됨)
- 글로벌 토큰: `C:/Users/hdh02/Desktop/cheonmyeongdang/.secrets_youtube_token.json`
  (scopes: youtube.readonly + yt-analytics.readonly)
- 채널별 토큰: `departments/media/youtube/shared/token_*.pickle` (deokgune / wealth / kunstudio)
- 둘 다 없으면 graceful fallback ("YouTube API 인증 필요")

## 사용법
```bash
# 채널 ID 자동 해상도 + 일일 스냅샷 갱신 (default)
python yt_dashboard.py

# 채널 ID 강제 재해상도 (yt_channel_map.json 비어있을 때)
python yt_dashboard.py --resolve

# 미리보기 (텔레그램 전송 X, 텍스트만)
python yt_dashboard.py --preview
```

## 데이터 (data/yt_4ch_daily.json)
- 채널별: subscriber_count, view_count_total, video_count
- 채널별 어제 신규 조회수 (시계열 diff)
- 채널별 신규 구독자 (시계열 diff)
- 채널별 top 5 영상 (viewCount, likeCount, commentCount)
- 매출 추정: CPM $1~$3 가정 (YPP 가입 후 estimatedRevenue 자동 연동)

## 브리핑 통합
`briefing_v2.py` 가 `build_yt_4ch_section()` 호출 → 4채널 어제 조회수 합/best 영상/신규 구독자.

## 금지
- 본인 4채널만 (다른 사용자 X)
- 영상 자동 업로드/삭제 X (`departments/media/youtube/shared/youtube_upload.py` 별도)
- AdMob 매출은 별도 모듈 (admob_collector.py)

